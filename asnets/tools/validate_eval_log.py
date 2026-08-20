#!/usr/bin/env python3

import argparse
import ast
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional


DEFAULT_ASNETS_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DOMAIN_MODULE_DIR = DEFAULT_ASNETS_DIR / "experiments_numeric" / "domain"


PLAN_RE = re.compile(
    r"\[EVAL\]\[PLAN\]\s+"
    r"(?P<difficulty>[^|]+?)\s*\|\s*"
    r"(?P<instance>[^|]+?)\s*\|\s*"
    r"steps=(?P<steps>[0-9]+)\s*\|\s*"
    r"plan=(?P<plan>.*)$"
)

EVAL_FINAL_RE = re.compile(
    r"\[EVAL FINAL\]\s+success=(?P<succ>[0-9]+(?:\.[0-9]+)?)/(?P<total>[0-9]+(?:\.[0-9]+)?)"
)


def fail(msg: str) -> None:
    print(f"[VAL ERROR] {msg}", flush=True)
    sys.exit(1)


def load_domain_module(domain: str, module_dir: Path):
    module_path = module_dir / f"{domain}.py"
    if not module_path.exists():
        fail(f"Domain module not found: {module_path}")

    spec = importlib.util.spec_from_file_location(f"val_domain_{domain}", module_path)
    if spec is None or spec.loader is None:
        fail(f"Could not load module spec for: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module_path


def resolve_pddl_dir(module, asnets_dir: Path) -> Path:
    if not hasattr(module, "PDDL_DIR"):
        fail("Domain module has no PDDL_DIR")

    pddl_dir = Path(module.PDDL_DIR)

    if pddl_dir.is_absolute():
        resolved = pddl_dir
    else:
        # Important:
        # PDDL_DIR is written relative to the asnets/ working directory,
        # e.g. '../problems/numeric/counters'
        resolved = (asnets_dir / pddl_dir).resolve()

    if not resolved.exists():
        fail(f"PDDL_DIR does not exist after resolving: {resolved}")

    return resolved


def get_common_pddls(module, pddl_dir: Path) -> List[Path]:
    if not hasattr(module, "COMMON_PDDLS"):
        fail("Domain module has no COMMON_PDDLS")

    common = []
    for rel in module.COMMON_PDDLS:
        path = (pddl_dir / rel).resolve()
        if not path.exists():
            fail(f"COMMON_PDDL not found: {path}")
        common.append(path)

    if not common:
        fail("COMMON_PDDLS is empty")

    return common


def build_test_instance_map(module, pddl_dir: Path) -> Dict[str, List[Path]]:
    if not hasattr(module, "TEST_RUNS"):
        fail("Domain module has no TEST_RUNS")

    instance_map: Dict[str, List[Path]] = {}

    for test_run in module.TEST_RUNS:
        # Expected structure:
        #   ([rel_pddl_1, rel_pddl_2, ...], something)
        rel_pddls = test_run[0]

        full_paths = []
        for rel in rel_pddls:
            path = (pddl_dir / rel).resolve()
            if not path.exists():
                fail(f"TEST_RUN PDDL not found: {path}")
            full_paths.append(path)

        # Map by basename, because stdout prints only fz_instance_11.pddl,
        # not vanilla/fz_instance_11.pddl.
        for path in full_paths:
            base = path.name
            if base in instance_map:
                fail(
                    f"Ambiguous instance basename in TEST_RUNS: {base}\n"
                    f"Existing: {instance_map[base]}\n"
                    f"New     : {full_paths}"
                )
            instance_map[base] = full_paths

    if not instance_map:
        fail("No TEST_RUNS instances found")

    return instance_map


def parse_eval_final_count(log_path: Path) -> Optional[Tuple[int, int]]:
    final_count = None

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = EVAL_FINAL_RE.search(line)
            if not m:
                continue

            succ_float = float(m.group("succ"))
            total_float = float(m.group("total"))

            succ = int(round(succ_float))
            total = int(round(total_float))

            if abs(succ_float - succ) > 1e-6:
                fail(f"Evaluator success count is not an integer: {succ_float}")

            if abs(total_float - total) > 1e-6:
                fail(f"Evaluator total count is not an integer: {total_float}")

            final_count = (succ, total)

    return final_count


def normalize_action(action: str) -> str:
    action = action.strip()

    if not action:
        fail("Empty action found in plan")

    # Backwards-compatible:
    #   increment c1
    #   (increment c1)
    if not (action.startswith("(") and action.endswith(")")):
        action = f"({action})"

    return action


def parse_plan_lines(log_path: Path) -> List[dict]:
    plans = []

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            m = PLAN_RE.search(line)
            if not m:
                continue

            instance_name = m.group("instance").strip()
            difficulty = m.group("difficulty").strip()
            steps = int(m.group("steps"))
            plan_repr = m.group("plan").strip()

            try:
                parsed = ast.literal_eval(plan_repr)
            except Exception as e:
                fail(f"Could not parse plan at line {lineno}, instance={instance_name}: {e}")

            actions = []

            for item in parsed:
                # New preferred format:
                #   ['increment c1', 'increment c2']
                if isinstance(item, str):
                    action = item

                # Old format:
                #   [(3, 'increment c1'), ...]
                elif isinstance(item, tuple) and len(item) >= 2:
                    action = item[1]

                else:
                    fail(
                        f"Unsupported plan item at line {lineno}, instance={instance_name}: "
                        f"{repr(item)}"
                    )

                if not isinstance(action, str):
                    fail(
                        f"Action is not a string at line {lineno}, instance={instance_name}: "
                        f"{repr(action)}"
                    )

                actions.append(normalize_action(action))

            if len(actions) != steps:
                print(
                    f"[VAL WARNING] steps field differs from parsed action count for "
                    f"{instance_name}: steps={steps}, actions={len(actions)}",
                    flush=True,
                )

            plans.append(
                {
                    "difficulty": difficulty,
                    "instance": instance_name,
                    "steps": steps,
                    "actions": actions,
                    "lineno": lineno,
                }
            )

    return plans


def write_plan_file(plan: dict, out_dir: Path) -> Path:
    instance_stem = Path(plan["instance"]).stem
    out_path = out_dir / f"{instance_stem}.plan"

    with out_path.open("w", encoding="utf-8") as f:
        for action in plan["actions"]:
            f.write(action)
            f.write("\n")

    return out_path


def run_val(
    validator: Path,
    common_pddls: List[Path],
    instance_pddls: List[Path],
    plan_file: Path,
) -> Tuple[bool, str]:
    cmd = [str(validator)]
    cmd.extend(str(p) for p in common_pddls)
    cmd.extend(str(p) for p in instance_pddls)
    cmd.append(str(plan_file))

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    out = proc.stdout or ""

    # VAL commonly prints "Plan valid" on success.
    valid = re.search(
        r"\bPlan valid\b",
        out,
        flags=re.IGNORECASE,
    ) is not None

    return bool(valid), out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse [EVAL][PLAN] lines from a Slurm log and validate them with VAL."
    )

    parser.add_argument("--log", required=True, help="Path to Slurm stdout log")
    parser.add_argument("--domain", required=True, help="Domain name, e.g. counters")
    parser.add_argument("--validator", required=True, help="Path to VAL Validate binary")

    parser.add_argument(
        "--asnets-dir",
        default=str(DEFAULT_ASNETS_DIR),
        help=f"Path to asnets dir. Default: {DEFAULT_ASNETS_DIR}",
    )

    parser.add_argument(
        "--domain-module-dir",
        default=str(DEFAULT_DOMAIN_MODULE_DIR),
        help=f"Path to experiments_numeric/domain. Default: {DEFAULT_DOMAIN_MODULE_DIR}",
    )

    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep generated temporary .plan files",
    )

    args = parser.parse_args()

    log_path = Path(args.log).resolve()
    validator = Path(args.validator).resolve()
    asnets_dir = Path(args.asnets_dir).resolve()
    domain_module_dir = Path(args.domain_module_dir).resolve()

    if not log_path.exists():
        fail(f"Log file not found: {log_path}")

    if not validator.exists():
        fail(f"VAL validator not found: {validator}")

    if not os.access(validator, os.X_OK):
        fail(f"VAL validator is not executable: {validator}")

    print("[VAL] Starting validation guardrail", flush=True)
    print(f"[VAL] Log       : {log_path}", flush=True)
    print(f"[VAL] Domain    : {args.domain}", flush=True)
    print(f"[VAL] Validator : {validator}", flush=True)

    eval_count = parse_eval_final_count(log_path)
    if eval_count is None:
        print("[VAL] No [EVAL FINAL] line found; skipping validation", flush=True)
        return 0

    evaluator_successes, evaluator_total = eval_count

    module, module_path = load_domain_module(args.domain, domain_module_dir)
    pddl_dir = resolve_pddl_dir(module, asnets_dir)
    common_pddls = get_common_pddls(module, pddl_dir)
    instance_map = build_test_instance_map(module, pddl_dir)

    print(f"[VAL] Domain module : {module_path}", flush=True)
    print(f"[VAL] PDDL dir      : {pddl_dir}", flush=True)
    print(f"[VAL] COMMON_PDDLS  : {', '.join(str(p) for p in common_pddls)}", flush=True)

    plans = parse_plan_lines(log_path)

    print(f"[VAL] Evaluator successes : {evaluator_successes}", flush=True)
    print(f"[VAL] Evaluator total     : {evaluator_total}", flush=True)
    print(f"[VAL] Plans found         : {len(plans)}", flush=True)

    if len(plans) != evaluator_successes:
        fail(
            f"Printed plan count differs from evaluator success count: "
            f"plans={len(plans)}, evaluator_successes={evaluator_successes}"
        )

    if evaluator_successes == 0:
        print("[VAL] No successful plans to validate; validation successful", flush=True)
        return 0

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix=f"val_plans_{args.domain}_{log_path.stem}_",
            dir=str(log_path.parent),
        )
    )

    valid_count = 0
    invalid = []

    try:
        for plan in plans:
            instance_name = plan["instance"]
            instance_base = Path(instance_name).name

            if instance_base not in instance_map:
                invalid.append(
                    {
                        "instance": instance_name,
                        "reason": f"Instance basename not found in TEST_RUNS: {instance_base}",
                        "output": "",
                    }
                )
                print(f"[VAL] FAIL {instance_name} -- not found in TEST_RUNS", flush=True)
                continue

            plan_file = write_plan_file(plan, temp_dir)
            instance_pddls = instance_map[instance_base]

            is_valid, val_output = run_val(
                validator=validator,
                common_pddls=common_pddls,
                instance_pddls=instance_pddls,
                plan_file=plan_file,
            )

            if is_valid:
                valid_count += 1
                print(f"[VAL] OK   {instance_name}", flush=True)
            else:
                invalid.append(
                    {
                        "instance": instance_name,
                        "reason": "VAL rejected plan",
                        "output": val_output,
                    }
                )
                print(f"[VAL] FAIL {instance_name}", flush=True)

        print("", flush=True)
        print("[VAL] ===== VALIDATION SUMMARY =====", flush=True)
        print(f"[VAL] Evaluator successes : {evaluator_successes}", flush=True)
        print(f"[VAL] Printed plans       : {len(plans)}", flush=True)
        print(f"[VAL] VAL-valid plans     : {valid_count}", flush=True)
        print(f"[VAL] VAL-invalid plans   : {len(invalid)}", flush=True)
        print("[VAL] =================================", flush=True)

        if valid_count != evaluator_successes:
            print("", flush=True)
            print("[VAL ERROR] Evaluator and VAL disagree", flush=True)

            for item in invalid[:10]:
                print("", flush=True)
                print(f"[VAL ERROR] Instance: {item['instance']}", flush=True)
                print(f"[VAL ERROR] Reason  : {item['reason']}", flush=True)

                if item["output"]:
                    print("[VAL ERROR] VAL output:", flush=True)
                    print(item["output"], flush=True)

            if len(invalid) > 10:
                print(
                    f"[VAL ERROR] Showing first 10 invalid plans only; "
                    f"{len(invalid) - 10} more invalid plans omitted.",
                    flush=True,
                )

            return 1

        print("[VAL] Validation successful: evaluator and VAL agree", flush=True)
        return 0

    finally:
        if args.keep_temp:
            print(f"[VAL] Keeping temp plans at: {temp_dir}", flush=True)
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
