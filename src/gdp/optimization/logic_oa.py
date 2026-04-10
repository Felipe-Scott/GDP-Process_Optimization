from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(slots=True)
class OAIteration:
    iteration: int
    x_value: float
    objective_value: float
    context: Dict[str, float]


@dataclass(slots=True)
class LogicOAResult:
    best_x: Optional[float]
    best_objective: float
    best_context: Optional[Dict[str, float]]
    iterations: List[OAIteration] = field(default_factory=list)


class LogicOAContinuous:
    """Initial continuous-only OA-style driver.

    This is intentionally lightweight. It does not yet build a full linearized
    master problem; instead it establishes the execution pattern we will need
    later for HYSYS-coupled OA/GDP:

    1. propose a candidate x
    2. evaluate the callback/simulator-backed NLP
    3. store incumbent and trace
    4. update candidate according to a pluggable strategy
    """

    def __init__(
        self,
        evaluator: Callable[[float], Dict[str, float]],
        objective: Callable[[Dict[str, float]], float],
        x_name: str = "A1",
    ) -> None:
        self.evaluator = evaluator
        self.objective = objective
        self.x_name = x_name

    def solve(
        self,
        x0: float,
        step: float = 1.0,
        max_iter: int = 10,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ) -> LogicOAResult:
        current_x = x0
        best_x: Optional[float] = None
        best_objective = float("inf")
        best_context: Optional[Dict[str, float]] = None
        history: List[OAIteration] = []

        direction = -1.0

        for k in range(1, max_iter + 1):
            trial_x = current_x
            if lower_bound is not None:
                trial_x = max(lower_bound, trial_x)
            if upper_bound is not None:
                trial_x = min(upper_bound, trial_x)

            context = self.evaluator(trial_x)
            value = self.objective(context)
            history.append(
                OAIteration(
                    iteration=k,
                    x_value=trial_x,
                    objective_value=value,
                    context=context,
                )
            )

            if value < best_objective:
                best_objective = value
                best_x = trial_x
                best_context = context
                current_x = trial_x + direction * step
            else:
                direction *= -1.0
                step *= 0.5
                current_x = trial_x + direction * step

        return LogicOAResult(
            best_x=best_x,
            best_objective=best_objective,
            best_context=best_context,
            iterations=history,
        )
