# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:26 +0400 — a read-only DIAGNOSTIC of the AMENDED gate's STOP (18:23,
# code-8767cf6, PREREG-TMEM2 + AMENDMENT 1 a7dceea): step 3 STOPPED again on the same five words (big, circle, green, small,
# square), and the rule set aside only 45 of 1,924 class-C claims (0.023) and 29 of 15,479 seen-referent claims (0.002 — the
# false-unseen rate, predicted 0.05–0.08). It asks ONE question: is the rule's check right, and if so how far does the said
# word's own band reach? It changes no verdict. It re-runs seed 20261101's life from the SAME pin with the gate's hook
# subclassed to record, per gradable claim of the truth-free row, the class (A: h* is the referent's hypothesis; B: the
# referent seen, h* elsewhere; C: the referent never seen), the said word's READER distance at h* against its band — taken
# from the claim step's own state (the distances the held words were read from) — and how many words of its type the band
# holds there. It reuses health.claims / attribution / grades and run.referent_index, and writes only under
# /data/dev/brain-runs/scene-tmem2/gate-diag-amend1/.
#
# Run (from the pin):
#   cd /data/dev/brain-runs/scene-tmem2/code-8767cf6 && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 \
#     /usr/bin/python3 -B /data/dev/genome-wt-scene-r/tools/scene/diag_tmem2_amend1.py
#
# PREDICTIONS, written and committed BEFORE the run:
#   P1 [Certain unless a bug] the rule's check (the said word among the held words at h*) agrees on EVERY gradable claim
#      with an independent recomputation (d_w(h*) ≤ band_w, from the reader's distances at the claim step); and the counts
#      reproduce the gate's readings for this seed (never seen: 45 / 1,924 set aside; seen: 29 / 15,479).
#   P2 [Likely] in class C the said word's d_w / band_w at the seen distractor sits mostly BELOW 1 (median well under 1):
#      the band holds the thing the parent did not speak about — the band is wider than the distance between the words of
#      a type, so «w's own band holds h*» cannot tell the thing the parent meant from a seen neighbour.
#   P3 [Likely] at a seen thing the band holds several words of the thing's type at once (the «what is this?» is not
#      exclusive within a type): the mean count of the type's words held at h* is ≥ 2 for the shape type.
#   P4 [Guessing] the two size words are held together at nearly every thing.
#   Refuted if: P1 any disagreement or a count that does not reproduce (a fault in the build — STOP); P2 the median ratio
#   in C ≥ 1 (then the rule should have fired, and P1's agreement would be the thing to re-read).
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

PIN = Path("/data/dev/brain-runs/scene-tmem2/code-8767cf6")
OUT = Path("/data/dev/brain-runs/scene-tmem2/gate-diag-amend1")
GATE = Path("/data/dev/brain-runs/scene-tmem2/gate/gate.json")
WS = 20261101

from brain.scene import health as H          # noqa: E402  (PYTHONPATH = the pin)
from brain.scene import run as R              # noqa: E402
from brain.scene import run_tmem2 as T        # noqa: E402
from brain.scene import world as W            # noqa: E402

if not str(Path(T.__file__).resolve()).startswith(str(PIN)):
    raise SystemExit(f"run from the pin: brain.scene resolves to {T.__file__}")


class DiagHook(T._Hook):
    made = []

    def __init__(self, L, train, truth):
        super().__init__(L, train, truth)
        self.recs = []
        DiagHook.made.append(self)

    def before(self, i, X):
        rec = super().before(i, X)
        if rec is not None:                                            # the claim step's own state: its distances
            rec["_D"] = self.L.reader_distances(self.L.stats.standardise(np.atleast_2d(X)), Lr_mode())
        return rec

    def after(self, i, X, words, new, rec):
        if rec is not None:
            att = H.attribution(self.L, X, words, new)
            ref = R.referent_index("A-RW", self.train, self.truth[i])
            st = self.L.reader[Lr_mode()]
            where = {w: k for k, Tt in enumerate(rec["types"]) for w in Tt}
            for b, ok, w in H.grades(rec, att):
                h = att[w]
                band = st["word"][w]["band"] if w in st["word"] else None
                d = float(rec["_D"][h, self.L.index[w]])
                Tt = rec["types"][where[w]]
                self.recs.append({"cls": "C" if ref is None else ("A" if h == ref else "B"), "w": w, "b": b,
                                  "type": W.word_type(w), "set_aside": ok is None, "confirmed": ok is True,
                                  "ratio": (d / band) if band else None, "indep_holds": band is not None and d <= band,
                                  "rule_holds": w in rec["held"][h], "n_type": len(Tt),
                                  "held_in_type": sum(1 for u in Tt if u in rec["held"][h])})
        super().after(i, X, words, new, rec)


def Lr_mode() -> str:
    return "ear"                                                       # the LAW road's types: the ear's (RWRoad default)


def q(v, p):
    return float(np.quantile(v, p)) if len(v) else float("nan")


def main() -> int:
    t0 = time.process_time()
    assert T.Lr.RWRoad.__init__.__defaults__[0] == "ear"               # the road the claims read: types="ear", band="reader"
    T._Hook = DiagHook
    rec = T.run_life(WS, T.S1B1R_ROOT, OUT / "lives", log=lambda s: print(s, flush=True))
    rs = DiagHook.made[-1].recs
    gate = json.loads(GATE.read_text())["perception"][str(WS)]
    lines = [f"== T-MEM-2 AMENDMENT 1 DIAGNOSTIC (seed {WS}; pin {rec['code']['code_sha_file'][:7]}; identity "
             f"{'PASS' if rec['identity']['pass'] else 'MISS'}; read-only, the gate's verdict unchanged) =="]
    un = [r for r in rs if r["cls"] == "C"]
    se = [r for r in rs if r["cls"] != "C"]
    mine = {"unseen": (sum(r["set_aside"] for r in un), len(un)), "seen": (sum(r["set_aside"] for r in se), len(se))}
    theirs = {k: (gate[k]["set_aside"], gate[k]["gradable"]) for k in ("unseen", "seen")}
    agree = sum(r["indep_holds"] == r["rule_holds"] for r in rs)
    lines.append(f"0. the gate's readings reproduced: never seen {mine['unseen'][0]} / {mine['unseen'][1]} (gate {theirs['unseen'][0]} / "
                 f"{theirs['unseen'][1]}) · seen {mine['seen'][0]} / {mine['seen'][1]} (gate {theirs['seen'][0]} / {theirs['seen'][1]}) → "
                 f"{'EQUAL' if mine == theirs else 'DIFFER'}")
    lines.append(f"1. the rule's check (the said word among the held words at h*) against d_w(h*) ≤ band_w recomputed from the "
                 f"claim step's distances: {agree} / {len(rs)} agree")
    lines.append("2. per class — gradable · set aside · the said word's d_w / band_w at h*: p10 / median / p90 · held (≤ 1) · "
                 "the type's words the band holds at h* (mean, of the type's n):")
    table = {}
    for c in ("A", "B", "C"):
        sub = [r for r in rs if r["cls"] == c]
        rat = [r["ratio"] for r in sub if r["ratio"] is not None]
        table[c] = {"gradable": len(sub), "set_aside": sum(r["set_aside"] for r in sub),
                    "ratio_p10": q(rat, 0.1), "ratio_median": q(rat, 0.5), "ratio_p90": q(rat, 0.9),
                    "held": sum(1 for x in rat if x <= 1.0),
                    "held_in_type": {t: (float(np.mean([r["held_in_type"] for r in sub if r["type"] == t])) if any(r["type"] == t for r in sub) else None,
                                         next((r["n_type"] for r in sub if r["type"] == t), None))
                                     for t in ("shape", "colour", "size")}}
        x = table[c]
        lines.append(f"   {c}: {x['gradable']:>6} · {x['set_aside']:>4} · {x['ratio_p10']:.3f} / {x['ratio_median']:.3f} / {x['ratio_p90']:.3f} · "
                     f"{x['held']:>6} · " + " · ".join(f"{t} {v[0]:.2f} of {v[1]}" for t, v in x["held_in_type"].items() if v[0] is not None))
    lines.append("3. class C by type — gradable · set aside · refuted (graded) · d_w / band_w median:")
    for t in ("shape", "colour", "size"):
        sub = [r for r in un if r["type"] == t]
        rat = [r["ratio"] for r in sub if r["ratio"] is not None]
        lines.append(f"   {t:<6} {len(sub):>5} · {sum(r['set_aside'] for r in sub):>4} · "
                     f"{sum(1 for r in sub if not r['set_aside'] and not r['confirmed']):>5} · {q(rat, 0.5):.3f}")
    lines.append(f"cpu {time.process_time() - t0:.1f} s")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "diag.json").write_text(json.dumps({"reproduced": mine == theirs, "agree": agree, "n": len(rs), "classes": table,
                                               "identity": rec["identity"]["pass"]}, sort_keys=True) + "\n")
    (OUT / "diag.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    return 0 if (mine == theirs and agree == len(rs)) else 3


if __name__ == "__main__":
    sys.exit(main())
