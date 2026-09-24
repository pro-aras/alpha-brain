# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:45 +0400 — A4L-VOICE task 7 (docs/briefs/A4L-VOICE.md): the SEAM
# tests — wherever the voice meets another organ, tested AT the seam (SOLUTIONS #235: a widened vector is a chain; a seam is tested
# at the seam). VOICE × SURPRISE · VOICE × BUDGET · VOICE × GROW · VOICE × the think thread · VOICE × the ask door and the exam.
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np

from creature import world_maker
from creature.mind import Mind
from creature.tape import Tape
from genome import machinery, voice, world
from genome.questions import build_ledgers

ROOT = Path(__file__).resolve().parents[2]
SOUND_LINES = "AREA     sound  from cochlea cos>=0.975\nMEET     sight  sound\nMEET     sound  words\n"


def _tmp_genome(text: str) -> Path:
    p = Path(tempfile.mkdtemp(prefix="voice-seam-g-")) / "g.genome"
    p.write_text(text)
    return p


def _meet_from_zero(text: str) -> str:
    import re
    return re.sub(r"STAGE\s+2\s+meet\s+moments\s+\d+\.\.", "STAGE  2 meet     moments 0..", re.sub(r"STAGE\s+1\s+senses\s+moments\s+0\.\.\d+", "STAGE  1 senses   moments 0..0", text))


def _voiced_rows(root: Path, things: List[str], n_per: int, seed: int = 5, voiced: bool = True) -> List[dict]:
    tape = Tape(root); rows: List[dict] = []

    def pub(sense, payload, meta, ext):
        r = tape.publish(sense, payload, meta, ext); rows.append(r); return r

    rng = np.random.default_rng(seed); k = 0
    for _i in range(n_per):
        for t in things:
            rgb, truth = world.render_canvas(t, rng)
            world_maker._publish_canvas(pub, root, f"w0000i{k:06d}t{k:09d}", t, rgb, truth, voice="formant" if voiced else None)
            k += 1
    return rows


def _journal(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return out


class SeamSurprise(unittest.TestCase):
    def test_a_sound_row_never_changes_a_glances_expectation_or_confirmation(self):
        """The same canvases, one mind hearing each thing's chord and one not: every eye row's residual/confirmed (and the coarse
        glance's) is identical, and so is the whole sight↔words road — the sound never reaches the expectation (a word's best
        sight cell), the gaze, or the confirmation; SLEEP (every 40 moments here) replays sight/words only."""
        text = _meet_from_zero((ROOT / "tests" / "creature" / "G5-surprise-coarse-test.genome").read_text()) + "\n" + SOUND_LINES
        g = _tmp_genome(text)
        root = Path(tempfile.mkdtemp(prefix="voice-seam-s-"))
        rows = _voiced_rows(root, ["circle", "ring", "dot", "square"], 8)
        a = Mind(g, root)
        for r in rows:
            a.consume(r)
        root_b = Path(tempfile.mkdtemp(prefix="voice-seam-s2-")); (root_b / "tape").mkdir(parents=True)
        (root_b / "tape" / "payload").symlink_to(root / "tape" / "payload")
        b = Mind(g, root_b)
        for r in rows:
            if r["sense"] != "ear-sound":
                b.consume(r)
        ja = [j for j in _journal(root) if "residual" in j]; jb = [j for j in _journal(root_b) if "residual" in j]
        self.assertGreater(len(ja), 0)
        self.assertEqual([(j["seq"], j["residual"], j["confirmed"]) for j in ja], [(j["seq"], j["residual"], j["confirmed"]) for j in jb])
        self.assertGreater(sum(1 for j in ja for c in (j["confirmed"] if isinstance(j["confirmed"], list) else [j["confirmed"]]) if c), 0,
                           "some glance was confirmed — else the seam was never exercised")
        np.testing.assert_array_equal(a.org.W, b.org.W); self.assertEqual(a.org.sight.n, b.org.sight.n)
        self.assertEqual(a.glances_confirmed, b.glances_confirmed)
        self.assertGreater(a.sleep_count, 0, "a sleep boundary crossed with sound on the tape")


class SeamBudget(unittest.TestCase):
    def test_a_sound_birth_spends_the_one_budget_and_is_counted(self):
        text = _meet_from_zero((ROOT / "genome" / "G4.genome").read_text()).replace("ARRIVAL  never-heard word", "#ARRIVAL off for this seam") + "\n" + SOUND_LINES
        g = _tmp_genome(text)
        root = Path(tempfile.mkdtemp(prefix="voice-seam-b-"))
        rows = _voiced_rows(root, ["cup", "key", "moon"], 2)
        a = Mind(g, root)
        for r in rows:
            a.consume(r)
        root_b = Path(tempfile.mkdtemp(prefix="voice-seam-b2-")); (root_b / "tape").mkdir(parents=True)
        (root_b / "tape" / "payload").symlink_to(root / "tape" / "payload")
        b = Mind(g, root_b)
        for r in rows:
            if r["sense"] != "ear-sound":
                b.consume(r)
        self.assertEqual(a.org.sound.n, 3)
        self.assertEqual(b.org.budget_left - a.org.budget_left, a.org.sound.n, "each sound birth spent ONE unit of the ONE budget")
        births = [x for j in _journal(root) for x in j.get("births", [])]
        self.assertEqual(sum(1 for x in births if x[0] == "sound"), 3, "the sound births are on the eye rows' birth lists")
        # a spent budget refuses a sound birth and counts it twice: the budget's own counter and the sound's
        text2 = text.replace("BUDGET   400 per arrival", "BUDGET   6 per arrival")
        root2 = Path(tempfile.mkdtemp(prefix="voice-seam-b3-"))
        rows2 = _voiced_rows(root2, ["cup", "key", "moon", "tree"], 1)
        c = Mind(_tmp_genome(text2), root2)
        for r in rows2:
            c.consume(r)
        self.assertGreater(c.org.c_sound["births_refused_budget_sound"], 0)
        self.assertGreaterEqual(c.org.c["births_refused_budget"], c.org.c_sound["births_refused_budget_sound"])
        from creature.body import Body
        body = Body.__new__(Body)
        body.mind = c; body._status_lock = __import__("threading").Lock(); body._mind_times = []; body.sense_restarts = {}
        body.crash = None; body.started_at = "x"
        import queue
        body.q = queue.Queue()
        st = Body._build_status(body)
        self.assertEqual(st["sound_births_refused"], c.org.c_sound["births_refused_budget_sound"])
        self.assertEqual(st["sound_born"], c.org.sound.n); self.assertEqual(st["voice_rows"], 4); self.assertEqual(st["voice_bound"], 4)


class _VoiceGenomeLife:
    """ONE short life on the rung's own genome (A4L-VOICE.genome, GROW) with the area capacities shrunk so the sound area
    crosses its capacity mid-life (4 -> 8 -> 16 -> 32) and the sound pairs grow by chunks — shared by three seams."""
    _built = None

    @classmethod
    def get(cls):
        if cls._built is not None:
            return cls._built
        # edit: Claude (Sonnet 5, ALPHA4-2 builder B3), 2026-09-23 17:1x +0400 — A42-B3 task 1: SOUND_GROW_CHUNK shrunk
        # alongside the other two so this fixture's own docstring ("the sound pairs grow by chunks") stays true of the
        # SOUND axis specifically too (17 things < the real SOUND_GROW_CHUNK=64 would never cross it otherwise).
        old_cap, old_chunk, old_sound_chunk = machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK
        machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = 4, 8, 8
        try:
            gpath = ROOT / "genome" / "ladder" / "A4L-VOICE.genome"
            things = list(world.THINGS_11) + list(world.THINGS_ARRIVAL2) + [world.THING_PLANT]
            root = Path(tempfile.mkdtemp(prefix="voice-seam-life-"))
            rows = _voiced_rows(root, things, 3)
            m = Mind(gpath, root)
            for r in rows:
                m.consume(r)
            m.close()        # the threaded think in flight lands; the snapshot is written (the ask door and the exam read it)
            twin_root = Path(tempfile.mkdtemp(prefix="voice-seam-life2-")); (twin_root / "tape").mkdir(parents=True)
            (twin_root / "tape" / "payload").symlink_to(root / "tape" / "payload")
            twin = Mind(gpath, twin_root)
            for r in rows:
                twin.consume(r)
            twin.close()
        finally:
            machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = old_cap, old_chunk, old_sound_chunk
        cls._built = (gpath, root, rows, m, twin, things)
        return cls._built


class SeamGrow(unittest.TestCase):
    def test_the_sound_area_crosses_its_capacity_and_the_hash_equals_a_from_scratch_recompute(self):
        gpath, root, rows, m, twin, things = _VoiceGenomeLife.get()
        self.assertEqual(m.org.sound.n, len(things))
        self.assertGreater(m.org.sound.nmax, 4, "the sound area grew past its initial capacity mid-life")
        self.assertGreaterEqual(m.org.sound_meets["sound-words"].W.shape[0], len(things))
        self.assertEqual(m.org.state_hash(), twin.org.state_hash(), "the same tape from scratch: the same digest")
        from genome.machinery import Organism, parse_genome
        back = Organism.load(root / "state" / "organism", parse_genome(gpath.read_text()))
        self.assertEqual(back.state_hash(), m.org.state_hash(), "the snapshot reloads to the same digest")


class SeamThink(unittest.TestCase):
    def test_the_think_never_reads_the_sound_state(self):
        """Which it is: the think thread's frozen shadow carries NO sound state (creature/think_thread.py builds sight/words/W
        only) and the think never reads one — its recall is sight↔words, and build_ledgers on the shadow still files a sound birth
        as SOUND from the births log. Thinks ran on a voiced life without a crash."""
        from creature import think_thread
        gpath, root, rows, m, twin, things = _VoiceGenomeLife.get()
        self.assertGreater(m.think_counters["thinks"], 0)
        shadow = think_thread.freeze_recall_view(m.org)
        self.assertFalse(hasattr(shadow, "sound"))
        L = build_ledgers(shadow, m.moment_word)
        self.assertEqual(len(L["sound"]), len(things))
        self.assertTrue(all(len(v) == 1 for v in L["sound"].values()))
        from genome.machinery import Organism
        self.assertEqual(Organism.recall_many(shadow, "words", [world.encode_word("circle", m.genome.ear_blank_zero)]),
                         m.org.recall_many("words", [world.encode_word("circle", m.genome.ear_blank_zero)]))


class SeamAskAndExam(unittest.TestCase):
    def test_show_still_answers_by_sight_and_the_exam_by_sound_never_moves_the_hash(self):
        from creature import ask as creature_ask
        gpath, root, rows, m, twin, things = _VoiceGenomeLife.get()
        reply = creature_ask.answer(root, "show", ["circle"])
        self.assertTrue(reply.startswith("show circle -> "), reply)
        self.assertNotIn("sound", reply)
        old = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(gpath), "--held", "3", "--check-tape", "20"]
            from tools import self_exam
            self_exam.main()
        finally:
            sys.argv = old
        exam = json.loads(sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit())[-1].read_text())
        self.assertTrue(exam["organism_hash_unchanged_by_exam"])
        self.assertIsInstance(exam["ask_sound"], dict)
        self.assertIn("V1", exam["ask_sound"]); self.assertIn("V2", exam["ask_sound"]); self.assertIn("V1b", exam["ask_sound"])
        self.assertEqual(exam["ask_sound"]["voiced"]["circle"], 3)


if __name__ == "__main__":
    unittest.main()
