#!/usr/bin/env python3
"""Recompute the sealed52 exact paired-seed tests and Holm family offline."""
import csv,itertools,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):return list(csv.DictReader((ROOT/'evidence'/n).open(encoding='utf-8-sig')))
diff=read('rq_statistical_seed_differences.csv');tests=read('rq_statistics.csv')
assert len(tests)==52 and len({r['test_id'] for r in tests})==52
assert len(diff)==520 and len({(r['test_id'],r['seed']) for r in diff})==520
assert {r['test_id'] for r in diff}=={r['test_id'] for r in tests}
assert all(abs(float(r['comparison'])-float(r['baseline'])-float(r['difference']))<1e-10 for r in diff)
for r in tests:
 d=[float(x['difference']) for x in diff if x['test_id']==r['test_id']];assert len(d)==10
 p=sum(abs(sum(a*b for a,b in zip(s,d)))>=abs(sum(d))-1e-10 for s in itertools.product((-1,1),repeat=10))/1024
 assert abs(p-float(r['raw_p']))<1e-12 and abs(statistics.mean(d)-float(r['effect']))<1e-12
running=0
for rank,r in enumerate(sorted(tests,key=lambda r:float(r['raw_p']))):
 running=max(running,min(1,(len(tests)-rank)*float(r['raw_p'])));assert abs(running-float(r['primary_holm_p']))<1e-12
seeds=read('rq_paired_seed_observations.csv');scope=read('historical_terminal_6360_identity_scope.csv')
assert len(seeds)==240 and len(scope)==6360 and all(r['current_terminal']=='true' for r in scope)
assert len({(r['domain'],r['vh'],r['stage'],r['seed']) for r in seeds})==240
assert len({r['identity'] for r in scope})==6360
cells={(r['domain'],r['vh'],r['stage']) for r in seeds};assert len(cells)==24
for cell in cells:
 ss={r['seed'] for r in seeds if (r['domain'],r['vh'],r['stage'])==cell};assert len(ss)==10
 rs=[r for r in scope if (r['domain'],r['vh'],r['stage'])==cell]
 assert len(rs)==10*(59 if cell[0]=='counters' else 20) and {r['seed'] for r in rs}==ss
 assert len({(r['seed'],r['original_instance_number']) for r in rs})==len(rs)
for test in tests:
 domain=test['domain'].replace('counters_repaired','counters');known={r['seed'] for r in seeds if r['domain']==domain}
 assert all(r['seed'] in known for r in diff if r['test_id']==test['test_id'])
print(json.dumps(dict(seed_rows=240,historical_cells=24,terminal_identities=6360,tests=len(tests),minimum_two_sided_p=2/1024,minimum_first_Holm_adjusted_p=len(tests)*2/1024,all_exact_statistics_reproduced=True),indent=2))
