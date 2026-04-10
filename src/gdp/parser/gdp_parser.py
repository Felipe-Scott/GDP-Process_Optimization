from __future__ import annotations

from typing import List

from gdp.model import (
    GDPModelIR,
    VariableDeclaration,
    Equation,
    BoundStatement,
    InitialStatement,
    CallbackStatement,
    SolverDirective,
)


class GDPParser:
    """
    Minimal but robust line-based parser for .gdp files.

    Goal: exact backward compatibility at the syntax level, without trying
    to evaluate MATLAB constructs. Everything is preserved as strings and
    classified.
    """

    def parse(self, text: str) -> GDPModelIR:
        model = GDPModelIR()

        lines = text.splitlines()
        i = 0

        current_block = None

        while i < len(lines):
            raw = lines[i]
            line = raw.strip()
            i += 1

            if not line or line.startswith("%"):
                continue

            lower = line.lower()

            # ---------------- VARIABLES ----------------
            if lower.startswith("variable"):
                domain = "free"
                if "positive" in lower:
                    domain = "positive"
                elif "binary" in lower:
                    domain = "binary"

                names: List[str] = []

                # read until EndVar
                while i < len(lines):
                    l = lines[i].strip()
                    i += 1
                    if l.lower().startswith("endvar"):
                        break
                    if l:
                        names.extend([v.strip() for v in l.split(",") if v.strip()])

                model.variables.append(VariableDeclaration(names, domain))
                continue

            # ---------------- OBJECTIVE ----------------
            if line.startswith(("fx..", "obj..", "objfun..")):
                model.objective = line
                continue

            # ---------------- EQUATIONS ----------------
            if line.startswith(("eqL..", "eq..", "ecn..", "eqlin..")):
                kind = "linear" if line.startswith("eqL") else "nonlinear"
                model.equations.append(Equation(kind, line, i))
                continue

            # ---------------- BOUNDS ----------------
            if lower.startswith("bounds"):
                while i < len(lines):
                    l = lines[i].strip()
                    i += 1
                    if l.lower().startswith("endbounds"):
                        break
                    if l:
                        model.bounds.append(BoundStatement(l, i))
                continue

            # ---------------- INITIAL ----------------
            if lower.startswith(("initial", "inicial")):
                while i < len(lines):
                    l = lines[i].strip()
                    i += 1
                    if l.lower().startswith(("endinitial", "endinicial")):
                        break
                    if l:
                        model.initials.append(InitialStatement(l, i))
                continue

            # ---------------- SOLVER ----------------
            if line.startswith("Solver."):
                try:
                    left, right = line.split("=")
                    model.solver_directives.append(
                        SolverDirective(left.strip(), right.strip(), i)
                    )
                except ValueError:
                    pass
                continue

            # ---------------- CALLBACK ----------------
            if line.startswith("onl.."):
                expr = line.replace("onl..", "", 1).strip()
                model.callbacks.append(CallbackStatement(expr, i))
                continue

            # fallback: ignore or store later

        return model
