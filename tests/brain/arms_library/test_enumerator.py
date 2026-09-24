# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:01 +0400 — arm D's DSL and enumerator: the counts per size are the design
# counter's (report §2.4, computed independently of this enumerator), the order within a size is EXACTLY
# lexicographic by the declared token ranks, every program is well-typed, and compose forms are type-checked.
from __future__ import annotations

import unittest

from brain.arms.library import dsl
from brain.arms.library.dsl import Sig
from brain.arms.library.enumerator import Enumerator, Grammar


def rank(g: Grammar, tok: str) -> int:
    for s in g.expr_syms + g.input_syms + g.ref_syms:
        if s.token == tok:
            return s.rank
    if tok == "compose":
        return dsl.RANK_COMPOSE
    if dsl.is_bvar(tok):
        return dsl.RANK_BVAR + dsl.bvar_index(tok)
    raise KeyError(tok)


class TestEnumerator(unittest.TestCase):
    def test_counts_match_the_design_counter(self):
        # docs/briefs/B1-BUILDER1-REPORT.md §2.4: G -> N programs per size 1..10 (a separate counter's numbers)
        g = Grammar([], [], [("x0", dsl.G)], dsl.N)
        en = Enumerator(g, Sig([dsl.G], dsl.N), 10)
        self.assertEqual([en.count_exact(s) for s in range(1, 11)], [0, 0, 2, 0, 9, 1, 68, 17, 676, 116])
        g2 = Grammar([], [], [("x0", dsl.G), ("cands", dsl.LG)], dsl.G)
        en2 = Enumerator(g2, Sig([dsl.G, dsl.LG], dsl.G), 10)
        self.assertEqual([en2.count_exact(s) for s in range(1, 11)], [1, 0, 2, 0, 12, 4, 87, 43, 798, 501])

    def test_order_is_size_then_lexicographic(self):
        g = Grammar([], [], [("x0", dsl.G)], dsl.N)
        en = Enumerator(g, Sig([dsl.G], dsl.N), 9)
        progs = list(en.programs())
        keys = [(dsl.size(p), [rank(g, t) for t in dsl.tokens(p)]) for p in progs]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(len(set(map(dsl.text_key, progs))), len(progs), "no program twice")
        name = ("argmaxN", ("order",), ("maxofG", ("taught", ("$0",)), ("sim", ("x0",), ("$0",))))
        self.assertIn(name, progs, "the 1-nearest-exemplar naming program is in the size-8 layer")

    def test_programs_are_well_typed_and_closed(self):
        g = Grammar([], [], [("x0", dsl.G), ("x1", dsl.N)], dsl.B)
        en = Enumerator(g, Sig([dsl.G, dsl.N], dsl.B), 8)
        for p in en.programs():
            self.assertEqual(dsl.free_bvars(p), frozenset(), dsl.render(p))

    def test_compose_is_typed_and_root_only(self):
        after = ("AFTER(G)>NAME", Sig([dsl.G], dsl.N))
        oc = ("OTHER_CASE(G;cands)>PICK", Sig([dsl.G, dsl.LG], dsl.G))
        # a CHAIN-shaped request: (G; cands) -> G
        g = Grammar([], [after, oc], [("x0", dsl.G), ("cands", dsl.LG)], dsl.G)
        en = Enumerator(g, Sig([dsl.G, dsl.LG], dsl.G), 3)
        comps = [p for p in en.programs() if p[0] == "compose"]
        self.assertIn(("compose", ("&AFTER(G)>NAME",), ("&OTHER_CASE(G;cands)>PICK",)), comps)
        self.assertNotIn(("compose", ("&OTHER_CASE(G;cands)>PICK",), ("&AFTER(G)>NAME",)), comps,
                         "OTHER_CASE then AFTER answers a NAME, not a PICK: ill-typed for this request")
        # TWO_AFTER-shaped: (G) -> N admits compose(&AFTER, &AFTER) (the bridge NAME -> GLYPH)
        g2 = Grammar([], [after], [("x0", dsl.G)], dsl.N)
        en2 = Enumerator(g2, Sig([dsl.G], dsl.N), 3)
        self.assertIn(("compose", ("&AFTER(G)>NAME",), ("&AFTER(G)>NAME",)), list(en2.programs()))
        for p in en2.programs():
            for t in dsl.tokens(p)[1:]:
                self.assertNotEqual(t, "compose", "compose never appears below the root's own compose chain"
                                    if p[0] != "compose" else "")


class TestDsl(unittest.TestCase):
    def test_shift_free_render_json(self):
        t = ("argmaxN", ("order",), ("maxofG", ("taught", ("$0",)), ("sim", ("$1",), ("$0",))))
        self.assertEqual(dsl.free_bvars(t), frozenset())
        body = t[2]
        self.assertEqual(dsl.free_bvars(body), frozenset({0}))
        self.assertEqual(dsl.shift(("sim", ("$1",), ("$0",)), -1, 1), ("sim", ("$0",), ("$0",)))
        self.assertEqual(dsl.from_json(dsl.to_json(t)), t)
        self.assertEqual(dsl.render(t), "argmaxN(order, λa. maxofG(taught(a), λb. sim(a, b)))")
        self.assertEqual(dsl.size(t), 8)

    def test_cue_keys_roundtrip(self):
        for ops, hc, kind in (((dsl.G,), False, "NAME"), ((dsl.N,), True, "PICK"), ((dsl.G, dsl.N), False, "YESNO")):
            k = dsl.cue_key("X", ops, hc, kind)
            self.assertEqual(dsl.parse_cue_key(k), ("X", ops, hc, kind))


if __name__ == "__main__":
    unittest.main()
