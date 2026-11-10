# Screenshot-Matched BJT Bias UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Flask BJT bias calculator as the three-panel lab dashboard in the approved screenshot, with working engineering units and the existing calculations preserved.

**Architecture:** A new `bjt/units.py` converts display units (V/mV, Ω/kΩ/MΩ) into the existing SI inputs before calculation. `bjt/routes.py` computes the default page on `GET /` and the submitted form on `POST /calculate`, then renders one Jinja template. The template draws the circuit as inline SVG so its labels follow the form, and CSS Grid supplies the three-column responsive layout.

**Tech Stack:** Python 3.10, Flask 3.x, Jinja2, stdlib `unittest`, inline SVG, plain CSS. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-10-bjt-bias-ui-design.md`

## Global Constraints

- Base engineering units stay SI: volts, ohms, amps; beta is dimensionless.
- Region rules stay `active` / `saturation` / `cutoff`; `VCE_SAT = 0.2`.
- Cross-check tolerance stays `math.isclose(rel_tol=1e-6, abs_tol=1e-9)`.
- Default display values are exactly: `vcc=12.0`, `r1=100`, `r2=22`, `rc=2.2`, `re=1.0`, `beta=100`, `vbe=0.70`.
- Default units are exactly: VCC `V`, R1/R2/RC/RE `kΩ`, beta `—`, VBE `V`.
- The independent cross-check remains active. It is invisible when it matches and shows a red warning when it does not.
- The app must not hard-code or display the screenshot's illustrative result numbers; it calculates real results.
- No new Python or frontend dependencies, no build step, no AJAX.
- `python -m unittest discover -s tests -v` and `python -m unittest test_electrical -v` must both pass at the end.

## Review Focus

1. **Unit tampering:** a forged or corrupted `*_unit` value such as `r1_unit=banana` must produce a field error and no calculation, never silently treat the value as ohms. Pinned by `test_unknown_unit_is_rejected` and `test_unknown_unit_is_an_error`.
2. **Mixed-unit equivalence:** `100 kΩ` and `100000 Ω` must produce identical results, and zero/negative values must still fail after conversion. Pinned by `test_resistance_units_are_equivalent` and `test_validation_still_rejects_zero_and_negative`.
3. **Overflow after conversion:** `1e308` with `kΩ` or `MΩ` becomes infinite and must return a validation error, never NaN, a 500, or an invalid result. Pinned by `test_conversion_can_overflow` and `test_overflow_is_an_error_not_a_500`.
4. **Invalid POST state:** a bad POST must preserve the raw value and selected unit while hiding results and showing the error. Pinned by `test_invalid_post_preserves_values_units_and_hides_results`.
5. **Default/live data fidelity:** the default page must show actually calculated values, and circuit labels must follow submitted inputs rather than static screenshot text. Pinned by `test_default_page_shows_calculated_active_results` and `test_circuit_labels_follow_posted_inputs`.

---

### Task 1: Engineering Unit Conversion

**Files:**
- Create: `bjt/units.py`
- Test: `tests/test_units.py`

**Interfaces:**
- Consumes: `FIELDS`, `parse_inputs` from `bjt.engineering`.
- Produces:
  - `VOLTAGE_UNITS: tuple[str, ...] = ("V", "mV")`
  - `RESISTANCE_UNITS: tuple[str, ...] = ("Ω", "kΩ", "MΩ")`
  - `BETA_UNITS: tuple[str, ...] = ("",)`
  - `UNIT_OPTIONS: dict[str, tuple[str, ...]]` keyed by every `FIELDS` name
  - `DEFAULT_UNITS: dict[str, str]`
  - `DEFAULT_VALUES: dict[str, str]`
  - `FIELD_META: tuple[tuple[str, str, str, str], ...]` of `(name, symbol, subscript, description)`
  - `parse_form(raw: Mapping[str, str]) -> tuple[dict[str, float], dict[str, str]]` returning SI values and field errors.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_units.py`:

```python
import unittest

from bjt.engineering import FIELDS
from bjt.units import (
    DEFAULT_UNITS,
    DEFAULT_VALUES,
    FIELD_META,
    UNIT_OPTIONS,
    parse_form,
)


def form(**overrides):
    raw = dict(DEFAULT_VALUES)
    raw.update({f"{field}_unit": DEFAULT_UNITS[field] for field in FIELDS})
    raw.update(overrides)
    return raw


class TestUnitConversion(unittest.TestCase):
    def test_default_form_converts_to_si(self):
        values, errors = parse_form(form())
        self.assertEqual(errors, {})
        self.assertAlmostEqual(values["vcc"], 12.0)
        self.assertAlmostEqual(values["r1"], 100_000)
        self.assertAlmostEqual(values["r2"], 22_000)
        self.assertAlmostEqual(values["rc"], 2_200)
        self.assertAlmostEqual(values["re"], 1_000)
        self.assertAlmostEqual(values["beta"], 100)
        self.assertAlmostEqual(values["vbe"], 0.7)

    def test_voltage_units_convert_to_volts(self):
        values, errors = parse_form(
            form(vcc="12000", vcc_unit="mV", vbe="700", vbe_unit="mV")
        )
        self.assertEqual(errors, {})
        self.assertAlmostEqual(values["vcc"], 12.0)
        self.assertAlmostEqual(values["vbe"], 0.7)

    def test_resistance_units_convert_to_ohms(self):
        values, errors = parse_form(
            form(r1="100000", r1_unit="Ω", r2="0.022", r2_unit="MΩ")
        )
        self.assertEqual(errors, {})
        self.assertEqual(values["r1"], 100_000)
        self.assertAlmostEqual(values["r2"], 22_000)

    def test_unknown_unit_is_rejected(self):
        _, errors = parse_form(form(r1_unit="banana"))
        self.assertEqual(errors["r1"], "invalid unit")

    def test_bad_text_and_non_finite_are_rejected(self):
        for text in ("abc", "nan", "inf", "-inf", "1e999"):
            _, errors = parse_form(form(vbe=text))
            self.assertIn("vbe", errors, text)

    def test_conversion_can_overflow(self):
        _, errors = parse_form(form(r1="1e308", r1_unit="kΩ"))
        self.assertEqual(errors["r1"], "must be finite")

    def test_validation_still_rejects_zero_and_negative(self):
        _, errors = parse_form(form(r1="0", re="-1"))
        self.assertIn("r1", errors)
        self.assertIn("re", errors)

    def test_metadata_covers_all_fields(self):
        self.assertEqual(tuple(meta[0] for meta in FIELD_META), FIELDS)
        self.assertEqual(set(UNIT_OPTIONS), set(FIELDS))
        self.assertEqual(set(DEFAULT_UNITS), set(FIELDS))
        self.assertEqual(set(DEFAULT_VALUES), set(FIELDS))
        for name in FIELDS:
            self.assertIn(DEFAULT_UNITS[name], UNIT_OPTIONS[name])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_units -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'bjt.units'`.

- [ ] **Step 3: Implement `bjt/units.py`**

Use these exact unit factors:

```python
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
```

Use voltage factors `V=1.0`, `mV=1e-3`; resistance factors `Ω=1.0`,
`kΩ=1e3`, `MΩ=1e6`; beta factor `""=1.0`. Implement `parse_form` to
strip text, validate the unit before conversion, convert each display
value to a base-unit string with `repr(float(text) * factor)`, then pass
that base mapping to `parse_inputs`. If conversion raises `ValueError`,
leave the original text in the base mapping so `parse_inputs` reports
`must be a number`. Merge unit errors after `parse_inputs` errors so
`invalid unit` wins for that field.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_units -v`
Expected: PASS, 8 tests.

- [ ] **Step 5: Run the full current suite**

Run: `python -m unittest discover -s tests -v; python -m unittest test_electrical -v`
Expected: all existing tests plus the 8 new unit tests pass.

- [ ] **Step 6: Commit**

```bash
git add bjt/units.py tests/test_units.py
git commit -m "feat: add display-unit conversion for bias inputs"
```

---

### Task 2: Dashboard Shell, Input Form, and Circuit

**Files:**
- Modify: `bjt/routes.py`
- Modify: `bjt/templates/index.html`
- Modify: `bjt/static/style.css`
- Test: `tests/test_routes.py`

**Interfaces:**
- Consumes: `FIELDS`, `analyze_bias` from `bjt.engineering`; `solve_bias_independent`, `compare_results` from `bjt.independent`; `DEFAULT_UNITS`, `DEFAULT_VALUES`, `FIELD_META`, `UNIT_OPTIONS`, `parse_form` from `bjt.units`.
- Produces:
  - `_calculate(values: dict[str, float]) -> tuple[dict, dict, dict]`
  - `_render(values, units, errors, result=None, independent=None, comparison=None)` with template context keys `values`, `units`, `errors`, `result`, `independent`, `comparison`, `field_meta`, `unit_options`.
  - `GET /` uses display defaults and calculates the initial result.
  - `POST /calculate` reads every `field` and `field_unit`, preserves raw display values/units, and calculates when there are no errors.

- [ ] **Step 1: Replace the old route test with the dashboard-shell tests**

Replace the entire contents of `tests/test_routes.py` with:

```python
import unittest

from bjt import create_app
from bjt.engineering import FIELDS


class TestDashboardShell(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_get_form_page_has_dashboard_shell(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        for text in (
            "Lab 02: BJT DC Bias Web App",
            "ENG29 2121",
            "Computer Programming for",
            "Input Parameters",
            "Circuit: Common-Emitter Amplifier",
            "DC Bias Results",
            "Week 2 Goal",
            "Calculate DC Bias",
        ):
            self.assertIn(text, html)

        for name in FIELDS:
            self.assertIn(f'name="{name}"', html)

        for name in ("vcc", "r1", "r2", "rc", "re", "vbe"):
            self.assertIn(f'name="{name}_unit"', html)
        self.assertIn('name="beta_unit"', html)

        for value in ('value="12.0"', 'value="100"', 'value="22"',
                      'value="2.2"', 'value="1.0"', 'value="0.70"'):
            self.assertIn(value, html)

        self.assertIn('value="kΩ" selected', html)
        self.assertIn("100 kΩ", html)
        self.assertIn("22 kΩ", html)
        self.assertIn("2.2 kΩ", html)
        self.assertIn("1.0 kΩ", html)
        self.assertIn("12.0 V", html)
        self.assertIn("β = 100", html)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_routes.TestDashboardShell -v`
Expected: FAIL because the current page has no dashboard headers, units, or schematic.

- [ ] **Step 3: Implement the route context**

Rewrite `bjt/routes.py` around these helpers:

```python
def _form_payload(values, units):
    payload = dict(values)
    payload.update({f"{field}_unit": units[field] for field in FIELDS})
    return payload


def _calculate(values):
    result = analyze_bias(**values)
    independent = solve_bias_independent(**values)
    comparison = compare_results(result, independent)
    return result, independent, comparison


def _render(values, units, errors, result=None, independent=None, comparison=None):
    return render_template(
        "index.html",
        values=values,
        units=units,
        errors=errors,
        result=result,
        independent=independent,
        comparison=comparison,
        field_meta=FIELD_META,
        unit_options=UNIT_OPTIONS,
    )
```

`index()` copies `DEFAULT_VALUES` and `DEFAULT_UNITS`, calls
`parse_form(_form_payload(...))`, calculates when `errors` is empty, and
renders. `calculate()` reads every `field` and `field_unit` from
`request.form`, defaulting a missing unit to `DEFAULT_UNITS[field]`, calls
`parse_form`, calculates when there are no errors, and renders. Catch
`ValueError` from `_calculate` into `errors["_form"]` exactly as the old
route did. Do not import or use `engineering.DEFAULTS` in the route.

- [ ] **Step 4: Rebuild the template shell and inline circuit**

Replace `bjt/templates/index.html` with the dashboard structure:

- Header: circuit-chip icon, `Lab 02: BJT DC Bias Web App`, subtitle
  `ENG29 2121 – Common Emitter (Voltage Divider Bias)`, right-side course
  badge `Computer Programming for Electrical Engineers`.
- Main grid: `<form class="panel input-panel" action="/calculate" method="post">`
  containing `Input Parameters`, then `<section class="panel circuit-panel">`
  containing `Circuit: Common-Emitter Amplifier`, then
  `<section class="panel results-panel">` containing `DC Bias Results`.
- Input rows loop over `field_meta` as `(name, symbol, subscript, description)`.
  Render `symbol` plus `<sub>{{ subscript }}</sub>` when non-empty, then
  `(description)`. Render the numeric input with `id`/`name` equal to `name`,
  `type="number"`, `step="any"`, and `value="{{ values[name] }}"`.
- When `unit_options[name]|length > 1`, render a select named
  `{{ name }}_unit` with one option per unit and `selected` on
  `units[name]`. Otherwise render a static `—` and a hidden input named
  `{{ name }}_unit` with an empty value.
- Show `errors[name]` immediately below the affected row and
  `errors['_form']` below the Calculate button.
- Button label is exactly `Calculate DC Bias`.
- Results panel contains only a placeholder in this task; Task 3 adds the
  table and status box.
- Footer is `<footer class="goal-panel">` with a target icon, `Week 2 Goal`,
  and this target text with the engineering symbols as subscripts:
  `Rough target for this lab: Build a Flask web app that takes the circuit
  parameters, computes the BJT DC bias (V_B, V_E, V_C, V_CE, I_B, I_C, I_E)
  for a common-emitter amplifier with voltage-divider bias, and displays the
  results.`

Use an inline SVG sprite at the top of `<body>` for the chip, code,
sliders, chart, calculator, target, check, and alert icons. Use
`<svg class="icon"><use href="#icon-name"></use></svg>` at call sites.

Draw the schematic as one inline SVG with `class="schematic"` and
`viewBox="0 0 420 340"`, `role="img"`, and an `aria-label`. It must show:

- top VCC rail with `VCC = {{ values.vcc }} {{ units.vcc }}`
- R1 in the left divider branch with `{{ values.r1 }} {{ units.r1 }}`
- R2 below the base node with `{{ values.r2 }} {{ units.r2 }}`
- RC in the collector branch with `{{ values.rc }} {{ units.rc }}`
- RE in the emitter branch with `{{ values.re }} {{ units.re }}`
- Q1 NPN circle and symbol, labelled `Q1`, `NPN`, and
  `(β = {{ values.beta }})`
- ground symbols below R2 and RE

Use stroke-only wires and resistor zigzags, small junction dots, and
`text-anchor` labels that stay inside the viewBox.

- [ ] **Step 5: Add the dashboard CSS**

Replace `bjt/static/style.css` with a visual system that supports:

- `:root` variables for blue/teal accent, green, amber, ink, muted, line,
  page background, and card background
- a max-width page card with light blue border, rounded corners, and shadow
- a header flex row with brand lockup and course badge
- `.dashboard` as a three-column CSS Grid with `gap: 12px`, stacking to one
  column below `800px`
- `.panel`, `.panel-header`, and `.panel-header h2` styling with a bottom
  divider and compact headings
- `.field-row` with label on the left and a compact input/unit control on the
  right; numeric inputs around 64px wide and unit selects around 48px
- `.calculate` as a full-width teal button
- `.schematic` filling the panel width and scaling with `height: auto`
- `.goal-panel` as a full-width blue-bordered footer row

Keep the page legible at 800px width, matching the screenshot's density.

- [ ] **Step 6: Run the shell test to verify it passes**

Run: `python -m unittest tests.test_routes.TestDashboardShell -v`
Expected: PASS.

- [ ] **Step 7: Run the full suite**

Run: `python -m unittest discover -s tests -v; python -m unittest test_electrical -v`
Expected: all tests pass. The old result assertions are gone because Step 1 replaced the whole route test file.

- [ ] **Step 8: Commit**

```bash
git add bjt/routes.py bjt/templates/index.html bjt/static/style.css tests/test_routes.py
git commit -m "feat: build screenshot-matched bias dashboard shell"
```

---

### Task 3: Results Table, Region Status, and Validation States

**Files:**
- Modify: `bjt/templates/index.html`
- Modify: `bjt/static/style.css`
- Modify: `tests/test_routes.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `result`, `independent`, `comparison` from Task 2; existing Jinja filters `current`, `voltage`, `delta`; `result.region`, `result.warnings`, `comparison.matches`.
- Produces: the seven-row results table, region status box, hidden passing cross-check text, visible failing cross-check warning, and the invalid-input placeholder.

- [ ] **Step 1: Add the failing result/state tests**

Append to `tests/test_routes.py`:

```python
from unittest.mock import patch

VALID_FORM = {
    "vcc": "12.0", "vcc_unit": "V",
    "r1": "100", "r1_unit": "kΩ",
    "r2": "22", "r2_unit": "kΩ",
    "rc": "2.2", "rc_unit": "kΩ",
    "re": "1.0", "re_unit": "kΩ",
    "beta": "100", "beta_unit": "",
    "vbe": "0.70", "vbe_unit": "V",
}


class TestDashboardResults(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_default_page_shows_calculated_active_results(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Active region approximation OK", html)
        self.assertIn("1.942 V", html)
        self.assertIn("12.30 µA", html)
        self.assertIn("8.052 V", html)
        self.assertIn("Independent cross-check passed", html)
        for label in ("V<sub>B</sub>", "V<sub>E</sub>", "V<sub>C</sub>",
                      "V<sub>CE</sub>", "I<sub>B</sub>", "I<sub>C</sub>",
                      "I<sub>E</sub>"):
            self.assertIn(label, html)
        positions = [html.index(label) for label in (
            "V<sub>B</sub>", "V<sub>E</sub>", "V<sub>C</sub>",
            "V<sub>CE</sub>", "I<sub>B</sub>", "I<sub>C</sub>",
            "I<sub>E</sub>",
        )]
        self.assertEqual(positions, sorted(positions))

    def test_valid_post_shows_results(self):
        html = self.client.post("/calculate", data=VALID_FORM).get_data(as_text=True)
        self.assertIn("Active region approximation OK", html)
        self.assertIn("1.942 V", html)
        self.assertIn("12.30 µA", html)
        self.assertIn("8.052 V", html)

    def test_resistance_units_are_equivalent(self):
        a = self.client.post("/calculate", data=VALID_FORM).get_data(as_text=True)
        b = self.client.post(
            "/calculate",
            data={**VALID_FORM, "r1": "100000", "r1_unit": "Ω"},
        ).get_data(as_text=True)
        for text in ("1.942 V", "8.052 V", "1.230 mA"):
            self.assertIn(text, a)
            self.assertIn(text, b)

    def test_invalid_post_preserves_values_units_and_hides_results(self):
        html = self.client.post(
            "/calculate", data={**VALID_FORM, "r1": "0"}
        ).get_data(as_text=True)
        self.assertIn("must be greater than zero", html)
        self.assertIn('value="0"', html)
        self.assertIn('value="kΩ" selected', html)
        self.assertNotIn("Active region approximation OK", html)
        self.assertIn("Enter valid parameters", html)

    def test_saturation_post_shows_warning(self):
        html = self.client.post(
            "/calculate",
            data={
                **VALID_FORM,
                "r1": "47", "r2": "10", "rc": "10",
                "re": "100", "re_unit": "Ω", "beta": "150",
            },
        ).get_data(as_text=True)
        self.assertIn("Saturation region", html)
        self.assertIn("not valid", html)
        self.assertIn("region-saturation", html)

    def test_cutoff_post_shows_cutoff(self):
        html = self.client.post(
            "/calculate",
            data={
                **VALID_FORM,
                "vcc": "5", "r1": "100", "r2": "1",
                "rc": "1", "re": "1", "beta": "100",
            },
        ).get_data(as_text=True)
        self.assertIn("Cutoff region", html)
        self.assertIn("transistor is off", html)

    def test_unknown_unit_is_an_error(self):
        html = self.client.post(
            "/calculate", data={**VALID_FORM, "r1_unit": "banana"}
        ).get_data(as_text=True)
        self.assertIn("invalid unit", html)
        self.assertNotIn("Active region approximation OK", html)

    def test_overflow_is_an_error_not_a_500(self):
        response = self.client.post(
            "/calculate",
            data={**VALID_FORM, "r1": "1e308", "r1_unit": "kΩ"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("must be finite", response.get_data(as_text=True))
        self.assertNotIn("Active region approximation OK", response.get_data(as_text=True))

    def test_crosscheck_failure_shows_warning(self):
        with patch(
            "bjt.routes.compare_results",
            return_value={"matches": False, "deltas": {}},
        ):
            html = self.client.post(
                "/calculate", data=VALID_FORM
            ).get_data(as_text=True)
        self.assertIn("Independent cross-check did not match", html)

    def test_circuit_labels_follow_posted_inputs(self):
        html = self.client.post(
            "/calculate", data={**VALID_FORM, "vcc": "9", "r1": "47"}
        ).get_data(as_text=True)
        self.assertIn("47 kΩ", html)
        self.assertIn("9 V", html)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python -m unittest tests.test_routes.TestDashboardResults -v`
Expected: FAIL because the template has only the placeholder and no result rows/status box.

- [ ] **Step 3: Add results and status markup**

Extend the results panel in `bjt/templates/index.html`:

- When `result` exists, render the table in this exact order:
  `V_B`, `V_E`, `V_C`, `V_CE`, `I_B`, `I_C`, `I_E`, using
  `result['vb']|voltage`, `result['ve']|voltage`, `result['vc']|voltage`,
  `result['vce']|voltage`, and the matching `current` filters for currents.
- Render symbols as `V<sub>B</sub>` etc., with the quantity cell left
  aligned and the value cell right aligned.
- Add a region box with class `region-{{ result.region }}`:
  - active: check icon, `Active region approximation OK`, and
    `V<sub>CE</sub> = {{ result.vce|voltage }} > 0.2 V (transistor in active region)`
  - saturation: alert icon, `Saturation region`, and
    `V<sub>CE</sub> = {{ result.vce|voltage }} < 0.2 V (active-region equations are not valid)`
  - cutoff: alert icon, `Cutoff region`, and
    `I<sub>B</sub> = 0 (transistor is off)`
- When `comparison` exists and matches, add
  `<span class="sr-only">Independent cross-check passed</span>`.
- When `comparison` exists and does not match, add a visible red
  `Independent cross-check did not match; results may be unreliable.`
- When `result` is absent, render the placeholder
  `Enter valid parameters and calculate to see the DC operating point.`

- [ ] **Step 4: Add results/status CSS**

Add to `bjt/static/style.css`:

- `.results-table` two-column table with compact rows, left-aligned
  quantity symbols, right-aligned tabular values, and bottom dividers
- `.region-box` with `.region-active` green, `.region-saturation` red, and
  `.region-cutoff` neutral/amber variants; rounded corners, border, and
  compact padding
- `.region-title` flex row with icon and bold label
- `.crosscheck-error` red small text
- `.results-empty` muted placeholder text
- `.sr-only` visually hidden but accessible

- [ ] **Step 5: Update README**

Append to `README.md`:

```markdown
### Units

Voltages accept `V` or `mV`. Resistances accept `Ω`, `kΩ`, or `MΩ`. Beta is
dimensionless. Values are converted to SI units before calculation.
```

- [ ] **Step 6: Run the new tests to verify they pass**

Run: `python -m unittest tests.test_routes -v`
Expected: PASS, all shell and result tests.

- [ ] **Step 7: Run the full suite**

Run: `python -m unittest discover -s tests -v; python -m unittest test_electrical -v`
Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add bjt/templates/index.html bjt/static/style.css tests/test_routes.py README.md
git commit -m "feat: show bias results and region status in new dashboard"
```

---

## Final Verification

After Task 3, run the app and inspect it in the browser at
`http://127.0.0.1:5000/`:

- The default page matches the three-panel screenshot layout.
- Unit selects change values; `100 kΩ` and `100000 Ω` produce the same
  results.
- An invalid value such as `R1 = 0` keeps the value and unit, shows the
  error, and hides results.
- Saturation and cutoff cases show the correct status box.
- The page stacks cleanly below 800px.
- No console errors.

Run both test commands one final time and report the counts.
