"""The comparison's contract: a run is judged on its own points against a reference that
converged runs agree on; a run off the others is set aside, two that disagree give none."""
import unittest

import numpy as np

from circref.compare import C, error, reference


def sine(points: int, amplitude: float = 1.0, shift: float = 0.0):
    t = np.linspace(0, 1e-3, points)
    return t, {"v(out)": amplitude * np.sin(2 * np.pi * 5e3 * t) + shift}


class Compare(unittest.TestCase):
    def test_own_points(self):
        # a run with few, exact points has no error against a dense reference
        e, sig = error(sine(41), sine(20001))
        self.assertLess(e, 1e-7)
        self.assertEqual(sig, "v(out)")

    def test_error_relative_to_peak(self):
        e, _ = error(sine(201, shift=1e-3), sine(20001))
        self.assertAlmostEqual(e, 1e-3 / (1 + C["floor"]["v"]), places=9)

    def test_outlier_set_aside(self):
        runs = {}
        for s, shift in (("a", 0.0), ("b", 1e-7), ("c", 1e-2)):
            runs[(s, "fine")] = sine(2001, shift=shift)
            runs[(s, "reference")] = sine(20001, shift=shift)
        info, ref = reference(runs)
        self.assertEqual(info["status"], "agreed")
        self.assertEqual(info["outliers"], ["c"])
        self.assertLess(info["error"], 1e-6)

    def test_two_disagree(self):
        runs = {(s, lv): sine(2001, shift=shift) for s, shift in (("a", 0.0), ("b", 1e-2))
                for lv in ("fine", "reference")}
        info, ref = reference(runs)
        self.assertEqual(info["status"], "disagree")
        self.assertIsNone(ref)

    def test_not_converged(self):
        runs = {("a", "fine"): sine(2001, shift=1e-2), ("a", "reference"): sine(20001)}
        self.assertEqual(reference(runs)[0]["status"], "none")


if __name__ == "__main__":
    unittest.main()
