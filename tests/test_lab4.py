import re
import unittest

from bjt import create_app
from bjt.engineering import MODE_LABELS
from bjt.sim_params import (
    DEFAULTS,
    DEFAULT_UNITS,
    FIELDS,
    parse_sim_inputs,
)
from bjt.spice_engine import (
    SpiceEngineError,
    _parse_ac,
    _parse_op,
    build_netlist,
)


MODEL = ".model QNPN NPN(IS=1e-14 BF=100)"


def _form(**changes):
    data = {"analysis": changes.pop("analysis", "dc")}
    for field in FIELDS:
        data[field] = changes.get(field, DEFAULTS[field])
        data[f"{field}_unit"] = changes.get(f"{field}_unit", DEFAULT_UNITS[field])
    return data


class TestLab4Inputs(unittest.TestCase):
    def test_baseline_matches_handout_fixture(self):
        values, errors = parse_sim_inputs("dc", DEFAULTS, DEFAULT_UNITS)
        self.assertEqual(errors, {})
        self.assertAlmostEqual(values["vcc"], 12.0)
        self.assertAlmostEqual(values["r1"], 100_000.0)
        self.assertAlmostEqual(values["r2"], 22_000.0)
        self.assertAlmostEqual(values["rc"], 2_200.0)
        self.assertAlmostEqual(values["re"], 1_000.0)
        self.assertAlmostEqual(values["rl"], 10_000.0)
        self.assertAlmostEqual(values["cin"], 10e-6)
        self.assertAlmostEqual(values["cout"], 10e-6)
        self.assertAlmostEqual(values["amp"], 0.01)
        self.assertAlmostEqual(values["freq"], 1_000.0)

    def test_invalid_re_and_unit_are_rejected(self):
        texts = dict(DEFAULTS, re="0", cin="abc")
        units = dict(DEFAULT_UNITS, cin="banana")
        _, errors = parse_sim_inputs("dc", texts, units)
        self.assertIn("re", errors)
        self.assertIn("cin", errors)
        self.assertIn("invalid unit", errors["cin"])

    def test_source_limits_are_enforced(self):
        _, errors = parse_sim_inputs(
            "tran", dict(DEFAULTS, amp="2"), dict(DEFAULT_UNITS, amp="V")
        )
        self.assertIn("amp", errors)
        _, errors = parse_sim_inputs(
            "tran", dict(DEFAULTS, freq="5"), dict(DEFAULT_UNITS, freq="Hz")
        )
        self.assertIn("freq", errors)


class TestNetlist(unittest.TestCase):
    def test_dc_netlist_uses_only_the_reference_circuit(self):
        values, errors = parse_sim_inputs("dc", DEFAULTS, DEFAULT_UNITS)
        self.assertEqual(errors, {})
        netlist = build_netlist(values, "dc", MODEL, "QNPN")
        self.assertIn("VCC vcc 0 DC 12", netlist)
        self.assertIn("R1 vcc base 100000", netlist)
        self.assertIn("RL out 0 10000", netlist)
        self.assertIn("CIN in base 1e-05", netlist)
        self.assertIn("SIN(0 0.01 1000)", netlist)
        self.assertIn(".op", netlist)
        self.assertNotIn("C_E", netlist)
        self.assertNotIn("CE emitter", netlist)
        self.assertTrue(netlist.rstrip().endswith(".end"))

    def test_ac_and_tran_have_distinct_directives(self):
        values, _ = parse_sim_inputs("ac", DEFAULTS, DEFAULT_UNITS)
        ac = build_netlist(values, "ac", MODEL, "QNPN")
        tran = build_netlist(values, "tran", MODEL, "QNPN")
        self.assertIn(".ac dec", ac)
        self.assertIn("vdb(in)", ac)
        self.assertIn("vp(out)", ac)
        self.assertNotIn(".tran", ac)
        self.assertIn(".tran", tran)
        self.assertIn("v(in) v(out)", tran)
        self.assertNotIn(".ac", tran)


class TestParsers(unittest.TestCase):
    def test_op_reads_index_table(self):
        log = """
Index   v(base)         v(emitter)      v(collector)    v(in)           v(out)
0       1.950000e+00    1.290000e+00    9.190000e+00    0.000000e+00    0.000000e+00
"""
        values, _ = parse_sim_inputs("dc", DEFAULTS, DEFAULT_UNITS)
        parsed = _parse_op(log, values)
        self.assertAlmostEqual(parsed["summary"]["vb"], 1.95)
        self.assertAlmostEqual(parsed["summary"]["vce"], 9.19 - 1.29)
        self.assertAlmostEqual(parsed["summary"]["ic"], (12 - 9.19) / 2200)

    def test_ac_merges_separate_vin_and_vout_tables(self):
        rows = "".join(
            f"{i}\t{100 * 2 ** i:.6e}\t0.000000e+00\t0.000000e+00\t\n"
            for i in range(6)
        )
        out_rows = "".join(
            f"{i}\t{100 * 2 ** i:.6e}\t{-12 + i}.000000e+00\t{-180 + i}.000000e+00\t\n"
            for i in range(6)
        )
        log = (
            "Index   frequency       vdb(in)         vp(in)\n"
            + rows
            + "Index   frequency       vdb(out)        vp(out)\n"
            + out_rows
        )
        parsed = _parse_ac(log)
        self.assertEqual(len(parsed["gain_points"]), 6)
        self.assertAlmostEqual(parsed["gain_points"][0][1], -12.0)
        self.assertAlmostEqual(parsed["gain_points"][-1][1], -7.0)
        self.assertAlmostEqual(parsed["summary"]["peak_gain_db"], -7.0)

    def test_missing_ac_table_raises_engine_error(self):
        with self.assertRaises(SpiceEngineError):
            _parse_ac("No. of Data Rows : 0\n")


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_lab3_modes_still_render(self):
        for mode in ("divider", "fixed", "emitter"):
            response = self.client.get(f"/?mode={mode}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(MODE_LABELS[mode], response.get_data(as_text=True))

    def test_sim_form_renders_documented_defaults(self):
        html = self.client.get("/").get_data(as_text=True)
        for field, expected in (
            ("vcc", "12.0"),
            ("r1", "100"),
            ("re", "1.0"),
            ("amp", "10"),
            ("freq", "1"),
            ("beta", "100"),
            ("vbe", "0.70"),
        ):
            match = re.search(
                r'id="sim-' + field + r'"[^>]*\s+value="([^"]*)"', html, re.S
            )
            self.assertIsNotNone(match, field)
            self.assertEqual(match.group(1), expected, field)

    def test_invalid_re_shows_error_without_success_or_plot(self):
        response = self.client.post("/simulate", data=_form(re="0"))
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("must be greater than zero", html)
        self.assertNotIn("sim-status ok", html)
        self.assertNotIn("<polyline", html)


if __name__ == "__main__":
    unittest.main()
