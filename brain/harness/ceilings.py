"""ceilings.py — STAGE -1 CLAUSE 3: the organ ceilings (B1-PREREG.md §3.3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:1x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

Must run under `/usr/bin/python3` (rendering + glancing, §3.0). Every function here takes its font/char
lists as EXPLICIT arguments rather than reaching into `brain.world.fonts` itself, so a smoke test can pass
a tiny subset (fast) while `stage_minus1.py`'s own `main()` passes the REAL, full lists (§2.2's TEACH/TEST
sets, all 26/26/10 characters) — the same code path either way, never a second "smoke" implementation.

"The organ ceiling of a family = the highest of the four readings (two oracles x two features)" read
together with the OUTPUT SHAPE (§3.3's own list: "organ_ceiling {nn, linear, max}" — three keys, not four)
means: `nn` = the better of F_cat/F_pool under the 1-NN oracle, `linear` = the better of F_cat/F_pool under
the linear oracle, `max` = the better of the two. All four raw numbers are kept in `by_feature` for
transparency (#162's law: print every gate's own reading, never only the verdict that follows from it).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from brain.glance_cache import Cache
from brain.world import names
from brain.world.build import RenderRequest, build_cache
from brain.world.glyphs import GlyphLibrary

from .oracles import LinearReadoutOracle, NearestNeighbourOracle, accuracy, f_cat, f_pool, permutation_null


class CeilingsError(Exception):
    pass


# ------------------------------------------------------------------------------------------ rendering + features
def build_naming_requests(script: str, chars: Sequence[str], teach_fonts: Sequence[str],
                           test_fonts: Sequence[str], lib: Optional[GlyphLibrary] = None) -> List[RenderRequest]:
    """One TEACH-tagged request per (char, teach font) and one TEST-tagged request per (char, test font) —
    only for pairs the library actually has (a font missing one character is skipped, never fabricated)."""
    lib = lib or GlyphLibrary(script)
    reqs: List[RenderRequest] = []
    for c in chars:
        for font in teach_fonts:
            if lib.has(c, font):
                reqs.append(RenderRequest(item_id=f"teach:{script}:{c}:{font}", script=script, char=c, font=font))
        for font in test_fonts:
            if lib.has(c, font):
                reqs.append(RenderRequest(item_id=f"test:{script}:{c}:{font}", script=script, char=c, font=font))
    return reqs


def dual_features(cache: Cache, row: int) -> Tuple[np.ndarray, np.ndarray]:
    g = cache.glances(row)
    return f_cat(g), f_pool(g)


def teach_exemplars_pool(script: str, chars: Sequence[str], teach_fonts: Sequence[str], seed: int,
                          cache_dir: Path) -> Tuple[np.ndarray, List[str]]:
    """F_pool TEACH exemplars only (no TEST renderings) — the shared input `between_class_p95` (theta, for
    other-case removal AND the never-taught filter) and `never_taught.candidate_pool` both need. A separate
    cache directory from `naming_ceiling`'s own (a documented, non-blocking inefficiency: the SAME TEACH
    renderings are built twice under two cache dirs today rather than shared — sharing them is a
    straightforward follow-up, not a correctness gap)."""
    lib = GlyphLibrary(script)
    reqs = [RenderRequest(item_id=f"teachpool:{script}:{c}:{font}", script=script, char=c, font=font)
            for c in chars for font in teach_fonts if lib.has(c, font)]
    if not reqs:
        raise CeilingsError(f"teach_exemplars_pool({script}): no renderable pairs")
    item_to_row, _header, _truths = build_cache(reqs, cache_dir, seed)
    cache = Cache(cache_dir)
    X, y = [], []
    for c in chars:
        for font in teach_fonts:
            iid = f"teachpool:{script}:{c}:{font}"
            if iid in item_to_row:
                X.append(f_pool(cache.glances(item_to_row[iid])))
                y.append(names.name_of(c, script))
    return np.array(X), y


# ------------------------------------------------------------------------------------------ label conflicts
def label_conflicts(pred: Sequence[str], truth: Sequence[str], threshold: float = 0.20) -> Set[Tuple[str, str]]:
    """"any pair (a, b) the oracle confuses a -> b in >= 20% of the test renderings" (§3.3). Confusions are
    counted PER TRUE LABEL (the denominator is that label's own test items), never pooled across labels."""
    by_true: Dict[str, List[str]] = defaultdict(list)
    for p, t in zip(pred, truth):
        by_true[t].append(p)
    out: Set[Tuple[str, str]] = set()
    for t, preds in by_true.items():
        n = len(preds)
        if n == 0:
            continue
        counts: Dict[str, int] = defaultdict(int)
        for p in preds:
            if p != t:
                counts[p] += 1
        for p, c in counts.items():
            if c / n >= threshold:
                out.add((t, p))
    return out


# ------------------------------------------------------------------------------------------ the naming ceiling
def naming_ceiling(script: str, chars: Sequence[str], teach_fonts: Sequence[str], test_fonts: Sequence[str],
                    seed: int, cache_dir: Path, n_teach_variants: Sequence[int] = (4, 3),
                    n_perm: int = 20) -> Dict[str, object]:
    """Per §3.3: naming ceiling at 4 TEACH fonts and at 3 (the first 3, `fonts.TEACH_FONTS_3`'s own order).
    Returns `{4: {...}, 3: {...}}`, each with `organ_ceiling {nn, linear, max, by_feature}`, `null {mean,
    p95}`, `label_conflicts`, `n_train`, `n_test`."""
    lib = GlyphLibrary(script)
    reqs = build_naming_requests(script, chars, teach_fonts, test_fonts, lib)
    if not reqs:
        raise CeilingsError(f"naming_ceiling({script}): no renderable (char, font) pairs at all")
    item_to_row, header, _truths = build_cache(reqs, cache_dir, seed)
    cache = Cache(cache_dir)

    out: Dict[str, object] = {"header_row_count": header["row_count"]}
    for k in n_teach_variants:
        used_fonts = list(teach_fonts)[:k]
        Xcat_tr, Xpool_tr, y_tr = [], [], []
        for c in chars:
            for font in used_fonts:
                iid = f"teach:{script}:{c}:{font}"
                if iid in item_to_row:
                    cat, pool = dual_features(cache, item_to_row[iid])
                    Xcat_tr.append(cat); Xpool_tr.append(pool); y_tr.append(names.name_of(c, script))
        Xcat_te, Xpool_te, y_te = [], [], []
        for c in chars:
            for font in test_fonts:
                iid = f"test:{script}:{c}:{font}"
                if iid in item_to_row:
                    cat, pool = dual_features(cache, item_to_row[iid])
                    Xcat_te.append(cat); Xpool_te.append(pool); y_te.append(names.name_of(c, script))
        if not y_tr or not y_te:
            raise CeilingsError(f"naming_ceiling({script}, k={k}): empty train or test set")
        Xcat_tr, Xpool_tr = np.array(Xcat_tr), np.array(Xpool_tr)
        Xcat_te, Xpool_te = np.array(Xcat_te), np.array(Xpool_te)

        nn_cat = NearestNeighbourOracle().fit(Xcat_tr, y_tr)
        nn_pool = NearestNeighbourOracle().fit(Xpool_tr, y_tr)
        lin_cat = LinearReadoutOracle().fit(Xcat_tr, y_tr)
        lin_pool = LinearReadoutOracle().fit(Xpool_tr, y_tr)

        pred_nn_cat = nn_cat.predict(Xcat_te)
        pred_nn_pool = nn_pool.predict(Xpool_te)
        pred_lin_cat = lin_cat.predict(Xcat_te)
        pred_lin_pool = lin_pool.predict(Xpool_te)

        by_feature = {
            "nn_fcat": accuracy(pred_nn_cat, y_te), "nn_fpool": accuracy(pred_nn_pool, y_te),
            "linear_fcat": accuracy(pred_lin_cat, y_te), "linear_fpool": accuracy(pred_lin_pool, y_te),
        }
        nn_best = max(by_feature["nn_fcat"], by_feature["nn_fpool"])
        linear_best = max(by_feature["linear_fcat"], by_feature["linear_fpool"])

        conflicts = (label_conflicts(pred_lin_pool, y_te) | label_conflicts(pred_nn_pool, y_te))

        def _fit_predict_pool(Xtr, ytr, Xte):
            return LinearReadoutOracle().fit(Xtr, ytr).predict(Xte)
        null = permutation_null(_fit_predict_pool, Xpool_tr, y_tr, Xpool_te, y_te, seed=seed, n_perm=n_perm)

        out[str(k)] = {
            "organ_ceiling": {"nn": nn_best, "linear": linear_best, "max": max(nn_best, linear_best), "by_feature": by_feature},
            "null": {"mean": null["mean"], "p95": null["p95"]},
            "label_conflicts": sorted(conflicts),
            "n_train": len(y_tr), "n_test": len(y_te),
        }
    out["cache_header"] = header
    return out


# ------------------------------------------------------------------------------------------ relation ceilings (derived, no new rendering)
def per_form_accuracy(script: str, chars: Sequence[str], naming_test_predictions: Dict[str, str],
                       naming_test_truth: Dict[str, str]) -> Dict[str, float]:
    """naming_test_{predictions,truth} keyed by (char, font) item_id-ish strings this caller controls;
    returns the per-CHAR accuracy over however many test fonts were asked (§3.3: "an item's ceiling = the
    oracle's naming accuracy on its operand(s)")."""
    by_char_correct: Dict[str, int] = defaultdict(int)
    by_char_total: Dict[str, int] = defaultdict(int)
    for key, truth in naming_test_truth.items():
        char = key.split(":")[0]
        by_char_total[char] += 1
        if naming_test_predictions.get(key) == truth:
            by_char_correct[char] += 1
    return {c: (by_char_correct[c] / by_char_total[c] if by_char_total[c] else 0.0) for c in chars}


def relation_ceiling(operand_names: Sequence[str], naming_accuracy_by_name: Dict[str, float],
                      is_pick: bool = False, pick_accuracy: Optional[float] = None) -> float:
    """§3.3: "an item's ceiling = the oracle's naming accuracy on its operand(s) x (for picks) its accuracy
    in identifying the right candidate; the family's ceiling = the mean over items." This function computes
    ONE item's ceiling (the product over its operands, times the pick factor if any); the caller means over
    its family's items."""
    ceiling = 1.0
    for nm in operand_names:
        ceiling *= naming_accuracy_by_name.get(nm, 0.0)
    if is_pick:
        if pick_accuracy is None:
            raise CeilingsError("relation_ceiling(is_pick=True) needs pick_accuracy")
        ceiling *= pick_accuracy
    return ceiling


def family_relation_ceiling(items: Sequence[Sequence[str]], naming_accuracy_by_name: Dict[str, float],
                             is_pick: bool = False, pick_accuracy: Optional[float] = None) -> float:
    vals = [relation_ceiling(item, naming_accuracy_by_name, is_pick, pick_accuracy) for item in items]
    return float(np.mean(vals)) if vals else 0.0


# ------------------------------------------------------------------------------------------ other-case removal (F_pool cosine)
def other_case_removed_pairs(script_upper: str, script_lower: str, letters: Sequence[str], font: str,
                              seed: int, cache_dir: Path, teach_cos_p95: float) -> List[Dict[str, object]]:
    """"Other-case pairs identical through the organ (their two forms' F cosine above the between-class p95
    of the TEACH letters) are REMOVED before counting n" (§3.3). `teach_cos_p95` is the between-class p95
    computed once over the TEACH exemplars (see `between_class_p95`, below) and passed in so it is computed
    ONCE per script pair, not recomputed per letter."""
    lib_u, lib_l = GlyphLibrary(script_upper), GlyphLibrary(script_lower)
    reqs = []
    for letter in letters:
        U = letter.upper()
        if lib_u.has(U, font):
            reqs.append(RenderRequest(item_id=f"oc:upper:{letter}", script=script_upper, char=U, font=font))
        if lib_l.has(letter, font):
            reqs.append(RenderRequest(item_id=f"oc:lower:{letter}", script=script_lower, char=letter, font=font))
    item_to_row, _header, _truths = build_cache(reqs, cache_dir, seed)
    cache = Cache(cache_dir)
    removed = []
    for letter in letters:
        u_key, l_key = f"oc:upper:{letter}", f"oc:lower:{letter}"
        if u_key not in item_to_row or l_key not in item_to_row:
            continue
        vu = f_pool(cache.glances(item_to_row[u_key]))
        vl = f_pool(cache.glances(item_to_row[l_key]))
        cos = float(np.dot(vu, vl))
        if cos > teach_cos_p95:
            removed.append({"letter": letter, "cosine": cos})
    return removed


# ------------------------------------------------------------------------------------------ perceptual ceilings (mirror, loop, vowel)
def _form_item_id(tag: str, form: Tuple[str, str], font: str, occurrence: int = 0) -> str:
    script, char = form
    return f"{tag}:{script}:{char}:{font}:{occurrence}"


def _render_forms(tag: str, forms: Sequence[Tuple[str, str]], fonts_by_form, seed: int, cache_dir: Path,
                   libs: Dict[str, GlyphLibrary]) -> Tuple[Dict[str, int], Dict[str, object]]:
    """`fonts_by_form(form) -> List[str]` decides which font(s) to render EACH form in (a fixed TEACH list
    for training, or a seeded pair of TEST fonts for a held-out form)."""
    reqs = []
    for form in forms:
        script, char = form
        lib = libs.setdefault(script, GlyphLibrary(script))
        for i, font in enumerate(fonts_by_form(form)):
            if lib.has(char, font):
                reqs.append(RenderRequest(item_id=_form_item_id(tag, form, font, i), script=script, char=char, font=font))
    if not reqs:
        raise CeilingsError(f"_render_forms({tag}): no renderable forms")
    item_to_row, header, _truths = build_cache(reqs, cache_dir, seed)
    return item_to_row, header


def binary_perceptual_ceiling(positive_taught: Sequence[Tuple[str, str]], negative_taught: Sequence[Tuple[str, str]],
                               positive_held: Sequence[Tuple[str, str]], negative_held: Sequence[Tuple[str, str]],
                               teach_fonts: Sequence[str], test_fonts_by_case: Dict[str, Sequence[str]],
                               seed: int, cache_dir: Path, tag: str, n_test_fonts_per_form: int = 3) -> Dict[str, object]:
    """MIRROR/HAS_LOOP (§3.3): "the linear oracle fitted on the TAUGHT letter-forms' category labels, tested
    on the held-out letter-forms ... (per form, majority over its 3 renderings)." Train = one TEACH-font
    rendering per taught form per TEACH font (all 4); test = `n_test_fonts_per_form` SEEDED test fonts (of
    the form's own case) per held-out form, majority-voted."""
    from .seeds import substream
    libs: Dict[str, GlyphLibrary] = {}

    def teach_fonts_fn(_form):
        return list(teach_fonts)

    taught_forms = list(positive_taught) + list(negative_taught)
    taught_labels = {f: True for f in positive_taught}
    taught_labels.update({f: False for f in negative_taught})
    item_to_row_tr, header = _render_forms(f"{tag}:train", taught_forms, teach_fonts_fn, seed, cache_dir, libs)
    cache = Cache(cache_dir)
    X_tr, y_tr = [], []
    for form in taught_forms:
        for font in teach_fonts:
            iid = _form_item_id(f"{tag}:train", form, font, teach_fonts.index(font))
            if iid in item_to_row_tr:
                X_tr.append(f_pool(cache.glances(item_to_row_tr[iid])))
                y_tr.append("yes" if taught_labels[form] else "no")
    if not y_tr:
        raise CeilingsError(f"binary_perceptual_ceiling({tag}): empty training set")
    oracle = LinearReadoutOracle().fit(np.array(X_tr), y_tr)

    held_forms = list(positive_held) + list(negative_held)
    held_labels = {f: True for f in positive_held}
    held_labels.update({f: False for f in negative_held})

    def test_fonts_fn(form):
        script, _char = form
        case_fonts = test_fonts_by_case[script]
        rng = substream(seed, f"{tag}:test_fonts:{form}")
        idx = rng.choice(len(case_fonts), size=min(n_test_fonts_per_form, len(case_fonts)), replace=False)
        return [case_fonts[i] for i in sorted(int(i) for i in idx)]

    item_to_row_te, _header2 = _render_forms(f"{tag}:test", held_forms, test_fonts_fn, seed, cache_dir, libs)
    cache = Cache(cache_dir)   # reopen: the SAME cache_dir now also holds the test renderings
    correct = 0
    total = 0
    for form in held_forms:
        fonts_used = test_fonts_fn(form)
        votes = []
        for i, font in enumerate(fonts_used):
            iid = _form_item_id(f"{tag}:test", form, font, i)
            if iid in item_to_row_te:
                v = f_pool(cache.glances(item_to_row_te[iid]))
                votes.append(oracle.predict(v[None, :])[0])
        if not votes:
            continue
        majority = max(set(votes), key=votes.count)
        truth = "yes" if held_labels[form] else "no"
        total += 1
        if majority == truth:
            correct += 1
    if total == 0:
        raise CeilingsError(f"binary_perceptual_ceiling({tag}): no held-out forms scored")
    return {"accuracy": correct / total, "n": total, "n_train": len(y_tr)}


def vowel_ceiling(vowel_forms: Sequence[Tuple[str, str]], consonant_forms_all: Sequence[Tuple[str, str]],
                   consonant_forms_test: Sequence[Tuple[str, str]], teach_fonts: Sequence[str],
                   test_fonts_by_case: Dict[str, Sequence[str]], seed: int, cache_dir: Path,
                   n_test_fonts_per_form: int = 2) -> Dict[str, object]:
    """VOWEL (§3.3): "fitted on TEACH-font renderings of all 52 forms, tested on §5.2's TEST-font items" —
    train = ALL 52 forms (vowel_forms + every OTHER letter form, i.e. `consonant_forms_all`, both cases) in
    every TEACH font; test = the 10 vowel forms + `consonant_forms_test`'s 10 seeded consonants, each in
    `n_test_fonts_per_form` seeded TEST fonts of its own case."""
    from .seeds import substream
    libs: Dict[str, GlyphLibrary] = {}
    all_forms = list(vowel_forms) + list(consonant_forms_all)

    def teach_fonts_fn(_form):
        return list(teach_fonts)

    item_to_row_tr, header = _render_forms("vowel:train", all_forms, teach_fonts_fn, seed, cache_dir, libs)
    cache = Cache(cache_dir)
    X_tr, y_tr = [], []
    vowel_set = set(vowel_forms)
    for form in all_forms:
        for font in teach_fonts:
            iid = _form_item_id("vowel:train", form, font, teach_fonts.index(font))
            if iid in item_to_row_tr:
                X_tr.append(f_pool(cache.glances(item_to_row_tr[iid])))
                y_tr.append("vowel" if form in vowel_set else "consonant")
    oracle = LinearReadoutOracle().fit(np.array(X_tr), y_tr)

    test_forms = list(vowel_forms) + list(consonant_forms_test)

    def test_fonts_fn(form):
        script, _char = form
        case_fonts = test_fonts_by_case[script]
        rng = substream(seed, f"vowel:test_fonts:{form}")
        idx = rng.choice(len(case_fonts), size=min(n_test_fonts_per_form, len(case_fonts)), replace=False)
        return [case_fonts[i] for i in sorted(int(i) for i in idx)]

    item_to_row_te, _h2 = _render_forms("vowel:test", test_forms, test_fonts_fn, seed, cache_dir, libs)
    cache = Cache(cache_dir)
    correct, total = 0, 0
    for form in test_forms:
        truth = "vowel" if form in vowel_set else "consonant"
        for i, font in enumerate(test_fonts_fn(form)):
            iid = _form_item_id("vowel:test", form, font, i)
            if iid in item_to_row_te:
                v = f_pool(cache.glances(item_to_row_te[iid]))
                pred = oracle.predict(v[None, :])[0]
                total += 1
                correct += int(pred == truth)
    if total == 0:
        raise CeilingsError("vowel_ceiling: no test items scored")
    return {"accuracy": correct / total, "n": total, "n_train": len(y_tr)}


def between_class_p95(X: np.ndarray, y: Sequence[str]) -> float:
    """The p95 of BETWEEN-CLASS cosines among a set of unit F_pool vectors — used both as the other-case
    removal threshold and as θ for the never-taught pool (§3.3 uses the same phrase, "between-class p95 of
    the TEACH letters", in both places)."""
    y = list(y)
    n = len(y)
    cos_vals = []
    for i in range(n):
        for j in range(i + 1, n):
            if y[i] != y[j]:
                cos_vals.append(float(np.dot(X[i], X[j])))
    if not cos_vals:
        raise CeilingsError("between_class_p95: no between-class pairs found")
    return float(np.percentile(cos_vals, 95))
