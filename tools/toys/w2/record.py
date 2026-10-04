"""tools/toys/w2/record.py — PREREG-W2 §3: the closed record's readers and the scene-canvas assembly.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:4x +0400 — new file, written after tests/tools/test_w2_record.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 (the bench reads the CLOSED record: the tape, the journal, the
truth specs, the saved census, and the brain STORE's real rows — the copies under the bench's scratch, RULES §7, never a
life's root).

assemble(bl2, lo, hi): the scene canvases lo..hi of the closed brain's own record, in learn order — each with its moment,
seq, scene index, the parent's words in tape order, the fixation cells, the journal's hyp groups, the turn and learn rows,
the truth spec, and the store's real (H, 146) rows (the brain's own `seen`, decoded with the organism's own _Decoder at
genome/brain.py:744-837, read-only). regenerate_spec(world_seed, scene): the truth spec rebuilt from (world_seed, scene) by
the world's own generator and renderer — G-TRUTH's comparison form (the W1 bench's, verbatim in kind).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np

from genome.brain import _Decoder
from brain.scene import world as W
from creature.senses import mentor as M
from creature.senses import scene as SC


@dataclass
class SceneCanvas:
    order: int                                   # the canvas's ordinal in the brain's own learn order
    moment: str
    seq: int
    scene: int
    words: List[str]                             # the parent's utterance, tape order
    fix: List[List[int]]
    hyps: List[List[int]]
    turn: Dict[str, object]
    learn: Dict[str, object]
    spec: Dict[str, object]
    things: List[M.Thing]
    X: np.ndarray
    world_seed: int

    def mentor_canvas(self, state: Dict[str, int], say=None, ask_target=None) -> M.Canvas:
        return M.Canvas(moment=self.moment, things=self.things, fix=self.fix, state=state, say=say,
                        ask_target=ask_target, order=self.order)


def iter_jsonl(files: List[Path]) -> Iterator[Dict[str, object]]:
    for f in files:
        with f.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)


def iter_tape_rows(tape_dir: Path) -> Iterator[Dict[str, object]]:
    yield from iter_jsonl(sorted(Path(tape_dir).glob("*.jsonl")))


def iter_journal(journal_dir: Path) -> Iterator[Dict[str, object]]:
    yield from iter_jsonl(sorted(Path(journal_dir).glob("*.jsonl")))


def load_seen(base: Path) -> List[Tuple[np.ndarray, List[str], object]]:
    """The brain store's `seen` — the real (X, words, referent) per learned canvas, decoded by the organism's own decoder."""
    meta = json.loads(Path(str(base) + ".json").read_text(encoding="utf-8"))
    with np.load(str(base) + ".npz") as z:
        arrays = {k: z[k] for k in z.files}
    dec = _Decoder(arrays)
    return [tuple(t) for t in dec.dec(meta["brain"]["seen"])]


def load_spec(truth_dir: Path, seq: int) -> Dict[str, object]:
    return json.loads((Path(truth_dir) / "scene" / f"{seq:09d}.json").read_text(encoding="utf-8"))


def regenerate_spec(world_seed: int, scene: int) -> Dict[str, object]:
    """The truth spec rebuilt by the world's own generator + renderer (G-TRUTH's form): train_scene + render_scene +
    the scene sense's own scene_dict builder, in the truth file's own wrapper keys."""
    sc = W.train_scene(world_seed, scene)
    render = lambda: W.render_scene(sc)                               # noqa: E731 — the memoized getter's own form
    return {"kind": "train", "scene": scene, "world_seed": world_seed,
            "scene_dict": SC._scene_dict_with_centroids(sc, scene, render), "said": list(sc.words)}


def _things_of(spec: Dict[str, object]) -> List[M.Thing]:
    return [M.Thing(shape=t["shape"], colour=t["colour"], size=t["size"], top=int(t["top"]), left=int(t["left"]),
                    side=int(t["side"])) for t in spec["scene_dict"]["things"]]


def assemble(bl2: Path, lo: int, hi: Optional[int], store_base: Optional[Path] = None) -> List[SceneCanvas]:
    """The scene canvases [lo, hi) of the closed brain's record, in learn order. bl2: the sanctioned copy's root
    (tape/, journal/, truth/, census/). store_base: the brain store's <base> (.json/.npz) — default
    /data/dev/swarm/2026-10-03/int/bl2-gen/prev/brain (the integrator's sha-checked copy of brain-long-2's store).
    The journal's own rows carry everything the assembly needs: the learn row's heard words, fix, hyps and seq, the
    moment id's own seed and scene index (`sc<seed>t<index:06d>`)."""
    bl2 = Path(bl2)
    if store_base is None:
        store_base = Path("/data/dev/swarm/2026-10-03/int/bl2-gen/prev/brain")
    turns: Dict[int, Dict[str, object]] = {}
    learns: Dict[int, Dict[str, object]] = {}
    seeds: Dict[int, int] = {}
    for row in iter_journal(bl2 / "journal"):
        if row.get("kind") != "brain":
            continue
        act = row.get("act")
        if act not in ("turn", "learn"):
            continue
        m = str(row.get("moment", ""))
        try:
            ws_s, ix_s = m.lstrip("sc").split("t", 1)
            ws, ix = int(ws_s), int(ix_s)
        except ValueError:
            continue                                        # not a scene-canvas row (another hand; the brain's own)
        if act == "turn":
            turns[ix] = row
        else:
            learns[ix] = row
        seeds[ix] = ws
    hi = len(learns) if hi is None else min(int(hi), len(learns))
    seen = load_seen(store_base)
    out: List[SceneCanvas] = []
    for i in range(int(lo), hi):
        if i not in learns:
            raise KeyError(f"scene {i}: no learn row in the closed journal (the record holds {len(learns)})")
        learn = learns[i]
        turn = turns.get(i)
        if turn is None:
            raise KeyError(f"scene {i}: a learn row without its turn row (the orphan form)")
        ws = seeds[i]
        moment = str(learn["moment"])
        if moment != f"sc{ws}t{i:06d}":
            raise ValueError(f"scene {i}: moment {moment!r} out of the record's own order")
        spec = load_spec(bl2 / "truth", int(learn["seq"]))
        X, _words, _ref = seen[i]
        out.append(SceneCanvas(order=i, moment=moment, seq=int(learn["seq"]), scene=i,
                               words=list(learn["words"]), fix=learn["fix"], hyps=learn["hyps"],
                               turn=turn, learn=learn, spec=spec, things=_things_of(spec), X=X, world_seed=ws))
    return out
