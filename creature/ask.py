# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:35 +0400 — A7: the ask door (docs/G4-PREREG.md §2.7).
"""creature/ask.py — the voice: answers from the LATEST snapshot in a PRIVATE Organism, never the live
mind's objects. Reuses genome/ask.py's own answer logic (glance_picture, word_cells) rather than
re-deriving the rules; never writes memory (a question never changes him, PREREG §2.7).

    python3 -m creature.ask --root R what-is <picture>
    python3 -m creature.ask --root R show <word>
    python3 -m creature.ask --root R is <picture> <word>
    python3 -m creature.ask --root R which <a> <b> <word>

The body runs `inbox_loop` as a thread: it polls root/ask/in/<id>.json {"q", "pic", "word", "pic_b"} and
writes root/ask/out/<id>.json with the answer (PREREG §2.7's inbox/outbox shape; "pic_b" is this file's
own extension for "which", which needs a second picture the PREREG's {"q","pic","word"} schema does not
carry — see the builder report).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from genome import ask as genome_ask
from genome.machinery import Genome, Organism, parse_genome
from genome.questions import why as questions_why
from genome.world import encode_word

Ledger = Dict[int, Set[str]]


# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.4 (docs/G4-WAVE3-CLAUSES.md W3-0b):
# ASK's declared verb list. ASK undeclared keeps today's unrestricted default (every verb `answer()`
# implements stays reachable, matching creature/genes.py's own finding that ASK's value is not read at
# all today); ASK declared gates on `declared['ASK']['verbs']` -- a verb not in that list is refused BY
# NAME, a row, never the ValueError `answer()` raises for a genuinely unimplemented verb.
def _ask_refusal(genome: Genome, q: str) -> Optional[str]:
    verbs = genome.declared.get("ASK", {}).get("verbs")
    if verbs is not None and q not in verbs:
        return f"refused: {q} is not an ASK verb"
    return None


def load_snapshot(run_root: Path) -> Tuple[Genome, Organism, Ledger, Ledger]:
    """The latest snapshot into a PRIVATE Organism (never the live mind's own). Raises
    FileNotFoundError if the mind has not snapshotted yet (every SNAPSHOT_EVERY moments, or close())."""
    state_dir = Path(run_root) / "state"
    meta_path = state_dir / "organism.json"
    ledger_path = state_dir / "ledger.json"
    if not meta_path.exists() or not ledger_path.exists():
        raise FileNotFoundError(f"no snapshot yet under {state_dir} (the mind snapshots every 500 moments, and on close())")
    meta = json.loads(meta_path.read_text())
    genome = parse_genome(meta["genome_text"])
    org = Organism.load(state_dir / "organism", genome)
    ledger = json.loads(ledger_path.read_text())
    Ls: Ledger = {int(k): set(v) for k, v in ledger.get("sight", {}).items()}
    Lw: Ledger = {int(k): set(v) for k, v in ledger.get("words", {}).items()}
    return genome, org, Ls, Lw


def render_what_is(picture_name: str, r: Dict[str, object], org: Organism, Lw: Ledger) -> str:
    """L-6/ANSWER (docs/briefs/LIFE-A-ANSWER-SELF.md #2): the graded sentence, given an ALREADY-COMPUTED
    `org.recall_many("sight", ...)` result -- split out from `answer()` so it is testable without a real
    picture on disk. `grade is None` (ANSWER undeclared -- every genome on disk before this gene) reaches
    the EXACT prior line, byte for byte; a `sure` answer with a cell also renders exactly as before. Only
    `unsure`/an abstain graded `sure`-or-`unsure` route to the "resembles" sentence; `unknown` (or a
    resemblance that resolves to no word at all) falls to "I do not know this", same as an ungraded
    abstain always did."""
    grade = r.get("grade")
    ans = "/".join(sorted(Lw.get(r["cell"], set()))) if r["cell"] is not None else None
    if grade is None or (ans is not None and grade == "sure"):
        return f"what-is {picture_name} -> {ans if ans else 'I do not know this'} ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})"
    if grade in ("sure", "unsure"):
        if ans is not None:
            resembles = ans                                     # reason=="answer": r["cell"] IS the words cell already
        else:
            resembles_cell = r.get("resembles_cell")             # an abstain (or a novel): the SIGHT cell the grade rests on
            ans_cell = org._answer_of(org.sight, resembles_cell) if resembles_cell is not None else None
            resembles = "/".join(sorted(Lw.get(ans_cell, set()))) if ans_cell is not None else None
        if resembles:
            label = "unsure" if r["reason"] == "answer" else r["reason"]
            return (f"what-is {picture_name} -> I don't know what it is, but it resembles {resembles} "
                    f"({label}; cos {r['cos']:.3f} under {resembles}'s own floor {r['own_floor']:.3f})")
    return f"what-is {picture_name} -> I do not know this ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})"


def answer(run_root: Path, q: str, args: List[str]) -> str:
    """The same rules genome/ask.py's main() applies for each command, over a PRIVATE Organism loaded
    from run_root's latest snapshot. Never mutates `org` (Organism.recall_many/edge_many never do)."""
    genome, org, Ls, Lw = load_snapshot(run_root)
    refusal = _ask_refusal(genome, q)
    if refusal is not None:
        return refusal
    if q == "what-is":
        r = org.recall_many("sight", genome_ask.glance_picture(Path(args[0]), genome))
        return render_what_is(args[0], r, org, Lw)
    if q == "show":
        r = org.recall_many("words", [encode_word(args[0], genome.ear_blank_zero)])
        ans = "/".join(sorted(Ls.get(r["cell"], set()))) if r["cell"] is not None else None
        return f"show {args[0]} -> {('a picture of ' + ans) if ans else 'I do not know this word'} ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f})"
    if q == "is":
        r = org.recall_many("sight", genome_ask.glance_picture(Path(args[0]), genome))
        yes = r["cell"] is not None and Lw.get(r["cell"], set()) == {args[1]}
        read = "/".join(sorted(Lw.get(r["cell"], set()))) if r["cell"] is not None else "nothing"
        return f"is {args[0]} {args[1]} -> {'yes' if yes else 'no'} ({r['reason']}; it reads {read})"
    if q == "which":
        wc = genome_ask.word_cells(org, Lw, args[2])
        ea = max([org.edge_many("sight", genome_ask.glance_picture(Path(args[0]), genome), c) for c in wc], default=0.0)
        eb = max([org.edge_many("sight", genome_ask.glance_picture(Path(args[1]), genome), c) for c in wc], default=0.0)
        pick = args[0] if ea > eb else (args[1] if eb > ea else "neither (tie)")
        return f"which {args[0]} {args[1]} {args[2]} -> {pick} (edges {ea:.3f} vs {eb:.3f}; word cells {len(wc)})"
    if q == "why":
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:5x +0400 — L-14/G-MIND-8 (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #4): renders questions.why()'s own {cells, episodes, edges} -- nothing new is computed. `episodes`
        # is always [] here: load_snapshot() (this module) never loads the FAST episode store (episodes.npz),
        # only the Organism + ledgers -- RAISED in the report, not silently worked around; `why()` itself
        # already documents `episodes=None` as a valid, honest call ("no FAST store yet").
        ledgers = {"sight": Ls, "words": Lw}
        rec = questions_why(org, ledgers, None, args[0])
        return f"why {args[0]} -> cells {rec['cells']} episodes {rec['episodes']} edges {rec['edges']}"
    # edit: Claude (Fable 5.1), 2026-09-21 11:44 +0400 — W3-0's law at the verb level (Builder C's finding 6: `next`/`why` are declared by the
    # live ASK line and have NO interpreter): a declared verb nothing runs answers a refusal ROW naming itself, never a
    # ValueError that would restart the ask sense (#230's class). `why` is now wired above (L-14); `next` still has no
    # mechanism (no code path predicts a next thing) and refuses here by name, exactly as before.
    return f"refused: {q} is declared but has no interpreter yet (W3-0)"


def _args_for(req: Dict[str, object]) -> List[str]:
    q = req["q"]
    if q == "what-is":
        return [str(req["pic"])]
    if q == "show":
        return [str(req["word"])]
    if q == "is":
        return [str(req["pic"]), str(req["word"])]
    if q == "which":
        return [str(req["pic"]), str(req["pic_b"]), str(req["word"])]
    if q == "why":
        return [str(req["word"])]
    return []   # a verb with no interpreter takes no args; answer() refuses it by name (W3-0 at the verb level)


def inbox_loop(run_root: Path, stop_event, poll_period: float = 1.0) -> None:
    """The voice thread: polls root/ask/in/*.json, writes root/ask/out/<id>.json. Never touches the
    mind's live objects (load_snapshot always builds a fresh, private Organism)."""
    run_root = Path(run_root)
    in_dir = run_root / "ask" / "in"
    out_dir = run_root / "ask" / "out"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    while not stop_event.is_set():
        for req_path in sorted(in_dir.glob("*.json")):
            qid = req_path.stem
            out_path = out_dir / f"{qid}.json"
            if out_path.exists():
                continue
            req = None
            try:
                req = json.loads(req_path.read_text())
                text = answer(run_root, req["q"], _args_for(req))
                out_path.write_text(json.dumps({"id": qid, "q": req["q"], "answer": text, "error": None}))
            except Exception as e:
                out_path.write_text(json.dumps({"id": qid, "q": (req or {}).get("q"), "answer": None, "error": repr(e)}))
        stop_event.wait(poll_period)


def main(argv: List[str]) -> int:
    root = Path(argv[argv.index("--root") + 1])
    argv2 = [a for i, a in enumerate(argv) if a != "--root" and not (i > 0 and argv[i - 1] == "--root")]
    if not argv2:
        print(__doc__)
        return 1
    q, args = argv2[0], argv2[1:]
    print(answer(root, q, args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
