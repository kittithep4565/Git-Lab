# BJT DC Bias Web App — Screenshot-Matched UI Design

Date: 2026-11-10
Status: Awaiting approval
Approach: A (server-rendered Flask + Jinja + CSS Grid + inline SVG)

## Intent

Make the existing DC-bias calculator look and behave like the supplied
reference screenshot: one wide lab dashboard with a header, a three-column
body (inputs, circuit, results), and a "Week 2 Goal" footer. The calculator
itself stays the same; this change is presentation plus a usable engineering
unit layer.

The screenshot's example output (`VB = 2.20 V`, `IC = 1.50 mA`, etc.) does
not follow from its displayed inputs and is treated as illustrative. The app
will show its own calculated values, not hard-coded screenshot values.

## Goals

- Match the screenshot's layout, hierarchy, labels, icons, and colour feel.
- Support working unit selectors: `V`/`mV` for voltages, `Ω`/`kΩ`/`MΩ` for
  resistances, no unit for beta.
- Show the entered values and units on the circuit diagram.
- Load the page with the screenshot's example parameters already calculated.
- Preserve validation, region classification, warnings, and the independent
  cross-check.
- Keep the app dependency-free beyond Flask.

## Non-goals

- No AC analysis, transient analysis, or circuit editor.
- No FET support.
- No live/AJAX recalculation; Calculate submits and re-renders.
- No authentication, database, or persistence.
- No pixel-perfect clone of the screenshot's fonts or illustrations; close
  visual match using local assets and system fonts.

## Anti-goals

- A pretty page that hides invalid input or silently converts units wrong.
- A static circuit picture whose labels do not match the form.
- Removing the independent cross-check just to match the screenshot.

## Approaches Considered

### A. Flask + Jinja + CSS Grid + inline SVG + native selects (chosen)

Server-rendered form, native unit selects, inline SVG schematic with dynamic
labels, existing Python calculation layer. No build step. Directly testable
with Flask's test client.

Trade-off: Calculate reloads the page. Acceptable for a lab calculator.

### B. Same visual design with non-functional unit labels

Fastest, but `100` next to `kΩ` would actually mean `100 Ω`, which is
misleading. Rejected.

### C. JavaScript framework for live updates

Adds an unnecessary dependency and build pipeline for one form. Rejected.

## Visual Design

- Page: light blue-grey background, centred white dashboard with a soft
  blue border and large rounded corners.
- Header: circuit-chip icon; title `Lab 02: BJT DC Bias Web App`; subtitle
  `ENG29 2121 – Common Emitter (Voltage Divider Bias)`; right-side course
  badge `Computer Programming for Electrical Engineers`.
- Main grid: three equal-ish columns at desktop width.
  1. **Input Parameters** — sliders icon, seven labelled rows, unit select
     at the right of each numeric field, full-width Calculate button with
     calculator icon.
  2. **Circuit: Common-Emitter Amplifier** — inline SVG showing VCC, R1, R2,
     RC, RE, Q1, grounds, and dynamic value labels.
  3. **DC Bias Results** — bar-chart icon, seven-row table in the order
     `VB, VE, VC, VCE, IB, IC, IE`, then a region-status box.
- Footer: target icon, `Week 2 Goal`, and the lab's rough target text.
- Responsive: three columns above roughly 800 px; single column below.
- Typography: bold rounded-feeling headings using a local system font stack;
  italic/subscript engineering symbols (`V_CC`, `R_C`, `V_CE`, `I_B`, etc.).
- Icons: inline SVG symbols, no icon font or external CDN.

## Unit Behaviour

| Field | Units | Default |
|---|---|---|
| VCC | V, mV | V |
| R1, R2, RC, RE | Ω, kΩ, MΩ | kΩ |
| Beta | — | — |
| VBE | V, mV | V |

- The value the user types is preserved for re-display after validation.
- Inputs are converted to base SI units (V, Ω) before calling the existing
  `analyze_bias` and `solve_bias_independent` functions.
- The circuit diagram uses the displayed value and unit, e.g. `R1 100 kΩ`.
- Invalid units are rejected; the HTML form only offers valid options, but
  server-side tests cover tampering.

## Defaults (match the screenshot's input panel)

```text
VCC = 12.0 V
R1  = 100  kΩ
R2  = 22   kΩ
RC  = 2.2  kΩ
RE  = 1.0  kΩ
Beta = 100
VBE = 0.70 V
```

On `GET /`, these defaults are calculated and rendered, so the initial page
looks complete like the screenshot. Calculated values will be the app's
engine results, not the screenshot's illustrative numbers.

## Results and Region Status

- Results table uses existing `format_voltage` / `format_current` filters.
- Active: green box, check icon, `Active region approximation OK`, and a
  line such as `VCE = 8.052 V > 0.2 V (transistor in active region)`.
- Saturation: red box with the existing saturation warning and comparison
  `VCE < 0.2 V`.
- Cutoff: neutral/amber box with the existing cutoff warning and `IB = 0`.
- The independent cross-check still runs on every calculation. In the normal
  matching case it adds nothing visible. If it fails, a red message appears
  below the region box rather than silently showing untrusted results.
- Invalid input hides calculated results and shows a placeholder in the
  results panel, while preserving all raw values and units.

## Engineering Boundary

No changes to the closed-form equations, region rules, or independent solver.
New unit conversion is a thin presentation-layer module that converts form
values into the existing base units before calculation.

## Files Expected to Change

- `bjt/units.py` — new: unit metadata, defaults, conversion, form parsing.
- `bjt/routes.py` — use display defaults, convert units, calculate on GET.
- `bjt/templates/index.html` — full dashboard layout and inline SVG.
- `bjt/static/style.css` — new visual system and responsive grid.
- `tests/test_units.py` — new: conversion and unit validation.
- `tests/test_routes.py` — updated for the new UI, units, and defaults.
- `README.md` — short note about units and the new UI.

`bjt/engineering.py`, `bjt/independent.py`, and `bjt/formatting.py` remain
unchanged unless a test exposes a real defect.

## Test Strategy

- Unit tests: V/mV, Ω/kΩ/MΩ conversion; invalid unit rejected; raw values
  preserved; overflow/non-finite still rejected.
- Route tests: default page contains the three panels, seven fields, unit
  selects, circuit labels, seven result rows, and active status.
- Route tests: `100 kΩ` and `100000 Ω` produce the same result.
- Route tests: invalid input preserves value/unit and hides results.
- Route tests: saturation and cutoff status boxes.
- Existing engineering and independent-solver tests stay green.

## Open Decisions for the Builder

- Exact icon shapes and spacing are implementation details; hierarchy and
  labels follow the screenshot.
- Local system font stack is acceptable in place of the screenshot's rounded
  font to avoid a network dependency.
