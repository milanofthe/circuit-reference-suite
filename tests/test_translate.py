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


class NgspiceToWrspice(unittest.TestCase):
    def test_behavioral_source(self):
        """B is A in WRspice; its device expressions have no ternary operator, min or max."""
        self.assertEqual(tr("B1 2 0 V=v(1) > 0 ? 2*v(1) : min(v(1), 1)\n", "ngspice", "wrspice"),
                         "aB1 2 0 V=(((v(1) > 0) != 0)*(2*v(1)) + ((v(1) > 0) == 0)*"
                         "((((v(1))+(1)-abs((v(1))-(1)))/2)))\n")
        self.assertEqual(tr("E1 3 0 vol={u(v(2))}\n", "ngspice", "wrspice"),
                         "E1 3 0 function=(0.5*(sgn(v(2))+1))\n")

    def test_expressions_in_quotes(self):
        out = tr(".param a={pwr(-2, 3)} b = 2 * a\n.func f(x) {x*2}\nR1 1 0 {a*f(b)}\n",
                 "ngspice", "wrspice")
        self.assertEqual(out, ".param a='(abs(-2)^(3))' b = '2 * a'\n.param f(x) = 'x*2'\n"
                              "R1 1 0 'a*f(b)'\n")

    def test_subcircuit_scope_and_names(self):
        out = tr(".subckt s n1 n2 params: w=1\nR1 n1 n2 {w}\n.ends\nx1 1 gnd s w=3\n"
                 ".ic v(x1.x2.n1)=1\n", "ngspice", "wrspice")
        self.assertEqual(out, ".options parhier=local\n.subckt s n1 n2 w=1\nR1 n1 n2 'w'\n.ends\n"
                              "x1 1 0 s w=3\n.ic v(n1.x2.x1)=1\n")

    def test_comments(self):
        self.assertEqual(tr("R1 1 0 1k;load\n*#### note\n", "ngspice", "wrspice"),
                         "R1 1 0 1k $ load\n* #### note\n")

    def test_bsim4_version_is_a_level(self):
        self.assertEqual(tr(".model n nmos level=14\n", "ngspice", "wrspice"), ".model n nmos level=18\n")
        self.assertEqual(tr(".model n nmos level=54 version=4.7\n", "ngspice", "wrspice"),
                         ".model n nmos level=16 version=4.7\n")
        with self.assertRaises(Untranslatable):
            tr(".model n nmos level=14 version=4.5\n", "ngspice", "wrspice")

    def test_source_arguments(self):
        self.assertEqual(tr("V1 1 0 sin(0, 1, 1k)\nV2 2 0 pwl(0 0 1n 1) r=0 td=1n\n",
                            "ngspice", "wrspice"),
                         "V1 1 0 sin(0 1 1k)\nV2 2 0 pwl(0 0 1n 1 r=0 td=1n)\n")

    def test_untranslatable(self):
        for body, reason in [(".model q npn\nQ1 1 2 0 q m=2\n", "multiplier"),
                             ("X1 1 2 s m=2\n", "multiplier"),
                             ("B1 1 0 V=floor(v(2))\n", "floor"),
                             (".options scale=1u\n", "scale"),
                             (".model d1 d level=3\n", "diode")]:
            with self.assertRaises(Untranslatable) as e:
                tr(body, "ngspice", "wrspice")
            self.assertIn(reason, str(e.exception))


class NgspiceToSpicesharp(unittest.TestCase):
    def test_element_forms(self):
        out = tr("V1 1 0 dc=0 ac=1 sin(0 1 1k)\nE1 3 0 vol='temper*2'\n.model q npn level=1 bf=100\n"
                 "Q1 1 2 0 q\nB1 2 0 V=pwr(v(1), 2)\n", "ngspice", "spicesharp")
        self.assertEqual(out, "V1 1 0 dc 0 ac 1 sin(0 1 1k)\nE1 3 0 value={temp*2}\n"
                              ".model q npn bf=100\nQ1 1 2 0 0 q\nB1 2 0 V={pwrs(v(1), 2)}\n")

    def test_resistor_coefficients_and_comment_lines(self):
        self.assertEqual(tr("R1 1 0 1k tc1=1m tc2=2u\n.model q npn\n+ bf=100\n* note\n+ is=1e-15\n",
                            "ngspice", "spicesharp"),
                         "R1 1 0 1k tc=1m,2u\n.model q npn\n+ bf=100\n+ is=1e-15\n")

    def test_scale_letters(self):
        """a is atto in ngspice, a unit in Xyce and SpiceSharp; x is mega in SpiceSharp."""
        self.assertEqual(tr("R1 1 0 5x\nC1 1 0 2a\n", "ngspice", "spicesharp"), "R1 1 0 5.0\nC1 1 0 2e-18\n")
        self.assertEqual(tr("I1 0 1 PWL(0 0 1 5A)\n", "xyce", "ngspice"), "I1 0 1 PWL(0 0 1 5.0)\n")

    def test_names_in_lower_case(self):
        self.assertEqual(tr(".SUBCKT S a b\n.ENDS S\n.LIB 'models.lib' TT\n", "ngspice", "spicesharp"),
                         ".subckt S a b\n.ends\n.lib 'models.lib' tt\n")

    def test_untranslatable(self):
        for body, reason in [(".subckt s a b\nL1 a 0 1u\nL2 b 0 1u\nK1 L1 L2 0.5\n.ends\n", "mutual"),
                             (".model n nmos level=14\n", "bsim4"),
                             ("V1 1 0 exp(0 1 1n 1n)\n", "exp"),
                             ("V1 1 0 pulse(0 1 0 0 0 1u 2u)\n", "zero rise"),
                             ("V1 1 0 pwl(0 0 1n 1) r=0\n", "pwl"),
                             (".subckt s a b w=1\n.ends\nX1 1 2 s l={w*2}\n", "names a parameter"),
                             ("Z1 1 2 0 mz\n", "MESFET")]:
            with self.assertRaises(Untranslatable) as e:
                tr(body, "ngspice", "spicesharp")
            self.assertIn(reason, str(e.exception))


class XyceToWrspice(unittest.TestCase):
    def test_through_ngspice(self):
        """Xyce to WRspice is Xyce to ngspice, then ngspice to WRspice."""
        out = tr(".param a={log(4)}\nB1 1 0 V={if(v(2) > 1, 2, 0)}\n", "xyce", "wrspice")
        self.assertEqual(out, ".param a='log10(4)'\naB1 1 0 V=(((((v(2) > 1)) != 0)*((2)) + "
                              "(((v(2) > 1)) == 0)*((0))))\n")


if __name__ == "__main__":
    unittest.main()
