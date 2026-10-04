# State-value objectives and per-domain calibration — 3 October 2026

Current evidence: [October4 live report](campaign_status_20261004_live.md),
[V2 final tables and label identities](../experiment_tracking/campaign_snapshot_20261004_live/README.md),
[inference-only transform screen](value_transform_screen_20261003.md).
This interpretation supersedes the earlier unqualified claim that Rover's large
native-ENHSP MAE establishes an intrinsically bad heuristic. It does not alter
any stored prediction, label, MAE or historical search outcome.

## Rover: same HMRP algorithm, different objective units

All 20 local Rover test problems declare `(:metric minimize (recharges))`.
The domain increments this fluent only in `recharge`; navigation, sampling and
communication can require actions without adding recharge cost.
The V2 estimator uses the requested `hmrp-ha-gbfs` configuration:
`-s gbfs -h hmrp -ha true`, without `-uch` (unit-cost heuristic override).
In the attached Java source, `ProblemTransfomer.generateCompactProblem` obtains
native metric action costs unless unitary cost is requested. H1's HMRP relaxed
plan estimate sums those action costs, rather than counting every action.
Helpful actions do not change those units. MPrime's local test PDDLs do not
declare this recharge objective, so using the same HMRP algorithm does not make
the two domains' heuristic units identical.

V2 instead labels a state with `1/(1+L)`, where L is the action count of an
independently obtained, simulated-to-goal plan. Its stored `planner_result.cost`
is the sum of simulator step costs; `state_reprs.sample_next_state` explicitly
uses `step_cost=1`. This field is therefore not a native ENHSP recharge-cost
certificate. Native cost-optimal labels are already distinguished from
shortest-action-certified labels; keep that distinction.

The saved Rover observations are:

| Seed | Non-goal labels | Finite h=0 | Other finite h |
| --- | ---: | ---: | ---: |
| 534933607 | 972 | 949 | 23 at h=1 |
| 923500475 | 978 | 939 | 39 at h=1 |
| Total | 1,950 | 1,888 (96.8%) | 62 at h=1 |

Those finite returns are not startup timeouts or empty-response fallbacks.
The wrapper initializes missing h to infinity, not zero. An estimated zero
remaining recharge cost can legitimately coexist with a positive remaining
action count; relaxation can also underestimate recharge requirements.
The source-level objective mismatch explains why zero is possible. It does
not prove the exact relaxed-plan reasoning of every saved state or that every
returned h is perfectly accurate. Most labels are correlated observations
from one productive instance per seed, not 1,950 independent instances.

Rover's ENHSP MAEs remain recorded as native-config descriptive results:
all states .8692/.8727, non-goal .8942/.8923. They must not be presented as
an apples-to-apples action-distance benchmark or as proof of a broken HMRP.
The S1 versus S2 head comparison remains meaningful: both heads are scored
against the identical independent labels, and S2 worsens in both Rover pairs.

Evidence:
[objective audit](../experiment_tracking/campaign_snapshot_20261003_evening/rover_value_objective_audit.json),
[20 problem checks](../experiment_tracking/campaign_snapshot_20261003_evening/rover_problem_objective_checks.csv),
[saved-label frequencies](../experiment_tracking/campaign_snapshot_20261003_evening/rover_h_zero_frequency.csv).
Relevant implementation: `problems/numeric/rover/domain.pddl`,
`asnets/asnets/interfaces/enhsp_interface.py`, `post_training/enhspwrapper.py`,
`asnets/asnets/state_reprs.py`, and `scripts/run_value_head_independent_planner_20260927.py`.
Attached Java implementation under `CheckingHowToGetHeuristic/jpddlplus/src/main/java`:
`enhsp2/ENHSP.java`, `pddl/heuristics/advanced/ProblemTransfomer.java` and `H1.java`.

## Calibration is future work, not a V2-selected production change

V2 motivates checking whether a domain-specific head/heuristic blend predicts
useful values. It does not validate fitting a weight on these same states and
reporting the fitted error as held-out accuracy. There is no globally changed
blend, heuristic configuration or training target.

A defensible continuation would:

- [ ] Audit heuristic objective units in every domain before fitting any blend.
- [ ] Compare action-length labels with a unit-cost heuristic, or use cost labels
  with cost-predicting heads; do not silently equate cost and action distance.
- [ ] Divide calibration and evaluation by donor instance/checkpoint groups,
  not random neighboring states that leak trajectory information.
- [ ] Freeze interpolation parameters using only calibration groups.
- [ ] Test held-out prediction error, goal/non-goal strata and certificate classes.
- [ ] Perform matched inference-only MCTS evaluation including successful controls,
  retaining checkpoint/RNG/budget/leaf/limits and gained/lost instances.

With the October18 deadline, this remains future work. The completed 32-arm
exp versus reciprocal inference screen is a separate bounded configuration
trial: it changes the transform, not fitted interpolation, and observed no
coverage gains or losses in 16 paired cases. A reciprocal function avoids finite
underflow but does not align different objective units by itself.

Cross-session navigation also references this document from the evidence index,
exploratory trial/stop-decision document, V2 implementation and acceleration
records, transform-screen report and current closure checklist.
