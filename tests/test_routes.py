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
