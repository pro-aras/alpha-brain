# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:06 +0400 — a REHEARSAL of arm D at B1's scale, on the creature's own front
# (real latin-upper and latin-lower glyphs in the 4 TEACH fonts, pasted and glanced by brain/world/build.py's one
# road under /usr/bin/python3). NOT B1's tape (Builder 2's world writes that): a stand-in with B1-PREREG §2.7's
# L1 + L2 + L4 COUNTS and the world's own family splits (brain/world/families.py), under a seed that is none of
# B1's (so no B1 split is read here), used for two things only: arm D's seconds-per-candidate sample (report §5)
# and a pre-flight of its search at realistic example counts (#239: a pre-flight on the road finds what suites
# do not). Operand shapes are this rehearsal's guesses (BETWEEN: two glyph operands; OTHER_CASE: a 26-glyph sheet
# of the other case in one font; POINT: a 4-glyph sheet of one case) — D keys its programs by the shape it is
# shown, so a different shape on B1's tape changes nothing in D.
#
#   cache (once, ~10 min under load):  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -m tests.brain.arms_library.rehearsal cache
#   tape:                              ... /data/dev/venvs/brain/bin/python -m tests.brain.arms_library.rehearsal tape
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REH_DIR = Path("/data/dev/brain-runs/tmp/b1-library-rehearsal")
REH_SEED = 777001            # none of B1's seeds (20261001, 20261002, 20260930)
TEACH_FONTS = ["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf", "UbuntuSans[wdth,wght].ttf", "cmr10.ttf"]
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER = "abcdefghijklmnopqrstuvwxyz"
K_TEACH = 3                  # renderings 0..2 per (form, font): TEACH only
K_ASK = 5                    # renderings 3..7 per (form, font): asks and sheets only (never a TEACH percept)
SHUFFLE_SHEETS = True        # False reproduces the first run's alphabetical OTHER_CASE sheets (report §4 R14)


def forms() -> List[Tuple[str, str]]:
    return [("latin-upper", c) for c in UPPER] + [("latin-lower", c) for c in LOWER]


def cache():
    from brain.world.build import RenderRequest, build_cache
    reqs = []
    for script, ch in forms():
        for f in TEACH_FONTS:
            for k in range(K_TEACH + K_ASK):
                reqs.append(RenderRequest(item_id=f"reh:{script}:{ch}:{f}:{k}", script=script, char=ch, font=f))
    REH_DIR.mkdir(parents=True, exist_ok=True)
    item_to_row, _h, _t = build_cache(reqs, REH_DIR / "cache", REH_SEED)
    (REH_DIR / "rows.json").write_text(json.dumps(item_to_row, sort_keys=True))
    print(f"rehearsal cache: {len(item_to_row)} rows")


def tape(l4_fraction: float = 1.0) -> Path:
    from brain.protocol import canonical_json, make_row, op_name, op_row
    from brain.world import families as fam
    from brain.world.seeds import substream
    rows = json.loads((REH_DIR / "rows.json").read_text())
    rng = substream(REH_SEED, "rehearsal:tape")

    def r(script, ch, font_i, k):
        return rows[f"reh:{script}:{ch}:{TEACH_FONTS[font_i % 4]}:{k}"]

    ask_k = {}

    def ask_row_of(script, ch, font_i=None):
        """A fresh-ish ask rendering: cycle through k = 3..7 per (form, font)."""
        fi = int(rng.integers(0, 4)) if font_i is None else font_i
        key = (script, ch, fi)
        n = ask_k.get(key, 0)
        ask_k[key] = n + 1
        return r(script, ch, fi, K_TEACH + (n % K_ASK))

    out: List[dict] = []
    seq = 1

    def add(kind, payload, phase, item="x"):
        nonlocal seq
        out.append(make_row(seq, kind, phase, item, payload))
        seq += 1
        if kind != "SLEEP" and len(out) % 500 == 499:
            out.append(make_row(seq, "SLEEP", phase, "-", {"steps": 0}))
            seq += 1

    # L1, L2: 12 rounds, the font cycling, 3 showings per font (renderings 0..2)
    for script, letters in (("latin-upper", UPPER), ("latin-lower", LOWER)):
        for rnd in range(12):
            for ch in letters:
                add("TEACH", {"glance_row": r(script, ch, rnd, rnd // 4), "name": ch.lower()}, "L1" if script.endswith("upper") else "L2")
        add("SLEEP", {"steps": 0}, "L")
    # L4: training episodes, interleaved in a seeded order
    eps = []
    for script, ch in forms():
        for _ in range(3):
            eps.append(("NAME", script, ch))
    for ch in LOWER:
        for _ in range(3):
            eps.append(("POINT", "latin-upper" if rng.random() < 0.5 else "latin-lower", ch))
    for script, ch in forms():
        for _ in range(3):
            eps.append(("IS+", script, ch))
            eps.append(("IS-", script, ch))
    ab = fam.after_before(REH_SEED)
    for a, b in ab["taught"]:
        for _ in range(3):
            for script in ("latin-upper", "latin-lower"):
                eps.append(("AFTER", script, (a, b)))
                eps.append(("BEFORE", script, (b, a)))
    for a, b, c in fam.between(REH_SEED)["taught"]:
        for _ in range(3):
            for script in ("latin-upper", "latin-lower"):
                eps.append(("BETWEEN", script, (a, b, c)))
    for x in fam.other_case(REH_SEED)["taught"]:
        for _ in range(3):
            for script in ("latin-upper", "latin-lower"):
                eps.append(("OTHER_CASE", script, x))
    same = [c for i, c in enumerate(LOWER) if i % 2 == 0]
    for x in same:
        for _ in range(3):
            for script in ("latin-upper", "latin-lower"):
                eps.append(("SAME", script, x))
    for fname, fobj in (("MIRROR", fam.mirror_symmetric(REH_SEED)), ("LOOP", fam.has_loop(REH_SEED))):
        for pol in ("positive", "negative"):
            for script, ch in fobj["taught"][pol]:
                for _ in range(6):
                    eps.append((fname, script, (ch, pol == "positive")))
    vowels = set("aeiou")
    for script, ch in forms():
        for _ in range(6):
            eps.append(("VOWEL", script, (ch, ch.lower() in vowels)))
    order = rng.permutation(len(eps))
    n_take = int(len(eps) * l4_fraction)
    for idx in order[:n_take]:
        kind, script, obj = eps[int(idx)]
        case_letters = UPPER if script == "latin-upper" else LOWER
        cv = (lambda nm: nm.upper()) if script == "latin-upper" else (lambda nm: nm)
        s = seq
        if kind == "NAME":
            add("ASK", {"cues": ["NAME"], "operands": [op_row(ask_row_of(script, obj))], "candidate_rows": None,
                        "answer_kind": "NAME"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": obj.lower()}, "L4")
        elif kind == "SAME":
            add("ASK", {"cues": ["SAME"], "operands": [op_row(ask_row_of(script, cv(obj)))], "candidate_rows": None,
                        "answer_kind": "NAME"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": obj}, "L4")
        elif kind == "POINT":
            fi = int(rng.integers(0, 4))
            others = [c for c in case_letters if c != cv(obj)]
            pick = [others[int(i)] for i in rng.choice(len(others), size=3, replace=False)]
            sheet_chars = pick + [cv(obj)]
            perm = rng.permutation(4)
            sheet_chars = [sheet_chars[int(i)] for i in perm]
            sheet = [ask_row_of(script, c, fi) for c in sheet_chars]
            add("ASK", {"cues": ["POINT"], "operands": [op_name(obj)], "candidate_rows": sheet, "answer_kind": "PICK"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": sheet_chars.index(cv(obj))}, "L4")
        elif kind in ("IS+", "IS-"):
            heard = obj.lower() if kind == "IS+" else LOWER[(LOWER.index(obj.lower()) + 1 + int(rng.integers(0, 25))) % 26]
            add("ASK", {"cues": ["IS"], "operands": [op_row(ask_row_of(script, obj)), op_name(heard)],
                        "candidate_rows": None, "answer_kind": "YESNO"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": "YES" if heard == obj.lower() else "NO"}, "L4")
        elif kind in ("AFTER", "BEFORE"):
            x, y = obj
            add("ASK", {"cues": [kind], "operands": [op_row(ask_row_of(script, cv(x)))], "candidate_rows": None,
                        "answer_kind": "NAME"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": y}, "L4")
        elif kind == "BETWEEN":
            a, b, c = obj
            add("ASK", {"cues": ["BETWEEN"], "operands": [op_row(ask_row_of(script, cv(a))), op_row(ask_row_of(script, cv(c)))],
                        "candidate_rows": None, "answer_kind": "NAME"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": b}, "L4")
        elif kind == "OTHER_CASE":
            other_script = "latin-lower" if script == "latin-upper" else "latin-upper"
            other_letters = LOWER if other_script == "latin-lower" else UPPER
            fi = int(rng.integers(0, 4))
            # the sheet's ORDER is shuffled per ask: an alphabetical sheet lets the answer be read off its
            # POSITION (index_of(order, name)) without comparing a single shape — found by this rehearsal's first
            # run (report §4 R14) and kept as tape-alphabetical-sheets.jsonl beside this one
            sheet_chars = [other_letters[int(i)] for i in rng.permutation(26)] if SHUFFLE_SHEETS else list(other_letters)
            sheet = [ask_row_of(other_script, c, fi) for c in sheet_chars]
            add("ASK", {"cues": ["OTHER_CASE"], "operands": [op_row(ask_row_of(script, cv(obj)))], "candidate_rows": sheet,
                        "answer_kind": "PICK"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": [c.lower() for c in sheet_chars].index(obj)}, "L4")
        else:   # MIRROR, LOOP, VOWEL
            ch, yes = obj
            add("ASK", {"cues": [kind], "operands": [op_row(ask_row_of(script, ch))], "candidate_rows": None,
                        "answer_kind": "YESNO"}, "L4")
            add("FEEDBACK", {"ask_seq": s, "right": "YES" if yes else "NO"}, "L4")
    add("SLEEP", {"steps": 0}, "L4")
    path = REH_DIR / "tape.jsonl"
    path.write_text("".join(canonical_json(x) + "\n" for x in out))
    kinds = {}
    for x in out:
        k = x["kind"] if x["kind"] != "ASK" else "ASK:" + "+".join(x["payload"]["cues"])
        kinds[k] = kinds.get(k, 0) + 1
    print(json.dumps({"rows": len(out), "kinds": kinds}, sort_keys=True))
    return path


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "tape"
    if what == "cache":
        cache()
    else:
        tape(float(sys.argv[2]) if len(sys.argv) > 2 else 1.0)
