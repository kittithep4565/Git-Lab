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
