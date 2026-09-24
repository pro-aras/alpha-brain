# resolve the three conflict hunks of tools/verdict_g4.py (reader v3.5 merge) — both sides land, additive
import sys, re
p = "/data/dev/genome-wt-reader35/tools/verdict_g4.py"
s = open(p).read()
STAMP = sys.argv[1]

# ---------- hunk 1: the header / READER_VERSION
h1_start = s.index("<<<<<<< HEAD\nREADER_VERSION = (\"tools/verdict_g4.py v3.3")
h1_mid = s.index("=======\n", h1_start)
h1_end = s.index(">>>>>>> master\n", h1_mid)
theirs = s[h1_mid + len("=======\n"):h1_end]          # master: the v3.4 edit comment + READER_VERSION v3.4
assert theirs.startswith("# edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — v3.4")
v34_comment = theirs[:theirs.index("READER_VERSION = (")]
new_h1 = (v34_comment +
    f"# edit: Claude (Opus 5.5, reader v3.5 builder), {STAMP} — v3.5: THE RECONCILIATION (docs/briefs/READER-V35-REPORT.md): master's v3.4 (READER-LAG-0923,\n"
    "# the read CUT at the mind's last consumed seq) merged with a4-integration's v3.3-line ladder additions (A4L-VOICE's twins and HEAR/VOICE_HARM/\n"
    "# SOUND_CELLS, A4L-LANG's blind-chat twin and CHAT L1-L9, A4L-COST's HASH and the witness beside COST) — both sides kept whole, the three\n"
    "# conflicting hunks (this header, the COST dict, the COST row) resolved additively.\n"
    "READER_VERSION = (\"tools/verdict_g4.py v3.5 (2026-09-24: v3.4 + a4-integration's ladder marks — A4L-VOICE's voice twins blind-ear/blind-sound/T-shuffle-sound \"\n"
    "                  \"when AREA sound is declared and the marks HEAR/VOICE_HARM/SOUND_CELLS; A4L-LANG's blind-chat twin and CHAT L1-L9; A4L-COST's HASH mark \"\n"
    "                  \"and the per-row witness's form and ms beside COST; v3.4: \" + \n"
    "                  \"READER-LAG-0923 — the read is CUT at the mind's last consumed seq when the mind is \"\n"
    "                  \"behind its world (ledger/STATUS last_seq, the journal's last mind row on a closed record): every twin replays the cut tape, \"\n"
    "                  \"closed_whole is judged against the cut, every mark reads the cut; ALIVE reads the world's hours and gaps, the mind's counters over \"\n"
    "                  \"the hours it lived; the unconsumed tail printed under ALIVE, COST and REPLAY; v3.3: EVOLVE's void round apart; COST as §8b's \"\n"
    "                  \"function of cells; ACT's census over the game's acts, ≥ 95 % on the last 100; SENTENCE's missions per episode; QUESTION once per \"\n"
    "                  \"question, the lexicon counted; READ's fixed-seed sample of shelf-only words + its blind twin; THREAD's gaps attributed to sleeps; \"\n"
    "                  \"STAGE's readiness series + the mind's stage events carried; not gradable never failed; the plant clauses not gradable before the plant)\")\n")
s = s[:h1_start] + new_h1 + s[h1_end + len(">>>>>>> master\n"):]

# ---------- hunk 2: the §8b COST dict — both the witness keys (a4-integration) and the lag (master)
h2 = ("<<<<<<< HEAD\n"
      "         \"sleeps_in_window\": sleeps_in_window, \"g4_7\": g47,\n"
      "         \"hash_form\": g47.get(\"hash_form\", \"not recorded\"), \"hash_ms_last\": g47.get(\"hash_ms_last\", \"not recorded\"),   # A4L-COST task 5, carried onto the §8b form at the merge\n"
      "=======\n"
      "         \"sleeps_in_window\": sleeps_in_window, \"g4_7\": g47, **({\"lag\": lag} if lag is not None else {}),\n"
      ">>>>>>> master\n")
assert s.count(h2) == 1, "hunk 2 not found verbatim"
new_h2 = ("         \"sleeps_in_window\": sleeps_in_window, \"g4_7\": g47, **({\"lag\": lag} if lag is not None else {}),   # READER-LAG-0923 (master)\n"
          "         \"hash_form\": g47.get(\"hash_form\", \"not recorded\"), \"hash_ms_last\": g47.get(\"hash_ms_last\", \"not recorded\"),   # A4L-COST task 5, carried onto the §8b form at the merge\n")
s = s.replace(h2, new_h2)

# ---------- hunk 3: the COST row — a4-integration's one renderer, carrying master's lag clauses
h3_start = s.index("<<<<<<< HEAD\n    m = M[\"viii_cost\"]; L.append(cost_line(m, gv))")
h3_end = s.index(">>>>>>> master\n", h3_start) + len(">>>>>>> master\n")
new_h3 = (f"    # edit: Claude (Opus 5.5, reader v3.5 builder), {STAMP} — the merge: a4-integration's ONE renderer (cost_line) now carries master's\n"
          "    # READER-LAG-0923 clauses (the sleeps window's end and the lag text); `_LS` is the fallback when the mark carries no lag of its own.\n"
          "    m = M[\"viii_cost\"]; L.append(cost_line(m, gv, _LS))   # A4L-COST: one renderer (cost_line, above) for both forms — the witness beside the cost\n")
s = s[:h3_start] + new_h3 + s[h3_end:]

# ---------- cost_line: master's two lag additions folded into the one renderer (both forms)
old_cl = s[s.index("def cost_line(m: dict, gv=None) -> str:"):s.index("# edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (2): ALPHA4-PREREG §8b's COST bar")]
assert "sleeps in its last 3 min {m.get('sleeps_in_window')} · RSS" in old_cl
new_cl = old_cl
new_cl = new_cl.replace("def cost_line(m: dict, gv=None) -> str:\n",
    "def cost_line(m: dict, gv=None, ls: Optional[dict] = None) -> str:\n"
    f"    # edit: Claude (Opus 5.5, reader v3.5 builder), {STAMP} — the v3.5 merge: master's READER-LAG-0923 row clauses (the sleeps window's end;\n"
    "    # `lag_text(m['lag'] or ls)` after the reason, on BOTH forms) folded into this one renderer; `ls` = write_verdict's lag summary.\n")
new_cl = new_cl.replace("    tail = f\"{hash_part}{(' · ' + m['reason']) if m.get('reason') else ''} | {gv(m)} |\"\n",
    "    tail = f\"{hash_part}{(' · ' + m['reason']) if m.get('reason') else ''} · {lag_text(m.get('lag') or ls or {})} | {gv(m)} |\"\n")
new_cl = new_cl.replace("sleeps in its last 3 min {m.get('sleeps_in_window')} · RSS",
    "sleeps in its last 3 min {m.get('sleeps_in_window')} (window end: {(m.get('lag') or {}).get('sleeps_window_end_is', 'STATUS heartbeat_at')}) · RSS")
assert new_cl != old_cl
s = s.replace(old_cl, new_cl)
assert "<<<<<<<" not in s and ">>>>>>>" not in s and "\n=======\n" not in s
open(p, "w").write(s)
print("resolved")
