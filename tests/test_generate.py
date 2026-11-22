"""The generators' contracts: what a generated circuit holds, by its parameters."""
import unittest
from collections import Counter
from pathlib import Path

from circref import generate
from circref.entry import Case

PULSE = {"v1": 0.0, "v2": 1.0, "delay": 1e-10, "rise": 2e-11, "fall": 2e-11, "width": 1e-9, "period": 2e-9}
TRAN = {"step": 1e-11, "stop": 1e-8}
CHAINS = {"stages": 3, "vdd": 1.0, "dc": 0.0, "nmos": {"subckt": "n", "w": 1e-6}, "pmos": {"subckt": "p", "w": 2e-6},
          "models": {"ngspice": [".include models"]}, "pulse": PULSE, "tran": TRAN}


def case(generator: dict) -> Case:
    return Case(Path("."), {"id": "t", "title": "t", "generator": generator})


class Chains(unittest.TestCase):
    def test_transistors_and_blocks(self):
        _, elements, probes = generate.circuit(case(CHAINS), 4)
        kinds = Counter(e[0] for e in elements)
        self.assertEqual(kinds, {"v": 3, "x": 2 * 3 * 4})
        gates = Counter(e[2][1] for e in elements if e[0] == "x" and e[1].endswith("_1"))
        self.assertEqual(gates, {"in": 4, "inb": 4})              # every second chain on the complement
        self.assertEqual(len(probes), 3)

    def test_net_totals_do_not_depend_on_ratio(self):
        wire = {"r": 200.0, "c": 2e-15, "coupling": 3e-15}
        for ratio in (1, 4, 25):
            _, elements, _ = generate.circuit(case(CHAINS | {"wire": wire | {"ratio": ratio}}), 2)
            net = lambda kind, prefix: sum(e[3] for e in elements if e[0] == kind and e[1].startswith(prefix)
                                           and e[1].split("_")[1] == "1")
            self.assertAlmostEqual(net("r", "r1_"), wire["r"])
            self.assertAlmostEqual(net("c", "c1_") / wire["c"], 1)
            self.assertAlmostEqual(net("c", "cc1_") / wire["coupling"], 1)
            nodes = {n for e in elements if e[0] == "c" for n in e[2]} - {"0"}
            self.assertEqual(len(nodes), ratio * 2 * 3 * 2)       # ratio RC nodes per transistor


class Network(unittest.TestCase):
    def test_a_diode_per_node_on_the_same_graph(self):
        g = {"network": "mesh", "r": 1e3, "c": 1e-15, "source_r": 100.0, "dc": 1.0, "pulse": PULSE, "tran": TRAN}
        _, linear, _ = generate.circuit(case(g), 5)
        _, diodes, _ = generate.circuit(case(g | {"diode": {"is": 1e-14}}), 5)
        self.assertEqual([e for e in diodes if e[0] != "d"], linear)
        self.assertEqual(sorted(e[2][0] for e in diodes if e[0] == "d"), sorted(e[2][0] for e in linear if e[0] == "c"))


if __name__ == "__main__":
    unittest.main()
