"""The mutant table for TOY C's tools/toys/frames/null.py `_BigramPool` and the new loop of `null2` (one single textual replacement each; the NAMED test must be what catches it).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 23:00 +0400 — new (the speed-up of NULL-2's pick; the identity test is the instrument, this sweep is its own check: a pick that is wrong in any one place must fail the proof).

Equivalent mutants are NOT in the table; each is listed below with its reason and covered by a different assertion where it matters:
  - `total - sum(n_excl...) == 0` -> `<= 0`: n_excl never exceeds the size, so it is the same test.
  - a doomed level that is NOT detected (the counters wrong in the direction «some admissible» when none is): the batch is drawn anyway (the same MAX_REJECT draws), no entry is accepted, the enumeration is empty and
    the level is left: the same picks and the same consumption, only slower. The counters themselves are therefore pinned by their own unit test (the counters agree with the masks), not by the identity.
"""
TESTS = "tests.tools.test_toys_frames_null_pick,tests.tools.test_toys_frames_null"
I = "TestIdentitySynthetic."
SYN = I + "test_every_scenario_reads_identical_in_pick_flag_and_generator_state_after_every_pick"
CNT = I + "test_a_reset_forgets_every_exclusion_and_the_counters_agree_with_the_masks"
ERR = I + "test_an_error_leaves_the_same_text_and_the_same_state"
N2S = "TestNull2KeepsItsContractOnSmallStreams.test_null2_equals_the_reference_null2_on_a_small_hand_stream_with_fallbacks"
N2R = "TestIdentityRealBins.test_null2_itself_equals_a_reference_null2_that_calls_the_old_pick_on_real_sets"
REAL = "TestIdentityRealBins.test_identical_pick_flag_and_generator_state_after_every_pick_on_real_bins_and_real_frame_sets"
REFPIN = "TestTheReferenceIsTheOldPickUnchanged.test_the_reference_source_is_the_one_of_724865d"
CONST = "TestTheReferenceIsTheOldPickUnchanged.test_the_constants_both_picks_read_are_the_ones_of_724865d"

MUTANTS = []


def M(name, old, new, expect, why, count=1):
    MUTANTS.append({"name": name, "old": old, "new": new, "expect": list(expect), "why": why, "count": count})


# ---- the levels
M("np-levels-short", "for d in range(0, (self.hi - self.lo) + 2):", "for d in range(0, (self.hi - self.lo) + 1):", [SYN], "one level too few")
M("np-order-swapped", "ks = [b0] if d == 0 else [b0 - d, b0 + d]", "ks = [b0] if d == 0 else [b0 + d, b0 - d]", [SYN], "the upper bin before the lower")
M("np-absent-bins-kept", "ks = [k for k in ks if k in bins]", "ks = [k for k in ks]", [SYN], "an absent bin is indexed")
M("np-total0-break", "            if total == 0:\n                continue\n            m = mask", "            if total == 0:\n                break\n            m = mask", [SYN], "an empty level ends the search")
M("np-mask-reversed", "else np.concatenate([mask[k] for k in ks])", "else np.concatenate([mask[k] for k in reversed(ks)])", [SYN], "the two masks joined in the other order")
M("np-enum-boundary", "if total > SMALL_ENUM:\n                if total - sum(n_excl[k] for k in ks) == 0:", "if total >= SMALL_ENUM:\n                if total - sum(n_excl[k] for k in ks) == 0:", [SYN], "a pool of exactly 64 is rejection-sampled")
# ---- the doomed level
M("np-doomed-one", "if total - sum(n_excl[k] for k in ks) == 0:", "if total - sum(n_excl[k] for k in ks) == 1:", [SYN], "a level with ONE admissible entry is treated as doomed")
M("np-doomed-advance-short", "rng.integers(total, size=MAX_REJECT)\n                    continue", "rng.integers(total, size=MAX_REJECT - 1)\n                    continue", [SYN], "the doomed level consumes 999 draws")
M("np-doomed-advance-long", "rng.integers(total, size=MAX_REJECT)\n                    continue", "rng.integers(total, size=MAX_REJECT + 1)\n                    continue", [SYN], "the doomed level consumes 1,001 draws")
M("np-doomed-no-draw", "rng.integers(total, size=MAX_REJECT)\n                    continue", "pass\n                    continue", [SYN], "the doomed level consumes nothing")
M("np-doomed-no-continue", "rng.integers(total, size=MAX_REJECT)\n                    continue", "rng.integers(total, size=MAX_REJECT)\n                    pass", [SYN], "the doomed level falls through to the batch")
# ---- the batch and the accept
M("np-batch-long", "r = rng.integers(total, size=MAX_REJECT)\n                ok = ~m[r]", "r = rng.integers(total, size=MAX_REJECT + 1)\n                ok = ~m[r]", [SYN], "a batch of 1,001 tries")
M("np-batch-short", "r = rng.integers(total, size=MAX_REJECT)\n                ok = ~m[r]", "r = rng.integers(total, size=MAX_REJECT - 1)\n                ok = ~m[r]", [SYN], "a batch of 999 tries")
M("np-accept-inverted", "ok = ~m[r]", "ok = m[r]", [SYN], "the loop accepts the excluded")
M("np-any-all", "if ok.any():", "if ok.all():", [SYN], "accept only when every try is admissible")
M("np-first-last", "j = int(np.argmax(ok))", "j = int(len(ok) - 1 - np.argmax(ok[::-1]))", [SYN], "the last accepted try, not the first")
M("np-first-min", "j = int(np.argmax(ok))", "j = int(np.argmin(ok))", [SYN], "the first REJECTED try")
M("np-no-restore", "rng.bit_generator.state = saved\n", "pass\n", [SYN], "the generator keeps the whole batch")
M("np-redraw-short", "rng.integers(total, size=j + 1)", "rng.integers(total, size=j)", [SYN], "the generator one draw behind")
M("np-redraw-long", "rng.integers(total, size=j + 1)", "rng.integers(total, size=j + 2)", [SYN], "the generator one draw ahead")
M("np-flag-accept", "return self._item(ks, sizes, int(r[j])), d > 0", "return self._item(ks, sizes, int(r[j])), d >= 0", [SYN], "the flag of a rejection accept")
M("np-flag-accept-false", "return self._item(ks, sizes, int(r[j])), d > 0", "return self._item(ks, sizes, int(r[j])), False", [SYN], "the flag of a rejection accept is never a fallback")
M("np-pick-index", "return self._item(ks, sizes, int(r[j])), d > 0", "return self._item(ks, sizes, int(r[0])), d > 0", [SYN], "the first try's index, not the accepted one's")
# ---- the enumeration
M("np-enum-inverted", "adm = np.flatnonzero(~m)", "adm = np.flatnonzero(m)", [SYN], "the excluded are enumerated")
M("np-enum-gt1", "if adm.size:", "if adm.size > 1:", [SYN], "a single admissible entry is not taken")
M("np-enum-first", "adm[int(rng.integers(adm.size))]", "adm[0]", [SYN], "no draw: the first admissible")
M("np-enum-last", "adm[int(rng.integers(adm.size))]", "adm[-1]", [SYN], "no draw: the last admissible")
M("np-enum-flag", "int(adm[int(rng.integers(adm.size))])), d > 0", "int(adm[int(rng.integers(adm.size))])), d >= 0", [SYN], "the flag of an enumerated pick")
M("np-error-text", "\n        raise NullError(f\"NULL-2: no admissible adjacent bigram in any bin for bin {b0}\")", "\n        raise NullError(f\"NULL-2: no admissible adjacent bigram in any bin for bin {b0 + 1}\")", [ERR], "the error names another bin")
# ---- the item map
M("np-item-le", "if r < size:\n                return self.bins[k][r]", "if r <= size:\n                return self.bins[k][r]", [SYN], "an index equal to the first bin's size is taken from it")
M("np-item-offset", "            r -= size\n        raise IndexError(r)", "            r -= size + 1\n        raise IndexError(r)", [SYN], "the second bin's offset is off by one")
# ---- the bookkeeping
M("np-where-index", "{p: (b, i) for b, lst in bins.items() for i, p in enumerate(lst)}", "{p: (b, i + 1) for b, lst in bins.items() for i, p in enumerate(lst)}", [SYN], "an exclusion marks the neighbour")
M("np-mask-ones", "np.zeros(len(lst), dtype=bool)", "np.ones(len(lst), dtype=bool)", [CNT], "everything starts excluded (null2 and the traces reset before the first pick, so only the fresh-pool assertion of the counters test sees it)")
M("np-mask-dtype", "np.zeros(len(lst), dtype=bool)", "np.zeros(len(lst), dtype=int)", [SYN], "an integer mask: ~0 is -1, always truthy")
M("np-exclude-twice", "if w is not None and not self.mask[w[0]][w[1]]:", "if w is not None:", [CNT], "excluding twice counts twice")
M("np-exclude-count2", "self.n_excl[w[0]] += 1", "self.n_excl[w[0]] += 2", [CNT], "each exclusion counts twice")
M("np-exclude-nocount", "self.n_excl[w[0]] += 1", "self.n_excl[w[0]] += 0", [CNT], "an exclusion is not counted")
M("np-reset-mask", "            self.mask[b][:] = False\n", "            pass\n", [SYN], "a reset forgets no mask")
M("np-reset-count", "            self.n_excl[b] = 0\n", "            pass\n", [CNT], "a reset forgets no counter")
M("np-reset-skip-base", "        for p in excluded:\n            self.exclude(p)", "        for p in []:\n            self.exclude(p)", [SYN], "the base frames are not excluded")
# ---- null2's loop
M("n2-reset-empty", "pool.reset(base)", "pool.reset(set())", [N2S], "the rule's own frames are not excluded")
M("n2-no-exclude", "p, fell = pool.pick(rng, b0)\n            pool.exclude(p)", "p, fell = pool.pick(rng, b0)\n            pass", [N2S], "a pick is not excluded after it")
M("n2-pick-other-bin", "p, fell = pool.pick(rng, b0)", "p, fell = pool.pick(rng, b0 + 1)", [N2S], "the bin of the frame's own count + 1")
M("n2-pool-per-draw", "    pool = _BigramPool(bb)\n", "    pool = _BigramPool({b: list(v)[:-1] for b, v in bb.items()})\n", [N2S], "a pool without the last entry of each bin")
M("n2-flag-dropped", "fallbacks += int(fell)\n        values.append(scorer.gain(set(dealt)).G)\n        if keep_pairs:\n            pairs.append(tuple(dealt))\n    return NullResult(\"NULL-2\"", "fallbacks += 0\n        values.append(scorer.gain(set(dealt)).G)\n        if keep_pairs:\n            pairs.append(tuple(dealt))\n    return NullResult(\"NULL-2\"", [N2S], "the fallbacks of NULL-2 are not counted")
# ---- the reference and the constants (the proof compares with the reference IN THE SAME TREE: both are pinned)
M("ref-constant-reject", "MAX_REJECT = 1000", "MAX_REJECT = 999", [CONST], "a constant both picks read")
M("ref-constant-enum", "SMALL_ENUM = 64 ", "SMALL_ENUM = 65 ", [CONST], "a constant both picks read")
M("ref-body", "                if pick not in excluded:\n                    return pick, d > 0\n        admissible = [p for x in lists for p in x if p not in excluded]\n        if admissible:\n            return admissible[int(rng.integers(len(admissible)))], d > 0\n    raise NullError(f\"NULL-2:", "                if pick not in excluded:\n                    return pick, d > 0\n        admissible = [p for x in lists for p in x if p not in excluded]\n        if admissible:\n            return admissible[int(rng.integers(len(admissible)))], d >= 0\n    raise NullError(f\"NULL-2:", [REFPIN], "the reference's own flag changed (the new class would still equal it only if it changed too)")

TABLE = {"module": "tools.toys.frames.null", "file": "tools/toys/frames/null.py", "tests": TESTS,
         "control_broken": {"old": "def log2_bin(count: int) -> int:\n", "new": "def log2_bin(count: int) -> int:\n    raise RuntimeError('BROKEN CONTROL')\n"}, "mutants": MUTANTS}
