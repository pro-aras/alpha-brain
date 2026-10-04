"""Orientation (synthetic data only): the PLANT gate on an ALPHA4-regime stream with ALPHA4's plant cadence (every 100th moment), to see whether WEB-S can keep the plant where B = 2V is ample."""
import numpy as np
from tools.toys.frames import evaluate as EV, plants as PL, streams as ST, synthetic as SY, verdicts as VD

tr0, he0 = SY.structure_free_alpha(20000, 1)
ms = tr0 + he0
planted = ST.with_plant(ms, 100)
tr, he = ST.split(planted)
cond = EV.evaluate_condition(tr, he, name="alpha-regime+plant", draws=100, web_seeds=EV.SEEDS, kind="plant")
print("V", cond["V"], "budget 2V =", 2 * cond["V"], "train words", cond["n_train_words"], "plants (train, held)", cond["plant_stream"]["plants_train"], cond["plant_stream"]["plants_held"])
g = VD.plant_gates(cond, "amend1")
for rule, x in g.items():
    print(rule, x)
print("B", round(cond["plant_stream"]["B"], 2), "expected", round(cond["plant_stream"]["expected_first_order"], 2), "plant_beats_null2", cond["plant_stream"]["plant_beats_null2"])
for r in cond["records"]:
    if r["rule"] == "WEB-S":
        print("WEB-S seed", r["seed"], "kept", r["plant"]["kept"], "C", None if r["plant"]["C"] is None else round(r["plant"]["C"], 1), "n_frames", r["n_frames"])
