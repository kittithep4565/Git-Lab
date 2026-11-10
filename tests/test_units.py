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
