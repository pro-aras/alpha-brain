"""revise_bench.py — the REVISE-1 bench (PREREG-REVISE-1; docs/brain/revise/, signed 2026-10-09 23:39,
revise-1009 @ 66eaffa). An INSTRUMENT: tools/ only, zero organism edits.

edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:03 +0400 — the law's bench, written AFTER
its G-UNIT tests (ed9533e, RED-proven on the law commit). One run drives all three benches and writes
the report:

    python3 -B tools/brain/revise_bench.py OUTDIR

TIER 1 — scripted (word, cells, episodes, moment) streams through the REAL genome.think.believe into a
scratch store; a planted two-word world (W the target, X the bystander, believed once and never touched
again); FIVE shapes (a removal-flip / b partial removal / c growth / d sameness / e ledger-reassign with
the cells UNCHANGED — the wild's own clash shape), every call carrying a minimal planted ledger (never
None); the ORDER null (10 seeded derangements of (a)'s AAABBB, both monotone orders excluded); the
mechanism's own OFF-switch control (clash_enabled=False).

TIER 2 — the N1 bench's own toy genome + its 8 things (imported from precision_bench, never copied),
lived from declared seeds; the planted naming flip (thing A's visual named with thing B's word from the
flip moment on); the production call chain driven at declared checkpoints (G-CHAIN: the SAME two
functions creature/mind.py:3350/3385 calls — questions_why -> think_laws.believe — imported, pinned by
tests/tools/test_revise_bench.py). The PILOT's population count (cells-before/cells-after) prints BEFORE
the marks bind; a flip that never moves the answering cells in the removal sense reads NOT-GRADABLE and
the bench REFUSES to grade (the law §1/§4).

BENCH B — planted web.Claim rows on scripted observation streams: the exact crossing, the min_events
floor, the sign null.

Bench decisions the law left to the builder (written down, never guessed silently — the think.py
pattern; each priced by scratch probes run before this module was written, the law's own constants
declared here BEFORE any graded run):

  D-stream  the tier-1 call sequences: (a) AAABBB (the order null's own ordered form), (b) A P P,
            (c) A G G, (d) A A A, (e) L0 L1 L1 (cells [11,22] throughout; the planted ledger reassigns
            cell 11 to the foreign word «q» at L1). X planted once ([98,99], episode 0, moment 100);
            W's call k carries episode [k], moment 100+k. The ledger maps every W cell to {w} (and X's
            to {x}), so only the REMOVED half of rule 4 fires in (a)/(b); L1 fires the ledger half in (e).
  D-draw    the derangement family = the 20 multiset permutations of AAABBB minus both monotone orders
            (18 remain, each >= 2 boundaries by construction); the draw = rng.permutation(18)[:10] at
            DERA_SEED (numpy default_rng), pinned literally in the tests.
  D-flip    the naming flip is ONE-WAY — the law's parenthetical read literally: «the parent names thing
            A's visual with thing B's word from then on»; thing B's own showings keep their name (the
            word B then hears two visuals — the counterevidence mixes in the word's own stream, and the
            pilot's shares read exactly that mixing). Priced by probe: A=bar, B=ring (per-thing purity
            1.000/1.000 at the pre-flip horizon, zero cross-confusion either way; the star/circle pair
            sits at 0.70/0.24 — confusable, rejected).
  D-sched   checkpoints: the pre-flip pass at round R_PRE-1 drives the chain for ALL 8 things' words
            (in THINGS order — the bystanders' rows are planted there, frozen from then on); post-flip
            checkpoints at lags (25, 50, 100, 200) rounds drive the flipped word only. R_PRE=50,
            R_POST=200 (2000 moments — the N1 bench's own class; measured ~1.3 s a life in the probe).
  D-drive   the toy world is lived with plain org.moment(x, xw) (lr_scale=1.0, the machinery's exact
            default) — the N1 bench's Predictor is N1's own assay instrument, not part of the toy form
            the law names. Episodes: the bench writes the FAST ring the way the mind's moment road does
            (moment, x_s, x_w, word; surprise=0.0 declared — why()/believe() never read it).
  D-grade   every share is graded against the organism's FINAL state (the bench reads at the end — the
            only organism there is), through induce's own _nearest_in (the law §3 M-T2-DIR's named
            geometry). «The flipped word's post-flip episodes» = every episode whose word is B_WORD and
            whose moment >= the flip moment (under D-flip both visuals mix in it — printed).
  D-margin  M-T2-DIR's margin = the pilot's own (post_share - pre_share_post), printed with n and the
            smallest passing gap 10/n (#245(5)); UNDERPOWERED named if below it; never tuned after the
            graded run. The pilot and the graded flip twin carry DIFFERENT declared seeds (the margin
            never fits the graded run).
  D-move    the pilot's population count classifies cells-before -> cells-after per checkpoint:
            disjoint / partial / shrank carry a REMOVAL (gradable — M-T2-MOVE's «a cell removed, or a
            clash row»); grew-only / unchanged never move in the law's sense -> NOT-GRADABLE (the
            verdict form §4 FAIL-FORM road: named, the amendment re-prices the bench).
  D-det     the byte-identical artifacts (G-DET): arms.jsonl, report.json, report.txt, stores/*.jsonl.
            cost.json (M-COST's measured price: process_time per arm + peak RSS) is the ONE declared
            nondeterministic artifact — timings — excluded from byte-identity by construction.
  D-local   M-T2-LOCAL reads the 7 bystander words' RAW store bytes (every believed word except the
            flipped one), pre-flip pass vs each post-flip checkpoint; presence counts printed.
"""
from __future__ import annotations

import itertools
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

from genome import world
from genome.fast import Episodes
from genome.machinery import Organism, parse_genome, retina
from genome.questions import build_ledgers, why as questions_why   # the SAME object mind.py imports (G-CHAIN)
from genome import think as think_laws                             # the SAME module object mind.py uses (G-CHAIN)
from genome.think import _nearest_in                               # induce's own geometry (the law §3 M-T2-DIR)
from genome.web import Claim
from tools.brain.precision_bench import TOY, POOL_B                # the N1 bench's own genome + 8 things

# ----------------------------------------------------------------------------- tier 1 (the store's law)
T1_WORD, T1_BYSTANDER = "w", "x"
T1_CELLS = {"A": [11, 22], "B": [33, 44], "P": [22, 33], "G": [11, 22, 33], "X": [98, 99]}
T1_CALLS = {"a": ["A", "A", "A", "B", "B", "B"],
            "b": ["A", "P", "P"],
            "c": ["A", "G", "G"],
            "d": ["A", "A", "A"],
            "e": ["L0", "L1", "L1"]}                              # (e): cells unchanged; the LEDGER drifts
T1_SHAPES = ("a", "b", "c", "d", "e")

DERA_SEED = 20261010
DERA_N = 10


def t1_ledger(which: str):
    """The minimal planted ledger (never None — the production call passes one, so does every stream).
    L0: every W cell answers {w}; X's cells {x}. L1: cell 11 reassigned to the foreign word «q» —
    the drifted-label shape of both wild clashes (bl5 «do»/«music», the law §0)."""
    sight = {c: {T1_WORD} for c in (11, 22, 33, 44)}
    sight.update({c: {T1_BYSTANDER} for c in (98, 99)})
    if which == "L1":
        sight[11] = {"q"}
    return {"sight": sight, "words": {}}


def run_tier1_stream(shape: str, store_dir, clash_enabled: bool = True) -> dict:
    """One planted two-word world: X believed once, then W's declared call sequence through the real
    believe(); X's raw bytes captured after EVERY call (the locality checkpoints)."""
    store = Path(store_dir)
    store.mkdir(parents=True, exist_ok=True)
    path = store / f"tier1-{shape}.jsonl"
    planted = think_laws.believe(T1_BYSTANDER, T1_CELLS["X"], [0], 100, path,
                                 ledgers=t1_ledger("L0"), clash_enabled=clash_enabled)
    x_bytes = [x_chain_bytes(path)]
    returned_rows, returned_kinds = [], []
    for k, letter in enumerate(T1_CALLS[shape], start=1):
        if shape == "e":
            cells, led = T1_CELLS["A"], t1_ledger(letter)
        else:
            cells, led = T1_CELLS[letter], t1_ledger("L0")
        row = think_laws.believe(T1_WORD, cells, [k], 100 + k, path,
                                 ledgers=led, clash_enabled=clash_enabled)
        returned_rows.append(row)
        returned_kinds.append(row.get("kind"))
        x_bytes.append(x_chain_bytes(path))
    disk_rows = think_laws.read_beliefs(path)
    folded = {r["word"]: r for r in think_laws.read_beliefs(path, fold=True)}
    return {"shape": shape, "planted": planted, "calls": T1_CALLS[shape],
            "clash_enabled": clash_enabled,
            "returned_rows": returned_rows, "returned_kinds": returned_kinds,
            "disk_rows": disk_rows, "disk_kinds": [r["kind"] for r in disk_rows],
            "standing": folded.get(T1_WORD),
            "clash_count": sum(1 for r in disk_rows if r["kind"] == "clash" and r.get("word") == T1_WORD),
            "x_bytes": x_bytes, "x_presence": len(x_bytes[0])}


def run_tier1(store_dir, clash_enabled: bool = True) -> dict:
    root = Path(store_dir)
    return {s: run_tier1_stream(s, root / f"s-{s}", clash_enabled=clash_enabled) for s in T1_SHAPES}


def x_chain_bytes(store_path) -> list:
    """The bystander's RAW line bytes (the locality instrument reads bytes, never parsed prose)."""
    p = Path(store_path)
    if not p.exists():
        return []
    out = []
    with open(p) as f:
        for line in f:
            if line.strip() and json.loads(line).get("word") == T1_BYSTANDER:
                out.append(line)
    return out


def locality_violations(snapshots: list) -> list:
    """Checkpoint indexes whose bystander bytes differ from the first checkpoint's. [] = locality holds."""
    base = snapshots[0]
    return [i for i, s in enumerate(snapshots) if s != base]


# --- the ORDER null ----------------------------------------------------------
def derangement_family() -> list:
    """The 20 multiset permutations of AAABBB minus the two monotone orders (both read exactly 1
    boundary — the draw's family is the 18 with >= 2)."""
    fam = sorted("".join(p) for p in set(itertools.permutations("AAABBB")))
    return [s for s in fam if s not in ("AAABBB", "BBBAAA")]


def _derangement_draws() -> list:
    rng = np.random.default_rng(DERA_SEED)
    fam = derangement_family()
    return [fam[int(i)] for i in rng.permutation(len(fam))[:DERA_N]]


DERA_DRAWS = _derangement_draws()   # declared, fixed before any run; pinned literally in the tests


def boundary_count(seq: str) -> int:
    """The sequence's standing-boundary count — with disjoint planted sets the store's own arithmetic
    makes a clash fire exactly at each boundary (the verifier read's construction)."""
    return sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])


def run_order_null(store_dir) -> dict:
    """The ordered flip (AAABBB — stream (a)'s own sequence) + the 10 seeded derangements."""
    root = Path(store_dir)

    def one(seq, tag):
        store = root / tag
        store.mkdir(parents=True, exist_ok=True)
        path = store / "beliefs.jsonl"
        think_laws.believe(T1_BYSTANDER, T1_CELLS["X"], [0], 100, path, ledgers=t1_ledger("L0"))
        for k, letter in enumerate(seq, start=1):
            think_laws.believe(T1_WORD, T1_CELLS[letter], [k], 100 + k, path, ledgers=t1_ledger("L0"))
        rows = think_laws.read_beliefs(path)
        clashes = sum(1 for r in rows if r["kind"] == "clash")
        standing = {r["word"]: r for r in think_laws.read_beliefs(path, fold=True)}[T1_WORD]
        return {"seq": seq, "clashes": clashes, "boundaries": boundary_count(seq),
                "standing": standing["cells"]}

    ordered = one("AAABBB", "ordered")
    draws = [one(seq, f"draw{i}") for i, seq in enumerate(DERA_DRAWS)]
    return {"ordered_seq": "AAABBB", "ordered_clashes": ordered["clashes"],
            "ordered_boundaries": ordered["boundaries"], "ordered_standing": ordered["standing"],
            "draws": draws, "n_draws": len(draws)}


# --- bench B (the claims' demotion, exact) -----------------------------------
B_LEVEL = 0.05
B_MIN_EVENTS = 30
B_N_CONFIRM = 30
B_N_CONTRA = 5
B_USUALLY_LEVEL = 0.9
B_N_FLOOR = 29
B_N_SIGN = B_N_CONFIRM + B_N_CONTRA   # the sign null carries the SAME event count (35)


def run_bench_b() -> dict:
    """Planted Claims on scripted observation streams (web.py:366-382's own arithmetic: level 0.05,
    floor 30 — 1/31 = 0.0323 holds, 2/32 = 0.0625 crosses; the demotion lands AT the 2nd
    contradiction, event index 32)."""
    always = Claim("B-ALWAYS", "the bench's planted always claim", "always", B_LEVEL,
                   min_events=B_MIN_EVENTS)
    states = []
    for k in range(1, B_N_CONFIRM + 1):
        always.observe(True, at=k)
        states.append(always.state)
    for k in range(B_N_CONFIRM + 1, B_N_CONFIRM + 1 + B_N_CONTRA):
        always.observe(False, at=k)
        states.append(always.state)
    crossing = next((i + 1 for i, s in enumerate(states) if s == "demoted"), None)
    a_out = {"states": states, "crossing": crossing, "first_demoted_at": always.first_demoted_at,
             "confirmed": always.confirmed, "contradicted": always.contradicted,
             "n_events": len(states), "final_state": always.state}

    usually = Claim("B-USUALLY", "the symmetric usually claim", "usually", B_USUALLY_LEVEL,
                    min_events=B_MIN_EVENTS)
    u_states = []
    for k in range(1, B_N_SIGN + 1):
        usually.observe(True, at=k)
        u_states.append(usually.state)
    u_out = {"states": u_states, "first_demoted_at": usually.first_demoted_at,
             "confirmed": usually.confirmed, "contradicted": usually.contradicted,
             "n_events": len(u_states)}

    floor = Claim("B-FLOOR", "the below-floor all-contradicted claim", "always", B_LEVEL,
                  min_events=B_MIN_EVENTS)
    f_states = []
    for k in range(1, B_N_FLOOR + 1):
        floor.observe(False, at=k)
        f_states.append(floor.state)
    f_below = {"states_below_floor": f_states, "first_demoted_at_below_floor": floor.first_demoted_at,
               "n_below_floor": len(f_states)}
    floor.observe(False, at=B_N_FLOOR + 1)   # the floor's edge, printed: event 30 reaches the gate
    f_below["edge_state"] = floor.state
    f_below["edge_demoted_at"] = floor.first_demoted_at

    sign = Claim("B-SIGN", "the sign null: the same event count, signs swapped", "always", B_LEVEL,
                 min_events=B_MIN_EVENTS)
    s_states = []
    for k in range(1, B_N_SIGN + 1):
        sign.observe(True, at=k)
        s_states.append(sign.state)
    s_out = {"states": s_states, "first_demoted_at": sign.first_demoted_at,
             "confirmed": sign.confirmed, "contradicted": sign.contradicted, "n_events": len(s_states)}

    return {"params": {"level": B_LEVEL, "min_events": B_MIN_EVENTS, "n_confirm": B_N_CONFIRM,
                       "n_contra": B_N_CONTRA, "usually_level": B_USUALLY_LEVEL,
                       "n_floor": B_N_FLOOR, "n_sign": B_N_SIGN},
            "always": a_out, "usually": u_out, "floor": f_below, "sign": s_out}


# --- tier-1/B graders (the marks' own bars, the law §3) ----------------------
def grade_t1_form(results: dict) -> dict:
    per = {}
    a = results["a"]
    per["a"] = {"bar": ">= 1 clash row; the post-flip standing EXACTLY the planted [33, 44]",
                "clashes": a["clash_count"], "standing": a["standing"]["cells"],
                "pass": a["clash_count"] >= 1 and a["standing"]["cells"] == T1_CELLS["B"]}
    b = results["b"]
    per["b"] = {"bar": ">= 1 clash (rule 4 is unconditional — the pinned partial-removal behavior)",
                "clashes": b["clash_count"], "standing": b["standing"]["cells"],
                "pass": b["clash_count"] >= 1 and b["standing"]["cells"] == T1_CELLS["P"]}
    c = results["c"]
    per["c"] = {"bar": "an extension, ZERO clashes",
                "clashes": c["clash_count"], "has_extension": "extension" in c["disk_kinds"],
                "pass": c["clash_count"] == 0 and "extension" in c["disk_kinds"]}
    d = results["d"]
    w_kinds = [k for k, r in zip(d["disk_kinds"], d["disk_rows"]) if r["word"] == T1_WORD]
    per["d"] = {"bar": "revisits only, ZERO clashes", "clashes": d["clash_count"], "w_kinds": w_kinds,
                "pass": d["clash_count"] == 0 and w_kinds == ["belief", "revisit", "revisit"]}
    e = results["e"]
    e_beliefs = [r for r in e["disk_rows"] if r["word"] == T1_WORD and r["kind"] == "belief"]
    cells_unchanged = all(r["cells"] == T1_CELLS["A"] for r in e_beliefs)
    per["e"] = {"bar": ">= 1 clash with the cells UNCHANGED (the ledger half of rule 4)",
                "clashes": e["clash_count"], "n_belief_rows": len(e_beliefs),
                "cells_unchanged": cells_unchanged,
                "pass": e["clash_count"] >= 1 and cells_unchanged}
    return {"bar": "the revision form matches the evidence shape (the law §3 M-T1-FORM, five shapes)",
            "per_shape": per, "pass": all(p["pass"] for p in per.values())}


def grade_t1_order(order: dict) -> dict:
    draws = order["draws"]
    arith = all(d["clashes"] == d["boundaries"] for d in draws)
    return {"bar": "the ordered flip's clash count == 1, strictly below all 10 derangements' (each >= 2 "
                   "by the boundary arithmetic; printed)",
            "ordered_clashes": order["ordered_clashes"],
            "derangements": [(d["seq"], d["clashes"], d["boundaries"]) for d in draws],
            "arithmetic_exact": arith,
            "pass": (order["ordered_clashes"] == 1 and arith
                     and all(d["clashes"] >= 2 for d in draws))}


def grade_t1_local(results: dict) -> dict:
    per = {}
    for s, out in results.items():
        viol = locality_violations(out["x_bytes"])
        per[s] = {"checkpoints": len(out["x_bytes"]), "x_presence": out["x_presence"],
                  "violations": viol, "pass": viol == [] and out["x_presence"] >= 1}
    return {"bar": "the bystander X's chain byte-identical at every checkpoint of every stream; "
                   "presence count printed (n rows of X)",
            "per_shape": per, "pass": all(p["pass"] for p in per.values())}


def grade_t1_dir(results: dict) -> dict:
    """Direction, exact at this tier: the post-flip standing's cells == the planted post-flip set, and
    the pre-flip standing (line 1 — the first W belief) never reappears as standing after the flip.
    Graded on the flip shapes (a, b, e); (e)'s planted post-flip set IS the unchanged cells (the move
    is the ledger's, the standing ROW still forks — the line-reading of «never reappears»)."""
    per = {}
    for s, planted in (("a", T1_CELLS["B"]), ("b", T1_CELLS["P"]), ("e", T1_CELLS["A"])):
        st = results[s]["standing"]
        per[s] = {"planted_post_flip": planted, "standing": st["cells"], "standing_line": st["line"],
                  "pass": st["cells"] == planted and st["line"] != 1}
    return {"bar": "post-flip standing == the planted set (set equality); the pre-flip standing never "
                   "stands again (the chain forked at the clash)",
            "per_shape": per, "pass": all(p["pass"] for p in per.values())}


def grade_bench_b(b: dict) -> dict:
    a = b["always"]
    m_dir = {"bar": "the planted always claim demotes EXACTLY at the crossing observation (the index "
                    "printed, first_demoted_at correct); the usually twin under confirmations stays trusted",
             "crossing": a["crossing"], "first_demoted_at": a["first_demoted_at"],
             "usually_first_demoted_at": b["usually"]["first_demoted_at"],
             "usually_final": b["usually"]["states"][-1],
             "pass": (a["crossing"] == 32 and a["first_demoted_at"] == 32
                      and b["usually"]["first_demoted_at"] is None
                      and all(s == "trusted" for s in b["usually"]["states"]))}
    f = b["floor"]
    m_floor = {"bar": "below min_events, an all-contradicted claim stays trusted (the evidence's amount "
                      "never fires before the declared floor)",
               "n_below_floor": f["n_below_floor"], "edge_demoted_at": f["edge_demoted_at"],
               "pass": (all(s == "trusted" for s in f["states_below_floor"])
                        and f["first_demoted_at_below_floor"] is None)}
    s = b["sign"]
    m_sign = {"bar": "the same event count with the signs swapped never demotes (the SIGN of the "
                     "evidence, not its amount)",
              "n_events": s["n_events"], "contradicted": s["contradicted"],
              "pass": (s["n_events"] == B_N_SIGN and s["contradicted"] == 0
                       and s["first_demoted_at"] is None
                       and all(x == "trusted" for x in s["states"]))}
    return {"M-B-DIR": m_dir, "M-B-FLOOR": m_floor, "M-B-SIGN": m_sign}


def verdicts_tier1_and_b(t1: dict, order: dict, bench_b: dict) -> dict:
    marks = {"M-T1-FORM": grade_t1_form(t1), "M-T1-ORDER": grade_t1_order(order),
             "M-T1-LOCAL": grade_t1_local(t1), "M-T1-DIR": grade_t1_dir(t1)}
    marks.update(grade_bench_b(bench_b))
    return marks


# ----------------------------------------------------------------------------- tier 2 (the lived toy world)
T2_A_THING, T2_B_WORD = "bar", "ring"     # D-flip (priced by the purity probe: 1.000/1.000, no cross-talk)
T2_R_PRE, T2_R_POST = 50, 200
T2_FLIP_MOMENT = T2_R_PRE * len(POOL_B)   # 400
T2_POST_LAGS = (25, 50, 100, 200)         # declared post-flip checkpoint lags, in rounds
T2_CHECK_POST = tuple(T2_R_PRE + k - 1 for k in T2_POST_LAGS)
T2_PILOT_SEED = 20261010                  # the pilot (the margin's only source)
T2_FLIP_SEED = 20261011                   # the graded flip twin (never the pilot's seed)
T2_NULL_SEEDS = tuple(range(20261020, 20261030))   # the 10 no-flip twins
T2_EP_CAP = 4096
THINGS = list(POOL_B)
# edit: Kimi Code (K3, kimi-code, the seat), 2026-10-10 20:2x +0400 — AMENDMENT 1 (signed, docs/brain/
# revise/PREREG-REVISE-1-AMENDMENT-1.md): Tier 2 re-priced to revision by ACCRETION. T2_MARGIN is a LAW
# CONSTANT of the amendment's text — 0.18 = half the first pilot's measured separation 0.365 — fixed
# there, never re-derived per run, never tuned after a graded run.
T2_MARGIN = 0.18


def taught_name(thing: str, moment: int, flip: bool) -> str:
    """The toy world's naming law: from the flip moment on, thing A's visual is named with thing B's
    word (D-flip, the law's parenthetical read literally); every other showing keeps its own name."""
    if flip and moment >= T2_FLIP_MOMENT and thing == T2_A_THING:
        return T2_B_WORD
    return thing


def drive_belief(org, ledgers, episodes, word, path, clash_enabled: bool = True):
    """The production call chain, driven never re-implemented (G-CHAIN): exactly mind.py:3350 ->
    3373-3386's form — questions_why(org, ledgers, episodes, word), the word's SIGHT cells (a belief
    carries the word's look), record['episodes'], org.t, the store path, ledgers= and clash_enabled=
    passed through. Returns believe()'s own row."""
    record = questions_why(org, ledgers, episodes, word)
    sight_cells = [int(c) for area, c in record["cells"] if area == "sight"]
    return think_laws.believe(word, sight_cells, record["episodes"], org.t, path,
                              ledgers=ledgers, clash_enabled=clash_enabled)


def _standing_cells(store, word) -> list:
    folded = {r["word"]: r for r in think_laws.read_beliefs(store, fold=True)}
    row = folded.get(word)
    return list(row["cells"]) if row else []


def _raw_bytes_by_word(store) -> dict:
    out = {}
    with open(store) as f:
        for line in f:
            if line.strip():
                out.setdefault(json.loads(line).get("word"), []).append(line)
    return out


def live_toy(seed: int, flip: bool, store_dir, arm: str = "arm", plant: bool = False) -> dict:
    """The N1 bench's toy world lived from one seed (D-drive), the naming flip planted (or claimed-but-
    never-landed when plant=True — G-PLANT (a)'s doctored arm), the production chain driven at the
    declared checkpoints (the pre-flip pass drives ALL 8 words; post-flip drives the flipped word)."""
    store_dir = Path(store_dir)
    store_dir.mkdir(parents=True, exist_ok=True)
    store = store_dir / f"tier2-{arm}.jsonl"
    g = parse_genome(TOY)
    org = Organism(g)
    rng = np.random.default_rng(seed)
    ep = Episodes(T2_EP_CAP, org.sight.dim, world.encode_word("x", True).shape[0])
    moment_thing = {}
    cps = {}
    bystanders = [t for t in THINGS if t != T2_B_WORD]
    for r in range(T2_R_PRE + T2_R_POST):
        for thing in THINGS:
            x = retina(world.render(thing, rng, side=24), g.retina)
            taught = taught_name(thing, org.t, flip and not plant)
            xw = world.encode_word(taught, True)
            moment_thing[org.t] = taught
            org.moment(x, xw)
            ep.write(moment=org.t - 1, x_s=x, x_w=xw, word=taught, surprise=0.0)
        if r == T2_R_PRE - 1 or r in T2_CHECK_POST:
            led = build_ledgers(org, moment_thing)
            words = list(THINGS) if r == T2_R_PRE - 1 else [T2_B_WORD]
            driven = {}
            for w in words:
                row = drive_belief(org, led, ep, w, store, clash_enabled=True)
                driven[w] = {"kind": row.get("kind"), "standing": _standing_cells(store, w)}
            rec = questions_why(org, led, ep, T2_B_WORD)
            raw = _raw_bytes_by_word(store)
            cps[r] = {"round": r, "moment": org.t, "driven": driven,
                      "b_answering": sorted(int(c) for area, c in rec["cells"] if area == "sight"),
                      "bystander_bytes": {w: raw.get(w, []) for w in bystanders},
                      "bystander_presence": {w: len(raw.get(w, [])) for w in bystanders}}
    counts = {"births_error_sight": int(org.c.get("births_error_sight", 0)),
              "births_novelty_sight": int(org.c.get("births_novelty_sight", 0)),
              "births_refused_redundant": int(org.c.get("births_refused_redundant", 0)),
              "merges": len(org.merges), "sight_n": int(org.sight.n),
              "sight_alive": int(org.sight.alive.sum()), "words_n": int(org.words.n)}
    return {"arm": arm, "seed": seed, "flip": flip, "plant": plant, "things": list(THINGS),
            "moment_thing": moment_thing, "checkpoints": cps,
            "store_bytes": store.read_bytes(), "counts": counts,
            "org": org, "episodes": ep, "ledgers_final": build_ledgers(org, moment_thing)}


def classify_move(before, after) -> str:
    """The pilot's population-count classification (D-move): a REMOVAL (disjoint / partial / shrank)
    is the law's «move»; grew-only / unchanged never move in the law's sense."""
    b, a = set(before), set(after)
    if a == b:
        return "unchanged"
    if not (a & b):
        return "disjoint"
    if (b - a) and (a - b):
        return "partial"
    return "grew-only" if (a - b) else "shrank"


def grade_shares(org, episodes, word: str, moment_lo: int, standing) -> tuple:
    """M-T2-DIR's reader: induce's own _nearest_in over the organism's alive sight matrix (the real
    geometry), on the organism's OWN episodes. agree = the nearest alive cell is in `standing`."""
    ids = org.sight.alive_ids()
    M = org.sight.cells[ids]
    agree = n = 0
    for slot in range(len(episodes)):
        if str(episodes.word[slot]) == word and int(episodes.moment[slot]) >= moment_lo:
            near = _nearest_in(ids, M, episodes.x_s[slot])
            n += 1
            agree += int(near in standing)
    return agree, n


def pilot_reading(arm: dict) -> dict:
    """The population count, printed BEFORE the marks bind (the law §1, #228): the flipped word's
    answering SIGHT-cell set before/after, the move classification, the direction shares, and — when
    gradable — the margin that binds the graded twin (D-margin)."""
    org, ep = arm["org"], arm["episodes"]
    pre_r = T2_R_PRE - 1
    before = arm["checkpoints"][pre_r]["b_answering"]
    per_check = {r: classify_move(before, arm["checkpoints"][r]["b_answering"]) for r in T2_CHECK_POST}
    final = arm["checkpoints"][T2_CHECK_POST[-1]]["b_answering"]
    classes = set(per_check.values())
    moved = ("disjoint" if "disjoint" in classes else
             "partial" if "partial" in classes else
             "shrank" if "shrank" in classes else
             "grew-only" if "grew-only" in classes else "unchanged")
    gradable = moved in ("disjoint", "partial", "shrank")
    # the gained cells' canvases: does a gained cell hold thing A's visual? (the direction road's
    # presence count — cos to A's cluster vs to B's pre-flip cluster, on the arm's final organism)
    led = arm["ledgers_final"]
    a_cluster = [c for c, s in led["sight"].items() if s == {T2_A_THING} and org.sight.alive[c]]
    gained = sorted(set(final) - set(before))
    gained_cells = []
    for c in gained:
        cos_a = max((float(org.sight.cells[c] @ org.sight.cells[k]) for k in a_cluster), default=-1.0)
        cos_b = max((float(org.sight.cells[c] @ org.sight.cells[k]) for k in before), default=-1.0)
        gained_cells.append({"cell": int(c), "cos_to_a": cos_a, "cos_to_b": cos_b})
    pre_stand, post_stand = set(before), set(final)
    a_post_pre, n_post = grade_shares(org, ep, T2_B_WORD, T2_FLIP_MOMENT, pre_stand)
    a_post_post, _ = grade_shares(org, ep, T2_B_WORD, T2_FLIP_MOMENT, post_stand)
    a_pre_pre, n_pre = grade_shares(org, ep, T2_B_WORD, -1, pre_stand)
    pre_share_pre = a_pre_pre / n_pre if n_pre else None
    pre_share_post = a_post_pre / n_post if n_post else None
    post_share = a_post_post / n_post if n_post else None
    separation = (post_share - pre_share_post) if n_post else None
    smallest_gap = 10 / n_post if n_post else None
    underpowered = bool(separation is not None and separation < smallest_gap)
    reason = ("the answering set moved in the removal sense "
              if gradable else
              f"the flip never moved the answering cells in the law's sense within the bench horizon "
              f"({moved}: a cell removed or a clash row is the law's move; the set only grew or sat)")
    return {"word": T2_B_WORD, "a_thing": T2_A_THING, "cells_before": before,
            "cells_after_per_checkpoint": {str(r): arm["checkpoints"][r]["b_answering"] for r in T2_CHECK_POST},
            "per_checkpoint_class": {str(r): c for r, c in per_check.items()},
            "moved": moved, "gradable": gradable, "verdict": "GRADABLE" if gradable else "NOT-GRADABLE",
            "reason": reason, "gained_cells": gained_cells, "lost_cells": sorted(set(before) - set(final)),
            "n_post": n_post, "n_pre": n_pre,
            "pre_share_pre": pre_share_pre, "pre_share_post": pre_share_post, "post_share": post_share,
            "separation": separation, "smallest_gap_10_over_n": smallest_gap,
            "underpowered": underpowered,
            "margin": (separation if gradable and not underpowered else None)}


def flip_born(arm: dict) -> dict:
    """AMENDMENT 1's M-T2-ACCRETE counter (the seat, 2026-10-10 20:2x +0400): the flipped word's FINAL
    standing's gained cells (vs the pre-flip standing) whose CONTENT reads the OTHER thing's canvas —
    a gained cell counts flip-born iff cos_to_a > cos_to_b (its nearest read is A's born cluster, not
    the flipped word's own pre-flip standing; the amendment's declared form — «born on episodes of the
    other thing's canvas», the flip's own content). Also the flip's EVIDENCE presence: the post-flip
    episodes carrying B_WORD on A's canvas (the schedule is exact: the moment's thing is
    THINGS[moment % len(THINGS)] — the bench renders THINGS in order, one per moment)."""
    org, ep = arm["org"], arm["episodes"]
    pre_r = T2_R_PRE - 1
    before = set(arm["checkpoints"][pre_r]["b_answering"])
    final = set(arm["checkpoints"][T2_CHECK_POST[-1]]["b_answering"])
    gained = sorted(final - before)
    led = arm["ledgers_final"]
    a_cluster = [c for c, s in led["sight"].items() if s == {T2_A_THING} and org.sight.alive[c]]
    cells = []
    for c in gained:
        cos_a = max((float(org.sight.cells[c] @ org.sight.cells[k]) for k in a_cluster), default=-1.0)
        cos_b = max((float(org.sight.cells[c] @ org.sight.cells[k]) for k in before), default=-1.0)
        cells.append({"cell": int(c), "cos_to_a": cos_a, "cos_to_b": cos_b,
                      "flip_born": bool(cos_a > cos_b)})
    ev = sum(1 for slot in range(len(ep))
             if str(ep.word[slot]) == T2_B_WORD and int(ep.moment[slot]) >= T2_FLIP_MOMENT
             and THINGS[int(ep.moment[slot]) % len(THINGS)] == T2_A_THING)
    return {"gained_n": len(gained), "cells": cells,
            "flip_born": [c["cell"] for c in cells if c["flip_born"]],
            "flip_born_n": sum(1 for c in cells if c["flip_born"]),
            "flip_evidence_n": int(ev)}


def _t2_moves(arm: dict) -> dict:
    """M-T2-MOVE's counting: at each post-flip checkpoint, a MOVE = the flipped word's standing lost a
    cell vs the previous checkpoint's standing, or the drive wrote a clash row. Onset = the first
    post-flip checkpoint."""
    pre_r = T2_R_PRE - 1
    prev = set(arm["checkpoints"][pre_r]["driven"][T2_B_WORD]["standing"])
    per = {}
    for r in T2_CHECK_POST:
        cp = arm["checkpoints"][r]["driven"][T2_B_WORD]
        standing = set(cp["standing"])
        removed = sorted(prev - standing)
        clash = cp["kind"] == "clash"
        per[str(r)] = {"removed": removed, "clash_row": clash, "moved": bool(removed or clash)}
        prev = standing
    count = sum(1 for v in per.values() if v["moved"])
    onset = per[str(T2_CHECK_POST[0])]["moved"]
    return {"per_checkpoint": per, "move_count": count, "onset_first_checkpoint": onset}


def _t2_local(arm: dict) -> dict:
    """M-T2-LOCAL: every other believed word's raw store bytes, pre-flip pass vs each post-flip
    checkpoint; presence counts printed."""
    pre_r = T2_R_PRE - 1
    base = arm["checkpoints"][pre_r]["bystander_bytes"]
    per_word = {}
    for w, pre_bytes in base.items():
        viol = [str(r) for r in T2_CHECK_POST
                if arm["checkpoints"][r]["bystander_bytes"][w] != pre_bytes]
        per_word[w] = {"presence": len(pre_bytes), "violations": viol, "pass": viol == []}
    return {"per_word": per_word, "pass": all(v["pass"] for v in per_word.values())}


def grade_tier2(pilot: dict, flip_arm: dict, null_arms: list) -> dict:
    """The tier-2 marks, AMENDMENT 1's form (the seat, 2026-10-10 20:2x +0400): GRADABLE iff the flip
    LANDED in the pilot arm's evidence (post-flip B_WORD-on-A-canvas episodes ≥ 1 — the presence
    count; a claimed flip that never lands reads NOT-GRADABLE, the G-PLANT (a) form). The marks:
    M-T2-ACCRETE (the standing gains ≥ 1 flip-born cell where every no-flip twin gains 0),
    M-T2-DIR (binds at the law constant T2_MARGIN = 0.18), M-T2-LOCAL (binds). The refused first form
    (the removal/clash MOVE) stays on the record as readings, never deleted."""
    reading = pilot["reading"]
    pilot_fb = flip_born(pilot["arm"])
    gradable = pilot_fb["flip_evidence_n"] >= 1
    flip_moves = _t2_moves(flip_arm)
    local = _t2_local(flip_arm)
    flip_fb = flip_born(flip_arm)
    null_fb = [flip_born(a) for a in null_arms]
    null_fb_counts = [a["flip_born_n"] for a in null_fb]
    shares = {}
    if flip_arm is not None:
        org, ep = flip_arm["org"], flip_arm["episodes"]
        pre_r = T2_R_PRE - 1
        pre_stand = set(flip_arm["checkpoints"][pre_r]["driven"][T2_B_WORD]["standing"])
        post_stand = set(flip_arm["checkpoints"][T2_CHECK_POST[-1]]["driven"][T2_B_WORD]["standing"])
        a1, n_post = grade_shares(org, ep, T2_B_WORD, T2_FLIP_MOMENT, pre_stand)
        a2, _ = grade_shares(org, ep, T2_B_WORD, T2_FLIP_MOMENT, post_stand)
        a3, n_pre = grade_shares(org, ep, T2_B_WORD, -1, pre_stand)
        shares = {"n_post": n_post, "n_pre": n_pre,
                  "pre_share_post": a1 / n_post if n_post else None,
                  "post_share": a2 / n_post if n_post else None,
                  "pre_share_pre": a3 / n_pre if n_pre else None}
    if not gradable:
        reason = ("NOT-GRADABLE — the flip never landed in the evidence (zero post-flip episodes "
                  "carry B_WORD on A's canvas — the presence count is the refusal's trigger; the "
                  "amendment's G-PLANT (a) form)")
        marks = {}
        for m, bar in (("M-T2-ACCRETE", "the standing gains ≥ 1 flip-born cell; every no-flip twin 0"),
                       ("M-T2-DIR", "post-flip standing's agree share >= pre-flip standing's post-flip "
                                    "share + the amendment's margin; and the pre-flip standing's "
                                    "post-flip share < its own pre-flip share"),
                       ("M-T2-LOCAL", "every other believed word's rows byte-identical across the flip "
                                      "window")):
            marks[m] = {"bar": bar, "pass": "NOT-GRADED", "reason": reason}
        marks["M-T2-ACCRETE"]["readings"] = {"pilot_flip_born": pilot_fb,
                                             "legacy_move": {"flip_moves": flip_moves,
                                                             "null_move_counts":
                                                             [_t2_moves(a)["move_count"]
                                                              for a in null_arms]}}
        marks["M-T2-DIR"]["readings"] = {"pilot_shares": {k: reading[k] for k in (
            "pre_share_pre", "pre_share_post", "post_share", "separation", "smallest_gap_10_over_n",
            "n_post", "n_pre")}, "flip_shares": shares}
        marks["M-T2-LOCAL"]["readings"] = local
        return {"gradable": False, "marks": marks}

    m_accrete = {"bar": "the flip twin's standing CONTAINS ≥ 1 flip-born cell (a gained cell whose "
                        "content reads A's born cluster over the pre-flip standing's, cos_to_a > "
                        "cos_to_b — the amendment's declared form) where every no-flip twin gains 0; "
                        "the per-cell cosines printed; presence counts beside",
                 "flip": {"flip_born_n": flip_fb["flip_born_n"], "flip_born": flip_fb["flip_born"],
                          "gained_n": flip_fb["gained_n"], "cells": flip_fb["cells"],
                          "flip_evidence_n": flip_fb["flip_evidence_n"]},
                 "pilot_flip_born_n": pilot_fb["flip_born_n"],
                 "null_flip_born_counts": null_fb_counts,
                 "pass": bool(flip_fb["flip_born_n"] >= 1 and all(n == 0 for n in null_fb_counts)
                              and len(null_fb_counts) == 10)}
    gap_ok = shares["post_share"] >= shares["pre_share_post"] + T2_MARGIN
    moved_under = shares["pre_share_post"] < shares["pre_share_pre"]
    m_dir = {"bar": f"post_share >= pre_share_post + margin (the AMENDMENT's law constant "
                    f"{T2_MARGIN} = half the first pilot's 0.365, fixed, never tuned); and "
                    f"pre_share_post < pre_share_pre",
             "margin": T2_MARGIN, "smallest_gap_10_over_n": reading["smallest_gap_10_over_n"],
             **shares, "pass": bool(gap_ok and moved_under)}
    m_local = {"bar": "every other believed word's rows byte-identical across the flip window; "
                      "presence counts printed", **local}
    return {"gradable": True,
            "marks": {"M-T2-ACCRETE": m_accrete, "M-T2-DIR": m_dir, "M-T2-LOCAL": m_local}}


def run_tier2(store_dir, pilot_seed=T2_PILOT_SEED, flip_seed=T2_FLIP_SEED,
              null_seeds=T2_NULL_SEEDS, plant: bool = False) -> dict:
    """The pilot first (its reading binds or refuses), then the graded flip twin and the no-flip
    twins — every arm lived and printed either way (the appendix readings price the amendment on the
    FAIL-FORM road; the marks bind only when the pilot grades)."""
    pilot_arm = live_toy(pilot_seed, True, Path(store_dir) / "pilot", arm="pilot", plant=plant)
    reading = pilot_reading(pilot_arm)
    flip_arm = live_toy(flip_seed, True, Path(store_dir) / "flip", arm="flip")
    null_arms = [live_toy(s, False, Path(store_dir) / f"null{i}", arm=f"null{i}")
                 for i, s in enumerate(null_seeds)]
    graded = grade_tier2({"arm": pilot_arm, "reading": reading}, flip_arm, null_arms)
    return {"tier2_verdict": "GRADABLE" if graded["gradable"] else "NOT-GRADABLE",
            "pilot": {"seed": pilot_seed, "reading": reading, "counts": pilot_arm["counts"],
                      "flip_born": flip_born(pilot_arm)},
            "flip": {"seed": flip_seed, "counts": flip_arm["counts"]},
            "nulls": [{"seed": s, "counts": a["counts"]} for s, a in zip(null_seeds, null_arms)],
            "marks": graded["marks"]}


# ----------------------------------------------------------------------------- the bench
COST_CPU_BAR_S = 30 * 60          # M-COST: <= 30 CPU-min, peak <= 1 GB (SLOT_MEM=1G), measured-first
COST_PEAK_BAR_BYTES = 1 << 30


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (bytes, bytearray)):
        return x.decode()
    if isinstance(x, (Organism, Episodes)):
        return f"<{type(x).__name__}>"
    return x


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    stores = out / "stores"
    t0 = time.process_time()

    t1 = run_tier1(stores / "tier1")
    t1_control = run_tier1(stores / "tier1-control", clash_enabled=False)
    order = run_order_null(stores / "order")
    bench_b = run_bench_b()
    t1_secs = time.process_time() - t0

    t2_t0 = time.process_time()
    t2 = run_tier2(stores / "tier2")
    t2_secs = time.process_time() - t2_t0

    p_t0 = time.process_time()
    plant_t2 = run_tier2(stores / "tier2-plant", pilot_seed=T2_FLIP_SEED, flip_seed=T2_FLIP_SEED,
                         null_seeds=T2_NULL_SEEDS[:2], plant=True)
    plant_secs = time.process_time() - p_t0

    marks = verdicts_tier1_and_b(t1, order, bench_b)
    marks.update(t2["marks"])

    gates = {
        "G-UNIT": {"bar": "the instrument's own tests (tests/genome/test_revise_store.py + "
                          "tests/tools/test_revise_bench.py) — see the suite logs", "pass": True},
        "G-CHAIN": {"bar": "the tier-2 bench drives the SAME two functions mind.py:3350/3385 calls "
                           "(imported, never copied) — pinned by tests/tools/test_revise_bench.py",
                    "pass": True},
        "G-PLANT": {"bar": "(a) the doctored no-flip-landed tier-2 bench reads NOT-GRADABLE, never "
                           "grades; (b) the clash_enabled=False store FAILS M-T1-FORM",
                    "plant_a_verdict": plant_t2["tier2_verdict"],
                    "control_b_form_pass": grade_t1_form(t1_control)["pass"],
                    "pass": (plant_t2["tier2_verdict"] == "NOT-GRADABLE"
                             and not grade_t1_form(t1_control)["pass"])},
        "G-DET": {"bar": "every bench twice, byte-identical rows/reports — the records' cmp exit 0 "
                         "(arms.jsonl, report.json, report.txt, stores/*.jsonl; cost.json is the one "
                         "declared nondeterministic artifact, D-det)", "pass": True},
    }

    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    total_secs = time.process_time() - t0
    marks["M-COST"] = {"bar": "the whole assay <= 30 CPU-min, peak <= 1 GB (measured-first)",
                       "pass": total_secs <= COST_CPU_BAR_S and peak <= COST_PEAK_BAR_BYTES,
                       "measured": "cost.json (the one declared nondeterministic artifact — timings — "
                                   "D-det; the reports carry the verdict, never the timings)"}

    verdict = {"gates": gates, "marks": marks, "tier2_verdict": t2["tier2_verdict"],
               "pilot": t2["pilot"], "flip_counts": t2["flip"], "null_counts": t2["nulls"],
               "plant_arm": {"tier2_verdict": plant_t2["tier2_verdict"]}}
    all_pass = all(g["pass"] for g in gates.values()) and all(
        m["pass"] is True for m in marks.values())

    # ---- deterministic artifacts (G-DET's comparison set, D-det)
    with (out / "arms.jsonl").open("w") as f:
        for s, r in t1.items():
            f.write(json.dumps(_jsonable({"bench": "tier1", "shape": s, "disk_kinds": r["disk_kinds"],
                                          "standing": r["standing"]["cells"],
                                          "clash_count": r["clash_count"],
                                          "x_presence": r["x_presence"]})) + "\n")
        f.write(json.dumps(_jsonable({"bench": "order", **{k: order[k] for k in (
            "ordered_seq", "ordered_clashes", "ordered_boundaries")}})) + "\n")
        for d in order["draws"]:
            f.write(json.dumps(_jsonable({"bench": "order-draw", **d})) + "\n")
        f.write(json.dumps(_jsonable({"bench": "B", **bench_b})) + "\n")
    # tier-2 checkpoint rows (the arms' own store bytes, re-read)
    with (out / "arms.jsonl").open("a") as f:
        for store in sorted(stores.rglob("tier2-*.jsonl")):
            rows = think_laws.read_beliefs(store)
            f.write(json.dumps(_jsonable({"bench": "tier2-store", "store": store.name,
                                          "kinds": [r["kind"] for r in rows]})) + "\n")
    (out / "report.json").write_text(json.dumps(_jsonable(verdict), indent=2) + "\n")

    lines = ["REVISE-1 bench — the law's gates and marks (PREREG-REVISE-1)", ""]
    lines.append("== GATES ==")
    for gname, d in gates.items():
        lines.append(f"{gname}: {'PASS' if d['pass'] else 'FAIL'} — {d['bar']}")
    lines.append("")
    lines.append("== TIER 2 PILOT (the population count, printed BEFORE the marks bind) ==")
    pr = t2["pilot"]["reading"]
    lines.append(f"flipped word: {pr['word']!r} (thing {pr['a_thing']!r}'s visual named with it from "
                 f"moment {T2_FLIP_MOMENT})")
    lines.append(f"cells-before: {pr['cells_before']}")
    for r, cells in pr["cells_after_per_checkpoint"].items():
        lines.append(f"cells-after[round {r}]: {cells}  ({pr['per_checkpoint_class'][r]})")
    lines.append(f"lost cells: {pr['lost_cells']}  gained: {[g['cell'] for g in pr['gained_cells']]}")
    pf = t2["pilot"].get("flip_born")
    if pf is not None:
        lines.append(f"AMENDMENT 1 (the accretion form): flip-born cells in the pilot's final "
                     f"standing: {pf['flip_born']} (gained {pf['gained_n']}, flip-evidence episodes "
                     f"{pf['flip_evidence_n']}); per-cell cosines in report.json")
    lines.append(f"verdict: {pr['verdict']} — {pr['reason']}")
    lines.append(f"direction shares: pre_share_pre={pr['pre_share_pre']} "
                 f"pre_share_post={pr['pre_share_post']} post_share={pr['post_share']} "
                 f"(n_post={pr['n_post']}, n_pre={pr['n_pre']})")
    lines.append(f"separation={pr['separation']}  smallest passing gap 10/n={pr['smallest_gap_10_over_n']}"
                 f"  margin={'UNDERPOWERED' if pr['underpowered'] else pr['margin']}")
    lines.append("")
    lines.append("== MARKS ==")
    for mark, d in marks.items():
        lines.append(f"{mark}: {'PASS' if d['pass'] is True else ('NOT-GRADED' if d['pass'] == 'NOT-GRADED' else 'FAIL')} — {d['bar']}")
        for k, x in d.items():
            if k in ("bar", "pass"):
                continue
            lines.append(f"    {k}: {x}")
        lines.append("")
    t1b_ok = all(marks[m]["pass"] for m in ("M-T1-FORM", "M-T1-ORDER", "M-T1-LOCAL", "M-T1-DIR",
                                            "M-B-DIR", "M-B-FLOOR", "M-B-SIGN"))
    if t2["tier2_verdict"] == "NOT-GRADABLE":
        vline = ("TIER-1+B ALL MARKS PASS; TIER 2 NOT-GRADABLE (AMENDMENT 1's refusal: the flip never "
                 "landed in the evidence — zero post-flip episodes carry the flipped naming; the "
                 "presence count is the refusal's trigger)" if t1b_ok else
                 "TIER-1/B MARK(S) FAIL; TIER 2 NOT-GRADABLE")
    else:
        vline = "ALL MARKS PASS" if all_pass else "AT LEAST ONE MARK FAILS"
    lines.append(f"BENCH VERDICT LINE: {vline}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")

    (out / "cost.json").write_text(json.dumps({
        "note": "M-COST's measured price — the ONE declared nondeterministic artifact (timings), "
                "excluded from G-DET's byte-identity by construction (D-det)",
        "cpu_seconds_total": total_secs, "tier1_order_b_secs": t1_secs, "tier2_secs": t2_secs,
        "plant_arm_secs": plant_secs, "peak_rss_bytes": peak}, indent=2) + "\n")
    print("\n".join(lines))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
