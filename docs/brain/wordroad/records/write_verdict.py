# the writer of docs/brain/wordroad/VERDICT-WORD-ROAD.md: every figure is read from the gate's own file (gate.json) and clock
import json
import sys
from pathlib import Path

now, gate_json, clock_txt, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
suites = sys.argv[5] if len(sys.argv) > 5 else None
g = json.loads(gate_json.read_text())
v, S = g["verdict"], g["seeds"]
clock = clock_txt.read_text().splitlines()


def f(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def tri(fn, d=3):
    return " / ".join(f(fn(s), d) if not isinstance(fn(s), (int, str)) else str(fn(s)) for s in S)


def pf(b):
    return "PASS" if b else "FAIL"


L = []
A = L.append
A("# VERDICT WORD-ROAD, stage 1 — the organism meets every word of an utterance (the gene `HEAR`), graded on replays of the closed lean lives")
A("")
A(f"*Claude (Fable 5.1, the seat), {now}. The law: `PREREG-WORD-ROAD.md` in this folder, signed by both on the final text (sha256 7ed1d132…). "
  f"The gate was read once. Every figure below is read from `{gate_json}`.*")
A("")
marks = [("I1", v["I1"]), ("I2", v["I2"]), ("A", v["A"]), ("P", v["P_pass"]), ("K", v["K"]["pass"]), ("K2", v["K2"]["pass"]),
         ("G", v["G"]), ("C", v["C"])]
failed = [k for k, x in marks if not x]
A("## The verdict")
if v["ADOPT"]:
    A("1. **Every mark passes. `HEAR` becomes the law of the next LEAN brain lives.** The templates BRAIN-LEAN and BRAIN-LEAN-TWIN take the line together. The full organism waits for stage 2.")
else:
    A(f"1. **`HEAR` is NOT adopted as written.** The mark{'s' if len(failed) > 1 else ''} that failed: {', '.join(failed)}. The decision rule of §4 asks for every mark at every seed.")
P1, P3 = v["P"]["M1"], v["P"]["M3"]
A(f"2. **Do the cells point by a size or colour word they now hear?** On the items that NEED the word, the whole phrase is right {f(P1['pooled']['full'])} of the time on test 1 "
  f"and {f(P3['pooled']['full'])} on test 3; the shape word alone, in the same cells, {f(P1['pooled']['alone'])} and {f(P3['pooled']['alone'])}. "
  f"The gaps are {P1['pooled']['gap']:+.3f} (n {P1['pooled']['n']}, p {P1['pooled']['p']:.1e}) and {P3['pooled']['gap']:+.3f} (n {P3['pooled']['n']}, p {P3['pooled']['p']:.1e}); the bar is + 0.10 with p < 0.001.")
A(f"3. **The old ability:** test 1 on the phrases OFF could already answer reads ON {f(v['K']['a'])} against OFF {f(v['K']['b'])} (n {v['K']['n']}); "
  f"«I don't know» by the grader's rule reads ON {f(v['K2']['a'])} against OFF {f(v['K2']['b'])} (n {v['K2']['n']}).")
A(f"4. **The price:** the mind's cost per training canvas is × {tri(lambda s: s['C']['ratio'])} of OFF's at the three seeds (bar ≤ 1.5).")
A("")
A("## The marks, per world seed (20261101 / 20261102 / 20261103)")
A("| Mark | What was read | The reading | Bar | Verdict |")
A("|---|---|---|---|---|")
A(f"| I1 | the line absent: the twin's replay against rung 2's recorded twin journal; the BRAIN genome's against the life's journal | exits {tri(lambda s: s['I']['i1-twin']['exit'])} (rows {tri(lambda s: s['I']['i1-twin']['rows'])}) and {tri(lambda s: s['I']['i1-brain']['exit'])} (rows {tri(lambda s: s['I']['i1-brain']['rows'])}) | every row equal | **{pf(v['I1'])}** |")
A(f"| I2 | ON against OFF, `words` masked: the first difference | seq {tri(lambda s: (s['I']['I2']['first_difference'] or [None])[0])}; the first multi-word canvas is scene {tri(lambda s: s['I']['I2']['first_multi_word_canvas']['scene'])}, eye seq {tri(lambda s: s['I']['I2']['first_multi_word_canvas']['eye_seq'])} | they differ, first there | **{pf(v['I2'])}** |")
for m, name in (("M1", "test 1"), ("M3", "test 3")):
    A(f"| A · {name} | phrases the road can be asked (not «unheard») | ON {tri(lambda s: s['A'][m]['on']['answerable'])} of {tri(lambda s: s['A'][m]['on']['n'])}; OFF {tri(lambda s: s['A'][m]['off']['answerable'])} | = 1.000 | **{pf(all(s['A'][m]['pass'] for s in S))}** |")
for m, name in (("M1", "test 1"), ("M3", "test 3")):
    A(f"| P · {name} | NEEDED items (n {tri(lambda s: s['P'][m]['n'])}): the whole phrase · the shape word alone · the gap | {tri(lambda s: s['P'][m]['full'])} · {tri(lambda s: s['P'][m]['alone'])} · {tri(lambda s: s['P'][m]['gap'])} | pooled gap ≥ 0.10, p < 0.001; above 0 at every seed; above every NULL-10 draw | **{pf(v['P'][m]['pass'])}** |")
A(f"| K | test 1 where OFF could answer (n {tri(lambda s: s['K']['n'])}): ON · OFF | {tri(lambda s: s['K']['a'])} · {tri(lambda s: s['K']['b'])} | pooled ON − OFF ≥ − 0.05 | **{pf(v['K']['pass'])}** |")
A(f"| K2 | never-taught shapes, both sets (n {tri(lambda s: s['K2']['n'])}): ON · OFF | {tri(lambda s: s['K2']['a'])} · {tri(lambda s: s['K2']['b'])} | pooled ON − OFF ≥ − 0.05 | **{pf(v['K2']['pass'])}** |")
A(f"| G | word cells; canvases where the word cells born are not the words first heard | ON {tri(lambda s: len(s['G']['word_cells_on']))} cells, OFF {tri(lambda s: len(s['G']['word_cells_off']))}; wrong canvases {tri(lambda s: len(s['G']['on']['canvases_wrong']))} of {tri(lambda s: s['G']['on']['canvases_read'])} | 14 words, each born where first heard | **{pf(v['G'])}** |")
A(f"| C | ms per training canvas, scenes 9,000–9,999: ON · OFF · ratio | {tri(lambda s: s['C']['on']['mean_ms'], 2)} · {tri(lambda s: s['C']['off']['mean_ms'], 2)} · {tri(lambda s: s['C']['ratio'])} | ≤ 1.5 | **{pf(v['C'])}** |")
A("")
A("## P, pooled over the three seeds")
A("| Test | n | the whole phrase | the shape word alone | gap | pairs for / against | p (exact, one-sided) | above 0 at every seed | NULL-10 at 20261102: ON against the draws' highest | Verdict |")
A("|---|---|---|---|---|---|---|---|---|---|")
for m, name in (("M1", "1"), ("M3", "3")):
    p, q, nul = v["P"][m], v["P"][m]["pooled"], v["P"][m]["null"]
    A(f"| {name} | {q['n']} | {f(q['full'])} | {f(q['alone'])} | {q['gap']:+.3f} | {q['f']} / {q['u']} | {q['p']:.2e} | {p['gap_above_0_at_every_seed']} | "
      + ("not read" if nul is None else f"{f(nul['on'])} against {f(nul['max'])}: above every draw {nul['above_every_draw']}") + f" | **{pf(p['pass'])}** |")
A("")
if g.get("nulls"):
    A("NULL-10's ten draws (the whole phrase, the same items, utterances shuffled among the scenes): test 1 "
      + ", ".join(f(x) for x in g["nulls"]["M1"]) + " · test 3 " + ", ".join(f(x) for x in g["nulls"]["M3"]) + ".")
    A("")
A("**Readings beside P, never graded** (per seed):")
for m, name in (("M1", "test 1"), ("M3", "test 3")):
    A(f"- {name}: chance (1 / hypotheses) {tri(lambda s: s['P'][m]['reading_chance']['chance'])}, exact p of the whole phrase against it {' / '.join(format(s['P'][m]['reading_chance']['p_exact'], '.1e') for s in S)}; "
      f"a road with a perfect shape word and no other {tri(lambda s: s['P'][m]['reading_shape_only_road'])}; the most-fixations pointer {tri(lambda s: s['P'][m]['reading_most_fixations'])}; "
      f"«none» read forced: {tri(lambda s: s['P'][m]['full_none'])} of the whole phrase, {tri(lambda s: s['P'][m]['alone_none'])} of the shape word alone; items with an «unheard» phrase {tri(lambda s: len(s['P_unheard']))}.")
A("")
A("## K and K2 are point rules (the PREREG says so)")
for key, name in (("K", "K"), ("K2", "K2")):
    k = v[key]
    A(f"- **{name}**, pooled n {k['n']}: ON − OFF {k['diff']:+.3f} ± {f(k['se'])}; pairs {k['f']} for ON, {k['u']} for OFF; the exact sign test for «ON lower» p {f(k['p_a_lower'], 4)}.")
A(f"- **K2's words.** «I don't know» share: ON {tri(lambda s: s['K2']['idk_share']['on'])}, OFF {tri(lambda s: s['K2']['idk_share']['off'])}. Words emitted by kind, ON: "
  + " / ".join(str(s["K2"]["words_emitted_by_kind"]["on"]) for s in S) + "; OFF: " + " / ".join(str(s["K2"]["words_emitted_by_kind"]["off"]) for s in S) + ".")
A("")
A("## G's readings (they decide nothing here; they price stage 2)")
A(f"- Sight cells ON / OFF at the end: {tri(lambda s: s['G']['readings']['sight_cells_on_over_off'])}. Births refused by the budget ON / OFF: {tri(lambda s: s['G']['readings']['refused_budget_on_over_off'])}. Refused as redundant ON / OFF: {tri(lambda s: s['G']['readings']['refused_redundant_on_over_off'])}.")
A(f"- Refused by the cap: {' / '.join(str(s['G']['readings']['births_refused_nmax']) for s in S)}. A word cell two words lit: {tri(lambda s: s['G']['hear_shared_cell'])}. Words the ear refused: {tri(lambda s: s['G']['hear_words_refused'])}.")
A("")
A("The series at 20261102, every 1,000 worded canvases (ON / OFF):")
A("")
A("| canvases | sight cells | refused by budget | refused redundant |")
A("|---|---|---|---|")
s2 = next(s for s in S if s["world_seed"] == 20261102)
for a, b in zip(s2["G"]["series"]["on"], s2["G"]["series"]["off"]):
    A(f"| {a['canvases']:,} | {a['cells_sight']:,} / {b['cells_sight']:,} | {a['births_refused_budget']:,} / {b['births_refused_budget']:,} | {a['births_refused_redundant']:,} / {b['births_refused_redundant']:,} |")
A("")
A("## The runs")
A("```")
for line in clock:
    A(line)
A("```")
if suites:
    A("")
    A("## The suites on the gate's commit")
    A("```")
    for line in Path(suites).read_text().splitlines():
        A(line)
    A("```")
A("")
A("## What this does and does not show")
A("- **Shown:** under the line every word has a cell named by itself; every pointing phrase can be asked; and the figures above.")
A("- **Not shown:** anything about the full organism. Stage 2 widens SLEEP, PREDICT, SURPRISE and the think road, each under its own signed line, before `HEAR` stands beside them.")
A("- **Not shown:** that the organism uses its brain. That wiring is its own build.")
A("- A and G are wiring pins. K and K2 are point rules, underpowered as tests. NULL-10 is one seed. C prices a replay of the lean body, never a life under the unit.")
A("- The test sets were read before for the brain. For the organs' road under `HEAR` this was the first read, and no value of the law was chosen on them.")
out.write_text("\n".join(L) + "\n")
print(len(L), "lines →", out)
