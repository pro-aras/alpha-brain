# edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:38 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §2, builder C's OWN
# reading of it — builder B writes the real sense from the same section; the seat tests the seam between the two). A helper module
# (leading underscore: no tests of its own).
"""A small scene-world tape for the mind's brain tests: `n_train` training scenes of `brain/scene/world.py` (ear rows in the
parent's order, then the eye row), then ONE sitting: a `begin` ask; per split and per scene row with ≥ 1 question, the ask rows
then the eye row (moment `sc<ws>q-<set>-<split>-<r:04d>`); one canvas-less `why` ask per word the parent said in training; an
`end` ask. The questions are the offline generators' own (brain/scene/marks.py); a `box` is `[top, left, side]` and a box ask
carries the thing's ink `centroid` (the seat's addendum 2). Every row gets an explicit `at` (a fixed day, +1 ms a row) so a tape
never splits across two day files and two writes are byte-identical. Truth files under root/truth/scene/ (the mind never reads them)."""
from __future__ import annotations

import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PIL import Image

from brain.scene import marks as M
from brain.scene import world as W
from creature.tape import Tape

ROOT = Path(__file__).resolve().parents[2]
ALPHA4 = ROOT / "genome" / "ALPHA4.genome"
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; "
              "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene")
WS = 20261101
T0 = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)


def scene_line(ws: int = WS, train: int = 60) -> str:
    return f"WORLD    scene seed {ws}; train {train}; sitting fresh; feed max backlog 8; utterance true"


def genome_text(brain: bool = True, train: int = 60) -> str:
    """ALPHA4.genome + the BRAIN line (+ the WORLD scene line once creature/genes.py wires WORLD_SCENE — builder B's row; until
    then the line would refuse at `unwired()`, and the mind never reads it)."""
    from creature import genes
    text = ALPHA4.read_text()
    lines = [BRAIN_LINE] if brain else []
    if genes.RUNS.get("body", {}).get("WORLD_SCENE") or genes.RUNS.get("mind", {}).get("WORLD_SCENE"):
        lines.append(scene_line(train=train))
    return text + "\n" + "\n".join(lines) + "\n"


def write_genome(path: Path, brain: bool = True, train: int = 60) -> Path:
    path.write_text(genome_text(brain=brain, train=train))
    return path


def png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(b, format="PNG")
    return b.getvalue()


class _Clock:
    def __init__(self, t0: datetime = T0) -> None:
        self.k = 0
        self.t0 = t0

    def __call__(self) -> str:
        t = self.t0 + timedelta(milliseconds=self.k)
        self.k += 1
        return t.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _box(thing: Dict[str, object]) -> List[int]:
    return [int(thing["top"]), int(thing["left"]), int(thing["side"])]


def _truth(root: Path, seq: int, obj: Dict[str, object]) -> None:
    d = root / "truth" / "scene"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{seq:09d}.json").write_text(json.dumps(obj))


def _ask(tape: Tape, clock: _Clock, moment: str, payload: Dict[str, object], meta_extra: Dict[str, object]) -> Dict[str, object]:
    return tape.publish("ask", json.dumps(payload).encode(), {"moment": moment, "source": "scene", **meta_extra}, "json", at=clock())


def build(root: Path, ws: int = WS, n_train: int = 60, sitting_set: str = "fresh", per_split: int = 2,
          t0: datetime = T0, one_day: bool = True) -> Dict[str, object]:
    """Write the tape under root/tape (+ truth). Returns {"tape": day file, "asks": n, "eyes": n, "said": [words, first-heard]}.
    `t0`/`one_day` False: a tape that crosses 00:00 UTC (two day files) for the replay-directory test."""
    tape = Tape(root)
    clock = _Clock(t0)
    said: List[str] = []
    n_asks = n_eyes = 0
    for i in range(n_train):
        scene = W.train_scene(ws, i)
        rgb = W.render_scene(scene)[0]
        moment = f"sc{ws}t{i:06d}"
        for w in scene.words:
            tape.publish("ear", w.encode(), {"moment": moment, "source": "scene", "word": w, "scene": i}, "txt", at=clock())
            if w not in said:
                said.append(w)
        row = tape.publish("eye", png(rgb), {"moment": moment, "source": "scene", "kind": "train", "scene": i, "world_seed": ws},
                           "png", at=clock())
        n_eyes += 1
        _truth(root, int(row["seq"]), {"kind": "train", "scene": i, "world_seed": ws, "scene_dict": scene.to_dict(), "said": list(scene.words)})

    ts = W.TEST_SETS[sitting_set][ws]
    _ask(tape, clock, f"sc{ws}q-{sitting_set}-begin", {"form": "begin", "set": sitting_set, "test_seed": ts}, {"form": "begin"})
    n_asks += 1

    def rows_of(split: str, n: int) -> List[Dict[str, object]]:
        return [{**s.to_dict(), "row": r} for r, s in enumerate(W.scenes_for(split, ts, limit=n))]

    test_rows = rows_of("test", 6)
    items_by_split: Dict[str, List[Dict[str, object]]] = {"test": [], "m2b": [], "m6": [], "m3": [], "speak": [], "decline": [], "speak2": []}
    for it in M.m1_items(test_rows, ts)[:per_split]:
        items_by_split["test"].append({**it, "form": "point"})
    for it in M.m2a_items(test_rows, ts)[:per_split]:
        items_by_split["test"].append({**it, "form": "point"})
    for row in test_rows:
        if len(row["things"]) == 1:
            items_by_split["test"].append({"item_id": f"NAME:{row['item_id']}", "mark": "NAME", "row": int(row["row"]), "phrase": [],
                                           "target": 0, "form": "what"})
            break
    truth = {"test": test_rows}
    for split, maker, form in (("m2b", M.m2b_items, "what"), ("m6", M.m6_items, "point"), ("m3", M.m3_items, "point"),
                               ("speak", M.speak_items, "say"), ("decline", M.decline_items, "say"), ("speak2", M.speak2_items, "say")):
        rows = rows_of(split, per_split if split != "speak2" else 1)
        truth[split] = rows
        for it in maker(rows):
            items_by_split[split].append({**it, "form": form})

    for split, items in items_by_split.items():
        rows = truth[split]
        by_row: Dict[int, List[Dict[str, object]]] = {}
        for it in items:
            by_row.setdefault(int(it["row"]), []).append(it)
        for r in sorted(by_row):
            srow = rows[r]
            scene_obj = W.scenes_for(split, ts, limit=r + 1)[r]
            rgb, cents = W.render_scene(scene_obj)
            moment = f"sc{ws}q-{sitting_set}-{split}-{r:04d}"
            for it in by_row[r]:
                box = centroid = None
                if it["form"] in ("what", "say"):
                    tgt = int(it["target"])
                    box = _box(srow["things"][tgt])
                    centroid = [float(cents[tgt][0]), float(cents[tgt][1])]
                payload = {"item": it["item_id"], "mark": it["mark"], "form": it["form"], "phrase": list(it.get("phrase") or []),
                           "box": box, "word": None, "test_seed": ts}
                if box is not None:
                    payload["centroid"] = centroid
                _ask(tape, clock, moment, payload, {"item": it["item_id"], "form": it["form"]})
                n_asks += 1
            row = tape.publish("eye", png(rgb), {"moment": moment, "source": "scene", "kind": "sitting", "set": sitting_set,
                                                 "split": split, "row": r}, "png", at=clock())
            n_eyes += 1
            _truth(root, int(row["seq"]), {"kind": "sitting", "set": sitting_set, "split": split, "row": r,
                                           "scene_dict": scene_obj.to_dict(), "items": [it["item_id"] for it in by_row[r]]})
    for k, w in enumerate(said):
        _ask(tape, clock, f"sc{ws}q-{sitting_set}-why-{k:04d}", {"form": "why", "item": f"M4:{w}", "mark": "M4", "word": w},
             {"item": f"M4:{w}", "form": "why"})
        n_asks += 1
    _ask(tape, clock, f"sc{ws}q-{sitting_set}-end", {"form": "end", "set": sitting_set}, {"form": "end"})
    n_asks += 1
    days = sorted((root / "tape").glob("*.jsonl"))
    assert (len(days) == 1) if one_day else (len(days) > 1), days
    return {"tape": days[0], "days": days, "asks": n_asks, "eyes": n_eyes, "said": said, "n_train": n_train}


def link_root(tape_root: Path, run_root: Path) -> Path:
    """A fresh mind root whose tape/ is the fixture's (the mind reads payloads only; never writes the tape)."""
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "tape").symlink_to((tape_root / "tape").resolve(), target_is_directory=True)
    return run_root


def rows(tape_root: Path) -> List[Dict[str, object]]:
    from creature.tape import read_tape
    return list(read_tape(tape_root))


def journal(root: Path) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        out.extend(json.loads(line) for line in f.read_text().splitlines() if line.strip())
    return out


def journal_bytes(root: Path) -> bytes:
    return b"".join(f.read_bytes() for f in sorted((root / "journal").glob("*.jsonl")))


def is_brain_row(r: Dict[str, object]) -> bool:
    return r.get("kind") in ("answer", "brain")


# ------------------------------------------------------------------------------------------------ the test double
class FakeBrain:
    """A small DETERMINISTIC stand-in with genome/brain.py's API (INTERFACE §3), until builder A's organ lands: it counts words,
    keeps one row per scene learned (moment, scene, the first located fixation, a digest of glance 0), calibrates at the
    declared counts, answers every form in §2's shapes with a `raw`, saves/loads to <base>.npz + <base>.json."""

    def __init__(self, cfg: Dict[str, object], *, mouth_incremental: bool = False):
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 — PREREG-ALPHA-6 §1.3: the organ's interface grew by the
        # mouth_incremental construction parameter (the «world=» growth's own form, #248 (3)): a stand-in takes it and
        # keeps it, so a test can read what the mind declared. Caught RED by the creature split's 8 TypeErrors.
        self.cfg = dict(cfg)
        self._mouth_incremental = bool(mouth_incremental)
        self.counts: Dict[str, int] = {}
        self.rows: List[Dict[str, object]] = []
        self.calibrations = 0
        self.since = 0

    def hears(self, source) -> bool:
        return source in list(self.cfg["hears"])

    def _digest(self, glance) -> float:
        return round(float(np.asarray(glance["feats"][0], dtype=np.float64).sum()), 9)

    def learn(self, glance, words, *, moment, scene, world_seed, world=None) -> Dict[str, object]:
        # edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1: the organ's interface grew by `world=` (a stand-in is a consumer, #248 (3))
        fix = [list(map(int, f)) for f in glance["fix"]]
        if len(glance["feats"]) != len(fix) + 1:
            raise AssertionError(f"FakeBrain: expected the coarse glance beside {len(fix)} located, got {len(glance['feats'])}")
        for w in words:
            self.counts[w] = self.counts.get(w, 0) + 1
        self.rows.append({"moment": moment, "scene": int(scene), "words": list(words), "fix0": fix[0] if fix else None,
                          "d": self._digest(glance), **({"world": str(world)} if world not in (None, "scene") else {})})
        self.since += 1
        calibrated = len(self.rows) in list(self.cfg["calibrate_at"])
        if calibrated:
            self.calibrate()
        return {"n_hyp": len(fix), "words": list(words), "attributed": {w: 0 for w in words}, "none": None, "calibrated": calibrated}

    def calibrate(self) -> Dict[str, object]:
        self.calibrations += 1
        self.since = 0
        return {"calibrations": self.calibrations}

    def ask(self, payload, glance) -> Dict[str, object]:
        form = payload["form"]
        if form == "begin":
            did = self.since > 0
            if did:
                self.calibrate()
            return {"kind": "begun", "calibrated": did, "raw": {"calibrated": did}}
        if form == "end":
            return {"kind": "end", "raw": {"kind": "end"}}
        if form == "why":
            w = payload["word"]
            if self.counts.get(w, 0) < int(self.cfg["young"]):
                return {"kind": "unknown", "raw": {"kind": "unknown"}}
            eps = [{"moment": r["moment"], "scene": r["scene"], "pos": r["fix0"]} for r in self.rows if w in r["words"]][:8]
            a = {"kind": "because", "word": w, "episodes": eps, "rule": {"over": [e["moment"] for e in eps], "band": float("inf")}}
            return {**a, "raw": dict(a)}
        fix = [list(map(int, f)) for f in glance["fix"]]
        if form == "point":
            unheard = [w for w in payload["phrase"] if w not in self.counts]
            if unheard:
                return {"kind": "unheard", "words": unheard, "raw": {"point": None, "none": None, "unheard": unheard}}
            k = int(round(self._digest(glance) * 1000)) % max(1, len(fix))
            return {"kind": "thing", "hyp": 0, "pos": [float(fix[k][0]), float(fix[k][1])], "fix": [fix[k]],
                    "raw": {"point": 0, "none": False, "none_i": False, "score": np.float64(0.5)}}
        best = sorted(self.counts.items(), key=lambda kv: (-kv[1], kv[0]))[:1]
        words = [w for w, _n in best]
        if form == "what":
            return {"kind": "words", "words": words, "raw": {"emit": words}}
        return {"kind": "phrase", "words": words, "raw": {"spoken": words, "reason": None, "target": 0, "readback_point": None}}

    def summary(self) -> Dict[str, object]:
        return {"scenes": len(self.rows), "words": len(self.counts), "calibrations": self.calibrations}

    # edit: Claude (Fable 5.1, the seat), 2026-09-29 21:38 +0400 — PREREG-METADATA-1: the organ's interface grew by `census()` (the mind writes it at
    # every calibration and at close). The stand-in answers in the organ's own shape: everything it holds it lived.
    def census(self) -> Dict[str, object]:
        n = len(self.rows)
        return {"scenes": n, "scenes_by_source": ({"lived": n} if n else {}), "n_words": len(self.counts),
                "words": {w: {"meetings": int(c), "episodes_by_source": {"lived": int(c)}, "mature": True, "kind": None}
                          for w, c in sorted(self.counts.items())},
                "given_only_words": [], "calibrations": self.calibrations, "runs": []}

    def _state(self) -> Dict[str, object]:
        return {"counts": self.counts, "rows": self.rows, "calibrations": self.calibrations, "since": self.since}

    def state_hash(self) -> str:
        import hashlib
        return hashlib.sha256(json.dumps(self._state(), sort_keys=True).encode()).hexdigest()

    def save(self, base) -> None:
        base = Path(base)
        np.savez(str(base) + ".npz", n=np.asarray([len(self.rows)]))
        Path(str(base) + ".json").write_text(json.dumps(self._state(), sort_keys=True))

    @classmethod
    def load(cls, base, cfg, *, mouth_incremental: bool = False) -> "FakeBrain":
        b = cls(cfg, mouth_incremental=mouth_incremental)
        st = json.loads(Path(str(base) + ".json").read_text())
        b.counts, b.rows, b.calibrations, b.since = st["counts"], st["rows"], st["calibrations"], st["since"]
        return b
