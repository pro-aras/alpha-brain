# edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:36 +0400 — ALPHA4-PREREG §4 AMENDED, §11 finding 1 (branch
# judge-units-0923, HELD for alpha4-2; never merged before the ladder's 22:00 cutoff). THE READINESS JUDGE's units, test-first.
# (11:45 +0400: the row builders moved to tests/creature/readiness_rows.py, shared with test_readiness_judge.py.)
#
# Every test marked RED below fails on the unamended tree (master 867e8bc) ON THE REVIEW'S OWN DEFECT
# (docs/reviews/ALPHA4-1-FIRST-HOURS-REVIEW.md §3): (a) a per-STEP reward mean over 200 acts graded against a per-EPISODE
# null; (b) an all() over every frame ever filed against a ring that forgets, and a read proxy over the 20 NEWEST heard
# words; the streak that asks for two consecutive all-true readings (three sittings deep for (b)'s read half and (c));
# (d) a PREREG path no sense reads; rows that carry booleans without their numbers (#164). The tests marked GUARD are
# controls; each says what it reads on the unamended tree.
#
# Synthetic rows carry the LANDED shapes (tests/creature/readiness_rows.py names them and where they were read). Row readers
# go through `rr.ok()`, which reads a clause's verdict from EITHER row shape, so a RED run on the old tree fails on the
# defect's READING, not on a KeyError.
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import threading
import unittest
from math import comb
from pathlib import Path
from typing import Dict, List, Optional

from creature.mind import Mind
from tests.creature import readiness_rows as rr

ROOT = Path(__file__).resolve().parents[2]
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()
PREREG = ROOT / "docs" / "ALPHA4-PREREG.md"          # __file__-relative, never a live-tree literal (#199)
BLOCK_KEYS = {
    "a": {"window", "n", "successes", "bound", "null", "ok"},
    "b": {"frames_alive", "lifts", "read_share_last2", "frames_ok", "read_ok", "ok"},
    "c": {"composite_last2", "q1_last2", "ok"},
    "d": {"answered", "right", "novel_window_n", "novel_right", "ok"},
    "e": {"hold", "ok"},
}


class _Base(unittest.TestCase):
    extra: List[str] = rr.EXTRA_LINES

    def _mind(self, extra: Optional[List[str]] = None) -> Mind:
        tmp = Path(tempfile.mkdtemp(prefix="judge-units-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        gp = tmp / "test.genome"
        gp.write_text(SKELETON_TEXT + "\n" + "\n".join(extra if extra is not None else self.extra) + "\n")
        root = tmp / "run"
        root.mkdir(parents=True)
        self._genome_path, self._root = gp, root
        return Mind(gp, root)

    @staticmethod
    def _feed(mind: Mind, rows: List[Dict[str, object]]) -> None:
        for r in rows:
            mind.consume(r)

    def _readiness_rows(self, root: Path) -> List[Dict[str, object]]:
        return [r for r in rr.journal(root) if "readiness" in r]


# ------------------------------------------------------------------ (a) per EPISODE, against the null's band
class TestAPerEpisode(_Base):
    def test_the_bound_is_computed_from_the_null_never_typed(self) -> None:
        """RED (absent on the old tree). The smallest k with P(Binomial(N, 0.29) >= k) <= 0.05: 10 at N = 20 (P = 0.0385;
        9 gives 0.0948), 6 at N = 10 — computed here independently of the mind's own function, then compared."""
        from creature import mind as mind_mod
        bound = getattr(mind_mod, "binomial_bound")
        tail = lambda n, p, k: sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))
        self.assertEqual(bound(20, 0.29, 0.05), 10)
        self.assertEqual(bound(10, 0.29, 0.05), 6)
        self.assertLessEqual(tail(20, 0.29, 10), 0.05)
        self.assertGreater(tail(20, 0.29, 9), 0.05)
        self.assertEqual((mind_mod.READY_A_WINDOW, mind_mod.READY_A_NULL, mind_mod.READY_A_BOUND), (20, 0.29, 10))

    def test_ten_of_twenty_opens_a_per_episode_where_the_per_act_mean_never_could(self) -> None:
        """RED on the review's defect: 10 successful episodes of the last 20 is the bound exactly; the unamended clause (a)
        reads the SAME history's per-step mean over its last 200 acts (≈ 0.01) against 0.35 and says False."""
        clk = rr.Clock()
        mind = self._mind()
        rows = rr.episodes(clk, "SF" * 10)
        self._feed(mind, rows)
        self.assertLess(rr.per_act_mean_last_200(rows), 0.35, "the history must be one the per-act clause could never pass")
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertIs(rr.ok(r, "a"), True, f"10 of the last 20 episodes succeeded (the bound is 10); (a) read {r['a']!r}")
        self.assertEqual({k: r["a"][k] for k in ("window", "n", "successes", "bound", "null")},
                         {"window": 20, "n": 20, "successes": 10, "bound": 10, "null": 0.29})

    def test_five_of_twenty_reads_false_under_both(self) -> None:
        """GUARD (passes on both trees): 5 of 20 is under the band and the per-act mean is under 0.35."""
        clk = rr.Clock()
        mind = self._mind()
        rows = rr.episodes(clk, "SFFF" * 5)
        self._feed(mind, rows)
        self.assertLess(rr.per_act_mean_last_200(rows), 0.35)
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertIs(rr.ok(r, "a"), False)

    def test_nine_of_twenty_is_inside_the_null_band(self) -> None:
        """GUARD (passes on both trees): one success under the bound reads False — P(X >= 9 | 0.29) = 0.095 > 0.05."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "S" * 9 + "F" * 11))
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        self.assertIs(rr.ok(self._readiness_rows(self._root)[-1]["readiness"], "a"), False)

    def test_the_window_must_be_full(self) -> None:
        """19 completed episodes, every one a success: not 20 — False, and n says 19."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "S" * 19))
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertIs(rr.ok(r, "a"), False)
        self.assertEqual((r["a"]["n"], r["a"]["successes"]), (19, 19))

    def test_the_window_holds_the_last_twenty_only(self) -> None:
        """Twelve successes long ago, then twenty failures: the window is the last 20 completed episodes — 0 successes."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "S" * 12 + "F" * 20))
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertEqual((r["a"]["n"], r["a"]["successes"], r["a"]["ok"]), (20, 0, False))

    def test_an_unfinished_episode_never_counts(self) -> None:
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "S" * 19))
        self._feed(mind, rr.episode(clk, success=True, finish=False, steps=5))     # in progress: no terminal row yet
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertEqual((r["a"]["n"], r["a"]["ok"]), (19, False))

    def test_schedule_chosen_episodes_never_count(self) -> None:
        """Only the MIND's acts are the creature's (the same gate as the act-mismatch check): 20 successful episodes the
        worker's own schedule chose read n = 0."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "S" * 20, chosen_by="schedule"))
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertEqual((r["a"]["n"], r["a"]["ok"]), (0, False))

    def test_a_republished_terminal_row_is_one_episode(self) -> None:
        """A sense restart between a publish and its cursor write re-publishes that step (creature/senses/game.py, #230's
        cursor law): the same terminal row twice is ONE completed episode, never two."""
        clk = rr.Clock()
        mind = self._mind()
        rows = rr.episodes(clk, "SSSS")
        dup = json.loads(json.dumps(rows[-1]))
        dup["seq"] = clk.next_seq()
        dup["at"] = rr.at(dup["seq"])
        self._feed(mind, rows + [dup])
        mind.consume(rr.sit(clk, 0.5, 0.5, None))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertEqual((r["a"]["n"], r["a"]["successes"]), (4, 4))


# ------------------------------------------------------------------ (b) frames within the ring; the read sample
class TestBFramesAndTheReadSample(_Base):
    SMALL_RING = [l if not l.startswith("FAST") else "FAST     episodes 50 keys sight words surprise" for l in rr.EXTRA_LINES]

    def test_a_frame_whose_evidence_left_the_ring_no_longer_blocks(self) -> None:
        """RED on the review's defect: THINK filed «old|pair» while its evidence was in FAST; the ring (50 here, 20,000 in
        the life) has since evicted every one of its episodes. Three frames are alive now with lift ≈ 3. The unamended
        clause asked all() over every frame ever filed, so the evicted one blocked (b) for the rest of the life."""
        clk = rr.Clock()
        mind = self._mind(self.SMALL_RING)
        rr.write_pairs(mind, [("old", "pair", 10), ("red", "ball", 17), ("blue", "key", 17), ("green", "box", 17)])
        from genome.sentence import find_frames
        alive = {f"{r['w1']}|{r['w2']}" for r in find_frames(mind.episodes)}
        self.assertEqual(alive, {"red|ball", "blue|key", "green|box"}, "premise: the old frame's evidence has left the ring")
        for key in ("old|pair", "red|ball", "blue|key", "green|box"):       # what THINK had filed (it never un-files)
            w1, w2 = key.split("|")
            mind._frames[key] = {"w1": w1, "w2": w2, "episodes": []}
        mind.consume(rr.sit(clk, 0.5, 0.5, 0.7))
        mind.consume(rr.sit(clk, 0.5, 0.5, 0.7))                              # the read half holds on both sittings
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertIs(rr.ok(r, "b"), True, f"three frames are alive in the ring; (b) read {r['b']!r}")
        self.assertEqual(r["b"]["frames_alive"], 3)
        self.assertEqual({x["frame"] for x in r["b"]["lifts"]}, {"red|ball", "blue|key", "green|box"})
        self.assertTrue(all(x["lift"] >= 2.0 for x in r["b"]["lifts"]))

    def test_two_frames_alive_block(self) -> None:
        """GUARD (passes on both trees): only two frames alive in the ring (the third's evidence evicted) — frames_ok False,
        the read half fine. Ten one-off noise instants keep the two survivors' lift at 2.5 (two equal pairs ALONE have lift
        exactly 2.0, which find_frames' strict `count > 2.0 * expected` does not return)."""
        clk = rr.Clock()
        mind = self._mind(self.SMALL_RING)
        noise = [(f"x{i}", f"y{i}", 1) for i in range(10)]
        rr.write_pairs(mind, [("green", "box", 25), ("red", "ball", 20), ("blue", "key", 20)] + noise)   # green|box evicted
        mind.consume(rr.sit(clk, 0.5, 0.5, 0.7))
        mind.consume(rr.sit(clk, 0.5, 0.5, 0.7))
        r = self._readiness_rows(self._root)[-1]["readiness"]
        self.assertIs(rr.ok(r, "b"), False)
        if isinstance(r["b"], dict):
            self.assertEqual((r["b"]["frames_alive"], r["b"]["frames_ok"], r["b"]["read_ok"]), (2, False, True))

    def test_the_read_sample_is_seeded_over_all_heard_words(self) -> None:
        """RED (absent on the old tree, which rendered heard[-20:], the 20 NEWEST, least-exposed words). The sample is
        deterministic, drawn over ALL of read/HEARD.json, in first-heard order, and covers the oldest words; fewer heard
        words than asked reads [] (the share then reads None and (b) fails closed)."""
        from tools import self_exam
        heard = [f"w{i:04d}" for i in range(600)]
        s1 = self_exam.read_sample(heard, 50, 20260923)
        s2 = self_exam.read_sample(list(heard), 50, 20260923)
        self.assertEqual(s1, s2, "a fixed seed over the same heard list must give the same sample")
        self.assertEqual(len(s1), 50)
        self.assertEqual(len(set(s1)), 50)
        self.assertTrue(set(s1) <= set(heard))
        self.assertEqual(s1, sorted(s1, key=heard.index), "first-heard order")
        self.assertNotEqual(s1, heard[-50:])
        self.assertGreaterEqual(sum(1 for w in s1 if heard.index(w) < 300), 10, "the oldest half must be sampled")
        self.assertEqual(self_exam.read_sample(heard[:49], 50, 20260923), [])
        self.assertNotEqual(self_exam.read_sample(heard, 50, 1), s1, "the seed is a real parameter")

    def test_the_sitter_asks_for_fifty_seeded_words_not_the_newest_twenty(self) -> None:
        """RED on the review's defect: the exam duty's own argv (creature/exam.py:run_exam) — «--read-words 50
        --read-seed 20260923», never «--read-words 20»."""
        from creature import exam as exam_mod
        from tools import self_exam
        seen: List[List[str]] = []
        root = Path(tempfile.mkdtemp(prefix="judge-units-sitter-"))
        self.addCleanup(shutil.rmtree, root, True)

        def fake_main() -> int:
            seen.append(list(sys.argv))
            (root / "exam").mkdir(exist_ok=True)
            (root / "exam" / "2026-09-23T000000Z.json").write_text(json.dumps({"ask_seen_words": {}}))
            return 0

        real = self_exam.main
        self_exam.main = fake_main
        try:
            exam_mod.run_exam(root, ROOT / "genome" / "ALPHA4.genome")
        finally:
            self_exam.main = real
        argv = seen[0]
        self.assertEqual(argv[argv.index("--read-words") + 1], "50", argv)
        self.assertIn("--read-seed", argv)
        self.assertEqual(argv[argv.index("--read-seed") + 1], "20260923", argv)


# ------------------------------------------------------------------ (d) the path the sense reads, and the law's text
class TestDThePath(_Base):
    def test_the_grade_sense_reads_ask_graded_id_json(self) -> None:
        """GUARD (passes on both trees): the sense publishes a grade from `$ROOT/ask/graded/<id>.json` — the path §4 must
        name."""
        from creature.senses import grade
        root = Path(tempfile.mkdtemp(prefix="judge-units-grade-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / "ask" / "graded").mkdir(parents=True)
        (root / "ask" / "graded" / "q-7.json").write_text(json.dumps({"id": "q-7", "right": True, "novel": True}))
        got: List[tuple] = []
        stop = threading.Event()

        def publish(sense, payload, meta, ext):
            got.append((sense, dict(meta)))
            stop.set()
            return {"seq": len(got)}

        th = threading.Thread(target=grade.sense, args=(publish, stop, root), kwargs={"period": 0.05}, daemon=True)
        th.start()
        th.join(timeout=10.0)
        stop.set()
        th.join(timeout=2.0)
        self.assertEqual([(s, m["id"], m["right"], m["novel"]) for s, m in got], [("grade", "q-7", True, True)])

    def test_prereg_section_4_names_the_path_the_sense_reads(self) -> None:
        """RED on the review's defect: §4 named a `.jsonl` ledger no sense reads — a seat following the law's letter grades
        into nothing. The amended text keeps the old words struck through (~~…~~) and names the real path."""
        text = PREREG.read_text()
        start = text.index("## 4 ·")
        end = text.index("\n## ", start + 1)
        live = "".join(part for i, part in enumerate(text[start:end].split("~~")) if i % 2 == 0)   # struck spans removed
        self.assertIn("ask/graded/<id>.json", live)
        self.assertNotIn("graded.jsonl", live, "the old path may stay only inside a strike-through")


# ------------------------------------------------------------------ the numbers on every row (#164)
class TestNumbersOnEveryRow(_Base):
    def test_every_readiness_row_carries_its_numbers(self) -> None:
        """RED on the review's defect: the 23 live rows carried booleans only. Every row now carries each clause's numbers
        beside its verdict, on every branch (the first sitting included, when (c) has one reading)."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, rr.episodes(clk, "SFF"))
        self._feed(mind, [rr.grade(clk, "g0", True, False), rr.grade(clk, "n0", False, True), rr.hold(clk, False)])
        self._feed(mind, [rr.sit(clk, 0.97, 0.93, 0.7), rr.sit(clk, 0.99, 0.96, 0.5), rr.sit(clk, 0.98, 0.95, None)])
        rows = self._readiness_rows(self._root)
        self.assertEqual(len(rows), 3)
        for row in rows:
            rd = row["readiness"]
            self.assertEqual(set(rd), set(BLOCK_KEYS), rd)
            for k, keys in BLOCK_KEYS.items():
                self.assertIsInstance(rd[k], dict, f"({k}) must be a block with its numbers, not {rd[k]!r}")
                self.assertEqual(set(rd[k]), keys, f"({k}) keys")
                self.assertIsInstance(rd[k]["ok"], bool)
        first, last = rows[0]["readiness"], rows[-1]["readiness"]
        self.assertEqual((first["c"]["q1_last2"], first["c"]["composite_last2"]), ([0.97], [0.93]))
        self.assertEqual((last["a"]["n"], last["a"]["successes"], last["a"]["bound"]), (3, 1, 10))
        self.assertEqual((last["c"]["q1_last2"], last["c"]["composite_last2"]), ([0.99, 0.98], [0.96, 0.95]))
        self.assertEqual(last["b"]["read_share_last2"], [0.5, None])
        self.assertEqual((last["d"]["answered"], last["d"]["right"], last["d"]["novel_window_n"], last["d"]["novel_right"]),
                         (2, 1, 1, 0))
        self.assertEqual((last["e"]["hold"], last["e"]["ok"]), (False, True))


# ------------------------------------------------------------------ the streak, defined once
def _passing_history(clk: rr.Clock, mind: Mind) -> List[Dict[str, object]]:
    """Every clause met, on BOTH trees, except what the sittings themselves bring ((c) and (b)'s read half need two): 200
    one-step successful episodes — the per-step mean 0.986 clears even the unamended per-act bar, so on the old tree the
    old (a) is NOT what keeps the door shut, the streak is; (d) exactly; no hold; three frames alive in the ring AND filed
    (the unamended (b) read the filed set). Returns the rows to feed (the frames are written into the ring directly)."""
    rows = rr.episodes(clk, "S" * 200, success_len=1)
    assert rr.per_act_mean_last_200(rows) >= 0.35
    rows += rr.grades_passing(clk)
    rows += [rr.hold(clk, False)]
    rr.write_pairs(mind, [("red", "ball", 10), ("blue", "key", 10), ("green", "box", 10)])
    for key in ("red|ball", "blue|key", "green|box"):
        w1, w2 = key.split("|")
        mind._frames[key] = {"w1": w1, "w2": w2, "episodes": []}
    return rows


class TestOneReadingOpensTheDoor(_Base):
    def test_the_door_opens_on_the_first_reading_where_all_five_hold(self) -> None:
        """RED on the review's defect: the unamended streak asked two CONSECUTIVE all-true readings, and (b)'s read half and
        (c) each already span the last two sittings — three sittings deep. The door now opens on the first reading whose
        five clauses all hold (here: the second sitting, the first at which (c) has its two readings), and the stage event
        carries the same block, every verdict read by its "ok" key (never a dict's truthiness). The history passes every
        other clause on both trees (_passing_history), so on the old tree the streak alone keeps the door shut."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, _passing_history(clk, mind))
        mind.consume(rr.sit(clk, 0.99, 0.97, 0.7))
        self.assertLess(mind.stage, 4, "(c) holds on one sitting only — no door yet")
        second = rr.sit(clk, 0.99, 0.97, 0.7)
        mind.consume(second)
        self.assertEqual(mind.stage, 4, "all five clauses hold on this ONE reading — the door opens now")
        journal = rr.journal(self._root)
        events = [r for r in journal if r.get("event") == "stage"]
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual((ev["stage"], ev["seq"]), (4, second["seq"]))
        reading = [r for r in journal if "readiness" in r and r["seq"] == second["seq"]][0]["readiness"]
        self.assertEqual(ev["readings"], reading, "the stage event carries the reading that opened the door, whole")
        for k in "abcde":
            self.assertIsInstance(ev["readings"][k], dict)
            self.assertIs(ev["readings"][k]["ok"], True, k)
        self.assertEqual((ev["readings"]["a"]["successes"], ev["readings"]["b"]["frames_alive"],
                          ev["readings"]["d"]["answered"]), (20, 3, 20))

    def test_once_open_never_undone_and_never_reopened(self) -> None:
        """RED on the old tree by the same streak (its door is not yet open after two sittings); then the law it pins: a
        later bad reading never closes the door and a later good one never writes a second event."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, _passing_history(clk, mind))
        self._feed(mind, [rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)])
        self.assertEqual(mind.stage, 4)
        self._feed(mind, [rr.hold(clk, True), rr.sit(clk, 0.1, 0.1, 0.1), rr.hold(clk, False),
                          rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)])
        self.assertEqual(mind.stage, 4)
        self.assertEqual(len([r for r in rr.journal(self._root) if r.get("event") == "stage"]), 1)


# ------------------------------------------------------------------ purity: a function of tape facts and own counters
def _full_history(clk: rr.Clock, mind: Mind) -> List[Dict[str, object]]:
    rows = _passing_history(clk, mind)
    rows += [rr.sit(clk, 0.97, 0.94, 0.6), rr.sit(clk, 0.99, 0.96, 0.55)]
    rows += rr.episodes(clk, "SSSS")
    rows += [rr.grade(clk, "late", True, True), rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)]
    return rows


class TestPurity(_Base):
    def test_two_minds_given_the_same_rows_write_the_same_readiness_rows(self) -> None:
        """GUARD (not a review defect): the judge is a pure function of tape facts and the mind's own counters — two fresh
        minds, one tape, the same rows. The count (four readings + the one stage event) needs the AMENDED judge: the old one's
        streak would open the door one sitting after this history ends, so on the old tree only the count fails, never the
        equality."""
        clk_a, clk_b = rr.Clock(), rr.Clock()
        mind_a = self._mind()
        root_a = self._root
        rows_a = _full_history(clk_a, mind_a)
        self._feed(mind_a, rows_a)
        mind_b = self._mind()
        root_b = self._root
        rows_b = _full_history(clk_b, mind_b)
        self.assertEqual(rows_a, rows_b)
        self._feed(mind_b, rows_b)
        ja = [json.dumps(r, sort_keys=True) for r in rr.journal(root_a) if "readiness" in r or r.get("event") == "stage"]
        jb = [json.dumps(r, sort_keys=True) for r in rr.journal(root_b) if "readiness" in r or r.get("event") == "stage"]
        self.assertEqual(len(ja), 5)
        self.assertEqual(ja, jb)

    def test_reading_twice_changes_nothing(self) -> None:
        """GUARD (passes on both trees): reading the judge moves no counter and returns the same reading."""
        clk = rr.Clock()
        mind = self._mind()
        self._feed(mind, _full_history(clk, mind))
        state = lambda: json.dumps([mind.stage, mind._grades_total, mind._grades_right, list(mind._novel_grades),
                                    mind._hold_active, [list(x) for x in mind._sit_readings],
                                    int(mind.episodes.n_written), sorted(mind._frames)], default=str)
        before = state()
        r1 = mind._readiness_readings()
        r2 = mind._readiness_readings()
        self.assertEqual(json.dumps(r1, sort_keys=True, default=str), json.dumps(r2, sort_keys=True, default=str))
        self.assertEqual(state(), before)

    def test_a_resume_mid_history_reads_the_rows_an_unbroken_mind_reads(self) -> None:
        """GUARD: the judge's own window (the last 20 completed episodes) survives a snapshot and a resume — a mind
        stopped half way and resumed writes the same readiness rows for the second half as one that never stopped.
        RED on the unamended tree for a defect the review did not name (found by this guard, 2026-09-23 11:40 +0400): the
        old (b) read the FILED frames (`Mind._frames`), which no snapshot persists — a resumed mind, or an EVOLVE twin
        restored from a checkpoint, read (b)'s frame half against an empty set until THINK filed again. The amended (b)
        reads only the FAST ring, which the snapshot does persist (state/episodes.npz)."""
        clk = rr.Clock()
        mind_a = self._mind()
        root_a = self._root
        rows = _full_history(clk, mind_a)
        self._feed(mind_a, rows)
        cut = [i for i, r in enumerate(rows) if r["sense"] == "sit"][1] + 1       # just after the second sitting
        mind_b = self._mind()
        root_b, gp_b = self._root, self._genome_path
        rr.write_pairs(mind_b, [("red", "ball", 10), ("blue", "key", 10), ("green", "box", 10)])
        for key in ("red|ball", "blue|key", "green|box"):                         # filed, as in mind_a (the old (b) read these)
            w1, w2 = key.split("|")
            mind_b._frames[key] = {"w1": w1, "w2": w2, "episodes": []}
        self._feed(mind_b, rows[:cut])
        mind_b.snapshot()
        resumed, _last = Mind.resume(gp_b, root_b)
        self._feed(resumed, rows[cut:])
        tail_seqs = {r["seq"] for r in rows[cut:]}
        ra = [r["readiness"] for r in rr.journal(root_a) if "readiness" in r and r["seq"] in tail_seqs]
        rb = [r["readiness"] for r in rr.journal(root_b) if "readiness" in r and r["seq"] in tail_seqs]
        self.assertEqual(len(ra), 2)
        self.assertEqual(ra, rb)


if __name__ == "__main__":
    unittest.main()
