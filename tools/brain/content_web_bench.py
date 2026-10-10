# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:5x +0400 — PREREG-CONTENT-WEB (F1) §3
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010): the law's bench,
# written AFTER the law (law before code) and AFTER its G-UNIT GREEN (638a852) and G-IDENTITY (fbc548b).
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:2x +0400 — AMENDMENT 1 (signed, same
# folder, 2026-10-10 15:3x): the s: token re-priced to the organism's own recognition (s:c<id>, the
# nearest alive sight cell by raw cosine — creature/contentweb.py's cell_of/sight_token). The pilot
# gains the per-component render-jitter σ (the diagnostic that killed the old form) and the null
# pieces; M-STABILITY is re-priced per the amendment (the planted things' recurrence share vs the
# 10-draw uniform-assignment null's MAX); every other mark reads the token stream unchanged. The
# failed form's run of record stands in docs/brain/content-web/records/bench-run2-* — never deleted.
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
               whose canvas yielded != 1 hypothesis are printed, never hidden; sightings whose canvas
               saw an EMPTY alive sight store yield NO token — AMENDMENT 1's declared floor — and are
               counted as silent, keyed by round so they never shift the later sightings).
  D-stability  AMENDMENT 1's re-priced form: the PLANTED things' recurrence share (the modal cell's
               share of each planted thing's sightings, averaged; the sightings span the bench's
               calibration boundaries by construction) must EXCEED the 10-draw random-assignment
               null's MAX — per draw, each sighting of a planted thing is assigned a uniform cell from
               the read's own vocabulary (the distinct s:c<id> tokens in the ON stream, printed), and
               the null share is computed exactly as the real one; the smallest passing gap (real
               share - null MAX) is printed. The OLD instrument's 16-comparison cross-boundary form
               (D-stability of the failed run) is printed in the pilot as stability_legacy for
               continuity — it is no longer the bar.
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
from typing import Optional

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


def pilot(on: dict, rows: list, tape_root: Path) -> dict:
    """THE PILOT — printed BEFORE any mark binds (#228). AMENDMENT 1's readings: the s:c<id>
    recognition key's recurrence on the toy world (per thing, the modal cell's share of its
    sightings — keyed BY ROUND so the declared floor's silent rows are honest gaps, never shifts),
    the all-pairs collision count (two things' sightings sharing one cell), the per-component
    render-jitter σ of the hypothesis feature row (the diagnostic that killed the old form — the
    amendment names it the diagnostic of record), and the planted pairs' chances ceiling (printed
    before the verdict). M-STABILITY's re-priced pieces (the planted things' share, the 10-draw
    uniform-assignment null) are computed HERE so the mark only reads them."""
    row_moment = {int(r["seq"]): str((r.get("meta") or {}).get("moment")) for r in rows if r["sense"] == "eye"
                  and str((r.get("meta") or {}).get("moment", "")).startswith("toy")}
    by_row: dict = {}
    for e in on["stream"]:
        if e["sense"] != "eye" or e["row"] not in row_moment:
            continue
        by_row.setdefault(e["row"], []).append(e["token"])
    per_thing: dict = {t: {} for t in TOY_THINGS}          # thing -> {round: FIRST-hyp token} (D-hyp)
    multi = 0
    silent = 0
    for seq, moment in sorted(row_moment.items(), key=lambda kv: kv[0]):
        i = int(moment[3:])
        thing, rnd = thing_of(moment), i // len(TOY_THINGS)
        toks = by_row.get(seq, [])
        if not toks:
            silent += 1                                    # the declared floor's silence (empty store)
            continue
        if len(toks) != 1:
            multi += 1
        per_thing[thing][rnd] = toks[0]
    recurrence = {}
    for t in TOY_THINGS:
        toks = [per_thing[t][r] for r in sorted(per_thing[t])]
        counts: dict = {}
        for x in toks:
            counts[x] = counts.get(x, 0) + 1
        modal, modal_n = (max(counts.items(), key=lambda kv: (kv[1], kv[0])) if counts else (None, 0))
        recurrence[t] = {"sightings": len(toks), "distinct": len(counts), "modal": modal, "modal_n": modal_n,
                         "modal_share": (modal_n / len(toks)) if toks else None}
    # the 16 cross-boundary comparisons of the OLD instrument's shape (printed for continuity with the
    # failed run — the mark below is the amendment's re-priced form)
    stability = []
    for t in TOY_THINGS:
        for ra, rb in STABILITY_PAIRS:
            ta, tb = per_thing[t].get(ra), per_thing[t].get(rb)
            stability.append({"thing": t, "rounds": [ra, rb],
                              "same": (ta == tb) if (ta is not None and tb is not None) else None})
    # the all-pairs collision count over every sighting of every thing (§6's other side: two DIFFERENT
    # things' sightings landing on one cell)
    owner: dict = {}
    collisions = 0
    for t in TOY_THINGS:
        for x in per_thing[t].values():
            if x in owner and owner[x] != t:
                collisions += 1
            owner.setdefault(x, t)
    # the render-jitter σ: the first-hypothesis feature row per sighting, recomputed from the tape's
    # own payloads by the law's path (a pure function of the canvas bytes — exactly what the mind's
    # glance computed), then the per-component std across each thing's sightings
    from genome import gaze
    from genome.brain import things_in_view
    from genome.machinery import parse_genome
    genome = parse_genome(genome_text())
    feats_by_thing: dict = {t: [] for t in TOY_THINGS}
    for r in rows:
        if r["sense"] != "eye":
            continue
        moment = str((r.get("meta") or {}).get("moment", ""))
        if not moment.startswith("toy"):
            continue
        payload = (tape_root / "tape" / r["payload"]).read_bytes()
        rgb = np.asarray(Image.open(io.BytesIO(payload)).convert("RGB"), dtype=np.uint8)
        g = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", r["sha"], colour=genome.colour)
        hyps, _X = things_in_view(g)
        if hyps:
            feats_by_thing[thing_of(moment)].append(np.asarray(hyps[0].feat, dtype=np.float64))
    jitter = {}
    for t in TOY_THINGS:
        F = np.stack(feats_by_thing[t]) if feats_by_thing[t] else np.zeros((0, 144))
        sigma = F.std(axis=0) if len(F) else np.zeros(0)
        jitter[t] = {"sightings": int(len(F)),
                     "sigma_mean": (float(sigma.mean()) if len(F) else None),
                     "sigma_max": (float(sigma.max()) if len(F) else None)}
    # the planted pairs' chances ceiling: each pair's realized co-occurrence (the web's own edge rows)
    edges = on["web_edges"]
    ceiling = {}
    for name, thing in PLANTED.items():
        tok_set = set(per_thing[thing].values())
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
    # M-STABILITY, re-priced (AMENDMENT 1): the planted things' recurrence share vs the 10-draw
    # random-assignment null's MAX. The null: each sighting assigned a uniform ALIVE cell — the pool
    # is the read's own vocabulary (the distinct s:c<id> tokens the organism actually used, printed);
    # per draw the modal share per planted thing is computed exactly as the real one.
    distinct_cells = sorted({x for t in TOY_THINGS for x in per_thing[t].values()})
    C = len(distinct_cells)
    planted_shares = {name: recurrence[thing]["modal_share"] for name, thing in PLANTED.items()}
    real_share = (sum(s for s in planted_shares.values() if s is not None)
                  / max(1, sum(1 for s in planted_shares.values() if s is not None)))
    rng = np.random.default_rng([BENCH_SEED, 5500])
    null_shares = []
    for _k in range(TWINS_N):
        per_draw = []
        for name, thing in PLANTED.items():
            n = len(per_thing[thing])
            if n == 0 or C == 0:
                continue
            draws = [int(x) for x in rng.integers(0, C, size=n)]
            counts: dict = {}
            for x in draws:
                counts[x] = counts.get(x, 0) + 1
            per_draw.append(max(counts.values()) / n)
        null_shares.append(sum(per_draw) / max(1, len(per_draw)))
    null_max = max(null_shares) if null_shares else None
    return {"recurrence": recurrence, "multi_hyp_sightings": multi, "silent_sightings": silent,
            "stability_legacy": stability,
            "stability_legacy_ok": sum(1 for s in stability if s["same"] is True),
            "collisions": collisions, "distinct_tokens": len(owner), "ceiling": ceiling,
            "jitter_sigma": jitter,
            "kind_tokens": {name: sorted(set(per_thing[thing].values())) for name, thing in PLANTED.items()},
            "planted_share": real_share, "planted_share_per_thing": planted_shares,
            "null_cell_pool": C, "null_shares": null_shares, "null_max": null_max,
            "stability_gap": (None if null_max is None else real_share - null_max)}


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


def _back_window(stream: list, i: int, d: int = 3) -> list:
    """The web's own window (web.py:222 the previous d DISTINCT words, most recent first), computed
    exactly: the up-to-d distinct tokens before position i."""
    out: list = []
    for e in reversed(stream[:i]):
        t = e["token"]
        if t not in out:
            out.append(t)
        if len(out) == d:
            break
    return out


def assert_misaligned(stream: list, name: str, own_tokens: set) -> None:
    """AMENDMENT 2's placement check (G-PLANT iii-bis): the pair forms only when one token lands in
    the OTHER's back-window (the web's hear() pairs a new token with the previous d distinct). So:
    for every w:<name> position, its back-window must exclude the name's OWN thing's s: tokens; and
    for every own-thing token position, ITS back-window must exclude w:<name>. A violation raises
    (the twin generator's own misalignment is asserted, never assumed)."""
    wtok = "w:" + name
    pos = [i for i, e in enumerate(stream) if e["token"] == wtok]
    assert pos, f"assert_misaligned: no {wtok} tokens at all (the presence count is zero — the plant?)"
    for i, e in enumerate(stream):
        win = _back_window(stream, i)
        if e["token"] == wtok:
            bad = [t for t in win if t in own_tokens]
            assert not bad, f"misalignment violated for {wtok} at {i}: own tokens {bad} in the window"
        if e["token"] in own_tokens:
            assert wtok not in win, f"misalignment violated: own token at {i} has {wtok} in its window"


def misaligned(stream: list, seed: int, k: int, kind_sets: dict) -> list:
    """AMENDMENT 2's twin k: the planted names' w: tokens MOVED so each lands immediately AFTER a
    DIFFERENT planted thing's s: token (the targets rotated across the twins), never within the
    d-window of its OWN thing's s: tokens. The multisets and the cadence counts are the real run's;
    only the WINDOWS move. Slots are pre-filtered for legality (the 3-distinct back- AND front-
    windows free of the own thing's tokens), then drawn seeded; the placement is asserted
    (assert_misaligned) per name after the insertion."""
    names = sorted(kind_sets)
    rng = np.random.default_rng([seed, 9000 + k])
    out = list(stream)
    for j, name in enumerate(names):
        target = names[(j + 1) % len(names)]                # always the OTHER thing — never itself
        # (the seeded k varies the slot draws; the target must never rotate onto the name's own
        # thing — a self-target is an ALIGNED twin, the null's exact opposite; caught at draft by
        # the test's odd-k draws, fixed before any run)
        wtok = "w:" + name
        own = kind_sets[name]
        pulled = [e for e in out if e["token"] == wtok]
        out = [e for e in out if e["token"] != wtok]
        for e in pulled:
            legal = []
            for i, e2 in enumerate(out):                    # re-vetted on the LIVE list per
                if e2["token"] not in kind_sets[target]:    # insertion — earlier insertions shift
                    continue                                # later indices (a stale slot landed
                back = _back_window(out, i + 1)             # beside an own token in the first
                front = []                                  # form; caught by assert_misaligned,
                for e3 in out[i + 1:]:                      # fixed here)
                    if e3["token"] not in front:
                        front.append(e3["token"])
                    if len(front) == 3:
                        break
                if not any(t in own for t in back + front):
                    legal.append(i)
            assert legal, f"misaligned: no legal slots beside {target}'s tokens"
            i = int(legal[int(rng.integers(len(legal)))])
            out.insert(i + 1, dict(e))                      # immediately after the target's token
        if pulled:
            assert_misaligned(out, name, own)
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


def verdicts(on: dict, off: dict, rows: list, twins: list, pilot_reading: dict,
             twins_mis: Optional[list] = None) -> dict:
    """Every mark of the law §3, computed from the arms' records, presence counts beside every number."""
    out: dict = {}
    cons_on = set(on["consolidated"])
    cross_on = cross_edges(on)
    # M-CROSS — the planted kind's OWN cells counted apart from the d=3 window's adjacency cells
    # (D-kind): an edge is IN-KIND when its s: token is one of the planted thing's sighting tokens
    # (the window's neighbors — the preceding thing's cells — are printed too, never hidden)
    per_kind = {}
    kind_sets = {name: set(pilot_reading["kind_tokens"][name]) for name in PLANTED}
    for name in PLANTED:
        kind_edges_all = [k for k in cross_on if k.endswith("|w:" + name) or k.startswith("w:" + name + "|")]
        in_kind = []
        for k in kind_edges_all:
            a, b = k.split("|")
            s_tok = a if a.startswith("s:") else b
            if s_tok in kind_sets[name]:
                in_kind.append(k)
        ceil = pilot_reading["ceiling"][name]
        per_kind[name] = {"consolidated_cross": len(in_kind), "edges": in_kind,
                          "consolidated_cross_incl_window": len(kind_edges_all),
                          "window_edges": sorted(set(kind_edges_all) - set(in_kind)),
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
    # M-STABILITY — re-priced (AMENDMENT 1): the pilot's reading printed FIRST (the pilot block above);
    # the planted things' recurrence share must EXCEED the 10-draw random-assignment null's MAX
    out["M-STABILITY"] = {"bar": "the planted things' tokens recur at a share EXCEEDING the 10-draw "
                                 "random-assignment null's MAX (the null: each sighting assigned a uniform "
                                 "alive cell — the organism's read must be better than chance and strong; "
                                 "the real share printed beside the null's max, the smallest passing gap "
                                 "printed, #245 (5)). AMENDMENT 1's form; the old 16/16 boundary form is "
                                 "printed in the pilot for continuity (stability_legacy)",
                          "planted_share": pilot_reading["planted_share"],
                          "planted_share_per_thing": pilot_reading["planted_share_per_thing"],
                          "null_cell_pool": pilot_reading["null_cell_pool"],
                          "null_shares": pilot_reading["null_shares"],
                          "null_max": pilot_reading["null_max"],
                          "gap": pilot_reading["stability_gap"],
                          "legacy_16": f"{pilot_reading['stability_legacy_ok']}/"
                                       f"{len(pilot_reading['stability_legacy'])}",
                          "pass": (pilot_reading["null_max"] is not None
                                   and pilot_reading["planted_share"] > pilot_reading["null_max"])}
    # M-NULL — AMENDMENT 2's re-priced form (the hub lesson: the derangement twins are blind to the
    # recognition key's concentration — they stay as the COUNT clause and a printed legacy reading):
    # the EVENT-MATCHED (misaligned) twins must never consolidate the planted PAIR (the name ↔ its
    # OWN thing's tokens), and the real run's consolidated cross-edge count exceeds the derangement
    # twins' MAX (the hub inflation is shared by the twins, so the excess is the teaching's).
    twin_cross = [t["consolidated_cross_n"] for t in twins]
    twin_planted = [t["planted_consolidated"] for t in twins]       # the legacy reading (printed)
    mis = twins_mis or []
    mis_pair = [t["planted_pair_consolidated"] for t in mis]
    mis_hub = {name: [t["name_other_edges"].get(name, []) for t in mis] for name in PLANTED}
    out["M-NULL"] = {"bar": "AMENDMENT 2: 10 event-matched (misaligned) twins — the planted PAIR "
                            "consolidates in NONE of them (0/10); AND the real run's consolidated "
                            "cross-edge count exceeds the derangement twins' MAX. (The deranged "
                            "twins' planted-pair readings are printed as the legacy reading — they "
                            "are hub-blind by measurement, never deleted.)",
                     "misaligned_pair_consolidated": mis_pair,
                     "misaligned_hub_readings": {k: [len(x) for x in v] for k, v in mis_hub.items()},
                     "legacy_deranged_planted": twin_planted,
                     "twin_cross_counts": twin_cross,
                     "real_cross_n": len(cross_on), "null_max": (max(twin_cross) if twin_cross else None),
                     "pass": len(mis) == TWINS_N and not any(mis_pair)
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
    p = pilot(on, rows, tape_root)
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
    # AMENDMENT 2 (the hub lesson — the derangement null is blind to the recognition key's
    # concentration): the event-matched twins — the planted names' tokens MOVED to sit beside a
    # DIFFERENT thing's windows, never their own. The planted PAIR (the name ↔ its OWN thing's
    # tokens) must never consolidate; a name consolidating onto OTHER cells is the hub reading,
    # printed per twin, never hidden.
    kind_sets = {name: set(p["kind_tokens"][name]) for name in PLANTED}
    twins_mis = []
    for k in range(twins_n):
        mis_stream = misaligned(on["stream"], BENCH_SEED, k, kind_sets)
        w = feed_web([e["token"] for e in mis_stream], seed)
        cons = [f"{a}|{b}" for a, b in w.consolidated()]
        planted_pair = False
        name_edges: dict = {}
        for name in PLANTED:
            hits = [key for key in cons
                    if (key.split("|")[0] == "w:" + name and key.split("|")[1] in kind_sets[name])
                    or (key.split("|")[1] == "w:" + name and key.split("|")[0] in kind_sets[name])]
            if hits:
                planted_pair = True
            name_edges[name] = [key for key in cons
                                if "w:" + name in key.split("|") and key not in hits]
        twins_mis.append({"k": k, "planted_pair_consolidated": planted_pair,
                          "name_other_edges": name_edges, "web_t": w.t, "stats": dict(w.stats)})
    v = verdicts(on, off, rows, twins, p, twins_mis)
    # durable evidence: the streams, the web readings, the report
    (out / "stream-on.json").write_text(json.dumps(on["stream"]))
    (out / "stream-off.json").write_text(json.dumps(off["stream"]))
    (out / "pilot.json").write_text(json.dumps(p, indent=2, default=str))
    (out / "twins.json").write_text(json.dumps(twins, indent=2, default=str))
    (out / "twins-misaligned.json").write_text(json.dumps(twins_mis, indent=2, default=str))
    (out / "report.json").write_text(json.dumps(v, indent=2, default=str))
    lines = ["CONTENT-WEB bench — the law's marks (PREREG-CONTENT-WEB §3)", ""]
    lines.append(f"toy: {len(TOY_THINGS)} things x {rounds} rounds · the planted arc "
                 f"{ {n: t for n, t in PLANTED.items()} } x {CHAT_ARC_N} one-word chat rows each · "
                 f"rows {on['rows']} · sleeps {on['sleeps']} · org.t {on['org_t']}")
    lines.append(f"web (ON, rule L): t {on['web_t']} · stats {json.dumps(on['web_stats'], sort_keys=True)}")
    lines.append(f"web (OFF): t {off['web_t']} · stats {json.dumps(off['web_stats'], sort_keys=True)}")
    lines.append("")
    lines.append("THE PILOT (printed before any mark binds — #228):")
    lines.append(f"  recurrence (the recognition key, AMENDMENT 1): "
                 f"{json.dumps({t: {'sightings': r['sightings'], 'distinct': r['distinct'], 'modal': r['modal'], 'modal_share': r['modal_share']} for t, r in p['recurrence'].items()})}")
    lines.append(f"  multi-hypothesis sightings: {p['multi_hyp_sightings']} · silent sightings (the declared "
                 f"floor): {p['silent_sightings']} · distinct s: tokens {p['distinct_tokens']} "
                 f"· all-pairs collisions {p['collisions']}")
    lines.append(f"  render-jitter sigma (the diagnostic of record — it killed the old form): "
                 f"{json.dumps({t: {'sigma_mean': round(p['jitter_sigma'][t]['sigma_mean'], 4), 'sigma_max': round(p['jitter_sigma'][t]['sigma_max'], 4)} for t in TOY_THINGS})}")
    lines.append(f"  cross-boundary stability, the OLD instrument's 16-comparison form (continuity): "
                 f"{p['stability_legacy_ok']}/{len(p['stability_legacy'])}")
    lines.append(f"  M-STABILITY's re-priced pieces: planted share {p['planted_share']:.4f} "
                 f"(per thing {json.dumps(p['planted_share_per_thing'])}) · null pool {p['null_cell_pool']} cells "
                 f"· null shares {[round(x, 4) for x in p['null_shares']]} · null MAX {p['null_max']:.4f} "
                 f"· gap {p['stability_gap']:.4f}")
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
    """The pilot readings only (measured-first, RULES §6d): the recurrence, the collisions, the
    render-jitter σ, the chances ceiling — before any arm's marks are read."""
    work = out / "probe"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    clock = _Clock()
    build_tape(work, clock)
    rows = _rows(work)
    on = drive(work, True, work / "probe-on")
    p = pilot(on, rows, work)
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
