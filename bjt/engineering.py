import math
from typing import Mapping

FIELDS = ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")

DEFAULTS = {
    "vcc": "12",
    "r1": "47000",
    "r2": "10000",
    "rc": "2200",
    "re": "1000",
    "beta": "150",
    "vbe": "0.7",
}

VCE_SAT = 0.2

_POSITIVE_FIELDS = ("vcc", "r1", "r2", "rc", "re", "beta")


def _is_finite(value: float) -> bool:
    try:
        return math.isfinite(value)
    except (TypeError, OverflowError):
        return False


def _validate_values(values: Mapping[str, float]) -> dict[str, str]:
    errors: dict[str, str] = {}

    for name, value in values.items():
        if name in FIELDS and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise TypeError(f"{name} must be a number")

    for field in FIELDS:
        if field in values and not _is_finite(values[field]):
            errors[field] = "must be finite"

    for field in _POSITIVE_FIELDS:
        if field in values and field not in errors and values[field] <= 0:
            errors[field] = "must be greater than zero"

    if "vbe" in values and "vbe" not in errors and values["vbe"] < 0:
        errors["vbe"] = "must be zero or greater"

    if (
        "vbe" in values
        and "vcc" in values
        and "vbe" not in errors
        and "vcc" not in errors
        and values["vbe"] >= values["vcc"]
    ):
        errors["vbe"] = "must be less than VCC"

    return errors


def parse_inputs(raw: Mapping[str, str]) -> tuple[dict[str, float], dict[str, str]]:
    values: dict[str, float] = {}
    errors: dict[str, str] = {}

    for field in FIELDS:
        text = str(raw.get(field, "")).strip()
        if not text:
            errors[field] = "required"
            continue
        try:
            values[field] = float(text)
        except (TypeError, ValueError):
            errors[field] = "must be a number"

    errors.update(_validate_values(values))
    return values, errors


def classify_region(ib: float, vce: float) -> str:
    if ib <= 0:
        return "cutoff"
    if vce < VCE_SAT:
        return "saturation"
    return "active"


def analyze_bias(
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

    rbb = r1 * r2 / (r1 + r2)
    vbb = vcc * r2 / (r1 + r2)
    ib = (vbb - vbe) / (rbb + (beta + 1) * re)

    if ib <= 0:
        return {
            "ib": 0.0,
            "ic": 0.0,
            "ie": 0.0,
            "vb": vbb,
            "ve": 0.0,
            "vc": vcc,
            "vce": vcc,
            "region": "cutoff",
            "warnings": ["Transistor is in cutoff (IB <= 0)."],
        }

    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if not all(_is_finite(value) for value in (ib, ic, ie, vb, ve, vc, vce)):
        raise ValueError("operating point is out of range")

    region = classify_region(ib, vce)
    warnings: list[str] = []
    if region == "saturation":
        warnings.append(
            "Transistor is in saturation (VCE < 0.2 V); active-region equations are not valid."
        )

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
