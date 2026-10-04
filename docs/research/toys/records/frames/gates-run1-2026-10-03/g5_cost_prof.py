"""g5_cost_prof.py — cProfile of ONE NULL-2 draw on WEB-H's real ALPHA4 set (timing only; no value printed).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 22:29 +0400 — new, scratch (untracked).
"""
import cProfile
import pstats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.toys.frames import compress as CO
from tools.toys.frames import null as NL
from tools.toys.frames import plants as PL
from tools.toys.frames import rules as RL
from tools.toys.frames import run as RN
from tools.toys.frames import streams as ST

a4 = RN.load_streams(Path(sys.argv[1]))["alpha4"]
train, held = PL.condition_parts(a4, "plain")
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
r = RL.web_rule(ST.flat_words(train), sc, "H", 0)
pr = cProfile.Profile()
pr.enable()
NL.null2(sc, r.frames, RL.RULE_TAG[r.rule], 0, 1)
pr.disable()
st = pstats.Stats(pr)
st.sort_stats("tottime").print_stats(14)
