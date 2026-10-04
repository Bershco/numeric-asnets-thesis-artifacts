# Cluster security alert and compute-node-only policy — 3 October 2026

The user received a university IT/security call about numerous Python commands
containing `import base64`. Matching our commands does not by itself exclude
unrelated unauthorized access. Record evidence, not assumptions of compromise.

## Mandatory policy

- First obtain one diagnostic allocation with
  `sinteractive --cpu 2 --mem 8 --time 0-01:00:00` (site syntax).
- Login-node commands: `sinteractive`, `squeue`, exact-job `scancel`, plus the
  quick SSH hop to the allocated compute node explicitly authorized in the
  user's follow-up. All Python, accounting, log/file analysis, deployment and
  process/session checks execute on the allocated compute node.
- Preserve SSH host verification. Use the approved SSH hop if direct compute
  access lacks a cached key; never silently disable security checks.
- Standing user authorization, 4 October 2026: first-use SSH keys may be accepted
  without repeated approval for a BGU compute hostname specifically allocated
  for the current diagnostic session and verified against its own Slurm job.
  Use `StrictHostKeyChecking=accept-new` only for that first connection; retain
  strict verification afterward and reject changed keys. This does not authorize
  arbitrary hosts or accepting a mismatch. Record hostname/job/public fingerprint.
- Reserve 8 GiB within the working 6 TiB account allocation envelope. Do not keep an
  allocation alive 24/7 or inflate requests. A capacity reserve cannot guarantee
  an immediate scheduler start.
- Avoid base64/compressed/encoded executable transport. Prefer readable named
  scripts or plain stdin on compute. Data decoding is distinct; do not substitute
  another encoding to evade IT monitoring.
- Never use a legacy encoded Python login dispatcher. If allocation or
  connection fails, preserve progress and report it; no login fallback.
- Immediately before the final reply, cancel only the diagnostic allocation's
  exact ID and verify absence using `squeue`. Leave scientific jobs untouched.
- Record allocation/hostname, command provenance and evidence limits.

## Interrupted experiment work preserved

The previous report is paused, not discarded or complete. Its evening packet is
`experiment_tracking/campaign_snapshot_20261003_evening/`; narrative publication
and current-navigation updates were not yet finished when interrupted.

- Science19:14:56/queue19:15:50: historical6360/6360,240 seed rows, V212000/12000,
  HER24/24, FO16/16 plus4 controls complete.
- Counters-off intended S1:254/590 goals,25.4/59 vs historical25.7/59;10 source
  training/epoch pairs saved in `counters_off_same_checkpoint_historical_intended.csv`.
- Intended inference: Drone288/800, **FO S2:76/400**, **FO S1:345/400**,
  Counters-off S2:367/590. Repaired Counters S2 six of20 final endpoints,
  fixed449/590 andPW475/590 durable outcomes; no final mean yet.
- Existing caps Drone8->12 andFO-S28->18:14 extra slots,56CPU,1216GiB.
 6080GiB science requests leave64GiB below6144, accommodating8GiB diagnostics
  and12GiB pending collectors. No additional scientific jobs submitted.
- Transform screen32/32 arms,16 pairs:9 both-success,7 both-failure,0 gains/losses.
  Existing complete action-progress traces show two-step state-key returns,
  including Counters with nonzeroQ/no underflow. No new replay or global change.
- Rover audit: native HMRP recharge-cost h differs from V2 action-count labels.
 1888/1950 non-goal samples have finiteh0; not startup failure. See
  `value_estimation_objectives_and_calibration_future_work_20261003.md`.
- Resume by publishing the seven-section report/checklist and current routes;
  do not resubmit already complete evidence.

The resumed21:02 audit/report now exists at
[current report](campaign_status_20261003_resumed.md). It uses diagnostic
allocation22017459 onise-cpu128-03,2CPU/8GiB, approved first-use SSH key and strict
changed-key rejection. Local-authenticated ProxyJump keeps login as a tunnel only;
plain Python input executes on compute. FO-S2 cap18->20 is the only scientific
queue-control change in this resumed session; no new evaluation was submitted.
The current packet owns the fresh storage and exact diagnostic cleanup receipts.

## Known transport pattern

Our helper sent
`python -c 'import base64,zlib;exec(zlib.decompress(base64.b64decode(...)))'`
through `audit_memory_two_months_20260930.ssh` to`hersco@slurm.bgu.ac.il`.
The dispatcher is `submit_intended_leaf_remaining_20261001.remote`; the full
capture helper duplicated that encoding. It avoided quoting/command-size issues
for legitimate experiment queries/deployment, but created opaque executable
commands and ran analysis on login. That was our own implementation decision
and is now prohibited. Do not count copied old artifacts as new executions.

Diagnostic job22001900:2CPU/8GiB,1h scheduler limit, node
`ise-cpu-intl-26.auth.ad.bgu.ac.il`. Direct SSH stalled and was interrupted;
local forwarding failed host verification. The user then expressly authorized
a quick login-to-compute SSH hop. No verification setting was disabled.

Only IT's event/process/source-IP correlation can confirm the exact alert cause
and assess unrelated account access. Normal process snapshots cannot prove an
account has never been compromised. Final findings and cleanup proof belong in
`experiment_tracking/cluster_security_incident_20261003/`.

Investigation details and scope:
[incident evidence](../experiment_tracking/cluster_security_incident_20261003/README.md).
The updated active transport has 12 passing offline safety tests and checks
the live own-job/node allocation before every SSH/SCP operation. These are
guardrails, not a security sandbox or proof of account integrity. Historical
direct encoders are retained as provenance and must not be reused without
migration. Exact IT-event attribution and the live cluster/login-process audit
remain access/evidence-limited, not completed findings.
