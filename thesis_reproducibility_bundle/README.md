# Numeric ASNet thesis reproducibility bundle

This directory packages the evidence and trained networks behind the five-domain
RQ1–RQ4 results table. It is intentionally self-contained at the experiment
level: the repository contains the source code, while this directory contains
the selected table, exact evaluation evidence, selected checkpoints, and the
commands needed to train or evaluate the models.

## Quick start: clean installation

Run these commands on a compute node with a sufficiently long allocation. The
initial dependency installation and planner compilation can take more than two
hours, although package caches make subsequent installations faster.

### 1. Create a clean directory and clone the complete bundle

```bash
cd "$HOME"
mkdir numeric-asnets-clean
cd numeric-asnets-clean

git lfs install

GIT_LFS_SKIP_SMUDGE=1 git clone \
  https://github.com/Bershco/numeric-asnets-thesis-artifacts.git

cd numeric-asnets-thesis-artifacts

git lfs pull
git lfs fsck
```

### 2. Enter the supplied Apptainer image

```bash
apptainer exec \
  --bind "$HOME:$HOME" \
  --pwd "$PWD/asnets" \
  thesis_reproducibility_bundle/container/image.sif \
  /bin/bash
```

The shell should now display an `Apptainer>` prompt. A message such as
`groups: cannot find name for group ID ...` is harmless.

### 3. Create and activate a clean virtual environment

Run the remaining commands inside Apptainer:

```bash
python3 -m venv ../venv-asnets
source ../venv-asnets/bin/activate

type -P python
python --version
```

### 4. Install the pinned packaging tools

```bash
python -m pip install \
  "pip==25.1.1" \
  "setuptools==59.6.0" \
  "wheel==0.45.1"
```

### 5. Install the pinned dependencies

```bash
python -m pip install \
  -r ../thesis_reproducibility_bundle/requirements.txt
```

### 6. Install Numeric ASNets

```bash
python -m pip install -e . --no-deps
```

If a compute allocation ends during this step, request another compute node,
enter the same image from the same checkout, reactivate `../venv-asnets`, and
repeat only this command. The installation is resumable; do not reinstall all
dependencies.

### 7. Verify the completed environment

```bash
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

python -m pip check

python -c \
  "import tensorflow, jpype, mdpsim, ssipp, pddl_parser, asnets; print('Environment OK')"
```

A successful clean installation ends with:

```text
No broken requirements found.
Environment OK
```

TensorFlow messages about registering CUDA, cuDNN, cuFFT, or cuBLAS factories
are harmless when running these CPU experiments.

## Contents

- `results/main_results_table.xlsx` — the single showcased results sheet.
- `results/main_results_table.csv` — machine-readable copy of the same table.
- `STATISTICAL_ANALYSIS.md` — what the current intervals mean, current
  replication limitations, and the recommended multi-seed design.
- `STATISTICAL_REPLICATION_PLAN.md` — the audited five-domain seed gap, fixed
  confirmatory seed set, required jobs, and planned confidence-interval/tests.
- `logs/` — exact evaluation logs, named by domain, research question, stage,
  inference type, and Slurm job ID.
- `weights/` — the stage-1 and selected stage-2 checkpoints used by those
  evaluations.
- `provenance/results_manifest.csv` — the authoritative link from each table
  cell to its checkpoint, evaluation log(s), configuration, score, and VAL
  status.
- `provenance/cluster_manifests/` — original submission/selection manifests
  retained for auditing.
- `cluster_reference/` — the actual Slurm and Apptainer wrappers used on the
  BGU cluster. They contain cluster-specific paths and should be adapted on a
  different system.
- `container/image.sif` — the exact Apptainer image, stored with Git LFS.
- `container/README.md` — how to download, verify, and use the image.
- `requirements.txt` — the pinned Python 3.10.12 package environment exported
  from the actual cluster virtual environment.

## Important result-status notes

The manifest is the source of truth. It distinguishes:

- a completed, VAL-confirmed result;
- a result reconstructed from an initial job plus one or more continuation
  logs;
- an exploratory narrow/search-budget result;
- a scheduler-limited lower bound from an evaluation that reached its allocation.

Do not treat `>=N` as a complete-test score. In the exported table this applies
to the two Counters stage-1 MCTS evaluations and the narrow Counters RQ2 result.

The workbook's statistical-support section reports formula-driven Wilson 95%
intervals over the fixed test instances and the available repetition counts.
These are not across-seed confidence intervals. Each displayed final cell
currently uses one selected network and one evaluation campaign; see
`STATISTICAL_ANALYSIS.md` before making significance claims.

## Requirements

- Linux (the experiments were run under Slurm, but Slurm is not required for a
  direct single-process run).
- Git and Git LFS.
- Apptainer.
- The experiment image described in `container/README.md`.
- This repository checked out at the commit recorded in
  `provenance/software_environment.txt`.
- For plan validation, VAL's `Validate` executable.

The original environment used Python 3 inside the Apptainer image, OpenJDK,
JPype, TensorFlow, ENHSP/JPDDL, and the repository's `venv-asnets` environment.

## Installation details

`pddl_parser` version 1.2 is installed from its pinned upstream Git commit
because that exact package is not published on PyPI.

The editable ASNet installation also checks out and builds the pinned
production revisions of Fast Downward and the SSiPP solver when they are
absent. It uses the active virtual environment's Python interpreter. On Slurm,
the Fast Downward build respects `SLURM_CPUS_PER_TASK` instead of
unconditionally compiling with 16 workers.

The virtual environment is created on the writable host filesystem while its
Python interpreter and native dependencies come from the supplied image. On an
existing BGU checkout, the already-created `venv-asnets` may be activated
instead, but it is not required for a fresh installation.

## Cluster execution

The exact working wrappers are included in `cluster_reference/`. Before using
them on another cluster, change these site-specific values:

1. repository path;
2. results/output path;
3. `image.sif` path;
4. VAL executable path;
5. Slurm partition, excluded nodes, CPU, memory, and time settings;
6. bind mounts and the optional fake-passwd file.

Use `submit_training.sh --dry-run` first. It prints the complete grid and job
count without submitting anything.

## Stage-1 imitation training

Run these commands from the repository's `asnets/` directory inside Apptainer.
The example below trains Drone with its domain-specific policy architecture.

```bash
DOMAIN=drone
POLICY_ARCH=experiments_numeric.architecture_2.drone
SEED=42

./run_experiment \
  "$POLICY_ARCH" \
  "experiments_numeric.domain.$DOMAIN" \
  --original-training-set \
  --supervised-lr 0.003 \
  --max-opt-epochs 1000 \
  --num-workers 3 \
  --jpddl-max-heap 4g \
  --random-seed "$SEED" \
  --worker-logs \
  --no-eval \
  2>&1 | tee ../stage1_${DOMAIN}_seed${SEED}.log
```

This is VH-on/RQ3-style stage-1 training. Add `--disable-value-head` for a
VH-off/RQ1 network. Replace both `DOMAIN` and `POLICY_ARCH` together; the
available domain-specific modules are under
`experiments_numeric/architecture_2/`. Do not load a checkpoint using a
different policy architecture, landmark setting, or value-head mode.

## Stage-2 MCTS-guided training

Stage 2 resumes training from a compatible stage-1 checkpoint and changes the
exploration algorithm to MCTS. The established campaigns used learning rate
`0.0003`, 100 stage-2 epochs, estimator coefficient `0.5`, and an explicitly
selected anchor coefficient.

```bash
DOMAIN=drone
MCTS_ARCH=experiments_numeric.architecture_2.drone_mcts
STAGE1_CHECKPOINT=/absolute/path/to/stage1_checkpoint
SEED=42
ANCHOR_COEFF=0.1

./run_experiment \
  "$MCTS_ARCH" \
  "experiments_numeric.domain.$DOMAIN" \
  --resume-from "$STAGE1_CHECKPOINT" \
  --resume-train \
  --original-training-set \
  --use-estimator 0.5 \
  --mcts-exploration-weight 0.1 \
  --sample-k-additional-states 0 \
  --policy-anchor-kl-coeff "$ANCHOR_COEFF" \
  --supervised-lr 0.0003 \
  --max-opt-epochs 100 \
  --num-workers 3 \
  --jpddl-max-heap 4g \
  --random-seed "$SEED" \
  --worker-logs \
  --no-eval \
  2>&1 | tee ../stage2_${DOMAIN}_seed${SEED}.log
```

Add `--disable-value-head` when the stage-1 source is VH-off/RQ1; omit it for
VH-on/RQ3. Use the matching `<domain>_mcts` architecture and the exact
domain-specific coefficient selected in `provenance/results_manifest.csv`.

## Policy-only evaluation

The same policy-only command evaluates either a stage-1 or stage-2 checkpoint.
Use the matching policy architecture without the `_mcts` suffix.

```bash
DOMAIN=drone
POLICY_ARCH=experiments_numeric.architecture_2.drone
CHECKPOINT=/absolute/path/to/checkpoint
SEED=42

./run_experiment \
  "$POLICY_ARCH" \
  "experiments_numeric.domain.$DOMAIN" \
  --resume-from "$CHECKPOINT" \
  --num-workers 3 \
  --jpddl-max-heap 4g \
  --random-seed "$SEED" \
  --worker-logs \
  2>&1 | tee ../policy_${DOMAIN}_seed${SEED}.log
```

Add `--disable-value-head` for a VH-off/RQ1 or RQ2 checkpoint. Omit it for a
VH-on/RQ3 or RQ4 checkpoint. Validate every completed policy log with VAL as
shown below.

## MCTS evaluation

The normal inference configuration used estimator `0.5`, PUCT `0.1`, expansion
width `20`, and `70` MCTS iterations. Some reported cells use explicitly
labelled narrow or search-budget variants; use the exact values in the
manifest rather than assuming the normal configuration.

```bash
DOMAIN=drone
MCTS_ARCH=experiments_numeric.architecture_2.drone_mcts
CHECKPOINT=/absolute/path/to/checkpoint
SEED=42
COMPLETION_FILE="../evaluation-state/${DOMAIN}_seed${SEED}.jsonl"
mkdir -p ../evaluation-state

./run_experiment \
  "$MCTS_ARCH" \
  "experiments_numeric.domain.$DOMAIN" \
  --resume-from "$CHECKPOINT" \
  --eval-with-mcts \
  --use-estimator 0.5 \
  --mcts-exploration-weight 0.1 \
  --mcts-expansion-size 20 \
  --mcts-iterations 70 \
  --eval-scheduling rolling \
  --eval-instance-timeout 21600 \
  --eval-completion-file "$COMPLETION_FILE" \
  --jpddl-max-heap 4g \
  --random-seed "$SEED" \
  --num-workers 3 \
  --worker-logs \
  2>&1 | tee ../mcts_${DOMAIN}_seed${SEED}.log
```

Add `--disable-value-head` for RQ2/VH-off and omit it for RQ4/VH-on. Keep at
most three workers: MCTS inference is memory intensive. The normal values above
must be replaced by the explicitly reported narrow or search-budget values
when reproducing one of those labelled cells.

## Resume an interrupted evaluation

Rolling evaluation stores completed instances in a JSONL completion file and
does not repeat successful or definitively unsolved instances. Timeout/crash
instances remain eligible for retry. The older wave interface is retained for
backward compatibility:

```bash
# Preferred: reuse the completion file produced by the wrapper.
--eval-scheduling rolling

# Optional explicit exclusions for already finished one-based positions.
--skip-instance-numbers 1,4,7

# Legacy wave continuation.
--eval-start-wave 3
```

## VAL plan validation

The cluster wrapper automatically validates a completed evaluation log when it
contains an `[EVAL FINAL]` record. To validate manually:

```bash
python tools/validate_eval_log.py \
  --log /path/to/evaluation.log \
  --domain block_grouping \
  --validator /path/to/VAL/build/bin/Validate
```

The validator checks every printed plan and fails when evaluator successes and
VAL-valid plans disagree.

## Reproducing a table cell

1. Locate the row in `provenance/results_manifest.csv`.
2. Use the named file under `weights/`.
3. Run policy-only or MCTS evaluation with the recorded architecture, value-head
   mode, teacher, estimator, PUCT, width, iterations, seed, timeout, and test
   set.
4. Validate the produced plans with VAL.
5. Compare the resulting summary with the packaged log(s) and manifest score.

When a result required continuation jobs, all constituent logs are listed in
the same manifest row; do not interpret only the final continuation log as the
entire test set.
