import math

from .engineering import _validate_values, classify_region

QUANTITIES = ("ib", "ic", "ie", "vb", "ve", "vc", "vce")

CUTOFF_WARNING = "Transistor is in cutoff (IB <= 0)."
SATURATION_WARNING = (
    "Transistor is in saturation (VCE < 0.2 V); active-region equations are not valid."
)


def solve_bias_independent(
    vcc: float,
    r1: float,
    r2: float,
    rc: float,
    re: float,
    beta: float,
    vbe: float,
) -> dict:
    values = {
        "vcc": vcc,
        "r1": r1,
        "r2": r2,
        "rc": rc,
        "re": re,
        "beta": beta,
        "vbe": vbe,
    }
    errors = _validate_values(values)
    if errors:
        raise ValueError(next(iter(errors.values())))

    vbb = vcc * r2 / (r1 + r2)

    def residual(ib: float) -> float:
        vb = vbe + (beta + 1) * ib * re
        return (vcc - vb) / r1 - vb / r2 - ib

    if residual(0.0) <= 0:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "vb": vbb,
            "ve": 0.0,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "warnings": [CUTOFF_WARNING],
        }

    lo, hi = 0.0, vcc / r1
    while residual(hi) > 0 and hi < 1e12:
        hi *= 2

    for _ in range(200):
        mid = (lo + hi) / 2
        if residual(mid) > 0:
            lo = mid
        else:
            hi = mid

    ib = (lo + hi) / 2
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if not all(math.isfinite(value) for value in (ib, ic, ie, vb, ve, vc, vce)):
        raise ValueError("operating point is out of range")

    region = classify_region(ib, vce)
    warnings = [SATURATION_WARNING] if region == "saturation" else []

    return {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "vb": vb,
        "ve": ve,
        "vc": vc,
        "vce": vce,
        "region": region,
        "warnings": warnings,
    }


def _bisect_base_current(residual, upper: float) -> float:
    lo, hi = 0.0, upper
    while residual(hi) > 0 and hi < 1e12:
        hi *= 2

    for _ in range(200):
        mid = (lo + hi) / 2
        if residual(mid) > 0:
            lo = mid
        else:
            hi = mid

    return (lo + hi) / 2


def _point_from_ib(vcc: float, rc: float, beta: float, vbe: float, ib: float, re: float) -> dict:
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if not all(math.isfinite(value) for value in (ib, ic, ie, vb, ve, vc, vce)):
        raise ValueError("operating point is out of range")

    region = classify_region(ib, vce)
    warnings = [SATURATION_WARNING] if region == "saturation" else []

    return {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "vb": vb,
        "ve": ve,
        "vc": vc,
        "vce": vce,
        "region": region,
        "warnings": warnings,
    }


def solve_fixed_independent(vcc: float, rb: float, rc: float, beta: float, vbe: float) -> dict:
    """Nodal solution for fixed bias: base current from the RB branch."""
    values = {"vcc": vcc, "rb": rb, "rc": rc, "beta": beta, "vbe": vbe}
    errors = _validate_values(values)
    if errors:
        raise ValueError(next(iter(errors.values())))

    ib = _bisect_base_current(lambda i: (vcc - vbe) / rb - i, vcc / rb)
    if ib <= 0:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "vb": vbe,
            "ve": 0.0,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "warnings": [CUTOFF_WARNING],
        }

    return _point_from_ib(vcc, rc, beta, vbe, ib, 0.0)


def solve_emitter_independent(
    vcc: float, rb: float, re: float, rc: float, beta: float, vbe: float
) -> dict:
    """KCL at the base with RE feedback, solved by bisection on IB."""
    values = {"vcc": vcc, "rb": rb, "re": re, "rc": rc, "beta": beta, "vbe": vbe}
    errors = _validate_values(values)
    if errors:
        raise ValueError(next(iter(errors.values())))

    ib = _bisect_base_current(
        lambda i: (vcc - (vbe + (beta + 1) * i * re)) / rb - i,
        vcc / rb,
    )
    if ib <= 0:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "vb": vbe,
            "ve": 0.0,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "warnings": [CUTOFF_WARNING],
        }

    return _point_from_ib(vcc, rc, beta, vbe, ib, re)


def solve_independent(mode: str, values: dict) -> dict:
    """Dispatch to the independent solver for the selected bias mode."""
    if mode == "divider":
        return solve_bias_independent(**values)
    if mode == "fixed":
        return solve_fixed_independent(**values)
    if mode == "emitter":
        return solve_emitter_independent(**values)
    raise ValueError(f"unknown bias mode: {mode}")


def compare_results(
    primary: dict,
    independent: dict,
    rel_tol: float = 1e-6,
    abs_tol: float = 1e-9,
) -> dict:
    deltas = {quantity: independent[quantity] - primary[quantity] for quantity in QUANTITIES}
    matches = all(
        math.isclose(primary[quantity], independent[quantity], rel_tol=rel_tol, abs_tol=abs_tol)
        for quantity in QUANTITIES
    )
    return {"matches": matches, "deltas": deltas}
