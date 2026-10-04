"""Durable, bounded external-action traces for selected MCTS evaluations."""

import hashlib
import json
import math
import os
from pathlib import Path
import time


def should_sample_action(action_index):
    """Use one-based external-action indices: 1..200, 300, 400, ..."""
    return action_index > 0 and (
        action_index <= 200 or action_index % 100 == 0)


def _finite(value):
    value = float(value)
    return value if math.isfinite(value) else None


def state_key_hex(state):
    key = getattr(state, "state_key", None)
    if isinstance(key, bytes):
        return key.hex()
    return None


def _instance_prefix(instance_path, evaluation_index, pid):
    identity = hashlib.sha256(str(instance_path).encode("utf-8")).hexdigest()[:12]
    position = str(evaluation_index) if evaluation_index is not None else "unknown"
    return f"instance-{position}-{identity}-pid{pid}-"


def root_snapshot(mcts, masked_pi, selected_action, duplicate_penalty):
    """Capture values as they stood at the external choice, before re-rooting."""
    root = mcts.curr_tree_root
    children = root.children
    rows = []
    if children is not None and not children.is_empty():
        trajectory = root.get_child_on_trajectory_mask()
        for index, (action, child) in enumerate(children.items()):
            action = int(action)
            duplicate = bool(index < len(trajectory) and trajectory[index] > 0)
            rows.append({
                "action": action,
                "prior": _finite(children.priors[index]),
                "edge_visits": int(children.visits[index]),
                "child_visits": int(child.visit_count),
                "q": _finite(child.Q_value),
                "mcts_probability": _finite(masked_pi[action]),
                "on_trajectory": duplicate,
                # A zero factor suppresses duplicates before the selector's
                # fallback; goal chase and safe fallback can still choose one.
                "duplicate_eligible": not duplicate or duplicate_penalty is None
                                      or duplicate_penalty > 0,
                "child_state_key_hex": state_key_hex(child.state),
            })
    return {
        "root_state_key_hex": state_key_hex(root.state),
        "root_visits": int(root.visit_count),
        "duplicate_penalty": duplicate_penalty,
        "duplicate_eligibility_stage": "before_goal_chase_and_fallback",
        "selected_action": int(selected_action),
        "selected_on_trajectory": next(
            (row["on_trajectory"] for row in rows
             if row["action"] == selected_action), None),
        "children": rows,
    }


class MechanismTrace:
    """One file per instance attempt; every JSONL record is flushed and synced."""

    def __init__(self, directory, *, instance_path, evaluation_index, start_time):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        filename = (_instance_prefix(instance_path, evaluation_index, os.getpid())
                    + f"{time.time_ns()}.jsonl")
        self.path = directory / filename
        self.start_time = start_time
        self._file = self.path.open("x", encoding="utf-8")
        self.write({"event": "start", "instance_path": str(instance_path),
                    "evaluation_index": evaluation_index,
                    "elapsed_seconds": 0.0})

    def write(self, record):
        self._file.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
        self._file.flush()
        os.fsync(self._file.fileno())

    def elapsed(self):
        return max(0.0, time.time() - self.start_time)

    def exit(self, *, reason, action_index, state, hit_goal, error=None):
        self.write({"event": "exit", "reason": reason,
                    "action_index": action_index,
                    "elapsed_seconds": self.elapsed(),
                    "state_key_hex": state_key_hex(state),
                    "hit_goal": bool(hit_goal), "error": error})

    def close(self):
        self._file.close()


def append_hard_timeout(directory, *, instance_path, evaluation_index, pid,
                        elapsed_seconds):
    """Record a supervisor kill after the process has stopped writing."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    prefix = _instance_prefix(instance_path, evaluation_index, pid)
    candidates = sorted(directory.glob(prefix + "*.jsonl"))
    path = candidates[-1] if candidates else directory / (prefix + "hard-timeout.jsonl")
    last_index = 0
    last_state = None
    if path.exists():
        with path.open("r", encoding="utf-8") as source:
            for line in source:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("event") == "action":
                    last_index = record["action_index"]
                    last_state = record.get("state_key_after_hex")
    record = {
        "event": "exit", "reason": "hard_timeout",
        "action_index_lower_bound": last_index,
        "action_index_exact": False,
        "elapsed_seconds": float(elapsed_seconds),
        "state_key_last_recorded_hex": last_state,
        "hit_goal": False,
    }
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
        output.flush()
        os.fsync(output.fileno())
    return path
