"""Validation and defaults for the Lab 4 CE reference circuit.

Only trusted local model files are read here.  Values coming from the browser
are parsed into SI numbers before they ever reach the netlist builder.
"""

from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Mapping

ANALYSES = ("dc", "ac", "tran")
ANALYSIS_LABELS = {
    "dc": "DC · .op",
    "ac": "AC · .ac",
    "tran": "Transient · .tran",
}

FIELDS = (
    "vcc",
    "r1",
    "r2",
    "rc",
    "re",
    "rl",
    "cin",
    "cout",
    "amp",
    "freq",
    "beta",
    "vbe",
)

UNITS: dict[str, tuple[tuple[str, float], ...]] = {
    "vcc": (("V", 1.0), ("mV", 1e-3)),
    "r1": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "r2": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "rc": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "re": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "rl": (("Ω", 1.0), ("kΩ", 1e3), ("MΩ", 1e6)),
    "cin": (("F", 1.0), ("mF", 1e-3), ("µF", 1e-6), ("nF", 1e-9), ("pF", 1e-12)),
    "cout": (("F", 1.0), ("mF", 1e-3), ("µF", 1e-6), ("nF", 1e-9), ("pF", 1e-12)),
    "amp": (("V", 1.0), ("mV", 1e-3), ("µV", 1e-6)),
    "freq": (("Hz", 1.0), ("kHz", 1e3), ("MHz", 1e6)),
    "beta": (("", 1.0),),
    "vbe": (("V", 1.0), ("mV", 1e-3)),
}

DEFAULT_UNITS: dict[str, str] = {
    "vcc": "V",
    "r1": "kΩ",
    "r2": "kΩ",
    "rc": "kΩ",
    "re": "kΩ",
    "rl": "kΩ",
    "cin": "µF",
    "cout": "µF",
    "amp": "mV",
    "freq": "kHz",
    "beta": "",
    "vbe": "V",
}

DEFAULTS: dict[str, str] = {
    "vcc": "12.0",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1.0",
    "rl": "10",
    "cin": "10",
    "cout": "10",
    "amp": "10",
    "freq": "1",
    "beta": "100",
    "vbe": "0.70",
}

LABELS: dict[str, tuple[str, str]] = {
    "vcc": ("V", "CC"),
    "r1": ("R", "1"),
    "r2": ("R", "2"),
    "rc": ("R", "C"),
    "re": ("R", "E"),
    "rl": ("R", "L"),
    "cin": ("C", "in"),
    "cout": ("C", "out"),
    "amp": ("V", "amp"),
    "freq": ("f", "src"),
    "beta": ("β", "ref"),
    "vbe": ("V", "BE ref"),
}

# β and VBE are used only by the analytical reference, never by SPICE.
ANALYTICAL_ONLY = frozenset({"beta", "vbe"})

CIRCUIT_FIELDS = ("vcc", "r1", "r2", "rc", "re", "rl", "cin", "cout")
REQUIRED_BY_ANALYSIS = {
    "dc": CIRCUIT_FIELDS + ("beta", "vbe"),
    "ac": CIRCUIT_FIELDS,
    "tran": CIRCUIT_FIELDS + ("amp", "freq"),
}

BUILTIN_MODEL = ".model QNPN NPN(IS=1e-14 BF=100 VAF=100 RB=10 RC=1)"
_MODEL_NAME_RE = re.compile(r"^\s*\.model\s+(\S+)", re.IGNORECASE | re.MULTILINE)


def parse_sim_inputs(
    analysis: str,
    texts: Mapping[str, str],
    units: Mapping[str, str],
) -> tuple[dict[str, float], dict[str, str]]:
    """Return SI values plus field errors.  No text reaches the netlist raw."""
    errors: dict[str, str] = {}
    if analysis not in ANALYSES:
        errors["analysis"] = f"unknown analysis mode: {analysis}"

    values: dict[str, float] = {}
    required = REQUIRED_BY_ANALYSIS.get(analysis, ())
    for field in FIELDS:
        if field not in required:
            # Unused inputs fall back to the documented fixture instead of
            # blocking the run (e.g. AC does not use the transient SIN source).
            factor = dict(UNITS[field])[DEFAULT_UNITS[field]]
            values[field] = float(DEFAULTS[field]) * factor
            continue
        raw = "" if texts.get(field) is None else str(texts.get(field)).strip()
        if not raw:
            errors[field] = "required"
            continue
        unit = units.get(field, DEFAULT_UNITS[field])
        factor = dict(UNITS[field]).get(unit)
        if factor is None:
            errors[field] = "invalid unit"
            continue
        try:
            number = float(raw) * factor
        except (TypeError, ValueError):
            errors[field] = "must be a number"
            continue
        if not math.isfinite(number):
            errors[field] = "must be finite"
            continue
        if number <= 0:
            errors[field] = "must be greater than zero"
            continue
        values[field] = number

    if "vbe" in values and "vbe" not in errors and "vcc" in values:
        if values["vbe"] >= values["vcc"]:
            errors["vbe"] = "must be less than VCC"

    if "freq" in values and "freq" not in errors:
        if not 10.0 <= values["freq"] <= 1e6:
            errors["freq"] = "use 10 Hz – 1 MHz"

    if "amp" in values and "amp" not in errors:
        if values["amp"] > 1.0:
            errors["amp"] = "use 1 V peak or less"

    return values, errors


def format_sim_value(text: str, unit: str) -> str:
    text = str(text).strip()
    if not text:
        return "—"
    return text if not unit else f"{text} {unit}"


def load_model() -> tuple[str, str, str]:
    """Return (model text, model name, source label).

    An instructor starter model can be dropped in ``bjt/spice_model.lib`` or
    pointed to by ``LAB04_MODEL_FILE``.  The fallback is explicitly a generic
    teaching model, not a claim about any specific transistor part.
    """
    override = os.environ.get("LAB04_MODEL_FILE")
    path = Path(override) if override else Path(__file__).with_name("spice_model.lib")

    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            match = _MODEL_NAME_RE.search(text)
            name = match.group(1) if match else "QNPN"
            return text, name, f"starter file: {path.name}"

    return BUILTIN_MODEL, "QNPN", "generic teaching model (no starter file found)"
