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
        self.assertIn('value="100"', html)
        self.assertIn('name="r1_unit"', html)
        self.assertIn('action="/calculate"', html)
        self.assertIn('method="post"', html)


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

