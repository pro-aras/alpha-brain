# edit: Claude (Fable 5.1), 2026-09-24 18:17 +0400 — the schedule's counts test (B1-PREREG.md §2.7: "a unit test recomputes them
# from the counts above"), its identity, its sleep placement (R16), KEEPS' fonts (§2.2), the probes' fonts (R14),
# every row's shape under the frozen validator, the U6 gap, the MLC rules (R19) and the raised inputs (§11).
# Pure — no rendering, runs under either interpreter in about a second.
from __future__ import annotations

import unittest
from typing import Dict, List

from brain.protocol import make_row, validate_tape_row, verify_row
from brain.world import schedule as S
from brain.world.families import LETTER_NAMES

SEED = 20261001


def _cand(script: str, ch: str, font: str) -> Dict[str, object]:
    return {"script": script, "char": ch, "font": font, "n_fonts_available": 12}


def _pools(n_u2: int = 40, n_u6: int = 10, n_u5: int = 10) -> Dict[str, object]:
    return {"u2": [_cand("greek", f"g{i}", "GF.ttf") for i in range(n_u2)],
            "u6_refusal": [_cand("hebrew", f"h{i}", "HF.ttf") for i in range(n_u6)],
            "u5_after_never_taught": [_cand("arabic", f"a{i}", "AF.ttf") for i in range(n_u5)],
            "plant": _cand("greek", "Ж", "GF.ttf")}


def _world(nu: int = 15, nl: int = 12, nd: int = 17, excluded: List[str] = None, pools=None, plant_fonts=None) -> S.WorldInputs:
    return S.WorldInputs(teach_fonts=["T1", "T2", "T3", "T4"],
                         test_fonts={"latin-upper": [f"U{i}" for i in range(nu)], "latin-lower": [f"L{i}" for i in range(nl)],
                                     "digits": [f"D{i}" for i in range(nd)]},
                         pools=pools or _pools(), plant_fonts=plant_fonts or [f"P{i}" for i in range(11)],
                         other_case_excluded=list(excluded or []))


def _resolve(rows: List[dict]) -> List[dict]:
    """Substitute rendering ids by a stable int (their first-use index) so the FROZEN validator can run."""
    ids: Dict[str, int] = {}

    def r(x: str) -> int:
        return ids.setdefault(x, len(ids))

    out = []
    for row in rows:
        p = dict(row["payload"])
        if row["kind"] == "TEACH":
            p["glance_row"] = r(p["glance_row"])
        elif row["kind"] == "ASK":
            p["operands"] = [({"kind": "row", "value": r(op["value"])} if op["kind"] == "row" else dict(op)) for op in p["operands"]]
            p["candidate_rows"] = [r(x) for x in p["candidate_rows"]] if p["candidate_rows"] else None
        out.append(make_row(row["seq"], row["kind"], row["phase"], row["item"], p))
    return out


class TestCounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.s = S.build(SEED, _world())
        cls.e = S.expected_counts()
        cls.smoke = S.build(SEED, _world(3, 3, 3), S.SMOKE)
        cls.esmoke = S.expected_counts(n_test_fonts_upper=3, n_test_fonts_lower=3, p=S.SMOKE)

    def _check(self, s: S.Schedule, e: Dict[str, object]) -> None:
        c = s.counts
        for k in ("TEACH", "ASK", "FEEDBACK", "ARRIVAL", "TEST_BEGIN", "TEST_END"):
            self.assertEqual(c["kinds"].get(k), e[k], k)
        for fam, n in e["L4_episodes"].items():
            self.assertEqual(c["episodes"].get(f"L4:{fam}"), n, f"L4 {fam}")
        self.assertEqual(c["episodes"].get("L5:TWO_AFTER"), e["L5_episodes"])
        self.assertEqual(c["episodes"].get("L6:CONST", 0), e["L6_episodes"])   # R47: 0 since B1.1
        for sit in ("T_L", "T_D"):
            for fam, n in e["letter_block"].items():
                self.assertEqual(c["asks"].get(f"{sit}:{fam}"), n, f"{sit} {fam}")
        for fam, n in e["T_L_only"].items():
            self.assertEqual(c["asks"].get(f"T_L:{fam}"), n, f"T_L {fam}")
        for fam, n in e["T_D_only"].items():
            self.assertEqual(c["asks"].get(f"T_D:{fam}"), n, f"T_D {fam}")
        for k in range(1, len(s.notes["params"]["probe_after_rounds"]) + 1):
            self.assertEqual(c["asks"].get(f"P{k}:TWO_AFTER"), e["probe_asks_each"], f"P{k}")
        self.assertEqual(c["mlc"]["episodes"], e["mlc_episodes"])
        self.assertEqual(c["mlc"]["relation_episodes_in_L4"], e["mlc_relation_episodes"])
        self.assertEqual(c["mlc"]["rows"], e["mlc_episodes"] * (S.MLC_K + S.MLC_Q) * 2)

    def test_prereg_counts_match_the_formulas(self) -> None:
        self._check(self.s, self.e)
        self.assertTrue(self.s.notes["params_are_prereg"])

    def test_smoke_counts_match_the_formulas(self) -> None:
        self._check(self.smoke, self.esmoke)
        self.assertFalse(self.smoke.notes["params_are_prereg"])

    def test_headline_prereg_numbers(self) -> None:
        # §2.7's own sentences, as numbers: 12 showings per letter (3 per font), zog once, digits 12 rounds.
        teach = [r for r in self.s.rows if r["kind"] == "TEACH"]
        by_name: Dict[str, int] = {}
        for r in teach:
            by_name[r["payload"]["name"]] = by_name.get(r["payload"]["name"], 0) + 1
        self.assertEqual(by_name["zog"], 1)
        for nm in LETTER_NAMES:
            self.assertEqual(by_name[nm], 24)      # 12 upper + 12 lower
        self.assertEqual(by_name["seven"], 12)
        self.assertGreaterEqual(self.s.notes["u6_gap_events"], 3000)   # §5.3 U6: "≈ 3,000 events of other learning later"

    def test_other_case_exclusion_shrinks_only_other_case(self) -> None:
        held = self.s.notes["other_case"]["held_out_graded"]
        taught = self.s.notes["other_case"]["taught"]
        s2 = S.build(SEED, _world(excluded=[held[0], taught[0]]))
        e2 = S.expected_counts(n_other_case_held=12, n_other_case_taught=12)
        self._check(s2, e2)
        self.assertNotIn(held[0], s2.notes["other_case"]["held_out_graded"])
        self.assertEqual(s2.counts["asks"]["T_L:CHAIN"], self.s.counts["asks"]["T_L:CHAIN"])   # R17: CHAIN keeps all 25


class TestB11NoBlockBeforeASitting(unittest.TestCase):
    """edit: Claude (Opus 5.5), 2026-09-27 15:05 +0400 — R47 (B1.1). The L6 block taught CONST («a», 78 corrections) between the last
    SLEEP and T_L, and phase D carries no correction, so it was the last thing corrected before T_L AND T_D: the networks
    answered «a» to every T_L letter. CONST's training asks now join L4's interleave exactly as SAME's; L6 is gone. The
    guard, declared in R47 before the change: before EVERY sitting the last 100 corrections carry >= 10 distinct answers
    and none above 50 %."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.s = S.build(SEED, _world())

    @staticmethod
    def _last_corrections(s: S.Schedule, before_seq: int, n: int = 100) -> List[str]:
        fb = [r for r in s.rows if r["kind"] == "FEEDBACK" and r["seq"] < before_seq]
        return [r["payload"]["right"] for r in fb[-n:]]

    def test_the_guard_holds_before_every_sitting(self) -> None:
        sittings = [r for r in self.s.rows if r["kind"] == "TEST_BEGIN"]
        self.assertEqual(len(sittings), 2 + len(S.PREREG.probe_after_rounds))
        for r in sittings:
            last = self._last_corrections(self.s, r["seq"])
            self.assertEqual(len(last), 100, r["payload"])
            top = max(last.count(a) for a in set(last))
            self.assertGreaterEqual(len(set(last)), 10, (r["payload"], sorted(map(str, set(last)))))   # `right` is a name or a PICK index
            self.assertLessEqual(top, 50, (r["payload"], top))

    def test_const_is_taught_in_L4_and_no_L6_phase_exists(self) -> None:
        self.assertNotIn("L6", {r["phase"] for r in self.s.rows})
        self.assertEqual(self.s.counts["episodes"].get("L4:CONST"), S.PREREG.control_taught_per_case * 2 * S.PREREG.control_reps)
        const_asks = [r for r in self.s.rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["CONST"] and r["phase"] == "L4"]
        self.assertEqual(len(const_asks), 78)
        self.assertEqual({r["payload"]["answer_kind"] for r in const_asks}, {"NAME"})

    def test_a_sleep_follows_every_const_training_ask_before_T_L(self) -> None:
        t_l = next(r["seq"] for r in self.s.rows if r["kind"] == "TEST_BEGIN" and r["phase"] == "T_L")
        last_const = max(r["seq"] for r in self.s.rows if r["kind"] == "ASK" and r["payload"]["cues"] == ["CONST"] and r["seq"] < t_l)
        self.assertTrue(any(last_const < q < t_l for q in self.s.sleep_seqs), (last_const, t_l))

    def test_const_is_spread_through_L4_not_a_block(self) -> None:
        """CONST's L4 training asks span most of L4 (a seeded interleave), and no more than 3 of them are adjacent
        among L4's corrections; the old L6 was one contiguous run of 78 outside L4."""
        l4 = [r for r in self.s.rows if r["kind"] == "ASK" and r["phase"] == "L4"]
        pos = [i for i, r in enumerate(l4) if r["payload"]["cues"] == ["CONST"]]
        self.assertEqual(len(pos), 78)
        self.assertGreaterEqual((pos[-1] - pos[0]) / len(l4), 0.5, (pos[0], pos[-1], len(l4)))
        run = best = 1
        for a, b in zip(pos, pos[1:]):
            run = run + 1 if b == a + 1 else 1
            best = max(best, run)
        self.assertLessEqual(best, 3, best)


class TestIdentityAndShape(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.s = S.build(SEED, _world())

    def test_built_twice_is_identical_and_another_seed_differs(self) -> None:
        s2 = S.build(SEED, _world())
        self.assertEqual(self.s.rows, s2.rows)
        self.assertEqual(self.s.truth_asks, s2.truth_asks)
        self.assertEqual(self.s.mlc_rows, s2.mlc_rows)
        self.assertEqual([r.item_id for r in self.s.renderings], [r.item_id for r in s2.renderings])
        s3 = S.build(SEED + 1, _world())
        self.assertEqual(len(s3.rows), len(self.s.rows))            # the counts never move with the seed (§2.8)
        self.assertNotEqual(self.s.notes["splits"]["after_before"]["held_out"], s3.notes["splits"]["after_before"]["held_out"])

    def test_every_row_passes_the_frozen_validator(self) -> None:
        rows = _resolve(self.s.rows)
        for row in rows:
            validate_tape_row(row)
            self.assertTrue(verify_row(row))
        self.assertEqual([r["seq"] for r in rows], list(range(1, len(rows) + 1)))

    def test_rendering_ids_are_unique_and_all_referenced(self) -> None:
        ids = [r.item_id for r in self.s.renderings]
        self.assertEqual(len(ids), len(set(ids)))
        used = set()
        for row in self.s.rows:
            p = row["payload"]
            if row["kind"] == "TEACH":
                used.add(p["glance_row"])
            elif row["kind"] == "ASK":
                used.update(op["value"] for op in p["operands"] if op["kind"] == "row")
                used.update(p["candidate_rows"] or [])
        for row in self.s.mlc_rows:
            if row["kind"] == "ASK":
                used.update(op["value"] for op in row["payload"]["operands"])
        self.assertEqual(used, set(ids))

    def test_sleep_placement_R16(self) -> None:
        in_sit, pend = False, None
        whys = []
        for r in self.s.rows:
            k = r["kind"]
            if k == "TEST_BEGIN":
                in_sit = True
            elif k == "TEST_END":
                in_sit = False
            elif k == "SLEEP":
                self.assertFalse(in_sit, f"SLEEP inside a sitting at seq {r['seq']}")
                self.assertIsNone(pend, f"SLEEP between an ASK and its FEEDBACK at seq {r['seq']}")
                whys.append(r["payload"]["why"])
                self.assertEqual(r["payload"]["steps"], S.SLEEP_STEPS)
            elif k == "ASK" and not in_sit:
                pend = r["seq"]
            elif k == "FEEDBACK":
                self.assertEqual(r["payload"]["ask_seq"], pend)
                pend = None
        for must in ("after L1", "after L2", "after L4", "after D") + tuple(f"after L5 round {i}" for i in range(1, 7)):
            self.assertIn(must, whys)
        self.assertNotEqual(self.s.rows[-1]["kind"], "SLEEP")
        # a periodic sleep never lets more than the period pass outside a sitting
        since, in_sit = 0, False
        for r in self.s.rows:
            if r["kind"] == "TEST_BEGIN":
                in_sit = True
            if r["kind"] == "TEST_END":
                in_sit = False
            if r["kind"] == "SLEEP":
                since = 0
            else:
                since += 1
                if not in_sit and r["kind"] in ("FEEDBACK", "TEACH"):
                    self.assertLessEqual(since, S.PREREG.periodic_sleep_every + 1)

    def test_keeps_reasks_the_same_items_in_the_same_fonts_with_new_renderings(self) -> None:
        tl = {(t["item"], t["class"], str(t["font"])): t for t in self.s.truth_asks if t["sitting"] == "T_L"
              and t["family"] in ("U1a_NAME", "AFTER", "BEFORE", "BETWEEN", "TWO_AFTER", "OTHER_CASE", "CHAIN", "MIRROR", "LOOP", "VOWEL")}
        td = [t for t in self.s.truth_asks if t["sitting"] == "T_D" and t["family"] in
              ("U1a_NAME", "AFTER", "BEFORE", "BETWEEN", "TWO_AFTER", "OTHER_CASE", "CHAIN", "MIRROR", "LOOP", "VOWEL")]
        self.assertEqual(len(td), len(tl))
        for t in td:
            key = (t["item"], t["class"], str(t["font"]))
            self.assertIn(key, tl, f"T_D item without its T_L twin: {key}")
            self.assertEqual(tl[key]["answer"], t["answer"])
            self.assertNotEqual(set(tl[key]["rendering"]), set(t["rendering"]))   # NEW renderings

    def test_probes_use_the_T_L_fonts_R14(self) -> None:
        tl: Dict[tuple, List[str]] = {}
        for t in self.s.truth_asks:
            if t["sitting"] == "T_L" and t["family"] == "TWO_AFTER":
                tl.setdefault((t["item"], t["class"]), []).append(str(t["font"]))
        tl = {k: sorted(v) for k, v in tl.items()}
        for k in ("P1", "P2", "P3", "P4"):
            pk = {}
            for t in self.s.truth_asks:
                if t["sitting"] == k:
                    pk.setdefault((t["item"], t["class"]), []).append(str(t["font"]))
            self.assertEqual(len(pk), 42)
            for key, fonts in pk.items():
                self.assertEqual(sorted(fonts), tl[key])

    def test_disjoint_by_construction_and_same_ref_shares_rows(self) -> None:
        teach_ids = {r["payload"]["glance_row"] for r in self.s.rows if r["kind"] == "TEACH"}
        in_sit = False
        for r in self.s.rows:
            if r["kind"] == "TEST_BEGIN":
                in_sit = True
            elif r["kind"] == "TEST_END":
                in_sit = False
            elif r["kind"] == "ASK" and in_sit:
                used = {op["value"] for op in r["payload"]["operands"] if op["kind"] == "row"} | set(r["payload"]["candidate_rows"] or [])
                self.assertFalse(used & teach_ids)
        same = {t["item"].split(":")[1] + ":" + t["item"].split(":")[2]: t["rendering"] for t in self.s.truth_asks if t["family"] == "CONTROL_SAME"}
        ref = {t["item"].split(":")[1] + ":" + t["item"].split(":")[2]: t["rendering"] for t in self.s.truth_asks if t["family"] == "SAME_NAME_REF"}
        self.assertEqual(same, ref)

    def test_mlc_rules_R19(self) -> None:
        mlc = [t for t in self.s.truth_asks if t.get("mlc")]
        for t in mlc:
            x, y = t["pair"]
            self.assertNotIn(abs(LETTER_NAMES.index(y) - LETTER_NAMES.index(x)), S.MLC_FORBIDDEN_DIFFS)
        seq_kind = {r["seq"]: (r["kind"], r["phase"], r["item"]) for r in self.s.rows}
        for row in self.s.mlc_rows:
            k, ph, item = seq_kind[row["after_seq"]]
            self.assertEqual((k, ph), ("FEEDBACK", "L4"))
            self.assertTrue(any(item.startswith(f + ":") for f in S.RELATION_TRAINING_FAMILIES), item)
            if row["kind"] == "ASK":
                self.assertEqual(row["payload"]["cues"], [f"MLC{row['episode'] % S.MLC_SLOTS}"])
        rules = self.s.notes["mlc_rules"]
        self.assertTrue(all(r["rule"].get("k") in (None, 3, 4, 5) for r in rules))
        self.assertGreater(sum(1 for r in rules if r["rule"]["kind"] == "permutation"), 0)

    def test_canary_answers_come_from_the_declared_generator(self) -> None:
        begin = next(r for r in self.s.rows if r["kind"] == "TEST_BEGIN" and r["payload"]["sitting"] == "T_L")
        purpose = begin["payload"]["canary_purpose"]
        rng = S.substream(SEED, purpose)
        want = [LETTER_NAMES[int(rng.integers(0, 26))] for _ in range(S.PREREG.canary_asks)]
        got = [t["answer"] for t in self.s.truth_asks if t["family"] == "CONTROL_CANARY"]
        self.assertEqual(got, want)


class TestRaises(unittest.TestCase):
    def test_short_pool_is_raised_never_padded(self) -> None:
        with self.assertRaises(S.ScheduleError):
            S.build(SEED, _world(pools=_pools(n_u2=39)))
        with self.assertRaises(S.ScheduleError):
            S.build(SEED, _world(plant_fonts=[f"P{i}" for i in range(10)]))
        with self.assertRaises(S.ScheduleError):
            S.build(SEED, _world(nu=2))


if __name__ == "__main__":
    unittest.main()
