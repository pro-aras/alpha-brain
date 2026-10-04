"""creature/senses/mentor.py — PREREG-W2 §2 (SIGNED x3, t-l4-1003 5b32d03): THE MENTOR WORLD's table-driven generator.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:01 +0400 — new file, written after tests/tools/test_w2_templates.py
and test_w2_mentor.py were red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §2 (the carriers C1-C5, the frozen template
set v1, the seat decisions). Never a model, never next-token: every production is a row of the frozen table, TRUE by
construction from the record it is handed (M-PURE).

The interface. One Canvas is the record of one scene moment as the BENCH assembles it (the truth spec's things with their
boxes, the canvas's fix cells, the moment's resolved state, the organism's say and the ask's target, the canvas's ordinal).
`mentor_rows` returns the canvas's mentor EAR rows — one row per word, each carrying source "mentor" and its tpl id from the
frozen v1 set — in the canvas's declared order: the variation run (a due canvas) or C1, then C2, then the mirror tokens,
then the answers. A canvas with NO fixated thing is SILENT for C1/C3 (the follow-in rule: it names what is attended, never
redirects — seat decision 2/3, R3). The mirror tokens land on the state's OWN canvas (decision 3, T-L4's LAG1 lesson).
The answer is BUILT from the referent or the asked thing — never copied from the organism's own sentence (the self-voice
rule holds by construction; the answer's truth path is the referent's, the say only chooses the act M-A1 vs M-A2).

The variation schedule (declared; the law's §2 names it «the declared schedule»): a run is due when
`order % run_every(order) == 0`, with run_every(order) = min(48, 3 << (order // 1000)) — every 3 canvases at the world's
start, the gap doubling each 1,000 canvases up to 48 (FRONT-LOADED, seat decision 8(a)). run_every is exported for the
tests and the bench's cadence print.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

SOURCE = "mentor"
NP_TEMPLATES = ("T1", "T2", "T3", "T4")

# -------------------------------------------------------------------------------------------------- the frozen template set v1
# The law's §2 table, verbatim (PREREG-W2, SIGNED x3; v1 frozen at signature; the set grows only by signed laws).
TEMPLATES_V1: Dict[str, Dict[str, str]] = {
    "M-C1-T1": {"surface": "alpha sees <shape>", "truth": "the referent is in the canvas's truth spec and fixated"},
    "M-C1-T2": {"surface": "alpha sees <colour> <shape>", "truth": "the referent is in the canvas's truth spec and fixated"},
    "M-C1-T3": {"surface": "alpha sees <size> <shape>", "truth": "the referent is in the canvas's truth spec and fixated"},
    "M-C1-T4": {"surface": "alpha sees <size> <colour> <shape>", "truth": "the referent is in the canvas's truth spec and fixated"},
    "M-C2-T1": {"surface": "alpha does not see <shape>", "truth": "a thing matching the NP is in the truth spec and never fixated"},
    "M-C2-T2": {"surface": "alpha does not see <colour> <shape>", "truth": "a thing matching the NP is in the truth spec and never fixated"},
    "M-C2-T3": {"surface": "alpha does not see <size> <shape>", "truth": "a thing matching the NP is in the truth spec and never fixated"},
    "M-C2-T4": {"surface": "alpha does not see <size> <colour> <shape>", "truth": "a thing matching the NP is in the truth spec and never fixated"},
    "M-C3": {"surface": "a run of >= 3 «alpha sees <NP>» rows, one carrier, one position changed, over the canvas's different things",
             "truth": "each row of the run passes its own M-C1 rule"},
    "M-M1": {"surface": "unsure", "truth": "doubt at the same canvas (no mature word holds the leading thing)"},
    "M-M2": {"surface": "fresh", "truth": "young at the same canvas (the name just heard met < 3 times)"},
    "M-M3": {"surface": "asked", "truth": "the previous canvas's act was ASK"},
    "M-A1": {"surface": "alpha sees <NP> (confirm)", "truth": "after a say TRUE of the attended thing; the attended thing named truly"},
    "M-A2": {"surface": "alpha sees <NP> (correct)", "truth": "after a say NOT true of the attended thing; the attended thing named truly"},
    "M-A3": {"surface": "alpha sees <NP> (re-name / the answer to an ask)", "truth": "the asked thing named truly"},
}

MENTOR_WORDS_V1: Tuple[str, ...] = ("alpha", "sees", "does", "not", "see", "unsure", "fresh", "asked")

_DOC_HEADER = """# MENTOR-TEMPLATES-v1 — the mentor world's frozen template set (PREREG-W2 §2, SIGNED x3 at t-l4-1003 5b32d03)
# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:01 +0400 — rendered from creature/senses/mentor.py's
# TEMPLATES_V1 by M.render_templates_v1(); the set is FROZEN at the law's signature (seat decision 8(d)) and grows only by
# signed laws (v2+). The equality of this file with the code table is pinned by tests/tools/test_w2_templates.py.

# tpl | surface | truth rule (the record)
"""


def render_templates_v1() -> str:
    """The versioned doc's exact bytes (the doc-equality test's reference; decision 8(d))."""
    out = [_DOC_HEADER]
    for tpl in sorted(TEMPLATES_V1):
        spec = TEMPLATES_V1[tpl]
        out.append(f"{tpl} | {spec['surface']} | {spec['truth']}\n")
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------- the canvas
@dataclass(frozen=True)
class Thing:
    """A thing of the truth spec: its class words and its picture box (px; the canvas is a 16 x 16 grid of 8 px cells)."""
    shape: str
    colour: str
    size: str
    top: int
    left: int
    side: int = 0

    def __post_init__(self):
        if not self.side:
            object.__setattr__(self, "side", 32 if self.size == "big" else 22)

    def cells(self, cell_px: int = 8, grid: int = 16) -> List[Tuple[int, int]]:
        """The grid cells the box covers (inclusive of partially covered cells, clamped to the grid)."""
        y0, x0 = self.top // cell_px, self.left // cell_px
        y1, x1 = (self.top + self.side - 1) // cell_px, (self.left + self.side - 1) // cell_px
        return [(y, x) for y in range(max(0, y0), min(grid - 1, y1) + 1) for x in range(max(0, x0), min(grid - 1, x1) + 1)]


def np_words(npt: str, t: Thing) -> Tuple[str, ...]:
    """The parent's own NP forms T1-T4 (brain/scene/world.py's template_words, verbatim)."""
    if npt == "T1":
        return (t.shape,)
    if npt == "T2":
        return (t.colour, t.shape)
    if npt == "T3":
        return (t.size, t.shape)
    if npt == "T4":
        return (t.size, t.colour, t.shape)
    raise ValueError(f"no such NP template: {npt!r}")


def word_true_of(w: str, t: Thing) -> bool:
    return w in (t.shape, t.colour, t.size)


@dataclass
class Canvas:
    """One scene moment's record as the bench hands it to the generator."""
    moment: str
    things: List[Thing]
    fix: List[List[int]]                       # the canvas's fixated cells [[y, x], ...]
    state: Dict[str, int]                      # doubt, young, ask_prev (0/1), resolved from the record by the bench
    say: Optional[List[str]] = None
    ask_target: Optional[int] = None
    order: int = 0


def fixation_hits(t: Thing, fix: Sequence[Sequence[int]]) -> int:
    """The organism's own seen rule (brain/scene/world.py:569's fixation_thing): the fixation cells whose CENTRE pixel
    (y*8+4, x*8+4) lands in the thing's box ± 4 px, half-open."""
    return sum(1 for y, x in fix if t.top - 4 <= int(y) * 8 + 4 < t.top + t.side + 4 and t.left - 4 <= int(x) * 8 + 4 < t.left + t.side + 4)


def _fixated(canvas: Canvas) -> List[int]:
    """The thing indices with >= 1 fixated cell by the organism's own seen rule, in things order."""
    return [i for i, t in enumerate(canvas.things) if fixation_hits(t, canvas.fix) >= 1]


def referent(canvas: Canvas) -> Optional[int]:
    """The follow-in referent: the thing holding the MOST fixated cells by the organism's own seen rule (the FIRST
    maximum in things order; `mentor_rows` breaks a tie with the canvas's own rng, `substream(seed, "w2:mentor:reftie:<canvas>")`).
    None when nothing is fixated."""
    best, best_n = None, 0
    for i, t in enumerate(canvas.things):
        n = fixation_hits(t, canvas.fix)
        if n > best_n:
            best, best_n = i, n
    return best


def _referent_pick(canvas: Canvas, rng) -> Optional[int]:
    """The referent with ties broken by the canvas's rng (the law's `w2:mentor:reftie` rule)."""
    counts = [fixation_hits(t, canvas.fix) for t in canvas.things]
    best = max(counts, default=0)
    if best == 0:
        return None
    tied = [i for i, n in enumerate(counts) if n == best]
    return tied[int(rng.integers(len(tied)))] if len(tied) > 1 else tied[0]


def run_every(order: int) -> int:
    """The declared variation schedule (front-loaded, seat decision 8(a)): 3, doubling each 1,000 canvases, capped 48."""
    return min(48, 3 << (order // 1000))


# -------------------------------------------------------------------------------------------------------- the productions
def _ear(moment: str, word: str, tpl: str) -> Dict[str, object]:
    assert word.isalpha() and word.islower() and len(word) <= 8, f"a mentor word outside the ear's alphabet: {word!r}"
    return {"sense": "ear", "meta": {"moment": moment, "source": SOURCE, "word": word, "tpl": tpl},
            "payload": word.encode("utf-8")}


def _sentence(moment: str, head: Sequence[str], np: Sequence[str], tpl_per_word: str) -> List[Dict[str, object]]:
    return [_ear(moment, w, tpl_per_word) for w in list(head) + list(np)]


def productions(rows: Sequence[Dict[str, object]]) -> List[List[str]]:
    """Segment a stream of ear rows into productions: a new production starts at every «alpha» and at every mirror token
    (the world's only sentence-initial words). Returns the word lists."""
    out: List[List[str]] = []
    for r in rows:
        w = r["meta"]["word"]
        if not out or w in ("alpha", "unsure", "fresh", "asked"):
            out.append([])
        out[-1].append(w)
    return out


def mentor_rows(canvas: Canvas, rng) -> List[Dict[str, object]]:
    """The canvas's mentor ear rows, in the declared order: the run (due) or C1, C2, the mirror tokens, the answers."""
    rows: List[Dict[str, object]] = []
    m = canvas.moment
    fix = _fixated(canvas)
    ref = _referent_pick(canvas, rng)
    # ---- C3 (a due canvas with >= 2 fixated things) or C1
    if ref is not None and len(fix) >= 2 and canvas.order % run_every(canvas.order) == 0:
        npt = NP_TEMPLATES[int(rng.integers(len(NP_TEMPLATES)))]
        picks = list(fix)
        rng.shuffle(picks)
        if len(picks) >= 3:
            chosen = picks[:3]
        else:
            chosen = [picks[0], picks[1], picks[0]]                 # the A B A of a two-thing run
        for i in chosen:
            rows.extend(_sentence(m, ("alpha", "sees"), np_words(npt, canvas.things[i]), "M-C3"))
    elif ref is not None:
        npt = NP_TEMPLATES[int(rng.integers(len(NP_TEMPLATES)))]
        rows.extend(_sentence(m, ("alpha", "sees"), np_words(npt, canvas.things[ref]), f"M-C1-{npt}"))
    # ---- C2 (the polarity pair; seat decision 4): an unseen thing whose NP is true of NO fixated thing, or silence
    c2_pairs = []
    for i, t in enumerate(canvas.things):
        if i in fix:
            continue
        for npt in NP_TEMPLATES:
            npw = np_words(npt, t)
            if not any(all(word_true_of(w, canvas.things[j]) for w in npw) for j in fix):
                c2_pairs.append((i, npt))
    if c2_pairs:
        i, npt = c2_pairs[int(rng.integers(len(c2_pairs)))]
        rows.extend(_sentence(m, ("alpha", "does", "not", "see"), np_words(npt, canvas.things[i]), f"M-C2-{npt}"))
    # ---- the mirror tokens (the state's OWN canvas; decision 3)
    for flag, word, tpl in (("doubt", "unsure", "M-M1"), ("young", "fresh", "M-M2"), ("ask_prev", "asked", "M-M3")):
        if canvas.state.get(flag):
            rows.append(_ear(m, word, tpl))
    # ---- the answers (decision 8(b); built from the referent / the asked thing, never copied)
    if canvas.say is not None and ref is not None:
        tpl = "M-A1" if all(word_true_of(w, canvas.things[ref]) for w in canvas.say) else "M-A2"
        npt = NP_TEMPLATES[int(rng.integers(len(NP_TEMPLATES)))]
        rows.extend(_sentence(m, ("alpha", "sees"), np_words(npt, canvas.things[ref]), tpl))
    if canvas.ask_target is not None:
        npt = NP_TEMPLATES[int(rng.integers(len(NP_TEMPLATES)))]
        rows.extend(_sentence(m, ("alpha", "sees"), np_words(npt, canvas.things[canvas.ask_target]), "M-A3"))
    return rows
