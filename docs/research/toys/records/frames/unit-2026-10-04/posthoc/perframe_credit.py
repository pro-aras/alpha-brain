"""perframe_credit.py — a POST-HOC reading of the Toy C unit (NOT a mark of the law; nothing it prints moves a verdict): for each rule's kept set F on ALPHA4 (plain split), the marginal credit of EACH frame, g_f = G(F) − G(F minus {f}),
the same difference AMENDMENT-1 §1 (C) signs for the planted frame. It answers the question the L1 SCHEMA design asks of Toy C's criterion: the whole-set G is negative for every rule, but L1 keeps or prunes ONE schema at a time:
how many frames pay for themselves on held-out text, which ones, and what the set of those would be worth (an OPTIMISTIC figure: the set is chosen by the same held-out text it is scored on).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-04 00:18 +0400 — new, written after the unit read (the report is at docs/research/toys/RESULT-TOY-FRAMES-REPORT.txt); a reading, labelled so everywhere it is quoted.

Controls (printed; the run STOPS if one fails):
  C1  the whole-set G recomputed here equals the record's G, for every rule, to 1e-6 bits (the instrument is the toy's own Scorer on the toy's own split);
  C2  the planted frame's marginal credit in the ALPHA4+PLANT record's WEB-H set equals the signed gate's (C) figure printed in the report, 3107.23, to 0.01 (the instrument reproduces a signed number);
  C3  a DEALT frame (a pair of train words that is never adjacent) added to a rule's set costs its description L = 2 log2 V PLUS the add-one smoothing's dilution (the inventory K grows by one, p(t) = (c_t + 1) / (N + K), so every
      held-out token costs a hair more): between −L − 1.5 and −L bits, and strictly below −L. (The first text of this control said «exactly −L»; the run read −L − 0.965, the dilution; the expectation was the script's error.)
usage: PYTHONPATH=. python3 -B -u perframe_credit.py <copies> <runs dir> <out json>
"""
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.toys.frames import compress as CO
from tools.toys.frames import plants as PL
from tools.toys.frames import run as RN

copies, runs, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
t0 = time.process_time()
a4 = RN.load_streams(copies)["alpha4"]
cond = json.loads((runs / "ALPHA4.json").read_text())
train, held = PL.condition_parts(a4, "plain")
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
L1 = 2.0 * math.log2(sc.V)
res = {"V": sc.V, "L_per_frame": L1, "rules": {}, "controls": {}}

# C2 first (the plant stream)
cp = json.loads((runs / "ALPHA4+PLANT.json").read_text())
trainp, heldp = PL.condition_parts(a4, "plant", every=100)
scp = CO.Scorer([m.words for m in trainp], [m.words for m in heldp])
wh = next(r for r in cp["records"] if r["rule"] == "WEB-H")
Fp = {tuple(f) for f in wh["frames"]}
star = ("zzq", "qxk")
assert star in Fp, "the planted frame is not in WEB-H's set on the plant stream"
c2 = scp.gain(Fp).G - scp.gain(Fp - {star}).G
res["controls"]["C2_plant_marginal_credit"] = {"value": c2, "signed_report_value": 3107.23, "ok": abs(c2 - 3107.23) < 0.01}
print(f"C2 the planted frame's marginal credit in WEB-H's set on ALPHA4+PLANT: {c2:.2f} (the signed gate's (C) reads 3107.23): {'OK' if abs(c2 - 3107.23) < 0.01 else 'FAILED'}", flush=True)
if abs(c2 - 3107.23) >= 0.01:
    sys.exit(3)

# C3: a dealt, never-adjacent pair costs exactly L
tb = sc.train_bigrams()
words = sorted({w for m in sc.train for w in m})
dealt = None
for a in words[:60]:
    for b in words[60:120]:
        if (a, b) not in tb and (b, a) not in tb:
            dealt = (a, b)
            break
    if dealt:
        break
assert dealt is not None
mdl = next(r for r in cond["records"] if r["rule"] == "MDL-GREEDY")
Fm = {tuple(f) for f in mdl["frames"]}
dg = sc.gain(Fm | {dealt}).G - sc.gain(Fm).G
c3ok = (-L1 - 1.5) < dg < -L1
res["controls"]["C3_dealt_pair_cost"] = {"pair": list(dealt), "delta_G": dg, "minus_L": -L1, "dilution": dg + L1, "ok": c3ok}
print(f"C3 a dealt never-adjacent pair {dealt} changes G by {dg:.6f} (−L = {-L1:.6f}; the add-one dilution {dg + L1:.6f} bits; expected strictly below −L and above −L − 1.5): {'OK' if c3ok else 'FAILED'}", flush=True)
if not c3ok:
    sys.exit(3)

for rec in cond["records"]:
    rule, seed = rec["rule"], rec["seed"]
    if rule == "WEB-S" and seed != 1:
        continue
    F = {tuple(f) for f in rec["frames"]}
    Gf = sc.gain(F).G
    ok = abs(Gf - rec["gain"]["G"]) < 1e-6
    print(f"C1 {rule} seed {seed}: recomputed G {Gf:.6f} against the record's {rec['gain']['G']:.6f}: {'OK' if ok else 'FAILED'}", flush=True)
    if not ok:
        sys.exit(3)
    credits = []
    for f in sorted(F):
        credits.append((Gf - sc.gain(F - {f}).G, f))
    credits.sort(key=lambda x: (-x[0], x[1]))
    pos = [(c, f) for c, f in credits if c > 0]
    Fpos = {f for _c, f in pos}
    Gpos = sc.gain(Fpos).G if Fpos else 0.0
    res["rules"][f"{rule}" + (f" s{seed}" if rule == "WEB-S" else "")] = {
        "n_frames": len(F), "G_whole": Gf, "n_positive": len(pos), "sum_positive": sum(c for c, _ in pos), "sum_negative": sum(c for c, _ in credits if c <= 0),
        "G_of_the_positive_subset_OPTIMISTIC": Gpos,
        "top": [[c, list(f)] for c, f in credits[:25]], "bottom": [[c, list(f)] for c, f in credits[-8:]],
        "credits_of_the_said_grounded_frames": {" ".join(f): c for c, f in credits if " ".join(f) in ("green box", "red box", "grey ball", "purple ball", "blue ball", "yellow key", "blue key", "red key")},
    }
    r_ = res["rules"][f"{rule}" + (f" s{seed}" if rule == "WEB-S" else "")]
    print(f"{rule} seed {seed}: |F| {len(F)}; frames with a positive marginal credit {len(pos)} (sum {r_['sum_positive']:.2f} bits); the others {len(credits) - len(pos)} (sum {r_['sum_negative']:.2f}); "
          f"G of the positive subset alone (OPTIMISTIC, selected on the held-out it is scored on) {Gpos:.2f}", flush=True)
res["cpu_seconds"] = time.process_time() - t0
out.write_text(json.dumps(res, indent=1, sort_keys=True))
print(f"wrote {out} ({res['cpu_seconds']:.0f} CPU-s)", flush=True)
