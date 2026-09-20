# BRIEF — Builder A: WAVE 3 clauses W3-0 (the generic refusal) + W3-3 (sleep_boundary)
*edit: Claude (Fable 5.1), 2026-09-20 22:33 +0400. You are a Sonnet 5 builder. The law is `docs/G4-PREREG.md` (§1–§16) and `docs/G4-WAVE3-CLAUSES.md` (W3-0, W3-3). An unimplementable clause is RAISED in your report, never worked around; a failed toy is a result, never a moved bar.*

## Where you work
- Worktree `/data/dev/genome-wt-d`, branch `g4-wave3-a` (already created from master a21858b+docs). Python 3.14, numpy 2.3, Pillow; **unittest**: write every suite's output to a file and read its own `Ran N … OK` line (`python3 -m unittest discover -s tests/creature -t . > /tmp/wt-d-creature.log 2>&1`; same for `tests/genome`).
- You OWN: `creature/mind.py`, `creature/body.py`, a new `creature/genes.py`, and `tests/creature/`. You NEVER edit `genome/*` (Builder B's), `tools/*`, `deploy/*`, `docs/G4-PREREG.md`, and you never touch `/data/dev/genome` (master — a live creature runs from it), `/data/dev/genome/run*`, or any systemd unit. No deletes. No restarts.
- Edit attribution: every edited region gets `# edit: Claude (Sonnet 5, W3 builder A), <date "+%Y-%m-%d %H:%M %z" run at write time> — <what>`; commit after every task on your branch.
- **Gates that must stay green after every task:** `tests/genome/test_pin_skeleton.py` (the pin d4b5c6b8… must not move), `python3 tools/gate_g4.py --tree /data/dev/genome-wt-d` (G4-1..3 with controls), both suites' OK lines, and `tests/creature/test_arrival.py` (the ARRIVAL road) — read from their log files.

## W3-0 — THE GENERIC REFUSAL (docs/G4-WAVE3-CLAUSES.md W3-0)
1. `creature/genes.py`: ONE registry of the genes the machinery RUNS, with the code site that runs each — `RUNS = {"machinery": {...}, "body": {...}, "mind": {...}}`, each value a short string naming the file and function (e.g. `"BUDGET": "genome/machinery.py:_birth"`). Build it by READING the code (grep `declared[`, `in self.genome.declared`, the parser's `required` set): a gene goes in only if you can name the line that consumes it. `unwired(declared: dict) -> list[str]` returns every declared gene missing from the union, sorted. Keep TRAITS as an explicit refusal row until W3-4 lands (`"TRAITS": None` → always unwired, with the reason).
2. `Mind.__init__` calls `unwired(self.genome.declared)` FIRST and raises `GenomeError("<GENE> is declared but nothing runs it (W3-0): …")` naming every offender; the existing TRAITS refusal becomes that path.
3. Toy `tests/creature/test_refusal.py`: (a) positive — `genome/G4.genome` starts a Mind in a temp root; (b) `G4.genome` + a line `INDUCE   rule from 5 episodes no counter` refuses, naming INDUCE; (c) the planted control — a `Genome` whose `declared` carries a made-up key (`PLANTED`) refuses naming it; (d) every gene in `RUNS` is a gene the parser knows (`parse_genome` of a genome text carrying each clause does not raise "unknown gene") — this pins the registry to the parser.
4. Report the full table (gene → site) — it is the deliverable Claude reads.

## W3-3 — `Interests.sleep_boundary()` WIRED (one line + one test)
- In `Mind._maybe_sleep`, after the SLEEP journal row: `if self.interests is not None: self.interests.sleep_boundary()` (read `genome/curiosity.py` lines ~120–135 for the contract).
- Toy `tests/creature/test_sleep_boundary.py`: read how `Interests` records an "answered" window (`_window_answered`) and write the test the clause names: a recombine chain never pairs an answer from before a sleep with one after it — plant one answered item before a sleep and one after; with the wiring, `_window_answered` is empty after the sleep (or the recombine that would pair them does not fire); WITHOUT the wiring (monkeypatch `sleep_boundary` to a no-op) it does — the negative control.

## Also (small, yours because the file is yours)
- `Mind.think_counters` gains `"revisits": 0, "extensions": 0, "clashes": 0` (all three written on every STATUS write — body.py already spreads think_counters). When `think_laws.believe(...)` returns a dict with `"kind"` in `{"belief","revisit","extension","clash"}` (Builder B's W3-1 interface; today it returns a belief row), count it in the matching counter; today's code counts `beliefs` only — keep that working when the key is absent. Do not wait for B: code against the interface, test with a stub.

## Report — `docs/briefs/W3-BUILDER-A-REPORT.md` in your worktree, committed
Per task: the log's OK line verbatim, the commit hash, the pin hash before/after, gate_g4's three lines, the RUNS table, every clause you could not meet with the reason. Nothing else. When done, stop; Claude merges — you never merge to master.
