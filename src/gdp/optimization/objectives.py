from __future__ import annotations

from typing import Mapping


def tres_cambiadores_total_area_cost(context: Mapping[str, float]) -> float:
    """Simple pilot objective for Tres Cambiadores.

    This is intentionally lightweight: it lets us optimize a real HYSYS-coupled
    callback before the full LogicOA and full cost structure are ported.
    """
    a1 = float(context.get("A1", 0.0))
    a2 = float(context.get("A2", 0.0))
    a3 = float(context.get("A3", 0.0))
    return a1 + a2 + a3
