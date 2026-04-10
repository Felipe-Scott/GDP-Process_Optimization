from __future__ import annotations

from typing import Callable, Dict, Tuple


def brute_force_optimize(
    executor_factory: Callable[[float], Dict[str, float]],
    objective: Callable[[Dict[str, float]], float],
    a1_min: float,
    a1_max: float,
    step: float = 1.0,
) -> Tuple[float, float, Dict[str, float]]:
    """Very simple optimizer to validate HYSYS + GDP execution loop.

    Parameters
    ----------
    executor_factory
        Function that takes A1 and returns execution context after callbacks.
    objective
        Function mapping context -> scalar objective.
    """
    best_val = float("inf")
    best_a1 = None
    best_ctx = None

    a1 = a1_min
    while a1 <= a1_max:
        ctx = executor_factory(a1)
        val = objective(ctx)

        if val < best_val:
            best_val = val
            best_a1 = a1
            best_ctx = ctx

        a1 += step

    return best_a1, best_val, best_ctx
