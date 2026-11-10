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
