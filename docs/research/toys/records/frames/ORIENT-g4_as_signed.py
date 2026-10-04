import json
from tools.toys.frames import gates as GT
r = GT.g4()          # the signed defaults: 3,000 moments, replicate seed 1, a plant after every 10th, ten WEB-S seeds, 100 draws
print("ok", r["ok"], "plants (train, held)", r["plants"], "B", round(r["B"], 2), "plant_beats_null2", r["plant_beats_null2"])
for rule, g in r["gates"].items():
    print(rule, g)
print("control", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r["control"].items()})
print("failures", r["failures"])
