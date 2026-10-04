#!/usr/bin/env python3
"""Portable, dry-run-first evaluation; explicit teacher/leaf and same-weight SHA."""
import argparse,hashlib,json,os,shlex,subprocess
from pathlib import Path
CONFIG={
 'block_grouping':('hadd-gbfs','hadd-gbfs',5,20),
 'drone':('hadd-astar','hmrp-gbfs',20,70),
 'fo_counters':('hmrmax-astar','hadd-gbfs',20,70),
 'counters':('hmrmax-astar','hmrp-ha-ht-gbfs',5,20),
 'rover':('hmrp-ha-gbfs','hmrp-ha-gbfs',20,70),
 'mprime':('hmrp-ha-gbfs','hmrp-ha-astar',20,70),
}
def build(a):
 root=a.repo.resolve();cp=a.checkpoint.resolve();weight=cp/'weights.joblib' if cp.is_dir() else cp
 if not (root/'asnets/run_experiment').is_file():raise ValueError('Repository evaluation entrypoint is absent')
 if not weight.is_file():raise ValueError('Checkpoint weights do not exist: '+str(weight))
 sha=hashlib.sha256(weight.read_bytes()).hexdigest()
 if a.expected_sha and sha!=a.expected_sha:raise ValueError('Checkpoint SHA-256 mismatch')
 teacher,intended,width,iterations=CONFIG[a.domain]
 leaf=a.leaf or (intended if a.leaf_mode=='intended' else teacher)
 base=['./run_experiment','experiments_numeric.architecture_2.'+a.domain+'_mcts','experiments_numeric.domain.'+a.domain,'--resume-from',str(cp),'--random-seed',str(a.seed+(a.instance-1 if a.instance else 0)),'--override-enhsp-config',teacher,'--override-mcts-enhsp-config',leaf,'--num-workers',str(a.workers),'--jpddl-max-heap','4g','--worker-logs','--eval-scheduling','rolling','--eval-instance-timeout',str(a.timeout),'--eval-completion-file',str(a.output.resolve())]
 if a.vh=='off':base+=['--disable-value-head']
 if a.inference!='policy':
  base+=['--eval-with-mcts','--mcts-expansion-size',str(a.width or width),'--mcts-iterations',str(a.iterations if a.iterations is not None else iterations),'--mcts-exploration-weight','0.1','--use-estimator','0.5']
  if a.inference=='pw':base+=['--mcts-progressive-widening','--mcts-pw-min-width','3','--mcts-pw-c','0.6','--mcts-pw-alpha','0.5']
 if a.instance:base+=['--restrict-test-probs',str(a.instance-1)]
 return dict(repo=str(root),checkpoint=str(cp),weights_sha256=sha,vh=a.vh,teacher=teacher,leaf=leaf,width=a.width or width,iterations=a.iterations if a.iterations is not None else iterations,inference=a.inference,base_seed=a.seed,effective_seed=a.seed+(a.instance-1 if a.instance else 0),configuration_role='explicit exploratory override' if a.leaf or a.width is not None or a.iterations is not None else 'documented domain inference configuration; reported-cell reproduction still requires manifest/data parity',command=base)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--domain',choices=CONFIG,required=True);p.add_argument('--vh',choices=['off','on'],required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--expected-sha');p.add_argument('--seed',type=int,required=True);p.add_argument('--inference',choices=['policy','fixed','pw'],required=True);p.add_argument('--leaf-mode',choices=['teacher','intended'],required=True);p.add_argument('--leaf');p.add_argument('--width',type=int);p.add_argument('--iterations',type=int);p.add_argument('--instance',type=int);p.add_argument('--workers',type=int,default=1);p.add_argument('--timeout',type=int,default=21600);p.add_argument('--output',type=Path,required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
 if a.instance is not None and not 1<=a.instance<=(59 if a.domain=='counters' else 20):p.error('Instance is outside the frozen test pool')
 if a.workers<1 or a.timeout<1 or (a.width is not None and a.width<1) or (a.iterations is not None and a.iterations<0):p.error('Workers, timeout and width must be positive; iterations may be zero for the explicitly requested automatic rule')
 record=build(a);print(json.dumps(record,indent=2))
 if not a.execute:return
 if not a.expected_sha:p.error('Execution requires --expected-sha; do not silently substitute checkpoint weights')
 if not os.environ.get('SLURM_JOB_ID') and not os.environ.get('ALLOW_LOCAL_EVALUATION'):p.error('Execution requires a compute allocation, or explicit ALLOW_LOCAL_EVALUATION=1 on another computer')
 if a.output.exists():p.error('Output already exists; reconcile before repeating scientific work')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 proof=a.output.with_suffix(a.output.suffix+'.preflight.json');proof.write_text(json.dumps(record,indent=2))
 subprocess.run(record['command'],cwd=a.repo/'asnets',check=True)
if __name__=='__main__':main()
