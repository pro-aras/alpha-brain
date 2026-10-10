# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:5x +0400 — PREREG-CONTENT-WEB (F1) §3
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010): the law's bench,
# written AFTER the law (law before code) and AFTER its G-UNIT GREEN (638a852) and G-IDENTITY (fbc548b).
"""content_web_bench.py — the CONTENT-WEB bench: the amodal feed measured on the toy world.

    python3 -B tools/brain/content_web_bench.py OUTDIR
    python3 -B tools/brain/content_web_bench.py --probe OUTDIR   # the pilot readings only (recurrence
                                                                 # + collisions + the chances ceiling)

THE TOY (the law §3 — the muse bench's own world, tools/brain/muse_bench.py's form): the 8 TOY_THINGS
x THING_ROUNDS=30 rounds on maker canvases (a fresh render per occurrence — render_canvas rng
[BENCH_SEED, k], the muse bench's exact world), the ear naming each thing at its canvas, driven ON vs
OFF (Mind(content_web=...)). The genome: A4L-LANG's own + the BRAIN line (hears toy).

Bench decisions the law left to the builder (written down, never guessed silently — the muse bench's
own D- form):
  D-isolation  DOOR ISOLATION: the muse bench's world carries «you are alpha» hearsay on the EAR; this
               bench's planted names must be heard ONLY through the chat door (the law §3's own words:
               «never the ear»), so the alpha ear-hearsay is ABSENT here — the hearsay stream of this
               toy is the thing-naming itself. Pinned at the tape level in tests/tools/.
  D-arc        the planted cross-channel arc of record: TWO pairs — «alpha» names STAR, «zeta» names
               RING — each a ONE-WORD chat row (the law §1's declared one-word naming: «the planted arc
               names things with ONE word») published right after the thing's canvas on the last
               CHAT_ARC_N=12 of its moments (the muse bench's sticky-tail window form).
  D-game       the game channel's presence: one outcome row per round (act «step», got +1.0, except
               every 5th round -1.0) — the g: tokens recur by construction (the categorical form).
  D-sleep      stock A4L-LANG SLEEP (no re-declare): the web consolidates ONLINE at evidence events —
               the muse bench's 200-moments re-declare served the muse's promotion rule, which this
               bench never drives. No sleep fires at this size (org.t stays under 2500; printed).
  D-muse       muse=False in both arms (the composition is G-UNIT(e)'s pin; the bench reads the web).
  D-hyp        a sighting's token = the FIRST hypothesis's token (the glance's own order; sightings
               whose canvas yielded != 1 hypothesis are printed, never hidden).
  D-stability  the 16 readings: for each of the 8 things, token(round 0) vs token(round 3) — straddling
               the calibration-at-20 boundary (learned scenes 0..19 vs 24..31) — and token(round 3) vs
               token(round 6) — straddling calibration-at-40. Bar 16/16, the pilot's FULL recurrence
               reading printed BEFORE the mark binds (#228).
  D-null       the 10 derangement twins: per-sense seeded NON-IDENTITY permutations of the ON arm's
               captured token stream (the muse bench's D-null form), every slot's moment kept — the
               co-occurrence destroyed, the marginal rates kept (the per-sense token multiset is
               invariant). Each twin feeds a FRESH Web with the mind's own L configuration (rule L,
               beta=WEB_BETA, seed=the bench genome's SEED, spend harmonic, reach WEB_REACH).
  D-cost       per-row process_time ON vs OFF over the consume loop (the N1/muse form, both arms timed).
"""
from __future__ import annotations

import io
import json
import shutil
import sys
import time
import unittest.mock as mock
from pathlib import Path

import numpy as np
from PIL import Image

import creature.contentweb as cw
from creature.mind import Mind, WEB_BETA, WEB_REACH
from creature.senses import chat as chat_sense
from creature.tape import Tape
from genome import web as _web, world

ROOT = Path(__file__).resolve().parents[2]
TOY_THINGS = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star"]   # the muse bench's own 8
BENCH_SEED = 20261010                # the muse bench's own
THING_ROUNDS = 30                    # 240 thing moments, the 8-cycle
CHAT_ARC_N = 12                      # the muse bench's HEARSAY_N window form
PLANTED = {"alpha": "star", "zeta": "ring"}     # the planted arc of record: name -> thing (D-arc)
GAME_EVERY = 5                       # D-game: rounds with r % GAME_EVERY == 4 pay -1.0, else +1.0
TWINS_N = 10
COST_BAR = 0.05
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3 nearest; "
              "calibrate at 20 40 60 and before a sitting; replay none; hears toy")
STABILITY_PAIRS = ((0, 3), (3, 6))   # D-stability: the round pairs straddling calibrations 20 and 40


def genome_text() -> str:
    """A4L-LANG's own body + the BRAIN line (hears the toy hand) — the muse bench's genome WITHOUT its
    SLEEP re-declare (D-sleep)."""
    return (ROOT / "genome" / "ladder" / "A4L-LANG.genome").read_text() + "\n" + BRAIN_LINE + "\n"


class _Clock:
    def __init__(self) -> None:
        self.k = 0

    def __call__(self) -> str:
        h, m, s = self.k // 3600, (self.k // 60) % 60, self.k % 60
        self.k += 1
        return f"2026-10-10T{h:02d}:{m:02d}:{s:02d}.000Z"


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(b, format="PNG")
    return b.getvalue()


def arc_after(thing: str, rounds: int = THING_ROUNDS, n: int = CHAT_ARC_N) -> set:
    """The thing-moment indices after which the planted name's chat row follows: the last n moments of
    the named thing (the muse bench's sticky-tail window form)."""
    ix = [i for i in range(rounds * len(TOY_THINGS)) if TOY_THINGS[i % len(TOY_THINGS)] == thing]
    return set(ix[-n:])


def _publish_chat(root: Path, tape: Tape, clock: _Clock, cid: str, text: str) -> None:
    """ONE chat row by the door's own road, at exactly this tape position (the planted arc's window)."""
    (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
    (root / "chat" / "in" / f"{cid}.json").write_text(json.dumps({"id": cid, "text": text}))
    chat_sense.scan_once(lambda s, p, m, e: tape.publish(s, p, m, e, at=clock()), root, canvas=128, letters=8)


def build_tape(root: Path, clock: _Clock, rounds: int = THING_ROUNDS, arc_n: int = CHAT_ARC_N) -> Tape:
    """The bench's tape, one deterministic build (the SAME tape feeds every arm): the toy life with the
    planted chat arc interleaved (D-arc) and the game channel's outcome rows (D-game)."""
    tape = Tape(root)
    after = {named_thing: arc_after(named_thing, rounds, arc_n) for named_thing in PLANTED.values()}
    k = 0
    chat_k = 0
    for i in range(rounds * len(TOY_THINGS)):
        thing = TOY_THINGS[i % len(TOY_THINGS)]
        moment = f"toy{i:06d}"
        tape.publish("ear", thing.encode(), {"moment": moment, "source": "toy", "word": thing}, "txt", at=clock())
        rgb, _t = world.render_canvas(thing, np.random.default_rng([BENCH_SEED, k]))
        k += 1
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "toy"}, "png", at=clock())
        for name, named_thing in PLANTED.items():
            if i in after[named_thing] and thing == named_thing:
                _publish_chat(root, tape, clock, f"c{chat_k:02d}{name}", name)     # ONE word — D-arc
                chat_k += 1
        if i % len(TOY_THINGS) == 0:                       # the round boundary: the game channel's row
            r = i // len(TOY_THINGS)
            got = -1.0 if (r % GAME_EVERY == GAME_EVERY - 1) else 1.0
            tape.publish("outcome", b"{}", {"moment": f"game{r:04d}", "source": "toy", "act": "step",
                                            "got": got}, "json", at=clock())
    return tape


def _rows(tape_root: Path) -> list:
    from creature.tape import read_tape
    return list(read_tape(tape_root))


def drive(tape_root: Path, content_web: bool, work: Path) -> dict:
    """One mind over the tape under the flag, the token stream captured at the ON road's own funnel
    (_cweb_hear — the census's own granularity; OFF: _web_hear, the old ear-only road). Returns the
    arm's records: the stream, the census, the web reading, the persisted web state bytes, the timing."""
    root = work
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "tape").symlink_to((tape_root / "tape").resolve(), target_is_directory=True)
    gp = root.parent / f"g-{root.name}.genome"
    gp.write_text(genome_text())
    m = Mind(gp, root, content_web=content_web)
    rows = _rows(tape_root)
    stream: list = []
    cur: dict = {"seq": None}

    if content_web:
        real = Mind._cweb_hear

        def spy(self, sense, token):
            stream.append({"row": cur["seq"], "sense": str(sense), "token": str(token)})
            return real(self, sense, token)
    else:
        real = Mind._web_hear

        def spy(self, word):                                  # the OFF road: the ear, bare
            stream.append({"row": cur["seq"], "sense": "ear", "token": str(word)})
            return real(self, word)

    t0 = time.process_time()
    with mock.patch.object(Mind, "_cweb_hear" if content_web else "_web_hear", spy):
        for row in rows:
            cur["seq"] = int(row["seq"])
            m.consume(row)
        m.close()
    cpu_s = time.process_time() - t0
    web = m.webs.get("L") if m.webs is not None else None
    web_json = (root / "state" / "web.json").read_bytes() if (root / "state" / "web.json").exists() else b""
    return {"rows": len(rows), "content_web": content_web, "cpu_s": cpu_s, "stream": stream,
            "census": dict(m._cweb_counts), "web_json_len": len(web_json),
            "web_json_s_nodes": web_json.count(b'"s:'), "web_json_g_nodes": web_json.count(b'"g:'),
            "sleeps": int(m.sleep_count), "org_t": int(m.org.t),
            "web_t": int(web.t) if web is not None else 0,
            "web_stats": dict(web.stats) if web is not None else {},
            "web_nodes": sorted(web.nodes) if web is not None else [],
            "web_edges": {f"{a}|{b}": {"c": int(e["c"]), "occ": int(e["occ"]), "state": e["state"],
                                       "t0": int(e["t0"]), "looks": int(e.get("looks", 0))}
                          for (a, b), e in web.edges.items()} if web is not None else {},
            "consolidated": [f"{a}|{b}" for a, b in web.consolidated()] if web is not None else [],
            "brain_hash": m.brain.state_hash() if m.brain is not None else None}


def thing_of(moment: str) -> str:
    return TOY_THINGS[int(moment[3:]) % len(TOY_THINGS)]


def pilot(on: dict, rows: list) -> dict:
    """THE PILOT — printed BEFORE any mark binds (#228): the s: token's recurrence on the toy world
    (per-thing distinct tokens / modal share over its sightings; the 16 cross-boundary comparisons of
    D-stability), the 8-thing all-pairs collision count (the law §6's knife-edge, both sides), and the
    planted pairs' chances ceiling (the co-occurrence counts, printed before the verdict)."""
    row_moment = {int(r["seq"]): str((r.get("meta") or {}).get("moment")) for r in rows if r["sense"] == "eye"
                  and str((r.get("meta") or {}).get("moment", "")).startswith("toy")}
    per_thing: dict = {t: [] for t in TOY_THINGS}
    multi = 0
    by_row: dict = {}
    for e in on["stream"]:
        if e["sense"] != "eye" or e["row"] not in row_moment:
            continue
        by_row.setdefault(e["row"], []).append(e["token"])
    for seq, toks in sorted(by_row.items()):
        if len(toks) != 1:
            multi += 1
        per_thing[thing_of(row_moment[seq])].append(toks[0])      # D-hyp: the FIRST hypothesis's token
    recurrence = {}
    for t in TOY_THINGS:
        toks = per_thing[t]
        counts: dict = {}
        for x in toks:
            counts[x] = counts.get(x, 0) + 1
        modal, modal_n = (max(counts.items(), key=lambda kv: (kv[1], kv[0])) if counts else (None, 0))
        recurrence[t] = {"sightings": len(toks), "distinct": len(counts), "modal": modal, "modal_n": modal_n}
    # D-stability: the 16 cross-boundary comparisons (round pairs of STABILITY_PAIRS)
    stability = []
    for t in TOY_THINGS:
        for ra, rb in STABILITY_PAIRS:
            stability.append({"thing": t, "rounds": [ra, rb],
                              "same": per_thing[t][ra] == per_thing[t][rb] if len(per_thing[t]) > rb else None})
    # the all-pairs collision count over every sighting of every thing (§6's other side)
    owner: dict = {}
    collisions = 0
    for t in TOY_THINGS:
        for x in per_thing[t]:
            if x in owner and owner[x] != t:
                collisions += 1
            owner.setdefault(x, t)
    # the planted pairs' chances ceiling: each pair's realized co-occurrence (the web's own edge rows)
    edges = on["web_edges"]
    ceiling = {}
    for name, thing in PLANTED.items():
        tok_set = set(per_thing[thing])
        pairs = []
        for key, e in edges.items():
            a, b = key.split("|")
            s_tok, w = (a, b) if a.startswith("s:") else (b, a)
            if w == "w:" + name and s_tok.startswith("s:"):
                pairs.append({"s": s_tok, "in_kind": s_tok in tok_set, "c": e["c"], "occ": e["occ"],
                              "state": e["state"]})
        pairs.sort(key=lambda p: -p["c"])
        ceiling[name] = {"chat_namings": CHAT_ARC_N, "thing_sightings": len(per_thing[thing]),
                         "distinct_s_tokens": len(tok_set),
                         "max_possible_pair_events": min(CHAT_ARC_N, len(per_thing[thing])),
                         "pair_edges": pairs[:4], "n_pair_edges": len(pairs),
                         "max_realized_c": (pairs[0]["c"] if pairs else 0)}
    return {"recurrence": recurrence, "multi_hyp_sightings": multi, "stability": stability,
            "stability_ok": sum(1 for s in stability if s["same"] is True),
            "collisions": collisions, "distinct_tokens": len(owner), "ceiling": ceiling}


def cross_edges(rec: dict) -> list:
    """The consolidated s:<->w: edges (either key order) of an arm's web."""
    out = []
    for key in rec["consolidated"]:
        a, b = key.split("|")
        if (a.startswith("s:") and b.startswith("w:")) or (a.startswith("w:") and b.startswith("s:")):
            out.append(key)
    return sorted(out)


def deranged(stream: list, seed: int, k: int) -> list:
    """M-NULL's twin k: the ON token stream with EACH sense's token subsequence deranged within itself
    (a seeded non-identity permutation; the slots — every token's row and sense — kept). The
    co-occurrence is destroyed, the per-sense marginal rates kept (the multiset is invariant)."""
    rng = np.random.default_rng([seed, 7000 + k])
    out = list(stream)
    for sense in sorted({e["sense"] for e in stream}):
        ix = [i for i, e in enumerate(stream) if e["sense"] == sense]
        if len(ix) < 2:
            continue
        n = len(ix)
        for _try in range(100):
            perm = [int(x) for x in rng.permutation(n)]
            if any(perm[j] != j for j in range(n)):
                break
        toks = [stream[ix[j]]["token"] for j in perm]
        for j, i in enumerate(ix):
            out[i] = dict(out[i], token=toks[j])
    return out


def feed_web(tokens: list, seed: int) -> "_web.Web":
    """A FRESH web with the mind's own L configuration (mind.py's construction), fed the token stream."""
    w = _web.Web("L", beta=WEB_BETA, seed=int(seed), spend="harmonic", reach=WEB_REACH, author="cweb-null")
    for t in tokens:
        w.hear(t)
    return w


def bench_seed() -> int:
    from genome.machinery import parse_genome
    return int(parse_genome(genome_text()).seed)


def verdicts(on: dict, off: dict, rows: list, twins: list, pilot_reading: dict) -> dict:
    """Every mark of the law §3, computed from the arms' records, presence counts beside every number."""
    out: dict = {}
    cons_on = set(on["consolidated"])
    cross_on = cross_edges(on)
    # M-CROSS
    per_kind = {}
    for name in PLANTED:
        kind_edges = [k for k in cross_on if k.endswith("|w:" + name) or k.startswith("w:" + name + "|")]
        ceil = pilot_reading["ceiling"][name]
        per_kind[name] = {"consolidated_cross": len(kind_edges), "edges": kind_edges,
                          "distinct_s_tokens_of_the_thing": ceil["distinct_s_tokens"],
                          "thing_sightings": ceil["thing_sightings"], "chat_namings": ceil["chat_namings"]}
    off_s = sum(1 for n in off["web_nodes"] if n.startswith("s:"))
    off_g = sum(1 for n in off["web_nodes"] if n.startswith("g:"))
    out["M-CROSS"] = {"bar": "ON reads >= 1 consolidated s:<->w: edge per planted kind (printed with "
                             "presence counts); OFF reads EXACTLY 0 s: and g: nodes (byte-difference proven)",
                      "per_kind": per_kind,
                      "off_s_nodes": off_s, "off_g_nodes": off_g,
                      "off_webjson_s_keys": off["web_json_s_nodes"], "off_webjson_g_keys": off["web_json_g_nodes"],
                      "on_webjson_s_keys": on["web_json_s_nodes"], "on_webjson_g_keys": on["web_json_g_nodes"],
                      "pass": all(p["consolidated_cross"] >= 1 for p in per_kind.values())
                      and off_s == 0 and off_g == 0 and off["web_json_s_nodes"] == 0 and off["web_json_g_nodes"] == 0}
    # M-GROUND (the law's core): the heard-only name's node and the seen-only content's node
    # CONSOLIDATED neighbours, the consolidation row's own evidence printed (c, occ, the Poisson tail).
    ground = {}
    for name in PLANTED:
        best = None
        for key, e in on["web_edges"].items():
            a, b = key.split("|")
            s_tok, w = (a, b) if a.startswith("s:") else (b, a)
            if w != "w:" + name or not s_tok.startswith("s:"):
                continue
            if best is None or e["c"] > best["c"]:
                best = {"s": s_tok, "c": e["c"], "occ": e["occ"], "state": e["state"], "t0": e["t0"]}
        ground[name] = best
    # the consolidation row's own evidence for the best pair per name, recomputed by the web's OWN
    # formula (E = 2 · d · fa · fb · max(1, t − t0 + 1), web.py:175; the mind's webs run the default
    # d = 3, web.py:71 — never overridden); the node counts come from the token stream (presence,
    # never inferred)
    n_of: dict = {}
    for e in on["stream"]:
        n_of[e["token"]] = n_of.get(e["token"], 0) + 1
    web_t = on["web_t"]
    for name, best in ground.items():
        if best is None:
            continue
        fa = n_of.get(best["s"], 0) / web_t
        fb = n_of.get("w:" + name, 0) / web_t
        E = 2 * 3 * fa * fb * max(1, web_t - best["t0"] + 1)
        best["E"] = E
        best["poisson_tail"] = _web.poisson_sf(int(best["c"]), E)
        best["consolidated"] = best["state"] == "consolidated"
    out["M-GROUND"] = {"bar": "after the planted arc, the heard-only name's node and the seen-only "
                              "content's node are CONSOLIDATED neighbours (the organism grounded a word it "
                              "never heard from a teacher's naming channel onto content it only saw); the "
                              "consolidation row's own evidence printed (c, occ, the Poisson tail)",
                       "pairs": ground,
                       "chances_ceiling": {n: pilot_reading["ceiling"][n] for n in PLANTED},
                       "pass": all(g is not None and g.get("consolidated") for g in ground.values())}
    # M-CHAT (the morning's finding as a regression pin)
    chat_nodes = {n: ("w:" + n in on["web_nodes"]) for n in PLANTED}
    alpha_edges = {k: v for k, v in on["web_edges"].items() if "w:alpha" in k.split("|")}
    off_has = {n: any(x == n or x == "w:" + n for x in off["web_nodes"]) for n in PLANTED}
    out["M-CHAT"] = {"bar": "ON: after the planted chat arc, «alpha» IS a node in the web with its edge "
                            "evidence printed; OFF: absent (the 00:32 finding reproduced as the control)",
                     "on_nodes_present": chat_nodes, "alpha_edge_evidence": alpha_edges,
                     "off_nodes_present": off_has,
                     "pass": all(chat_nodes.values()) and not any(off_has.values())}
    # M-STABILITY — the pilot's reading printed FIRST (the pilot block above; the mark binds here)
    out["M-STABILITY"] = {"bar": "the same thing re-seen across the bench's own calibration boundary maps "
                                 "to the same s: token >= the declared share (bar 16/16; the quantization is "
                                 "deterministic and the calibration does not touch the eye's features — "
                                 "MEASURED, never assumed; a drift reads FAIL-FORM, the instrument's fault)",
                          "ok": pilot_reading["stability_ok"], "of": len(pilot_reading["stability"]),
                          "comparisons": pilot_reading["stability"],
                          "pass": pilot_reading["stability_ok"] == len(pilot_reading["stability"])}
    # M-NULL
    twin_cross = [t["consolidated_cross_n"] for t in twins]
    twin_planted = [t["planted_consolidated"] for t in twins]
    out["M-NULL"] = {"bar": "10 derangement twins (each sense's token stream deranged within itself, "
                            "moments kept): the planted s:<->w: edge consolidates in NONE of them; the real "
                            "run's consolidated cross-edge count exceeds the null MAX",
                     "twin_cross_counts": twin_cross, "twin_planted_consolidated": twin_planted,
                     "real_cross_n": len(cross_on), "null_max": (max(twin_cross) if twin_cross else None),
                     "pass": len(twins) == TWINS_N and not any(twin_planted)
                     and len(cross_on) > (max(twin_cross) if twin_cross else -1)}
    # M-COST
    t_on, t_off = on["cpu_s"], off["cpu_s"]
    overhead = (t_on - t_off) / t_off if t_off > 0 else float("nan")
    out["M-COST"] = {"bar": f"per-row process_time overhead ON vs OFF <= {COST_BAR:.0%} (both directions "
                            f"timed — the web hears more tokens per row, priced)",
                     "cpu_on_s": t_on, "cpu_off_s": t_off, "overhead": overhead,
                     "rows": on["rows"],
                     "pass": overhead <= COST_BAR}
    return out


def run(out: Path, rounds: int = THING_ROUNDS, twins_n: int = TWINS_N) -> dict:
    """The bench itself: one tape, two arms (ON/OFF), the 10 null twins, the pilot first, the marks."""
    out.mkdir(parents=True, exist_ok=True)
    tape_root = out / "tape-root"
    if tape_root.exists():
        shutil.rmtree(tape_root)
    tape_root.mkdir()
    clock = _Clock()
    build_tape(tape_root, clock, rounds=rounds)
    rows = _rows(tape_root)
    on = drive(tape_root, True, out / "run-on")
    off = drive(tape_root, False, out / "run-off")
    p = pilot(on, rows)
    seed = bench_seed()
    twins = []
    for k in range(twins_n):
        twin_stream = deranged(on["stream"], BENCH_SEED, k)
        w = feed_web([e["token"] for e in twin_stream], seed)
        cons = [f"{a}|{b}" for a, b in w.consolidated()]
        cross = [key for key in cons if ("s:" in key.split("|")[0] and "w:" in key.split("|")[1])
                 or ("w:" in key.split("|")[0] and "s:" in key.split("|")[1])]
        planted_hit = False
        for name in PLANTED:
            if any(k2.endswith("|w:" + name) or k2.startswith("w:" + name + "|") for k2 in cross):
                planted_hit = True
        twins.append({"k": k, "consolidated_cross_n": len(cross), "planted_consolidated": planted_hit,
                      "web_t": w.t, "stats": dict(w.stats)})
    v = verdicts(on, off, rows, twins, p)
    # durable evidence: the streams, the web readings, the report
    (out / "stream-on.json").write_text(json.dumps(on["stream"]))
    (out / "stream-off.json").write_text(json.dumps(off["stream"]))
    (out / "pilot.json").write_text(json.dumps(p, indent=2, default=str))
    (out / "twins.json").write_text(json.dumps(twins, indent=2, default=str))
    (out / "report.json").write_text(json.dumps(v, indent=2, default=str))
    lines = ["CONTENT-WEB bench — the law's marks (PREREG-CONTENT-WEB §3)", ""]
    lines.append(f"toy: {len(TOY_THINGS)} things x {rounds} rounds · the planted arc "
                 f"{ {n: t for n, t in PLANTED.items()} } x {CHAT_ARC_N} one-word chat rows each · "
                 f"rows {on['rows']} · sleeps {on['sleeps']} · org.t {on['org_t']}")
    lines.append(f"web (ON, rule L): t {on['web_t']} · stats {json.dumps(on['web_stats'], sort_keys=True)}")
    lines.append(f"web (OFF): t {off['web_t']} · stats {json.dumps(off['web_stats'], sort_keys=True)}")
    lines.append("")
    lines.append("THE PILOT (printed before any mark binds — #228):")
    lines.append(f"  recurrence: {json.dumps({t: {'sightings': r['sightings'], 'distinct': r['distinct'], 'modal_n': r['modal_n']} for t, r in p['recurrence'].items()})}")
    lines.append(f"  multi-hypothesis sightings: {p['multi_hyp_sightings']} · distinct s: tokens {p['distinct_tokens']} "
                 f"· all-pairs collisions {p['collisions']}")
    lines.append(f"  cross-boundary stability: {p['stability_ok']}/{len(p['stability'])}")
    for name in PLANTED:
        c = p["ceiling"][name]
        lines.append(f"  planted pair «{name}»↔{PLANTED[name]}: namings {c['chat_namings']} · sightings "
                     f"{c['thing_sightings']} · distinct s: tokens {c['distinct_s_tokens']} · "
                     f"max possible pair events {c['max_possible_pair_events']} · realized max c "
                     f"{c['max_realized_c']} over {c['n_pair_edges']} pair edges {c['pair_edges']}")
    lines.append("")
    all_pass = True
    for mark, d in v.items():
        lines.append(f"{mark}: {'PASS' if d['pass'] else 'FAIL'} — bar {d['bar']}")
        for k2, x in d.items():
            if k2 in ("bar", "pass"):
                continue
            lines.append(f"    {k2}: {x}")
        all_pass = all_pass and bool(d["pass"])
        lines.append("")
    lines.append(f"BENCH VERDICT LINE: {'ALL MARKS PASS' if all_pass else 'AT LEAST ONE MARK FAILS'}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return {"verdicts": v, "all_pass": all_pass, "pilot": p, "on": {k: on[k] for k in ("cpu_s", "census", "web_t", "web_stats")},
            "off": {k: off[k] for k in ("cpu_s", "web_t", "web_stats")}}


def probe(out: Path) -> int:
    """The pilot readings only (measured-first, RULES §6d): the recurrence, the collisions, the chances
    ceiling — before any arm's marks are read."""
    work = out / "probe"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    clock = _Clock()
    build_tape(work, clock)
    rows = _rows(work)
    on = drive(work, True, work / "probe-on")
    p = pilot(on, rows)
    print(json.dumps({"pilot": p, "web_stats": on["web_stats"], "web_t": on["web_t"],
                      "census": on["census"]}, indent=2, default=str))
    return 0


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--probe":
        return probe(Path(sys.argv[2]))
    res = run(Path(sys.argv[1]))
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
