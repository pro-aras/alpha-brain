# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:34 +0400 (re-stamped from `date`: the first stamp, «05:14», was typed — #50) — A4-LADDER-2-PREREG ADDENDUM §7(2) item 2: check.py's glances line is gated on
# the genome's OWN `; drop confirmed` clause. The three cases the brief names (declared+equal, declared+unequal, undeclared) on fixture roots,
# plus «not recorded» (an older body), an unknown genome, the unit.env fallback, and the six ladder-2 genomes themselves (only A4L2-ALL declares).
"""tools/lives/check.py: MISMATCH only when the genome declares `; drop confirmed` AND dropped != confirmed."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TREE = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("lives_check_drop", TREE / "tools" / "lives" / "check.py")
check = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(check)

ALL = TREE / "genome" / "ladder2" / "A4L2-ALL.genome"       # declares SURPRISE ...; drop confirmed
FLOOR = TREE / "genome" / "ladder2" / "A4L2-FLOOR.genome"   # does not


def _root(tmp: Path, name: str, status: dict, genome: "Path | None" = None, via_unit_env: bool = False) -> Path:
    root = tmp / name
    for d in ("journal", "tape", "exam"):
        (root / d).mkdir(parents=True)
    (root / "STATUS.json").write_text(json.dumps(status))
    if genome is not None:
        if via_unit_env:
            (root / "code").mkdir()
            g = root / "code" / genome.name; g.write_text(genome.read_text())
            (root / "unit.env").write_text(f"GENOME={g}\nPLANT_AFTER=15000\n")
        else:
            (root / "GENOME.genome").write_text(genome.read_text())
    return root


def _glances_line(root: Path) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        check.main(["--root", str(root)])
    lines = [l for l in buf.getvalue().splitlines() if l.startswith("[check] glances")]
    assert len(lines) == 1, buf.getvalue()[-600:]
    return lines[0]


class DropClauseGatesTheComparison(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(); self.tmp = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def test_declared_and_equal_reads_ok(self):
        line = _glances_line(_root(self.tmp, "eq", {"glances_confirmed": 6125, "glances_surprised": 9000, "glances_dropped": 6125}, ALL))
        self.assertIn("OK: dropped == confirmed", line); self.assertNotIn("MISMATCH", line)

    def test_declared_and_unequal_reads_mismatch(self):
        line = _glances_line(_root(self.tmp, "ne", {"glances_confirmed": 6125, "glances_dropped": 6000}, ALL))
        self.assertIn("MISMATCH: dropped 6000 != confirmed 6125", line)

    def test_undeclared_reads_not_declared_never_mismatch(self):
        line = _glances_line(_root(self.tmp, "und", {"glances_confirmed": 20805, "glances_dropped": 0}, FLOOR))
        self.assertNotIn("MISMATCH", line)
        self.assertIn("not declared (no `; drop confirmed` in the genome; dropped 0 is the ordinary reading)", line)
        self.assertNotIn("UNEXPECTED", line)

    def test_undeclared_with_a_drop_is_flagged(self):
        line = _glances_line(_root(self.tmp, "und-drop", {"glances_confirmed": 10, "glances_dropped": 3}, FLOOR))
        self.assertNotIn("MISMATCH", line); self.assertIn("UNEXPECTED: dropped 3", line)

    def test_an_older_body_reads_not_recorded(self):
        line = _glances_line(_root(self.tmp, "old", {"glances_confirmed": 10}, ALL))
        self.assertIn("not recorded", line); self.assertNotIn("MISMATCH", line); self.assertNotIn("OK:", line)

    def test_an_unknown_genome_is_never_compared(self):
        line = _glances_line(_root(self.tmp, "nog", {"glances_confirmed": 10, "glances_dropped": 0}, None))
        self.assertIn("genome unknown", line); self.assertNotIn("MISMATCH", line)
        self.assertIsNone(check.drop_declared(self.tmp / "nog"))

    def test_the_unit_env_names_the_genome_when_no_copy_sits_at_the_root(self):
        root = _root(self.tmp, "env", {"glances_confirmed": 7, "glances_dropped": 5}, ALL, via_unit_env=True)
        self.assertFalse((root / "GENOME.genome").exists())
        self.assertIs(check.drop_declared(root), True)
        self.assertIn("MISMATCH: dropped 5 != confirmed 7", _glances_line(root))

    def test_a_genome_that_refuses_to_parse_is_unknown(self):
        root = _root(self.tmp, "bad", {"glances_confirmed": 7, "glances_dropped": 0}, None)
        (root / "GENOME.genome").write_text("not a genome\n")
        self.assertIsNone(check.drop_declared(root))
        self.assertNotIn("MISMATCH", _glances_line(root))


class TheLadderTwoGenomes(unittest.TestCase):
    """The PREREG's own statement (ADDENDUM §7(2) item 2): only R5 ALL declares `; drop confirmed`."""
    def test_only_all_declares_the_drop(self):
        got = {}
        with tempfile.TemporaryDirectory() as td:
            for g in sorted((TREE / "genome" / "ladder2").glob("*.genome")):
                r = Path(td) / g.stem; r.mkdir(); (r / "GENOME.genome").write_text(g.read_text())
                got[g.stem] = check.drop_declared(r)
        self.assertEqual(got, {"A4L2-ACT": False, "A4L2-ALL": True, "A4L2-COST": False, "A4L2-FLOOR": False, "A4L2-LINE": False, "A4L2-NURSERY": False})


if __name__ == "__main__":
    unittest.main()
