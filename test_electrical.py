import unittest
from electrical import analyze_dc


class TestDCAnalyzer(unittest.TestCase):
    def test_known_values(self):
        result = analyze_dc(12, 6)
        self.assertAlmostEqual(result["current_a"], 2.0)
        self.assertAlmostEqual(result["power_w"], 24.0)

    def test_zero_voltage(self):
        result = analyze_dc(0, 10)
        self.assertAlmostEqual(result["current_a"], 0.0)
        self.assertAlmostEqual(result["power_w"], 0.0)

    def test_zero_resistance_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_dc(12, 0)

    def test_negative_resistance_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_dc(12, -5)


if __name__ == "__main__":
    unittest.main()

    
