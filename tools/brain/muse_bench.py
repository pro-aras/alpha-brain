"""muse_bench.py — the CONTEMPLATE-1 bench (PREREG-CONTEMPLATE-1 §3; docs/brain/muse/).

edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:37 +0400 — the law's bench, written AFTER
the law (law before code) and AFTER its G-UNIT (faa8bd2). One run drives the arc and writes the report:

    python3 -B tools/brain/muse_bench.py OUTDIR
    python3 -B tools/brain/muse_bench.py --probe OUTDIR     # the toy world's web/maturity readings only

THE TOY (the law §3, declared before any reading): a small organism state built by LIVING a toy world —
the N1 bench's own 8 things (TOY_THINGS, precision_bench's POOL_B) shown cycling on maker canvases
(THING_ROUNDS rounds), and the SELF carrying «alpha» hearsay: the parent says «you are alpha» HEARSAY_N
times, ear-only (heard, never shown — a name, not a thing), each time right after a «star» moment in the
life's last third (the sticky-pair window: the web's own consolidation math, verified by --probe before
any arm ran). The organism body is A4L-LANG's own + the BRAIN line (the inner-mind fixture's form,
calibrate at 20 40 60) with SLEEP re-declared at 200 moments so the arc crosses a consolidation pass.

THE ARC (the law §3's order): the planted sentence «you are alpha» (a chat row by the door's own road) →
the control «the circle is big» → the 10 shuffled twins (the same bag, order destroyed — non-identity
permutations of the planted sentence, 10 seeded draws, printed) → the tentative re-ask (M-TENTATIVE's
composer half) → the bench's parent answers the chain's what-is «alpha» through the LEXICON door's own
form (gloss ear rows + the rendered gloss eye row + the q-<n>.answered.json marker; the other two
questions stay on the record as asked-and-unanswered — promotion's condition (i) is chain-level, §1.4's
letter) → FILLER thing moments to cross the SLEEP boundary → the fruit re-ask → the twin re-asks.

Arms: real (muse=True), off (muse=False, M-COST's baseline, the SAME tape), plant (a short tape: toy
life + the control ALONE under a doctored trigger that fires on every sentence — the control-sentence
check must catch it; the plant asserts it changed the bytes).

Bench decisions the law left to the builder (written down, never guessed silently — the think.py pattern):
  D-fruit   the fruit's answer = the chain's candidacy rows' words in chain order, deduped, capped at the
            CHAT line's own max_words; every word printed with its [tentative -> candidacy] line trace.
  D-null    the 10 twins are 10 seeded NON-IDENTITY permutations of the 3-word bag (only 5 distinct
            orders exist; the draws repeat with fixed seeds, each printed). They arrive INSIDE the
            budget window of the planted chain: "spawn no self-chains" is read under the declared budget
            (G-UNIT(c)'s own pin), and "no fruit" under the content address — a bag-keyed fruit store
            WOULD answer the twin re-asks, and this null catches exactly that (the verifier's teeth).
  D-walk    the chain rests when the web's consolidated neighbourhood among mature words is exhausted
            (never INNER's self-restart — the thought is ABOUT the heard claim).
"""
from __future__ import annotations

import io
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

import creature.muse as MUSE
from creature.mind import Mind
from creature.senses import chat as chat_sense
from creature.senses import read_common
from creature.tape import Tape
from genome import think, web as _web, world

ROOT = Path(__file__).resolve().parents[2]
TOY_THINGS = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star"]   # the N1 bench's own 8
BENCH_SEED = 20261010                # declared, fixed before any run
THING_ROUNDS = 30                    # 240 thing moments, the 8-cycle
HEARSAY = ("you", "are", "alpha")    # the hearsay sentence — the law's own
HEARSAY_N = 12                       # occurrences (the web's own consolidation window; --probe verifies)
PLANTED = "you are alpha"
CONTROL = "the circle is big"
TWINS_N = 10
GLOSS = {"alpha": "the name of the creature"}     # the bench parent's declared answer to what-is «alpha»
HEARSAY_CLAIM = ("HEAR-1", "you are alpha.", "usually", 0.5)   # the SELF's «alpha» hearsay (the law §3's toy)
FILLER_MOMENTS = 60                  # thing moments after the answers (>= one SLEEP boundary's 200 moments)
SLEEP_LINE = "SLEEP    every 200 moments replay 50 by surprise"
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3 nearest; "
              "calibrate at 20 40 60 and before a sitting; replay none; hears toy")
COST_BAR = 0.05
# the arc's chat ids, in consume order (the door publishes in bytewise filename order): batch 1 runs to
# the tentative re-ask, the parent's answers and the fillers follow on the tape, batch 2 is the re-asks.
CID_PLANTED, CID_CONTROL, CID_TENT, CID_FRUIT = "c01planted", "c02control", "c13tent", "c14fruit"
CID_TWINS = [f"c{k + 3:02d}twin{k:02d}" for k in range(TWINS_N)]
CID_TWINRS = [f"c{k + 15:02d}twinr{k:02d}" for k in range(TWINS_N)]


def genome_text() -> str:
    """A4L-LANG's own body + the BRAIN line (hears the toy hand) with SLEEP re-declared at 200 moments."""
    text = (ROOT / "genome" / "ladder" / "A4L-LANG.genome").read_text()
    text, n = re.subn(r"^SLEEP\s+every 2500 moments replay 200 by surprise.*$", SLEEP_LINE, text, count=1, flags=re.M)
    assert n == 1, "the A4L-LANG SLEEP line moved — find the new form and re-declare the bench's"
    return text + "\n" + BRAIN_LINE + "\n"


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


def hearsay_after() -> set:
    """The thing-moment indices after which a hearsay moment follows: the last HEARSAY_N «star» moments
    (star is TOY_THINGS[-1], one per round) — the sticky window at the life's tail."""
    star_ix = [i for i in range(THING_ROUNDS * len(TOY_THINGS)) if TOY_THINGS[i % len(TOY_THINGS)] == "star"]
    return set(star_ix[-HEARSAY_N:])


def twin_texts(n: int = TWINS_N) -> list:
    """The 10 shuffled twins: seeded NON-IDENTITY permutations of the planted bag (D-null)."""
    bag = PLANTED.split()
    rng = np.random.default_rng([BENCH_SEED, 7])
    out = []
    while len(out) < n:
        p = [bag[int(i)] for i in rng.permutation(len(bag))]
        if p != bag:
            out.append(" ".join(p))
    return out


def build_tape(root: Path, clock: _Clock, short: bool = False) -> Tape:
    """The arc's tape, one deterministic build (the SAME tape feeds every arm). `short` = the plant
    arm's form: a brief toy life and ONLY the control chat."""
    tape = Tape(root)
    rounds = 8 if short else THING_ROUNDS
    after = hearsay_after() if not short else set(sorted(i for i in range(rounds * len(TOY_THINGS))
                                                         if TOY_THINGS[i % len(TOY_THINGS)] == "star")[-4:])
    k = 0
    for i in range(rounds * len(TOY_THINGS)):
        thing = TOY_THINGS[i % len(TOY_THINGS)]
        moment = f"toy{i:06d}"
        tape.publish("ear", thing.encode(), {"moment": moment, "source": "toy", "word": thing}, "txt", at=clock())
        rgb, _t = world.render_canvas(thing, np.random.default_rng([BENCH_SEED, k]))
        k += 1
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "toy"}, "png", at=clock())
        if i in after:
            hm = f"hear{i:06d}"
            for w in HEARSAY:
                tape.publish("ear", w.encode(), {"moment": hm, "source": "toy", "word": w}, "txt", at=clock())
    # the chats, by the door's own road (chat/in + scan_once) — BATCH 1: the planted, the control, the
    # ten twins, the tentative re-ask (the arc's order is the cids' bytewise order)
    def publish_chats(texts: dict) -> None:
        (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
        for cid, text in texts.items():
            (root / "chat" / "in" / f"{cid}.json").write_text(json.dumps({"id": cid, "text": text}))
        for _ in texts:
            chat_sense.scan_once(lambda s, p, m, e: tape.publish(s, p, m, e, at=clock()), root, canvas=128, letters=8)

    twins = twin_texts()
    batch1 = {CID_PLANTED: PLANTED, CID_CONTROL: CONTROL,
              **{cid: t for cid, t in zip(CID_TWINS, twins)}, CID_TENT: PLANTED}
    publish_chats({"control": CONTROL} if short else batch1)
    if short:
        return tape
    # the parent's answer rows, the lexicon door's own form (creature/senses/lexicon.py:_moment_id's own
    # sha; the qid is deterministic: the chain's «alpha» want is the THIRD filed (steps you/are/alpha ->
    # q-0/q-1/q-2) — printed in the report)
    import hashlib
    for qid, (word, gloss) in enumerate(GLOSS.items(), start=2):
        moment = "lex" + hashlib.sha256(f"{word}:q-{qid}".encode("utf-8")).hexdigest()[:8]
        for w in gloss.split():
            tape.publish("ear", w.encode(), {"moment": moment, "source": "lexicon", "word": w}, "txt", at=clock())
        rgb = read_common.render_line(gloss, 128, read_common.DEFAULT_FONT_PATH)
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "lexicon", "answers": word, "gloss": gloss},
                     "png", at=clock())
    # the fillers (cross the SLEEP boundary)
    for i in range(FILLER_MOMENTS):
        thing = TOY_THINGS[i % len(TOY_THINGS)]
        moment = f"fill{i:06d}"
        tape.publish("ear", thing.encode(), {"moment": moment, "source": "toy", "word": thing}, "txt", at=clock())
        rgb, _t = world.render_canvas(thing, np.random.default_rng([BENCH_SEED, k]))
        k += 1
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "toy"}, "png", at=clock())
    # BATCH 2: the fruit re-ask and the twin re-asks (after the answers + the consolidation pass)
    publish_chats({CID_FRUIT: PLANTED, **{cid: t for cid, t in zip(CID_TWINRS, twins)}})
    return tape


def _rows(tape_root: Path) -> list:
    from creature.tape import read_tape
    return list(read_tape(tape_root))


def _journal(root: Path) -> list:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
    return out


def _out_answer(root: Path, cid: str):
    p = root / "chat" / "out" / f"{cid}.json"
    return json.loads(p.read_text())["answer"] if p.exists() else None


def _say(root: Path, cid: str) -> dict:
    for r in _journal(root):
        s = r.get("say")
        if s and s.get("id") == cid:
            return s
    return {}


def drive(tape_root: Path, muse_flag: bool, work: Path, plant: bool = False) -> dict:
    """One mind over the tape. At the declared checkpoint (the row right after the parent's answer eye
    row) the bench AS the parent marks the answered question's file (the lexicon door's own marker).
    Returns the arc's records and the consumed process time (M-COST's own measure, N1's form)."""
    root = work
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "tape").symlink_to((tape_root / "tape").resolve(), target_is_directory=True)
    gp = root.parent / f"g-{root.name}.genome"
    gp.write_text(genome_text())
    m = Mind(gp, root, muse=muse_flag)
    # the law §3's toy: the SELF carries «alpha» hearsay (the KW-1 implanted-knowledge form) — the toy
    # state itself, placed in EVERY arm (real/off/plant), never by the mechanism
    if m.self_node is not None:
        m.self_node.place(_web.Claim(HEARSAY_CLAIM[0], HEARSAY_CLAIM[1], HEARSAY_CLAIM[2], HEARSAY_CLAIM[3],
                                     source="implanted-knowledge", author="toy-parent"))
    rows = _rows(tape_root)
    rec: dict = {"rows": len(rows), "muse": muse_flag, "plant": plant}
    real_trigger = MUSE.trigger
    calls = {"n": 0}

    def doctored(words, web, self_ws, mature):
        calls["n"] += 1
        out = dict(real_trigger(words, web, self_ws, mature))
        out.update({"fire": True, "anchors": [str(w) for w in dict.fromkeys(words)], "classes": ["planted"]})
        return out

    if plant:
        MUSE.trigger = doctored
    answered_marked = False
    t0 = time.process_time()
    try:
        for row in rows:
            m.consume(row)
            if not answered_marked and row["sense"] == "eye" and (row.get("meta") or {}).get("source") == "lexicon":
                qdir = root / "world" / "questions"
                for qp in sorted(qdir.glob("q-*.json")) if qdir.exists() else []:
                    try:
                        req = json.loads(qp.read_text())
                    except (OSError, ValueError):
                        continue
                    if req.get("word") in GLOSS:
                        qp.rename(qp.with_name(qp.stem + ".answered.json"))
                answered_marked = True
        m.close()
    finally:
        if plant:
            MUSE.trigger = real_trigger
    rec["cpu_s"] = time.process_time() - t0
    rec["answered_marked"] = answered_marked
    J = _journal(root)
    rec["muse_rows"] = [r for r in J if r.get("kind") == "muse"]
    rec["state"] = {k: m._muse[k] for k in ("heard", "chains_started")}
    rec["chains"] = {cid: {"heard": c["heard"], "anchors": c["anchors"], "classes": c["classes"],
                           "steps": c["steps"], "beliefs": c["beliefs"], "questions": c["questions"],
                           "promoted": c["promoted"], "reheard": c["reheard"]}
                     for cid, c in m._muse["chains"].items()}
    for key, cid in (("planted", CID_PLANTED), ("control", CID_CONTROL), ("tent", CID_TENT), ("fruit", CID_FRUIT)):
        rec[f"answer_{key}"] = _out_answer(root, cid)
        rec[f"say_{key}"] = _say(root, cid)
    rec["twin_answers"] = {cid: _out_answer(root, cid) for cid in CID_TWINS}
    rec["twinr_answers"] = {cid: _out_answer(root, cid) for cid in CID_TWINRS}
    bel = root / "state" / "beliefs.jsonl"
    raw = [json.loads(l) for l in bel.read_text().splitlines() if l.strip()] if bel.exists() else []
    rec["beliefs_raw_n"] = len(raw)
    rec["beliefs_statused_n"] = sum(1 for r in raw if "status" in r)
    rec["trusted_leaks"] = [r for r in think.read_beliefs(bel) + think.read_beliefs(bel, fold=True) if "status" in r] if bel.exists() else []
    claims = m.self_node.claims if m.self_node is not None else {}
    rec["self_claims_n"] = len(claims)
    rec["self_muse_sourced"] = [k for k, c in claims.items() if "muse" in (c.source or "")]
    rec["sleep_count"] = int(m.sleep_count)
    rec["web"] = _web_reading(m)
    rec["plant_calls"] = calls["n"]
    rec["brain_hash_final"] = m.brain.state_hash() if m.brain is not None else None
    # durable evidence: the arc's muse + say rows beside the report
    rec["_journal_rows"] = [r for r in J if r.get("kind") == "muse" or "say" in r]
    rec["_considered"] = think.read_considered(bel) if bel.exists() else []
    return rec


def _web_reading(m: Mind) -> dict:
    """The web's own reading of the toy (presence, never a bare claim): the watched words' node counts,
    the consolidated edges among them, the maturity of the control's words."""
    web = m.webs.get("L") if m.webs is not None else None
    if web is None:
        return {}
    watch = ["you", "are", "alpha", "star", "circle", "square", "the", "is", "big", "zog", "vex"]
    cons = set(web.consolidated())
    mature = set(str(w) for w in m.brain.L.mature_words()) if m.brain is not None else set()
    return {"t": web.t, "nodes": {w: (int(web.nodes[w]["n"]) if w in web.nodes else 0) for w in watch},
            "consolidated": sorted([f"{a}|{b}" for a, b in cons if a in watch and b in watch]),
            "consolidated_n": len(cons), "mature_n": len(mature),
            "control_mature": {w: (w in mature) for w in ("circle", "big")}}


def verdicts(real: dict, off: dict, plant: dict) -> dict:
    """Every mark of the law §3, computed from the arms' records, presence counts beside every number."""
    out: dict = {}
    chains = real["chains"]
    planted_chain = chains.get(MUSE.seed_of(PLANTED.split()), {})
    control_chain = chains.get(MUSE.seed_of(CONTROL.split()))
    n_beliefs = len(planted_chain.get("beliefs", []))
    n_questions = len(planted_chain.get("questions", []))
    out["M-CHAIN"] = {"bar": "exactly one chain on the planted sentence; >= 1 tentative belief AND >= 1 "
                             "counter-question (printed, presence counts); the control spawns NONE",
                      "chains_started": real["state"]["chains_started"], "beliefs": n_beliefs,
                      "questions": n_questions,
                      "question_words": [q["word"] for q in planted_chain.get("questions", [])],
                      "steps": [s["topic"] for s in planted_chain.get("steps", [])],
                      "control_chain_present": control_chain is not None,
                      "pass": real["state"]["chains_started"] == 1 and n_beliefs >= 1 and n_questions >= 1
                      and control_chain is None}
    out["M-HONEST"] = {"bar": "the immediate answer to the planted sentence stays an abstention (same breath)",
                       "answer": real["answer_planted"], "say_has_muse_key": "muse" in real["say_planted"],
                       "pass": real["answer_planted"] is None and "muse" not in real["say_planted"]}
    leaks = real["trusted_leaks"]
    out["M-TENTATIVE"] = {"bar": "no trusted read (the store both modes, the SELF's trusted claims, the "
                                 "composer's believed sets) contains a tentative row's content; presence counts",
                          "statused_on_disk": real["beliefs_statused_n"], "trusted_leaks": len(leaks),
                          "self_claims_n": real["self_claims_n"], "self_muse_sourced": len(real["self_muse_sourced"]),
                          "tentative_reask_answer": real["answer_tent"],
                          "pass": len(leaks) == 0 and len(real["self_muse_sourced"]) == 0
                          and real["beliefs_statused_n"] > 0 and real["answer_tent"] is None}
    twin_answers = [a for a in real["twinr_answers"].values()]
    twin_skips = [r for r in real["muse_rows"] if r.get("act") == "budget-skip"]
    fruit_say = real["say_fruit"].get("muse") or {}
    out["M-FRUIT"] = {"bar": "after the chain's questions are answered by the bench's parent AND one "
                             "consolidation pass, the re-ask yields a non-null answer whose words trace to "
                             "the chain's tentative rows (the trace printed). NULL: the 10 shuffled twins "
                             "spawn no self-chains and no fruit",
                      "promoted_pairs": planted_chain.get("promoted", []),
                      "sleeps": real["sleep_count"], "fruit_answer": real["answer_fruit"],
                      "trace": fruit_say.get("trace"),
                      "twin_budget_skips": len(twin_skips), "twin_chains_extra": real["state"]["chains_started"] - 1,
                      "twin_reask_answers": twin_answers,
                      "pass": bool(planted_chain.get("promoted")) and real["answer_fruit"] is not None
                      and bool(fruit_say.get("trace")) and real["state"]["chains_started"] == 1
                      and all(a is None for a in twin_answers) and len(twin_skips) >= TWINS_N}
    t_on, t_off = real["cpu_s"], off["cpu_s"]
    overhead = (t_on - t_off) / t_off if t_off > 0 else float("nan")
    out["M-COST"] = {"bar": f"ON vs OFF process_time overhead <= {COST_BAR:.0%} (N1's own measure)",
                     "cpu_on_s": t_on, "cpu_off_s": t_off, "overhead": overhead,
                     "sentences_heard": real["state"]["heard"],
                     "pass": overhead <= COST_BAR}
    plant_chains = plant["state"]["chains_started"]
    out["G-PLANT"] = {"bar": "the doctored trigger (fires on EVERY sentence) is CAUGHT by the "
                             "control-sentence check — the plant arm's control spawns a chain",
                      "plant_calls": plant["plant_calls"], "plant_control_chains": plant_chains,
                      "pass": plant["plant_calls"] > 0 and plant_chains > 0}
    return out


def probe(out: Path) -> int:
    """The toy world's own readings (measured-first, RULES §6d): the web's consolidation over the watched
    words, the control words' maturity — before any arm runs."""
    work = out / "probe"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    clock = _Clock()
    build_tape(work, clock)
    rec = drive(work, True, out / "probe-mind")
    reading = rec["web"]
    print(json.dumps({"web": reading, "chains": rec["state"], "sleeps": rec["sleep_count"]}, indent=2))
    return 0


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--probe":
        return probe(Path(sys.argv[2]))
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    tape_root = out / "tape-root"
    if tape_root.exists():
        shutil.rmtree(tape_root)
    tape_root.mkdir()
    clock = _Clock()
    build_tape(tape_root, clock)
    plant_root = out / "plant-tape"
    if plant_root.exists():
        shutil.rmtree(plant_root)
    plant_root.mkdir()
    build_tape(plant_root, clock, short=True)

    real = drive(tape_root, True, out / "run-real")
    off = drive(tape_root, False, out / "run-off")
    plant = drive(plant_root, True, out / "run-plant", plant=True)

    with (out / "arc-journal.jsonl").open("w") as f:
        for r in real["_journal_rows"]:
            f.write(json.dumps(r, default=str) + "\n")
    (out / "considered.json").write_text(json.dumps(real["_considered"], indent=2, default=str))
    (out / "web-reading.json").write_text(json.dumps(real["web"], indent=2, default=str))
    v = verdicts(real, off, plant)
    (out / "report.json").write_text(json.dumps(v, indent=2, default=str))
    lines = ["CONTEMPLATE-1 muse bench — the law's marks (PREREG-CONTEMPLATE-1 §3)", ""]
    lines.append(f"toy: things {TOY_THINGS} x {THING_ROUNDS} rounds · hearsay {HEARSAY} x {HEARSAY_N} · "
                 f"rows {real['rows']} · sleeps {real['sleep_count']}")
    lines.append(f"web: {json.dumps(real['web'], default=str)}")
    lines.append("")
    all_pass = True
    for mark, d in v.items():
        lines.append(f"{mark}: {'PASS' if d['pass'] else 'FAIL'} — bar {d['bar']}")
        for k, x in d.items():
            if k in ("bar", "pass"):
                continue
            lines.append(f"    {k}: {x}")
        all_pass = all_pass and bool(d["pass"])
        lines.append("")
    lines.append(f"BENCH VERDICT LINE: {'ALL MARKS PASS' if all_pass else 'AT LEAST ONE MARK FAILS'}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
