from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class VariableDeclaration:
    names: List[str]
    domain: str = "free"


@dataclass(slots=True)
class Equation:
    kind: str
    expression: str
    source_line: int


@dataclass(slots=True)
class BoundStatement:
    expression: str
    source_line: int


@dataclass(slots=True)
class InitialStatement:
    expression: str
    source_line: int


@dataclass(slots=True)
class SolverDirective:
    level: str
    value: str
    source_line: int


@dataclass(slots=True)
class CallbackStatement:
    expression: str
    source_line: int


@dataclass(slots=True)
class GDPModelIR:
    name: Optional[str] = None
    variables: List[VariableDeclaration] = field(default_factory=list)
    objective: Optional[str] = None
    equations: List[Equation] = field(default_factory=list)
    bounds: List[BoundStatement] = field(default_factory=list)
    initials: List[InitialStatement] = field(default_factory=list)
    callbacks: List[CallbackStatement] = field(default_factory=list)
    solver_directives: List[SolverDirective] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "num_variable_blocks": len(self.variables),
            "num_equations": len(self.equations),
            "num_bounds": len(self.bounds),
            "num_initials": len(self.initials),
            "num_callbacks": len(self.callbacks),
            "num_solver_directives": len(self.solver_directives),
            "has_objective": self.objective is not None,
        }
