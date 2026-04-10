from __future__ import annotations

import math
from typing import Any, Tuple


def _safe_lmtd(delta_t1: float, delta_t2: float) -> float:
    if delta_t1 <= 0 or delta_t2 <= 0:
        raise ValueError(
            f"Invalid temperature approach for LMTD: delta_t1={delta_t1}, delta_t2={delta_t2}"
        )
    if abs(delta_t1 - delta_t2) < 1e-12:
        return delta_t1
    return (delta_t1 - delta_t2) / math.log(delta_t1 / delta_t2)


def modelo(context: Any, hysys: Any, A1: float, Prob: Any = None) -> Tuple[float, float, float, float]:
    """Python translation of Modelo.m for the Tres_Cambiadores example.

    Parameters
    ----------
    context:
        Execution context from the GDP runtime.
    hysys:
        HYSYS adapter instance. Expected to expose `set_exchanger_ua` and
        `read_tres_cambiadores_state` helper methods, or equivalent project-
        specific methods added later.
    A1:
        Area of exchanger 1.
    Prob:
        Reserved for compatibility with legacy callback signatures.
    """
    Tincw = 50.0
    Toutcw = 90.0
    Tins = 284.0
    Touts = 284.0
    U2 = 0.5
    U3 = 1.0
    HTF1 = 1.5

    if hysys is None:
        raise RuntimeError("modelo callback requires a HYSYS adapter")

    if hasattr(hysys, "set_exchanger_ua"):
        hysys.set_exchanger_ua("E-101 UA", A1 * HTF1)
    if hasattr(hysys, "run"):
        hysys.run()

    if not hasattr(hysys, "read_tres_cambiadores_state"):
        raise RuntimeError(
            "HYSYS adapter must implement read_tres_cambiadores_state() for this example"
        )

    state = hysys.read_tres_cambiadores_state()
    Tinhot = state["Tinhot"]
    Touthot = state["Touthot"]
    Tcoldin = state["Tcoldin"]
    Tcoldout = state["Tcoldout"]
    Q2 = state["Q2"]
    Q3 = state["Q3"]

    delta_t_cooler_lm = _safe_lmtd(Tins - Tcoldout, Touts - Tcoldin)
    delta_t_heater_lm = _safe_lmtd(Tinhot - Toutcw, Touthot - Tincw)

    A2 = Q2 / (U2 * delta_t_cooler_lm)
    A3 = Q3 / (U3 * delta_t_heater_lm)
    return Q2, Q3, A2, A3
