import argparse
import math


def analyze_dc(voltage_v: float, resistance_ohm: float) -> dict[str, float]:
    """Calculate current and power for a single DC resistor."""
    for name, value in (("voltage_v", voltage_v), ("resistance_ohm", resistance_ohm)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")

    if resistance_ohm <= 0:
        raise ValueError("resistance_ohm must be greater than zero")

    current_a = voltage_v / resistance_ohm
    power_w = voltage_v * current_a
    return {"current_a": current_a, "power_w": power_w}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate current and power for a DC resistor.")
    parser.add_argument("voltage_v", nargs="?", type=float, default=12, help="voltage in volts (default: 12)")
    parser.add_argument("resistance_ohm", nargs="?", type=float, default=6, help="resistance in ohms (default: 6)")
    args = parser.parse_args()

    try:
        result = analyze_dc(args.voltage_v, args.resistance_ohm)
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print(f"Current: {result['current_a']} A")
    print(f"Power: {result['power_w']} W")