# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:58 +0400 — a read-only DIAGNOSTIC of THE FIRST GATE's step-3 STOP
# (gate at 17:51, code-15b047e): five trained words read truth-free cal_20 below truth-fed by > 0.10 (big, circle, green,
# small, square). It is NOT a re-read of the gate and changes no verdict: the STOP stands on cal_20 as ruled. It re-runs
# seed 20261101's HEALTH life from the SAME pin with the gate's own hook subclassed to RECORD, per said word, which class of
# scene each grade came from — reusing health.claims / health.attribution / health.grades / run.referent_index, never a
# re-implementation — and writes only under /data/dev/brain-runs/scene-tmem2/gate-diag/.
#
# Run (from the pin, never the worktree's code):
#   cd /data/dev/brain-runs/scene-tmem2/code-15b047e && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 \
#     /usr/bin/python3 -B /data/dev/genome-wt-scene-r/tools/scene/diag_tmem2_step3.py
#
# The classes of a graded said word w (of a learned type) in a training scene, ref = the referent's hypothesis:
#   A  ref seen AND the learner's attribution h* == ref  — the free and fed grades are ONE claim at ONE hypothesis
#   B  ref seen AND h* != ref                              — the free grade is about a distractor, the fed about the referent
#   C  ref None (the gaze never landed on the referent)    — the fed row cannot grade; the free row grades a seen thing
#   N  h* None (nothing stored)                            — ungraded in the free row
#
# PREDICTIONS, written and committed BEFORE the run:
#   P1 [Certain unless a bug] class A: 0 disagreements between the free and fed grades. Any disagreement is a BUILD fault.
#   P2 [Likely] class A holds the majority of the ref-seen said words (M1 0.985 — attributions of trained words mostly
#      right); a small A share would point at an index misalignment in the attribution.
#   P3 [Likely] the free row's EXTRA grades (free n_graded > fed n_graded on 13 / 13 words in gate.txt) live in class C,
#      and C's free grades are mostly REFUTATIONS whose claim is TRUE of the thing it was made about (b_T(h*) = the true
#      value of h*'s majority thing): the free row is charged with the GAZE's misses, which the declared sign (§6: «two
#      argmaxes of one score matrix … the truth-free row over-confirms») did not count.
#   P4 [Guessing] without class C the free row's whole-life precision sits within 0.05 of the fed row's on most words.
#   Refuted if: P1 any A disagreement (a bug in the build); P3 the extra grades and refutations sit in A or B; P4 the gap
#   survives without C (then class B carries it: attributions among SEEN things fall on a thing believed to be another
#   word — p_w is not contrastive across the words of a type).
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

PIN = Path("/data/dev/brain-runs/scene-tmem2/code-15b047e")
OUT = Path("/data/dev/brain-runs/scene-tmem2/gate-diag")
GATE_LIFE = Path("/data/dev/brain-runs/scene-tmem2/gate/lives/20261101/life/record.json")
WS = 20261101

from brain.scene import health as H          # noqa: E402  (PYTHONPATH = the pin)
from brain.scene import run as R              # noqa: E402
from brain.scene import run_tmem2 as T        # noqa: E402
from brain.scene import world as W            # noqa: E402

if not str(Path(T.__file__).resolve()).startswith(str(PIN)):
    raise SystemExit(f"run from the pin: brain.scene resolves to {T.__file__}")


def maj_thing(members_h, fix_thing):
    c = Counter(fix_thing[m] for m in members_h if fix_thing[m] is not None)
    if not c:
        return None
    best = max(c.values())
    return min(t for t, v in c.items() if v == best)


class DiagHook(T._Hook):
    made = []

    def __init__(self, L, train, truth):
        super().__init__(L, train, truth)
        self.recs = []
        DiagHook.made.append(self)

    def after(self, i, X, words, new, rec):
        if rec is not None:
            att = H.attribution(self.L, X, words, new)                      # read-only; super() reads the same
            ref = R.referent_index("A-RW", self.train, self.truth[i])
            tr = self.truth[i]
            members, _ = self.train.members(int(tr["row"]))
            where = {w: k for k, Tt in enumerate(rec["types"]) for w in Tt}
            for w in dict.fromkeys(words):
                if w not in where:
                    continue
                hs = att.get(w)
                gf = H.grades(rec, {w: hs})
                gd = H.grades(rec, {w: ref})
                cls = "N" if hs is None else ("C" if ref is None else ("A" if hs == ref else "B"))
                typ = W.word_type(w)
                t_hs = maj_thing(members[hs], tr["fix_thing"]) if hs is not None and hs < len(members) else None
                true_hs = tr["things"][t_hs].get(typ) if t_hs is not None else None
                true_ref = tr["things"][int(tr["referent"])].get(typ) if tr.get("referent") is not None else None
                self.recs.append({"i": int(i), "w": w, "cls": cls, "hs": hs, "ref": ref,
                                  "free": [gf[0][0], bool(gf[0][1])] if gf else None,
                                  "fed": [gd[0][0], bool(gd[0][1])] if gd else None,
                                  "true_hs": true_hs, "w_true_of_ref": (true_ref == w) if true_ref is not None else None})
        super().after(i, X, words, new, rec)


def cal20(seq):
    last = seq[-20:]
    return (sum(last) / len(last)) if len(seq) >= H.GATE_N else None


def prec(seq):
    return (sum(seq) / len(seq)) if seq else None


def f(x, n=3):
    return "  —  " if x is None else f"{x:.{n}f}"


def main() -> int:
    t0 = time.process_time()
    T._Hook = DiagHook
    rec = T.run_life(WS, T.S1B1R_ROOT, OUT / "lives", log=lambda s: print(s, flush=True))
    hook = DiagHook.made[-1]
    rs = hook.recs
    gate = json.loads(GATE_LIFE.read_text())["rows"]
    lines = [f"== T-MEM-2 step-3 DIAGNOSTIC (seed {WS}; pin {rec['code']['code_sha_file'][:7]}; identity "
             f"{'PASS' if rec['identity']['pass'] else 'MISS'}; read-only, the gate's verdict unchanged) =="]
    # 0. reproduction of the gate's own rows, from this accounting
    free_seq, fed_seq = {}, {}
    for r in rs:
        if r["free"]:
            free_seq.setdefault(r["free"][0], []).append(r["free"][1])
        if r["fed"]:
            fed_seq.setdefault(r["fed"][0], []).append(r["fed"][1])
    bad = []
    for w in T.TRAINED:
        g_f, g_d = gate["free"].get(w, {}), gate["fed"].get(w, {})
        mine = (len(free_seq.get(w, [])), cal20(free_seq.get(w, [])), len(fed_seq.get(w, [])), cal20(fed_seq.get(w, [])))
        theirs = (g_f.get("n_graded", 0), g_f.get("cal20"), g_d.get("n_graded", 0), g_d.get("cal20"))
        hk = (hook.free.row(w).n_graded, hook.free.row(w).cal20(), hook.fed.row(w).n_graded, hook.fed.row(w).cal20())
        if not (mine[0] == theirs[0] == hk[0] and mine[2] == theirs[2] == hk[2]
                and all(abs((a or 0) - (b or 0)) < 1e-12 and abs((a or 0) - (c or 0)) < 1e-12
                        for a, b, c in ((mine[1], theirs[1], hk[1]), (mine[3], theirs[3], hk[3])))):
            bad.append(w)
    lines.append(f"0. the gate's own rows reproduced from this accounting (n_graded and cal_20, free and fed, 13 words; "
                 f"the gate life's record.json AND this life's hook): {'ALL EQUAL' if not bad else 'DIFFER on ' + str(bad)}")
    # 1. the classes
    lines.append("1. graded said words by class (free = the learner's attribution; fed = the referent):")
    lines.append("   class  said-words  free graded (confirmed)  fed graded (confirmed)  A: free≠fed")
    cls_tab = {}
    for c in ("A", "B", "C", "N"):
        sub = [r for r in rs if r["cls"] == c]
        fg = [r for r in sub if r["free"]]
        dg = [r for r in sub if r["fed"]]
        dis = sum(1 for r in sub if r["free"] != r["fed"]) if c == "A" else None
        cls_tab[c] = {"said": len(sub), "free_n": len(fg), "free_ok": sum(r["free"][1] for r in fg),
                      "fed_n": len(dg), "fed_ok": sum(r["fed"][1] for r in dg), "A_disagree": dis}
        lines.append(f"   {c:<5}  {len(sub):>10}  {len(fg):>6} ({sum(r['free'][1] for r in fg):>6})           "
                     f"{len(dg):>6} ({sum(r['fed'][1] for r in dg):>6})         {'' if dis is None else dis}")
    seen = cls_tab["A"]["said"] + cls_tab["B"]["said"]
    lines.append(f"   the referent unseen (class C) in {cls_tab['C']['said']} of {len(rs)} graded-type said words "
                 f"({cls_tab['C']['said'] / max(len(rs), 1):.3f}); class A's share of the referent-seen: "
                 f"{cls_tab['A']['said'] / max(seen, 1):.3f}")
    # 2. the refutations of B and C: was the refuted claim TRUE of the thing it was made about?
    lines.append("2. free-row REFUTATIONS in B and C — the claim b_T(h*) against the TRUE value of h*'s majority thing:")
    ref_tab = {}
    for c in ("B", "C"):
        refs = [r for r in rs if r["cls"] == c and r["free"] and not r["free"][1]]
        right = sum(1 for r in refs if r["true_hs"] is not None and r["free"][0] == r["true_hs"])
        w_true = sum(1 for r in refs if r["true_hs"] is not None and r["true_hs"] == r["w"])
        unk = sum(1 for r in refs if r["true_hs"] is None)
        ref_tab[c] = {"refuted": len(refs), "claim_true_of_its_thing": right, "said_word_true_of_its_thing": w_true,
                      "no_thing": unk}
        lines.append(f"   {c}: refuted {len(refs)} · the claim TRUE of its thing {right} · the said word true of that "
                     f"thing {w_true} · h* on no thing {unk}")
    # 3. per word, filed under the claimed word
    lines.append("3. per claimed word — whole-life precision free (all · without C) / fed · cal_20 free (all · without C) / fed · C grades (confirmed):")
    per = {}
    for w in T.TRAINED:
        fa = free_seq.get(w, [])
        fnc = [r["free"][1] for r in rs if r["free"] and r["free"][0] == w and r["cls"] != "C"]
        fc = [r["free"][1] for r in rs if r["free"] and r["free"][0] == w and r["cls"] == "C"]
        fd = fed_seq.get(w, [])
        per[w] = {"prec_free": prec(fa), "prec_free_noC": prec(fnc), "prec_fed": prec(fd), "cal20_free": cal20(fa),
                  "cal20_free_noC": cal20(fnc), "cal20_fed": cal20(fd), "C_n": len(fc), "C_ok": sum(fc)}
        lines.append(f"   {w:<9} {f(prec(fa))} · {f(prec(fnc))} / {f(prec(fd))}   ·   {f(cal20(fa), 2)} · {f(cal20(fnc), 2)} / "
                     f"{f(cal20(fd), 2)}   ·   C {len(fc):>4} ({sum(fc):>4})")
    lines.append(f"cpu {time.process_time() - t0:.1f} s")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "diag.json").write_text(json.dumps({"classes": cls_tab, "refutations": ref_tab, "per_word": per,
                                               "reproduced": not bad, "differ": bad, "identity": rec["identity"]["pass"],
                                               "records": rs}, sort_keys=True) + "\n")
    (OUT / "diag.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
