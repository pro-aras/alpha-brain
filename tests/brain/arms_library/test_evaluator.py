# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:58 +0400 — arm D's evaluator: its semantics pinned case by case, and three
# PARITY gates over every program the enumerator yields up to size 9 (fast path == the plain loop; memo on ==
# memo off; one example at a time == the whole batch) — the answer never depends on how it was computed.
from __future__ import annotations

import unittest

import numpy as np

from brain.arms.library import dsl
from brain.arms.library.core import quantize_pool
from brain.arms.library.dsl import Sig
from brain.arms.library.enumerator import Enumerator, Grammar
from brain.arms.library.evaluate import Batch, Data, Evaluator, LVal, Val, pick_index, SIM_ONE

from .synth import SynthWorld


def world():
    w = SynthWorld(seed=5)
    names = list("abcde")
    teach = [(i, w.render(nm)) for _r in range(2) for i, nm in enumerate(names)]
    ex_rows = [w.render(nm) for nm in names for _ in range(2)]
    sheets = [[w.render(nm) for nm in names[:4]] for _ in range(len(ex_rows))]
    Q = quantize_pool(np.stack(w.rows))
    order = [nid for nid, _r in teach]
    taught = {}
    for nid, r in teach:
        taught.setdefault(nid, []).append(r)
    data = Data(Q, order, taught, n_names=len(names) + 1)   # one name with no exemplar (id 5)
    n = len(ex_rows)
    x0 = Val(False, np.array(ex_rows, dtype=np.int64), np.ones(n, dtype=bool))
    x1 = Val(False, np.array([k % 6 for k in range(n)], dtype=np.int64), np.ones(n, dtype=bool))
    lens = np.array([4 - (k % 2) for k in range(n)], dtype=np.int64)          # ragged sheets: 4 or 3
    mat = np.array(sheets, dtype=np.int64)
    cands = LVal(False, mat=mat, lens=lens, ok=np.ones(n, dtype=bool))
    return data, Batch(n, {"x0": x0, "x1": x1, "cands": cands})


def vals(v, n):
    if isinstance(v, LVal):
        return ("L", v.const, v.items if v.const else (v.mat.tolist(), v.lens.tolist(), v.ok.tolist()))
    if v.const:
        return ("C", int(v.v) if not isinstance(v.v, bool) else bool(v.v), bool(v.ok))
    ok = np.asarray(v.ok, dtype=bool)
    arr = np.asarray(v.v)
    return ("V", [int(a) if o else None for a, o in zip(arr.tolist(), ok.tolist())])


def as_col(v, n):
    if v.const:
        return [int(v.v) if bool(v.ok) else None] * n
    ok = np.asarray(v.ok, dtype=bool)
    return [int(a) if o else None for a, o in zip(np.asarray(v.v).tolist(), ok.tolist())]


class TestSemantics(unittest.TestCase):
    def setUp(self):
        self.data, self.batch = world()

    def ev(self, tree, **kw):
        return Evaluator(self.data, self.batch, {}, {}, **kw).run(tree)

    def test_sim_is_exact_symmetric_and_one_on_itself(self):
        a = self.ev(("sim", ("x0",), ("x0",)))
        self.assertTrue(np.all(np.abs(a.v - SIM_ONE) < 2 ** 32), "cos(x, x) is 1 up to the 2**-26 rounding")
        b = self.ev(("sim", ("x0",), ("nthG", ("cands",), ("0",))))
        c = self.ev(("sim", ("nthG", ("cands",), ("0",)), ("x0",)))
        self.assertEqual(b.v.tolist(), c.v.tolist())
        self.assertEqual(b.v.dtype, np.int64)

    def test_argmax_ties_go_to_the_first(self):
        # every name scores the same constant -> the FIRST name of `order` wins
        r = self.ev(("argmaxN", ("order",), ("b2r", ("eq", ("$0",), ("$0",)))))
        self.assertTrue(r.const and r.v == self.data.order[0] and r.ok)

    def test_nth_bounds_and_index_of_absent_raise(self):
        self.assertFalse(self.ev(("nthN", ("order",), ("sub", ("0",), ("1",)))).ok)       # negative
        big = ("add", ("1",), ("1",))
        for _ in range(4):
            big = ("add", big, big)                                                          # 32
        self.assertFalse(self.ev(("nthN", ("order",), big)).ok)                              # past the end
        r = self.ev(("index_of", ("order",), ("x1",)))
        self.assertEqual([o for o in r.ok.tolist()], [int(k % 6) < 5 for k in range(self.batch.n)],
                         "name id 5 is never in `order`: index_of raises there only")

    def test_empty_list_raises(self):
        # taught(x1) is empty for name 5 -> maxofG raises there
        r = self.ev(("maxofG", ("taught", ("x1",)), ("sim", ("x0",), ("$0",))))
        self.assertEqual(r.ok.tolist(), [int(k % 6) != 5 for k in range(self.batch.n)])

    def test_pick_membership(self):
        idx = pick_index(np.array([self.batch.inputs["cands"].mat[0, 2], -7]),
                         LVal(False, mat=self.batch.inputs["cands"].mat[:2], lens=self.batch.inputs["cands"].lens[:2],
                              ok=np.ones(2, dtype=bool)))
        self.assertEqual(idx.tolist(), [2, -1])


class TestParity(unittest.TestCase):
    """Every program up to size 9 of three request types: fast == loop, memo == no memo, row == batch."""

    REQUESTS = [
        ([("x0", dsl.G)], dsl.N),
        ([("x0", dsl.G), ("cands", dsl.LG)], dsl.G),
        ([("x0", dsl.G), ("x1", dsl.N)], dsl.B),
    ]

    def test_parity(self):
        data, batch = world()
        n = batch.n
        checked = 0
        for ins, out in self.REQUESTS:
            g = Grammar([], [], ins, out)
            en = Enumerator(g, Sig([t for _k, t in ins], out), 9)
            ev_fast = Evaluator(data, batch, {}, {}, memo=True, fast=True)
            for tree in en.programs():
                a = ev_fast.run(tree)
                b = Evaluator(data, batch, {}, {}, memo=False, fast=False).run(tree)
                self.assertEqual(as_col(a, n), as_col(b, n), dsl.render(tree))
                if checked % 7 == 0:     # a sample of the programs, one example at a time
                    for i in range(n):
                        sub = {}
                        for k, v in batch.inputs.items():
                            if isinstance(v, LVal):
                                sub[k] = LVal(False, mat=v.mat[i:i + 1], lens=v.lens[i:i + 1], ok=v.ok[i:i + 1])
                            else:
                                sub[k] = Val(False, v.v[i:i + 1], v.ok[i:i + 1])
                        one = Evaluator(data, Batch(1, sub), {}, {}, memo=False).run(tree)
                        self.assertEqual(as_col(one, 1), [as_col(a, n)[i]], dsl.render(tree))
                checked += 1
        self.assertGreater(checked, 2000)


class TestParityWithLibrary(unittest.TestCase):
    """The memo names values by provenance in EVERY context (abstraction bodies, cue ops' programs): one evaluator
    reused across every program up to size 8 of a grammar WITH abstractions and cue ops must give exactly what a
    fresh, memo-less evaluator gives, program by program."""

    def test_parity_with_abstractions_and_cue_ops(self):
        data, batch = world()
        n = batch.n
        naming = ("argmaxN", ("order",), ("maxofG", ("taught", ("$0",)), ("sim", ("x0",), ("$0",))))
        after = ("nthN", ("order",), ("add", ("index_of", ("order",), ("@NAME(G)>NAME", ("x0",))), ("1",)))
        point = ("argmaxG", ("cands",), ("maxofG", ("taught", ("x0",)), ("sim", ("$1",), ("$0",))))
        abstractions = {"f0": (("maxofG", ("taught", ("#0",)), ("sim", ("#1",), ("$0",))), 2),
                        "f1": (("nthN", ("order",), ("#0",)), 1)}
        abs_sigs = [("f0", Sig([dsl.N, dsl.G], dsl.R)), ("f1", Sig([dsl.Z], dsl.N))]
        cues = {"NAME(G)>NAME": (naming, ("x0",), Sig([dsl.G], dsl.N)),
                "AFTER(G)>NAME": (after, ("x0",), Sig([dsl.G], dsl.N)),
                "POINT(N;cands)>PICK": (point, ("x0", "cands"), Sig([dsl.N, dsl.LG], dsl.G))}
        cue_ops = [(k, v[2]) for k, v in cues.items()]
        checked = 0
        for ins, out in (([("x0", dsl.G), ("cands", dsl.LG)], dsl.G), ([("x0", dsl.G), ("x1", dsl.N)], dsl.B)):
            g = Grammar(abs_sigs, cue_ops, ins, out)
            en = Enumerator(g, Sig([t for _k, t in ins], out), 8)
            shared = Evaluator(data, batch, abstractions, cues, memo=True, fast=True)
            for tree in en.programs():
                a = shared.run(tree)
                b = Evaluator(data, batch, abstractions, cues, memo=False, fast=False).run(tree)
                self.assertEqual(as_col(a, n), as_col(b, n), dsl.render(tree))
                checked += 1
        self.assertGreater(checked, 1500)          # 1,834 programs at size <= 8 on 2026-09-24
        self.assertGreater(len(shared.memo), 0)


if __name__ == "__main__":
    unittest.main()
