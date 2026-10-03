# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:25 +0400 — a one-off DIAGNOSIS, not a gate: the bench grade holds ONE bar whose pass flag differs between the arms, TRUTH-NEED (SPEAK2): OFF 0.561 (n 41) PASS, ON 0.389 (n 36) FAIL.
# grade.json keeps rates, not SPEAK2 item rows, so the rows are rebuilt with the grader's OWN machinery (Life, SetCtx, offline_answers, marks.grade_mouth_r) and paired by item id.
# CONTROL (built in): per arm, the rebuilt rows must reproduce the grade's own TRUTH-NEED n and value exactly, or the script stops.
import json
import sys
from pathlib import Path

import numpy as np

from brain.scene import marks as M
from tools.brain import grade_life as G


def arm_rows(label):
    life = G.Life(Path("scratch/bench-1/groot"), Path(f"scratch/bench-1/{label}/journal.jsonl"), Path(f"scratch/bench-1/GENOME-{label}.genome"))
    ms = G.meeting_seen(life)
    sc = G.SetCtx(life, G.GRADED_SET)
    A = G.offline_answers(life, sc)
    ctx = G._Ctx(sc, ms["seen"])
    ans = A["roads"][G.LAW]
    rows = M.grade_mouth_r(ctx.items["SPEAK2"], ans, ctx.truth["speak2"], ctx.ptr["gaze"])
    return rows, A


def main():
    res = {}
    for label in ("off", "on"):
        rows, A = arm_rows(label)
        grade = json.load(open(f"scratch/bench-1/grade-{label}/grade.json"))
        want_v = grade["bars"]["TRUTH-NEED"]["value"]
        want_n = grade["bars"]["TRUTH-NEED"]["n"]
        spk = [r for r in rows if r["covered"] and r["spoken"]]
        got_v = float(np.mean([r["true"] for r in spk])) if spk else None
        ok = (len(spk) == want_n) and (got_v is not None) and abs(got_v - want_v) < 1e-12
        print(f"CONTROL {label}: rebuilt TRUTH-NEED n {len(spk)} value {got_v} · the grade holds n {want_n} value {want_v} → {'REPRODUCED' if ok else 'NOT REPRODUCED'}")
        if not ok:
            sys.exit(2)
        res[label] = {r["item_id"]: r for r in rows}
    off, on = res["off"], res["on"]
    ids = sorted(set(off) | set(on))
    print("items: off", len(off), "on", len(on), "union", len(ids), "same ids", set(off) == set(on))
    cov_both = [i for i in ids if off[i]["covered"] and on[i]["covered"]]
    print("covered in OFF", sum(off[i]["covered"] for i in ids), "in ON", sum(on[i]["covered"] for i in ids), "in both", len(cov_both))
    cells = {"spoke_both": [], "only_off": [], "only_on": [], "neither": []}
    for i in cov_both:
        a, b = off[i]["spoken"], on[i]["spoken"]
        cells["spoke_both" if a and b else "only_off" if a else "only_on" if b else "neither"].append(i)
    print({k: len(v) for k, v in cells.items()})
    sb = cells["spoke_both"]
    on_right = [i for i in sb if on[i]["true"] and not off[i]["true"]]
    off_right = [i for i in sb if off[i]["true"] and not on[i]["true"]]
    both_t = [i for i in sb if on[i]["true"] and off[i]["true"]]
    both_f = [i for i in sb if not on[i]["true"] and not off[i]["true"]]
    print(f"spoke in both n {len(sb)}: both true {len(both_t)} · both false {len(both_f)} · ON-right only {len(on_right)} · OFF-right only {len(off_right)} · smallest passing gap 10/n = {10.0/len(sb):.3f}")
    from tools.brain.grade_life import sign_test
    print("sign test (ON worse = OFF-right more) p =", sign_test(len(off_right), len(on_right)) if hasattr(G, 'sign_test') else None)
    for tag, lst in (("OFF right, ON wrong", off_right), ("ON right, OFF wrong", on_right)):
        print(" ", tag)
        for i in lst:
            print("    ", i, "kind", off[i].get("kind"), "· OFF", off[i]["phrase"], off[i]["true"], "· ON", on[i]["phrase"], on[i]["true"])
    for tag in ("only_off", "only_on"):
        print(" ", tag, "(spoke in one arm only):")
        for i in cells[tag]:
            who = off if tag == "only_off" else on
            other = on if tag == "only_off" else off
            print("    ", i, "kind", who[i].get("kind"), "· spoke", who[i]["phrase"], "true", who[i]["true"], "· other arm reason", other[i].get("reason"))
    # the rest of the population view: TRUTH-NEED by arm, by kind, length mixes
    for label, d in (("off", off), ("on", on)):
        spk = [r for r in d.values() if r["covered"] and r["spoken"]]
        mix = {k: sum(1 for r in spk if r["length"] == k) for k in (1, 2, 3)}
        print(label, "spoken covered", len(spk), "true", sum(r["true"] for r in spk), "length mix", mix)
        for kind in ("CS", "SC", "SS"):
            k = [r for r in spk if r.get("kind") == kind]
            print("    kind", kind, "n", len(k), "true", sum(r["true"] for r in k))
    print("reasons not spoken among covered:", {lbl: dict(__import__('collections').Counter(r["reason"] for r in d.values() if r["covered"] and not r["spoken"])) for lbl, d in (("off", off), ("on", on))})


if __name__ == "__main__":
    main()
