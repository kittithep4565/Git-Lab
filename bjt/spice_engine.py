"""ngspice adapter: build a netlist, run a batch process, parse real output.

The Flask route never talks to ngspice directly.  All solver interaction is
kept in this module so that errors, timeouts and provenance can be reported.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping

TIMEOUT_SECONDS = 25
AC_POINTS_PER_DECADE = 50
_AC_FSTART_HZ = 1.0
_AC_FSTOP_HZ = 1e8

_NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_ROW_RE = re.compile(r"^\s*\d+\s+(" + _NUMBER + r"(?:\s+" + _NUMBER + r")+)\s*$")
_NODES = ("base", "emitter", "collector", "in", "out")


class SpiceEngineError(RuntimeError):
    """Raised when ngspice is missing, fails, or returns unusable output."""


def find_ngspice() -> str | None:
    configured = os.environ.get("NGSPICE_EXE")
    candidates = [configured] if configured else []
    candidates.append(shutil.which("ngspice"))
    candidates.append(str(Path.home() / "ngspice-47" / "Spice64" / "bin" / "ngspice.exe"))
    candidates.append("C:/Program Files/ngspice/bin/ngspice.exe")

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def _num(value: float) -> str:
    return f"{value:.10g}"


def build_netlist(
    values: Mapping[str, float],
    analysis: str,
    model_text: str,
    model_name: str,
) -> str:
    """Create one verified netlist.  All numbers are already SI floats."""
    lines = [
        "* ENG29 2121 Lab 04 - CE voltage-divider reference",
        "* Vin = source node before Cin; Vout = node across RL.",
        "* beta/vbe inputs are analytical reference only; SPICE uses the .model below.",
        f"VCC vcc 0 DC {_num(values['vcc'])}",
        f"VIN in 0 DC 0 AC 1 SIN(0 {_num(values['amp'])} {_num(values['freq'])})",
        f"R1 vcc base {_num(values['r1'])}",
        f"R2 base 0 {_num(values['r2'])}",
        f"RC vcc collector {_num(values['rc'])}",
        f"RE emitter 0 {_num(values['re'])}",
        f"Q1 collector base emitter {model_name}",
        f"CIN in base {_num(values['cin'])}",
        f"COUT collector out {_num(values['cout'])}",
        f"RL out 0 {_num(values['rl'])}",
        model_text.strip(),
    ]

    if analysis == "dc":
        lines += [
            ".op",
            ".print op " + " ".join(f"v({node})" for node in _NODES),
        ]
    elif analysis == "ac":
        lines += [
            f".ac dec {AC_POINTS_PER_DECADE} {_num(_AC_FSTART_HZ)} {_num(_AC_FSTOP_HZ)}",
            ".print ac vdb(in) vp(in) vdb(out) vp(out)",
        ]
    elif analysis == "tran":
        period = 1.0 / values["freq"]
        tstep = period / 100.0
        tstop = period * 5.0
        lines += [
            f".tran {_num(tstep)} {_num(tstop)}",
            ".print tran v(in) v(out)",
        ]
    else:
        raise SpiceEngineError(f"unknown analysis: {analysis}")

    lines.append(".end")
    return "\n".join(lines) + "\n"


def _row_numbers(line: str) -> list[float] | None:
    match = _ROW_RE.match(line)
    if not match:
        return None
    try:
        return [float(token) for token in match.group(1).split()]
    except ValueError:
        return None


def _version(log: str, executable: str = "") -> str:
    match = re.search(r"ngspice[-\s]?(\d+\.\d+|\d+)", log, re.IGNORECASE)
    if match:
        return match.group(1)
    path_match = re.search(r"ngspice-(\d+(?:\.\d+)?)", executable, re.IGNORECASE)
    return path_match.group(1) if path_match else "unknown (see run log)"


def _parse_print_tables(log: str) -> dict[str, float]:
    """Read the `Index ...` tables that ngspice writes for .print."""
    lines = log.splitlines()
    data: dict[str, float] = {}
    i = 0
    while i < len(lines):
        if re.match(r"^\s*Index\s", lines[i], re.IGNORECASE):
            headers = re.findall(r"v\(\s*([A-Za-z0-9_]+)\s*\)", lines[i], re.IGNORECASE)
            j = i + 1
            while j < len(lines) and j < i + 8:
                numbers = _row_numbers(lines[j])
                if numbers and headers and len(numbers) >= len(headers):
                    for name, value in zip(headers, numbers):
                        data[name.lower()] = value
                    break
                if "Index" in lines[j]:
                    break
                j += 1
            i = j + 1
        else:
            i += 1
    return data


def _log_tail(log: str, limit: int = 4000) -> str:
    return log[-limit:] if len(log) > limit else log


def _parse_op(log: str, values: Mapping[str, float]) -> dict:
    node_values = _parse_print_tables(log)

    needed = ("base", "emitter", "collector")
    missing = [name for name in needed if name not in node_values]
    if missing:
        raise SpiceEngineError(f".op output missing node(s): {', '.join(missing)}")

    vb = node_values["base"]
    ve = node_values["emitter"]
    vc = node_values["collector"]
    ic = (values["vcc"] - vc) / values["rc"]

    return {
        "points": [
            ("VB", vb),
            ("VE", ve),
            ("VC", vc),
            ("VCE", vc - ve),
            ("IC", ic),
        ],
        "summary": {
            "vb": vb,
            "ve": ve,
            "vc": vc,
            "vce": vc - ve,
            "ic": ic,
            "vin_dc": node_values.get("in"),
            "vout_dc": node_values.get("out"),
        },
    }


def _wrap_phase(phase: float) -> float:
    while phase > 180.0:
        phase -= 360.0
    while phase < -180.0:
        phase += 360.0
    return phase


def _iter_print_tables(log: str):
    """Yield ``(headers, rows)`` for each ``Index ...`` table in a run log.

    The leading ``Index`` column is removed from both the header list and the
    numeric rows, so positions line up.  ngspice repeats the header every 60
    rows; each repeated block is yielded separately and merged by the caller.
    """
    headers: list[str] = []
    rows: list[list[float]] = []

    for line in log.splitlines():
        if re.match(r"^\s*Index\b", line, re.IGNORECASE):
            if headers and rows:
                yield headers, rows
            headers = [token for token in line.split() if token.lower() != "index"]
            rows = []
            continue
        if not headers or re.fullmatch(r"[\s\-]+", line):
            continue
        numbers = _row_numbers(line)
        if numbers and len(numbers) >= len(headers):
            rows.append(numbers)

    if headers and rows:
        yield headers, rows


def _parse_ac(log: str) -> dict:
    # ngspice writes Vin and Vout as separate Index tables.  Merge them by the
    # printed frequency so the gain/phase always pair the same sweep points.
    series: dict[str, list[tuple[float, float, float]]] = {}

    for headers, rows in _iter_print_tables(log):
        lowered = [name.lower() for name in headers]
        try:
            freq_index = next(
                i for i, name in enumerate(lowered) if name in ("frequency", "freq")
            )
            db_index = next(i for i, name in enumerate(lowered) if name.startswith("vdb("))
            phase_index = next(i for i, name in enumerate(lowered) if name.startswith("vp("))
        except StopIteration:
            continue

        db_match = re.search(r"vdb\(\s*([^)]+)\s*\)", headers[db_index], re.IGNORECASE)
        phase_match = re.search(r"vp\(\s*([^)]+)\s*\)", headers[phase_index], re.IGNORECASE)
        if not db_match or not phase_match:
            continue
        node = db_match.group(1).strip().lower()

        for row in rows:
            if max(freq_index, db_index, phase_index) >= len(row):
                continue
            freq = row[freq_index]
            db_value = row[db_index]
            phase_value = row[phase_index]
            if freq <= 0 or not all(map(math.isfinite, (freq, db_value, phase_value))):
                continue
            series.setdefault(node, []).append((freq, db_value, phase_value))

    if "in" not in series or "out" not in series:
        raise SpiceEngineError(".ac output is missing the Vin or Vout sweep table")

    vin_by_freq = {freq: (db, phase) for freq, db, phase in series["in"]}
    vout_by_freq = {freq: (db, phase) for freq, db, phase in series["out"]}
    common_freqs = sorted(set(vin_by_freq) & set(vout_by_freq))
    if len(common_freqs) < 5:
        raise SpiceEngineError(".ac output has too few matching data rows")

    gain_points: list[tuple[float, float]] = []
    phase_points: list[tuple[float, float]] = []
    for freq in common_freqs:
        vin_db, vin_phase = vin_by_freq[freq]
        vout_db, vout_phase = vout_by_freq[freq]
        gain_points.append((freq, vout_db - vin_db))
        phase_points.append((freq, _wrap_phase(vout_phase - vin_phase)))

    peak = max(gain for _, gain in gain_points)
    target = peak - 3.0
    in_band = [freq for freq, gain in gain_points if gain >= target]
    f_low = in_band[0] if in_band else None
    f_high = in_band[-1] if in_band else None
    bracketed = (
        f_low is not None
        and f_high is not None
        and f_low > common_freqs[0]
        and f_high < common_freqs[-1]
    )

    return {
        "gain_points": gain_points,
        "phase_points": phase_points,
        "summary": {
            "peak_gain_db": peak,
            "peak_gain_linear": 10 ** (peak / 20.0),
            "f_low_hz": f_low,
            "f_high_hz": f_high,
            "cutoff_note": (
                f"-3 dB band {f_low:.3g} – {f_high:.3g} Hz"
                if bracketed
                else "not determined in sweep range (-3 dB point not bracketed)"
            ),
            "vin_reference": "source node 'in' before Cin",
        },
    }


def _parse_tran(log: str) -> dict:
    points: list[tuple[float, float, float]] = []
    for line in log.splitlines():
        numbers = _row_numbers(line)
        if not numbers or len(numbers) < 3:
            continue
        # Batch output is "index time vin vout" (4 values) or "time vin vout".
        time_s, vin, vout = numbers[-3:]
        if not all(map(math.isfinite, (time_s, vin, vout))):
            continue
        points.append((time_s * 1e3, vin, vout))

    if len(points) < 10:
        raise SpiceEngineError(".tran output has too few data rows")

    vin_values = [p[1] for p in points]
    vout_values = [p[2] for p in points]
    mean_in = sum(vin_values) / len(vin_values)
    mean_out = sum(vout_values) / len(vout_values)
    covariance = sum(
        (v - mean_in) * (o - mean_out) for v, o in zip(vin_values, vout_values)
    )

    return {
        "wave_points": [(t, v, o) for t, v, o in points],
        "vin_series": [(t, v) for t, v, _ in points],
        "vout_series": [(t, o) for t, _, o in points],
        "summary": {
            "vin_pp": max(vin_values) - min(vin_values),
            "vout_pp": max(vout_values) - min(vout_values),
            "relation": (
                "inverted (negative correlation)"
                if covariance < 0
                else "non-inverted (positive or zero correlation)"
            ),
            "samples": len(points),
        },
    }


def run_simulation(
    values: Mapping[str, float],
    analysis: str,
    model_text: str,
    model_name: str,
) -> dict:
    """Run one analysis in an isolated directory and return parsed data."""
    executable = find_ngspice()
    if not executable:
        raise SpiceEngineError(
            "ngspice not found. Install ngspice 47 or set NGSPICE_EXE to its full path."
        )

    netlist = build_netlist(values, analysis, model_text, model_name)
    run_dir = Path(tempfile.mkdtemp(prefix="lab04_"))

    try:
        (run_dir / "circuit.cir").write_text(netlist, encoding="utf-8")
        # Do not pass -r here: with a raw file ngspice ignores .print and the
        # log has no readable table.  The .print output in run.log is our
        # parsed, auditable result file.
        command = [
            executable,
            "-b",
            "-o",
            "run.log",
            "circuit.cir",
        ]
        completed = subprocess.run(
            command,
            cwd=run_dir,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            shell=False,
        )

        log_path = run_dir / "run.log"
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""

        # This ngspice Windows build returns 1 after a successful batch run, so
        # success is decided by usable output, not by the exit code alone.
        if not log.strip():
            raise SpiceEngineError(
                f"ngspice produced no output (exit {completed.returncode}): "
                f"{completed.stderr.strip()[:300]}"
            )
        if re.search(r"(?im)^\s*error\s*:", log):
            raise SpiceEngineError("ngspice reported an error:\n" + _log_tail(log, 1200))
        if "No. of Data Rows" not in log and "Index" not in log:
            raise SpiceEngineError("ngspice output has no data table:\n" + _log_tail(log, 1200))

        if analysis == "dc":
            parsed = _parse_op(log, values)
        elif analysis == "ac":
            parsed = _parse_ac(log)
        elif analysis == "tran":
            parsed = _parse_tran(log)
        else:
            raise SpiceEngineError(f"unknown analysis: {analysis}")

        parsed.update(
            {
                "status": "success",
                "engine": "ngspice",
                "version": _version(log, executable),
                "model": model_name,
                "netlist": netlist,
                "log_excerpt": _log_tail(log),
                "run_dir": str(run_dir),
            }
        )
        return parsed
    except subprocess.TimeoutExpired as exc:
        raise SpiceEngineError(
            f"ngspice timed out after {TIMEOUT_SECONDS} s; check the frequency and source settings."
        ) from exc
    finally:
        if os.environ.get("LAB04_KEEP_RUNS") != "1":
            shutil.rmtree(run_dir, ignore_errors=True)
