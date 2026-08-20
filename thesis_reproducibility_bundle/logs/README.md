# Evaluation logs

This directory contains the complete evaluation logs supporting the displayed
results. Logs are gzip-compressed without removing lines.

File names encode:

1. domain;
2. RQ/value-head branch;
3. checkpoint stage;
4. policy or MCTS inference;
5. displayed coverage or result status;
6. Slurm job ID.

Some MCTS evaluations were interrupted and resumed. Those results have more
than one constituent log. `../provenance/results_manifest.csv` is authoritative:
its `packaged_logs` column lists every part needed to reconstruct a table cell.
A continuation is part of the same evaluation campaign, not an independent
statistical repetition.

Every completed modern result is labelled with its VAL status in the manifest.
The two Counters stage-1 MCTS results are explicitly scheduler-limited lower
bounds. Stage-1 policy baselines use
their original evaluation evidence; the bundle does not rerun them merely to
create new standalone logs.

To inspect a compressed log:

```bash
gzip -cd path/to/log.log.gz | less
```

To validate the plans again, follow the VAL instructions in the bundle's main
README after decompressing the log.
