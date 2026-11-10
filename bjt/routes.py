from flask import Blueprint, render_template, request

from .engineering import FIELDS, analyze_bias
from .independent import compare_results, solve_bias_independent
from .units import (
    DEFAULT_UNITS,
    DEFAULT_VALUES,
    FIELD_META,
    UNIT_OPTIONS,
    parse_form,
)

bp = Blueprint("bias", __name__)


def _form_payload(values, units):
    payload = dict(values)
    payload.update({f"{field}_unit": units[field] for field in FIELDS})
    return payload


def _calculate(values):
    result = analyze_bias(**values)
    independent = solve_bias_independent(**values)
    comparison = compare_results(result, independent)
    return result, independent, comparison


def _render(values, units, errors, result=None, independent=None, comparison=None):
    return render_template(
        "index.html",
        values=values,
        units=units,
        errors=errors,
        result=result,
        independent=independent,
        comparison=comparison,
        field_meta=FIELD_META,
        unit_options=UNIT_OPTIONS,
    )


@bp.get("/")
def index():
    values = dict(DEFAULT_VALUES)
    units = dict(DEFAULT_UNITS)
    parsed, errors = parse_form(_form_payload(values, units))

    result = None
    independent = None
    comparison = None

    if not errors:
        try:
            result, independent, comparison = _calculate(parsed)
        except ValueError as exc:
            errors["_form"] = str(exc)

    return _render(values, units, errors, result, independent, comparison)


@bp.post("/calculate")
def calculate():
    values = {field: request.form.get(field, "") for field in FIELDS}
    units = {
        field: request.form.get(f"{field}_unit", DEFAULT_UNITS[field])
        for field in FIELDS
    }
    parsed, errors = parse_form(_form_payload(values, units))

    result = None
    independent = None
    comparison = None

    if not errors:
        try:
            result, independent, comparison = _calculate(parsed)
        except ValueError as exc:
            errors["_form"] = str(exc)

    return _render(values, units, errors, result, independent, comparison)
