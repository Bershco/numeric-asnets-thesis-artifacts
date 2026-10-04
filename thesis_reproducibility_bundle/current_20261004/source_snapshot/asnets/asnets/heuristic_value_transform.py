"""Explicit inference transform; legacy exponential remains the default."""
import math

def heuristic_value(h, coefficient=1.0, transform="exp"):
    h = float(h)
    if transform not in ("exp", "reciprocal"):
        raise ValueError("unknown heuristic value transform")
    if math.isnan(h) or h < 0 or coefficient <= 0:
        raise ValueError("invalid heuristic/coefficient")
    if transform == "reciprocal":
        return 1.0 / (1.0 + coefficient * h)
    return math.exp(-coefficient * h)
