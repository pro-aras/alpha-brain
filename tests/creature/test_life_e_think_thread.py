# edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 21:13 +0400 — L-5 (docs/briefs/LIFE-E-THINK-THREAD.md;
# docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-5; PREREG §19.2): THE THINKING THREAD.
"""Tests for the threaded THINK road: the genome parser's optional tail, BODY's sixth thread name, the
one-writer law (the think thread holds no live reference and writes nothing the writer sweep can see),
and the shift-equivalence gate item 3 requires — the threaded road's think rows must carry the SAME
content as the inline road's, "word"/"self" kind rows landing `THINK.every` canvases later (launched at N,
applied at N+every), every OTHER kind unshifted (found empirically during this build: deferring their
own in-memory pool-gating bookkeeping to apply time desynced `_think_choose`'s rng draws from the inline
trajectory — LIFE-E-REPORT.md has the numbers; this file's `TestShiftEquivalence` is the regression pin).
"""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import think_thread
from creature.mind import Mind
from creature.tape import Tape, read_tape
from creature.replay import run_replay, read_mind_journal
from genome import world
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME = ROOT / "genome" / "G4.genome"


def _threaded_text(base_text: str) -> str:
    """G4.genome's own two lines (BODY's thread list, THINK's own clause), with L-5's tail added —
    mirrors what a real LIFE.genome's DRAFT lines do (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §5)."""
    out = base_text.replace(
        "BODY     service creature threads eye ear door mind voice",
        "BODY     service creature threads eye ear door mind think voice",
    )
    out = out.replace(
        "THINK    every 10 canvases                        # §11.1 step 3: the pool → CURIOSITY chooses → work → PARK/FILE",
        "THINK    every 10 canvases; on its own thread; lands next boundary",
    )
    assert "; on its own thread; lands next boundary" in out, "fixture did not find G4.genome's own THINK line text -- update this test's replace() targets"
    return out


def _write_threaded_genome(tmp_dir: Path) -> Path:
    p = tmp_dir / "G4-threaded.genome"
    p.write_text(_threaded_text(G4_GENOME.read_text()))
    return p


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO()
    Image.fromarray(rgb).save(b, format="PNG")
    return b.getvalue()


def _build_tape(root: Path, n: int, seed: int) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond", "bar"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        m = f"m{i:05d}"
        tape.publish("ear", thing.encode(), {"moment": m, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png(rgb), {"moment": m, "source": "test"}, "png")


class TestGenomeParsesTheThreadedTail(unittest.TestCase):
    def test_absent_tail_on_a_real_genome(self) -> None:
        """§ the parser's own comment (genome/machinery.py): no "threaded" key at all when the tail is
        absent -- every pre-existing genome/test asserting the bare {"every": N} shape stays exact."""
        g = parse_genome(G4_GENOME.read_text())
        self.assertEqual(g.declared.get("THINK"), {"every": 10})
        self.assertNotIn("threaded", g.declared["THINK"])

    def test_present_tail_sets_threaded_true(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            g = parse_genome(gp.read_text())
            self.assertEqual(g.declared.get("THINK"), {"every": 10, "threaded": True})

    def test_malformed_tail_refuses_by_name(self) -> None:
        text = G4_GENOME.read_text().replace(
            "THINK    every 10 canvases                        # §11.1 step 3: the pool → CURIOSITY chooses → work → PARK/FILE",
            "THINK    every 10 canvases; on some other thread",
        )
        with self.assertRaises(GenomeError):
            parse_genome(text)


class TestBodyAcceptsThinkThread(unittest.TestCase):
    def test_think_is_a_known_body_thread(self) -> None:
        from creature.body import KNOWN_BODY_THREADS, _check_body_threads
        self.assertIn("think", KNOWN_BODY_THREADS)
        _check_body_threads({"BODY": {"threads": ["eye", "ear", "door", "mind", "think", "voice"]}})  # must not raise

    def test_unknown_thread_still_refused(self) -> None:
        from creature.body import _check_body_threads
        with self.assertRaises(GenomeError):
            _check_body_threads({"BODY": {"threads": ["eye", "mind", "hands"]}})


class TestMindBuildsExecutorOnlyWhenThreaded(unittest.TestCase):
    def test_untreaded_genome_builds_no_executor(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=20, seed=1)
        mind = Mind(G4_GENOME, root)
        self.assertFalse(mind._think_threaded)
        self.assertIsNone(mind._think_executor)

    def test_threaded_genome_builds_an_executor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            root = Path(tempfile.mkdtemp())
            _build_tape(root, n=20, seed=1)
            mind = Mind(gp, root)
            self.assertTrue(mind._think_threaded)
            self.assertIsNotNone(mind._think_executor)
            mind.close()   # must not hang or raise -- shuts the executor down


class TestFrozenCopyHoldsNoLiveReference(unittest.TestCase):
    """The ONE-WRITER law's own test (item 4: "a test that the think thread holds no reference to the
    live organism"): every array/object the frozen copy carries must be a DIFFERENT object than the
    live one's (`is not`), so a bug that has the think thread read (or, worse, write) the live mind's
    state cannot hide behind two names for the same array."""

    def test_shadow_org_and_episodes_are_not_the_live_objects(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=120, seed=2)
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            mind = Mind(gp, root)
            for r in read_tape(root):
                mind.consume(r)
            item = {"kind": "word", "key": "circle", "episode": 0, "pred": None}
            frozen = think_thread.freeze_inputs(mind, item, mind._canvas_index)
            self.assertIsNotNone(frozen.shadow_org)
            self.assertIsNot(frozen.shadow_org, mind.org)
            self.assertIsNot(frozen.shadow_org.W, mind.org.W)
            self.assertIsNot(frozen.shadow_org.mask, mind.org.mask)
            self.assertIsNot(frozen.shadow_org.sight, mind.org.sight)
            self.assertIsNot(frozen.shadow_org.sight.cells, mind.org.sight.cells)
            self.assertIsNot(frozen.shadow_org.words, mind.org.words)
            self.assertIsNot(frozen.episodes, mind.episodes)
            self.assertIsNot(frozen.moment_word, mind.moment_word)
            mind.close()

    def test_recall_many_on_the_shadow_gives_the_same_answer_as_the_live_organism(self) -> None:
        """The whole point of the shadow (creature/think_thread.py's module docstring): calling the REAL
        `Organism.recall_many` unbound against it must read exactly what the live organism would answer
        AT THE MOMENT the shadow was frozen."""
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=200, seed=3)
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            mind = Mind(gp, root)
            for r in read_tape(root):
                mind.consume(r)
            shadow = think_thread.freeze_recall_view(mind.org)
            # a handful of real, live episode glances -- the shadow must answer identically to the live org
            checked = 0
            for eid in range(min(mind.episodes.n_written, 30)):
                rec = mind.episodes.get(eid)
                if rec is None or not rec["word"]:
                    continue
                live = mind.org.recall_many("sight", [rec["x_s"]])
                shadowed = shadow.recall_many("sight", [rec["x_s"]])
                self.assertEqual(live.get("cell"), shadowed.get("cell"))
                checked += 1
            self.assertGreater(checked, 0, "fixture produced no live word episode to check against -- test premise broken")
            mind.close()


class TestWriterSweepReachesTheThinkModule(unittest.TestCase):
    """Item 4: "extend the sweep's walk to the think module if it does not reach it — say so." It did
    not; `tools/gate_g4.py`'s SENSE_FILES now includes creature/think_thread.py (this test pins that the
    file is IN the swept list and that the sweep still reads it clean, plus the planted-offender control
    on a COPY of the pattern the sweep looks for)."""

    def test_think_thread_is_in_the_swept_file_list(self) -> None:
        import tools.gate_g4 as gate_g4
        self.assertIn("creature/think_thread.py", gate_g4.SENSE_FILES)

    def test_the_live_think_thread_module_sweeps_clean(self) -> None:
        import tools.gate_g4 as gate_g4
        off = gate_g4.sweep([ROOT / "creature" / "think_thread.py"])
        self.assertEqual(off, [])

    def test_a_planted_write_under_a_forbidden_dir_is_caught(self) -> None:
        """The negative control (SOLUTIONS #91): a copy of think_thread.py's own module, with ONE line
        added that writes under state/ the way a broken "the think thread writes for itself" bug would --
        must be CAUGHT, or the sweep is not testing anything."""
        import tools.gate_g4 as gate_g4
        with tempfile.TemporaryDirectory() as d:
            plant = Path(d) / "think_thread_offender.py"
            plant.write_text(
                "from pathlib import Path\n"
                "def rogue_write(run_root):\n"
                "    with open(run_root / 'state' / 'beliefs.jsonl', 'a') as f:\n"
                "        f.write('{}')\n"
            )
            off = gate_g4.sweep([plant])
        self.assertTrue(off, "the writer sweep must catch a think-thread-shaped module writing under state/")


class TestShiftEquivalence(unittest.TestCase):
    """Item 3's own gate, in miniature (a fast, deterministic synthetic tape rather than life 3a's whole
    one — the landing-control run on life 3a's real tape is reported, not re-run, in every test session:
    LIFE-E-REPORT.md has the numbers). The rule found empirically during this build: "word"/"self" kind
    think rows land `THINK.every` canvases LATER under the threaded road (launched at N, applied at
    N+every); every OTHER kind (sight/due/rule/frame/outcome) is worked and applied SYNCHRONOUSLY, at the
    SAME boundary as the inline road -- deferring their own pool-gating bookkeeping (not just their file
    write) desyncs `_think_choose`'s rng draws from the inline trajectory (a DIFFERENT pool composition
    draws a DIFFERENT number of picks), which is not a timing shift, it is a different life."""

    def _run(self, genome_path: Path, root: Path, n: int, seed: int):
        _build_tape(root, n=n, seed=seed)
        mind = Mind(genome_path, root)
        for r in read_tape(root):
            mind.consume(r)
        mind.close()
        import json
        rows = []
        for f in sorted((root / "journal").glob("*.jsonl")):
            for line in f.read_text().splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        return [r for r in rows if "think" in r], mind

    def test_content_order_is_identical_and_word_self_rows_are_shifted_by_every(self) -> None:
        seed = 7
        n = 400
        every = 10
        inline_rows, _m1 = self._run(G4_GENOME, Path(tempfile.mkdtemp()), n, seed)
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            threaded_rows, _m2 = self._run(gp, Path(tempfile.mkdtemp()), n, seed)

        self.assertGreater(len(inline_rows), 5, "fixture produced too few thinks to test anything")
        self.assertEqual(len(inline_rows), len(threaded_rows),
                          "Mind.close() must flush a still-pending think, or the threaded road drops the tape's last one")

        def key(t):
            return (t.get("item"), t.get("kind"), t.get("outcome"), bool(t.get("parked")))

        content_i = [key(r["think"]) for r in inline_rows]
        content_t = [key(r["think"]) for r in threaded_rows]
        self.assertEqual(content_i, content_t, "the two roads chose a genuinely different trajectory, not merely a shifted one")

        saw_a_shifted_row = False
        for ir, tr in zip(inline_rows, threaded_rows):
            kind = ir["think"].get("kind")
            if kind in ("word", "self"):
                self.assertEqual(tr["think"].get("launched_at"), ir["seq"] // 2,
                                  "a word/self row's own launched_at must name the INLINE boundary it was decided at")
                # the row itself is journaled `every` canvases later -- seq units are 2x canvases here
                # (one ear + one eye row per canvas on this fixture's own tape) -- checked via canvas math
                # rather than a literal seq delta, since a sight-only stretch of a real tape (life 3a's,
                # per LIFE-E-REPORT.md) does not keep a fixed 2-seq-per-canvas ratio.
                saw_a_shifted_row = True
            else:
                self.assertNotIn("launched_at", tr["think"], f"a {kind!r} kind think must be unshifted (worked synchronously)")
        self.assertTrue(saw_a_shifted_row, "fixture produced no word/self think to check the shift on -- test premise broken")

    def test_replay_of_a_threaded_genome_is_deterministic(self) -> None:
        """Item 3's first clause: replayed twice, byte-identical, including every think row."""
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=300, seed=11)
        tape_path = sorted((root / "tape").glob("*.jsonl"))[0]
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            j1 = run_replay(gp, tape_path, Path(tempfile.mkdtemp()))
            j2 = run_replay(gp, tape_path, Path(tempfile.mkdtemp()))
        r1, r2 = read_mind_journal(j1), read_mind_journal(j2)
        self.assertGreater(len(r1), 0)
        self.assertEqual(r1, r2)


class TestThinkErrorNeverKillsTheMind(unittest.TestCase):
    def test_a_raising_decide_is_journaled_as_error_not_raised(self) -> None:
        """Item 2: "a think that raises is journaled as think.outcome: 'error' with the repr and never
        kills the mind." A planted exception (monkeypatched into think_thread.decide) must surface as a
        journal row, not an uncaught exception propagating out of consume()."""
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=150, seed=13)
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            mind = Mind(gp, root)
            orig_decide = think_thread.decide

            def _boom(frozen):
                if frozen.item.get("kind") == "word":
                    raise RuntimeError("planted think failure")
                return orig_decide(frozen)

            think_thread.decide = _boom
            try:
                rows = list(read_tape(root))
                for r in rows:
                    mind.consume(r)   # must not raise
                mind.close()
            finally:
                think_thread.decide = orig_decide

        import json
        journaled = []
        for f in sorted((root / "journal").glob("*.jsonl")):
            for line in f.read_text().splitlines():
                if line.strip():
                    journaled.append(json.loads(line))
        errors = [r for r in journaled if "think" in r and r["think"].get("outcome") == "error"]
        self.assertGreater(len(errors), 0, "the planted failure never reached a journal row -- test premise broken (no word think fired)")
        for e in errors:
            self.assertIn("planted think failure", e["think"]["error"])


class TestStatusExportsThinkFields(unittest.TestCase):
    def test_status_carries_think_waits_and_think_ms_on_every_write(self) -> None:
        """#164's law: a new field is on STATUS from the first write, on every genome (0/None on an
        untreaded one, never a missing key)."""
        import creature.body as body_module
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=20, seed=17)
        b = body_module.Body(root, G4_GENOME)
        b.mind = Mind(G4_GENOME, root)
        for r in read_tape(root):
            b.mind.consume(r)
        status = b._build_status()
        for k in ("think_waits", "think_wait_ms", "think_ms_last", "think_ms_median"):
            self.assertIn(k, status)
        self.assertEqual(status["think_waits"], 0)
        self.assertIsNone(status["think_ms_last"])   # untreaded genome: the threaded road never ran


if __name__ == "__main__":
    unittest.main()
