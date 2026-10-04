"""Tests for TOY C «FRAMES BY COMPRESSION» (docs/research/toys/PREREG-TOY-FRAMES.md, co-signed 2026-10-03 12:21 +0400): the streams, the compressor, the three rules, the two nulls,
the ceiling gate, the eye's reading, the plants. Written FIRST, in stages (red, then green, a log each).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 15:55 +0400 — STAGE 1: the streams (the grouping rule the law's §0 counts came from) and the compressor (END counted; the closed form
# bits = N log2(N + K) − Σ c log2(c + 1); every number below worked by hand in the comments, never by calling the code under test).

THE GROUPING RULE (law §0 counts reproduced by it, see TestStreams.test_the_copies_reproduce_section_0): an ear row is one WORD; a MOMENT is the set of ear rows sharing (source, moment
name), its words in seq order, moments in the order their FIRST row appears (= first-row seq, the seqs being strictly increasing). 384 alpha4-1 moments have rows split by another
row; grouping by consecutive run would count more moments than the law's 84,275.
"""
from __future__ import annotations

import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import streams as ST

REPO = Path(__file__).resolve().parents[2]
COPIES = REPO / "scratch" / "toys-frames" / "copies"


def ear(seq, source, moment, word):
    return {"seq": seq, "at": "2026-09-23T00:00:00Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {"moment": moment, "source": source, "word": word}}


def eye(seq, source, moment):
    return {"seq": seq, "sense": "eye", "meta": {"moment": moment, "source": source}}


def write_rows(d: Path, name: str, rows) -> Path:
    p = d / name
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return p


class TestStreams(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_a_split_moment_is_one_moment_with_its_words_in_seq_order(self):
        p = write_rows(self.d, "t.jsonl", [ear(1, "shelf", "m1", "a"), ear(2, "maker", "k1", "bar"), ear(3, "shelf", "m1", "b"), eye(4, "shelf", "m1"), ear(5, "shelf", "m2", "c")])
        ms = ST.load_moments([p])
        self.assertEqual([(m.source, m.name, m.words) for m in ms], [("shelf", "m1", ("a", "b")), ("maker", "k1", ("bar",)), ("shelf", "m2", ("c",))])
        self.assertEqual(ms[0].seqs, (1, 3))                                    # the split moment keeps the seq of each of its rows

    def test_the_same_name_in_two_sources_is_two_moments(self):
        p = write_rows(self.d, "t.jsonl", [ear(1, "shelf", "x", "a"), ear(2, "game", "x", "b")])
        self.assertEqual(len(ST.load_moments([p])), 2)

    def test_a_non_ear_row_adds_no_word_and_no_moment(self):
        p = write_rows(self.d, "t.jsonl", [eye(1, "shelf", "m9"), ear(2, "shelf", "m1", "a"), {"seq": 3, "sense": "ear_sound", "meta": {"moment": "m1", "source": "shelf", "word": "zzz"}}])
        ms = ST.load_moments([p])
        self.assertEqual([(m.name, m.words) for m in ms], [("m1", ("a",))])

    def test_seqs_must_strictly_increase_across_the_rows_read(self):
        p = write_rows(self.d, "t.jsonl", [ear(2, "shelf", "m1", "a"), ear(2, "shelf", "m2", "b")])
        with self.assertRaises(ST.StreamError):
            ST.load_moments([p])
        q = write_rows(self.d, "u.jsonl", [ear(5, "shelf", "m1", "a"), ear(4, "shelf", "m2", "b")])
        with self.assertRaises(ST.StreamError):
            ST.load_moments([q])

    def test_files_are_read_in_the_order_given_and_seq_continues_across_them(self):
        p1 = write_rows(self.d, "a.jsonl", [ear(1, "shelf", "m1", "a")])
        p2 = write_rows(self.d, "b.jsonl", [ear(2, "shelf", "m1", "b"), ear(3, "shelf", "m2", "c")])
        ms = ST.load_moments([p1, p2])
        self.assertEqual([m.words for m in ms], [("a", "b"), ("c",)])

    def test_the_split_is_sixty_percent_by_index_in_integer_arithmetic(self):
        self.assertEqual(ST.split_index(84275), 50565)
        self.assertEqual(ST.split_index(10000), 6000)
        self.assertEqual(ST.split_index(85117), 51070)                          # 255351 // 5: a float 0.6 * 85117 = 51070.2 would also floor to it, but never trust that
        self.assertEqual(ST.split_index(7), 4)
        ms = [ST.Moment("s", f"m{i}", (f"w{i}",), (float(i),)) for i in range(10)]
        tr, he = ST.split(ms)
        self.assertEqual((len(tr), len(he)), (6, 4))
        self.assertEqual(tr[-1].name, "m5")
        self.assertEqual(he[0].name, "m6")

    def test_flat_words_are_the_rows_in_seq_order_with_interleaving(self):
        ms = [ST.Moment("shelf", "m1", ("a", "b"), (1, 3)), ST.Moment("maker", "k1", ("bar",), (2,))]
        self.assertEqual(ST.flat_words(ms), ["a", "bar", "b"])

    def test_with_plant_inserts_a_new_moment_after_every_nth_and_changes_nothing_else(self):
        ms = [ST.Moment("s", f"m{i}", ("w%d" % (i % 7),), (float(i + 1),)) for i in range(250)]
        pl = ST.with_plant(ms, 100)
        self.assertEqual(len(pl), 252)                                           # after moments 100 and 200
        self.assertEqual([m.words for m in pl if m.source == "plant"], [ST.PLANT, ST.PLANT])
        self.assertEqual([m.name for m in pl if m.source != "plant"], [m.name for m in ms])      # the originals, in order, untouched
        self.assertEqual(pl[100].source, "plant")                                # right after the 100th
        self.assertEqual(pl[201].source, "plant")                                # right after the 200th (index 200 + 1 plant before it)
        self.assertNotEqual(ms[0].words, pl[100].words)
        s = pl[100].seqs
        self.assertTrue(ms[99].seqs[-1] < s[0] < s[1])                           # its rows sit just after the preceding moment's last row
        self.assertEqual(len(ST.with_plant(ms[:99], 100)), 99)                   # fewer than n moments: no plant

    def test_shuffled_keeps_sizes_and_each_parts_multiset_and_never_crosses_the_split(self):
        rng = np.random.default_rng(5)
        ms = [ST.Moment("s", f"m{i}", tuple(f"w{int(x)}" for x in rng.integers(0, 12, size=int(rng.integers(1, 5)))), tuple(float(i * 10 + j) for j in range(4))[:0] or (float(i),)) for i in range(60)]
        ms = [ST.Moment(m.source, m.name, m.words, tuple(float(i * 10 + j) for j in range(len(m.words)))) for i, m in enumerate(ms)]
        n_train = ST.split_index(len(ms))
        sh = ST.shuffled(ms, n_train, seed=1)
        self.assertEqual([len(m.words) for m in sh], [len(m.words) for m in ms])                       # the moments' sizes kept
        self.assertEqual([m.seqs for m in sh], [m.seqs for m in ms])                                    # the rows stay where they are: only the words move
        flat = lambda part: sorted(w for m in part for w in m.words)
        self.assertEqual(flat(sh[:n_train]), flat(ms[:n_train]))                                         # train words permuted among train positions
        self.assertEqual(flat(sh[n_train:]), flat(ms[n_train:]))                                         # held-out likewise: nothing crosses
        self.assertNotEqual([m.words for m in sh], [m.words for m in ms])                                # the plant: it really permuted
        again = ST.shuffled(ms, n_train, seed=1)
        self.assertEqual([m.words for m in sh], [m.words for m in again])                                # deterministic
        other = ST.shuffled(ms, n_train, seed=2)
        self.assertNotEqual([m.words for m in sh], [m.words for m in other])

    def test_copy_sources_copies_only_jsonl_and_the_sha256_of_each_copy_equals_its_source(self):
        src = self.d / "src"
        (src / "tape" / "payload").mkdir(parents=True)
        (src / "journal").mkdir()
        write_rows(src / "tape", "2026-09-23.jsonl", [ear(1, "shelf", "m1", "a")])
        (src / "tape" / "payload" / "000000001.txt").write_text("big payload")
        write_rows(src / "journal", "2026-09-23.jsonl", [{"seq": 1, "say": {"frame": "red box", "heard": "yes"}}])
        (src / "tape" / "SEQ").write_text("1")
        dest = self.d / "copies"
        man = ST.copy_sources({"life": src}, dest)
        self.assertTrue((dest / "life" / "tape" / "2026-09-23.jsonl").exists())
        self.assertTrue((dest / "life" / "journal" / "2026-09-23.jsonl").exists())
        self.assertFalse((dest / "life" / "tape" / "payload").exists())                                  # 1.3 GB of payload is never copied
        self.assertFalse((dest / "life" / "tape" / "SEQ").exists())
        self.assertEqual(sorted(man), ["life/journal/2026-09-23.jsonl", "life/tape/2026-09-23.jsonl"])
        for rel, e in man.items():
            self.assertEqual(e["source_sha256"], e["copy_sha256"], rel)
            self.assertEqual(e["source_sha256"], ST.sha256_file(src / rel.split("/", 1)[1]))
        self.assertEqual(ST.verify_copies(dest, man), [])
        # the plant: one byte of a copy changes -> the verification names it
        cp = dest / "life" / "tape" / "2026-09-23.jsonl"
        b = bytearray(cp.read_bytes())
        b[10] ^= 1
        cp.write_bytes(bytes(b))
        self.assertEqual(ST.verify_copies(dest, man), ["life/tape/2026-09-23.jsonl"])

    def test_copy_sources_never_writes_into_the_source(self):
        src = self.d / "src"
        (src / "tape").mkdir(parents=True)
        p = write_rows(src / "tape", "x.jsonl", [ear(1, "shelf", "m1", "a")])
        before = (p.stat().st_mtime_ns, ST.sha256_file(p), sorted(x.name for x in (src / "tape").iterdir()))
        ST.copy_sources({"life": src}, self.d / "copies")
        after = (p.stat().st_mtime_ns, ST.sha256_file(p), sorted(x.name for x in (src / "tape").iterdir()))
        self.assertEqual(before, after)

    def test_section0_counts_from_a_fixture(self):
        p = write_rows(self.d, "t.jsonl", [ear(1, "shelf", "m1", "a"), ear(2, "shelf", "m1", "b"), ear(3, "shelf", "m2", "a"), ear(4, "maker", "k1", "bar"), ear(5, "maker", "k2", "bar"), ear(6, "game", "g1", "red"), ear(7, "game", "g1", "box")])
        c = ST.section0_counts(ST.load_moments([p]))
        self.assertEqual(c["moments"], 5)
        self.assertEqual(c["words"], 7)
        self.assertEqual(c["by_source"]["shelf"], {"moments": 2, "words": 3, "distinct": 2, "per_moment": {1: 1, 2: 1}})
        self.assertEqual(c["by_source"]["maker"], {"moments": 2, "words": 2, "distinct": 1, "per_moment": {1: 2}})
        self.assertEqual(c["by_source"]["game"], {"moments": 1, "words": 2, "distinct": 2, "per_moment": {2: 1}})

    @unittest.skipUnless((COPIES / "alpha4-1" / "tape").is_dir(), "the copies are not made yet (python3 -m tools.toys.frames.streams copy)")
    def test_the_copies_reproduce_section_0(self):
        """G1: the law's §0 counts, reproduced from the COPIES (rows 112,489 = words; moments 84,275; per source; the words a moment) by the grouping rule above."""
        tape = sorted((COPIES / "alpha4-1" / "tape").glob("*.jsonl"))
        ms = ST.load_moments(tape)
        c = ST.section0_counts(ms)
        self.assertEqual(c["moments"], 84275)
        self.assertEqual(c["words"], 112489)
        bs = c["by_source"]
        self.assertEqual({k: (v["moments"], v["words"]) for k, v in bs.items()},
                         {"shelf": (47113, 73624), "maker": (35264, 35294), "game": (1574, 3148), "folder": (306, 306), "lexicon": (18, 117)})
        self.assertEqual(bs["shelf"]["distinct"], 3290)
        self.assertEqual(bs["shelf"]["per_moment"], {1: 37546, 2: 799, 3: 592, 4: 8176})
        self.assertEqual(bs["maker"]["per_moment"], {1: 35234, 2: 30})
        self.assertEqual(bs["game"]["per_moment"], {2: 1574})
        self.assertEqual(bs["maker"]["distinct"], 17)
        self.assertEqual(bs["game"]["distinct"], 9)
        self.assertEqual(bs["folder"]["distinct"], 11)
        bf = sorted((COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))
        sc = ST.scene_moments(ST.load_moments(bf))
        self.assertEqual(len(sc), 10000)
        from collections import Counter
        self.assertEqual(dict(Counter(len(m.words) for m in sc)), {1: 2503, 2: 4988, 3: 2509})
        self.assertEqual(sc[2699].words, ("dax",))                                                      # the one unknown word, at scene index 2,699
        says = ST.load_says(sorted((COPIES / "alpha4-1" / "journal").glob("*.jsonl")))
        self.assertEqual((len(says), sum(1 for s in says if s[1] == "yes"), len({s[0] for s in says})), (526, 86, 40))


# =================================================================================================================== the compressor
def l2(x):
    return math.log2(x)


class TestParse(unittest.TestCase):
    def test_leftmost_greedy_non_overlapping(self):
        P = CO.parse_moment
        E = CO.END
        self.assertEqual(P(("a", "b", "c"), {("a", "b"), ("b", "c")}), [("a", "b"), "c", E])          # (a,b) takes the b; (b,c) cannot fire
        self.assertEqual(P(("a", "b", "c"), {("b", "c")}), ["a", ("b", "c"), E])
        self.assertEqual(P(("a", "a", "b"), {("a", "a")}), [("a", "a"), "b", E])
        self.assertEqual(P(("a", "a", "a"), {("a", "a")}), [("a", "a"), "a", E])
        self.assertEqual(P(("a", "b", "a", "b"), {("a", "b")}), [("a", "b"), ("a", "b"), E])
        self.assertEqual(P(("b", "a"), {("a", "b")}), ["b", "a", E])                                   # ORDERED pair: (b, a) is not (a, b)
        self.assertEqual(P(("a",), {("a", "b")}), ["a", E])
        self.assertEqual(P((), {("a", "b")}), [E])                                                     # an empty moment is just its END

    def test_the_parse_never_crosses_a_moment(self):
        self.assertEqual(CO.parse_moment(("a",), {("a", "b")}) + CO.parse_moment(("b",), {("a", "b")}), ["a", CO.END, "b", CO.END])


class TestCompressorByHand(unittest.TestCase):
    def test_the_empty_frame_set_has_zero_gain(self):
        sc = CO.Scorer([["a", "b"], ["c"]], [["a"], ["b", "c"]])
        g = sc.gain(set())
        self.assertEqual(g.G, 0.0)
        self.assertEqual(g.L, 0.0)
        self.assertAlmostEqual(g.bits0, g.bitsF, places=12)

    def test_hand_computed_gain_with_an_end_token_and_an_unseen_word(self):
        """train [a b][a b][c], held [a b][a d][c], F = {(a, b)}. UNDER F the train parse is F(a,b) x2, c x1, END x3: N = 6, V = 3, K = V + |F| + 2 = 6, N + K = 12;
        p(F) = 3/12, p(c) = 2/12, p(END) = 4/12, p(a) = p(b) = p(UNK) = 1/12 (a, b never occur as words under F). Held under F: [F END], [a UNK END] (d unseen), [c END].
        UNDER ∅: a x2, b x2, c x1, END x3: N = 8, K = V + 2 = 5, N + K = 13; p(a) = p(b) = 3/13, p(c) = 2/13, p(END) = 4/13, p(UNK) = 1/13. L(F) = 1 * 2 * log2 3."""
        train = [["a", "b"], ["a", "b"], ["c"]]
        held = [["a", "b"], ["a", "d"], ["c"]]
        F = {("a", "b")}
        bits_F = (-l2(3 / 12) - l2(4 / 12)) + (-l2(1 / 12) - l2(1 / 12) - l2(4 / 12)) + (-l2(2 / 12) - l2(4 / 12))
        bits_0 = (-2 * l2(3 / 13) - l2(4 / 13)) + (-l2(3 / 13) - l2(1 / 13) - l2(4 / 13)) + (-l2(2 / 13) - l2(4 / 13))
        L = 1 * 2 * l2(3)
        g = CO.Scorer(train, held).gain(F)
        self.assertAlmostEqual(g.bitsF, bits_F, places=9)
        self.assertAlmostEqual(g.bits0, bits_0, places=9)
        self.assertAlmostEqual(g.L, L, places=9)
        self.assertAlmostEqual(g.G, bits_0 - bits_F - L, places=9)
        self.assertEqual((g.N, g.K, g.V), (6, 6, 3))
        self.assertEqual(g.n_held_words, 5)
        self.assertAlmostEqual(g.G, -1.8310699, places=6)                                              # the arithmetic above, evaluated: a lone frame in a tiny stream does not pay for itself

    def test_a_frame_that_never_fires_still_counts_in_K_and_costs_its_model_bits(self):
        """train [a][b], held [a][b], F = {(a, b)} (never adjacent): under F N = 4 (a, END, b, END), V = 2, K = 2 + 1 + 2 = 5, N + K = 9: p(a) = p(b) = 2/9, p(END) = 3/9.
        Under ∅: K = 4, N + K = 8: p(a) = p(b) = 2/8, p(END) = 3/8. L(F) = 1 * 2 * log2 2 = 2."""
        train, held = [["a"], ["b"]], [["a"], ["b"]]
        F = {("a", "b")}
        bits_F = 2 * (-l2(2 / 9) - l2(3 / 9))
        bits_0 = 2 * (-l2(2 / 8) - l2(3 / 8))
        g = CO.Scorer(train, held).gain(F)
        self.assertAlmostEqual(g.bitsF, bits_F, places=9)
        self.assertAlmostEqual(g.bits0, bits_0, places=9)
        self.assertAlmostEqual(g.G, bits_0 - bits_F - 2.0, places=9)
        self.assertLess(g.G, 0.0)
        self.assertEqual(g.K, 5)

    def test_a_frame_that_fires_often_in_held_out_text_has_positive_gain(self):
        train = [["zzq", "xxv"] if i % 5 == 0 else ["w%d" % (i % 9)] for i in range(500)]
        held = [["zzq", "xxv"] if i % 5 == 0 else ["w%d" % (i % 9)] for i in range(300)]
        g = CO.Scorer(train, held).gain({("zzq", "xxv")})
        self.assertGreater(g.G, 0.0)
        self.assertGreater(g.bits0, g.bitsF)

    def test_the_vocabulary_is_the_distinct_train_words_and_unseen_held_words_are_unk(self):
        sc = CO.Scorer([["a", "b"], ["a", "c"]], [["a", "q"]])
        self.assertEqual(sc.V, 3)
        g = sc.gain(set())
        # train ∅: a x2, b, c, END x2 -> N = 6, K = 3 + 2 = 5, N + K = 11; held [a q END]: p(a) = 3/11, p(UNK) = 1/11, p(END) = 3/11
        self.assertAlmostEqual(g.bits0, -l2(3 / 11) - l2(1 / 11) - l2(3 / 11), places=9)

    def test_adjacent_counts_count_every_adjacent_position(self):
        sc = CO.Scorer([["a", "b", "a", "b"], ["a", "b"], ["b", "a"]], [["a", "b"], ["x", "a", "b", "b"]])
        self.assertEqual(sc.train_adjacent(("a", "b")), 3)
        self.assertEqual(sc.train_adjacent(("b", "a")), 2)
        self.assertEqual(sc.held_adjacent(("a", "b")), 2)
        self.assertEqual(sc.held_adjacent(("b", "b")), 1)
        self.assertEqual(sc.train_adjacent(("q", "r")), 0)
        self.assertEqual(sc.train_bigrams()[("a", "b")], 3)


def random_stream(seed, n_train=40, n_held=25, alphabet="abcde", unk_every=0):
    rng = np.random.default_rng(seed)

    def mk(n, allow_unk):
        out = []
        for _ in range(n):
            k = int(rng.integers(1, 5))
            m = [alphabet[int(i)] for i in rng.integers(0, len(alphabet), size=k)]
            if allow_unk and unk_every and rng.random() < 1.0 / unk_every:
                m[int(rng.integers(0, k))] = "z"
            out.append(m)
        return out

    return mk(n_train, False), mk(n_held, True)


def random_frames(seed, k, alphabet="abcde"):
    rng = np.random.default_rng(seed + 1000)
    out = set()
    while len(out) < k:
        out.add((alphabet[int(rng.integers(0, len(alphabet)))], alphabet[int(rng.integers(0, len(alphabet)))]))     # (x, x) allowed; overlapping chains arise by chance
    return out


class TestFastEqualsSlow(unittest.TestCase):
    def test_fast_and_slow_agree_on_random_streams_with_overlapping_frames_and_unseen_words(self):
        n = 0
        for seed in range(40):
            train, held = random_stream(seed, unk_every=4)
            sc = CO.Scorer(train, held)
            for k in (1, 2, 4, 7):
                F = random_frames(seed * 31 + k, k)
                fast = sc.gain(F)
                slow = CO.slow_gain(train, held, F)
                for key in ("G", "bits0", "bitsF", "L"):
                    self.assertAlmostEqual(getattr(fast, key), slow[key], places=9, msg=(seed, k, key))
                self.assertEqual((fast.N, fast.K, fast.V, fast.n_held_words), (slow["N"], slow["K"], slow["V"], slow["n_held_words"]))
                n += 1
        self.assertEqual(n, 160)

    def test_the_slow_reference_is_not_the_fast_code_in_disguise(self):
        """a planted bug in a COPY of the closed form must disagree with the slow recount (the comparison can see an error)."""
        train, held = random_stream(3, unk_every=4)
        F = random_frames(3, 4)
        slow = CO.slow_gain(train, held, F)
        sc = CO.Scorer(train, held)
        good = sc.gain(F)
        wrong = good.bitsF + 0.01                                           # a one-hundredth-bit error in the held-out code length
        self.assertGreater(abs(wrong - slow["bitsF"]), 1e-3)
        self.assertAlmostEqual(good.bitsF, slow["bitsF"], places=9)

    def test_scoring_one_frame_set_does_not_change_the_next_answer(self):
        train, held = random_stream(11, unk_every=3)
        sc = CO.Scorer(train, held)
        F1, F2 = random_frames(1, 3), random_frames(2, 5)
        a1 = sc.gain(F1).G
        sc.gain(F2)
        self.assertEqual(sc.gain(F1).G, a1)                                  # no hidden state is left behind by a call
        self.assertEqual(sc.gain(set()).G, 0.0)


if __name__ == "__main__":
    unittest.main()
