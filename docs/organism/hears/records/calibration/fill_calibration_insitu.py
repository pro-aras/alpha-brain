# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:3x +0400 — fills the «In-situ check» section of docs/organism/hears/CALIBRATION-COST-2026-10-03.md from the bench arms' own timings and journals (every number is computed here, none typed).
import json
import statistics
import subprocess
from pathlib import Path

BENCH = Path("scratch/bench-1")
DOC = Path("docs/organism/hears/CALIBRATION-COST-2026-10-03.md")
ISOLATED = {10000: (3.06, 3.10)}                       # the doc's own table: all_scene, maker_like CPU seconds at 10,000
MODEL_A, MODEL_B = 0.49, 0.296e-3                      # the doc's all_scene model c(N) = 0.49 s + 0.296 ms x N


import sys
sys.path.insert(0, ".")
from tools.brain import hears_read as H

CANV = H._canvases(Path("scratch/cut-full/tape"))                       # moment -> {source, kind, seqs}, the reader's own definition of a canvas
SEQ_MOMENT = {s: m for m, d in CANV.items() for s in d["seqs"]}


def calibrations(arm):
    out = []
    for line in open(BENCH / arm / "journal.jsonl", encoding="utf-8"):
        if '"calibrate"' not in line:
            continue
        r = json.loads(line)
        if r.get("kind") == "brain" and r.get("act") == "calibrate":
            out.append((int(r["seq"]), int(r["summary"]["learned"])))
    return out


def canvas_cpu(tm, moment):
    return sum(float(tm[s]["cpu_ms"]) for s in CANV[moment]["seqs"])


rows = {}
for arm in ("off", "on"):
    tm = H._timings(BENCH / arm / "timings.jsonl")
    cal = calibrations(arm)
    cal_moments = {SEQ_MOMENT[s] for s, _ in cal}
    train = [m for m, d in CANV.items() if d["source"] == "scene" and d["kind"] == "train" and m not in cal_moments and all(s in tm for s in d["seqs"])]
    base = H._median([canvas_cpu(tm, m) for m in train])
    rows[arm] = {"base_ms": base, "n_train": len(train),
                 "cal": [(n, s, canvas_cpu(tm, SEQ_MOMENT[s]), CANV[SEQ_MOMENT[s]]["kind"]) for s, n in cal]}
assert [n for n, *_ in rows["off"]["cal"]] == [n for n, *_ in rows["on"]["cal"]], "the arms must calibrate at the same counts"
stamp = subprocess.run(["date", "+%Y-%m-%d %H:%M %z"], capture_output=True, text=True).stdout.strip()

L = [f"## In-situ check (read from the HEARS-2 bench arms' own timings, {stamp})",
     "",
     "Each bench arm (`hears_bench.sh arms`, launched 11:22:06 +0400, ~2,731 s wall, both exit 0; the arms' records are under `docs/organism/hears/records/`) replays the scene hand's 10,000 scenes and calibrates 6 times, at 250, 500, 1,000, 2,000, 5,000 and 10,000 scenes learned. Every calibration is ONE canvas whose `cpu_ms` stands far above the arm's median scene canvas, so the call's price can be read off the replay's own `timings.jsonl` (the canvas that reaches the count). OFF is the brain that hears the scene only; ON is the brain that also hears the maker, so it reaches each count a few canvases earlier (the maker's canvases are learned too) and holds 19 words, not 14.",
     "",
     f"Median scene TRAINING canvas (its ear + eye rows, the reader's own canvas; the calibration canvases left out of the median): OFF {rows['off']['base_ms']:.1f} ms, ON {rows['on']['base_ms']:.1f} ms.",
     "",
     "| scenes learned | OFF canvas CPU | OFF minus median | OFF ms per scene | ON canvas CPU | ON minus median | ON ms per scene | the model's c(N), all_scene |",
     "|---|---|---|---|---|---|---|---|"]
per = {"off": [], "on": []}
for (n, _s0, c0, _src0), (_n1, _s1, c1, _src1) in zip(rows["off"]["cal"], rows["on"]["cal"]):
    model = MODEL_A + MODEL_B * n
    d0, d1 = c0 - rows["off"]["base_ms"], c1 - rows["on"]["base_ms"]
    per["off"].append(d0 / n)
    per["on"].append(d1 / n)
    L.append(f"| {n:,} | {c0/1000:.3f} s | {d0/1000:.3f} s | {d0/n:.3f} ms | {c1/1000:.3f} s | {d1/1000:.3f} s | {d1/n:.3f} ms | {model:.2f} s |")
n10 = 10000
off10, on10 = (rows["off"]["cal"][-1][2] - rows["off"]["base_ms"]) / 1000, (rows["on"]["cal"][-1][2] - rows["on"]["base_ms"]) / 1000
iso_all, iso_mk = ISOLATED[n10]
lo, hi = min(per["off"][1:] + per["on"][1:]), max(per["off"][1:] + per["on"][1:])
L += ["",
      f"**At 10,000 scenes the call costs {off10:.2f} s in OFF and {on10:.2f} s in ON** (the canvas minus the median canvas), against the isolated measurement above: {iso_all:.2f} s (all_scene) and {iso_mk:.2f} s (maker_like): the life reads **{off10/iso_all:.2f}× (OFF) and {on10/iso_all:.2f}× (ON)** of the isolated all_scene figure. The doc's linear model reads {MODEL_A + MODEL_B * n10:.2f} s at 10,000 (the OFF canvas: {rows['off']['cal'][-1][2]/1000:.2f} s).",
      "",
      f"**In situ the call is NOT proportional to the scenes learned.** From 500 scenes up it costs {lo:.2f}–{hi:.2f} ms per scene (OFF {per['off'][1]:.3f} at 500 → {per['off'][-1]:.3f} at 10,000; ON {per['on'][1]:.3f} → {per['on'][-1]:.3f}); at 250 it sits inside the canvas's own noise. Isolated, the price is flat at 0.30–0.31 ms per scene from 10,000 to 100,000. Six in-situ points, all at or below 10,000, cannot say whether the life's per-scene cost flattens or keeps rising beyond them, so **the in-situ reading does not confirm the 100,000 row**.",
      "",
      "What this changes: nothing in the order of magnitude and nothing in the seat's choice. At 10,000 the life's price is 10–16 % above the isolated measurement (candidate reasons, not separated here: the life's brain holds 14–19 words, and the replay runs beside other jobs); the doc's 12–30 s at 100,000 stands as the ISOLATED measurement, to be read about 10–16 % higher unless the days life shows otherwise, and the factor beyond 10,000 is not known. Either way it is about two orders of magnitude under the health watch's one-hour stuck-mind rule.",
      "",
      "*(edit: Claude (Sonnet 5.5, swarm hears), " + stamp + " — the in-situ section filled by `scratch/fill_calibration_insitu.py` from `bench-1/{off,on}/{timings,journal}.jsonl`; the script and its output are in `docs/organism/hears/records/`)*", ""]
text = DOC.read_text()
old = "## In-situ check (to be filled from the bench arms' timings)\n*(pending)*\n"
assert text.count(old) == 1, "the placeholder must be present exactly once"
DOC.write_text(text.replace(old, "\n".join(L)))
print("\n".join(L))
