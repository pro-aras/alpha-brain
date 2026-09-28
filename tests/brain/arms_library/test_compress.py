# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:02 +0400 — arm D's Stitch-shaped compressor: the anti-unifier of the
# naming and pointing programs IS the resemblance operation; a filler that would capture a binder inside the
# pattern is refused; the gain arithmetic; and rewriting a corpus never changes what any program computes.
from __future__ import annotations

import unittest

import numpy as np

from brain.arms.library import compress as C
from brain.arms.library import dsl
from brain.arms.library.core import quantize_pool
from brain.arms.library.dsl import Sig
from brain.arms.library.evaluate import Batch, Data, Evaluator, LVal, Val

from .synth import SynthWorld

NAME = ("argmaxN", ("order",), ("maxofG", ("taught", ("$0",)), ("sim", ("x0",), ("$0",))))
POINT = ("argmaxG", ("cands",), ("maxofG", ("taught", ("x0",)), ("sim", ("$1",), ("$0",))))
IS = ("eq", NAME, ("x1",))


def typer():
    return C.Typer({}, {})


class TestAntiUnify(unittest.TestCase):
    def test_resemblance_is_found(self):
        pairs, holes = {}, {}
        u = NAME[2]            # maxofG(taught($0), λ. sim(x0, $0)) — $0 is bound OUTSIDE (the name)
        v = POINT[2]           # maxofG(taught(x0), λ. sim($1, $0)) — $1 is bound OUTSIDE (the candidate)
        pat = C.anti_unify(u, v, 0, pairs, holes, typer(), (dsl.N,), {"x0": dsl.G})
        self.assertEqual(pat, ("maxofG", ("taught", ("#0",)), ("sim", ("#1",), ("$0",))))
        self.assertEqual(holes, {0: dsl.N, 1: dsl.G})

    def test_capture_is_refused(self):
        # sim($0, $0) vs sim(x0, $0) under the pattern's own binder: the left filler $0 would read the
        # pattern's binder -> no admissible pattern at that position (the whole anti-unifier is refused)
        u = ("maxofG", ("taught", ("x1",)), ("sim", ("$0",), ("$0",)))
        v = ("maxofG", ("taught", ("x1",)), ("sim", ("x0",), ("$0",)))
        self.assertIsNone(C.anti_unify(u, v, 0, {}, {}, typer(), (), {"x0": dsl.G, "x1": dsl.N}))

    def test_gain_and_greedy(self):
        corpus = [C.Program("NAME", NAME, {"x0": dsl.G}),
                  C.Program("POINT", POINT, {"x0": dsl.N, "cands": dsl.LG}),
                  C.Program("IS", IS, {"x0": dsl.G, "x1": dsl.N})]
        added, new = C.compress(corpus, typer(), 0, top_k=3)
        self.assertTrue(added, "NAME, POINT and IS share structure worth a library entry")
        tok, pat, sig, g = added[0]
        self.assertGreater(g, 0)
        self.assertEqual(C.corpus_size(new) + sum(C.body_size(a[1]) for a in added),
                         C.corpus_size(corpus) - sum(a[3] for a in added),
                         "each added entry's gain is exactly the corpus shrink minus its body")


class TestRewritePreservesMeaning(unittest.TestCase):
    def test_rewritten_programs_compute_the_same(self):
        w = SynthWorld(seed=9)
        names = list("abcd")
        teach = [(i, w.render(nm)) for _ in range(2) for i, nm in enumerate(names)]
        ops = [w.render(nm) for nm in names for _ in range(2)]
        sheets = [[w.render(nm) for nm in names] for _ in ops]
        Q = quantize_pool(np.stack(w.rows))
        taught = {}
        for nid, r in teach:
            taught.setdefault(nid, []).append(r)
        data = Data(Q, [nid for nid, _ in teach], taught, len(names))
        n = len(ops)
        batch = Batch(n, {"x0": Val(False, np.array(ops), np.ones(n, dtype=bool)),
                          "x1": Val(False, np.array([k % 4 for k in range(n)]), np.ones(n, dtype=bool)),
                          "cands": LVal(False, mat=np.array(sheets), lens=np.full(n, 4), ok=np.ones(n, dtype=bool))})
        point_g = ("argmaxG", ("cands",), ("maxofG", ("taught", ("argmaxN", ("order",), ("maxofG", ("taught", ("$0",)),
                                                                                        ("sim", ("x0",), ("$0",))))),
                                           ("sim", ("$1",), ("$0",))))
        corpus = [C.Program("NAME", NAME, {"x0": dsl.G}), C.Program("IS", IS, {"x0": dsl.G, "x1": dsl.N}),
                  C.Program("OC", point_g, {"x0": dsl.G, "cands": dsl.LG})]
        t = typer()
        added, new = C.compress(corpus, t, 0, top_k=3)
        self.assertTrue(added)
        abs_table = {tok: (pat, len(sig.ins)) for tok, pat, sig, _g in added}
        for old, nw in zip(corpus, new):
            a = Evaluator(data, batch, {}, {}, memo=False).run(old.tree)
            b = Evaluator(data, batch, abs_table, {}, memo=False).run(nw.tree)
            av = np.asarray(a.v) if not a.const else np.full(n, a.v)
            bv = np.asarray(b.v) if not b.const else np.full(n, b.v)
            self.assertEqual(av.tolist(), bv.tolist(), (dsl.render(old.tree), dsl.render(nw.tree)))
            self.assertLess(dsl.size(nw.tree), dsl.size(old.tree) + 1)


if __name__ == "__main__":
    unittest.main()
