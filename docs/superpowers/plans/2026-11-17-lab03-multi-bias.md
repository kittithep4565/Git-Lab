# Lab 03 — Multi-Mode BJT DC Bias Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline execution was requested). Steps use checkbox (`- [ ]`) syntax.

**Goal:** Extend the Lab 02 Flask app so one page computes DC bias for three modes — Voltage Divider (unchanged results), Fixed Bias and single-supply Emitter Bias — with per-mode input validation and browser acceptance evidence.

**Architecture:** Keep equations in `bjt/engineering.py` (one function per mode plus a dispatcher), keep the independent bisection cross-check in `bjt/independent.py` (one solver per mode), and let `bjt/routes.py` choose the mode with `if/elif`, convert units once at input, and validate only the fields the mode uses. The Jinja template renders mode tabs, only the active mode's fields, and a matching schematic. No JavaScript: switching modes is a GET (`/?mode=...`) that reloads the form.

**Tech Stack:** Python 3.12, Flask 3.1, Jinja2, unittest (existing suite only), OpenCode Browser for acceptance.

**Spec:** `C:\Users\B6827441\Downloads\ENG29_2121_Lab03_BJT_Bias_Web_App.html`

## Global Constraints

- DC operating point only; no SPICE, load line, AC/transient, bypass capacitors.
- Shared inputs: `VCC`, `RC`, `β`, `VBE`. Divider adds `R1`, `R2`, `RE`; Fixed adds `RB`; Emitter adds `RB`, `RE`.
- Keep existing result keys and units: `ib, ic, ie, vb, ve, vc, vce` (SI: A, V) plus `region`, `warnings`; display V and mA/µA.
- Invalid input (empty, non-numeric, non-finite, non-positive where required) → field error; unknown mode → error, never fall back to Divider.
- Valid input but `IB <= 0` or `VCE <= 0.2 V` → active-model warning, not an error.
- Divider with the Lab 02 inputs must reproduce the Lab 02 numbers.
- Do not add new unittest files (lab rule); keep `python -m unittest discover -s tests` green.

## Review Focus

- Submitting a Fixed/Emitter form that still carries stale `r1`/`r2` keys from the browser must not require or use them.
- Unknown `mode` value in a POST must produce a visible error and no result block.
- Unknown unit string must produce an "invalid unit" error instead of a silent 1.0 scale.
- Switching modes must not show the previous mode's result underneath the new form.
- Emitter results must change when only `RE` changes (A4 direction check).

---

### Task 1: Mode-aware engineering core

**Files:**
- Modify: `bjt/engineering.py`
- Test: existing `tests/test_engineering.py` must stay green

**Interfaces:**
- Produces: `MODES`, `MODE_LABELS`, `MODE_FIELDS`, `ALL_FIELDS`, `parse_mode_inputs(mode, raw) -> (values, errors)`, `analyze_fixed(vcc, rb, rc, beta, vbe) -> dict`, `analyze_emitter(vcc, rb, re, rc, beta, vbe) -> dict`, `analyze_mode(mode, values) -> dict`.
- Consumes: existing `_validate_values`, `classify_region`, `analyze_bias`.

- [ ] **Step 1:** Add `rb` field metadata, positive-validation entry, `MODES = ("divider", "fixed", "emitter")`, per-mode field tuples, `parse_mode_inputs` that requires only the mode's fields.
- [ ] **Step 2:** Implement `analyze_fixed` (IB = (VCC−VBE)/RB, VE = 0) and `analyze_emitter` (IB = (VCC−VBE)/(RB+(β+1)RE)) returning the same result dict shape; reuse the existing cutoff/saturation/warning logic through a shared helper so all three modes agree.
- [ ] **Step 3:** Add `analyze_mode` dispatcher; unknown mode raises `ValueError`.
- [ ] **Step 4:** Run `python -m unittest discover -s tests`; existing tests pass.

### Task 2: Independent cross-check per mode

**Files:**
- Modify: `bjt/independent.py`

**Interfaces:**
- Produces: `solve_fixed_independent(vcc, rb, rc, beta, vbe)`, `solve_emitter_independent(vcc, rb, re, rc, beta, vbe)`, `solve_independent(mode, values)`.
- Consumes: existing `solve_bias_independent` (divider), `compare_results`, `classify_region`.

- [ ] **Step 1:** Add bisection on the KCL/KVL residual for Fixed and Emitter (different formulation from the closed-form expression).
- [ ] **Step 2:** Add `solve_independent` dispatcher mirroring `analyze_mode`.
- [ ] **Step 3:** Run the test suite.

### Task 3: Routes — mode selection, per-mode parsing, unit errors

**Files:**
- Modify: `bjt/routes.py`

**Interfaces:**
- Produces (template context): `mode`, `mode_label`, `mode_options`, `labels` (mode fields only), `unit_options`, `values`, `units`, `circuit`, `errors`, `result`, `independent`, `comparison`.
- Consumes: `parse_mode_inputs`, `analyze_mode`, `solve_independent`, `compare_results`.

- [ ] **Step 1:** GET `/` accepts `?mode=`; valid mode renders that form with per-mode defaults; unknown mode renders Divider form plus a mode error.
- [ ] **Step 2:** POST `/calculate` reads `mode` (absent → `divider` to keep Lab 02 forms working); unknown mode → `errors["mode"]`, no calculation.
- [ ] **Step 3:** Convert only the mode's fields to SI; `_scale_for` returns `None` for unknown units so the route reports `invalid unit`.
- [ ] **Step 4:** Raise `errors["_form"]` for dispatcher `ValueError`; keep results empty when errors exist.
- [ ] **Step 5:** Run the test suite (existing route tests post Divider data).

### Task 4: Template and styles — tabs, per-mode form, three schematics, mode-labelled results

**Files:**
- Modify: `bjt/templates/index.html`, `bjt/static/style.css`

- [ ] **Step 1:** Add mode tabs (`/?mode=divider|fixed|emitter`) with `aria-current`, hidden `mode` input in the form, and mode-specific field loop.
- [ ] **Step 2:** Add Fixed and Emitter schematics next to the existing Divider one; label values from `circuit`.
- [ ] **Step 3:** Results heading shows the selected mode; empty state names the mode; error text for `errors.mode`.
- [ ] **Step 4:** Retitle the page/footer as Lab 03; add minimal CSS for tabs.
- [ ] **Step 5:** Run the test suite, start the app, open it in the browser and check all three modes render.

### Task 5: Browser acceptance A1–A5 + deliverables

**Files:**
- Create: `docs/validation.md`, evidence image under `docs/evidence/`
- Modify: `README.md`

- [ ] **Step 1:** Compute the independent reference values from the worksheet equations (already done: A1 1.2299 mA / 8.052 V; A2 1.1300 mA / 9.514 V; A3 1.0263 mA / 8.705 V; A4 0.9401 mA / 8.033 V).
- [ ] **Step 2:** Run A1–A5 in OpenCode Browser: select mode, fill fields, submit, read the rendered values, judge PASS/FAIL with tolerance (IC ±0.01 mA, VCE ±0.02 V).
- [ ] **Step 3:** Record the case table in `docs/validation.md` with method "OpenCode Browser" and a screenshot as evidence.
- [ ] **Step 4:** Update README (three modes, how to run, validation pointer).
- [ ] **Step 5:** Run the full suite, commit.
