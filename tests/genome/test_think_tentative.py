# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 06:50 +0400 — G-UNIT of PREREG-CONTEMPLATE-1
# (docs/brain/muse/PREREG-CONTEMPLATE-1.md, signed 2026-10-09 23:01) for the STORE half: genome/think.py
# gains exactly the `status` field (tentative -> candidacy by an append-only superseding row), and
# tentative/candidacy rows are EXCLUDED from every trusted read by construction. Test-first (RED on
# 823c02d: file_tentative/promote/read_considered do not exist yet).
"""tests/genome/test_think_tentative.py — the muse's belief-store gates, store level (law §1.2/§1.4/§2
G-UNIT(d)):

  * a tentative filing is a plain belief row + `"status": "tentative"` (the store gains EXACTLY the
    status field; believe()/revisit/extension/clash are untouched);
  * read_beliefs (raw AND fold) excludes statused rows by default — every existing caller's bytes are
    what they were; the muse's own view is a SEPARATE reader (read_considered);
  * the standing chain never sees a tentative: believe() for a word whose only row is tentative writes
    a FRESH "belief" (never a revisit/extension of the tentative);
  * promotion is a NEW append-only row naming the line it supersedes (the store never overwrites):
    the tentative's bytes stand; the candidacy row carries "supersedes";
  * the reader inventory is pinned: every reader of the store is grepped and counted (SOLUTIONS #168:
    every "0 of N" prints the field's presence count).
"""
from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from genome import think

ROOT = Path(__file__).resolve().parents[2]


def _rows_raw(path: Path) -> list:
    """The file's OWN rows, no reader between — the presence count's source."""
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


class TestTentativeFiling(unittest.TestCase):
    def test_a_tentative_row_is_a_belief_row_plus_status(self) -> None:
        p = Path(tempfile.mkdtemp()) / "beliefs.jsonl"
        row = think.file_tentative(p, "alpha", [3, 1], [7], 42)
        self.assertEqual(row["kind"], "belief")
        self.assertEqual(row["status"], "tentative")
        self.assertEqual(row["word"], "alpha")
        self.assertEqual(row["cells"], [1, 3], "the belief row's own sorted-cell law holds")
        self.assertEqual(row["episodes"], [7])
        self.assertEqual(row["moment"], 42)
        self.assertEqual(row["clashes"], [], "a belief row carries clashes so a reader never KeyErrors")
        self.assertEqual(row["line"], 0)
        row2 = think.file_tentative(p, "you", [], [], 43)
        self.assertEqual(row2["line"], 1, "append-only: the line counter advances")
        raw = _rows_raw(p)
        self.assertEqual(len(raw), 2, "presence: two rows on disk")
        print(f"[think-tentative] filing shape ok · raw rows {len(raw)} · statused "
              f"{sum(1 for r in raw if 'status' in r)}")


class TestExclusionFromTrustedReads(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Path(tempfile.mkdtemp()) / "beliefs.jsonl"
        # a trusted chain first (the think road's own rows), then the muse's statused rows
        think.believe("circle", [1, 2], [10], 1, self.p)
        think.believe("square", [9], [11], 2, self.p)
        think.file_tentative(self.p, "alpha", [], [], 3)
        think.file_tentative(self.p, "you", [], [], 4)

    def test_read_beliefs_raw_excludes_statused(self) -> None:
        raw = _rows_raw(self.p)
        n_statused = sum(1 for r in raw if "status" in r)
        got = think.read_beliefs(self.p)
        leaks = [r for r in got if "status" in r]
        print(f"[think-tentative] raw read: {len(leaks)} of {n_statused} statused rows visible "
              f"(trusted rows present: {len(got)})")
        self.assertGreater(n_statused, 0, "presence: the fixture actually carries statused rows")
        self.assertEqual(leaks, [], "no statused row may meet a trusted read")
        self.assertEqual({r["word"] for r in got}, {"circle", "square"}, "the trusted rows are all there")

    def test_read_beliefs_fold_excludes_statused(self) -> None:
        raw = _rows_raw(self.p)
        n_statused = sum(1 for r in raw if "status" in r)
        got = think.read_beliefs(self.p, fold=True)
        leaks = [r for r in got if "status" in r]
        words = {r["word"] for r in got}
        print(f"[think-tentative] fold read: {len(leaks)} of {n_statused} statused rows visible; "
              f"folded words {sorted(words)}")
        self.assertGreater(n_statused, 0, "presence: statused rows on disk")
        self.assertEqual(leaks, [])
        self.assertNotIn("alpha", words, "the tentative word must not fold into a standing row")
        self.assertNotIn("you", words)
        self.assertEqual(words, {"circle", "square"})

    def test_the_standing_chain_never_sees_a_tentative(self) -> None:
        """believe() for the tentative's word must write a FRESH belief (rule 1: no standing), never a
        revisit/extension of the tentative — the quarantine holds inside the store's own machinery."""
        row = think.believe("alpha", [5], [99], 5, self.p)
        self.assertEqual(row["kind"], "belief", f"a tentative standing would have drawn revisit/extension: {row}")
        self.assertNotIn("status", row, "the trusted write carries no status")
        got = think.read_beliefs(self.p)
        self.assertEqual(sum(1 for r in got if r["word"] == "alpha"), 1)
        print(f"[think-tentative] standing quarantine ok · trusted rows now {len(got)}")

    def test_deduce_never_pairs_a_statused_row(self) -> None:
        claims = think.deduce(think.read_beliefs(self.p))
        text = json.dumps(claims)
        print(f"[think-tentative] deduce claims {len(claims)} over the trusted rows")
        self.assertNotIn("alpha", text)
        self.assertNotIn('"you"', text)

    def test_read_considered_is_the_muses_own_view(self) -> None:
        got = think.read_considered(self.p)
        raw = _rows_raw(self.p)
        n_statused = sum(1 for r in raw if "status" in r)
        self.assertEqual(len(got), n_statused, "the muse's reader sees exactly the statused rows")
        self.assertEqual([r["word"] for r in got], ["alpha", "you"])
        self.assertTrue(all(r["status"] == "tentative" for r in got))
        print(f"[think-tentative] read_considered: {len(got)} of {n_statused} statused rows")


class TestPromotion(unittest.TestCase):
    def test_promotion_appends_a_superseding_row_never_overwrites(self) -> None:
        p = Path(tempfile.mkdtemp()) / "beliefs.jsonl"
        t = think.file_tentative(p, "alpha", [], [], 3)
        before = p.read_bytes()
        c = think.promote(p, "alpha", of_line=int(t["line"]), cells=[], episode_ids=[], moment=9)
        after = p.read_bytes()
        self.assertTrue(after.startswith(before), "append-only: the tentative's bytes stand untouched")
        self.assertGreater(len(after), len(before))
        self.assertEqual(c["kind"], "belief")
        self.assertEqual(c["status"], "candidacy")
        self.assertEqual(c["supersedes"], int(t["line"]), "the new row names the line it supersedes")
        self.assertEqual(c["line"], int(t["line"]) + 1)
        # the trusted reads still see nothing; the muse's view resolves the supersession
        self.assertEqual(think.read_beliefs(p), [])
        got = think.read_considered(p)
        by_line = {int(r["line"]): r for r in got}
        self.assertEqual(by_line[int(t["line"])]["current"], "superseded",
                         "the tentative reads as superseded by its candidacy row")
        self.assertEqual(by_line[int(c["line"])]["current"], "candidacy")
        print(f"[think-tentative] promotion ok · rows {len(got)} · candidacy line {c['line']}")


class TestReaderInventory(unittest.TestCase):
    def test_every_reader_of_the_store_is_pinned(self) -> None:
        """G-UNIT(d)'s grep proof: the store's readers are exactly the pinned set — a NEW reader of
        beliefs.jsonl or read_beliefs anywhere in the tree fails this test until its exclusion is
        proven here (SOLUTIONS #168: counts printed, never a bare '0')."""
        pat = re.compile(r"read_beliefs|beliefs\.jsonl")
        hits = []
        for f in sorted(ROOT.rglob("*.py")):
            if any(part in (".git", "scratch", "node_modules") for part in f.parts):
                continue
            try:
                text = f.read_text(errors="replace")
            except OSError:
                continue
            n = len(pat.findall(text))
            if n:
                hits.append((str(f.relative_to(ROOT)), n))
        pinned = {
            "creature/mind.py",            # the think road's believe() call sites + the DEDUCE pool's read_beliefs(fold=True)
            "genome/think.py",             # the store itself
            "tools/verdict_g4.py",         # the offline G4 verdict (archived lives; raw read_jsonl, never a muse file)
            # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:37 +0400 — the muse bench CAUGHT by this
            # pin on its first run (the pin works): it reads the store ONLY through the two declared doors —
            # read_beliefs (the excluding reader) for its trusted-leak probe and read_considered (the muse's
            # own view); its one raw parse is the presence COUNT (counting, never trusting).
            "tools/brain/muse_bench.py",
        }
        got = {k for k, _n in hits}
        test_files = {k for k, _n in hits if k.startswith("tests/")}
        print(f"[think-tentative] reader inventory: {hits}")
        self.assertEqual(got - test_files, pinned,
                         f"the store's non-test readers moved: {sorted(got - test_files)}")
        bench = (ROOT / "tools" / "brain" / "muse_bench.py").read_text()
        self.assertIn("read_beliefs(bel)", bench, "the bench's trusted read goes through the excluding door")
        self.assertIn("read_considered", bench, "the bench's muse view goes through the muse's own door")
        # the mind's only READ of the store is the DEDUCE pool, through read_beliefs (the excluding reader)
        mind = (ROOT / "creature" / "mind.py").read_text()
        reads = [l for l in mind.splitlines() if "read_beliefs" in l]
        self.assertEqual(len(reads), 1, f"the mind reads the store in exactly one place: {reads}")
        self.assertIn("fold=True", reads[0])
        print(f"[think-tentative] mind read sites {len(reads)} · the DEDUCE pool only · fold=True")


if __name__ == "__main__":
    unittest.main()
