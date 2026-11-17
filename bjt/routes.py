from flask import Blueprint, render_template, request

from .engineering import FIELDS, analyze_bias, parse_inputs
from .formatting import format_with_unit
from .independent import compare_results, solve_bias_independent

bp = Blueprint("bias", __name__)

# Unit choices offered in the form. Values are converted back to SI base units
# (V, Ω) before they reach the engineering core, so that module stays unit-free.
UNITS: dict[str, tuple[tuple[str, float], ...]] = {
    "vcc": (("V", 1.0), ("mV", 1e-3)),
    "r1": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "r2": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "rc": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "re": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "beta": (("–", 1.0),),
    "vbe": (("V", 1.0), ("mV", 1e-3)),
}

DEFAULT_UNITS = {field: UNITS[field][0][0] for field in FIELDS}

# First render uses kΩ for the resistors (matches the lab handout); posted forms
# without a unit selector fall back to the SI base unit.
FORM_UNITS = {**DEFAULT_UNITS, "r1": "kΩ", "r2": "kΩ", "rc": "kΩ", "re": "kΩ"}

# Values shown on the first page load (the lab's rough-target example circuit).
FORM_DEFAULTS = {
    "vcc": "12.0",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1.0",
    "beta": "100",
    "vbe": "0.70",
}

_FORM_LABELS = {
    "vcc": ("V", "CC", "Supply Voltage"),
    "r1": ("R", "1", "Upper Divider"),
    "r2": ("R", "2", "Lower Divider"),
    "rc": ("R", "C", "Collector Resistor"),
    "re": ("R", "E", "Emitter Resistor"),
    "beta": ("β", "", "Current Gain"),
    "vbe": ("V", "BE", "Base–Emitter Voltage"),
}


def _scale_for(field: str, unit: str) -> float:
    return dict(UNITS[field]).get(unit, 1.0)


def _read_form(form) -> tuple[dict[str, str], dict[str, str]]:
    """Read the raw text and the selected unit for every field."""
    texts: dict[str, str] = {}
    units: dict[str, str] = {}
    for field in FIELDS:
        texts[field] = form.get(field, "").strip()
        unit = form.get(f"{field}_unit", DEFAULT_UNITS[field])
        units[field] = unit if unit in dict(UNITS[field]) else DEFAULT_UNITS[field]
    return texts, units


def _to_base_units(texts: dict[str, str], units: dict[str, str]) -> dict[str, str]:
    """Convert typed values into SI base units, leaving bad text for the validator."""
    scaled: dict[str, str] = {}
    for field in FIELDS:
        text = texts[field]
        try:
            scaled[field] = repr(float(text) * _scale_for(field, units[field]))
        except ValueError:
            scaled[field] = text
    return scaled


def _circuit_labels(texts: dict[str, str], units: dict[str, str]) -> dict[str, str]:
    return {field: format_with_unit(texts[field], units[field]) for field in FIELDS}


def _render(texts, units, errors, result, independent, comparison):
    return render_template(
        "index.html",
        values=texts,
        units=units,
        unit_options=UNITS,
        labels=_FORM_LABELS,
        circuit=_circuit_labels(texts, units),
        errors=errors,
        result=result,
        independent=independent,
        comparison=comparison,
    )


@bp.get("/")
def index():
    return _render(dict(FORM_DEFAULTS), dict(FORM_UNITS), {}, None, None, None)


@bp.post("/calculate")
def calculate():
    texts, units = _read_form(request.form)
    values, errors = parse_inputs(_to_base_units(texts, units))

    result = None
    independent = None
    comparison = None

    if not errors:
        try:
            result = analyze_bias(**values)
            independent = solve_bias_independent(**values)
            comparison = compare_results(result, independent)
        except ValueError as exc:
            errors["_form"] = str(exc)

    return _render(texts, units, errors, result, independent, comparison)
