from flask import Blueprint, render_template, request

from .engineering import DEFAULTS, FIELDS, analyze_bias, parse_inputs
from .independent import compare_results, solve_bias_independent

bp = Blueprint("bias", __name__)


@bp.get("/")
def index():
    return render_template(
        "index.html",
        values=DEFAULTS,
        errors={},
        result=None,
        independent=None,
        comparison=None,
    )


@bp.post("/calculate")
def calculate():
    raw = {field: request.form.get(field, "") for field in FIELDS}
    values, errors = parse_inputs(raw)

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

    return render_template(
        "index.html",
        values=raw,
        errors=errors,
        result=result,
        independent=independent,
        comparison=comparison,
    )
