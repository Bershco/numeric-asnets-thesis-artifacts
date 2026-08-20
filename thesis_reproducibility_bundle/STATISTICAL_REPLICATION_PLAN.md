# Five-domain statistical replication plan

## Objective

The current results establish exact coverage for selected trained networks, but
they do not yet estimate variation across independently trained networks.  The
confirmatory campaign will repeat the complete stage-1 -> stage-2 lineage under
matched seeds, then evaluate policy and MCTS inference on the same selected
checkpoints and ordered test instances.

The statistical unit is an independently trained lineage.  Re-evaluating the
same checkpoint with a different random seed measures inference variability;
it is not an independent training replicate.

## Audit result

The historical and current audit scanned 80,379 candidate parent/canonical
logs and parsed 76,945 experiment records across Block Grouping, Drone, FO
Counters, Rover, and Counters.

For every selected domain/value-head configuration:

- the selected anchor coefficient has completed stage-2 jobs for seeds 42 and
  2026;
- those two jobs resume from one shared stage-1 checkpoint;
- both stage-2 learning curves have policy-only evaluations;
- the displayed final policy/MCTS comparison is based on one selected trained
  network;
- repeated checkpoint evaluations and continuation logs do not add independent
  training replicates.

Accordingly, the archive provides two conditional stage-2 seeds but only one
stage-1 source per selected configuration.  It does not provide five or ten
independent end-to-end replications for any displayed table cell.

## Predeclared additional seeds

The displayed result supplies one existing trained network per cell. The
following nine additional seeds were generated once from Python's deterministic
`random.Random(20260820)` stream and must be used across every domain and both
value-head conditions:

```text
1963100312, 2011206605, 1073581256, 1239739722, 1472491096,
534933607, 2082152039, 1510771779, 923500475
```

All nine are one declared cohort and may be submitted together. Slurm array or
controller concurrency limits should restrict how many memory-heavy tasks run
at once; that is resource throttling, not a statistical wave or stopping rule.
Seed `1972442430` is reserved as a tenth fresh matched seed if the advisors
require ten prospective pairs rather than nine new pairs plus the existing
displayed network.

Nine new lineages plus the displayed lineage give ten networks per table cell.
With only five paired seeds, a two-sided exact sign-flip test cannot reach
p < 0.05 even if all five differences have the same sign. Nine prospective
matched seeds can reach that threshold and give a materially more interpretable
interval. Because several legacy VH-off stage-1 seeds were time-generated or
not recorded, the clean paired RQ3 analysis has nine prospective pairs; report
the ten-network cell summaries as a sensitivity analysis that includes the
legacy displayed result.

## Fixed training protocol

Each seed creates ten matched lineages: five domains times VH off/on.

- Stage 1: original training set, learning rate 0.003, domain-specific policy
  architecture and teacher, maximum three workers.
- Stage 2: resume only the matching stage-1 seed/checkpoint; learning rate
  0.0003; 100 epochs; estimator 0.5; PUCT 0.1; tree sampling 0; domain/VH anchor
  from the gap manifest; maximum three workers.
- Checkpoint selection: use only the declared validation rule.  Never select a
  checkpoint using test coverage.
- Evaluation: identical ordered test set, same selected checkpoint for policy
  and MCTS, maximum three MCTS workers, rolling completion manifest, six-hour
  per-instance limit, immediate plan printing, and VAL validation.

The displayed narrow/search-budget settings are predeclared as the inference
configuration for the cells that currently use them.  Normal configurations
retained in parentheses remain sensitivity results and must not be silently
mixed with the primary configuration.

## Required outputs per lineage

1. completed stage-1 training log and validation-selected checkpoint;
2. stage-1 policy evaluation with per-instance outcomes and VAL results;
3. stage-1 MCTS evaluation with the declared domain/VH search configuration;
4. completed stage-2 training log and validation-selected checkpoint;
5. stage-2 policy evaluation on that exact checkpoint;
6. stage-2 MCTS evaluation on that same checkpoint;
7. optional-but-recommended every-five stage-2 policy curve (epochs 0, 5,
   ..., 95, 99), never used for checkpoint selection.

The additional-nine campaign requires 90 stage-1 training jobs, 90 stage-2
training jobs, 180 selected-checkpoint policy evaluations, and 180 primary MCTS
evaluations: 540 core Slurm tasks. Thirty-six explicitly labelled secondary
normal/narrow/search-budget evaluations bring the job manifest to 576 tasks.
Complete every-five curves add 1,890 cheap policy-evaluation tasks. Submit the
cohort together but throttle concurrent execution; do not run all memory-heavy
MCTS evaluations simultaneously.

## Research-question estimands

For seed `i`, calculate coverage on the fixed domain test set.

- RQ1: VH-off stage-2 policy minus VH-off stage-1 policy.
- RQ2: VH-off stage-2 MCTS minus policy on the identical stage-2 checkpoint.
  Stage-1 MCTS remains a prespecified secondary comparison.
- RQ3: difference in policy improvement:
  `(VH-on stage2 - VH-on stage1) - (VH-off stage2 - VH-off stage1)`.
  Stage-2 learning-curve AUC is a secondary metric when full curves exist.
- RQ4: VH-on stage-2 MCTS minus policy on the identical stage-2 checkpoint.
  Stage-1 MCTS remains a prespecified secondary comparison.

## Confidence intervals and tests

For every domain and RQ:

- show all ten seed-level values;
- report mean, median, standard deviation, and a paired seed-bootstrap 95%
  confidence interval for the mean difference;
- run an exact paired sign-flip/randomization test on the seed-level
  differences;
- apply Holm correction across the five domain tests within each RQ;
- retain the paired per-instance solved/unsolved table and McNemar result as a
  secondary diagnostic, not as a substitute for training-seed replication.

The fixed test instances are not independent training seeds.  Wilson intervals
over 20 or 59 test instances and seed-level confidence intervals answer
different questions and must remain separately labelled.

## Repository roles

- `Bershco/numeric-asnets` remains the development and cluster-production
  repository.  New training/evaluation launchers and analysis code belong
  there first.
- `Bershco/numeric-asnets-thesis-artifacts` is a separate, stable advisor-facing
  reproducibility snapshot containing selected source, weights, logs, table,
  provenance, requirements, and the Apptainer image.

The project did not switch repositories.  After the confirmatory campaign is
complete, selected final evidence can be copied into a new version of the
artifact repository.
