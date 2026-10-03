"""result_figure_check.py — every number of RESULT-TOY-FRAMES.md against the report it is written from: «every figure from its file» as a script, not a sentence.

# edit: Claude (Sonnet 5.5, swarm toys), written with the RESULT (the minute of the run is in the RESULT's own foot note).
usage: python3 result_figure_check.py <RESULT.md> <REPORT.txt> [extra reference files...]
A number counts as found when its digits occur (thousands commas removed, a leading minus or plus sign ignored) in the report or in an extra reference file. Dates, shas and section numbers are ignored by pattern.
"""
import re
import sys

res = open(sys.argv[1]).read()
ref = "\n".join(open(p, errors="replace").read() for p in sys.argv[2:])
ref_n = ref.replace(",", "")
# drop what is not a figure: fenced code, urls, shas, dates/times, commit-like tokens, section signs
res2 = re.sub(r"`[^`]*`", " ", res)
res2 = re.sub(r"\b[0-9a-f]{7,64}\b", " ", res2)
res2 = re.sub(r"\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?( \+\d{4})?", " ", res2)
res2 = re.sub(r"§\s*\d+(\.\d+)*|#\d+|\b[A-Z]{1,3}\d*[-–]\d+\b|\bP-C\d\b|\bG\d\b|\bAMENDMENT[- ]\d\b|\bF\d+\b", " ", res2)
nums = []
for m in re.finditer(r"(?<![\w.])[-+−]?\d[\d,]*\.?\d*(?![\w])", res2):
    s = m.group(0).replace(",", "").lstrip("-+−").rstrip(".")
    if len(s.replace(".", "")) >= 3 or "." in s:
        nums.append(s)
seen, missing = set(), []
for s in nums:
    if s in seen:
        continue
    seen.add(s)
    if s not in ref_n:
        missing.append(s)
print(f"{len(seen)} distinct figures of three or more digits (or with a decimal point); {len(missing)} not found in the references:")
print(" ".join(missing))
