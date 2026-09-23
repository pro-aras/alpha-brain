# tests/creature/test_a42_b1.py — A42-B1 (docs/ALPHA4-2-PREREG.md §2 M3/M4/M5, §2.5, §2.6; the report docs/briefs/A42-B1-REPORT.md).
# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:1x +0400 — written RED first on a50b0f3 (+ the WIP report), then the code.
#
# M3 one hash per canvas: `Organism.row_hash()` is called ONCE per worded canvas (today twice: the canvas row's dict and
#   `_coarse_row` hash the same state one statement apart — identical in 9,331 of 9,331 alpha4-1 canvases); the coarse row takes
#   the canvas row's digest; a planted write between the two rows (a test-only `org.moment`) makes the reuse REFUSE (recompute);
#   an AST seam test pins that nothing between the digest statement and the `_coarse_row` call touches `self.org`, with a planted
#   offender the scanner must catch (#91's rule: a 0-finding sweep needs its negative control).
# M4 the sitter's canvas unit: the snapshot ledger carries the mind's own `_canvas_index`; `creature.exam.canvas_count_of` prefers it
#   and falls back to `moments // fixations` on an old ledger; `resume()` restores it (the advisor's block: a live restart under a
#   LAST.json cursor in the thousands would otherwise never sit again); `voice_loop` and SIT's `sense` read the one helper.
# M5 the think thread's real cost: `think_freeze_ms` / `think_apply_ms` on STATUS from `_build_status` (the one builder — the
#   existing pin tests/creature/test_a4l_cost_marks.py::test_every_status_write_goes_through_the_one_builder covers "every write");
#   the clock stays in creature/think_thread.py (test_mind_parity's no-clock AST law), mind.py does arithmetic on floats.
# tools/inventory.py: a `<BASE>_<X>` declared key resolves through its OWN RUNS row only (A4L-EXPLORE-REPORT §0 item 10 (a)),
#   agreeing with `creature.genes.unwired` (exact keys) by construction.
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import tempfile
import textwrap
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from creature import think_thread
from creature.mind import Mind
from creature.tape import read_tape
from genome.machinery import Organism, parse_genome
from genome.world import encode_word
from tests.creature import test_life_e_think_thread as _te      # helpers only: a module attribute is not a TestCase, so nothing runs twice
from tests.creature import test_surprise_coarse as _tc
from tests.genome.test_a4l_cost_witness import HASH_LINE

TREE = Path(__file__).resolve().parents[2]
MIND_SRC = TREE / "creature" / "mind.py"
COARSE_GENOME = TREE / "tests" / "creature" / "G5-surprise-coarse-test.genome"   # GAZE ... coarse 32 + SURPRISE: the coarse row is journaled

_spec = importlib.util.spec_from_file_location("inventory_tool", TREE / "tools" / "inventory.py")
inventory = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(inventory)


def _consume_tape(mind: Mind, root: Path) -> None:
    for r in read_tape(root):
        mind.consume(r)


def _moment_rows(root: Path):
    return [j for j in _tc._mind_rows(root) if "moment" in j]


# ============================================================================ the seam scanner (M3)
def org_touches_between(src: str, func_name: str = "_consume_eye"):
    """For every DIRECT statement calling `self._coarse_row(...)` in `func_name`, walk back in the SAME statement list to the
    nearest direct statement holding the digest call (`self.org.row_hash()` or `self._row_digest()`). Returns
    (call sites, sites with no digest statement in their block, [(lineno, source) of every statement strictly between that
    touches `self.org` — a read, a call or a write: any attribute chain rooted at it])."""
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func_name)

    def direct_call(st, names) -> bool:
        return isinstance(st, (ast.Assign, ast.AnnAssign, ast.Expr)) and any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in names for n in ast.walk(st))

    def touches_org(st) -> bool:
        return any(isinstance(n, ast.Attribute) and n.attr == "org" and isinstance(n.value, ast.Name) and n.value.id == "self"
                   for n in ast.walk(st))

    sites = unanchored = 0
    offenders = []
    for node in ast.walk(fn):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(node, field, None)
            if not isinstance(body, list):
                continue
            for i, st in enumerate(body):
                if not direct_call(st, {"_coarse_row"}):
                    continue
                sites += 1
                anchor = next((k for k in range(i - 1, -1, -1) if direct_call(body[k], {"row_hash", "_row_digest"})), None)
                if anchor is None:
                    unanchored += 1
                    continue
                offenders += [(st2.lineno, ast.unparse(st2)[:90]) for st2 in body[anchor + 1:i] if touches_org(st2)]
    return sites, unanchored, offenders


PLANTED = textwrap.dedent('''
    class M:
        def _consume_eye(self, row):
            if row:
                journal_row = {"seq": 1, "hash": self.org.row_hash()}
                self._write_journal(row["at"], journal_row)
                self.org.moment(x, w)
                coarse_row = self._coarse_row(1, None, [], [], None, digest=journal_row["hash"])
            else:
                sight_row = {"seq": 1, "hash": self._row_digest()}
                self._write_journal(row["at"], sight_row)
                t = self.org.t
                coarse_row = self._coarse_row(1, None, [], [], None, digest=sight_row["hash"])
    ''')

CLEAN = PLANTED.replace("            self.org.moment(x, w)\n", "").replace("            t = self.org.t\n", "")
UNANCHORED = textwrap.dedent('''
    class M:
        def _consume_eye(self, row):
            digest = "computed elsewhere"
            self._write_journal(row["at"], {"hash": digest})
            coarse_row = self._coarse_row(1, None, [], [], None, digest=digest)
    ''')


class M3OneHashPerCanvas(unittest.TestCase):
    def test_row_hash_is_called_once_per_worded_canvas(self) -> None:
        root = Path(tempfile.mkdtemp()); _tc._build_repeated_tape(root, "circle", 1)
        mind = Mind(COARSE_GENOME, root)
        rows = list(read_tape(root))
        self.assertEqual(sum(1 for r in rows if r["sense"] == "eye"), 1)
        calls = []
        orig = Organism.row_hash

        def counting(org):
            calls.append(1); return orig(org)

        for r in rows:
            if r["sense"] == "eye":
                with mock.patch.object(Organism, "row_hash", counting):
                    mind.consume(r)
            else:
                mind.consume(r)
        self.assertEqual(sum(1 for j in _moment_rows(root) if j.get("act") == "coarse"), 1, "premise: the coarse row was journaled")
        self.assertEqual(len(calls), 1, f"row_hash calls on one worded canvas: {len(calls)} — the coarse row must carry the canvas row's digest (M3)")

    def test_coarse_row_carries_the_canvas_rows_digest_under_both_witnesses(self) -> None:
        """PREREG §5.5 (100 % of canvases) and §7.2 seam 8 (COST × one hash: from whichever witness is declared)."""
        for label, text in (("dense", _tc.GENOME_TEXT), ("sparse", _tc.GENOME_TEXT + "\n" + HASH_LINE + "\n")):
            with self.subTest(witness=label):
                tmp = Path(tempfile.mkdtemp()); gp = _tc._write_genome(tmp, text); root = tmp / "run"; root.mkdir()
                _tc._build_repeated_tape(root, "square", 3)
                mind = Mind(gp, root); _consume_tape(mind, root)
                self.assertEqual("HASH" in mind.genome.declared, label == "sparse")
                by_seq = {}
                for j in _moment_rows(root):
                    by_seq.setdefault(j["seq"], []).append(j)
                pairs = [(rs[0], rs[1]) for rs in by_seq.values() if len(rs) == 2 and rs[1].get("act") == "coarse"]
                self.assertEqual(len(pairs), 3)
                for canvas, coarse in pairs:
                    self.assertEqual(coarse["hash"], canvas["hash"])
                    self.assertEqual(len(coarse["hash"]), 64)

    def test_a_planted_moment_between_the_two_rows_refuses_the_reuse(self) -> None:
        """PREREG §2.5 M3: 'a planted write between the two rows (a test-only moment) makes the reuse REFUSE (the digest
        recomputed), so the reuse can never hide a change' — and without the plant, no refusal."""
        for plant in (False, True):
            with self.subTest(plant=plant):
                root = Path(tempfile.mkdtemp()); _tc._build_repeated_tape(root, "circle", 1)
                mind = Mind(COARSE_GENOME, root)
                real_write = mind._write_journal
                rng = np.random.default_rng(3)

                def writing(at, obj):
                    real_write(at, obj)
                    if plant and isinstance(obj.get("fix"), list):     # the canvas row is on disk; a test-only moment before the coarse row
                        x = rng.standard_normal(mind.genome.sight_dim()); x /= np.linalg.norm(x)
                        mind.org.moment(x, encode_word("zog", mind.genome.ear_blank_zero))

                with mock.patch.object(mind, "_write_journal", writing):
                    _consume_tape(mind, root)
                rows = _moment_rows(root)
                canvas = next(j for j in rows if isinstance(j.get("fix"), list))
                coarse = next(j for j in rows if j.get("act") == "coarse")
                if plant:
                    self.assertNotEqual(coarse["hash"], canvas["hash"], "the digest must be recomputed over the planted write")
                    self.assertEqual(mind.hash_reuse_refused, 1)
                else:
                    self.assertEqual(coarse["hash"], canvas["hash"])
                    self.assertEqual(mind.hash_reuse_refused, 0)

    def test_nothing_touches_the_organism_between_the_digest_and_the_coarse_row(self) -> None:
        sites, unanchored, offenders = org_touches_between(MIND_SRC.read_text())
        self.assertEqual(sites, 2, "both canvas branches (worded; sight-only + FAST) journal a coarse row")
        self.assertEqual(unanchored, 0, "each branch computes the digest in the same statement list as its _coarse_row call")
        self.assertEqual(offenders, [])

    def test_the_seam_scanner_catches_a_planted_touch(self) -> None:
        sites, unanchored, offenders = org_touches_between(PLANTED)
        self.assertEqual((sites, unanchored), (2, 0))
        self.assertEqual([o[1] for o in offenders], ["self.org.moment(x, w)", "t = self.org.t"], "a write AND a read between the rows are both caught")
        self.assertEqual(org_touches_between(CLEAN), (2, 0, []))
        self.assertEqual(org_touches_between(UNANCHORED)[:2], (1, 1), "a digest computed outside the block is not a witness")


# ============================================================================ M4
class M4TheSittersCanvasUnit(unittest.TestCase):
    def test_canvas_count_of_prefers_the_minds_own_count_and_falls_back(self) -> None:
        from creature.exam import canvas_count_of
        self.assertEqual(canvas_count_of({"moments": 2200}, 4), 550, "an old ledger: the old arithmetic, unchanged")
        self.assertEqual(canvas_count_of({"moments": 2200, "canvas_index": 400}, 4), 400)
        self.assertEqual(canvas_count_of({}, 4), 0)
        self.assertEqual(canvas_count_of({"moments": 7, "canvas_index": None}, 4), 1, "a malformed key falls back, never crashes")
        self.assertEqual(canvas_count_of({"moments": 7, "canvas_index": True}, 4), 1, "a bool is not a count")
        self.assertEqual(canvas_count_of({"moments": 7}, 0), 7)

    def test_snapshot_writes_canvas_index_and_resume_restores_it(self) -> None:
        root = Path(tempfile.mkdtemp()); _tc._build_repeated_tape(root, "circle", 3)
        mind = Mind(COARSE_GENOME, root); _consume_tape(mind, root)
        self.assertEqual(mind._canvas_index, 3)
        mind.snapshot()
        ledger = json.loads((root / "state" / "ledger.json").read_text())
        self.assertEqual(ledger.get("canvas_index"), 3)
        self.assertNotIn("canvas_index", (root / "state" / "organism.json").read_text(), "a ledger key, never an organism key (the hash law)")
        resumed, last_seq = Mind.resume(COARSE_GENOME, root)
        self.assertEqual(last_seq, mind.last_seq)
        self.assertEqual(resumed._canvas_index, 3, "a live restart must continue the canvas count the sitter's LAST.json cursor was set from")
        self.assertEqual(resumed.org.state_hash(), mind.org.state_hash())

    def test_voice_loop_fires_at_the_minds_canvas_count_not_the_moment_arithmetic(self) -> None:
        """PREREG §2.5 M4: on a toy ledger with 5 moments a canvas + 200 per sleep (400 canvases = 2,200 moments), the exam fired
        at canvas 400 (2,200 // 4 = 550 ≥ 500) — RED against «at 500»; an old ledger (no key) keeps the old arithmetic."""
        from creature import exam as exam_module
        cases = (({"moments": 2200, "canvas_index": 400}, False),
                 ({"moments": 2200}, True),
                 ({"moments": 2600, "canvas_index": 500}, True))
        for ledger, fires in cases:
            with self.subTest(ledger=ledger):
                root = Path(tempfile.mkdtemp()); (root / "state").mkdir(); (root / "exam").mkdir()
                birth = root / "birth.genome"; birth.write_text("SEED 1\n")
                (root / "state" / "ledger.json").write_text(json.dumps(ledger))
                seen = []; stop = threading.Event()

                def fake_run(r, gp, held=10, check_tape=400):
                    seen.append(1); stop.set(); return {}

                fake_genome = mock.Mock(); fake_genome.gaze = {"fixations": 4}
                with mock.patch.object(exam_module, "run_and_journal", side_effect=fake_run), \
                     mock.patch("genome.machinery.parse_genome", return_value=fake_genome):
                    th = threading.Thread(target=exam_module.voice_loop, args=(root, birth, stop),
                                          kwargs={"every_canvases": 500, "poll_period": 0.01}, daemon=True)
                    th.start(); th.join(timeout=0.6)       # bounded: the loop only stops itself when it fires
                    stop.set(); th.join(timeout=2.0)
                self.assertEqual(bool(seen), fires)
                if fires:
                    self.assertEqual(json.loads((root / "exam" / "LAST.json").read_text())["last_canvas"], 550 if "canvas_index" not in ledger else 500)

    def test_sit_sense_reads_the_same_canvas_unit(self) -> None:
        from creature.senses import sit as sit_sense
        root = Path(tempfile.mkdtemp()); (root / "exam").mkdir(); (root / "state").mkdir()
        genome = root / "g.genome"; genome.write_text((TREE / "genome" / "LIFE.genome").read_text())
        (root / "exam" / "2026-09-23T000001Z.json").write_text(json.dumps({"ask_seen_words": {"Q1": {"acc": 0.8}, "composite": 0.9}, "read_share": 0.7}))
        (root / "state" / "ledger.json").write_text(json.dumps({"moments": 40, "canvas_index": 3}))   # 3 real canvases; 40 // 4 read 10
        published = []; stop = threading.Event()
        th = threading.Thread(target=sit_sense.sense, args=(lambda s_, p_, m_, e_: published.append(m_) or {"seq": 1}, stop),
                              kwargs={"root": root, "genome_path": genome, "every_canvases": 5, "poll_period": 0.05}, daemon=True)
        th.start(); time.sleep(0.6)
        self.assertEqual(published, [], "3 real canvases < every 5: no sitting row (the old arithmetic read 40 // 4 = 10 and published)")
        (root / "state" / "ledger.json").write_text(json.dumps({"moments": 40, "canvas_index": 5}))
        deadline = time.time() + 5.0
        while len(published) < 1 and time.time() < deadline:
            time.sleep(0.05)
        self.assertEqual(len(published), 1)
        stop.set(); th.join(timeout=2.0)


# ============================================================================ M5
class M5ThinkTiming(unittest.TestCase):
    def test_status_carries_think_freeze_and_apply_ms_on_every_write(self) -> None:
        """#164's law, as tests/creature/test_life_e_think_thread.py pins think_ms: on STATUS from the first write, None on an
        untreaded genome (the road never ran), never a missing key."""
        import creature.body as body_module
        root = Path(tempfile.mkdtemp()); _te._build_tape(root, n=20, seed=17)
        b = body_module.Body(root, _te.G4_GENOME); b.mind = Mind(_te.G4_GENOME, root)
        for r in read_tape(root):
            b.mind.consume(r)
        st = b._build_status()
        for k in ("think_freeze_ms", "think_apply_ms"):
            self.assertIn(k, st); self.assertIsNone(st[k])

    def test_a_threaded_run_records_freeze_and_apply_ms_as_floats(self) -> None:
        import creature.body as body_module
        tmp = Path(tempfile.mkdtemp()); gp = _te._write_threaded_genome(tmp); root = tmp / "run"; root.mkdir()
        _te._build_tape(root, n=30, seed=7)
        mind = Mind(gp, root); _consume_tape(mind, root); mind.close()
        b = body_module.Body(root, gp); b.mind = mind
        st = b._build_status()
        self.assertGreater(st["thinks"], 0, "premise: a threaded think ran on this tape")
        self.assertIsInstance(mind.think_freeze_ms_last, float); self.assertGreaterEqual(mind.think_freeze_ms_last, 0.0)
        self.assertIsInstance(mind.think_apply_ms_last, float); self.assertGreaterEqual(mind.think_apply_ms_last, 0.0)
        self.assertEqual(st["think_freeze_ms"], round(mind.think_freeze_ms_last, 3))
        self.assertEqual(st["think_apply_ms"], round(mind.think_apply_ms_last, 3))

    def test_the_clock_stays_in_think_thread(self) -> None:
        tree = ast.parse(MIND_SRC.read_text())
        self.assertEqual([n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr in ("perf_counter", "monotonic")], [],
                         "creature/mind.py does arithmetic on the floats think_thread hands back; it never reads a clock (test_mind_has_no_clock is the law)")
        self.assertTrue(callable(getattr(think_thread, "freeze_inputs_timed", None)))
        self.assertTrue(callable(getattr(think_thread, "timed_call", None)))
        result, ms = think_thread.timed_call(time.sleep, 0.02)
        self.assertIsNone(result); self.assertGreaterEqual(ms, 15.0)


# ============================================================================ tools/inventory.py
class InventoryResolvesAKeyThroughItsOwnRow(unittest.TestCase):
    def test_a_base_x_key_resolves_only_through_its_own_runs_row(self) -> None:
        self.assertEqual(inventory.site_of("ACT", {"ACT"}), "genes.RUNS")
        self.assertTrue(inventory.site_of("ACT_VALUE", {"ACT"}).startswith("NO SITE"),
                        "ACT_VALUE read MADE through ACT's row while Mind.__init__ refused the organism (A4L-EXPLORE-REPORT §0 item 10 (a))")
        self.assertEqual(inventory.site_of("ACT_VALUE", {"ACT", "ACT_VALUE"}), "genes.RUNS")

    def test_agrees_with_the_refusal_law_on_the_real_registry(self) -> None:
        from creature import genes
        g = parse_genome((TREE / "genome" / "ALPHA4.genome").read_text())

        def wired():
            return {k for layer in genes.RUNS.values() for k, s in layer.items() if s is not None}

        for k in g.declared:
            self.assertEqual(inventory.site_of(k, wired()).startswith("NO"), k in genes.unwired(g.declared), k)
        layer = next(name for name, d in genes.RUNS.items() if "WORLD_GAME" in d)
        with mock.patch.dict(genes.RUNS[layer], {"WORLD_GAME": None}):      # its own row gone; WORLD's stays — the old rule read MADE through it
            self.assertIn("WORLD", wired(), "premise of the control: the base IS wired, so only the exact-key rule can refuse")
            self.assertIn("WORLD_GAME", genes.unwired(g.declared))
            self.assertTrue(inventory.site_of("WORLD_GAME", wired()).startswith("NO"))

    def test_the_real_genome_still_reads_clear(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = inventory.main([str(TREE / "genome" / "ALPHA4.genome"), "--tree", str(TREE)])
        self.assertEqual(rc, 0, buf.getvalue()[-600:])
        self.assertIn("DECLARED-ONLY 0", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
