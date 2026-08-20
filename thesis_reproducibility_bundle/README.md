# Numeric ASNet thesis reproducibility bundle

This directory packages the evidence and trained networks behind the five-domain
RQ1–RQ4 results table. It is intentionally self-contained at the experiment
level: the repository contains the source code, while this directory contains
the selected table, exact evaluation evidence, selected checkpoints, and the
commands needed to train or evaluate the models.

## Contents

- `results/main_results_table.xlsx` — the single showcased results sheet.
- `results/main_results_table.csv` — machine-readable copy of the same table.
- `STATISTICAL_ANALYSIS.md` — what the current intervals mean, current
  replication limitations, and the recommended multi-seed design.
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
- Apptainer.
- The experiment image described in `container/README.md`.
- This repository checked out at the commit recorded in
  `provenance/software_environment.txt`.
- For plan validation, VAL's `Validate` executable.

The original environment used Python 3 inside the Apptainer image, OpenJDK,
JPype, TensorFlow, ENHSP/JPDDL, and the repository's `venv-asnets` environment.

## One-time setup

```bash
git clone https://github.com/Bershco/numeric-asnets.git
cd numeric-asnets
git lfs pull

# Verify the bundled image.
cd thesis_reproducibility_bundle/container
sha256sum -c image.sif.sha256
cd ../..

# The image is entered with the repository and its parent storage visible.
apptainer exec \
  --bind "$PWD:$PWD" \
  --pwd "$PWD/asnets" \
  thesis_reproducibility_bundle/container/image.sif \
  /bin/bash
```

Inside the container:

```bash
source ../venv-asnets/bin/activate
export PYTHONPATH="$(cd .. && pwd):${PYTHONPATH:-}"
```

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

Example: train one VH-off Block Grouping policy from the original training set.

```bash
./cluster_reference/submit_training.sh \
  --dom-block_grouping \
  --original-only \
  --override-arch comparison \
  --vh-off \
  --seed 42 \
  --supervised-lr 0.003 \
  --max-opt-epochs 1000 \
  --workers 3 \
  --cpus 6 \
  --mem 48G \
  --time 3-00:00:00 \
  --eval
```

Omit `--vh-off` for VH-on/RQ3-style training. Domain-specific no-landmark
architectures use `--domain-architecture policy` and must not be mixed with a
checkpoint produced by a different landmark/input representation.

## Stage-2 MCTS-guided training

Stage 2 resumes from a stage-1 checkpoint. The principal campaigns used a
learning rate of `0.0003`, 100 stage-2 epochs, and explicit policy-anchor
coefficients recorded in `provenance/results_manifest.csv`.

```bash
./cluster_reference/submit_training.sh \
  --dom-block_grouping \
  --original-only \
  --train-from /absolute/path/to/stage1_checkpoint \
  --override-arch comparison_mcts_hadd_gbfs \
  --vh-off \
  --use-estimator 0.5 \
  --exploration-weight 0.1 \
  --override-tree-sampling 0 \
  --policy-anchor-kl-coeff 0.1 \
  --supervised-lr 0.0003 \
  --max-opt-epochs 100 \
  --seed 42 \
  --workers 3 \
  --cpus 6 \
  --mem 48G \
  --time 3-00:00:00
```

Replace the architecture/teacher with the domain-specific values in the
manifest. `--train-from` resumes training; `--eval-from` performs evaluation
only.

## Policy-only evaluation

Use the policy architecture corresponding to the checkpoint, without the
`_mcts` inference suffix and without `--eval-with-mcts`.

```bash
./cluster_reference/submit_training.sh \
  --dom-block_grouping \
  --original-only \
  --eval-from /absolute/path/to/checkpoint \
  --override-arch comparison \
  --vh-off \
  --seed 42 \
  --workers 3 \
  --cpus 6 \
  --mem 20G \
  --time 04:00:00
```

## MCTS evaluation

The normal inference configuration used estimator `0.5`, PUCT `0.1`, expansion
width `20`, and `70` MCTS iterations. Some reported cells use explicitly
labelled narrow or search-budget variants; use the exact values in the
manifest rather than assuming the normal configuration.

```bash
./cluster_reference/submit_training.sh \
  --dom-block_grouping \
  --original-only \
  --eval-from /absolute/path/to/checkpoint \
  --eval-with-mcts \
  --override-arch comparison_mcts_hadd_gbfs \
  --vh-off \
  --use-estimator 0.5 \
  --exploration-weight 0.1 \
  --mcts-expansion-size 20 \
  --mcts-iterations 70 \
  --eval-scheduling rolling \
  --eval-instance-timeout 21600 \
  --jpddl-max-heap 4g \
  --seed 42 \
  --workers 3 \
  --cpus 6 \
  --mem 120G \
  --time 3-00:00:00
```

For VH-on/RQ4 evaluation, omit `--vh-off`. Keep at most three workers: MCTS
inference is memory intensive.

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
python asnets/tools/validate_eval_log.py \
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
