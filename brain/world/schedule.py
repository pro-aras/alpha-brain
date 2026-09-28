"""schedule.py — THE TAPE'S SCHEDULE, PURE (B1-PREREG.md §2.6–§2.7, §5.2–§5.5; docs/brain/b1/SEAT-DECISIONS.md
R2, R10–R21).

edit: Claude (Fable 5.1), 2026-09-24 18:09 +0400 — the seat, alone (Ahmad's 17:42 word: «only you do it now. No builders»).

NO RENDERING HERE. `build(seed, world)` returns a `Schedule`: the tape's rows in order with every glance
reference carried as a RENDERING ID (a string) where the written tape carries a cache row (an int), the flat
list of renderings the tape needs (each id unique — `brain.world.build.build_cache` refuses duplicates), the
truth record of every ask, the MLC side rows (R19), the SLEEP positions and every count. `brain/world/tape.py`
(the materialiser, `/usr/bin/python3` only) renders the list through `build_cache` and substitutes id → row.
The split is the advisor's (2026-09-24 17:5x): the counts test runs in seconds under either interpreter, and
nothing that decides WHAT is on the tape lives beside a gaze call.

The seed decides only the draws (§2.8): every draw comes from `brain.world.seeds.substream(seed, purpose)`
with a purpose string unique to the decision, so adding a rendering in one family moves nothing in another.
His order is A then B then C (`families.LETTER_NAMES`); the counts are fixed by the PREREG and pinned by
`tests/brain/harness/test_schedule.py`.

What this module takes as INPUT and never computes (stage −1's own outputs, §3.3): the never-taught pools
(40 U2 · 10 U6-refusal · 10 U5 · 1 plant), the plant's fonts (its TEACH font first, then ≥ 10 test fonts), and
the OTHER_CASE letters stage −1 removed. A pool short of its count is RAISED (§11), never padded.
"""
from __future__ import annotations

from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from . import families
from .names import DIGIT_CHARS, DIGIT_NAMES, LOWER, PLANT_NAME, UPPER, digit_name
from .seeds import substream

CASES: Tuple[str, str] = ("latin-upper", "latin-lower")
SLEEP_STEPS = 64                 # R16: A1's R; printed, read by each arm as it will
CANARY_PURPOSE_TEMPLATE = "canary:{sitting}"   # R15
POINT_SHEET_SIZE = 4             # §5.3 U1 (b): "among 4 glyphs of the same case"
MLC_K, MLC_Q = 3, 3
MLC_SLOTS = 4
MLC_SHIFTS = (3, 4, 5)
MLC_FORBIDDEN_DIFFS = (0, 1, 2)  # R19: no x -> x, x±1, x±2 in any MLC rule
REFUSE = "REFUSE"                # the truth's answer for a misuse / never-taught item (R20)


@dataclass(frozen=True)
class Params:
    """The schedule's counts. The DEFAULTS are the PREREG's (§2.7, §5.2–§5.5) and are what every graded tape
    is built with; `SMOKE` below is a small, fast world for the end-to-end tests of the materialiser
    (`tape.py`) — the SAME code path, never a second implementation (#173's class)."""
    teach_rounds: int = 12                 # §2.7 L1/L2/D: 12 rounds, 3 per TEACH font
    naming_reps: int = 3                   # NAME / POINT / IS "each 3 times"
    relation_reps_per_case: int = 3        # R10: "6 times" = 3 per case / direction
    perceptual_reps: int = 6               # R10: a FORM's 6 renderings
    control_reps: int = 3                  # SAME / CONST: "13 letters per case, 3 times"
    l5_rounds: int = 6
    probe_after_rounds: Tuple[int, ...] = (1, 2, 3, 6)   # §5.2: P1–P4 after 6, 12, 18, 36 feedback episodes
    test_renderings_per_case: int = 3      # §5.1: 3 renderings per case (or direction)
    perceptual_test_renderings: int = 3    # §5.2 MIRROR/LOOP: 3 renderings in 3 test fonts
    vowel_test_fonts: int = 2              # §5.2 VOWEL: 2 seeded test fonts per form, one rendering each
    control_taught_per_case: int = 13      # §5.5 (0a)/(0a′)
    control_test_asks: int = 20            # §5.5: "asked on 20 others"
    canary_asks: int = 20
    periodic_sleep_every: int = 500        # §2.7: "and after every 500th event" (R16: at an episode boundary only)
    mlc_share: float = 0.30                # §4 A1-MLC: 30 % of L4's relation episodes


PREREG = Params()
SMOKE = Params(teach_rounds=1, naming_reps=1, relation_reps_per_case=1, perceptual_reps=1, control_reps=1,
               l5_rounds=2, probe_after_rounds=(1, 2), test_renderings_per_case=1, perceptual_test_renderings=1,
               vowel_test_fonts=1, control_test_asks=4, canary_asks=4, periodic_sleep_every=200, mlc_share=0.05)

RELATION_TRAINING_FAMILIES = ("AFTER", "BEFORE", "BETWEEN", "OTHER_CASE", "MIRROR", "LOOP", "VOWEL")


class ScheduleError(Exception):
    pass


@dataclass(frozen=True)
class Rendering:
    """One rendering the tape needs. `item_id` is the §2.4 rng purpose key — UNIQUE per occurrence."""
    item_id: str
    script: str
    char: str
    font: str


@dataclass
class WorldInputs:
    teach_fonts: List[str]                       # the 4 TEACH fonts, his order (fonts.TEACH_FONTS_ORDER)
    test_fonts: Dict[str, List[str]]             # per script: latin-upper / latin-lower / digits
    pools: Dict[str, Any]                        # never_taught.select_pools' output: u2, u6_refusal, u5_after_never_taught, plant
    plant_fonts: List[str]                       # the plant's fonts: [TEACH font] + >= 10 test fonts
    other_case_excluded: List[str] = field(default_factory=list)   # stage −1's removals (letter names)


@dataclass
class Schedule:
    seed: int
    rows: List[Dict[str, Any]]                   # abstract tape rows: {seq, kind, phase, item, payload} (ids, not cache rows)
    truth_asks: List[Dict[str, Any]]             # one record per ASK (main tape + MLC), R20's "ask" type
    renderings: List[Rendering]                  # first-use order; ids unique
    mlc_rows: List[Dict[str, Any]]               # R19: {mlc_seq, after_seq, episode, kind, phase, item, payload}
    sleep_seqs: List[int]
    counts: Dict[str, Any]
    notes: Dict[str, Any]


def op_row_id(item_id: str) -> Dict[str, Any]:
    """An operand carrying a RENDERING ID; `tape.py` turns `value` into the cache row (an int)."""
    return {"kind": "row", "value": str(item_id)}


def op_name(name: str) -> Dict[str, Any]:
    return {"kind": "name", "value": str(name)}


def char_of(name: str, case: str) -> str:
    if case == "latin-upper":
        return name.upper()
    if case == "latin-lower":
        return name
    raise ScheduleError(f"char_of: unknown case {case!r}")


def other_case(case: str) -> str:
    return "latin-lower" if case == "latin-upper" else "latin-upper"


def _form_of(script: str, char: str) -> Tuple[str, str]:
    return (script, char)


class _Builder:
    def __init__(self, seed: int, w: WorldInputs, params: Params) -> None:
        self.seed = int(seed)
        self.w = w
        self.p = params
        self._check_inputs()
        self.rows: List[Dict[str, Any]] = []
        self.truth_asks: List[Dict[str, Any]] = []
        self.renderings: "OrderedDict[str, Rendering]" = OrderedDict()
        self._tag_counts: Counter = Counter()
        self._sheets: Dict[Tuple[str, str, str], List[str]] = {}
        self.sleep_seqs: List[int] = []
        self._since_sleep = 0
        self._in_sitting: Optional[str] = None
        self._font_assign: Dict[Tuple[str, str], List[str]] = {}
        self.counts: Dict[str, Any] = {"kinds": Counter(), "asks": Counter(), "episodes": Counter(), "sittings": Counter()}
        self.notes: Dict[str, Any] = {}
        self._l4_relation_feedback_seqs: List[int] = []
        self.mlc_rows: List[Dict[str, Any]] = []
        # the family splits, once
        self.ab = families.after_before(self.seed)
        self.between = families.between(self.seed)
        self.two_after = families.two_after(self.seed)
        self.oc = families.other_case(self.seed)
        self.chain = families.chain(after_before_result=self.ab)
        self.transfer = families.transfer()
        self.mirror = families.mirror_symmetric(self.seed)
        self.loop = families.has_loop(self.seed)
        self.vowel = families.vowel(self.seed)
        excluded = set(self.w.other_case_excluded)
        self.oc_held = [nm for nm in self.oc["held_out"] if nm not in excluded]
        self.oc_taught = [nm for nm in self.oc["taught"] if nm not in excluded]
        # the controls' taught letters (R13): one seeded choice each, both cases taught
        self.same_letters = self._choose_names("control:same:letters", self.p.control_taught_per_case)
        self.const_letters = self._choose_names("control:const:letters", self.p.control_taught_per_case)

    # ------------------------------------------------------------------------------------------ helpers
    def _check_inputs(self) -> None:
        w = self.w
        if len(w.teach_fonts) != 4:
            raise ScheduleError(f"teach_fonts must be the 4 TEACH fonts (§2.2), got {len(w.teach_fonts)}")
        for script in ("latin-upper", "latin-lower", "digits"):
            if len(w.test_fonts.get(script, [])) < self.p.test_renderings_per_case:
                raise ScheduleError(f"test_fonts[{script!r}] needs >= {self.p.test_renderings_per_case} fonts, got {len(w.test_fonts.get(script, []))}")
        need = {"u2": 40, "u6_refusal": 10, "u5_after_never_taught": 10}
        for key, n in need.items():
            got = len(w.pools.get(key, []))
            if got < n:
                raise ScheduleError(f"never-taught pool {key!r} has {got} signs, the PREREG needs {n} (§3.3) — RAISED, never padded")
        plant = w.pools.get("plant")
        if not plant or not all(k in plant for k in ("script", "char")):
            raise ScheduleError("pools['plant'] must carry script and char")
        if len(w.plant_fonts) < 11:
            raise ScheduleError(f"plant_fonts needs the TEACH font + 10 test fonts (§3.3), got {len(w.plant_fonts)}")

    def _rng(self, purpose: str) -> np.random.Generator:
        return substream(self.seed, purpose)

    def _choose_names(self, purpose: str, n: int) -> List[str]:
        rng = self._rng(purpose)
        idx = sorted(int(i) for i in rng.choice(len(families.LETTER_NAMES), size=n, replace=False))
        return [families.LETTER_NAMES[i] for i in idx]

    def _render(self, tag: str, script: str, char: str, font: str) -> str:
        n = self._tag_counts[tag]
        self._tag_counts[tag] += 1
        item_id = f"{tag}#{n}:{script}:{char}:{font}"
        if item_id in self.renderings:
            raise ScheduleError(f"duplicate rendering id {item_id!r}")
        self.renderings[item_id] = Rendering(item_id=item_id, script=script, char=char, font=font)
        return item_id

    def _sheet(self, sitting: str, case: str, font: str) -> List[str]:
        """R11: one rendering per glyph per (sitting, case, font), in his order a..z."""
        key = (sitting, case, font)
        if key not in self._sheets:
            self._sheets[key] = [self._render(f"sheet:{sitting}:{case}:{font}", case, char_of(nm, case), font)
                                 for nm in families.LETTER_NAMES]
        return self._sheets[key]

    def _assign_fonts(self, key: str, script: str, n: int) -> List[str]:
        """The seeded test-font assignment of one test item (§2.8), cached so KEEPS at T_D and the probes
        P1–P4 re-use the SAME fonts (§2.2, R14)."""
        k = (key, script)
        if k not in self._font_assign:
            fonts = list(self.w.test_fonts[script])
            if n > len(fonts):
                raise ScheduleError(f"{key}: needs {n} distinct test fonts of {script}, only {len(fonts)} exist")
            rng = self._rng(f"fonts:{key}:{script}")
            idx = [int(i) for i in rng.choice(len(fonts), size=n, replace=False)]
            self._font_assign[k] = [fonts[i] for i in idx]
        return self._font_assign[k]

    def _emit(self, kind: str, phase: str, item: str, payload: Dict[str, Any]) -> int:
        seq = len(self.rows) + 1
        self.rows.append({"seq": seq, "kind": kind, "phase": phase, "item": item, "payload": payload})
        self.counts["kinds"][kind] += 1
        if kind != "SLEEP":
            self._since_sleep += 1
        return seq

    def _sleep(self, phase: str, why: str) -> None:
        if self._in_sitting is not None:
            raise ScheduleError(f"a SLEEP inside sitting {self._in_sitting!r} ({why}) — R16 forbids it")
        seq = self._emit("SLEEP", phase, "-", {"steps": SLEEP_STEPS, "why": why})
        self.sleep_seqs.append(seq)
        self._since_sleep = 0

    def _boundary(self, phase: str) -> None:
        """R16: the periodic sleep, only at an episode boundary outside any sitting."""
        if self._in_sitting is None and self._since_sleep >= self.p.periodic_sleep_every:
            self._sleep(phase, f"periodic ({self.p.periodic_sleep_every} rows)")

    def _teach(self, phase: str, tag: str, script: str, char: str, font: str, name: str) -> Tuple[int, str]:
        iid = self._render(tag, script, char, font)
        seq = self._emit("TEACH", phase, f"TEACH:{name}:{script}", {"glance_row": iid, "name": name})
        return seq, iid

    def _ask(self, phase: str, family: str, item: str, cues: Sequence[str], operands: List[Dict[str, Any]],
             candidate_rows: Optional[List[str]], answer_kind: str, answer: Any, split: str, *,
             klass: str = "", pair: Any = None, rendering: Optional[List[str]] = None, font: Any = None,
             extra: Optional[Dict[str, Any]] = None) -> int:
        payload = {"cues": list(cues), "operands": list(operands), "candidate_rows": (list(candidate_rows) if candidate_rows else None),
                   "answer_kind": answer_kind}
        seq = self._emit("ASK", phase, item, payload)
        sitting = self._in_sitting or phase
        rec = {"type": "ask", "seq": seq, "item": item, "family": family, "class": klass, "answer": answer,
               "pair": pair, "rendering": list(rendering or []), "font": font, "split": split, "sitting": sitting,
               "answer_kind": answer_kind}
        if extra:
            rec.update(extra)
        self.truth_asks.append(rec)
        self.counts["asks"][f"{sitting}:{family}"] += 1
        return seq

    def _feedback(self, phase: str, item: str, ask_seq: int, right: Any) -> int:
        return self._emit("FEEDBACK", phase, item, {"ask_seq": ask_seq, "right": right})

    def _episode(self, phase: str, family: str, item: str, cues, operands, candidate_rows, answer_kind, answer, **kw) -> int:
        ask_seq = self._ask(phase, family, item, cues, operands, candidate_rows, answer_kind, answer, "taught", **kw)
        fb_seq = self._feedback(phase, item, ask_seq, answer)
        self.counts["episodes"][f"{phase}:{family}"] += 1
        self._boundary(phase)
        return fb_seq

    def _begin(self, phase: str, sitting: str, extra: Optional[Dict[str, Any]] = None) -> int:
        if self._in_sitting is not None:
            raise ScheduleError(f"sitting {sitting!r} opened inside {self._in_sitting!r}")
        self._in_sitting = sitting
        payload = {"sitting": sitting}
        if extra:
            payload.update(extra)
        seq = self._emit("TEST_BEGIN", phase, "-", payload)
        self.counts["sittings"][sitting] += 1
        return seq

    def _end(self, phase: str, sitting: str, boundary: bool = True) -> None:
        assert self._in_sitting == sitting
        self._emit("TEST_END", phase, "-", {"sitting": sitting})
        self._in_sitting = None
        if boundary:
            self._boundary(phase)

    def _point_candidates(self, sheet: List[str], name: str, rng: np.random.Generator) -> Tuple[List[str], int]:
        """R11: the target + 3 seeded distractors of the same case, in a seeded order → (rows, right index)."""
        target = families.LETTER_NAMES.index(name)
        others = [i for i in range(26) if i != target]
        picks = [others[int(i)] for i in rng.choice(len(others), size=POINT_SHEET_SIZE - 1, replace=False)]
        order = [target] + picks
        perm = [int(i) for i in rng.permutation(POINT_SHEET_SIZE)]
        order = [order[i] for i in perm]
        return [sheet[i] for i in order], order.index(target)

    # ------------------------------------------------------------------------------------------ phase L
    def phase_L1_L2_L3(self) -> None:
        for phase, case, chars in (("L1", "latin-upper", UPPER), ("L2", "latin-lower", LOWER)):
            for r in range(self.p.teach_rounds):
                font = self.w.teach_fonts[r % len(self.w.teach_fonts)]
                for ch in chars:
                    self._teach(phase, f"{phase}:r{r:02d}", case, ch, font, families.LETTER_NAMES[UPPER.index(ch.upper())])
                    self._boundary(phase)
            self._sleep(phase, f"after {phase}")
        plant = self.w.pools["plant"]
        seq, iid = self._teach("L3", "L3:plant", plant["script"], plant["char"], self.w.plant_fonts[0], PLANT_NAME)
        self.notes["plant"] = {"script": plant["script"], "char": plant["char"], "teach_font": self.w.plant_fonts[0],
                               "test_fonts": list(self.w.plant_fonts[1:11]), "teach_seq": seq, "teach_item_id": iid}

    def _l4_episode_list(self) -> List[Tuple]:
        eps: List[Tuple] = []
        for case in CASES:
            for nm in families.LETTER_NAMES:
                for rep in range(self.p.naming_reps):
                    eps.append(("NAME", case, nm, rep))
                    eps.append(("POINT", case, nm, rep))
                    eps.append(("IS", case, nm, True, rep))
                    eps.append(("IS", case, nm, False, rep))
            for rep in range(self.p.relation_reps_per_case):
                for a, b in self.ab["taught"]:
                    eps.append(("AFTER", case, (a, b), rep))
                for b, a in self.ab["before_taught"]:
                    eps.append(("BEFORE", case, (b, a), rep))
                for a, b, c in self.between["taught"]:
                    eps.append(("BETWEEN", case, (a, b, c), rep))
                for nm in self.oc_taught:
                    eps.append(("OTHER_CASE", case, nm, rep))   # `case` = the direction's FROM case (R10)
                for nm in self.same_letters:
                    eps.append(("SAME", case, nm, rep))
            # edit: Claude (Opus 5.5), 2026-09-27 15:06 +0400 — R47 (B1.1): CONST's training asks join L4's interleave exactly as SAME's
            # (13 letters per case, `control_reps` times — the counts L6 had). As its own L6 block they were the last 78
            # corrections before T_L and T_D, all «a», and every network answered «a» to every T_L letter (R46 addendum).
            for rep in range(self.p.control_reps):
                for nm in self.const_letters:
                    eps.append(("CONST", case, nm, rep))
        for fam, spec in (("MIRROR", self.mirror), ("LOOP", self.loop)):
            forms = list(spec["taught"]["positive"]) + list(spec["taught"]["negative"])
            positives = set(spec["positive_forms"])
            for form in forms:
                for rep in range(self.p.perceptual_reps):
                    eps.append((fam, form, form in positives, rep))
        vowels = set(self.vowel["vowel_forms"])
        for form in families.FORMS_52:
            for rep in range(self.p.perceptual_reps):
                eps.append(("VOWEL", form, form in vowels, rep))
        return eps

    def phase_L4(self) -> None:
        eps = self._l4_episode_list()
        rng = self._rng("L4:interleave")
        order = [int(i) for i in rng.permutation(len(eps))]
        font_rng = {fam: self._rng(f"L4:fonts:{fam}") for fam in ("NAME", "POINT", "IS", "AFTER", "BEFORE", "BETWEEN", "OTHER_CASE", "SAME", "CONST", "MIRROR", "LOOP", "VOWEL")}
        pick_rng = self._rng("L4:POINT:candidates")
        lure_rng = self._rng("L4:IS:lures")
        tf = self.w.teach_fonts

        def draw_font(fam: str) -> str:
            return tf[int(font_rng[fam].integers(0, len(tf)))]

        for i in order:
            ep = eps[i]
            fam = ep[0]
            if fam == "NAME":
                _f, case, nm, rep = ep
                font = draw_font(fam)
                iid = self._render("L4:NAME", case, char_of(nm, case), font)
                self._episode("L4", fam, f"NAME:{nm}:{case}", ["NAME"], [op_row_id(iid)], None, "NAME", nm,
                              klass=case, rendering=[iid], font=font)
            elif fam == "POINT":
                _f, case, nm, rep = ep
                font = draw_font(fam)
                sheet = self._sheet("L4", case, font)
                cands, right = self._point_candidates(sheet, nm, pick_rng)
                self._episode("L4", fam, f"POINT:{nm}:{case}", ["POINT"], [op_name(nm)], cands, "PICK", right,
                              klass=case, rendering=cands, font=font)
            elif fam == "IS":
                _f, case, nm, positive, rep = ep
                font = draw_font(fam)
                if positive:
                    y = nm
                else:
                    others = [n2 for n2 in families.LETTER_NAMES if n2 != nm]
                    y = others[int(lure_rng.integers(0, len(others)))]
                iid = self._render("L4:IS", case, char_of(y, case), font)
                self._episode("L4", fam, f"IS:{nm}:{'pos' if positive else 'lure'}:{case}", ["IS"],
                              [op_name(nm), op_row_id(iid)], None, "YESNO", "YES" if positive else "NO",
                              klass=f"{case}:{'positive' if positive else 'lure'}", pair=(nm, y), rendering=[iid], font=font)
            elif fam in ("AFTER", "BEFORE"):
                _f, case, (x, y), rep = ep
                font = draw_font(fam)
                iid = self._render(f"L4:{fam}", case, char_of(x, case), font)
                fb = self._episode("L4", fam, f"{fam}:{x}>{y}", [fam], [op_row_id(iid)], None, "NAME", y,
                                   klass=case, pair=(x, y), rendering=[iid], font=font)
                self._l4_relation_feedback_seqs.append(fb)
            elif fam == "BETWEEN":
                _f, case, (a, b, c), rep = ep
                font = draw_font(fam)
                ia = self._render("L4:BETWEEN", case, char_of(a, case), font)
                ic = self._render("L4:BETWEEN", case, char_of(c, case), font)
                fb = self._episode("L4", fam, f"BETWEEN:{a},{c}>{b}", ["BETWEEN"], [op_row_id(ia), op_row_id(ic)], None, "NAME", b,
                                   klass=case, pair=(a, b, c), rendering=[ia, ic], font=font)
                self._l4_relation_feedback_seqs.append(fb)
            elif fam == "OTHER_CASE":
                _f, case_from, nm, rep = ep
                font = draw_font(fam)
                iid = self._render("L4:OTHER_CASE", case_from, char_of(nm, case_from), font)
                sheet_font = draw_font(fam)
                sheet = self._sheet("L4", other_case(case_from), sheet_font)
                right = families.LETTER_NAMES.index(nm)
                fb = self._episode("L4", fam, f"OTHER_CASE:{nm}", ["OTHER_CASE"], [op_row_id(iid)], sheet, "PICK", right,
                                   klass=f"{case_from}->{other_case(case_from)}", pair=(nm,), rendering=[iid], font=[font, sheet_font])
                self._l4_relation_feedback_seqs.append(fb)
            elif fam == "SAME":
                _f, case, nm, rep = ep
                font = draw_font(fam)
                iid = self._render("L4:SAME", case, char_of(nm, case), font)
                self._episode("L4", fam, f"SAME:{nm}:{case}", ["SAME"], [op_row_id(iid)], None, "NAME", nm,
                              klass=case, rendering=[iid], font=font)
            elif fam == "CONST":                                  # R47 (B1.1): L6's episode, now inside L4
                _f, case, nm, rep = ep
                font = draw_font(fam)
                iid = self._render("L4:CONST", case, char_of(nm, case), font)
                self._episode("L4", fam, f"CONST:{nm}:{case}", ["CONST"], [op_row_id(iid)], None, "NAME", "a",
                              klass=case, rendering=[iid], font=font)
            elif fam in ("MIRROR", "LOOP", "VOWEL"):
                _f, (script, ch), positive, rep = ep
                font = draw_font(fam)
                iid = self._render(f"L4:{fam}", script, ch, font)
                fb = self._episode("L4", fam, f"{fam}:{script}:{ch}", [fam], [op_row_id(iid)], None, "YESNO",
                                   "YES" if positive else "NO", klass=script, pair=(script, ch), rendering=[iid], font=font)
                self._l4_relation_feedback_seqs.append(fb)
            else:  # pragma: no cover
                raise ScheduleError(f"unknown L4 episode {ep!r}")
        self._sleep("L4", "after L4")

    def _probe(self, phase: str, sitting: str) -> None:
        self._begin(phase, sitting)
        self._two_after_test_items(phase, sitting)
        self._end(phase, sitting)

    def _two_after_test_items(self, phase: str, sitting: str) -> None:
        for a, c in self.two_after["held_out"]:
            key = f"TWO_AFTER:{a}>{c}"
            for case in CASES:
                for font in self._assign_fonts(key, case, self.p.test_renderings_per_case):
                    iid = self._render(f"{sitting}:TWO_AFTER", case, char_of(a, case), font)
                    self._ask(phase, "TWO_AFTER", key, ["TWO_AFTER"], [op_row_id(iid)], None, "NAME", c, "held_out",
                              klass=case, pair=(a, c), rendering=[iid], font=font)

    def phase_L5(self) -> None:
        taught = self.two_after["taught"]
        rng = self._rng("L5:rounds")
        font_rng = self._rng("L5:fonts")
        tf = self.w.teach_fonts
        probe_k = 0
        for r in range(1, self.p.l5_rounds + 1):
            eps = [(pair, case) for pair in taught for case in CASES]
            order = [int(i) for i in rng.permutation(len(eps))]
            for i in order:
                (a, c), case = eps[i]
                font = tf[int(font_rng.integers(0, len(tf)))]
                iid = self._render("L5:TWO_AFTER", case, char_of(a, case), font)
                self._episode("L5", "TWO_AFTER", f"TWO_AFTER:{a}>{c}", ["TWO_AFTER"], [op_row_id(iid)], None, "NAME", c,
                              klass=case, pair=(a, c), rendering=[iid], font=font)
            self._sleep("L5", f"after L5 round {r}")          # R2 / R14
            if r in self.p.probe_after_rounds:
                probe_k += 1
                self._probe("L5", f"P{probe_k}")

    # ------------------------------------------------------------------------------------------ the sittings
    def _letter_items(self, phase: str, sitting: str) -> None:
        """U1 (a), and every letter U3 family — the block T_L asks and T_D re-asks (KEEPS) with NEW renderings
        in the SAME fonts (§2.2, §5.4)."""
        # U1 (a): NAME on every (letter, test font) of each case
        for case in CASES:
            for nm in families.LETTER_NAMES:
                for font in self.w.test_fonts[case]:
                    iid = self._render(f"{sitting}:U1a", case, char_of(nm, case), font)
                    self._ask(phase, "U1a_NAME", f"NAME:{nm}:{case}:{font}", ["NAME"], [op_row_id(iid)], None, "NAME", nm, "test",
                              klass=case, rendering=[iid], font=font)
        # U3 REACH: AFTER / BEFORE / BETWEEN (held out)
        for a, b in self.ab["held_out"]:
            key = f"AFTER:{a}>{b}"
            for case in CASES:
                for font in self._assign_fonts(key, case, self.p.test_renderings_per_case):
                    iid = self._render(f"{sitting}:AFTER", case, char_of(a, case), font)
                    self._ask(phase, "AFTER", key, ["AFTER"], [op_row_id(iid)], None, "NAME", b, "held_out",
                              klass=case, pair=(a, b), rendering=[iid], font=font)
        for b, a in self.ab["before_held_out"]:
            key = f"BEFORE:{b}>{a}"
            for case in CASES:
                for font in self._assign_fonts(key, case, self.p.test_renderings_per_case):
                    iid = self._render(f"{sitting}:BEFORE", case, char_of(b, case), font)
                    self._ask(phase, "BEFORE", key, ["BEFORE"], [op_row_id(iid)], None, "NAME", a, "held_out",
                              klass=case, pair=(b, a), rendering=[iid], font=font)
        for a, b, c in self.between["held_out"]:
            key = f"BETWEEN:{a},{c}>{b}"
            for case in CASES:
                for font in self._assign_fonts(key, case, self.p.test_renderings_per_case):
                    ia = self._render(f"{sitting}:BETWEEN", case, char_of(a, case), font)
                    ic = self._render(f"{sitting}:BETWEEN", case, char_of(c, case), font)
                    self._ask(phase, "BETWEEN", key, ["BETWEEN"], [op_row_id(ia), op_row_id(ic)], None, "NAME", b, "held_out",
                              klass=case, pair=(a, b, c), rendering=[ia, ic], font=font)
        # U3 NEW CUE
        self._two_after_test_items(phase, sitting)
        # U3 OTHER_CASE (held out, minus stage −1's removals — R17) and CHAIN (all 25 pairs)
        sheet_rng = self._rng(f"{sitting}:sheet-fonts")   # per sitting: the sheet font of each PICK item
        for nm in self.oc_held:
            key = f"OTHER_CASE:{nm}"
            for case_from in CASES:
                to = other_case(case_from)
                for font in self._assign_fonts(key, case_from, self.p.test_renderings_per_case):
                    iid = self._render(f"{sitting}:OTHER_CASE", case_from, char_of(nm, case_from), font)
                    sheet_font = self._assign_fonts(f"{key}:sheet:{font}", to, 1)[0]
                    sheet = self._sheet(sitting, to, sheet_font)
                    self._ask(phase, "OTHER_CASE", key, ["OTHER_CASE"], [op_row_id(iid)], sheet, "PICK",
                              families.LETTER_NAMES.index(nm), "held_out", klass=f"{case_from}->{to}", pair=(nm,),
                              rendering=[iid], font=[font, sheet_font])
        taught_after = set(self.ab["taught"])
        for a, b in self.chain["items"]:
            key = f"CHAIN:{a}>{b}"
            for case_from in CASES:
                to = other_case(case_from)
                for font in self._assign_fonts(key, case_from, self.p.test_renderings_per_case):
                    iid = self._render(f"{sitting}:CHAIN", case_from, char_of(a, case_from), font)
                    sheet_font = self._assign_fonts(f"{key}:sheet:{font}", to, 1)[0]
                    sheet = self._sheet(sitting, to, sheet_font)
                    self._ask(phase, "CHAIN", key, ["AFTER", "OTHER_CASE"], [op_row_id(iid)], sheet, "PICK",
                              families.LETTER_NAMES.index(b), "held_out", klass=f"{case_from}->{to}", pair=(a, b),
                              rendering=[iid], font=[font, sheet_font],
                              extra={"after_was": "taught" if (a, b) in taught_after else "held_out"})
        del sheet_rng
        # U3 perceptual: MIRROR / LOOP (held-out forms, 3 renderings in 3 test fonts), VOWEL (20 forms x 2 fonts)
        for fam, spec in (("MIRROR", self.mirror), ("LOOP", self.loop)):
            positives = set(spec["positive_forms"])
            forms = list(spec["held_out"]["positive"]) + list(spec["held_out"]["negative"])
            for script, ch in forms:
                key = f"{fam}:{script}:{ch}"
                for font in self._assign_fonts(key, script, self.p.perceptual_test_renderings):
                    iid = self._render(f"{sitting}:{fam}", script, ch, font)
                    self._ask(phase, fam, key, [fam], [op_row_id(iid)], None, "YESNO",
                              "YES" if (script, ch) in positives else "NO", "held_out", klass=script, pair=(script, ch),
                              rendering=[iid], font=font)
        vowels = set(self.vowel["vowel_forms"])
        for script, ch in list(self.vowel["vowel_forms"]) + list(self.vowel["consonant_forms"]):
            key = f"VOWEL:{script}:{ch}"
            for font in self._assign_fonts(key, script, self.p.vowel_test_fonts):
                iid = self._render(f"{sitting}:VOWEL", script, ch, font)
                self._ask(phase, "VOWEL", f"{key}:{font}", ["VOWEL"], [op_row_id(iid)], None, "YESNO",
                          "YES" if (script, ch) in vowels else "NO", "test", klass=script, pair=(script, ch),
                          rendering=[iid], font=font)

    def sitting_T_L(self) -> None:
        phase, sitting = "T_L", "T_L"
        canary_purpose = CANARY_PURPOSE_TEMPLATE.format(sitting=sitting)
        begin = self._begin(phase, sitting, {"canary_purpose": canary_purpose})
        self.notes["T_L_begin_seq"] = begin
        self.notes["u6_gap_events"] = begin - self.notes["plant"]["teach_seq"]
        self._letter_items(phase, sitting)
        # U1 (b): PICK the glyph for a heard name among 4 of the same case in one test font — 52 items
        rng = self._rng("T_L:U1b")
        for case in CASES:
            fonts = self.w.test_fonts[case]
            for nm in families.LETTER_NAMES:
                font = fonts[int(rng.integers(0, len(fonts)))]
                sheet = self._sheet(sitting, case, font)
                cands, right = self._point_candidates(sheet, nm, rng)
                self._ask(phase, "U1b_PICK", f"POINT:{nm}:{case}", ["POINT"], [op_name(nm)], cands, "PICK", right, "test",
                          klass=case, rendering=cands, font=font)
        # U2 (a): 40 never-taught signs
        for cand in self.w.pools["u2"][:40]:
            iid = self._render("T_L:U2a", cand["script"], cand["char"], cand["font"])
            self._ask(phase, "U2a_NEVER_TAUGHT", f"NAME:nt:{cand['script']}:{cand['char']}", ["NAME"], [op_row_id(iid)], None, "NAME",
                      REFUSE, "never_taught", klass=cand["script"], rendering=[iid], font=cand["font"])
        # U2 (b): 52 positives + 52 lures, «is this X?»
        rng = self._rng("T_L:U2b")
        for case in CASES:
            fonts = self.w.test_fonts[case]
            for nm in families.LETTER_NAMES:
                font = fonts[int(rng.integers(0, len(fonts)))]
                iid = self._render("T_L:U2b", case, char_of(nm, case), font)
                self._ask(phase, "U2b_LURES", f"IS:{nm}:pos:{case}", ["IS"], [op_name(nm), op_row_id(iid)], None, "YESNO", "YES", "test",
                          klass=f"{case}:positive", pair=(nm, nm), rendering=[iid], font=font)
                others = [n2 for n2 in families.LETTER_NAMES if n2 != nm]
                y = others[int(rng.integers(0, len(others)))]
                font2 = fonts[int(rng.integers(0, len(fonts)))]
                iid2 = self._render("T_L:U2b", case, char_of(y, case), font2)
                self._ask(phase, "U2b_LURES", f"IS:{nm}:lure:{case}", ["IS"], [op_name(nm), op_row_id(iid2)], None, "YESNO", "NO", "test",
                          klass=f"{case}:lure", pair=(nm, y), rendering=[iid2], font=font2)
        # U5: misuse (the letters' kinds; OTHER_CASE of a digit is at T_D)
        rng = self._rng("T_L:U5")

        def tfont(case: str) -> str:
            fonts = self.w.test_fonts[case]
            return fonts[int(rng.integers(0, len(fonts)))]

        for case in CASES:
            f = tfont(case); iid = self._render("T_L:U5", case, char_of("z", case), f)
            self._ask(phase, "U5", "AFTER:z", ["AFTER"], [op_row_id(iid)], None, "NAME", REFUSE, "misuse", klass="after_z", rendering=[iid], font=f)
            f = tfont(case); iid = self._render("T_L:U5", case, char_of("a", case), f)
            self._ask(phase, "U5", "BEFORE:a", ["BEFORE"], [op_row_id(iid)], None, "NAME", REFUSE, "misuse", klass="before_a", rendering=[iid], font=f)
            for nm in ("y", "z"):
                f = tfont(case); iid = self._render("T_L:U5", case, char_of(nm, case), f)
                self._ask(phase, "U5", f"TWO_AFTER:{nm}", ["TWO_AFTER"], [op_row_id(iid)], None, "NAME", REFUSE, "misuse", klass="two_after_yz", rendering=[iid], font=f)
            for a, b in families.AFTER_PAIRS:
                f = tfont(case)
                ia = self._render("T_L:U5", case, char_of(a, case), f)
                ib = self._render("T_L:U5", case, char_of(b, case), f)
                self._ask(phase, "U5", f"BETWEEN:{a},{b}", ["BETWEEN"], [op_row_id(ia), op_row_id(ib)], None, "NAME", REFUSE, "misuse",
                          klass="between_adjacent", pair=(a, b), rendering=[ia, ib], font=f)
        for cand in self.w.pools["u5_after_never_taught"][:10]:
            iid = self._render("T_L:U5", cand["script"], cand["char"], cand["font"])
            self._ask(phase, "U5", f"AFTER:nt:{cand['script']}:{cand['char']}", ["AFTER"], [op_row_id(iid)], None, "NAME", REFUSE, "misuse",
                      klass="after_never_taught", rendering=[iid], font=cand["font"])
        # U6: the plant on 10 held-out renderings (10 other fonts), and 10 unrelated never-taught signs
        plant = self.notes["plant"]
        for font in plant["test_fonts"]:
            iid = self._render("T_L:U6", plant["script"], plant["char"], font)
            self._ask(phase, "U6_PLANT", f"NAME:{PLANT_NAME}:{font}", ["NAME"], [op_row_id(iid)], None, "NAME", PLANT_NAME, "held_out",
                      klass=plant["script"], rendering=[iid], font=font)
        for cand in self.w.pools["u6_refusal"][:10]:
            iid = self._render("T_L:U6", cand["script"], cand["char"], cand["font"])
            self._ask(phase, "U6_REFUSAL", f"NAME:nt:{cand['script']}:{cand['char']}", ["NAME"], [op_row_id(iid)], None, "NAME", REFUSE,
                      "never_taught", klass=cand["script"], rendering=[iid], font=cand["font"])
        # controls (0a) CONST, (0a′) SAME + its NAME reference, (0d) CANARY — R13 / R15
        tf = self.w.teach_fonts
        for fam, taught, answer_of in (("CONTROL_CONST", self.const_letters, lambda nm: "a"),
                                       ("CONTROL_SAME", self.same_letters, lambda nm: nm)):
            rng = self._rng(f"T_L:{fam}")
            untaught = [(case, nm) for case in CASES for nm in families.LETTER_NAMES if nm not in set(taught)]
            picks = [untaught[int(i)] for i in rng.choice(len(untaught), size=self.p.control_test_asks, replace=False)]
            cue = "CONST" if fam == "CONTROL_CONST" else "SAME"
            for case, nm in picks:
                font = tf[int(rng.integers(0, len(tf)))]
                iid = self._render(f"T_L:{fam}", case, char_of(nm, case), font)
                self._ask(phase, fam, f"{cue}:{nm}:{case}", [cue], [op_row_id(iid)], None, "NAME", answer_of(nm), "control",
                          klass=case, rendering=[iid], font=font)
                if fam == "CONTROL_SAME":
                    self._ask(phase, "SAME_NAME_REF", f"NAME:{nm}:{case}:same-ref", ["NAME"], [op_row_id(iid)], None, "NAME", nm, "control",
                              klass=case, rendering=[iid], font=font)
        rng = self._rng("T_L:CANARY:items")
        canary = self._rng(canary_purpose)
        for i in range(self.p.canary_asks):
            case = CASES[int(rng.integers(0, 2))]
            nm = families.LETTER_NAMES[int(rng.integers(0, 26))]
            font = tf[int(rng.integers(0, len(tf)))]
            iid = self._render("T_L:CANARY", case, char_of(nm, case), font)
            right = families.LETTER_NAMES[int(canary.integers(0, 26))]
            self._ask(phase, "CONTROL_CANARY", f"CANARY:{i}", ["CANARY"], [op_row_id(iid)], None, "NAME", right, "control",
                      klass=case, pair=(nm, right), rendering=[iid], font=font, extra={"canary_purpose": canary_purpose})
        self._end(phase, sitting)

    def phase_D(self) -> None:
        self._emit("ARRIVAL", "D", "digits", {"what": "digits"})
        for r in range(self.p.teach_rounds):
            font = self.w.teach_fonts[r % len(self.w.teach_fonts)]
            for ch in DIGIT_CHARS:
                self._teach("D", f"D:r{r:02d}", "digits", ch, font, digit_name(ch))
                self._boundary("D")
        self._sleep("D", "after D")

    def sitting_T_D(self) -> None:
        phase, sitting = "T_D", "T_D"
        self._begin(phase, sitting, {"canary_purpose": CANARY_PURPOSE_TEMPLATE.format(sitting=sitting)})
        # TRANSFER: AFTER and BEFORE on the digits' own order, 3 renderings each in the digits' test fonts
        for cue, items in (("AFTER", self.transfer["after"]), ("BEFORE", self.transfer["before"])):
            for x, y in items:
                key = f"TRANSFER_{cue}:{x}>{y}"
                for font in self._assign_fonts(key, "digits", self.p.test_renderings_per_case):
                    iid = self._render(f"T_D:TRANSFER", "digits", DIGIT_CHARS[DIGIT_NAMES.index(x)], font)
                    self._ask(phase, "TRANSFER", key, [cue], [op_row_id(iid)], None, "NAME", y, "test",
                              klass=cue, pair=(x, y), rendering=[iid], font=font)
        # U5: OTHER_CASE of a digit (R18): a PICK whose sheet is T_D's lower-case sheet in a seeded lower test font
        rng = self._rng("T_D:U5")
        for d in DIGIT_NAMES:
            dfonts = self.w.test_fonts["digits"]
            font = dfonts[int(rng.integers(0, len(dfonts)))]
            iid = self._render("T_D:U5", "digits", DIGIT_CHARS[DIGIT_NAMES.index(d)], font)
            lfonts = self.w.test_fonts["latin-lower"]
            sheet_font = lfonts[int(rng.integers(0, len(lfonts)))]
            sheet = self._sheet(sitting, "latin-lower", sheet_font)
            self._ask(phase, "U5", f"OTHER_CASE:{d}", ["OTHER_CASE"], [op_row_id(iid)], sheet, "PICK", REFUSE, "misuse",
                      klass="other_case_digit", pair=(d,), rendering=[iid], font=[font, sheet_font])
        # KEEPS: T_L's letter items again — NEW renderings, the SAME fonts (the assignment cache)
        self._letter_items(phase, sitting)
        self._end(phase, sitting, boundary=False)   # the tape ends here: no periodic sleep after the last sitting

    # ------------------------------------------------------------------------------------------ MLC (R19)
    def build_mlc(self) -> None:
        anchors_all = sorted(self._l4_relation_feedback_seqs)
        n_rel = len(anchors_all)
        n_ep = int(round(self.p.mlc_share * n_rel))
        rng = self._rng("mlc:anchors")
        anchors = sorted(anchors_all[int(i)] for i in rng.choice(n_rel, size=n_ep, replace=False))
        rule_rng = self._rng("mlc:rules")
        item_rng = self._rng("mlc:items")
        font_rng = self._rng("mlc:fonts")
        tf = self.w.teach_fonts
        mlc_seq = 0
        rules: List[Dict[str, Any]] = []
        for e, anchor in enumerate(anchors):
            if int(rule_rng.integers(0, 2)) == 0:
                k = int(MLC_SHIFTS[int(rule_rng.integers(0, len(MLC_SHIFTS)))])
                perm = [(i + k) % 26 for i in range(26)]
                rule = {"kind": "shift", "k": k}
            else:
                perm = self._mlc_permutation(rule_rng)
                rule = {"kind": "permutation"}
            slot = e % MLC_SLOTS
            cue = f"MLC{slot}"
            case = CASES[int(item_rng.integers(0, 2))]
            xs = [int(i) for i in item_rng.choice(26, size=MLC_K + MLC_Q, replace=False)]
            rules.append({"episode": e, "after_seq": anchor, "slot": slot, "rule": rule, "case": case,
                          "study": [families.LETTER_NAMES[i] for i in xs[:MLC_K]], "query": [families.LETTER_NAMES[i] for i in xs[MLC_K:]]})
            for j, xi in enumerate(xs):
                x = families.LETTER_NAMES[xi]
                y = families.LETTER_NAMES[perm[xi]]
                font = tf[int(font_rng.integers(0, len(tf)))]
                iid = self._render("MLC", case, char_of(x, case), font)
                role = "study" if j < MLC_K else "query"
                mlc_seq += 1
                ask_seq = mlc_seq
                self.mlc_rows.append({"mlc_seq": ask_seq, "after_seq": anchor, "episode": e, "kind": "ASK", "phase": "L4",
                                      "item": f"MLC:{e}:{role}:{x}",
                                      "payload": {"cues": [cue], "operands": [op_row_id(iid)], "candidate_rows": None, "answer_kind": "NAME"}})
                mlc_seq += 1
                self.mlc_rows.append({"mlc_seq": mlc_seq, "after_seq": anchor, "episode": e, "kind": "FEEDBACK", "phase": "L4",
                                      "item": f"MLC:{e}:{role}:{x}", "payload": {"ask_seq": ask_seq, "right": y}})
                self.truth_asks.append({"type": "ask", "seq": ask_seq, "mlc": True, "item": f"MLC:{e}:{role}:{x}", "family": "MLC",
                                        "class": f"{rule['kind']}:{role}", "answer": y, "pair": (x, y), "rendering": [iid], "font": font,
                                        "split": "mlc", "sitting": "MLC", "answer_kind": "NAME", "after_seq": anchor, "episode": e})
        self.counts["mlc"] = {"episodes": n_ep, "relation_episodes_in_L4": n_rel, "rows": len(self.mlc_rows),
                              "share": self.p.mlc_share, "shift": sum(1 for r in rules if r["rule"]["kind"] == "shift"),
                              "permutation": sum(1 for r in rules if r["rule"]["kind"] == "permutation")}
        self.notes["mlc_rules"] = rules

    def _mlc_permutation(self, rng: np.random.Generator, max_tries: int = 20000) -> List[int]:
        """R19: a permutation of the 26 letter indices with NO x -> x, x±1, x±2 (so no order-family pair,
        taught or held out, in either direction). Rejection sampling; the expected acceptance is ≈ e^-5."""
        for _ in range(max_tries):
            perm = [int(i) for i in rng.permutation(26)]
            if all(abs(perm[i] - i) not in MLC_FORBIDDEN_DIFFS for i in range(26)):
                return perm
        raise ScheduleError("could not draw an MLC permutation with no x->x±{0,1,2} in 20,000 tries")

    # ------------------------------------------------------------------------------------------ the whole
    def build(self) -> Schedule:
        self.phase_L1_L2_L3()
        self.phase_L4()
        self.phase_L5()
        self.sitting_T_L()          # R47 (B1.1): no L6 — CONST is taught inside L4
        self.phase_D()
        self.sitting_T_D()
        self.build_mlc()
        if self._in_sitting is not None:  # pragma: no cover
            raise ScheduleError("a sitting was left open")
        self.counts["kinds"] = dict(self.counts["kinds"])
        self.counts["asks"] = dict(self.counts["asks"])
        self.counts["episodes"] = dict(self.counts["episodes"])
        self.counts["sittings"] = dict(self.counts["sittings"])
        self.counts["rows"] = len(self.rows)
        self.counts["renderings"] = len(self.renderings)
        self.counts["sleeps"] = len(self.sleep_seqs)
        self.counts["sheets"] = {f"{s}:{c}:{f}": len(v) for (s, c, f), v in self._sheets.items()}
        self.notes["sleep_seqs"] = list(self.sleep_seqs)
        self.notes["sleep_steps"] = SLEEP_STEPS
        self.notes["font_assignment"] = {f"{k[0]}|{k[1]}": v for k, v in self._font_assign.items()}
        self.notes["controls"] = {"same_letters": self.same_letters, "const_letters": self.const_letters}
        self.notes["other_case"] = {"held_out_graded": self.oc_held, "taught": self.oc_taught, "excluded": list(self.w.other_case_excluded)}
        self.notes["splits"] = {"after_before": self.ab, "between": self.between, "two_after": self.two_after,
                                "other_case": self.oc, "mirror": self.mirror, "loop": self.loop, "vowel": self.vowel}
        return Schedule(seed=self.seed, rows=self.rows, truth_asks=self.truth_asks, renderings=list(self.renderings.values()),
                        mlc_rows=self.mlc_rows, sleep_seqs=self.sleep_seqs, counts=self.counts, notes=self.notes)


def build(seed: int, world: WorldInputs, params: Params = PREREG) -> Schedule:
    """The one entry point. Pure: the same (seed, world, params) → the identical Schedule, in any process.
    Every graded tape is built with `params=PREREG` (the default); `SMOKE` is for the materialiser's tests."""
    sch = _Builder(seed, world, params).build()
    sch.notes["params"] = dict(params.__dict__)
    sch.notes["params_are_prereg"] = (params == PREREG)
    return sch


def expected_counts(n_other_case_held: int = 13, n_other_case_taught: int = 13, n_test_fonts_upper: int = 15,
                    n_test_fonts_lower: int = 12, p: Params = PREREG) -> Dict[str, Any]:
    """§2.7 / §5.2 / §5.3 / §5.5, recomputed from the counts above — what `test_schedule.py` pins the built
    schedule against (the PREREG's own test: "a unit test recomputes them from the counts above")."""
    teach = 26 * p.teach_rounds * 2 + 1 + 10 * p.teach_rounds
    l4 = {"NAME": 52 * p.naming_reps, "POINT": 52 * p.naming_reps, "IS": 104 * p.naming_reps,
          "AFTER": 13 * 2 * p.relation_reps_per_case, "BEFORE": 13 * 2 * p.relation_reps_per_case,
          "BETWEEN": 12 * 2 * p.relation_reps_per_case, "OTHER_CASE": n_other_case_taught * 2 * p.relation_reps_per_case,
          "MIRROR": (17 - 8 + 35 - 8) * p.perceptual_reps, "LOOP": (15 - 7 + 37 - 7) * p.perceptual_reps,
          "VOWEL": 52 * p.perceptual_reps, "SAME": p.control_taught_per_case * 2 * p.control_reps,
          "CONST": p.control_taught_per_case * 2 * p.control_reps}      # R47 (B1.1): CONST inside L4

    l5_episodes = 3 * 2 * p.l5_rounds
    l6_episodes = 0                                                   # R47 (B1.1): L6 is gone
    two_after_test = 21 * 2 * p.test_renderings_per_case
    letter_block = {"U1a_NAME": 26 * (n_test_fonts_upper + n_test_fonts_lower),
                    "AFTER": 12 * 2 * p.test_renderings_per_case, "BEFORE": 12 * 2 * p.test_renderings_per_case,
                    "BETWEEN": 12 * 2 * p.test_renderings_per_case, "TWO_AFTER": two_after_test,
                    "OTHER_CASE": n_other_case_held * 2 * p.test_renderings_per_case, "CHAIN": 25 * 2 * p.test_renderings_per_case,
                    "MIRROR": 16 * p.perceptual_test_renderings, "LOOP": 14 * p.perceptual_test_renderings, "VOWEL": 20 * p.vowel_test_fonts}
    t_l_only = {"U1b_PICK": 52, "U2a_NEVER_TAUGHT": 40, "U2b_LURES": 104, "U5": 2 + 2 + 4 + 50 + 10,
                "U6_PLANT": 10, "U6_REFUSAL": 10, "CONTROL_CONST": p.control_test_asks, "CONTROL_SAME": p.control_test_asks,
                "SAME_NAME_REF": p.control_test_asks, "CONTROL_CANARY": p.canary_asks}
    t_d_only = {"TRANSFER": 18 * p.test_renderings_per_case, "U5": 10}
    n_rel = sum(l4[f] for f in RELATION_TRAINING_FAMILIES)
    return {"TEACH": teach, "L4_episodes": l4, "L4_episodes_total": sum(l4.values()), "L5_episodes": l5_episodes,
            "L6_episodes": l6_episodes, "probe_asks_each": two_after_test, "letter_block": letter_block,
            "T_L_only": t_l_only, "T_D_only": t_d_only,
            "ASK": (sum(l4.values()) + l5_episodes + l6_episodes + len(p.probe_after_rounds) * two_after_test
                    + 2 * sum(letter_block.values()) + sum(t_l_only.values()) + sum(t_d_only.values())),
            "FEEDBACK": sum(l4.values()) + l5_episodes + l6_episodes,
            "ARRIVAL": 1, "TEST_BEGIN": 2 + len(p.probe_after_rounds), "TEST_END": 2 + len(p.probe_after_rounds),
            "mlc_episodes": int(round(p.mlc_share * n_rel)), "mlc_relation_episodes": n_rel}
