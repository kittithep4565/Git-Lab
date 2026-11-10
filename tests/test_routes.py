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
