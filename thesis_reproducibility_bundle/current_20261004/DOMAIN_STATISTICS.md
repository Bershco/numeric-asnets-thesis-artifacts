# Full six-domain structural and behavioral statistics — 4 October2026

This replaces the successful-plan-length-only summary, not the underlying
historical measurements. [Current packet](README.md)
contains the159-instance native census, explicit state bounds, original problem
paths and hashes. All159 production/local problem texts match after newline
normalization; none is newly claimed byte-identical across Windows/Linux.

## Action and state spaces

Native mdpsim instantiated each exact TEST_RUNS problem in the production
container. Counts below are actual ground action catalogues, **not** Cartesian
parameter estimates and **not** the number applicable in a particular state.
An action space's catalogue size is the same reported ground-action quantity;
applicable branching depends on the state and is not fabricated here.

|Domain|Instances|Lifted actions|Ground actions: mean [min,max]|Propositions mean|Numeric fluents mean¹|Projected state-space magnitude: log10 range²|
|---|---:|---:|---:|---:|---:|---|
|Block Grouping|20|4|87 [20,160]|0|49.5|13.01–111.84, exact coordinate states|
|Counters|59|2|62 [4,120]|0|34|1.40–124.97, exact bounded counter states|
|Drone|20|8|73.1 [9,307]|66.1|211.3|2.68–94.68, upper bound|
|FO Counters|20|4|46 [8,84]|0|27|3.48–56.17, upper bound excluding cost|
|MPrime|20|4|4105.1 [68,17595]|479.3|20.8|13.55–505.53, conservative upper bound|
|Rover|20|10|774.3 [55,4040]|350.45|6.75|21.57–394.43, conservative upper bound excluding recharge metric|

¹ Includes two special simulator functions. The CSV separately records native
comparisons and per-instance minima/maxima. Static numeric bounds are not
dynamic state coordinates.

² A value55 means10^55, not55 states. Ranges span individual instances; a mean
logarithm is a geometric-size summary, not an arithmetic mean state count.
These are physical-state valuations, excluding simulator history/action indices.
Exact reachable graph enumeration was not attempted for the hybrid domains.

Derivations:

- BG: `grid_cells ^ number_of_blocks`; independent bounded unit-coordinate
  moves, with no collision prohibition in this domain.
- Counters: `(max_int+1) ^ number_of_counters`; independent reversible unit
  increments/decrements, each value bounded0..max_int.
- FO: `[11*(max_int+1)] ^ number_of_counters` bounds values and rates0..10.
  Repeatable rate cycles make accumulated total-cost unbounded if retained.
- Drone: `grid_cells*(full_battery+1)*2^locations`; battery/visit constraints
  make many valuations unreachable, hence an upper bound.
- Rover: `2^ground_propositions *101^rovers`; static propositions make this
  very loose. Accumulated recharge cost can be unbounded on repeatable cycles.
- MPrime: `2^ground_propositions * product(initial_harmony+n_pain+1) *
  C(initial_total_locale+n_food,n_food)`. Total locale cannot increase; harmony
  plus associated fears cannot increase. Missing numeric initial entries are
  treated as zero; all pleasure objects participate in the bound.

## Primary-paper classifications

Wang and Thiébaux's **Learning Generalised Policies for Numeric Planning**,
ICAPS2024, Table1 classifies BG/Counters as heavily numeric/simple,
Drone/FO as heavily numeric/linear, and MPrime/Rover as hybrid/simple.
“Simple” permits constant numeric updates; “linear” covers richer linear
arithmetic. “Hybrid” has substantial classical as well as numeric structure.
These are domain categories, not claims that our experimental effects share a
cause. [Official paper](https://ojs.aaai.org/index.php/ICAPS/article/download/31526/33686/35583).

## Distinctive features and empirical diagnostics

|Domain|Structural/observed features; limits on explanation|
|---|---|
|BG|Long coordinate-moving plans and reversible moves. Bounded initial/successor screen:36/120 finite heuristic values underflowed under exp(-h). Selected inverse-action cases exist, but one timeout executed5164 actions with5161 distinct rounded state keys and no two-step returns: not every loss is cycling.|
|Counters|Many bounded reversible counters; long successful policy trajectories. Repaired-on has237 policy-only losses:132 action caps and105 six-hour timeouts. Bounded heuristic screen had0/348 underflow cases. The near-universal zero heuristic finding was **Rover**, not Counters.|
|Drone|3D position, battery and visited-location goals; recharge/resource constraints. Policy/action-history context can matter independently of physical-state identity.|
|FO|Numeric counter values and mutable rates; long wall-time search despite relatively short successful external plans. Accumulated cost is separate from executable physical state.|
|MPrime|Hybrid cravings/fears graph and numeric harmony/locale resources; by far the largest actual ground-action catalogue in this census. HMRP-HA GBFS/AStar flags are equivalent in the verified heuristic-only estimator path.|
|Rover|Classical data/navigation goals plus numeric energy and recharge cost. HMRP-HA returned finite h=0 on1888/1950 V2 non-goal states. The native objective minimizes recharges, not action count; positive-length zero-cost plans can therefore have h=0. This is not evidence of estimator startup timeout.|

## Successful-run behavior and regression budgets

Current displayed successful-run means, VH-off/on respectively; success conditioning
and stage/cohort scope are retained in the source CSV rather than construed as
unconditional domain averages:

|Domain|Policy external actions|MCTS external actions|
|---|---|---|
|BG|442.3 /359.6|336.4 /274.4|
|Drone|92.7 /94.5|70.3 /129.0|
|FO|51.0 /55.0|63.5 /63.6|
|Rover|10.3 /11.9|57.4 /26.1|
|Counters, narrow off /repaired on|973.2 /1559.0|377.4 /447.7|
|MPrime|26.01 /20.35|9.33 /16.17|

For the repaired Counters policy-success/MCTS-failure population specifically:
132 capped searches executed10000 external actions; their successful policies
used mean2403.28 [568,5320]. The105 timeouts' policies used mean2933.76
[813,4772]. Original timeout logs do not contain external action indices:
elapsed time cannot defensibly reconstruct them. The14 selected instrumented
replicas record action/time progress, but do not replace those population scores.
Four Counters nonreproductions originally split2 caps/2 timeouts, so a
context-switching explanation alone cannot account for all four.

## Sources and cross-links

- [Actual native grounding and state-bound means](evidence/six_domain_full_statistics.csv)
- [All159 per-instance counts, bounds and hashes](evidence/domain_instance_grounding_and_state_bounds.csv)
- [Current behavioral source table, repairedCounters-on](evidence/six_domain_current_successful_run_behavior.csv)
- [Historical behavioral table retained separately](evidence/six_domain_successful_run_behavior.csv)
- [All237 policy-only losses with policy steps](evidence/repaired_counters_policy_only_instances_with_steps.csv)
- [Rover objective-unit audit/calibration future work](value_estimation_objectives_and_calibration_future_work_20261003.md)
- [Current configuration axes](EXPLORATORY_AXES.md)

The structural census suggests mechanisms worth checking; it does not establish
that action count, numeric category or state-space magnitude caused a particular
coverage change. Ground catalogue size must not be conflated with retained
search width5/20, simulation count20/70 or executed action limit10000.
