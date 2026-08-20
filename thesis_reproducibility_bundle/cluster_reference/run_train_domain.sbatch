#!/bin/bash
#SBATCH --partition=main
#SBATCH --mem=80G
#SBATCH --cpus-per-task=8
#SBATCH --exclude=ise-cpu256-[11-12],ise-cpu-intl-[01,08-15,18,24-28]
###SBATCH --mail-type=END,FAIL,REQUEUE,TIME_LIMIT
#SBATCH --mail-user=hersco@post.bgu.ac.il

MAX_RETRIES=5
RETRY_DELAY=10 #seconds between retries

if [[ -n "$SLURM_JOB_GPUS" ]]; then
APPTAINER_GPU_FLAG="--nv"
else
APPTAINER_GPU_FLAG=""
fi


echo "[SLURM] Starting job $SLURM_JOB_ID on $(hostname)" 
echo "[HYPERPARAMETERS] Using the following hyperparameters:" 
#echo "[HYPERPARAMETERS] Original training, ${TEACHER_CONFIG}" 
echo "[HYPERPARAMETERS] AlphaZero training"
echo "[HYPERPARAMETERS] Current domain:  ${DOMAIN}" 
echo "[HYPERPARAMETERS] Seed: ${SEED}"

CURRENT_LOG="${OUTPUT_DIR}/${SLURM_JOB_ID}_${CURRENT_JOB_NAME}.txt"
RESUME_STATE_DIR="${OUTPUT_DIR}/.resume_state"
RESUME_STATE_FILE="${RESUME_STATE_DIR}/${SLURM_JOB_ID}.snapshot_root"
EVAL_WAVE_STATE_FILE="${RESUME_STATE_DIR}/${SLURM_JOB_ID}.eval_wave"
EVAL_COMPLETION_FILE="${RESUME_STATE_DIR}/${SLURM_JOB_ID}.eval_completed.jsonl"
mkdir -p "${RESUME_STATE_DIR}"

# Evaluation continuations persist the next unfinished wave. This makes an
# in-job retry and a Slurm requeue advance past waves that finished before the
# failure instead of repeating the caller's original --eval-start-wave.
update_eval_wave_state() {
  [[ -n "${EVAL_START_WAVE_ARG:-}" && -f "${CURRENT_LOG}" ]] || return 0
  next_wave="$(awk '
    /^\[EVAL RESUME\] starting wave [0-9]+;/ {
      line = $0
      sub(/^\[EVAL RESUME\] starting wave /, "", line)
      sub(/;.*/, "", line)
      start = line + 0
      completed = 0
      seen = 1
      next
    }
    seen && /^\[EVAL\] [A-Z]+ wave [0-9]+: .* \| time=[0-9.]+s$/ {
      completed++
    }
    END {
      if (seen) print start + completed
    }
  ' "${CURRENT_LOG}")"
  if [[ "${next_wave}" =~ ^[0-9]+$ ]]; then
    current_wave="$(cat "${EVAL_WAVE_STATE_FILE}" 2>/dev/null || true)"
    if [[ ! "${current_wave}" =~ ^[0-9]+$ ||
          "${next_wave}" -gt "${current_wave}" ]]; then
      printf '%s\n' "${next_wave}" > "${EVAL_WAVE_STATE_FILE}.tmp"
      mv "${EVAL_WAVE_STATE_FILE}.tmp" "${EVAL_WAVE_STATE_FILE}"
      echo "[EVAL RESUME] persisted next unfinished wave ${next_wave}"
    fi
  fi
}

EVAL_WAVE_WATCHER_PID=""
if [[ -n "${EVAL_START_WAVE_ARG:-}" ]]; then
  requested_eval_wave="${EVAL_START_WAVE_ARG##* }"
  if [[ ! -s "${EVAL_WAVE_STATE_FILE}" ]]; then
    printf '%s\n' "${requested_eval_wave}" > "${EVAL_WAVE_STATE_FILE}"
  fi
  (
    while true; do
      update_eval_wave_state
      sleep 10
    done
  ) &
  EVAL_WAVE_WATCHER_PID=$!
fi

# A Slurm requeue restarts this batch script from its beginning. Only in that
# case, and only when the caller did not explicitly supply a checkpoint, resume
# training from the latest checkpoint recorded for this same Slurm job.
if [[ -z "${RESUME_FROM_ARG:-}" &&
      "${SLURM_RESTART_COUNT:-0}" -gt 0 &&
      -s "${RESUME_STATE_FILE}" ]]; then
  SNAPSHOT_ROOT="$(<"${RESUME_STATE_FILE}")"
  LATEST_SNAPSHOT="$(
    find "${SNAPSHOT_ROOT}" -maxdepth 1 \( -type f -o -type d \) \
      -name 'snapshot_*' -printf '%f\n' |
      sort -t_ -k2,2n |
      tail -n1
  )"

  if [[ -n "${LATEST_SNAPSHOT}" &&
        -e "${SNAPSHOT_ROOT}/${LATEST_SNAPSHOT}" ]]; then
    RESUME_FROM_ARG="--resume-from ${SNAPSHOT_ROOT}/${LATEST_SNAPSHOT}"
    RESUME_TRAIN_FLAG="--resume-train"
    echo "[RESUME] Slurm restart ${SLURM_RESTART_COUNT}: resuming from ${SNAPSHOT_ROOT}/${LATEST_SNAPSHOT}"
  else
    echo "[RESUME] Restart detected, but no valid checkpoint found; starting fresh."
  fi
fi

# Persist the snapshot root independently of Slurm stdout. Slurm may truncate
# the output log on requeue, whereas this per-job state file survives.
SNAPSHOT_WATCHER_PID=""
if [[ ! -s "${RESUME_STATE_FILE}" ]]; then
  (
    while true; do
      snapshot_root="$(
        sed -n 's/^Snapshot directory:[[:space:]]*//p' "${CURRENT_LOG}" 2>/dev/null |
          tail -n1
      )"
      if [[ -n "${snapshot_root}" ]]; then
        printf '%s\n' "${snapshot_root}" > "${RESUME_STATE_FILE}.tmp"
        mv "${RESUME_STATE_FILE}.tmp" "${RESUME_STATE_FILE}"
        exit 0
      fi
      sleep 10
    done
  ) &
  SNAPSHOT_WATCHER_PID=$!
fi

# === Start cgroup-isolated process monitor (every 60s, per-domain path) ===

MONITOR_LOG="${OUT_DIR}/monitor_${SLURM_JOB_ID}.csv"
echo "[MONITOR] Logging process stats every 60s (auto-cgroup detection) -> ${MONITOR_LOG}"
echo "timestamp,pid,ppid,pcpu,pmem,rss_kb,vsz_kb,cmd" > "$MONITOR_LOG"

# --- Detect cgroup path (v1 or v2) ---
CGROUP_PATH=""
if [ -f /proc/self/cgroup ]; then
    # cgroup v2 usually lists '0::/slurm/uid_xxx/job_xxx/step_xxx'
    CGROUP_PATH=$(awk -F: '{if ($3 ~ /slurm/) print $3}' /proc/self/cgroup | head -n1)
fi

# Try fallback to unified hierarchy (cgroup v2 default mount)
if [ -z "$CGROUP_PATH" ] && [ -d /sys/fs/cgroup/slurm ]; then
    CGROUP_PATH="/slurm/uid_${UID}/job_${SLURM_JOB_ID}"
fi

if [ -n "$CGROUP_PATH" ] && [ -d "/sys/fs/cgroup${CGROUP_PATH}" ]; then
    echo "[MONITOR] Using cgroup path: ${CGROUP_PATH}"
else
    echo "[MONITOR] Warning: could not detect job-specific cgroup path, falling back to user-wide view" >&2
    CGROUP_PATH=""
fi

(
  while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [ -n "$CGROUP_PATH" ] && [ -r "/sys/fs/cgroup${CGROUP_PATH}/cgroup.procs" ]; then
        PIDS=$(cat "/sys/fs/cgroup${CGROUP_PATH}/cgroup.procs" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
        if [ -n "$PIDS" ]; then
            ps -o pid=,ppid=,%cpu=,%mem=,rss=,vsz=,cmd= -p ${PIDS} 2>/dev/null \
              | awk -v ts="$timestamp" '{
                    gsub(",", ";", $7)
                    printf "%s,%s,%s,%s,%s,%s,%s,\"", ts, $1, $2, $3, $4, $5, $6
                    for (i=7; i<=NF; i++) printf "%s%s", $i, (i<NF?" ":"")
                    print "\""
                }'
        fi
    else
        # fallback: all user processes
        ps -u "$USER" -o pid=,ppid=,%cpu=,%mem=,rss=,vsz=,cmd= \
          | awk -v ts="$timestamp" '{
                gsub(",", ";", $7)
                printf "%s,%s,%s,%s,%s,%s,%s,\"", ts, $1, $2, $3, $4, $5, $6
                for (i=7; i<=NF; i++) printf "%s%s", $i, (i<NF?" ":"")
                print "\""
            }'
    fi
    sleep 60
  done >> "$MONITOR_LOG"
) &
MONITOR_PID=$!
cleanup_background_processes() {
  kill "${MONITOR_PID}" 2>/dev/null || true
  wait "${MONITOR_PID}" 2>/dev/null || true
  if [[ -n "${SNAPSHOT_WATCHER_PID}" ]]; then
    kill "${SNAPSHOT_WATCHER_PID}" 2>/dev/null || true
    wait "${SNAPSHOT_WATCHER_PID}" 2>/dev/null || true
  fi
  if [[ -n "${EVAL_WAVE_WATCHER_PID}" ]]; then
    kill "${EVAL_WAVE_WATCHER_PID}" 2>/dev/null || true
    wait "${EVAL_WAVE_WATCHER_PID}" 2>/dev/null || true
  fi
}
trap cleanup_background_processes EXIT
# =========================================================


for ((i=1; i<=MAX_RETRIES; i++)); do
  echo "[RETRY] Attempt $i of $MAX_RETRIES" 
  PROFILE_ARGS=""
  if [[ "${ENABLE_PROFILING:-0}" == "1" ]]; then
    PROFILE_DIR="${OUTPUT_DIR}/worker_profiles/job_${SLURM_JOB_ID}/attempt_${i}"
    mkdir -p "$PROFILE_DIR"
    PROFILE_ARGS="--profiling --profile-dir ${PROFILE_DIR}"
    echo "[PROFILE] Enabled: ${PROFILE_DIR}"
  else
    echo "[PROFILE] Disabled"
  fi

  ATTEMPT_EVAL_START_WAVE_ARG="${EVAL_START_WAVE_ARG:-}"
  if [[ -n "${EVAL_START_WAVE_ARG:-}" && -s "${EVAL_WAVE_STATE_FILE}" ]]; then
    ATTEMPT_EVAL_START_WAVE_ARG="--eval-start-wave $(<"${EVAL_WAVE_STATE_FILE}")"
    echo "[EVAL RESUME] Attempt $i uses ${ATTEMPT_EVAL_START_WAVE_ARG}"
  fi
  EVAL_COMPLETION_FILE_ARG=""
  if [[ "${EVAL_SCHEDULING_ARG:-}" == "--eval-scheduling rolling" ]]; then
    EVAL_COMPLETION_FILE_ARG="--eval-completion-file ${EVAL_COMPLETION_FILE}"
  fi

  apptainer exec $APPTAINER_GPU_FLAG --bind /home/hersco:/home/hersco --bind /home/hersco/apptainer_fake_passwd:/etc/passwd /home/hersco/Docker/image.sif /bin/bash -c "
    echo '[CONTAINER] Entered container on $(hostname)'
  
    # Signal traps for debugging early terminations
    trap 'echo \"[TRAP] SIGTERM received at \$(date)\"' TERM
    trap 'echo \"[TRAP] SIGSEGV received at \$(date)\"' SEGV
    trap 'echo \"[TRAP] SIGUSR1 received at \$(date)\"' USR1
    trap 'echo \"[TRAP] SIGUSR2 received at \$(date)\"' USR2
    trap 'echo \"[TRAP] Exit trap fired at \$(date) with code \$?\"' EXIT
  
  
    cd /home/hersco/bershco-nu-asnets/numeric-asnets/asnets || { echo '[CONTAINER] cd failed'; exit 1; }
    source /home/hersco/bershco-nu-asnets/numeric-asnets/venv-asnets/bin/activate
    export PYTHONPATH=/home/hersco/bershco-nu-asnets/numeric-asnets:\$PYTHONPATH
    echo '[CONTAINER] Activated environment'
    
    ./run_experiment "$ARCHITECTURE_MODULE" \
                   experiments_numeric.domain.$DOMAIN \
                   $RESUME_TRAIN_FLAG \
                   $RESUME_FROM_ARG \
                   $NO_EVAL_FLAG \
                   $EVAL_WITH_MCTS_FLAG \
                   $ATTEMPT_EVAL_START_WAVE_ARG \
                   $EVAL_SCHEDULING_ARG \
                   $SKIP_INSTANCE_NUMBERS_ARG \
                   $EVAL_INSTANCE_TIMEOUT_ARG \
                   $EVAL_COMPLETION_FILE_ARG \
                   --jpddl-max-heap ${JPDDL_MAX_HEAP:-1g} \
                   $ACTION_DEBUG_FLAG \
                   $PUCT_DEBUG_FLAG \
                   --override-mse-coeff $MSE_COEFF \
	               ${PROFILE_ARGS} --worker-logs --num-workers ${NUM_WORKERS} \
                   --mcts-exploration-weight ${EXPLORATION_WEIGHT} \
                   ${ENHSP_CONFIG_OVERRIDE:+--override-enhsp-config ${ENHSP_CONFIG_OVERRIDE}} \
                   $MCTS_EXPANSION_SIZE_ARG $MCTS_ITERATIONS_ARG \
                   --sample-k-additional-states $TREE_SAMPLE \
                   $USE_ESTIMATOR_ARG \
                   $USE_ESTIMATOR_DECAY \
                   $ORIGINAL_TRAINING_SET \
                   $DISABLE_VALUE_HEAD \
                   $DISCARD_FAILED_RUNS \
                   --max-opt-epochs ${OVERRIDE_MAX_EPOCHS:-1000} \
                   --supervised-lr ${OVERRIDE_LR:-0.003} \
                   --policy-anchor-kl-coeff ${POLICY_ANCHOR_KL_COEFF:-0.0} \
                   --random-seed ${SEED}
  "
  STATUS=$?
  update_eval_wave_state
  echo "[RETRY] apptainer exit code: $STATUS" 

  if [ "$STATUS" -eq 0 ]; then
    echo "[RETRY] Success on attempt $i" 
    break
  fi
  echo "[RETRY] Attempt $i failed" 
  if [ "$i" -lt "$MAX_RETRIES" ]; then
    echo "[RETRY] Sleeping for $RETRY_DELAY seconds before next attempt..." 
    sleep "$RETRY_DELAY"
  else
    echo "[ERROR] All $MAX_RETRIES attempts failed. Exiting." 
    exit 1
  fi
done
echo "Current job name: $CURRENT_JOB_NAME"
echo "[VAL] Looking for log: $CURRENT_LOG"
if [[ ! -f "$CURRENT_LOG" ]]; then
    echo "[VAL ERROR] Log file not found: $CURRENT_LOG"
    exit 1
fi

if [[ -z "${NO_EVAL_FLAG:-}" ]] && grep -q "\[EVAL FINAL\]" "$CURRENT_LOG"; then
    echo "[VAL] Evaluation detected, validating printed plans..."

    python /home/hersco/bershco-nu-asnets/numeric-asnets/asnets/tools/validate_eval_log.py \
        --log "$CURRENT_LOG" \
        --domain "$DOMAIN" \
        --validator "/home/hersco/tools/VAL/build/bin/Validate"

    VAL_STATUS=$?

    if [[ "$VAL_STATUS" -ne 0 ]]; then
        echo "[VAL ERROR] Validation guardrail failed"
        exit 1
    fi
else
    echo "[VAL] No evaluation detected, skipping validation"
fi


echo "[SLURM] Job $SLURM_JOB_ID finished" 
