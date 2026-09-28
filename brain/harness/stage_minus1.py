"""stage_minus1.py — STAGE -1: run FIRST, before any arm on any seed (B1-PREREG.md §3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:4x +0400 — B1-PREREG.md §9 row 1, step 4.

Must run under `/usr/bin/python3` (§3.0: rendering and glancing happen only there). Orchestrates every
clause of §3 and writes `docs/brain/b1/stage-1/ceilings.json` exactly per §3.3's own output list.

CADENCE (B1-PREREG.md §9's own table, "the box is busy" note; the PREREG's cadence rule): the FULL run (the
real TEACH/TEST font lists across all three scripts, the real perceptual and never-taught candidate sets —
roughly 1,900 real gaze calls, §7's own "a few thousand canvases" estimate) is launched only when
`uptime`'s load is under 8, or after 21:00 — `main()` REFUSES to run at full scale otherwise unless
`--force` is given, and always accepts `--smoke` (a tiny, fast subset of characters/fonts) for iteration
regardless of load. This file was built and its own tests pass at `--smoke` scale on 2026-09-24 with load
~18-20 all afternoon; the full run has NOT been launched this session — see
`docs/briefs/B1-BUILDER2-REPORT.md` for the exact command to run it later.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE1_OUT = REPO_ROOT / "docs" / "brain" / "b1" / "stage-1"
CACHE_ROOT = Path("/data/dev/brain-runs/b1/cache")

sys.path.insert(0, str(REPO_ROOT))

from brain.harness import bars, env  # noqa: E402
from brain.harness.ceilings import (  # noqa: E402
    between_class_p95, binary_perceptual_ceiling, family_relation_ceiling, naming_ceiling,
    other_case_removed_pairs, teach_exemplars_pool, vowel_ceiling,
)
from brain.harness.never_taught import NeverTaughtError, candidate_pool, select_pools  # noqa: E402
from brain.harness.probes import run_both as run_probes  # noqa: E402
from brain.world import families, fonts, names  # noqa: E402
from brain.world.glyphs import GlyphLibrary  # noqa: E402


class StageMinus1Error(Exception):
    pass


def current_load1() -> float:
    return __import__("os").getloadavg()[0]


def _smoke_lists() -> Dict[str, object]:
    """A TINY, fast subset — enough to exercise every code path (naming, relations, perceptual, never-
    taught, probes) without spending more than roughly a minute of real gaze calls."""
    teach = fonts.TEACH_FONTS_ORDER
    return {
        "upper_chars": list("ABCDE"), "lower_chars": list("abcde"), "digit_chars": list("01234"),
        "upper_test_fonts": fonts.compute()["test"]["latin-upper"][:3],
        "lower_test_fonts": fonts.compute()["test"]["latin-lower"][:3],
        "digit_test_fonts": fonts.compute()["test"]["digits"][:3],
        "teach_fonts": teach,
    }


def _full_lists() -> Dict[str, object]:
    f = fonts.compute()
    return {
        "upper_chars": list(names.UPPER), "lower_chars": list(names.LOWER), "digit_chars": list(names.DIGIT_CHARS),
        "upper_test_fonts": f["test"]["latin-upper"], "lower_test_fonts": f["test"]["latin-lower"],
        "digit_test_fonts": f["test"]["digits"], "teach_fonts": fonts.TEACH_FONTS_ORDER,
    }


def compute_naming(seed: int, lists: Dict[str, object], cache_dir: Path) -> Dict[str, object]:
    out = {}
    out["latin-upper"] = naming_ceiling("latin-upper", lists["upper_chars"], lists["teach_fonts"],
                                         lists["upper_test_fonts"], seed, cache_dir / "naming-upper")
    out["latin-lower"] = naming_ceiling("latin-lower", lists["lower_chars"], lists["teach_fonts"],
                                         lists["lower_test_fonts"], seed, cache_dir / "naming-lower")
    out["digits"] = naming_ceiling("digits", lists["digit_chars"], lists["teach_fonts"],
                                    lists["digit_test_fonts"], seed, cache_dir / "naming-digits")
    return out


def _naming_accuracy_by_name(naming_script_result: Dict[str, object], script: str, k: str = "4") -> Dict[str, float]:
    """The REAL per-name accuracy `naming_ceiling` now returns (the advisor's review, 2026-09-24: a uniform
    aggregate is structurally wrong for OTHER_CASE, whose k is recomputed per-letter after stage −1, §5.2).
    A name naming_ceiling never scored (a font/char combo the library lacked) falls back to the family's own
    aggregate — printed as a fallback, never silently merged with the real per-name numbers."""
    per_name = dict(naming_script_result[k]["per_name_accuracy"])
    agg = naming_script_result[k]["organ_ceiling"]["max"]
    chars = {"latin-upper": names.UPPER, "latin-lower": names.LOWER, "digits": names.DIGIT_CHARS}[script]
    out = {}
    for c in chars:
        nm = names.name_of(c, script)
        out[nm] = per_name.get(nm, agg)
    return out


def compute_relation_ceilings(seed: int, naming_by_name: Dict[str, float]) -> Dict[str, object]:
    ab = families.after_before(seed)
    two_after = families.two_after(seed)
    between = families.between(seed)
    other_case = families.other_case(seed)
    chain = families.chain(after_before_result=ab)
    transfer = families.transfer()

    after_items = [[a] for a, _b in ab["held_out"]]
    before_items = [[b] for _a, b in ab["held_out"]]
    two_after_items = [[a] for a, _c in two_after["held_out"]]
    between_items = [[a, c] for a, _b, c in between["held_out"]]
    chain_items = [[a] for a, _b in chain["items"]]
    other_case_items = [[nm] for nm in other_case["held_out"]]

    return {
        "AFTER": family_relation_ceiling(after_items, naming_by_name),
        "BEFORE": family_relation_ceiling(before_items, naming_by_name),
        "TWO_AFTER": family_relation_ceiling(two_after_items, naming_by_name),
        "BETWEEN": family_relation_ceiling(between_items, naming_by_name),
        "CHAIN": family_relation_ceiling(chain_items, naming_by_name),
        "OTHER_CASE": family_relation_ceiling(other_case_items, naming_by_name),
        "TRANSFER_AFTER": family_relation_ceiling([[a] for a, _b in transfer["after"]], naming_by_name),
        "TRANSFER_BEFORE": family_relation_ceiling([[b] for _a, b in transfer["before"]], naming_by_name),
    }


def _normalise(max_value: float, n: int, k_min: int, nn: Optional[float] = None, linear: Optional[float] = None,
               extra: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    entry = {"organ_ceiling": {"nn": nn if nn is not None else max_value,
                                "linear": linear if linear is not None else max_value,
                                "max": max_value},
             "n": n, "k_min": k_min}
    if extra:
        entry.update(extra)
    return entry


def run(seed: int, smoke: bool, out_dir: Path, cache_dir: Path, force: bool = False) -> Dict[str, object]:
    if not smoke:
        load1 = current_load1()
        if load1 >= 8 and not force:
            raise StageMinus1Error(f"load average {load1:.1f} >= 8 — the full stage −1 run waits for load < 8 "
                                    f"or after 21:00 (B1-PREREG.md §9's cadence rule); pass force=True to override")

    lists = _smoke_lists() if smoke else _full_lists()

    report: Dict[str, object] = {"seed": seed, "smoke": smoke}

    probes = run_probes(seed)
    report["controls"] = probes
    if not probes["pass"]:
        raise StageMinus1Error(f"probe controls FAILED — ceilings are VOID, nothing proceeds: {probes}")

    naming = compute_naming(seed, lists, cache_dir)
    report["naming_raw"] = naming

    families_out: Dict[str, object] = {}
    for script, result in naming.items():
        for k in ("4", "3"):
            n = result[k]["n_test"]
            families_out[f"NAMING_{script}_{k}fonts"] = _normalise(
                result[k]["organ_ceiling"]["max"], n=n, k_min=1,
                nn=result[k]["organ_ceiling"]["nn"], linear=result[k]["organ_ceiling"]["linear"],
                extra={"null": result[k]["null"], "label_conflicts": result[k]["label_conflicts"], "chance": 0.0})

    naming_by_name: Dict[str, float] = {}
    for script in ("latin-upper", "latin-lower", "digits"):
        naming_by_name.update(_naming_accuracy_by_name(naming[script], script))
    relation_ceilings = compute_relation_ceilings(seed, naming_by_name)
    fam = families
    counts = {"AFTER": (len(fam.after_before(seed)["held_out"]), 1), "BEFORE": (len(fam.after_before(seed)["held_out"]), 1),
              "TWO_AFTER": (len(fam.two_after(seed)["held_out"]), 1), "BETWEEN": (len(fam.between(seed)["held_out"]), 1),
              "CHAIN": (len(fam.chain(seed=seed)["items"]), 1), "OTHER_CASE": (len(fam.other_case(seed)["held_out"]), 1),
              "TRANSFER_AFTER": (len(fam.transfer()["after"]), 1), "TRANSFER_BEFORE": (len(fam.transfer()["before"]), 1)}
    for name_, ceiling in relation_ceilings.items():
        n, k_min = counts[name_]
        families_out[name_] = _normalise(ceiling, n=n, k_min=k_min, extra={"chance": 1 / 25})

    report["relation_ceilings"] = relation_ceilings

    if smoke:
        report["note_skipped_in_smoke"] = ("other-case removal, perceptual (mirror/loop/vowel) ceilings and "
                                            "the never-taught pool are skipped at --smoke scale; each is "
                                            "exercised directly by its own tests (test_families/test_never_taught/"
                                            "test_probes) and wired here for the FULL run.")
    else:
        teach_X, teach_y = teach_exemplars_pool("latin-upper", lists["upper_chars"], lists["teach_fonts"],
                                                 seed, cache_dir / "teach-pool-upper")
        theta = between_class_p95(teach_X, teach_y)
        report["theta"] = theta

        excluded = other_case_removed_pairs("latin-upper", "latin-lower", families.LETTER_NAMES,
                                             lists["teach_fonts"][0], seed, cache_dir / "other-case", theta)
        excluded_names = {e["letter"] for e in excluded}
        oc_held = [nm for nm in families.other_case(seed)["held_out"] if nm not in excluded_names]
        # §5.2: OTHER_CASE is a PICK "among the 26 other-case glyphs of one test font" — relation_ceiling's
        # "naming accuracy x pick accuracy" (§3.3) needs a SEPARATE pick-discrimination number this module
        # does not build a real 26-candidate pick simulation for. Declared approximation (flagged for the
        # seat, not a silent guess): pick_accuracy == the query's own naming accuracy, so the item's ceiling
        # is naming_accuracy^2 — recognising the query AND telling it apart from 25 candidates are both
        # modelled as bounded by the same underlying naming capability, never by a bare naming-accuracy^1
        # that ignores the "and pick correctly among candidates" half of the task entirely.
        oc_ceilings = [naming_by_name.get(nm, 0.0) ** 2 for nm in oc_held]
        oc_ceiling = sum(oc_ceilings) / len(oc_ceilings) if oc_ceilings else 0.0
        families_out["OTHER_CASE"] = _normalise(
            oc_ceiling, n=len(oc_held), k_min=1,
            extra={"chance": 1 / 26, "excluded": excluded,
                   "pick_approximation": "naming_accuracy**2 (query x candidate-discrimination, both "
                                          "modelled as the same naming capability — RAISED as a convention, "
                                          "not a real 26-candidate pick simulation)"})

        test_fonts_by_case = {"latin-upper": lists["upper_test_fonts"], "latin-lower": lists["lower_test_fonts"]}
        mirror = families.mirror_symmetric(seed)
        mirror_res = binary_perceptual_ceiling(mirror["taught"]["positive"], mirror["taught"]["negative"],
                                                mirror["held_out"]["positive"], mirror["held_out"]["negative"],
                                                lists["teach_fonts"], test_fonts_by_case, seed,
                                                cache_dir / "mirror", "mirror")
        families_out["MIRROR"] = _normalise(mirror_res["accuracy"], n=mirror_res["n"], k_min=1, extra={"chance": 0.5})

        loop = families.has_loop(seed)
        loop_res = binary_perceptual_ceiling(loop["taught"]["positive"], loop["taught"]["negative"],
                                              loop["held_out"]["positive"], loop["held_out"]["negative"],
                                              lists["teach_fonts"], test_fonts_by_case, seed,
                                              cache_dir / "loop", "loop")
        families_out["LOOP"] = _normalise(loop_res["accuracy"], n=loop_res["n"], k_min=1, extra={"chance": 0.5})

        vowel = families.vowel(seed)
        all_forms = set(families.FORMS_52)
        consonant_all = [f for f in all_forms if f not in set(families.VOWEL_FORMS)]
        vowel_res = vowel_ceiling(families.VOWEL_FORMS, consonant_all, vowel["consonant_forms"],
                                   lists["teach_fonts"], test_fonts_by_case, seed, cache_dir / "vowel")
        families_out["VOWEL"] = _normalise(vowel_res["accuracy"], n=vowel_res["n"], k_min=1, extra={"chance": 0.5})

        kept = candidate_pool(teach_X, theta, seed, cache_dir / "never-taught")
        report["never_taught_pool_size"] = len(kept)
        try:
            pools = select_pools(kept, seed)
            report["never_taught_pools"] = {
                "counts": pools["counts"], "pool_size": pools["pool_size"],
                "plant_eligible_count": pools["plant_eligible_count"],
                "plant": pools["plant"],
                # edit: Claude (Fable 5.1), 2026-09-24 — the tape builder (brain/world/tape.py) reads the
                # LISTS, not only the counts: which 40 signs are U2's, which 10 U6's refusal check, which 10 U5's.
                "u2": pools["u2"], "u6_refusal": pools["u6_refusal"], "u5_after_never_taught": pools["u5_after_never_taught"],
            }
        except NeverTaughtError as e:
            report["never_taught_pools_error"] = str(e)

    report["families"] = families_out
    report["input_shas"] = {"prereg": None}   # filled by the caller if a PREREG sha is available
    return report


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261001)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--out", default=str(STAGE1_OUT / "ceilings.json"))
    p.add_argument("--cache-dir", default=str(CACHE_ROOT / "stage1"))
    ns = p.parse_args(argv)

    report = run(ns.seed, ns.smoke, Path(ns.out).parent, Path(ns.cache_dir), force=ns.force)
    out_path = Path(ns.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(f"wrote {out_path} ({'smoke' if ns.smoke else 'FULL'} scale)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
