# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:37 +0400 — A4L-VOICE tasks 1–4 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3): the drawn world speaks, the mind binds the chord at its canvas, and the toy lives read the
# exam by sound. The pinned positive control of the whole road (the brief's own words: «a blind-ear toy life whose ask_sound
# V1 reads ≥ 0.8»), the maker's row order and shape, the FAST-only roads that must stay, and the blind twins.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np

from creature import world_maker
from creature.mind import Mind
from creature.tape import Tape
from genome import run_g1, voice, world
from genome.machinery import parse_genome
from genome.questions import ask_sound, build_ledgers

ROOT = Path(__file__).resolve().parents[2]
G4 = ROOT / "genome" / "G4.genome"
SOUND_LINES = "AREA     sound  from cochlea cos>=0.975\nMEET     sight  sound\nMEET     sound  words\n"
THINGS = ["circle", "square", "triangle", "cross"]


def _genome(sound: bool = True, fast_sound: bool = False) -> Path:
    """G4.genome with the meeting from moment 0 (a toy life is shorter than G4's 200-moment senses stage)."""
    t = G4.read_text()
    t = t.replace("STAGE    1 senses   moments 0..200", "STAGE    1 senses   moments 0..0").replace("STAGE    2 meet     moments 200..", "STAGE    2 meet     moments 0..")
    assert "moments 0.." in t
    if fast_sound:
        t = t.replace("FAST     episodes 20000 keys sight words surprise", "FAST     episodes 20000 keys sight words surprise sound")
    p = Path(tempfile.mkdtemp(prefix="voice-g-")) / "g.genome"
    p.write_text(t + ("\n" + SOUND_LINES if sound else ""))
    return p


def _voiced_tape(root: Path, n_per: int = 10, seed: int = 11, voice_kind: str = "formant") -> List[dict]:
    """The maker's own publish road (world_maker._publish_canvas) onto a real Tape: ear, ear-sound, eye per canvas."""
    tape = Tape(root)
    rows: List[dict] = []

    def pub(sense, payload, meta, ext):
        r = tape.publish(sense, payload, meta, ext)
        rows.append(r)
        return r

    rng = np.random.default_rng(seed)
    k = 0
    for i in range(n_per):
        for t in THINGS:
            rgb, truth = world.render_canvas(t, rng)
            world_maker._publish_canvas(pub, root, f"w0000i{k:06d}t{k:09d}", t, rgb, truth, voice=voice_kind)
            k += 1
    return rows


def _journal(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return out


def _held(genome_path: Path, n: int = 4):
    g = parse_genome(genome_path.read_text())
    held = world.holdout_canvas(THINGS, n, np.random.default_rng(2))
    return run_g1.feats_only(run_g1.glance_held(held, g, "surprise"))


class TestTheMakersVoice(unittest.TestCase):
    def test_ear_then_sound_then_eye_one_row_each(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="voice-maker-"))
        rows = _voiced_tape(root, n_per=1)
        self.assertEqual([r["sense"] for r in rows[:3]], ["ear", "ear-sound", "eye"])
        self.assertEqual(len(rows), 3 * len(THINGS))
        snd = rows[1]
        self.assertEqual(snd["meta"]["source"], "maker"); self.assertEqual(snd["meta"]["word"], "circle")
        self.assertEqual(snd["meta"]["moment"], rows[0]["meta"]["moment"]); self.assertEqual(snd["meta"]["moment"], rows[2]["meta"]["moment"])
        payload = np.frombuffer((root / "tape" / snd["payload"]).read_bytes(), dtype="float32")
        np.testing.assert_array_equal(payload, voice.trait("circle").astype("float32"))
        self.assertTrue((root / "truth" / "voice" / "circle.wav").exists(), "the audit wav, under truth/, never on the tape")

    def test_the_trait_is_the_ear_doors_trait_for_the_same_chord_as_a_wav(self) -> None:
        """«runs the SAME cochlea front the ear door runs»: the chord written as a wav and read by the ear door's own road
        (cochlea.read_wav_mono + analyse) gives the maker's trait byte-for-byte."""
        from genome import cochlea
        d = Path(tempfile.mkdtemp(prefix="voice-wav-"))
        (d / "x.wav").write_bytes(voice.wav_bytes("tree"))
        x = cochlea.read_wav_mono(d / "x.wav", target_rate=16000)
        ev = cochlea.analyse(x, fs=16000)["events"][0]["trait"]
        np.testing.assert_array_equal(ev.astype("float32"), voice.trait("tree").astype("float32"))

    def test_undeclared_voice_publishes_exactly_two_rows(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="voice-silent-"))
        rows = _voiced_tape(root, n_per=1, voice_kind=None)
        self.assertEqual([r["sense"] for r in rows], ["ear", "eye"] * len(THINGS))
        self.assertFalse((root / "truth" / "voice").exists())

    def test_the_body_arms_the_voice_only_when_declared(self) -> None:
        from creature import body
        root = Path(tempfile.mkdtemp())
        on = body._maker_sense_fn([], parse_genome((ROOT / "genome" / "ladder" / "A4L-VOICE.genome").read_text()).declared, root)
        off = body._maker_sense_fn([], parse_genome((ROOT / "genome" / "ladder" / "A4L-FLOOR.genome").read_text()).declared, root)
        self.assertEqual(on.keywords["voice"], "formant")
        self.assertNotIn("voice", off.keywords)


class TestTheMindBindsTheSound(unittest.TestCase):
    def test_bound_at_its_canvas_and_named_by_sound(self) -> None:
        gpath = _genome()
        root = Path(tempfile.mkdtemp(prefix="voice-mind-"))
        rows = _voiced_tape(root, n_per=30)      # 12 showings left circle/square sharing a cell in the WORD road too (Q2 answered «circle» for square, measured)
        mind = Mind(gpath, root)
        for r in rows:
            mind.consume(r)
        self.assertEqual(mind.org.sound.n, len(THINGS), "one sound cell per chord (V4's expectation)")
        self.assertEqual(mind.voice_rows, 30 * len(THINGS)); self.assertEqual(mind.voice_bound, 30 * len(THINGS))
        eye_rows = [j for j in _journal(root) if j.get("moment") and "births" in j]
        self.assertTrue(all("sound" in j for j in eye_rows), "every voiced canvas's row names the sound it bound")
        L = build_ledgers(mind.org, mind.moment_word)
        self.assertEqual(sorted(tuple(sorted(v)) for v in L["sound"].values()), sorted((t,) for t in THINGS))
        chords = {t: voice.trait_f32(t) for t in THINGS}
        h0 = mind.org.state_hash()
        a = ask_sound(mind.org, L, THINGS, _held(gpath), chords, voiced={t: 30 for t in THINGS})
        self.assertEqual(mind.org.state_hash(), h0, "the exam by sound never moves the organism")
        self.assertGreaterEqual(a["V1"]["acc"], 0.8, a["V1"]); self.assertGreaterEqual(a["V2"]["acc"], 0.8, a["V2"])
        self.assertGreaterEqual(a["V5"]["acc"], 0.8, a["V5"]); self.assertTrue(a["gradable"])

    def test_blind_ear_toy_life_still_hears_by_sound(self) -> None:
        """The brief's pinned test: under --blind ear every maker canvas is wordless for the organism, and a canvas that
        carries a SOUND must still run the sight↔sound meeting — V1 ≥ 0.8 with the words area never lit; the arrival
        clock still runs (the twin is blind to exactly one thing)."""
        gpath = _genome()
        root = Path(tempfile.mkdtemp(prefix="voice-blind-ear-"))
        rows = _voiced_tape(root, n_per=30)
        mind = Mind(gpath, root, blind=frozenset({"ear"}))
        for r in rows:
            mind.consume(r)
        self.assertEqual(mind.org.words.n, 0, "the words area never lights")
        self.assertEqual(int(mind.org.mask.sum()), 0)
        self.assertEqual(mind.org.arrivals, len(THINGS), "ARRIVAL still reads the world's clock (one per never-heard word)")
        L = build_ledgers(mind.org, mind.moment_word)
        a = ask_sound(mind.org, L, THINGS, _held(gpath), {t: voice.trait_f32(t) for t in THINGS}, voiced={t: 30 for t in THINGS})
        self.assertGreater(mind.org.c["births_error_sight"], 0, "with no word, sight cells split in the sight↔sound meeting (their one chance)")
        self.assertGreaterEqual(a["V1"]["acc"], 0.8, a["V1"])
        self.assertEqual(a["V5"]["correct"], 0, "no word cell exists to answer")

    def test_blind_sound_is_the_silent_tape(self) -> None:
        """--blind sound (V3's twin) steps every sound row over: its journal equals a mind that never saw them."""
        gpath = _genome()
        root1 = Path(tempfile.mkdtemp(prefix="voice-bs1-")); rows = _voiced_tape(root1, n_per=3)
        m1 = Mind(gpath, root1, blind=frozenset({"sound"}))
        for r in rows:
            m1.consume(r)
        root2 = Path(tempfile.mkdtemp(prefix="voice-bs2-"))
        (root2 / "tape").mkdir(parents=True); (root2 / "tape" / "payload").symlink_to(root1 / "tape" / "payload")
        m2 = Mind(gpath, root2)
        for r in rows:
            if r["sense"] != "ear-sound":
                m2.consume(r)
        self.assertEqual(_journal(root1), _journal(root2))
        self.assertEqual(m1.org.sound.n, 0)

    def test_the_ear_doors_sound_keeps_the_fast_only_road(self) -> None:
        gpath = _genome(fast_sound=True)
        root = Path(tempfile.mkdtemp(prefix="voice-door-"))
        tape = Tape(root)
        row = tape.publish("ear-sound", voice.trait("key").astype("float32").tobytes(),
                           {"moment": "a0123456789e0000", "source": "ear_sound", "file": "k.wav", "when": 0.006, "level": 0.1}, "f32")
        mind = Mind(gpath, root); mind.consume(row)
        self.assertEqual(mind.sound_episodes.n_written, 1)
        self.assertEqual(mind.pending_sound, {}); self.assertEqual(mind.voice_rows, 0)
        self.assertNotIn("pending", _journal(root)[0]["sound"])

    def test_without_the_area_the_voice_is_heard_into_fast_only(self) -> None:
        """«The voice alone» (the FLOOR genome on the rung's tape): no sound area -> the maker's rows take today's L-13
        road (the FAST sound ring), nothing is bound, nothing learned."""
        gpath = _genome(sound=False, fast_sound=True)
        root = Path(tempfile.mkdtemp(prefix="voice-alone-"))
        rows = _voiced_tape(root, n_per=2)
        mind = Mind(gpath, root)
        for r in rows:
            mind.consume(r)
        self.assertIsNone(mind.org.sound)
        self.assertEqual(mind.sound_episodes.n_written, 2 * len(THINGS))
        self.assertEqual(mind.voice_rows, 0)
        self.assertTrue(all("pending" not in j["sound"] for j in _journal(root) if "sound" in j and "births" not in j))

    def test_snapshot_resume_keeps_a_pending_sound_and_the_sound_ledger(self) -> None:
        gpath = _genome()
        root = Path(tempfile.mkdtemp(prefix="voice-resume-"))
        rows = _voiced_tape(root, n_per=2)
        mind = Mind(gpath, root)
        for r in rows[:-1]:            # the last canvas's eye row not yet consumed: its sound is pending
            mind.consume(r)
        self.assertEqual(len(mind.pending_sound), 1)
        mind.snapshot()
        led = json.loads((root / "state" / "ledger.json").read_text())
        self.assertIn("sound", led); self.assertEqual(len(led["sound_pending"]), 1)
        back, _seq = Mind.resume(gpath, root)
        self.assertEqual(set(back.pending_sound), set(mind.pending_sound))
        back.consume(rows[-1])
        self.assertEqual(back.voice_bound, mind.voice_bound + 1)


if __name__ == "__main__":
    unittest.main()
