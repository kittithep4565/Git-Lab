"""Small dependency-free SVG line plots for real ngspice result arrays."""

from __future__ import annotations

import html
import math
from typing import Iterable


def _fmt(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) >= 1000 or abs(value) < 0.01:
        return f"{value:.2e}"
    return f"{value:.3g}"


def line_svg(
    series: list[dict],
    x_label: str,
    y_label: str,
    *,
    width: int = 660,
    height: int = 280,
    x_log: bool = False,
) -> str:
    """Return an SVG string built only from the supplied numeric points.

    ``series`` items are ``{"name", "points": [(x, y), ...], "color"}``.
    """
    left, right, top, bottom = 68, 18, 42, 54
    plot_w = width - left - right
    plot_h = height - top - bottom

    all_points: list[tuple[float, float]] = []
    for item in series:
        all_points.extend(item["points"])
    if not all_points:
        return '<svg viewBox="0 0 10 10" role="img" aria-label="no data"></svg>'

    raw_x = [p[0] for p in all_points]
    raw_y = [p[1] for p in all_points]
    if x_log:
        if any(x <= 0 for x in raw_x):
            raise ValueError("log x axis requires positive values")
        xs = [math.log10(x) for x in raw_x]
    else:
        xs = raw_x

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(raw_y), max(raw_y)
    if xmax == xmin:
        xmax = xmin + 1.0
    if ymax == ymin:
        ymin -= 1.0
        ymax += 1.0
    else:
        pad = (ymax - ymin) * 0.08
        ymin -= pad
        ymax += pad

    def sx(x: float) -> float:
        value = math.log10(x) if x_log else x
        return left + (value - xmin) / (xmax - xmin) * plot_w

    def sy(y: float) -> float:
        return top + (ymax - y) / (ymax - ymin) * plot_h

    parts = [
        f'<svg class="sim-plot" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{html.escape(x_label)} versus {html.escape(y_label)}">',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" '
        'fill="#fbfdff" stroke="#d5e5ef"/>',
    ]

    for i in range(1, 5):
        y = top + plot_h * i / 5
        value = ymax - (ymax - ymin) * i / 5
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
            'stroke="#e7eff5" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#557084">{html.escape(_fmt(value))}</text>'
        )

    tick_count = 5
    for i in range(tick_count + 1):
        xv = xmin + (xmax - xmin) * i / tick_count
        x = left + plot_w * i / tick_count
        if x_log:
            real_x = 10 ** xv
            label = _fmt(real_x)
        else:
            label = _fmt(xv)
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" '
            'stroke="#e7eff5" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 18}" text-anchor="middle" '
            f'font-size="11" fill="#557084">{html.escape(label)}</text>'
        )

    parts.append(
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" '
        'y2="{top + plot_h}" stroke="#7e9aab" stroke-width="1.3"/>'
    )
    parts.append(
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" '
        'stroke="#7e9aab" stroke-width="1.3"/>'
    )

    for item in series:
        coords = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in item["points"])
        parts.append(
            f'<polyline points="{coords}" fill="none" stroke="{item["color"]}" '
            'stroke-width="2" stroke-linejoin="round"/>'
        )

    legend_x = left
    for item in series:
        parts.append(
            f'<line x1="{legend_x}" y1="22" x2="{legend_x + 18}" y2="22" '
            f'stroke="{item["color"]}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<text x="{legend_x + 23}" y="26" font-size="11" fill="#33556a">'
            f'{html.escape(str(item["name"]))}</text>'
        )
        legend_x += 28 + 7 * len(str(item["name"]))

    parts.append(
        f'<text x="{left + plot_w / 2}" y="{height - 8}" text-anchor="middle" '
        f'font-size="12" fill="#33556a">{html.escape(x_label)}</text>'
    )
    parts.append(
        f'<text transform="translate(16 {top + plot_h / 2}) rotate(-90)" '
        f'text-anchor="middle" font-size="12" fill="#33556a">{html.escape(y_label)}</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def gain_plot(points: Iterable[tuple[float, float]]) -> str:
    return line_svg(
        [{"name": "|Vout/Vin|", "points": list(points), "color": "#0e7c86"}],
        "Frequency (Hz, log scale)",
        "Gain (dB)",
        x_log=True,
    )


def phase_plot(points: Iterable[tuple[float, float]]) -> str:
    return line_svg(
        [{"name": "phase", "points": list(points), "color": "#a65a2c"}],
        "Frequency (Hz, log scale)",
        "Phase (°)",
        x_log=True,
    )


def waveform_plot(
    vin_points: Iterable[tuple[float, float]],
    vout_points: Iterable[tuple[float, float]],
) -> str:
    return line_svg(
        [
            {"name": "Vin", "points": list(vin_points), "color": "#0e7c86"},
            {"name": "Vout", "points": list(vout_points), "color": "#c2702f"},
        ],
        "Time (ms)",
        "Voltage (V)",
    )
