"""apply_null_pool.py — apply the NULL-2 pick speed-up to tools/toys/frames/null.py (run ONLY after the RED log of tests/tools/test_toys_frames_null_pick.py has been read).

Every anchor is asserted (count == 1) BEFORE the first write; the edit stamp is read from `date` when this runs.
"""
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "tools" / "toys" / "frames" / "null.py"
s = P.read_text()
stamp = subprocess.run(["date", "+%Y-%m-%d %H:%M %z"], capture_output=True, text=True, check=True).stdout.strip()


def sub(old: str, new: str) -> None:
    global s
    n = s.count(old)
    if n != 1:
        print(f"ANCHOR FAILED ({n} matches): {old[:90]!r}")
        sys.exit(2)
    s = s.replace(old, new)


# 1. the module docstring: a stamp line
sub('''# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:24 +0400 — new module, red-first against tests/tools/test_toys_frames_null.py (stage 3b).
''', f'''# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:24 +0400 — new module, red-first against tests/tools/test_toys_frames_null.py (stage 3b).
# edit: Claude (Sonnet 5.5, swarm toys), {stamp} — NULL-2's pick is now `_BigramPool` (numpy exclusion masks): BYTE-IDENTICAL to the old `_pick_bigram` (kept below, unchanged, as the REFERENCE) in picks,
# fallback flags AND generator consumption, proved by tests/tools/test_toys_frames_null_pick.py (synthetic bins of every branch, the real ALPHA4 bins and frame sets, the generator state compared after
# every pick, six planted one-line changes caught). Why: the REAL gates stopped at G5 (predicted unit CPU 182.1 min against 40): the old pick ran its 1,000-try rejection loop to its end on 892 of WEB-H's
# 1,430 real picks. No law text changes (the law pins the keys and the matching rule, not the loop).
''')

# 2. the reference comment above the old pick
sub('''def _pick_bigram(rng, bins: Dict[int, List[Frame]], b0: int, excluded: Set[Frame], lo: int, hi: int) -> Tuple[Frame, bool]:
''', '''# REFERENCE (the oracle of tests/tools/test_toys_frames_null_pick.py): not called by `null2` since the speed-up of the `_BigramPool` below; this body is unchanged from commit 724865d.
def _pick_bigram(rng, bins: Dict[int, List[Frame]], b0: int, excluded: Set[Frame], lo: int, hi: int) -> Tuple[Frame, bool]:
''')

# 3. the new pool, before the draws
sub('''# ------------------------------------------------------------------------------------------------------------------ the draws
def null1(''', '''class _BigramPool:
    """NULL-2's pool as numpy exclusion masks: the SAME picks and the SAME generator consumption as `_pick_bigram`, without its Python loop of doomed rejection tries.

    The reference ran its MAX_REJECT-try rejection loop to its end whenever a bin of more than SMALL_ENUM entries had every entry excluded, or nearly every one (on the real ALPHA4 split 892 of WEB-H's 1,430
    picks, about 3 ms each: G5's price). Level by level, in the reference's own order (d = 0, 1, ...; the lower bin's entries before the upper's), this does the same draws:
      - a level whose bins hold at most SMALL_ENUM entries together is ENUMERATED: the admissible entries, one integers() over their number;
      - a larger level with NO admissible entry would have burned MAX_REJECT tries and found `admissible` empty: it draws those MAX_REJECT integers in ONE vectorised call (the same stream: the tests compare
        the whole generator state after every pick) and goes on;
      - a larger level with some admissible entries draws the MAX_REJECT tries in one call and takes the first accepted one; the generator is then RESTORED to its state before the batch and the tries the
        reference would have made (j + 1) are redrawn, so the consumption is identical; if none is accepted the level is enumerated, as the reference does after its loop.
    The caller drives it as `null2` does: `reset(base)` at the start of a draw, `exclude(pick)` after every pick."""

    def __init__(self, bins: Dict[int, List[Frame]]):
        self.bins = bins
        self.lo, self.hi = min(bins), max(bins)
        self.where: Dict[Frame, Tuple[int, int]] = {p: (b, i) for b, lst in bins.items() for i, p in enumerate(lst)}
        self.mask: Dict[int, np.ndarray] = {b: np.zeros(len(lst), dtype=bool) for b, lst in bins.items()}
        self.n_excl: Dict[int, int] = {b: 0 for b in bins}

    def reset(self, excluded: Iterable[Frame]) -> None:
        """Forget every exclusion, then exclude `excluded` (frames outside the pool matter to nothing)."""
        for b in self.mask:
            self.mask[b][:] = False
            self.n_excl[b] = 0
        for p in excluded:
            self.exclude(p)

    def exclude(self, p: Frame) -> None:
        w = self.where.get(p)
        if w is not None and not self.mask[w[0]][w[1]]:
            self.mask[w[0]][w[1]] = True
            self.n_excl[w[0]] += 1

    def _item(self, ks: List[int], sizes: List[int], r: int) -> Frame:
        for k, size in zip(ks, sizes):
            if r < size:
                return self.bins[k][r]
            r -= size
        raise IndexError(r)

    def pick(self, rng, b0: int) -> Tuple[Frame, bool]:
        bins, mask, n_excl = self.bins, self.mask, self.n_excl
        for d in range(0, (self.hi - self.lo) + 2):
            ks = [b0] if d == 0 else [b0 - d, b0 + d]
            ks = [k for k in ks if k in bins]
            sizes = [len(bins[k]) for k in ks]
            total = sum(sizes)
            if total == 0:
                continue
            m = mask[ks[0]] if len(ks) == 1 else np.concatenate([mask[k] for k in ks])
            if total > SMALL_ENUM:
                if total - sum(n_excl[k] for k in ks) == 0:
                    rng.integers(total, size=MAX_REJECT)
                    continue
                saved = rng.bit_generator.state
                r = rng.integers(total, size=MAX_REJECT)
                ok = ~m[r]
                if ok.any():
                    j = int(np.argmax(ok))
                    rng.bit_generator.state = saved
                    rng.integers(total, size=j + 1)
                    return self._item(ks, sizes, int(r[j])), d > 0
            adm = np.flatnonzero(~m)
            if adm.size:
                return self._item(ks, sizes, int(adm[int(rng.integers(adm.size))])), d > 0
        raise NullError(f"NULL-2: no admissible adjacent bigram in any bin for bin {b0}")


# ------------------------------------------------------------------------------------------------------------------ the draws
def null1(''')

# 4. null2 uses the pool
sub('''    lo, hi = min(bb), max(bb)
    own = [log2_bin(max(1, scorer.train_adjacent(f))) for f in frames]
    rng = np.random.default_rng([SEED_ROOT, int(rule_tag), int(seed), 2])
    base = set(frames)
    values: List[float] = []
    pairs: List[Tuple[Frame, ...]] = []
    fallbacks = 0
    for _ in range(draws):
        excluded = set(base)
        dealt: List[Frame] = []
        for b0 in own:
            p, fell = _pick_bigram(rng, bb, b0, excluded, lo, hi)
            excluded.add(p)
            dealt.append(p)
            fallbacks += int(fell)
''', '''    own = [log2_bin(max(1, scorer.train_adjacent(f))) for f in frames]
    pool = _BigramPool(bb)
    rng = np.random.default_rng([SEED_ROOT, int(rule_tag), int(seed), 2])
    base = set(frames)
    values: List[float] = []
    pairs: List[Tuple[Frame, ...]] = []
    fallbacks = 0
    for _ in range(draws):
        pool.reset(base)
        dealt: List[Frame] = []
        for b0 in own:
            p, fell = pool.pick(rng, b0)
            pool.exclude(p)
            dealt.append(p)
            fallbacks += int(fell)
''')

P.write_text(s)
print("applied at", stamp)
