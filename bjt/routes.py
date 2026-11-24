from flask import Blueprint, render_template, request

from .engineering import (
    FIELDS,
    MODE_FIELDS,
    MODE_LABELS,
    MODES,
    analyze_bias,
    analyze_mode,
    parse_mode_inputs,
)
from .formatting import format_current, format_delta, format_voltage, format_with_unit
from .independent import compare_results, solve_independent
from .plots import gain_plot, phase_plot, waveform_plot
from .sim_params import (
    ANALYSIS_LABELS,
    ANALYSES,
    DEFAULTS as SIM_DEFAULTS,
    FIELDS as SIM_FIELDS,
    LABELS as SIM_LABELS,
    DEFAULT_UNITS as SIM_DEFAULT_UNITS,
    UNITS as SIM_UNITS,
    format_sim_value,
    load_model,
    parse_sim_inputs,
)
from .spice_engine import SpiceEngineError, find_ngspice, run_simulation

bp = Blueprint("bias", __name__)

# Unit choices offered in the form. Values are converted back to SI base units
# (V, Ω) before they reach the engineering core, so that module stays unit-free.
UNITS: dict[str, tuple[tuple[str, float], ...]] = {
    "vcc": (("V", 1.0), ("mV", 1e-3)),
    "r1": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "r2": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "rb": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "rc": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "re": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "beta": (("–", 1.0),),
    "vbe": (("V", 1.0), ("mV", 1e-3)),
}

DEFAULT_UNITS = {field: UNITS[field][0][0] for field in FIELDS}

# First render uses kΩ/MΩ where the lab handout does; posted forms without a
# unit selector fall back to the SI base unit.
MODE_UNITS = {
    "divider": {**DEFAULT_UNITS, "r1": "kΩ", "r2": "kΩ", "rc": "kΩ", "re": "kΩ"},
    "fixed": {**DEFAULT_UNITS, "rb": "MΩ", "rc": "kΩ"},
    "emitter": {**DEFAULT_UNITS, "rb": "MΩ", "re": "kΩ", "rc": "kΩ"},
}

# Values shown on the first page load for each mode.
MODE_DEFAULTS = {
    "divider": {
        "vcc": "12.0",
        "r1": "100",
        "r2": "22",
        "rc": "2.2",
        "re": "1.0",
        "beta": "100",
        "vbe": "0.70",
    },
    "fixed": {
        "vcc": "12.0",
        "rb": "1",
        "rc": "2.2",
        "beta": "100",
        "vbe": "0.70",
    },
    "emitter": {
        "vcc": "12.0",
        "rb": "1",
        "re": "1.0",
        "rc": "2.2",
        "beta": "100",
        "vbe": "0.70",
    },
}

_FORM_LABELS = {
    "vcc": ("V", "CC", "Supply Voltage"),
    "r1": ("R", "1", "Upper Divider"),
    "r2": ("R", "2", "Lower Divider"),
    "rb": ("R", "B", "Base Resistor"),
    "rc": ("R", "C", "Collector Resistor"),
    "re": ("R", "E", "Emitter Resistor"),
    "beta": ("β", "", "Current Gain"),
    "vbe": ("V", "BE", "Base–Emitter Voltage"),
}

MODE_OPTIONS = tuple((mode, MODE_LABELS[mode]) for mode in MODES)

SIM_ANALYSIS_OPTIONS = tuple((mode, ANALYSIS_LABELS[mode]) for mode in ANALYSES)
SIM_FIELD_LABELS = {field: SIM_LABELS[field] for field in SIM_FIELDS}
SIM_CIRCUIT_FIELDS = ("vcc", "r1", "r2", "rc", "re", "rl", "cin", "cout", "amp", "freq")
SIM_ANALYTICAL_FIELDS = ("beta", "vbe")


def _new_sim_form(analysis: str = "dc") -> dict:
    return {
        "analysis": analysis,
        "values": dict(SIM_DEFAULTS),
        "units": dict(SIM_DEFAULT_UNITS),
        "errors": {},
        "result": None,
        "engine_ready": find_ngspice() is not None,
    }


def _scale_for(field: str, unit: str) -> float | None:
    if field == "beta" and unit == "":
        return 1.0
    return dict(UNITS[field]).get(unit)


def _read_form(form) -> tuple[dict[str, str], dict[str, str]]:
    """Read the raw text and the selected unit for every field."""
    texts: dict[str, str] = {}
    units: dict[str, str] = {}
    for field in FIELDS:
        texts[field] = form.get(field, "").strip()
        units[field] = form.get(f"{field}_unit", DEFAULT_UNITS[field])
    return texts, units


def _to_base_units(
    texts: dict[str, str], units: dict[str, str], fields: tuple[str, ...]
) -> tuple[dict[str, str], dict[str, str]]:
    """Convert typed values into SI base units and flag unknown units."""
    scaled: dict[str, str] = {}
    errors: dict[str, str] = {}

    for field in fields:
        text = texts[field]
        factor = _scale_for(field, units[field])
        if factor is None:
            errors[field] = "invalid unit"
            scaled[field] = text
            continue
        try:
            scaled[field] = repr(float(text) * factor)
        except ValueError:
            scaled[field] = text

    return scaled, errors


def _circuit_labels(texts: dict[str, str], units: dict[str, str], fields: tuple[str, ...]) -> dict[str, str]:
    return {field: format_with_unit(texts[field], units[field]) for field in fields}


def _defaults_for(mode: str) -> tuple[dict[str, str], dict[str, str]]:
    texts = {field: MODE_DEFAULTS[mode].get(field, "") for field in MODE_FIELDS[mode]}
    units = {field: MODE_UNITS[mode][field] for field in MODE_FIELDS[mode]}
    return texts, units


def _render(
    mode,
    texts,
    units,
    errors,
    result,
    independent,
    comparison,
    sim_form=None,
):
    fields = MODE_FIELDS[mode]
    return render_template(
        "index.html",
        mode=mode,
        mode_label=MODE_LABELS[mode],
        mode_options=MODE_OPTIONS,
        fields=fields,
        values=texts,
        units=units,
        unit_options=UNITS,
        labels={field: _FORM_LABELS[field] for field in fields},
        circuit=_circuit_labels(texts, units, fields),
        errors=errors,
        result=result,
        independent=independent,
        comparison=comparison,
        sim_form=sim_form or _new_sim_form(),
        sim_analysis_options=SIM_ANALYSIS_OPTIONS,
        sim_labels=SIM_FIELD_LABELS,
        sim_unit_options=SIM_UNITS,
        sim_circuit_fields=SIM_CIRCUIT_FIELDS,
        sim_analytical_fields=SIM_ANALYTICAL_FIELDS,
    )


@bp.get("/")
def index():
    mode = request.args.get("mode", "divider")
    errors: dict[str, str] = {}

    if mode not in MODES:
        errors["mode"] = f"Unknown bias mode: {mode} (showing Voltage Divider Bias)"
        mode = "divider"

    texts, units = _defaults_for(mode)
    return _render(mode, texts, units, errors, None, None, None)


@bp.post("/calculate")
def calculate():
    mode = request.form.get("mode", "divider")
    errors: dict[str, str] = {}

    if mode not in MODES:
        errors["mode"] = f"Unknown bias mode: {mode} (showing Voltage Divider Bias)"
        texts, units = _defaults_for("divider")
        return _render("divider", texts, units, errors, None, None, None)

    fields = MODE_FIELDS[mode]
    texts, units = _read_form(request.form)
    texts = {field: texts[field] for field in fields}
    units = {field: units[field] for field in fields}

    scaled, errors = _to_base_units(texts, units, fields)
    values, parse_errors = parse_mode_inputs(mode, scaled)
    errors.update(parse_errors)

    result = None
    independent = None
    comparison = None

    if not errors:
        try:
            result = analyze_mode(mode, values)
            independent = solve_independent(mode, values)
            comparison = compare_results(result, independent)
        except ValueError as exc:
            errors["_form"] = str(exc)

    return _render(mode, texts, units, errors, result, independent, comparison)


@bp.post("/simulate")
def simulate():
    """Run the one CE voltage-divider reference circuit through ngspice."""
    analysis = request.form.get("analysis", "dc")
    errors: dict[str, str] = {}

    if analysis not in ANALYSES:
        errors["analysis"] = f"unknown analysis mode: {analysis}"
        analysis = "dc"

    texts = {field: request.form.get(field, "").strip() for field in SIM_FIELDS}
    units = {
        field: request.form.get(f"{field}_unit", SIM_DEFAULT_UNITS[field])
        for field in SIM_FIELDS
    }
    values, field_errors = parse_sim_inputs(analysis, texts, units)
    errors.update(field_errors)

    sim = None
    if not errors:
        model_text, model_name, model_source = load_model()
        try:
            raw = run_simulation(values, analysis, model_text, model_name)
            sim = {
                "analysis": analysis,
                "analysis_label": ANALYSIS_LABELS[analysis],
                "engine": raw["engine"],
                "version": raw["version"],
                "model": raw["model"],
                "model_source": model_source,
                "netlist": raw["netlist"],
                "log_excerpt": raw["log_excerpt"],
                "run_dir": raw.get("run_dir", "temporary (cleaned after run)"),
                "circuit": {
                    field: format_sim_value(texts[field], units[field])
                    for field in SIM_CIRCUIT_FIELDS
                },
            }

            if analysis == "dc":
                summary = raw["summary"]
                analytical = analyze_bias(
                    values["vcc"],
                    values["r1"],
                    values["r2"],
                    values["rc"],
                    values["re"],
                    values["beta"],
                    values["vbe"],
                )
                comparison_rows = []
                for key, label, formatter in (
                    ("vb", "VB", format_voltage),
                    ("ve", "VE", format_voltage),
                    ("vc", "VC", format_voltage),
                    ("vce", "VCE", format_voltage),
                    ("ic", "IC", format_current),
                ):
                    comparison_rows.append(
                        {
                            "label": label,
                            "spice": formatter(summary[key]),
                            "analytical": formatter(analytical[key]),
                            "delta": format_delta(summary[key] - analytical[key]),
                        }
                    )
                sim["dc_points"] = raw["points"]
                sim["comparison_rows"] = comparison_rows
                sim["assumption_note"] = (
                    "SPICE uses the BJT .model above; the analytical column uses "
                    f"constant β={values['beta']:g}, VBE={values['vbe']:g} V. "
                    "Different models need not agree digit-for-digit. "
                    "IC shown here is derived from the simulated VC and RC, not printed as a device current."
                )

            elif analysis == "ac":
                sim["gain_plot"] = gain_plot(raw["gain_points"])
                sim["phase_plot"] = phase_plot(raw["phase_points"])
                sim["ac_summary"] = raw["summary"]

            else:
                sim["wave_plot"] = waveform_plot(
                    raw["vin_series"], raw["vout_series"]
                )
                sim["tran_summary"] = raw["summary"]

        except (SpiceEngineError, ValueError, OSError) as exc:
            errors["_sim"] = str(exc)

    sim_form = {
        "analysis": analysis,
        "values": texts,
        "units": units,
        "errors": errors,
        "result": sim,
        "engine_ready": find_ngspice() is not None,
    }
    bias_texts, bias_units = _defaults_for("divider")
    return _render(
        "divider",
        bias_texts,
        bias_units,
        {},
        None,
        None,
        None,
        sim_form=sim_form,
    )
