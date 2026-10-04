# Exploratory configuration trials, tested axes and lineage-stop decisions

Current as of4October2026; [current report](REPORT.md),
[machine-readable17-axis index](evidence/configuration_axes.csv),
[full structural/behavioral domain statistics](DOMAIN_STATISTICS.md).
This supersedes old pending side-comparison descriptions; archived sources remain.

## Completed two-seed training screens

Every entry is a control→treatment mean out of20. Training cost has already
been paid; HER24/24, FO16/16+historical controls4/4 and BG8/8 search tasks are
closed. Same-seed original/control/treatment and gained/lost-instance tables
are retained in the packet.

|Intervention|Policy|Fixed|PW|
|---|---|---|---|
|BG off K0→K10|15→14.5|14.5→15|Treatment15; no equivalent reused PW control|
|BG on K0→K10|11.5→16|11→16.5|Treatment16.5; same limitation|
|FO off K0→K10|4→4|9→8.5|7.5→10|
|FO on K0→K10|2→1.5|5→3|7→5|
|MPrime off HER|17.5→17|16.5→16.5|18.5→18.5|
|MPrime on HER|18→17.5|16.5→17|19→20|
|Rover on HER|4→4|5→4|4.5→4|

FO-off K10 PW's two seeds scored14 and6. Six is below the user-approved
second-seed gate8: do not expand to5 seeds. The K0 PW mean7.5→K10 PW10 is
positive in this tested screen, not evidence of a universally favorable K10.
MPrime-on HER PW improved19→20 in both seeds; preserve that positive result.
No broad K10/HER expansion before submission is a deadline/cohort decision,
not a claim that these interventions are universally ineffective.

## All configuration axes and existing results

|Axis|What it changes; evidence already obtained|
|---|---|
|Expansion/admission|Fixed top-k versus PW, width and admission schedule. Multi-domain fixed/PW exists; Drone width-only8.7 versus8.6/20; MPrime S2 fixed→PW16.6→17.9 off,16→17.2 on.|
|Simulation allocation|Search effort before an external action, not width. Selected Rover70→200 gives6→8/20; two Drone70→140 cells unchanged6→6 and2→2.|
|Tree selection|PUCT score/exploration/prior, versus untested isolated UCT alternative. PUCT mainline and limited coefficient screens exist.|
|Q backup|Mean sampled return is used. Max backup is untested; root Q tie-breaking does not change backup semantics.|
|Leaf source/config/transform|Network, ENHSP or blend; teacher versus domain-planning configuration; exp(-h) versus reciprocal. Main and leaf-source studies, V2 and32-arm transform screen exist. Transform screen16pairs:9 both solve,7 both fail,0 gains/losses.|
|External action decision|Visits/tie rules and goal chase, distinct from simulation selection. Selected tie rescues and ten-seed confirmation exist; goal chase is enabled. No mandatory chase ablation.|
|State identity/context|SAFE-CONTEXT affects sharing statistics/predictions, not action eligibility. Drone off8.8→8.4/on10.8→7.4 in its bounded cohort; horizon-indexed SAFE2 untested.|
|Eligibility/safety|Duplicate/path filtering, terminal-child exclusion, fallback. SAFE-1 rescued2/4 selected failures; broad successful-instance harm screen untested.|
|Remaining executable horizon|Budget-aware depth; bounded Drone/Counters screens had no coverage gain. This is not the external simulation budget.|
|Search organization|Profiling: selected BG successor generation55.2%, estimation32.4%, selection4.4%. Bilevel/path-batched methods not evaluated.|
|Training target construction|Visit distributions used; hard-action-target isolated efficacy not established.|
|Tree Sampling K|Adds original-goal internal states. Historical K−1/K0:28cells/two seeds, BG+1, FO+.5, Drone/Rover0; older extraction semantics differ from current K10.|
|HER|Relabels goals, distinct from original-goal tree sampling. Completed selected-anchor comparisons above.|
|Anchor strength|Coefficient grids; repaired Counters anchor10 selected from validation, policy33.5/59; search still active.|
|KL objective semantics|Stochastic-current versus deterministic-current distribution, not coefficient. Drone fixed5→6/PW5.5→6.5; FO fixed9→7/PW8.5→8, two seeds. Concluded; stochastic-current retained.|
|Replay/optimization|Resume/replay/learning-rate safeguards implemented; no universally isolated coverage benefit claimed.|
|Architecture/input|VH on/off main comparison and independent V2. Broad depth/width/history ablation not completed. Network width is not tree width.|

Historical and intended estimator results can be reported as retrospective
configuration sensitivity, with actual checkpoint/budget/training differences.
Do not rewrite the experimental history as a prospectively controlled factorial
study or erase useful historical results. Runtime leaf evidence, not teacher
flags alone, determines the estimator label.

## Defensible thesis wording

- Completed matched comparison: “Under these tested conditions, A achieved…”
- Two-seed screen: “No improvement was observed in these tested cells,” or
  “the tested cells had positive/adverse/unchanged outcomes.”
- Selected failure-only diagnostic: “This mechanism occurred in selected cases.”
- Unimplemented alternative: future work, not an experimentally rejected method.

Interpolation calibration remains future work: fit on separate donor/instance
groups, distinguish planner cost from action distance, and then evaluate MCTS.
V2's correlated states must not be treated as12000 independent replications.

## Machine-readable evidence

- [Original/control/treatment scores](evidence/side_original_control_treatment_scores.csv)
- [Paired means](evidence/side_paired_cohort_means.csv)
- [Gained/lost instance memberships](evidence/side_gained_lost_instance_pairs.csv)
- [Explicit non-expansion decisions](evidence/side_nonexpansion_decisions.csv)
- [Current experiment registry](evidence/experiment_inventory.csv)
- [Deadline plan](PLAN.md)
