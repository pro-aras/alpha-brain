# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:29 +0400 — A4L-LANG task 4/5 (docs/A4-LADDER-PREREG.md
# §3.2 items 4-5; docs/briefs/A4L-LANG.md): the composer and its judge, pure, over hand-built stores (genome.sentence's
# own _FakeEpisode shape — `.get(eid)["words_in_instant"]`, n_written/cap). No rng, no probability, no argmax over a
# vocabulary: every choice below is the PREREG's own order, pinned level by level.
from __future__ import annotations

import unittest

from genome import chain
from genome.sentence import _FakeEpisode, find_frames


def store(instants):
    return _FakeEpisode([{"id": i, "words_in_instant": list(w)} for i, w in enumerate(instants)])


def dev_toy():
    """«it is X» 25 times (X over twelve distinct words: «is» is heard in 25 multi-word instants and followed by 12
    distinct words — a PIVOT; «it is» is a frame heard adjacent 25 times — a LINK), beside 100 filler instants that
    name no question word (so the independence bar of find_frames clears: expected(it,is) = 25*25/125 = 5 < 25/2)."""
    xs = [f"x{k}" for k in range(12)]
    inst = [["it", "is", xs[k % 12]] for k in range(25)]
    inst += [["red", "box"]] * 50 + [["blue", "ball"]] * 50
    return store(inst)


def compose_on(st, qwords, content, adj=5, distinct=10, instants=20, max_words=6):
    S = chain.store_stats(st)
    L = chain.links(st, adj=adj, stats=S)
    P = chain.pivots(st, distinct=distinct, instants=instants, stats=S)
    return chain.compose(qwords, content, L, P, S["follow"], S["adjacency"], max_words=max_words)


class TestLinksAndPivots(unittest.TestCase):
    def test_a_link_is_a_landed_frame_heard_adjacent_at_least_adj_times(self) -> None:
        st = dev_toy()
        L = {(r["w1"], r["w2"]): r for r in chain.links(st, adj=5)}
        self.assertIn(("it", "is"), L)
        self.assertEqual(L[("it", "is")]["adj_count"], 25)
        self.assertEqual(L[("it", "is")]["n_episodes"], 25)
        self.assertEqual(len(L[("it", "is")]["adj_episodes"]), 25)
        frames = {(f["w1"], f["w2"]) for f in find_frames(st)}
        self.assertTrue(set(L) <= frames, "every link is a landed frame (find_frames' own rows)")

    def test_a_frame_never_heard_adjacent_is_not_a_link(self) -> None:
        inst = [["it", "then", "is", f"x{k % 12}"] for k in range(25)] + [["red", "box"]] * 100
        st = store(inst)
        frames = {(f["w1"], f["w2"]) for f in find_frames(st)}
        self.assertIn(("it", "is"), frames, "the pair co-occurs in one instant: a frame")
        self.assertNotIn(("it", "is"), {(r["w1"], r["w2"]) for r in chain.links(st, adj=5)}, "never adjacent: never a link")

    def test_a_pivot_needs_both_its_followers_and_its_instants(self) -> None:
        P = chain.pivots(dev_toy(), distinct=10, instants=20)
        self.assertIn("is", P)
        self.assertEqual(P["is"], 12)
        self.assertNotIn("it", P, "«it» is only ever followed by «is»")
        self.assertNotIn("is", chain.pivots(dev_toy(), distinct=13, instants=20), "12 followers < 13")
        self.assertNotIn("is", chain.pivots(dev_toy(), distinct=10, instants=26), "25 instants < 26")

    def test_adjacency_reads_the_raw_heard_order_never_the_deduplicated_list(self) -> None:
        # «the dog and the cat»: «and the» IS adjacent; «and cat» is NOT (the de-duplicated list would say it is)
        S = chain.store_stats(store([["the", "dog", "and", "the", "cat"]]))
        self.assertIn(("and", "the"), S["adjacency"])
        self.assertNotIn(("and", "cat"), S["adjacency"])


class TestCompose(unittest.TestCase):
    def test_the_dev_toy_reproduces_it_is_ring(self) -> None:
        r = compose_on(dev_toy(), ["what", "is", "this"], "ring")
        self.assertEqual(r["answer"], ["it", "is", "ring"])
        self.assertEqual(r["form"], ["it", "is"])
        self.assertEqual(r["pivot"], "is")
        self.assertEqual(r["candidates_n"], 2)          # [is] and [it, is]

    def test_the_form_is_chosen_before_the_content_is_placed(self) -> None:
        a = compose_on(dev_toy(), ["what", "is", "this"], "ring")
        b = compose_on(dev_toy(), ["what", "is", "this"], "star")
        self.assertEqual(a["form"], b["form"])
        self.assertEqual(b["answer"], ["it", "is", "star"])

    def test_a_store_with_no_pivot_says_the_content_alone(self) -> None:
        st = store([["it", "is", "x"]] * 25 + [["red", "box"]] * 100)      # «is» followed by ONE word only
        r = compose_on(st, ["what", "is", "this"], "ring")
        self.assertEqual((r["answer"], r["form"], r["pivot"], r["candidates_n"]), (["ring"], [], None, 0))

    def test_no_question_word_in_any_path_says_the_content_alone(self) -> None:
        r = compose_on(dev_toy(), ["where", "now"], "ring")
        self.assertEqual(r["answer"], ["ring"])

    def test_no_content_is_no_answer_but_the_form_is_still_recorded(self) -> None:
        r = compose_on(dev_toy(), ["what", "is", "this"], None)
        self.assertIsNone(r["answer"])
        self.assertEqual(r["form"], ["it", "is"])

    def test_at_most_max_words_including_the_slot(self) -> None:
        r = compose_on(dev_toy(), ["what", "is", "this"], "ring", max_words=2)
        self.assertEqual(r["answer"], ["is", "ring"], "a path of at most max_words - 1 = 1 word")

    # ---- the CHOICE order, level by level (compose's inputs built by hand) ----
    def _c(self, q, links, pivots, adjacency=None):
        follow = {}
        for p, n in pivots.items():
            follow[p] = {f"f{p}{k}" for k in range(n)}
        adjacency = adjacency or {l: 5 for l in links}
        return chain.compose(q, "X", [{"w1": a, "w2": b} for a, b in links], pivots, follow, adjacency)

    def test_level_1_most_question_words_beats_everything(self) -> None:
        # «a b» carries two question words ending in a weak pivot; «c d e» one question word ending in the strongest pivot
        r = self._c(["a", "b", "c"], [("a", "b"), ("c", "d"), ("d", "e")], {"b": 10, "e": 99})
        self.assertEqual(r["form"], ["a", "b"])

    def test_level_2_the_pivot_with_most_followers_beats_length(self) -> None:
        r = self._c(["a"], [("a", "b"), ("a", "c"), ("c", "d")], {"b": 50, "d": 10})
        self.assertEqual(r["form"], ["a", "b"])

    def test_level_3_the_longest_beats_adjacency(self) -> None:
        # two DIFFERENT paths, one question word each, pivots tied at 20 followers: the 3-word path wins over the
        # 2-word one although the 2-word path carries more adjacency evidence (90 vs 5 + 5)
        r = self._c(["a", "b"], [("a", "p"), ("b", "c"), ("c", "r")], {"p": 20, "r": 20},
                    adjacency={("a", "p"): 90, ("b", "c"): 5, ("c", "r"): 5})
        self.assertEqual(r["form"], ["b", "c", "r"])

    def test_level_4_the_most_adjacency_beats_lexicographic(self) -> None:
        r = self._c(["q"], [("a", "q"), ("b", "q"), ("q", "p")], {"p": 20},
                    adjacency={("a", "q"): 5, ("b", "q"): 9, ("q", "p"): 5})
        self.assertEqual(r["form"], ["b", "q", "p"])

    def test_level_5_lexicographic_last(self) -> None:
        r = self._c(["q"], [("b", "q"), ("a", "q"), ("q", "p")], {"p": 20})
        self.assertEqual(r["form"], ["a", "q", "p"])

    def test_a_path_is_simple(self) -> None:
        # a cycle a->b->a must never yield a path that repeats a word
        r = self._c(["a"], [("a", "b"), ("b", "a")], {"a": 20, "b": 20})
        for p in r.get("considered", []):
            self.assertEqual(len(p), len(set(p)))
        self.assertEqual(len(r["form"]), len(set(r["form"])))

    def test_the_enumeration_is_capped_and_says_so(self) -> None:
        words = [f"w{k}" for k in range(12)]
        links = [(a, b) for a in words for b in words if a != b]
        r = chain.compose(["w0"], "X", [{"w1": a, "w2": b} for a, b in links], {w: 20 for w in words},
                          {w: set(words) for w in words}, {l: 5 for l in links}, max_words=6, cap=500)
        self.assertTrue(r["truncated"])
        self.assertLessEqual(r["paths_n"], 500)

    def test_deterministic(self) -> None:
        self.assertEqual(compose_on(dev_toy(), ["what", "is", "this"], "ring"), compose_on(dev_toy(), ["what", "is", "this"], "ring"))


class TestJudge(unittest.TestCase):
    def test_a_composed_form_passes_the_back_parse_with_its_citations(self) -> None:
        st = dev_toy()
        j = chain.judge_form(["it", "is"], st, adj=5, distinct=10, instants=20)
        self.assertTrue(j["ok"], j)
        self.assertEqual(j["links"], [["it", "is", 25, 25]])
        self.assertEqual((j["pivot_followers"], j["pivot_instants"]), (12, 25))
        self.assertEqual(len(j["cited"][0]), 25)

    def test_a_planted_non_link_fails_the_back_parse(self) -> None:
        j = chain.judge_form(["x3", "is"], dev_toy(), adj=5, distinct=10, instants=20)
        self.assertFalse(j["ok"])
        self.assertIn("link", j["reason"])

    def test_a_non_pivot_ending_fails_the_back_parse(self) -> None:
        j = chain.judge_form(["red", "box"], dev_toy(), adj=5, distinct=10, instants=20)
        self.assertFalse(j["ok"])
        self.assertIn("pivot", j["reason"])

    def test_the_empty_form_is_the_content_alone_and_passes(self) -> None:
        self.assertTrue(chain.judge_form([], dev_toy(), adj=5, distinct=10, instants=20)["ok"])


if __name__ == "__main__":
    unittest.main()
