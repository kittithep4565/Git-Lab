def _trim(text: str) -> str:
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def format_current(value_a: float) -> str:
    """Auto-scale amperes to A / mA / µA for display."""
    if abs(value_a) >= 1:
        return f"{value_a:.2f} A"
    if abs(value_a) >= 1e-3:
        return f"{value_a * 1e3:.2f} mA"
    return f"{_trim(f'{value_a * 1e6:.2f}')} µA"


def format_voltage(value_v: float) -> str:
    return f"{value_v:.3f} V"


def format_voltage_short(value_v: float) -> str:
    return f"{value_v:.2f} V"


def format_delta(value: float) -> str:
    return f"{value:.2e}"


def format_with_unit(text: str, unit: str) -> str:
    """Join a raw form value with its unit for display (e.g. ``100 kΩ``)."""
    text = str(text).strip()
    if unit in ("", "–"):
        return text
    return f"{text} {unit}".strip()
