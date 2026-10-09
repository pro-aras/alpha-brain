# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §1/§2 B4 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…): genome/brain/lives/BRAIN-LONG-5.genome is brain-long-4's launched genome with
# EXACTLY the law's §1 diff — SEED 20261201 AND the scene world's seed 20261201 (the two together, the standing
# rule); + the WORLD video line; MOUTH gains «incremental»; BRAIN hears gains « video» (hears scene maker video);
# everything else byte-identical. BRAIN-LONG-4.genome (added beside it) is BYTE-IDENTICAL to the sealed life's
# launch file (/data/dev/genome-lives/brain-long-4/GENOME.genome) — the repo's missing rung, so the comparator
# below reads repo files only (test_brain_long_3.py's own form). The pre-flight twin differs by the pre-flight's
# own three values (train 400, calibrate at 250, the DECLARED toy shelf — never the real one). The comparator is
# run on planted offenders and must see them.
"""tests/genome/test_brain_long_5.py — BRAIN-LONG-5.genome and BRAIN-LONG-5-PREFLIGHT.genome (PREREG-ALPHA-6)."""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import parse_genome

LIVES = Path(__file__).resolve().parents[2] / "genome" / "brain" / "lives"
LONG4, LONG5 = (LIVES / "BRAIN-LONG-4.genome").read_text(), (LIVES / "BRAIN-LONG-5.genome").read_text()
PRE5 = (LIVES / "BRAIN-LONG-5-PREFLIGHT.genome").read_text()

VIDEO_SHELF = "/data/dev/genome-lives/brain-long-5/world/video-shelf"
TOY_SHELF = "/data/dev/brain-runs/alpha-6/bl5-preflight-toy/video-shelf"


def code_lines(text: str):
    """Every non-comment line with its trailing comment cut off (test_brain_long_3.py's own form)."""
    out = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        out.append(line.split("#", 1)[0].rstrip())
    return out


def differing(a: str, b: str):
    """The code lines in one text and not the other, as (only in a, only in b)."""
    ca, cb = code_lines(a), code_lines(b)
    return [l for l in ca if l not in cb], [l for l in cb if l not in ca]


class Long4IsTheSealedLifesFile(unittest.TestCase):
    def test_the_repos_long_4_is_byte_identical_to_the_launched_copy(self) -> None:
        launched = Path("/data/dev/genome-lives/brain-long-4/GENOME.genome")
        if not launched.exists():                    # a tree away from the machine: the repo file alone stands
            self.skipTest("the sealed life's root is not readable here")
        self.assertEqual(LONG4, launched.read_text())


class Long5(unittest.TestCase):
    def test_it_parses_and_every_new_value_reads_back(self) -> None:
        d = parse_genome(LONG5)
        self.assertEqual(d.seed, 20261201)
        self.assertEqual(d.declared["WORLD_SCENE"]["seed"], 20261201)
        self.assertEqual(d.declared["WORLD_SCENE"]["train"], 50000)
        self.assertEqual(d.declared["WORLD_VIDEO"], {"shelf": VIDEO_SHELF, "every_s": 2, "loop": True,
                                                     "manifest": "sha256"})
        self.assertEqual(d.declared["MOUTH"], {"say": "one frame per think", "journaled": True,
                                               "brain": "phrase per canvas", "incremental": True})
        self.assertEqual(d.declared["BRAIN"]["hears"], ["scene", "maker", "video"])
        at = d.declared["BRAIN"]["calibrate_at"]
        self.assertTrue(all(x < y for x, y in zip(at, at[1:])), "the calibration list must be strictly rising")
        self.assertEqual(at[:8], [250, 500, 1000, 2000, 5000, 10000, 20000, 50000])

    def test_the_diff_against_long_4_is_exactly_the_laws_own(self) -> None:
        """PREREG-ALPHA-6 §1, every line named: the two seeds (together), the ONE new WORLD video line, the
        MOUTH's «; incremental», the BRAIN's hears gaining « video». Nothing else."""
        only4, only5 = differing(LONG4, LONG5)
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only4), ["BRAIN", "MOUTH", "SEED", "WORLD"])
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only5), ["BRAIN", "MOUTH", "SEED", "WORLD", "WORLD"])
        by4 = {l.split(None, 1)[0]: l for l in only4}
        by5seed = [l for l in only5 if l.startswith("SEED")]
        self.assertEqual(by5seed, [by4["SEED"].replace("20261101", "20261201", 1)])
        self.assertIn(by4["MOUTH"].replace("; journaled", "; journaled; incremental", 1), only5)
        world5 = sorted(l for l in only5 if l.startswith("WORLD"))
        self.assertEqual(world5[0], by4["WORLD"].replace("seed 20261101", "seed 20261201", 1))
        self.assertEqual(world5[1], f"WORLD    video shelf {VIDEO_SHELF} every 2 s; loop; manifest sha256")
        self.assertIn(by4["BRAIN"].replace("hears scene maker", "hears scene maker video", 1), only5)

    def test_everything_else_is_byte_identical(self) -> None:
        # the strongest form of the law's "everything else byte-identical": reconstruct BRAIN-LONG-5.genome
        # from brain-long-4's launched file by EXACTLY the law's §1 edits, and the two files must be byte-equal.
        a, b = LONG4.splitlines(), LONG5.splitlines()
        self.assertEqual(len(b), len(a) + 1, "exactly one line is ADDED (the WORLD video line)")
        recon = list(a)
        recon[22] = recon[22].replace("SEED     20261101", "SEED     20261201", 1)                     # SEED
        recon[85] = recon[85].replace("; journaled", "; journaled; incremental", 1)                    # MOUTH
        recon[118] = recon[118].replace("seed 20261101", "seed 20261201", 1)                           # WORLD scene
        recon.insert(119, f"WORLD    video shelf {VIDEO_SHELF} every 2 s; loop; manifest sha256")      # + WORLD video
        recon[120] = recon[120].replace("hears scene maker", "hears scene maker video", 1)             # BRAIN hears
        self.assertEqual(b, recon)

    def test_the_comparator_sees_planted_offenders(self) -> None:
        seed = LONG5.replace("SEED     20261201", "SEED     20261202", 1)
        self.assertNotEqual(seed, LONG5, "the plant must change the text")
        only_real, only_planted = differing(LONG5, seed)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertTrue(only_real[0].startswith("SEED") and only_planted[0].startswith("SEED"))
        no_video = LONG5.replace("hears scene maker video", "hears scene maker", 1)
        self.assertNotEqual(no_video, LONG5, "the plant must change the text")
        only_real, only_planted = differing(LONG5, no_video)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertIn("hears scene maker video", only_real[0])
        self.assertNotIn("hears scene maker video", only_planted[0])
        no_mouth = LONG5.replace("; journaled; incremental", "; journaled", 1)
        only_real, only_planted = differing(LONG5, no_mouth)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertIn("incremental", only_real[0])
        self.assertNotIn("incremental", only_planted[0])


class Preflight5(unittest.TestCase):
    def test_it_parses_and_reads_back(self) -> None:
        d = parse_genome(PRE5)
        self.assertEqual(d.declared["BRAIN"]["calibrate_at"], [250])
        self.assertEqual(d.declared["BRAIN"]["hears"], ["scene", "maker", "video"])
        self.assertEqual(d.declared["WORLD_SCENE"]["train"], 400)
        self.assertEqual(d.declared["WORLD_VIDEO"]["shelf"], TOY_SHELF)
        self.assertIn("incremental", d.declared["MOUTH"])

    def test_it_differs_from_long_5_by_the_preflights_own_values_only(self) -> None:
        only_long, only_pre = differing(LONG5, PRE5)
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_long), ["BRAIN", "WORLD", "WORLD"])
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_pre), ["BRAIN", "WORLD", "WORLD"])
        joined_pre, joined_long = " ".join(only_pre), " ".join(only_long)
        self.assertIn("train 400", joined_pre)
        self.assertIn("train 50000", joined_long)
        self.assertIn("calibrate at 250 and before a sitting", joined_pre)
        self.assertIn(TOY_SHELF, joined_pre)
        self.assertIn(VIDEO_SHELF, joined_long)
        self.assertIn("hears scene maker video", joined_pre)

    def test_the_toy_shelf_is_never_the_real_one(self) -> None:
        self.assertNotIn(VIDEO_SHELF, PRE5)
        self.assertNotIn("records/open-world-4", PRE5,
                         "the pre-flights run a DECLARED toy shelf, never the real one (the law §2 B5)")


if __name__ == "__main__":
    unittest.main()
