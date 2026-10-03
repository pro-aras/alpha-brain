"""g5_cost_diag.py — WHERE does G5's 21.6 CPU-s per null draw go?  A timing-only diagnosis of the G5 failure (2026-10-03 22:2x gates run).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 22:27 +0400 — new, scratch (untracked): prints set sizes and SECONDS only; no gain, no null value and no verdict is printed or kept.

For the real ALPHA4 plain split (the stream G5 piloted): build the Scorer and the thirteen rule results as evaluate_condition does, then for each rule time (a) one sc.gain(F), (b) ONE NULL-1 draw and (c) ONE
NULL-2 draw (draws=1).  Output: rule, seed, |F|, seconds.  The null values themselves are never read.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.toys.frames import compress as CO
from tools.toys.frames import null as NL
from tools.toys.frames import plants as PL
from tools.toys.frames import rules as RL
from tools.toys.frames import run as RN
from tools.toys.frames import streams as ST

copies = Path(sys.argv[1])
a4 = RN.load_streams(copies)["alpha4"]
train, held = PL.condition_parts(a4, "plain")
t0 = time.process_time()
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
print(f"Scorer built: {time.process_time() - t0:.2f} cpu-s; train moments {len(train)}, held moments {len(held)}, V {sc.V}", flush=True)
flat = ST.flat_words(train)
results = []
for label, fn in (("WEB-H", lambda: RL.web_rule(flat, sc, "H", 0)), ("WEB-S s1", lambda: RL.web_rule(flat, sc, "S", 1)), ("WEB-S s2", lambda: RL.web_rule(flat, sc, "S", 2)),
                  ("SENTENCE", lambda: RL.sentence_rule(sc.train)), ("MDL-GREEDY", lambda: RL.mdl_greedy(sc))):
    t0 = time.process_time()
    r = fn()
    results.append((label, r, time.process_time() - t0))
print(f"{'rule':<12}{'|F|':>8}{'rule s':>10}{'gain s':>10}{'null1 draw s':>14}{'null2 draw s':>14}", flush=True)
for label, r, rule_s in results:
    t0 = time.process_time()
    sc.gain(r.frames)
    g_s = time.process_time() - t0
    tag = RL.RULE_TAG[r.rule]
    seed = r.seed if r.rule == "WEB-S" else 0
    out = []
    for fn in (NL.null1, NL.null2):
        t0 = time.process_time()
        try:
            fn(sc, r.frames, tag, seed, 1)
        except NL.NullError:
            pass
        out.append(time.process_time() - t0)
    print(f"{label:<12}{len(r.frames):>8}{rule_s:>10.2f}{g_s:>10.3f}{out[0]:>14.2f}{out[1]:>14.2f}", flush=True)
