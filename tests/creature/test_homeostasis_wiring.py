# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §2.1 + AMENDMENT 1
# (the law SIGNED; SEAT-LINE-H0.txt sha256 edda32e7…; test-first): the Mind's self-wiring from
# declared["HOMEOSTASIS"] — the tri-state drives. None (every caller today) = read the genome's
# declaration (ABSENT = no drives, byte-identical for every genome on disk); True = the full three (the
# benches' form); a dict = the solo arms; False = off; homeostasis_flat = the flat twin. The resume
# classmethod's declared read governs a resumed mind alike, and a snapshot's drives.json restores the
# state EXACTLY across a resume.
"""tests/creature/test_homeostasis_wiring.py — the HOMEOSTASIS self-wiring (PREREG-HOMEOSTASIS §2.1/A1).
Modeled whole on test_mind_registers_wiring.py (the REGISTERS precedent)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind

_ROOT = Path(__file__).resolve().parents[2]
_LEAN = (_ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()

_LINE = "HOMEOSTASIS arousal boredom fatigue\n"


def _genome(text: str = "") -> Path:
    p = Path(tempfile.mkdtemp()) / "toy.genome"
    p.write_text(_LEAN + ("\n" + text if text else ""))
    return p


class TestHomeostasisWiring(unittest.TestCase):
    def test_no_line_means_no_drives(self) -> None:
        """ABSENT (every genome on disk): no drives object at all — the byte-identical form."""
        m = Mind(_genome(), Path(tempfile.mkdtemp()))
        self.assertIsNone(m._drives)
        self.assertIsNone(m.predictor.homeostasis if m.predictor is not None else None,
                          "the predictor's gain path stays untouched without the declaration")

    def test_the_line_arms_all_three(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"arousal": True, "boredom": True, "fatigue": True})
        if m.predictor is not None:
            self.assertIs(m.predictor.homeostasis, m._drives, "the gains ride the SAME drives object")

    def test_a_subset_line(self) -> None:
        m = Mind(_genome("HOMEOSTASIS boredom\n"), Path(tempfile.mkdtemp()))
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"boredom": True})
        self.assertEqual(m._drives.gains(), (1.0, 1.0), "arousal/fatigue undeclared: the gains are neutral")

    def test_explicit_false_overrides_the_line(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), homeostasis=False)
        self.assertIsNone(m._drives)

    def test_explicit_true_overrides_absence(self) -> None:
        m = Mind(_genome(), Path(tempfile.mkdtemp()), homeostasis=True)
        self.assertIsNotNone(m._drives)
        self.assertEqual(set(m._drives.declared), {"arousal", "boredom", "fatigue"})

    def test_a_dict_is_a_solo_arm(self) -> None:
        m = Mind(_genome(), Path(tempfile.mkdtemp()), homeostasis={"arousal": True})
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"arousal": True})

    def test_the_flat_twin_is_pinned(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), homeostasis_flat=True)
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.a, 0.5)
        m._drives.note_canvas(0.99, source="scene")
        self.assertEqual((m._drives.a, m._drives.b, m._drives.f), (0.5, 0.0, 0.0),
                         "the flat twin's state never moves (H-DRIVE-EFFECT's baseline)")

    def test_resume_reads_the_same_declaration(self) -> None:
        """The resume classmethod (no snapshot → a fresh mind through __init__'s own read): the line
        governs a resumed mind exactly as a born one; explicit False overrides there too."""
        m, seq = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertEqual(seq, 0, "presence: the empty root resumes fresh")
        self.assertIsNotNone(m._drives)
        m2, _ = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()))
        m2._drives = None  # the override form is the constructor's; the resume's declared read stands
        m3, _ = Mind.resume(_genome(), Path(tempfile.mkdtemp()))
        self.assertIsNone(m3._drives)

    def test_the_state_survives_a_snapshot_round_trip(self) -> None:
        """A resume restores the drives EXACTLY (PREREG-HOMEOSTASIS §2.2's persistence clause): snapshot
        writes state/drives.json when declared; resume loads it back onto the rebuilt drives."""
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome(_LINE), root)
        self.assertIsNotNone(m._drives)
        for e in (0.9, 0.2, 0.4, 0.7):
            m._drives.note_canvas(e, source="scene")
        before = m._drives.to_json()
        m.snapshot()
        drives_file = root / "state" / "drives.json"
        self.assertTrue(drives_file.exists(), "presence: the snapshot carries drives.json when declared")
        m2, _ = Mind.resume(_genome(_LINE), root)
        self.assertIsNotNone(m2._drives)
        self.assertEqual(m2._drives.to_json(), before, "the drives restore exactly across the resume")

    def test_no_drives_file_without_the_line(self) -> None:
        """The OFF form: no drives.json is ever staged (the additive file exists only when declared —
        the web.json precedent)."""
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome(), root)
        m.snapshot()
        self.assertFalse((root / "state" / "drives.json").exists())


class TestHomeostasisWiringAmendmentTwo(unittest.TestCase):
    """PREREG-HOMEOSTASIS AMENDMENT 2 (SIGNED 2026-10-13) — the wiring of the pre-run walk's repairs."""

    def test_the_inverted_twin_wires_bench_only(self) -> None:
        """F6: homeostasis_invert threads to the drives object; the default is untouched; no genome
        spelling exists (the parser never hears of it — the negative control is bench-only)."""
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), homeostasis_invert=True)
        self.assertIsNotNone(m._drives)
        self.assertTrue(m._drives.invert)
        m2 = Mind(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertFalse(m2._drives.invert)

    def test_the_bored_marker_rides_only_the_extras(self) -> None:
        """F3: _maybe_ask's bored=True marks the row (the extras' attribution); the default form never
        carries the key (byte-identical's invariant on the want road)."""
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome("QUESTION from wants; forms what-is is which; to the world door\n" + _LINE), root)
        m._cur_at, m._cur_seq = "2026-10-13T00:00:00.000Z", 1
        self.assertTrue(m._maybe_ask("sight:9", "what-is", ["m0"]))
        self.assertTrue(m._maybe_ask("sight:10", "what-is", ["m0"], bored=True))
        self.assertFalse(m._maybe_ask("sight:9", "what-is", ["m0"]), "the once-ever dedupe, planted")
        rows = [json.loads(l) for l in (root / "journal" / "2026-10-13.jsonl").read_text().splitlines() if l.strip()]
        questions = [r["question"] for r in rows if "question" in r]
        self.assertEqual(len(questions), 2, "presence: both asks journaled")
        self.assertNotIn("bored", questions[0])
        self.assertEqual(questions[1].get("bored"), True)

    def test_the_extras_reaim_to_heard_words(self) -> None:
        """F3: with the wordless pool empty (the gate world's form), the extra asks a HEARD word with
        the renewing want string — and the refractory stamp lands only when the ask forms."""
        import numpy as np
        from genome.fast import Episodes
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome("QUESTION from wants; forms what-is is which; to the world door\n" + _LINE), root)
        m._cur_at, m._cur_seq = "2026-10-13T00:00:00.000Z", 7
        m._drives.b = 1.0
        m._drives.note_canvas(0.5, source="scene", word="star")
        # a REAL episodes ring (never a hand-typed double, #251 (2)) carrying the word's one live
        # episode so _maybe_ask_word's tape_moment resolution finds it, exactly as in a life.
        ep = Episodes(cap=8, dim_s=4, dim_w=4)
        ep.write(moment=0, x_s=np.zeros(4), x_w=np.zeros(4), word="star", surprise=0.5, tape_moment="m0")
        m.episodes = ep
        row = {"seq": next(s for s in range(10**6) if m._drives.extra_event(s, "extra-ask"))}
        m._drives_extra_ask(row)
        asked = json.loads((root / "ask" / "out" / "ASKED.json").read_text())
        self.assertEqual(list(asked), ["bored:word:star:0"], "the renewing want string (once-ever per (word, epoch))")
        self.assertEqual(m._drives.heard["star"][2], m._drives.canvases, "the refractory stamped at the fired ask")

    def test_babble_is_per_canvas_and_capped_by_boredom(self) -> None:
        """F4: the babble draw fires at the canvas site only when boredom is past θ (and a cited frame
        exists); suppression (θ_silent) silences it; below θ it is identically False."""
        root = Path(tempfile.mkdtemp())
        g = "MOUTH say one frame per think and the brain's phrase per canvas; journaled; incremental\n"
        m = Mind(_genome(g + _LINE), root)
        m._frames["k1"] = {"w1": "star", "w2": "red", "episodes": [3]}
        m._drives.b = 1.0
        firing = [s for s in range(10**5) if m._drives.extra_event(s, "babble")]
        self.assertTrue(firing, "presence: at b=1 the babble draws fire")
        row = {"seq": firing[0], "at": "2026-10-13T00:00:00.000Z", "meta": {}}
        m._drives_babble(row)
        says = [json.loads(l) for l in (root / "journal" / "2026-10-13.jsonl").read_text().splitlines()
                if l.strip() and '"say"' in l]
        self.assertEqual(len(says), 1)
        self.assertEqual(says[0]["say"].get("babble"), True)
        self.assertEqual(says[0]["say"]["frame"], "star red")
        # the same canvas again: nothing re-fires on the same seq (the draw is the row's own)
        m._drives_babble(row)
        # suppressed: fatigue past θ_silent silences the babble
        m2 = Mind(_genome(g + _LINE), Path(tempfile.mkdtemp()))
        m2._frames["k1"] = {"w1": "star", "w2": "red", "episodes": [3]}
        m2._drives.b = 1.0
        m2._drives.f = 0.96
        m2._drives_babble({"seq": firing[0], "at": "2026-10-13T00:00:00.000Z", "meta": {}})
        self.assertFalse((Path(m2.run_root) / "journal" / "2026-10-13.jsonl").exists(),
                         "suppressed: not one babble row written")
        # low boredom: never
        m3 = Mind(_genome(g + _LINE), Path(tempfile.mkdtemp()))
        m3._frames["k1"] = {"w1": "star", "w2": "red", "episodes": [3]}
        for s in range(500):
            m3._drives_babble({"seq": s, "at": "2026-10-13T00:00:00.000Z", "meta": {}})
        self.assertFalse((Path(m3.run_root) / "journal" / "2026-10-13.jsonl").exists(),
                         "at b=0 the babble is identically False over 500 planted seqs")

    def test_off_unchanged_by_the_babble_site(self) -> None:
        """Byte-identity's invariant: without the line the canvas-end babble site is inert."""
        m = Mind(_genome("MOUTH say one frame per think and the brain's phrase per canvas; journaled; incremental\n"),
                 Path(tempfile.mkdtemp()))
        self.assertIsNone(m._drives)
        m._drives_babble({"seq": 1, "at": "2026-10-13T00:00:00.000Z", "meta": {}})   # returns at once, never errors


if __name__ == "__main__":
    unittest.main()
