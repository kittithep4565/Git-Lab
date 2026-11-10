# BJT Common-Emitter DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Flask web app that computes, validates, and cross-checks the DC operating point of an NPN voltage-divider common-emitter bias circuit.

**Architecture:** A `bjt` package holds pure engineering logic (`engineering.py`), an independently written numeric solver (`independent.py`), and a Flask blueprint (`routes.py`). `create_app()` builds the app, Jinja renders one page, and plain CSS styles it. Tests use `unittest` and the Flask test client.

**Tech Stack:** Python 3.10, Flask 3.x, Jinja2, `unittest` (stdlib only), plain CSS.

**Spec:** `docs/superpowers/specs/2026-11-10-bjt-ce-bias-design.md`

## Global Constraints

- Python 3.10.11 on Windows; run with `python run.py` at `http://127.0.0.1:5000`.
- Only runtime dependency: `Flask>=3.0,<4`. Tests use stdlib `unittest`.
- No JavaScript, AC, transient, circuit editor, FET, or PNP. NPN only.
- Resistances are entered and stored in Ω (no `47k` suffix).
- `VCE_SAT = 0.2` V. Saturation is strictly `VCE < 0.2`; `VCE == 0.2` is active. Cutoff is `IB <= 0`.
- Require finite numbers; reject `bool`; `VCC > 0`; `R1, R2, RC, RE > 0`; `β > 0`; `0 <= VBE < VCC`.
- Comparison tolerance: `math.isclose(rel_tol=1e-6, abs_tol=1e-9)`.
- Do not modify `electrical.py` or `test_electrical.py`; both must keep passing.
- Branch: `feature/bjt-bias-app`; final merge to `main` and push to `origin`.

## Review Focus

1. Extreme finite resistances (`R1 = R2 = 1e308`) overflow `VBB` to `NaN`; the app must return a validation error, never a 500 or `NaN` output. Tests: Task 1 (`analyze_bias` raises) and Task 4 (POST returns 200 with an error).
2. Form text `"nan"`, `"inf"`, `"-inf"`, and `"1e999"` must be rejected as non-finite. Test: Task 1 `test_parse_rejects_nan_inf_and_overflow_text`.
3. The cutoff boundary `VBB == VBE` (`IB == 0`) must be reported as cutoff, not a tiny active result. Test: Task 1 `test_cutoff_boundary_vbb_equals_vbe`.
4. `VCE == 0.2` exactly must classify as active, while `0.199999` is saturation. Test: Task 1 `test_vce_exactly_vce_sat_is_active`.
5. An invalid POST must keep the user's raw values and render no results table. Test: Task 4 `test_invalid_post_keeps_values_and_hides_results`.

---

## Execution Setup

- [ ] Create the branch and commit the approved design before Task 1.

```bash
git switch -c feature/bjt-bias-app
git add docs/superpowers/specs/2026-11-10-bjt-ce-bias-design.md docs/superpowers/plans/2026-11-10-bjt-ce-bias.md
git commit -m "docs: add BJT bias app design and plan"
```

---

### Task 1: Engineering Core

**Files:**
- Create: `bjt/__init__.py` (empty package marker for now)
- Create: `bjt/engineering.py`
- Create: `tests/__init__.py` (empty)
- Test: `tests/test_engineering.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `FIELDS: tuple[str, ...] = ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")`
  - `DEFAULTS: dict[str, str]` with `vcc="12"`, `r1="47000"`, `r2="10000"`, `rc="2200"`, `re="1000"`, `beta="150"`, `vbe="0.7"`
  - `VCE_SAT: float = 0.2`
  - `parse_inputs(raw: Mapping[str, str]) -> tuple[dict[str, float], dict[str, str]]`
  - `analyze_bias(vcc, r1, r2, rc, re, beta, vbe) -> dict` with float keys `ib, ic, ie, vb, ve, vc, vce`, plus `region: str` (`"active" | "saturation" | "cutoff"`) and `warnings: list[str]`
  - `classify_region(ib: float, vce: float) -> str`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_engineering.py`:

```python
import unittest

from bjt.engineering import analyze_bias, classify_region, parse_inputs

VALID = {"vcc": "12", "r1": "47000", "r2": "10000", "rc": "2200",
         "re": "1000", "beta": "150", "vbe": "0.7"}


class TestOperatingPoint(unittest.TestCase):
    def test_textbook_example(self):
        r = analyze_bias(12, 47000, 10000, 2200, 1000, 150, 0.7)
        self.assertAlmostEqual(r["ib"], 8.8245e-6, places=9)
        self.assertAlmostEqual(r["ic"], 1.323675e-3, places=9)
        self.assertAlmostEqual(r["ie"], 1.3325e-3, places=9)
        self.assertAlmostEqual(r["vb"], 2.0325, places=6)
        self.assertAlmostEqual(r["ve"], 1.3325, places=6)
        self.assertAlmostEqual(r["vc"], 9.087915, places=6)
        self.assertAlmostEqual(r["vce"], 7.755415, places=6)
        self.assertEqual(r["region"], "active")
        self.assertEqual(r["warnings"], [])

    def test_outputs_change_with_inputs(self):
        a = analyze_bias(12, 47000, 10000, 2200, 1000, 150, 0.7)
        b = analyze_bias(15, 47000, 10000, 2200, 1000, 150, 0.7)
        self.assertGreater(b["ic"], a["ic"])
        self.assertNotAlmostEqual(b["vce"], a["vce"], places=6)

    def test_cutoff(self):
        r = analyze_bias(5, 100000, 1000, 1000, 1000, 100, 0.7)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ib"], 0.0)
        self.assertEqual(r["vce"], 5.0)
        self.assertAlmostEqual(r["vb"], 0.04950495, places=6)

    def test_cutoff_boundary_vbb_equals_vbe(self):
        r = analyze_bias(10, 90, 10, 100, 100, 100, 1.0)
        self.assertEqual(r["region"], "cutoff")
        self.assertEqual(r["ib"], 0.0)

    def test_saturation(self):
        r = analyze_bias(12, 47000, 10000, 10000, 100, 150, 0.7)
        self.assertEqual(r["region"], "saturation")
        self.assertTrue(any("saturation" in w for w in r["warnings"]))


class TestRegionBoundary(unittest.TestCase):
    def test_vce_exactly_vce_sat_is_active(self):
        self.assertEqual(classify_region(1e-3, 0.2), "active")
        self.assertEqual(classify_region(1e-3, 0.199999), "saturation")
        self.assertEqual(classify_region(0.0, 5.0), "cutoff")


class TestValidation(unittest.TestCase):
    def test_parse_rejects_missing_and_text(self):
        _, errors = parse_inputs({**VALID, "vcc": "", "r1": "abc"})
        self.assertIn("vcc", errors)
        self.assertIn("r1", errors)

    def test_parse_rejects_nan_inf_and_overflow_text(self):
        for text in ("nan", "inf", "-inf", "1e999"):
            _, errors = parse_inputs({**VALID, "vbe": text})
            self.assertIn("vbe", errors, text)

    def test_parse_rejects_non_positive_and_bad_vbe(self):
        for field in ("vcc", "r1", "r2", "rc", "re", "beta"):
            _, errors = parse_inputs({**VALID, field: "0"})
            self.assertIn(field, errors, field)
        _, errors = parse_inputs({**VALID, "vbe": "12"})
        self.assertIn("vbe", errors)

    def test_bool_is_rejected(self):
        with self.assertRaises(TypeError):
            analyze_bias(12, 47000, 10000, 2200, 1000, True, 0.7)

    def test_overflow_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_bias(12, 1e308, 1e308, 2200, 1000, 150, 0.7)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'bjt'`.

- [ ] **Step 3: Implement the engineering core**

Create `bjt/__init__.py` and `tests/__init__.py` as empty files. In `bjt/engineering.py`:

- Define `FIELDS`, `DEFAULTS`, and `VCE_SAT` exactly as in Interfaces.
- Define a private `_validate_values(values: Mapping[str, float]) -> dict[str, str]` that returns field errors: non-number/`bool` → TypeError; non-finite → `"must be finite"`; `vcc/r1/r2/rc/re/beta <= 0` → `"must be greater than zero"`; `vbe < 0` → `"must be zero or greater"`; `vbe >= vcc` → `"must be less than VCC"`.
- `parse_inputs` strips each string; missing/empty → `"required"`; `float()` failure → `"must be a number"`; otherwise run `_validate_values` on the successfully parsed fields.
- `analyze_bias` validates its arguments, then implements the spec formulas:

```python
rbb = r1 * r2 / (r1 + r2)
vbb = vcc * r2 / (r1 + r2)
ib = (vbb - vbe) / (rbb + (beta + 1) * re)
```

  If `ib <= 0`, return cutoff values: `ib=ic=ie=0.0`, `ve=0.0`, `vb=vbb`, `vc=vcc`, `vce=vcc`, `region="cutoff"`, warning `"Transistor is in cutoff (IB <= 0)."`.
  Otherwise compute `ic = beta * ib`, `ie = (beta + 1) * ib`, `ve = ie * re`, `vb = ve + vbe`, `vc = vcc - ic * rc`, `vce = vc - ve`.
  Before returning, raise `ValueError("operating point is out of range")` unless every computed quantity is finite.
  Classify with `classify_region(ib, vce)`; add the saturation warning `"Transistor is in saturation (VCE < 0.2 V); active-region equations are not valid."` when saturated; active returns `warnings=[]`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest discover -s tests -v`
Expected: all Task 1 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add bjt/__init__.py bjt/engineering.py tests/__init__.py tests/test_engineering.py
git commit -m "feat: add BJT bias engineering core"
```

---

### Task 2: Independent Solver and Comparison

**Files:**
- Create: `bjt/independent.py`
- Test: `tests/test_independent.py`

**Interfaces:**
- Consumes: `analyze_bias` and `classify_region` from `bjt.engineering`; result dict shape from Task 1.
- Produces:
  - `solve_bias_independent(vcc, r1, r2, rc, re, beta, vbe) -> dict` with the same keys as `analyze_bias` (`ib, ic, ie, vb, ve, vc, vce, region, warnings`).
  - `QUANTITIES: tuple[str, ...] = ("ib", "ic", "ie", "vb", "ve", "vc", "vce")`
  - `compare_results(primary: dict, independent: dict, rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> dict` with `matches: bool` and `deltas: dict[str, float]` where each delta is `independent[q] - primary[q]`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_independent.py`:

```python
import unittest

from bjt.engineering import analyze_bias
from bjt.independent import compare_results, solve_bias_independent

CASES = {
    "active": (12, 47000, 10000, 2200, 1000, 150, 0.7),
    "cutoff": (5, 100000, 1000, 1000, 1000, 100, 0.7),
    "saturation": (12, 47000, 10000, 10000, 100, 150, 0.7),
}


class TestIndependentSolver(unittest.TestCase):
    def test_matches_closed_form_for_every_region(self):
        for name, args in CASES.items():
            with self.subTest(name=name):
                primary = analyze_bias(*args)
                independent = solve_bias_independent(*args)
                self.assertEqual(independent["region"], primary["region"])
                self.assertTrue(compare_results(primary, independent)["matches"], name)

    def test_compare_detects_mismatch(self):
        primary = analyze_bias(*CASES["active"])
        independent = solve_bias_independent(*CASES["active"])
        independent["ic"] *= 1.001
        self.assertFalse(compare_results(primary, independent)["matches"])

    def test_solution_satisfies_base_kcl(self):
        r = solve_bias_independent(12, 47000, 10000, 2200, 1000, 150, 0.7)
        vb = 0.7 + 151 * r["ib"] * 1000
        residual = (12 - vb) / 47000 - vb / 10000 - r["ib"]
        self.assertAlmostEqual(residual, 0.0, places=12)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_independent -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'bjt.independent'`.

- [ ] **Step 3: Implement the independent solver**

In `bjt/independent.py`, validate arguments the same way as `analyze_bias` (reuse a small local check; raising `TypeError`/`ValueError` for the same cases). Solve the base-node KCL numerically:

```python
def f(ib):
    vb = vbe + (beta + 1) * ib * re
    return (vcc - vb) / r1 - vb / r2 - ib

if f(0.0) <= 0:
    # cutoff: same reporting values as the closed form
    vbb = vcc * r2 / (r1 + r2)
    return {... region "cutoff", vb=vbb, ve=0.0, vc=vcc, vce=vcc, ib=ic=ie=0.0 ...}

lo, hi = 0.0, vcc / r1
while f(hi) > 0 and hi < 1e12:
    hi *= 2
for _ in range(200):
    mid = (lo + hi) / 2
    if f(mid) > 0:
        lo = mid
    else:
        hi = mid
ib = (lo + hi) / 2
```

Compute `ic`, `ie`, `ve`, `vb`, `vc`, `vce` from `ib` with the same physics equations, raise `ValueError("operating point is out of range")` if any result is non-finite, classify with `classify_region`, and use the same warning strings as Task 1.

Implement `compare_results` using `QUANTITIES`, `math.isclose`, and subtraction for each delta.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_independent -v`
Expected: all Task 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add bjt/independent.py tests/test_independent.py
git commit -m "feat: add independent bias solver and comparison"
```

---

### Task 3: Flask App Scaffold and Input Form

**Files:**
- Modify: `bjt/__init__.py`
- Create: `bjt/routes.py`
- Create: `bjt/templates/index.html`
- Create: `bjt/static/style.css`
- Create: `run.py`
- Create: `requirements.txt`
- Modify: `README.md` (append run/test instructions)
- Test: `tests/test_routes.py`

**Interfaces:**
- Consumes: `FIELDS` and `DEFAULTS` from `bjt.engineering`.
- Produces: `create_app() -> flask.Flask`; blueprint endpoint `bias.index` at `GET /`; template context `values`, `errors`, `result` (Task 3 uses `result=None`).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_routes.py`:

```python
import unittest

from bjt import create_app


class TestFormPage(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_get_form_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for name in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{name}"', html)
        self.assertIn('value="47000"', html)
        self.assertIn('action="/calculate"', html)
        self.assertIn('method="post"', html)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_routes -v`
Expected: FAIL with `ImportError: cannot import name 'create_app'`.

- [ ] **Step 3: Implement the scaffold**

- `bjt/routes.py`: `bp = Blueprint("bias", __name__)`; `@bp.get("/")` returns `render_template("index.html", values=DEFAULTS, errors={}, result=None)`.
- `bjt/__init__.py`: `create_app()` creates `Flask(__name__)`, registers `bp`, and returns it.
- `bjt/templates/index.html`: HTML5 page with `<form action="/calculate" method="post">`, seven labeled numeric inputs (`type="number" step="any"`), values from `values`, per-field errors from `errors`, and a submit button. Link `style.css` via `url_for`.
- `bjt/static/style.css`: readable system font, centered card, responsive two-column form grid, error text in red, table and badge base styles.
- `run.py`: builds `create_app()` and runs `host="127.0.0.1", port=5000, debug=True` under `if __name__ == "__main__"`.
- `requirements.txt`: `Flask>=3.0,<4`.
- `README.md`: append a section with install, `python run.py`, browser URL, and `python -m unittest discover -s tests -v`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_routes -v`
Expected: Task 3 test PASS.

- [ ] **Step 5: Commit**

```bash
git add bjt/__init__.py bjt/routes.py bjt/templates/index.html bjt/static/style.css run.py requirements.txt README.md tests/test_routes.py
git commit -m "feat: add Flask form page and run instructions"
```

---

### Task 4: Calculation Route, Formatting, and Comparison View

**Files:**
- Create: `bjt/formatting.py`
- Modify: `bjt/__init__.py` (register Jinja filters)
- Modify: `bjt/routes.py` (add `POST /calculate`)
- Modify: `bjt/templates/index.html` (results section)
- Modify: `bjt/static/style.css` (badges, table)
- Test: `tests/test_routes.py` (add POST tests)

**Interfaces:**
- Consumes: `FIELDS`, `parse_inputs`, `analyze_bias`; `solve_bias_independent`, `compare_results`; `create_app`.
- Produces:
  - `format_current(value_a: float) -> str` → `"8.80 µA"`, `"1.324 mA"`, or `"1.500 A"`
  - `format_voltage(value_v: float) -> str` → `"7.755 V"`
  - `format_delta(value: float) -> str` → `"{value:.2e}"`
  - Jinja filters `current`, `voltage`, `delta`
  - `POST /calculate` rendering the same template with `values` (raw strings), `errors`, `result`, `independent`, `comparison`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_routes.py`:

```python
VALID = {"vcc": "12", "r1": "47000", "r2": "10000", "rc": "2200",
         "re": "1000", "beta": "150", "vbe": "0.7"}


class TestCalculateRoute(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_valid_post_shows_both_calculations(self):
        response = self.client.post("/calculate", data=VALID)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Closed-form", html)
        self.assertIn("Independent", html)
        self.assertIn("ACTIVE", html)
        self.assertIn("Matches within tolerance", html)
        self.assertIn("8.82 µA", html)

    def test_invalid_post_keeps_values_and_hides_results(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "0"})
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("must be greater than zero", html)
        self.assertIn('value="0"', html)
        self.assertNotIn("Closed-form", html)

    def test_saturation_post_shows_warning(self):
        response = self.client.post("/calculate", data={**VALID, "rc": "10000", "re": "100"})
        html = response.get_data(as_text=True)
        self.assertIn("SATURATION", html)
        self.assertIn("not valid", html)

    def test_cutoff_post_shows_cutoff(self):
        response = self.client.post("/calculate", data={**VALID, "vcc": "5", "r1": "100000", "r2": "1000"})
        self.assertIn("CUTOFF", response.get_data(as_text=True))

    def test_overflow_is_an_error_not_a_500(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "1e308", "r2": "1e308"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("out of range", response.get_data(as_text=True))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_routes -v`
Expected: the new POST tests FAIL with 404/405 or missing content.

- [ ] **Step 3: Implement formatting, route, and results view**

- `bjt/formatting.py`: implement the three functions; use `abs(value)` thresholds `>= 1` → A, `>= 1e-3` → mA, else µA, with the exact formats shown in Interfaces.
- `bjt/routes.py`: add `@bp.post("/calculate")`; build `raw = {field: request.form.get(field, "") for field in FIELDS}`, call `parse_inputs(raw)`. If there are errors, render with `values=raw`, `errors`, `result=None`. Otherwise call `analyze_bias(**values)`, `solve_bias_independent(**values)`, and `compare_results(...)` inside `try/except ValueError`; on error, set `errors["_form"] = str(exc)` and render without results.
- `bjt/__init__.py`: register `current`, `voltage`, `delta` filters from `bjt.formatting`.
- `index.html`: show `errors.get('_form')` as a form-level error message. When `result` is set, render a region badge (`result.region|upper` with class `badge-{{ result.region }}`), the warnings list, and a four-column table (Quantity, Closed-form, Independent, Delta) for `ib, ic, ie` with the `current` filter, `vb, ve, vc, vce` with `voltage`, and each `comparison.deltas.<q>` with `delta`. Show `Matches within tolerance` or `Mismatch` based on `comparison.matches`.
- `style.css`: green badge for active, red for saturation, gray for cutoff; style warnings and the table.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_routes -v`
Expected: all route tests PASS.

- [ ] **Step 5: Commit**

```bash
git add bjt/formatting.py bjt/__init__.py bjt/routes.py bjt/templates/index.html bjt/static/style.css tests/test_routes.py
git commit -m "feat: show operating point and independent comparison"
```

---

## Final Verification

- [ ] Run the full new suite: `python -m unittest discover -s tests -v` — all pass.
- [ ] Run the existing suite: `python -m unittest test_electrical -v` — all pass.
- [ ] Run `python run.py`, open `http://127.0.0.1:5000`, submit the defaults, and confirm ACTIVE, the seven rows, and the match badge.
- [ ] Submit `R1=0` and confirm the per-field error and preserved value.
- [ ] Submit `RC=10000, RE=100` and confirm the SATURATION warning.
- [ ] Stop the server, then merge `feature/bjt-bias-app` into `main` and push to `origin` (finishing-a-development-branch).
