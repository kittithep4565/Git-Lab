import unittest

from bjt import create_app
from bjt.engineering import FIELDS


from unittest.mock import patch


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
