def format_current(value_a: float) -> str:
    if abs(value_a) >= 1:
        return f"{value_a:.3f} A"
    if abs(value_a) >= 1e-3:
        return f"{value_a * 1e3:.3f} mA"
    return f"{value_a * 1e6:.2f} µA"


def format_voltage(value_v: float) -> str:
    return f"{value_v:.3f} V"


def format_delta(value: float) -> str:
    return f"{value:.2e}"
