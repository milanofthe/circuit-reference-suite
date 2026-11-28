import unittest

from circref.query import compile_filter, index

ROW = dict(index()[0]) | {"name": "x_rc_1", "devices": 120, "m": 4, "nodes": None,
                          "linear": False, "family": "opamp", "analyses": ("op", "tran")}


class Filter(unittest.TestCase):
    def test_comparisons_and_logic(self):
        self.assertTrue(compile_filter("m >= 1 and 100 <= devices <= 1000")(ROW))
        self.assertFalse(compile_filter("100 <= devices <= 110")(ROW))
        self.assertTrue(compile_filter("not linear and ('tran' in analyses or m > 9)")(ROW))
        self.assertTrue(compile_filter("family in ('opamp', 'ldo')")(ROW))
        self.assertTrue(compile_filter("glob(name, 'x_rc*')")(ROW))

    def test_empty_value_compares_false(self):
        self.assertFalse(compile_filter("nodes < 10")(ROW))
        self.assertFalse(compile_filter("nodes >= 10")(ROW))

    def test_outside_the_grammar(self):
        for expr in ("__import__('os')", "devices.bit_length()", "nosuch > 1", "devices +",
                     "[d for d in analyses]", "lambda: 1"):
            with self.assertRaises(ValueError, msg=expr):
                compile_filter(expr)



class Study(unittest.TestCase):
    def test_committed_studies_load(self):
        from circref.cli import load_study
        from circref.entry import ROOT
        for path in (ROOT / "studies").glob("*.toml"):
            self.assertIn("select", load_study(path))

    def test_unknown_key_and_bad_filter(self):
        import tempfile
        from pathlib import Path
        from circref.cli import load_study
        from circref.query import FilterError
        for text in ('title = "t"\nselect = "m >= 1"\n[run]\nsimulator = ["x"]\n',
                     'title = "t"\nselect = "nosuch > 1"\n'):
            with tempfile.TemporaryDirectory() as d:
                f = Path(d) / "s.toml"
                f.write_text(text, encoding="utf-8")
                with self.assertRaises(FilterError):
                    load_study(f)


if __name__ == "__main__":
    unittest.main()
