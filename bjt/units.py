from typing import Mapping

from .engineering import FIELDS, parse_inputs

VOLTAGE_UNITS = ("V", "mV")
RESISTANCE_UNITS = ("Ω", "kΩ", "MΩ")
BETA_UNITS = ("",)

UNIT_OPTIONS = {
    "vcc": VOLTAGE_UNITS,
    "r1": RESISTANCE_UNITS,
    "r2": RESISTANCE_UNITS,
    "rc": RESISTANCE_UNITS,
    "re": RESISTANCE_UNITS,
    "beta": BETA_UNITS,
    "vbe": VOLTAGE_UNITS,
}

DEFAULT_UNITS = {
    "vcc": "V",
    "r1": "kΩ",
    "r2": "kΩ",
    "rc": "kΩ",
    "re": "kΩ",
    "beta": "",
    "vbe": "V",
}

DEFAULT_VALUES = {
    "vcc": "12.0",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1.0",
    "beta": "100",
    "vbe": "0.70",
}

FIELD_META = (
    ("vcc", "V", "CC", "Supply Voltage"),
    ("r1", "R", "1", "Upper Divider"),
    ("r2", "R", "2", "Lower Divider"),
    ("rc", "R", "C", "Collector Resistor"),
    ("re", "R", "E", "Emitter Resistor"),
    ("beta", "β", "", "Current Gain"),
    ("vbe", "V", "BE", "Base-Emitter Voltage"),
)

_FACTORS = {
    "vcc": {"V": 1.0, "mV": 1e-3},
    "r1": {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6},
    "r2": {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6},
    "rc": {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6},
    "re": {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6},
    "beta": {"": 1.0},
    "vbe": {"V": 1.0, "mV": 1e-3},
}


def parse_form(raw: Mapping[str, str]) -> tuple[dict[str, float], dict[str, str]]:
    base: dict[str, str] = {}
    unit_errors: dict[str, str] = {}

    for field in FIELDS:
        text = str(raw.get(field, "")).strip()
        unit = str(raw.get(f"{field}_unit", DEFAULT_UNITS[field]))
        factors = _FACTORS[field]

        if unit not in factors:
            unit_errors[field] = "invalid unit"
            base[field] = text
            continue

        try:
            base[field] = repr(float(text) * factors[unit])
        except (TypeError, ValueError):
            base[field] = text

    values, errors = parse_inputs(base)
    errors.update(unit_errors)
    return values, errors
