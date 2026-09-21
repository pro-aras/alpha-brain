# edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-EYE-1/G-MIND-1 (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md;
# docs/organs/G5-DESIGN.md §3/§4; docs/organs/EYE.md §4 G-EYE-1; docs/organs/MIND-MEMORY.md §4 G-MIND-1). The seam contract:
# DELIVER (the eye's promise) + MOMENT (the mind's promise) carry where/when/act/source (and the glance index) BESIDE every
# glance's feature into the FAST episode row and the journal row, NEVER into the cosine-compared vectors (x_s/x_w). Four
# things are pinned here, matching the brief's own TESTS clause: (a) the seam actually reaches a real episode on a real
# tape (#180: one episode row carrying where/when/act/source, proven through Mind.consume(), never hand-built); (b) PARITY
# — declaring DELIVER+MOMENT moves no mark and no state_hash, with a planted leak proving the check is sensitive, not
# vacuous; (c) the E51 A1.2 position plant — two classes whose 32x32 glance windows are byte-identical and differ only in
# where they were taken: chance is a FACT (asserted, not hoped) before any answer is read, the mind answers ABOVE chance
# through `where` (Episodes.nearest_where — a rule that never reads x_s), and the `--blind where` twin sits at EXACTLY
# chance.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import gaze as gaze_module
from genome.machinery import parse_genome, retina as retina_fn
from tests.creature.test_wave2_predict_fast import _build_mixed_tape, _png_bytes

ROOT = Path(__file__).resolve().parents[2]
WAVE2_GENOME_TEXT = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()
DELIVER_LINE = "DELIVER  where fixation when instant act glance"
MOMENT_LINE = "MOMENT   keys sight words surprise where when act source"
SEAM_GENOME_TEXT = WAVE2_GENOME_TEXT + "\n" + DELIVER_LINE + "\n" + MOMENT_LINE + "\n"

SEAM_ONLY_JOURNAL_KEYS = {"windows", "when", "act", "source", "glance"}


def _write_genome(tmp_dir: Path, text: str, name: str) -> Path:
    p = tmp_dir / name
    p.write_text(text)
    return p


def _journal_rows(root: Path) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
    return out


class TestSeamGenomeParses(unittest.TestCase):
    def test_seam_genome_declares_both(self) -> None:
        g = parse_genome(SEAM_GENOME_TEXT)
        self.assertIn("DELIVER", g.declared)
        self.assertIn("MOMENT", g.declared)


class TestSeamReachesARealEpisode(unittest.TestCase):
    """#180: only conjunction computes a value — prove the LAST link with one real value. Not a hand-built
    Episodes row: a real tape, a real Mind.consume() loop, then read what actually landed."""

    def test_episode_row_carries_where_when_act_source_on_a_real_tape(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _write_genome(tmp, SEAM_GENOME_TEXT, "seam.genome")
        root = tmp / "run"
        _build_mixed_tape(root, n_worded=8, n_sight_only=3, seed=1234)
        mind = Mind(genome_path, root)
        rows = list(read_tape(root))
        eye_rows = [r for r in rows if r["sense"] == "eye"]
        for r in rows:
            mind.consume(r)

        self.assertGreater(mind.episodes.n_written, 0)
        checked_worded = checked_sight = 0
        for eid in range(mind.episodes.n_written):
            rec = mind.episodes.get(eid)
            if rec is None:
                continue
            with self.subTest(eid=eid):
                self.assertIsNotNone(rec["where"])
                self.assertEqual(len(rec["where"]), 2)
                self.assertIsNotNone(rec["when"])
                self.assertTrue(rec["when"].endswith("Z"), "when must be the tape's own ISO instant")
                self.assertEqual(rec["act"], "glance")
                self.assertEqual(rec["source"], "test")   # _build_mixed_tape's own meta["source"]
                self.assertEqual(rec["glance"], 0)
            if rec["word"]:
                checked_worded += 1
            else:
                checked_sight += 1
        self.assertGreater(checked_worded, 0, "at least one real worded episode must carry the seam")
        self.assertGreater(checked_sight, 0, "at least one real sight-only episode must carry the seam")

        # and onto the journal row (the audit-facing per-tick record), additively
        canvas_rows = [r for r in _journal_rows(root) if "event" not in r and "sleep" not in r and "think" not in r]
        self.assertEqual(len(canvas_rows), len(eye_rows))
        for r in canvas_rows:
            self.assertIn("windows", r); self.assertGreaterEqual(len(r["windows"]), 1)
            self.assertIn("when", r); self.assertEqual(r["act"], "glance")
            self.assertEqual(r["source"], "test"); self.assertEqual(r["glance"], 0)


class TestUndeclaredMeansAbsent(unittest.TestCase):
    def test_no_seam_fields_when_genes_undeclared(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _write_genome(tmp, WAVE2_GENOME_TEXT, "base.genome")  # no DELIVER/MOMENT
        root = tmp / "run"
        _build_mixed_tape(root, n_worded=6, n_sight_only=2, seed=1234)
        mind = Mind(genome_path, root)
        for r in read_tape(root):
            mind.consume(r)
        self.assertGreater(mind.episodes.n_written, 0)
        for eid in range(mind.episodes.n_written):
            rec = mind.episodes.get(eid)
            if rec is None:
                continue
            self.assertIsNone(rec["where"]); self.assertIsNone(rec["when"])
            self.assertIsNone(rec["act"]); self.assertIsNone(rec["source"]); self.assertIsNone(rec["glance"])
        for r in _journal_rows(root):
            self.assertNotIn("windows", r)


class TestSeamParity(unittest.TestCase):
    """The refusing test (G-EYE-1/G-MIND-1's own clause a): declaring DELIVER+MOMENT must move no mark
    and no state_hash — the four fields never enter x_s/x_w."""

    @staticmethod
    def _run(genome_path: Path, root: Path) -> Mind:
        mind = Mind(genome_path, root)
        for r in read_tape(root):
            mind.consume(r)
        return mind

    @staticmethod
    def _strip_seam(row: Dict[str, object]) -> Dict[str, object]:
        return {k: v for k, v in row.items() if k not in SEAM_ONLY_JOURNAL_KEYS}

    def test_parity_state_hash_and_every_pre_existing_mark(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        base_path = _write_genome(tmp, WAVE2_GENOME_TEXT, "base.genome")
        seam_path = _write_genome(tmp, SEAM_GENOME_TEXT, "seam.genome")

        root_a = tmp / "run_base"
        _build_mixed_tape(root_a, n_worded=25, n_sight_only=6, seed=4242)
        mind_a = self._run(base_path, root_a)

        root_b = tmp / "run_seam"
        _build_mixed_tape(root_b, n_worded=25, n_sight_only=6, seed=4242)  # same seed -> byte-identical tape content
        mind_b = self._run(seam_path, root_b)

        self.assertEqual(mind_a.org.state_hash(), mind_b.org.state_hash(),
                          "declaring DELIVER+MOMENT must not move the organism's state_hash (gate G4-2's own digest)")
        self.assertEqual(mind_a.org.summary(), mind_b.org.summary(), "every existing mark (births/cells/edges/…) must match")

        rows_a = _journal_rows(root_a)
        rows_b = [self._strip_seam(r) for r in _journal_rows(root_b)]
        self.assertEqual(len(rows_a), len(rows_b))
        for i, (ra, rb) in enumerate(zip(rows_a, rows_b)):
            self.assertEqual(ra, rb, f"journal row {i} diverged once the seam's own new keys are excluded")

    def test_negative_control_a_leak_into_the_cosine_is_caught(self) -> None:
        """Plant exactly the failure G-EYE-1 forbids -- a position folded into the cosine-compared
        vector -- and prove the parity check above is sensitive to it, not vacuously equal."""
        tmp = Path(tempfile.mkdtemp())
        base_path = _write_genome(tmp, WAVE2_GENOME_TEXT, "base.genome")
        seam_path = _write_genome(tmp, SEAM_GENOME_TEXT, "seam.genome")

        root_a = tmp / "run_base"
        _build_mixed_tape(root_a, n_worded=10, n_sight_only=2, seed=99)
        base_hash = self._run(base_path, root_a).org.state_hash()

        real_glances = gaze_module.glances

        def leaky_glances(rgb, spec, gz, mode="surprise", pic_id="", colour=None):
            # edit: Claude (Fable 5.1), 2026-09-21 22:12 +0400 — the I×J seam: the mind now passes `colour=` (Builder J); a wrapper that drops it raised TypeError under the merged tree (landing J)
            g = real_glances(rgb, spec, gz, mode, pic_id, colour=colour)
            if g["feats"] and g["windows"]:
                top, left = g["windows"][0]
                leaked = g["feats"][0].copy()
                leaked[0] = leaked[0] + (top + left) * 1e-3   # the position, folded into the compared vector
                g["feats"] = [leaked] + list(g["feats"][1:])
            return g

        root_b = tmp / "run_leak"
        _build_mixed_tape(root_b, n_worded=10, n_sight_only=2, seed=99)   # same tape content as root_a
        with patch("creature.mind.gaze.glances", side_effect=leaky_glances):
            leaked_hash = self._run(seam_path, root_b).org.state_hash()

        self.assertNotEqual(base_hash, leaked_hash,
                             "CONTROL: a position leaked into the cosine must move state_hash — CAUGHT. "
                             "If this assertion ever fails, the parity test above is not sensitive.")


class TestPositionPlantE51A12(unittest.TestCase):
    """E51's A1.2 form (SOLUTIONS #228 addendum; docs/organs/EYE.md G-EYE-1's own test clause): two classes
    whose 32x32 glance windows are byte-identical, differing only in the window's position on the full
    canvas. `fixations` (Alpha 2's sha-pinned saliency organ, out of this seam's scope) is replaced here by
    a controlled, deterministic rule so the test is not at the mercy of a black-box saliency call landing
    on the plant's exact 8-pixel grid cell — the SAME discipline #228(c) used to redeclare this family as
    "a window on a canvas" rather than "invisible to a colour-blind eye"."""

    GRID = 16
    CANVAS = 128
    GLANCE = 32
    CELL_A = (4, 4)
    CELL_B = (10, 10)
    BACKGROUND = 180

    @classmethod
    def _window_origin(cls, cell):
        h = w = cls.CANVAS
        cy, cx = (cell[0] + 0.5) * (h / cls.GRID), (cell[1] + 0.5) * (w / cls.GRID)
        top = int(min(max(round(cy - cls.GLANCE / 2), 0), h - cls.GLANCE))
        left = int(min(max(round(cx - cls.GLANCE / 2), 0), w - cls.GLANCE))
        return top, left

    @classmethod
    def _patch(cls) -> np.ndarray:
        """A 32x32 RGB patch with real structure (a filled disc) — deterministic, no RNG."""
        yy, xx = np.mgrid[0:cls.GLANCE, 0:cls.GLANCE]
        disc = ((yy - cls.GLANCE // 2) ** 2 + (xx - cls.GLANCE // 2) ** 2) <= 10 ** 2
        arr = np.full((cls.GLANCE, cls.GLANCE), 40, dtype=np.uint8)
        arr[disc] = 220
        return np.stack([arr, arr, arr], axis=-1)

    @classmethod
    def _canvas(cls, top: int, left: int) -> np.ndarray:
        c = np.full((cls.CANVAS, cls.CANVAS, 3), cls.BACKGROUND, dtype=np.uint8)
        c[top:top + cls.GLANCE, left:left + cls.GLANCE] = cls._patch()
        return c

    def setUp(self) -> None:
        self.top_a, self.left_a = self._window_origin(self.CELL_A)
        self.top_b, self.left_b = self._window_origin(self.CELL_B)
        self.canvas_a = self._canvas(self.top_a, self.left_a)
        self.canvas_b = self._canvas(self.top_b, self.left_b)

    def test_a_ceiling_first_byte_identical_frames_equal_vectors(self) -> None:
        """So chance is a fact, not a hope, BEFORE any answer is read."""
        win_a, tl_a = gaze_module.glance_window(gaze_module.luminance(self.canvas_a), self.CELL_A, self.GRID, self.GLANCE)
        win_b, tl_b = gaze_module.glance_window(gaze_module.luminance(self.canvas_b), self.CELL_B, self.GRID, self.GLANCE)
        self.assertEqual(tl_a, (self.top_a, self.left_a))
        self.assertEqual(tl_b, (self.top_b, self.left_b))
        self.assertNotEqual(tl_a, tl_b, "the two classes' window ORIGINS must differ (that is the whole plant)")
        self.assertTrue(np.array_equal(win_a, win_b), "the two classes' glance windows must be byte-identical")

        genome = parse_genome(SEAM_GENOME_TEXT)
        f_a = retina_fn(gaze_module.ink_border(win_a), genome.retina)
        f_b = retina_fn(gaze_module.ink_border(win_b), genome.retina)
        self.assertTrue(np.array_equal(f_a, f_b), "the 112-vectors must be identical: chance is a fact")

    def _content_routed_fixations(self, rgb, F, mode="surprise", pic_id=""):
        """Stands in for Alpha 2's saliency organ (sha-pinned, out of scope here): route to whichever
        class's patch this canvas actually carries, read off the one pixel that tells them apart. Never
        reads `pic_id`/`mode` — a pure function of the picture's own content, same as a real fixation
        rule would be, just without the black-box saliency machinery in between."""
        if int(rgb[self.top_a, self.left_a, 0]) != self.BACKGROUND:
            return [self.CELL_A]
        return [self.CELL_B]

    def _run_labelled_tape(self, genome_path: Path, root: Path, n_train_per_class: int, n_query_per_class: int,
                             blind=frozenset()):
        """Publishes N_TRAIN worded canvases (word = "classa"/"classb", interleaved) then N_QUERY sight-only
        canvases (no ear row) of the SAME two byte-identical images, through the REAL Mind.consume() loop
        with `fixations` routed as above. Returns (mind, train_ids_by_word, query_ids_by_word)."""
        tape = Tape(root)
        order = []
        for i in range(n_train_per_class):
            order.append("classa"); order.append("classb")
        for i, cls_ in enumerate(order):
            moment = f"tr{i:04d}"
            tape.publish("ear", cls_.encode(), {"moment": moment, "source": "test", "word": cls_}, "txt")
            rgb = self.canvas_a if cls_ == "classa" else self.canvas_b
            tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")
        query_order = []
        for i in range(n_query_per_class):
            query_order.append("classa"); query_order.append("classb")
        for i, cls_ in enumerate(query_order):
            moment = f"q{i:04d}"
            rgb = self.canvas_a if cls_ == "classa" else self.canvas_b
            tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")

        mind = Mind(genome_path, root, blind=blind)
        with patch("genome.gaze.fixations", side_effect=self._content_routed_fixations):
            rows = list(read_tape(root))
            train_ids: Dict[str, List[int]] = {"classa": [], "classb": []}
            query_ids: Dict[str, List[int]] = {"classa": [], "classb": []}
            for r in rows:
                before = mind.episodes.n_written
                mind.consume(r)
                wrote = mind.episodes.n_written > before
                if not wrote:
                    continue
                eid = mind.episodes.n_written - 1
                meta = r.get("meta") or {}
                moment = meta.get("moment", "")
                if moment.startswith("tr"):
                    idx = int(moment[2:])
                    train_ids[order[idx]].append(eid)
                elif moment.startswith("q"):
                    idx = int(moment[1:])
                    query_ids[query_order[idx]].append(eid)
        return mind, train_ids, query_ids

    def test_b_answers_above_chance_through_the_mind_reading_where(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _write_genome(tmp, SEAM_GENOME_TEXT, "seam.genome")
        root = tmp / "run"
        mind, train_ids, query_ids = self._run_labelled_tape(genome_path, root, n_train_per_class=6, n_query_per_class=5)
        train_id_set = set(train_ids["classa"]) | set(train_ids["classb"])
        self.assertGreater(len(train_id_set), 0)

        def word_of(eid: int) -> str:
            return mind.episodes.get(eid)["word"]

        # (i) the x_s-blind ceiling, computed on the SAME store: nearest() over the identical-by-construction
        # 112-vectors ties every candidate at cosine 1.0, so the deterministic "smaller id first" tie-break
        # always returns the SAME training id regardless of the query's true class -- exactly chance on a
        # balanced query set (not "near" chance: EXACTLY, because the tie-break is deterministic).
        correct_x_s = total = 0
        for cls_, eids in query_ids.items():
            for qeid in eids:
                q = mind.episodes.get(qeid)
                cands = [(i, c) for i, c in mind.episodes.nearest(q["x_s"], mind.episodes.n_written) if i in train_id_set]
                self.assertGreater(len(cands), 0)
                pred = word_of(cands[0][0])
                total += 1
                correct_x_s += int(pred == cls_)
        self.assertEqual(correct_x_s / total, 0.5, "reading only x_s must sit at EXACTLY chance (the vectors are identical)")

        # (ii) the answer through the mind, reading `where` (Episodes.nearest_where — never x_s):
        correct_where = 0
        for cls_, eids in query_ids.items():
            for qeid in eids:
                q = mind.episodes.get(qeid)
                self.assertIsNotNone(q["where"], "the query episode must itself carry `where` (the seam, end to end)")
                cands = [(i, d) for i, d in mind.episodes.nearest_where(q["where"], mind.episodes.n_written) if i in train_id_set]
                self.assertGreater(len(cands), 0)
                pred = word_of(cands[0][0])
                correct_where += int(pred == cls_)
        self.assertEqual(correct_where / total, 1.0,
                          "a rule that reads `where` must answer ABOVE chance (here: perfectly, since where IS the class signal)")

    def test_c_blind_where_twin_sits_at_exactly_chance(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _write_genome(tmp, SEAM_GENOME_TEXT, "seam.genome")
        root = tmp / "run_blind"
        mind, train_ids, query_ids = self._run_labelled_tape(genome_path, root, n_train_per_class=6, n_query_per_class=5,
                                                                blind=frozenset({"where"}))
        train_id_set = set(train_ids["classa"]) | set(train_ids["classb"])

        # `where` was blinded: no episode -- training or query -- carries it, so nearest_where sees nothing.
        for eid in train_id_set | set(query_ids["classa"]) | set(query_ids["classb"]):
            self.assertIsNone(mind.episodes.get(eid)["where"])
        self.assertEqual(mind.episodes.nearest_where((0, 0), 5), [], "with `where` blinded there is nothing to answer from")

        # the only road left is the x_s-blind one -- exactly chance, same as the ceiling above.
        correct = total = 0
        for cls_, eids in query_ids.items():
            for qeid in eids:
                q = mind.episodes.get(qeid)
                cands = [(i, c) for i, c in mind.episodes.nearest(q["x_s"], mind.episodes.n_written) if i in train_id_set]
                pred = mind.episodes.get(cands[0][0])["word"]
                total += 1
                correct += int(pred == cls_)
        self.assertEqual(correct / total, 0.5, "the --blind where twin must sit at EXACTLY chance")


if __name__ == "__main__":
    unittest.main()
