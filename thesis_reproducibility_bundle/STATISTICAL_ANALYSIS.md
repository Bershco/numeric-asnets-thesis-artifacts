# Statistical support and recommended replication

## What the current workbook reports

The workbook contains exact coverage counts on fixed test sets. Counters has 59
test instances; the other domains have 20. The lower table reports a 95% Wilson
interval for each coverage proportion.

That interval is descriptive across the fixed instances. It is **not** an
across-seed confidence interval: every displayed final result currently comes
from one selected trained network and one evaluation campaign. Interrupted and
resumed logs complete that same campaign and do not increase the repetition
count.

The RQ1/RQ3 anchor-coefficient comparison itself used two training seeds per
coefficient. That makes the configuration-selection summary stronger than a
single run, but the displayed checkpoint score is still the evaluation of one
selected network. Two seeds are also too few for a stable seed-level interval.

Consequently, the current evidence supports exact statements about these
networks on these test sets, but it does not estimate training-seed variability.
Formal seed-level confidence intervals and significance tests are not yet
available.

## Recommended replication design

For each final selected configuration:

1. predeclare the additional training seeds before observing results;
2. train the identical configuration independently for every seed;
3. apply the same checkpoint-selection rule without looking at test coverage;
4. evaluate every selected checkpoint on the identical ordered test set;
5. retain per-instance solved/unsolved outcomes and plan lengths;
6. compare policy versus MCTS using the same checkpoint and instances;
7. report the mean coverage across seeds with a seed-level interval;
8. report paired per-instance comparisons separately.

Five independent training seeds per configuration is a practical minimum for a
first uncertainty analysis; more is preferable when resources allow. With very
few seeds, show every seed explicitly rather than relying on a normal-theory
interval.

For policy-versus-MCTS comparisons on the same network and instances, a paired
analysis such as McNemar's test can describe discordant solved/unsolved outcomes.
It does not replace replication across independently trained networks. A final
analysis should therefore present both levels:

- variation across training seeds;
- paired differences across the common test instances.

Exploratory narrow-search and increased-budget results must remain labelled as
exploratory unless their configurations are included in the predeclared
replication design.
