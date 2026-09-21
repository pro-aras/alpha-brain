"""fast.py — FAST: one-shot episodic memory (G4 §3 B3; docs/G4-PREREG.md, row 2c of docs/G4-DESIGN.md
§1: "nearest-neighbour memory", new/minimal).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B3 (docs/briefs/G4-BUILDER-B-GENES.md).

Law of this file: a fixed-capacity RING of (moment, x_s, x_w, word, surprise) rows. `write` never refuses
— at capacity the OLDEST row is overwritten (the ring, never a "least-used" cap — #227's law is SLOW's,
this store forgets by AGE alone, which is what "one-shot, fast, complementary to slow" means: an episode
IS meant to fall off once SLEEP has had its turn to consolidate it, or once it ages out unreplayed).
`nearest`/`most_surprising` read over currently-held rows only (an overwritten id is simply gone — `get`
then returns None, never a stale or wrong record). Cosine similarity assumes x_s vectors are unit length,
exactly as every sight vector in this genome already is (genome/machinery.py's retina()); `nearest` does
NOT re-normalise, so a caller must pass a unit query (a shuffled/foreign query still scores correctly —
"shuffled" here means a DIFFERENT vector, not a differently-scaled one).
"""
from __future__ import annotations

import pathlib as _pl
from typing import Dict, List, Optional, Tuple

import numpy as np


class Episodes:
    """FAST — PREREG §3 B3: `Episodes(cap, dim_s, dim_w)`; `write` (ring, oldest overwritten);
    `nearest(x_s, k)` (nearest-neighbour recall by cosine, ties by id); `most_surprising(n)` (top-n
    live episodes by their own surprise value, descending); `save(path)/load(path)` (npz, atomic via
    tmp+rename). `get(id)` is a small extension beyond the four named methods — a caller (B5's «why»,
    B7's SLEEP) needs the record an id names, not only the id.

    edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — B12 (docs/G4-PREREG.md §11.2,
    TRAITS): `write` gains an optional `x_s2` (default None) — a canvas's SECOND glance, alongside
    `x_s`'s first, so genome/traits.py's InfoNCE has a same-canvas positive pair to train against.
    Stored as `x_s2` (zeros where absent) + `has_s2` (a uint8 mask) so a reader can tell "no second
    glance" from "a second glance that happened to be near zero". Nothing else reads it (`nearest`
    ignores it, per the PREREG); Episodes is never hashed anywhere, so "kept out of the pin" is
    automatic.

    edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-MIND-1 (docs/organs/MIND-MEMORY.md
    §4; docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md): `write` gains four more optional fields — `where`
    (window origin), `when` (the tape's own instant), `act` (the act that produced this glance), `source`
    (which sense delivered the canvas) — plus `glance` (which glance ordinal this row's x_s came from).
    Same convention as `x_s2`: a presence mask for `where` (a real (-1,-1) origin is possible on some
    front, so a sentinel alone is not enough), the empty string as "absent" for the three string fields
    (matching `word`'s own convention), -1 as "absent" for `glance` (matching `moment`/`ids`). New method
    `nearest_where(where, k)` — the mechanism the position-plant test (G-EYE-1/G-MIND-1) answers through:
    a rule that reads ONLY `where`, never x_s, because the plant makes x_s identical across classes by
    construction. Nothing here is read by `nearest`; Episodes stays unhashed."""

    def __init__(self, cap: int, dim_s: int, dim_w: int):
        if cap < 1:
            raise ValueError(f"Episodes: cap must be >= 1, got {cap}")
        self.cap = cap
        self.dim_s = dim_s
        self.dim_w = dim_w
        self.moment = np.full(cap, -1, dtype=np.int64)
        self.ids = np.full(cap, -1, dtype=np.int64)
        self.x_s = np.zeros((cap, dim_s), dtype=np.float64)
        self.x_s2 = np.zeros((cap, dim_s), dtype=np.float64)
        self.has_s2 = np.zeros(cap, dtype=np.uint8)
        self.x_w = np.zeros((cap, dim_w), dtype=np.float64)
        self.word = np.array([""] * cap, dtype="<U32")
        self.surprise = np.zeros(cap, dtype=np.float64)
        # edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-MIND-1 (docs/organs/MIND-MEMORY.md §4): the seam
        # contract's four new fields, BESIDE x_s/x_w, never inside them (his 13:30 word; #228 (c)). Mirrors the x_s2/has_s2
        # pattern (B12): a fixed-dtype column per field + a presence mask for `where` (a (-1,-1) coordinate is a real
        # coordinate the moment the eye's canvas is 2x2 or bigger, so "absent" must be its own bit, not a sentinel value).
        # `when`/`act`/`source` use the empty string as their own "absent" — exactly how `word` already reads "no word yet"
        # for a sight-only episode, so no new convention is invented. `glance` (the ordinal of the glance this row's x_s
        # came from — today always 0, the first glance; BIND/G-EYE-2 may store more than one glance's episode later) uses
        # -1 for absent, matching `moment`/`ids`. Episodes is never hashed (state_hash reads Organism only), so none of
        # this moves gate G4-2's pin — the parity test proves it directly (tests/genome/test_deliver_moment.py).
        self.where_y = np.full(cap, -1, dtype=np.int64)
        self.where_x = np.full(cap, -1, dtype=np.int64)
        self.has_where = np.zeros(cap, dtype=np.uint8)
        self.when = np.array([""] * cap, dtype="<U32")
        self.act = np.array([""] * cap, dtype="<U16")
        self.source = np.array([""] * cap, dtype="<U32")
        self.glance = np.full(cap, -1, dtype=np.int64)
        self.n_written = 0        # episodes ever written (the next write's id)
        self._next_slot = 0       # the ring's next slot to write (== the oldest live slot once full)
        self._id_to_slot: Dict[int, int] = {}

    def __len__(self) -> int:
        return min(self.n_written, self.cap)

    # ------------------------------------------------------------------------------------- write
    def write(self, moment: int, x_s: np.ndarray, x_w: np.ndarray, word: str, surprise: float,
               x_s2: Optional[np.ndarray] = None,
               where: Optional[Tuple[int, int]] = None, when: Optional[str] = None,
               act: Optional[str] = None, source: Optional[str] = None,
               glance: Optional[int] = None) -> int:
        """Writes one episode at the ring's next slot (the oldest, once the ring is full) and returns
        its id (0, 1, 2, … — never reused; an overwritten episode's old id simply stops resolving).
        `x_s2` (B12): the same canvas's second glance, if the caller has one; None (the default) marks
        the slot's `has_s2` False and leaves `x_s2` zeroed there.

        edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-MIND-1: `where` (the glance's
        window origin, (top, left) in pixel space), `when` (the tape row's own wall-clock instant,
        already the ONE clock read on this box — creature/tape.py:now_iso), `act` (the act that produced
        this glance — today always "glance", the only verb the seam declares; MOTOR-HANDS.md's wider
        vocabulary is a later gene), `source` (the eye row's OWN `meta["source"]`, already written by the
        sense that published it — creature/world_maker.py / creature/senses/folder.py — copied here, not
        invented) and `glance` (which glance of the canvas this episode's x_s came from — always 0 today,
        the first glance, since that is all a canvas currently writes to FAST). None of the five ever
        touches x_s/x_w — they are new COLUMNS, read by nothing that computes a cosine."""
        slot = self._next_slot
        old_id = int(self.ids[slot])
        if old_id != -1:
            self._id_to_slot.pop(old_id, None)
        eid = self.n_written
        self.moment[slot] = int(moment)
        self.x_s[slot] = x_s
        if x_s2 is not None:
            self.x_s2[slot] = x_s2
            self.has_s2[slot] = 1
        else:
            self.x_s2[slot] = 0.0
            self.has_s2[slot] = 0
        self.x_w[slot] = x_w
        self.word[slot] = word
        self.surprise[slot] = float(surprise)
        if where is not None:
            self.where_y[slot] = int(where[0]); self.where_x[slot] = int(where[1]); self.has_where[slot] = 1
        else:
            self.where_y[slot] = -1; self.where_x[slot] = -1; self.has_where[slot] = 0
        self.when[slot] = when if when is not None else ""
        self.act[slot] = act if act is not None else ""
        self.source[slot] = source if source is not None else ""
        self.glance[slot] = int(glance) if glance is not None else -1
        self.ids[slot] = eid
        self._id_to_slot[eid] = slot
        self._next_slot = (self._next_slot + 1) % self.cap
        self.n_written += 1
        return eid

    # ------------------------------------------------------------------------------------- read
    def get(self, eid: int) -> Optional[Dict[str, object]]:
        """The episode's own record, or None if it is no longer live (overwritten by the ring). G-MIND-1
        (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400): `where`/`when`/`act`/`source`/
        `glance` read back as None wherever they were never written (an episode written before MOMENT
        was declared, or by a genome that never declares it) — exactly `x_s2`'s own "no second glance"
        convention, so a caller cannot tell "absent" from a real but empty value."""
        slot = self._id_to_slot.get(eid)
        if slot is None:
            return None
        return {"id": eid, "moment": int(self.moment[slot]), "x_s": self.x_s[slot].copy(),
                "x_w": self.x_w[slot].copy(), "word": str(self.word[slot]), "surprise": float(self.surprise[slot]),
                "x_s2": (self.x_s2[slot].copy() if self.has_s2[slot] else None),
                "where": ((int(self.where_y[slot]), int(self.where_x[slot])) if self.has_where[slot] else None),
                "when": (str(self.when[slot]) or None),
                "act": (str(self.act[slot]) or None),
                "source": (str(self.source[slot]) or None),
                "glance": (int(self.glance[slot]) if int(self.glance[slot]) != -1 else None)}

    def nearest(self, x_s: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """The top-k live episodes by cosine of `x_s` to the episode's own x_s (best first, ties by the
        SMALLER id). Never changes the store. k <= 0 or an empty store returns []."""
        n = len(self)
        if n == 0 or k <= 0:
            return []
        c = self.x_s[:n] @ x_s
        order = sorted(range(n), key=lambda i: (-float(c[i]), int(self.ids[i])))[:k]
        return [(int(self.ids[i]), float(c[i])) for i in order]

    def most_surprising(self, n: int) -> List[int]:
        """The ids of the `n` live episodes with the largest `surprise` value (best first, ties by the
        SMALLER id). Never changes the store."""
        m = len(self)
        if m == 0 or n <= 0:
            return []
        order = sorted(range(m), key=lambda i: (-float(self.surprise[i]), int(self.ids[i])))[:n]
        return [int(self.ids[i]) for i in order]

    def nearest_where(self, where: Tuple[int, int], k: int) -> List[Tuple[int, float]]:
        """G-MIND-1 (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400): the top-k live
        episodes by SMALLEST squared euclidean distance of `where` to the episode's OWN `where` (nearest
        first — ascending distance, unlike `nearest`'s descending cosine — ties by the SMALLER id) —
        reads the `where` column only, NEVER x_s. An episode
        with no `where` (has_where=0 — written before MOMENT was declared, or a sight-only glance the
        seam never reached) is never a candidate. Never changes the store; k <= 0, an empty store, or a
        store with no `where` anywhere returns [].

        This is the mechanism G-EYE-1/G-MIND-1's own test asks for: the E51 A1.2 position plant makes
        two classes' 32x32 glance windows BYTE-IDENTICAL (so `nearest`'s cosine cannot separate them —
        every x_s is the same vector), and only a rule that reads `where` can answer above chance
        (docs/organs/MIND-MEMORY.md §4 G-MIND-1's own test clause)."""
        n = len(self)
        if n == 0 or k <= 0:
            return []
        have = np.flatnonzero(self.has_where[:n])
        if have.size == 0:
            return []
        dy = self.where_y[have].astype(np.float64) - float(where[0])
        dx = self.where_x[have].astype(np.float64) - float(where[1])
        d2 = dy * dy + dx * dx
        order = sorted(range(have.size), key=lambda i: (float(d2[i]), int(self.ids[have[i]])))[:k]
        return [(int(self.ids[have[i]]), float(d2[i])) for i in order]

    # ------------------------------------------------------------------------------------- persistence
    def save(self, path) -> None:
        """Atomic: write to a sibling `<name>.tmp` (a real file handle, so numpy never appends its own
        `.npz` suffix) then `os.replace` it onto `path` — a reader never observes a half-written file
        (#47/#186's discipline: a fixture built by scripts/tools on this machine is never trusted
        half-written)."""
        path = _pl.Path(path)
        tmp = path.with_name(path.name + ".tmp")
        meta = np.array([self.cap, self.dim_s, self.dim_w, self.n_written, self._next_slot], dtype=np.int64)
        with open(tmp, "wb") as f:
            np.savez_compressed(f, meta=meta, moment=self.moment, ids=self.ids, x_s=self.x_s, x_w=self.x_w,
                                 word=self.word, surprise=self.surprise, x_s2=self.x_s2, has_s2=self.has_s2,
                                 # G-MIND-1 (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400):
                                 where_y=self.where_y, where_x=self.where_x, has_where=self.has_where,
                                 when=self.when, act=self.act, source=self.source, glance=self.glance)
        tmp.replace(path)

    @classmethod
    def load(cls, path) -> "Episodes":
        path = _pl.Path(path)
        with open(path, "rb") as f:
            z = np.load(f)
            meta = z["meta"]
            ep = cls(int(meta[0]), int(meta[1]), int(meta[2]))
            ep.moment[:] = z["moment"]; ep.ids[:] = z["ids"]; ep.x_s[:] = z["x_s"]; ep.x_w[:] = z["x_w"]
            ep.word[:] = z["word"]; ep.surprise[:] = z["surprise"]
            # B12: x_s2/has_s2 are absent from a file saved before this gene existed — default to "no
            # second glance anywhere" rather than refusing to load an older store.
            if "x_s2" in z.files:
                ep.x_s2[:] = z["x_s2"]; ep.has_s2[:] = z["has_s2"]
            # G-MIND-1 (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400): same rule for the
            # where/when/act/source/glance columns — absent from a file saved before MOMENT existed;
            # default to "nowhere, no clock, no act, no source, no glance" (the __init__ defaults) rather
            # than refusing to load an older store (life 3a's own episodes.npz has none of these keys).
            if "where_y" in z.files:
                ep.where_y[:] = z["where_y"]; ep.where_x[:] = z["where_x"]; ep.has_where[:] = z["has_where"]
                ep.when[:] = z["when"]; ep.act[:] = z["act"]; ep.source[:] = z["source"]; ep.glance[:] = z["glance"]
            ep.n_written = int(meta[3]); ep._next_slot = int(meta[4])
        ep._id_to_slot = {int(ep.ids[s]): s for s in range(len(ep))}
        return ep
