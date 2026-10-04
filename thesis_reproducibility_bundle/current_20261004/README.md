# Six-domain thesis evidence and evaluation release — October4,2026

This dated release supersedes the old five-domain bundle as the results entrypoint.
The old bundle is retained as dated evidence, not silently relabeled. MAIN-VAL
includes Block Grouping, Drone, FO Counters, Counters, Rover and MPrime: both VH
modes, both stages, ten historical seeds each,6360 terminal identities. Current
oracle figure replaces its teacher-confounded Counters-on cell with the repaired
teacher-correct lineage. Historical tables retain the older cohort separately;
the populations are never pooled.

## Reproduce the reported statistics without the cluster

Use Python3.10+; this command uses only the standard library:

```bash
python thesis_reproducibility_bundle/current_20261004/recompute_statistics.py
```

It recomputes all52 exact paired-seed tests, their common Holm adjustment and
the240-seed/6360-identity denominator checks. The oracle SVG/PNG, source CSVs,
all/non-goal V2 tables and full native-grounding census are in `evidence/`.

## Run policy or MCTS evaluation on an existing compatible checkpoint

First install the pinned environment and native planners using the parent
bundle's installation instructions. Evaluation entrypoints do not install
dependencies, train new networks, submit jobs or connect to the cluster.

```bash
python thesis_reproducibility_bundle/current_20261004/evaluate_checkpoint.py \
  --repo /path/to/clone --domain block_grouping --vh off \
  --checkpoint /path/to/checkpoint --seed 1963100312 \
  --inference fixed --leaf-mode intended --instance 1 \
  --expected-sha CHECKPOINT_SHA256 --output /path/to/new/completion.jsonl
```

This is a dry run. Inspect the printed checkpoint hash, teacher/leaf roles,
search budget and effective instance RNG, then add `--execute` on a compute
node. `--inference policy` uses exactly the same weights; `pw` enables the
explicit documented widening parameters. `--instance` is one-based and keeps
the original base-seed+position−1 RNG. Existing outputs are never overwritten.
The wrapper requires explicit VH and leaf mode; flags alone do not prove that
the estimator executed correctly. Retain its runtime configuration log and
completion records, then independently validate returned plans with VAL.

`evaluate.sbatch` is a portable scheduler example, not a universal resource
default. Set partition/account, installed Python/container and measured memory
for your site. Current one-worker completion evidence supports64GiB for
Counters/Drone and96GiB for FO;3-worker parents can need192GiB. Requesting less
must not turn operational OOMs into scientific failures.

## Checkpoints, dependencies and reproducibility boundary

The legacy `weights/` directory contains65 files representing20 selected networks
(15 weights.joblib and5 Stage1.pkl files, plus45 optimizer/trainer/debug files);
it does **not** contain every240-seed endpoint or the newly repaired Counters
networks. Current CSVs retain original absolute cluster paths as provenance,
not portable runnable paths. `checkpoint_inventory.csv` enumerates bundled
files, network/support roles and hashes. To replay a current seed, obtain the exact weight
identified by its source/epoch/SHA ledger from the experiment owner, place it
locally and pass its actual path/hash. Missing checkpoints are not substituted
by the old bundled network from the same domain. Current problem files and
explicit estimator/teacher flags must also match the selected cohort.

This release therefore supports complete **evidence/statistics replay** and
a reusable evaluation workflow, but does not claim an independently repeated
full240-network training/search campaign. The full native runtime is not newly
rebuilt during this packaging turn. Current Python runtime files are updated
in the repository and preserved under `source_snapshot/`, with file hashes and the dirty
source-repository revision recorded in `release_manifest.json`.

Manifests preserve the original packaging-machine byte SHA and also give an
LF-normalized SHA for text, because Git checkouts can convert Windows/Linux
line endings. Network-weight and image hashes are binary byte hashes, never
newline-normalized. Do not interpret an expected text newline conversion as a
different scientific checkpoint or certify arbitrary other content changes.

## Evidence navigation

- `REPORT.md`: current seven-section scientific/operational report.
- `PLAN.md`: deadline checklist with denominators.
- `DOMAIN_STATISTICS.md`:159-instance actual grounding and explicit state bounds.
- `EXPLORATORY_AXES.md`: tested axes, results and non-expansion decisions.
- `evidence/rq_all_stage_cutoffs.csv`: all stages, policy/MCTS time cutoffs.
- `evidence/rq_paired_seed_observations.csv`: same-checkpoint seed results.
- `evidence/configuration_axes.csv`: all17 implemented/tested/proposed axes.
- `evidence/experiment_inventory.csv`: current/completed/gated experiments.
- `evidence/manifest_sha256.csv`: file integrity checks for this release.

Remote analysis must run on a small allocated compute node, not a login-node
Python dispatcher. No encoded executable transport is included. Allocate,
verify, work, cancel only that diagnostic allocation and verify its absence.
The working6TiB envelope reserves8GiB for the next diagnostic session.
