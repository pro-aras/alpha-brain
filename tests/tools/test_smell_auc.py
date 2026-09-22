# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:47 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 4
# (BODY-SENSES.md §4.5's own refusal test), run against the REAL closed life named in the brief's own words
# ("the closed folder rows of /data/dev/genome-lives/g5-seam-1/tape/*.jsonl") and the maker's real,
# read-only world/ directory -- never a synthetic fixture, since the whole point is what the ACTUAL folder
# door's recorded rows and the ACTUAL shelf of pictures say.
from __future__ import annotations

import unittest
from pathlib import Path

from tools import smell_auc

LIFE_ROOT = Path("/data/dev/genome-lives/g5-seam-1")
WORLD_ROOT = Path("/data/dev/genome/world")


@unittest.skipUnless(LIFE_ROOT.exists() and WORLD_ROOT.exists(), "the closed life / world directory are not present on this box")
class TestSmellAucOnRealClosedLife(unittest.TestCase):
    def test_most_folder_rows_match_a_real_world_file(self) -> None:
        rows = smell_auc._read_folder_eye_rows(LIFE_ROOT)
        self.assertGreater(len(rows), 0, "the brief's own life must carry folder eye rows")
        result = smell_auc.compute_auc(LIFE_ROOT, WORLD_ROOT, blind_folder_axis=False)
        self.assertGreater(result["matched"], 0, "at least some folder rows must match a real world/ file by sha12")
        print(f"smell_auc: {result['matched']}/{result['folder_eye_rows']} folder rows matched "
              f"({result['unmatched']} unmatched)")

    def test_full_and_folder_blind_auc_printed(self) -> None:
        """The brief's own instruction: print the number, never tune the vector to it. This test's only
        assertion is that the AUC is a real number in [0, 1] (or NaN when there are too few pairs) --
        whatever value it reads is a FINDING, not a pass/fail bar."""
        full = smell_auc.compute_auc(LIFE_ROOT, WORLD_ROOT, blind_folder_axis=False)
        blind = smell_auc.compute_auc(LIFE_ROOT, WORLD_ROOT, blind_folder_axis=True)
        print(f"smell channel AUC (same-folder-word vs different, by distance): "
              f"full kind+size+folder = {full['auc']:.4f} ({full['same_pairs']} same / {full['diff_pairs']} diff pairs); "
              f"folder-BLIND kind+size only = {blind['auc']:.4f} ({blind['same_pairs']} same / {blind['diff_pairs']} diff pairs)")
        for result in (full, blind):
            if result["same_pairs"] > 0 and result["diff_pairs"] > 0:
                self.assertGreaterEqual(result["auc"], 0.0)
                self.assertLessEqual(result["auc"], 1.0)

    def test_folder_blind_auc_is_not_trivially_inflated_by_the_hash_axis(self) -> None:
        """The construction argument (#217/#162): a same-word pair's FOLDER axis distance is 0 by
        construction, which can inflate the full vector's AUC without the channel separating anything on
        its own merits. This test only prints the gap; it does not bar on it (the brief's own "never tune"
        instruction)."""
        full = smell_auc.compute_auc(LIFE_ROOT, WORLD_ROOT, blind_folder_axis=False)
        blind = smell_auc.compute_auc(LIFE_ROOT, WORLD_ROOT, blind_folder_axis=True)
        print(f"full - blind AUC gap: {full['auc'] - blind['auc']:.4f} "
              "(a large gap means the folder-hash axis, not kind/size, is doing the separating)")


class TestAucFromDistancesToy(unittest.TestCase):
    """A synthetic sanity check independent of any real data: perfectly separated distances must read
    AUC 1.0, perfectly overlapping distributions must read close to 0.5, and reversed separation reads 0.0
    -- the instrument's own positive/negative controls."""

    def test_perfect_separation_reads_one(self) -> None:
        import numpy as np
        same = np.array([0.0, 0.1, 0.2])
        diff = np.array([1.0, 1.1, 1.2])
        self.assertEqual(smell_auc._auc_from_distances(same, diff), 1.0)

    def test_reversed_separation_reads_zero(self) -> None:
        import numpy as np
        same = np.array([1.0, 1.1, 1.2])
        diff = np.array([0.0, 0.1, 0.2])
        self.assertEqual(smell_auc._auc_from_distances(same, diff), 0.0)

    def test_identical_distributions_read_near_half(self) -> None:
        import numpy as np
        rng = np.random.default_rng(0)
        same = rng.normal(0, 1, 2000)
        diff = rng.normal(0, 1, 2000)
        auc = smell_auc._auc_from_distances(same, diff)
        self.assertAlmostEqual(auc, 0.5, delta=0.05)


if __name__ == "__main__":
    unittest.main()
