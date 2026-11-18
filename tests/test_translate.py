"""Statement forms of the SPICE translation, one per rule of circref/translate.py."""
import unittest
from pathlib import Path

from circref.translate import Untranslatable, translate_text


def tr(body: str, source: str, target: str) -> str:
    deck = Path("deck.cir")
    return translate_text({deck: ("title\n" + body, True)}, source, target)[deck][len("title\n"):]


class Untouched(unittest.TestCase):
    def test_byte_for_byte(self):
        body = ("R1 a  b 1k ; load\n* comment\n.subckt amp in out\n+ params: g=2\n"
                "E1 out 0 in 0 {g}\n.ends\n")
        self.assertEqual(tr(body, "xyce", "ngspice"), body)
        self.assertEqual(tr(body, "ngspice", "xyce"), body)

    def test_analysis_and_output_lines_dropped(self):
        self.assertEqual(tr("R1 1 0 1\n.tran 1n 1u\n.print tran v(1)\n.options timeint reltol=1e-3\n",
                            "xyce", "ngspice"), "R1 1 0 1\n")


class Options(unittest.TestCase):
    def test_circuit_options_kept_solver_options_dropped(self):
        self.assertEqual(tr(".options parser scale=1u model_binning=true\n.options nonlin maxstep=50\n",
                            "xyce", "ngspice"), ".options scale=1u\n")
        self.assertEqual(tr(".options klu scale=1u\n", "ngspice", "xyce"),
                         ".options parser scale=1u\n")

    def test_no_equivalent(self):
        with self.assertRaises(Untranslatable):
            tr(".options rshunt=1e12\n", "ngspice", "xyce")


class XyceToNgspice(unittest.TestCase):
    def test_bare_parameter_in_braces(self):
        out = tr(".param rv=2k wv=1u\n.model nm nmos level=1 vto=rv\nR1 rv 0 rv\n"
                 "M1 d g 0 0 nm w=wv l=1u\n", "xyce", "ngspice")
        self.assertIn("R1 rv 0 {rv}", out)                  # the node keeps its name
        self.assertIn("vto={rv}", out)
        self.assertIn("w={wv}", out)

    def test_mutual_inductor_pairs(self):
        out = tr("K1 L1 L2 L3 0.9\n", "xyce", "ngspice")
        self.assertEqual(out.split("\n")[:3], ["K1 L1 L2 0.9", "K1_1 L1 L3 0.9", "K1_2 L2 L3 0.9"])

    def test_bsim3_level_and_version(self):
        out = tr(".model n nmos (level=9 tox=4n)\n", "xyce", "ngspice")
        self.assertEqual(out, ".model n nmos (level=8 tox=4n version=3.2.2)\n")

    def test_bsim4_version_of_xyce(self):
        out = tr(".model n nmos level=54 version=4.7\n", "xyce", "ngspice")
        self.assertIn("version=4.7.0", out)

    def test_expression_functions(self):
        out = tr(".param a={log(x)+if(x>1, 2, 3)+pwr(x, 2)}\n", "xyce", "ngspice")
        self.assertEqual(out, ".param a={log10(x)+((x>1) ? (2) : (3))+pow(x, 2)}\n")

    def test_random_functions_are_their_mean(self):
        self.assertEqual(tr(".param a={agauss(1, 0.1, 3)}\n", "xyce", "ngspice"), ".param a={1}\n")

    def test_table_holds_its_ends(self):
        out = tr("B1 1 0 V={table(v(2), 1, 10, 0, 0)}\n", "xyce", "ngspice")
        self.assertIn("pwl(v(2), 0, 0, 1, 10)", out)
        self.assertIn("((v(2)) < (0) ? (0) : (((v(2)) > (1) ? (10)", out)

    def test_passive_model_multiplier(self):
        out = tr("R1 1 0 rm 1k\nC1 1 0 cm c=2p\n.model rm R R=2 TC1=0\n.model cm C (C=3)\n",
                 "xyce", "ngspice")
        self.assertIn("R1 1 0 rm {(1k)*(2)}", out)
        self.assertIn("C1 1 0 cm c={(2p)*(3)}", out)
        self.assertIn(".model rm R TC1=0", out)

    def test_tc_vector_and_stray_ends(self):
        self.assertEqual(tr("R1 1 0 50 tc=1m,2u\n.ends\n", "xyce", "ngspice"),
                         "R1 1 0 50 tc1=1m tc2=2u\n")

    def test_global_param(self):
        self.assertEqual(tr(".global_param a=1\n", "xyce", "ngspice"), ".param a=1\n")

    def test_gnd_is_a_node_in_xyce(self):
        self.assertEqual(tr("R1 gnd 0 1\n", "xyce", "ngspice"), "R1 gnd_ 0 1\n")
        out = tr(".preprocess replaceground true\nR1 gnd 0 1\n", "xyce", "ngspice")
        self.assertEqual(out, "R1 0 0 1\n")

    def test_undeclared_subcircuit_parameter(self):
        out = tr(".param w=2\n.subckt s a b\nR1 a b {w*l}\n.ends\nX1 1 0 s w=1 l=3\n",
                 "xyce", "ngspice")
        self.assertIn(".subckt s a b l=0 w={w}\n", out)

    def test_dc_value_of_a_transient_source(self):
        deck = Path("deck.cir")
        run = lambda analyses: translate_text({deck: ("t\nV1 1 0 sin(1 1 1k)\n", True)},
                                              "xyce", "ngspice", None, analyses)[deck]
        self.assertEqual(run({"tran"}), "t\nV1 1 0 sin(1 1 1k)\n")
        self.assertEqual(run({"op"}), "t\nV1 1 0 dc 0 sin(1 1 1k)\n")
        with self.assertRaises(Untranslatable):
            run({"op", "tran"})

    def test_global_node(self):
        out = tr("VDD $G_VDD 0 5\n", "xyce", "ngspice")
        self.assertEqual(out, ".global G_VDD\nVDD G_VDD 0 5\n")

    def test_dcvolt_pairs(self):
        self.assertEqual(tr(".dcvolt 1 1.0 2 {v2}\n", "xyce", "ngspice"),
                         ".ic v(1)=1.0 v(2)={v2}\n")

    def test_variables(self):
        self.assertEqual(tr("B1 1 0 V={sin(2*pi*freq)}\n", "xyce", "ngspice"),
                         "B1 1 0 V={sin(2*3.141592653589793*hertz)}\n")
        with self.assertRaises(Untranslatable):
            tr("R1 1 0 {1+time}\n", "xyce", "ngspice")

    def test_hierarchical_node(self):
        self.assertEqual(tr(".ic v(x1:n1)=1\n", "xyce", "ngspice"), ".ic v(x1.n1)=1\n")

    def test_untranslatable(self):
        for body, reason in [("S1 1 0 2 0 sw\n", "switch"),
                             ("K1 L1 L2 1 c\n.model c core\n", "core"),
                             (".model q npn level=11\n", "VBIC 1.3"),
                             (".param a={2^3}\n", "XOR")]:
            with self.assertRaises(Untranslatable) as e:
                tr(body, "xyce", "ngspice")
            self.assertIn(reason, str(e.exception))


class NgspiceToXyce(unittest.TestCase):
    def test_source_assignments(self):
        self.assertEqual(tr("vs a 0 dc=0 sin 0 50 100k\n", "ngspice", "xyce"),
                         "vs a 0 dc 0 sin 0 50 100k\n")

    def test_comments(self):
        self.assertEqual(tr("R1 1 0 1k $ load\n$ note\n", "ngspice", "xyce"),
                         "R1 1 0 1k ; load\n*$ note\n")

    def test_expressions(self):
        out = tr("B1 1 0 V=log(v(2))^2 + pwr(v(2), 3)\n.param p={pwr(-2, 2)}\n", "ngspice", "xyce")
        self.assertIn("V={ln(v(2))**2 + pwrs(v(2), 3)}", out)
        self.assertIn(".param p={pow(abs(-2), 2)}", out)

    def test_value_form(self):
        self.assertEqual(tr("E1 1 0 vol='v(2)*2'\n", "ngspice", "xyce"), "E1 1 0 value={v(2)*2}\n")

    def test_indented_line_is_a_comment_in_xyce(self):
        self.assertEqual(tr("  R1 1 0 1k\n", "ngspice", "xyce"), "R1 1 0 1k\n")
        self.assertEqual(tr("R1 1 0 1k\n  R2 1 0 1k\n", "xyce", "ngspice"), "R1 1 0 1k\n*R2 1 0 1k\n")

    def test_ltra_flags(self):
        self.assertEqual(tr(".model ll ltra r=1 len=1 steplimit nocontrol\n", "ngspice", "xyce"),
                         ".model ll ltra r=1 len=1 steplimit=1\n")

    def test_params_keyword(self):
        self.assertEqual(tr(".subckt inv a b w=1u\n.ends\nx1 1 2 inv w=2u\n", "ngspice", "xyce"),
                         ".subckt inv a b params: w=1u\n.ends\nx1 1 2 inv params: w=2u\n")

    def test_gnd_is_ground(self):
        self.assertEqual(tr("R1 gnd 1 1\n", "ngspice", "xyce"), "R1 0 1 1\n")

    def test_bsim4_default_version(self):
        self.assertIn("version=4.8.3", tr(".model n nmos level=14\n", "ngspice", "xyce"))
        with self.assertRaises(Untranslatable):
            tr(".model n nmos level=8\n", "ngspice", "xyce")    # BSIM3 3.3.0


if __name__ == "__main__":
    unittest.main()
