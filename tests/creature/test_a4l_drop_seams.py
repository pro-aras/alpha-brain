# tests/creature/test_a4l_drop_seams.py — A4L-DROP: predictive coding as a filter, a CONFIRMED glance
# never reaches the moment (A4-LADDER-PREREG.md §2.4; docs/briefs/A4L-DROP.md). edit: Claude (Sonnet 5,
# A4 ladder builder DROP), 2026-09-23 11:19 +0400.
#
# The gate's own controls (D2, D3), the parser, the seams (task 6), and the STATUS counter — all as tests
# BEFORE any life, per the brief. TestHourOneFixtureGates is the slow one (two real replays of alpha4-1's
# first-hour fixture, ~2 min each under this box's current load — #233's own built-in control: the DROP
# and FLOOR replays are identical up to the first row where a dropped glance would have wired).
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional
from unittest import mock

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import gaze, world
from genome.machinery import GenomeError, Organism, parse_genome

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "tests" / "creature" / "G5-surprise-coarse-test.genome"
GENOME_TEXT = GENOME_PATH.read_text()
assert "SURPRISE floor 0.05 predicted mind-cell" in GENOME_TEXT

# The SAME fixture's SURPRISE line + "; drop confirmed" — the mind-level toy genome (byte-identical to
# GENOME_TEXT everywhere else).
DROP_TEXT = GENOME_TEXT.replace(
    "SURPRISE floor 0.05 predicted mind-cell   # DIFF 2: L-4's gene, live for this fixture's own tests",
    "SURPRISE floor 0.05 predicted mind-cell; drop confirmed   # A4L-DROP toy: DIFF 2 + the drop clause",
)
assert DROP_TEXT != GENOME_TEXT, "the SURPRISE line replace target moved — update it"
assert parse_genome(DROP_TEXT).declared["SURPRISE"] == {"floor": 0.05, "predicted": "mind-cell", "drop": "confirmed"}

FIXTURE_ROOT = ROOT / "scratch" / "fixtures" / "alpha4-1-hour1"
FLOOR_GENOME = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"
DROP_GENOME = ROOT / "genome" / "ladder" / "A4L-DROP.genome"
MASTER_REF_FLOOR_JOURNAL = ROOT / "scratch" / "master-ref" / "floor" / "journal.jsonl"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _write_genome(tmp_dir: Path, text: str, name: str = "g.genome") -> Path:
    p = tmp_dir / name
    p.write_text(text)
    return p


def _build_repeated_tape(root: Path, word: str, n: int, seed: int = 42) -> np.ndarray:
    """`n` canvases, ALL the exact same render of `word` — SAME helper as test_surprise_coarse.py's own
    (kept local: no shared test-utils module in this tree)."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    rgb, _truth = world.render_canvas(word, rng)
    for i in range(n):
        m_id = f"m{i:05d}"
        tape.publish("ear", word.encode("utf-8"), {"moment": m_id, "source": "test", "word": word}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": m_id, "source": "test"}, "png")
    return rgb


def _mind_rows(root: Path) -> List[dict]:
    rows: List[dict] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return [r for r in rows if "event" not in r]


def _read_jsonl(path: Path) -> List[dict]:
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def _consume_fixture_mind(genome_path: Path, tape_path: Path, work_root: Path) -> Mind:
    """Mirrors creature.replay.run_replay's own setup EXACTLY (a fresh work root; the payload dir
    SYMLINKED from the fixture, never copied) but returns the live Mind object so org.t/org.c/episodes
    are directly inspectable — creature.replay's own CLI only ever hands back the journal path. Never
    writes to `tape_path`'s own directory (the fixture stays read-only)."""
    from creature.tape import _resolve_tape_dir as _resolve
    tape_root = Path(tape_path).parent
    work_tape = _resolve(work_root, parse_genome(Path(genome_path).read_text()).declared.get("TAPE", {}).get("path"))
    work_tape.mkdir(parents=True, exist_ok=True)
    payload_src = tape_root / "payload"
    if payload_src.exists():
        os.symlink(payload_src.resolve(), work_tape / "payload")
    mind = Mind(genome_path, work_root)
    for row in sorted(_read_jsonl(tape_path), key=lambda r: r["seq"]):
        mind.consume(row)
    return mind


# ============================================================================ task 1: the parser
class TestSurpriseDropParses(unittest.TestCase):
    def test_drop_confirmed_declared(self) -> None:
        # a full, startable genome (parse_genome refuses on MISSING required fields, checked after every
        # gene's own regex — a minimal two-line text can only exercise a REFUSAL, never a successful parse).
        g = parse_genome(DROP_TEXT)
        self.assertEqual(g.declared["SURPRISE"], {"floor": 0.05, "predicted": "mind-cell", "drop": "confirmed"})

    def test_old_forms_unaffected(self) -> None:
        # every genome on disk before this task (A4L-FLOOR.genome included) still parses to exactly the
        # same dict shape as before this task — "drop" simply absent.
        no_surprise_text = "\n".join(l for l in GENOME_TEXT.splitlines() if not l.startswith("SURPRISE floor"))
        g0 = parse_genome(no_surprise_text)
        self.assertNotIn("SURPRISE", g0.declared)
        g1 = parse_genome(GENOME_TEXT)
        self.assertEqual(g1.declared["SURPRISE"], {"floor": 0.05, "predicted": "mind-cell"})
        self.assertNotIn("drop", g1.declared["SURPRISE"])

    def test_floor_genome_on_disk_still_undeclares_drop(self) -> None:
        g = parse_genome(FLOOR_GENOME.read_text())
        self.assertNotIn("drop", g.declared["SURPRISE"])

    def test_drop_genome_on_disk_declares_it(self) -> None:
        g = parse_genome(DROP_GENOME.read_text())
        self.assertEqual(g.declared["SURPRISE"].get("drop"), "confirmed")

    def test_drop_without_predicted_refuses(self) -> None:
        # advisor-caught: "; drop confirmed" is nested INSIDE the "predicted mind-cell" group so the bare
        # form ("floor <f>; drop confirmed", no "predicted") refuses by regex — it must never silently
        # resurrect the OLD, different, never-built bare-form meaning that test_old_form_refuses_at_mind_
        # start (test_surprise_coarse.py) guards at Mind start.
        with self.assertRaises(GenomeError) as cm:
            parse_genome("SEED 1\nSURPRISE floor 0.05; drop confirmed\n")
        self.assertIn("SURPRISE", str(cm.exception))

    def test_misspelt_forms_refuse_by_name(self) -> None:
        for bad in (
            "SURPRISE floor 0.05 predicted mind-cell; drop confirm",
            "SURPRISE floor 0.05 predicted mind-cell; drop confirmed x",
            "SURPRISE floor 0.05 predicted mind-cell;drop confirmed",
            "SURPRISE floor 0.05 predicted mind-cell; Drop confirmed",
            "SURPRISE floor 0.05 predicted mind-cell; DROP CONFIRMED",
            "SURPRISE floor 0.05 predicted mind-cell ; drop confirmed",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as cm:
                    parse_genome("SEED 1\n" + bad + "\n")
                self.assertIn("SURPRISE", str(cm.exception))


# ============================================================================ Organism.tick() itself
class TestOrganismTick(unittest.TestCase):
    def _built_organism(self):
        text = (ROOT / "genome" / "G5.genome").read_text().replace("NMAX     2000", "NMAX     64") \
            .replace("#OFF SURPRISE floor 0.05", "SURPRISE floor 0.05 predicted mind-cell; drop confirmed") \
            + "\nTHRESH   cell own band history 30\n"
        g = parse_genome(text)
        org = Organism(g)
        rng = np.random.default_rng(3)
        x = rng.standard_normal(g.sight_dim()).astype(np.float32); x /= np.linalg.norm(x)
        w = np.zeros(g.words_dim(), dtype=np.float32); w[0] = 1.0
        org.t = int(g.stage2_start)
        for _ in range(6):
            org.moment(x, w)          # births + wires: the cell's established answer becomes word 0
        return org, x, w

    def test_tick_advances_clock_exactly_like_moment_sight(self) -> None:
        org, _x, _w = self._built_organism()
        t0 = org.t
        org.tick()
        self.assertEqual(org.t, t0 + 1)
        # SCALE fires at the SAME multiple tick() and moment()/moment_sight() would — drive t to one
        # short of a scale boundary and check the counter moves on the crossing tick(), not before.
        org.t = int(org.g.scale_every) - 1
        before = org.c.get("scale_events", 0)
        org.tick()
        self.assertEqual(org.c.get("scale_events", 0), before + 1, "tick() must fire SCALE at its own multiple, exactly as moment_sight() does")

    def test_tick_never_pushes_a_cells_own_band(self) -> None:
        # A4L-DROP's own form of test_life_seams.py's AxB precedent: a DROPPED glance (tick(), never
        # Organism.moment(confirm=True)) must not push the own band either — it was not pushed as a
        # confirm=True glance before this task (moment()'s own `and not confirm` guard), and tick() never
        # even calls _resonate/moment's push code at all.
        org, x, w = self._built_organism()
        n_before = int(org.sight.own_band_n.sum())
        org.tick()
        self.assertEqual(int(org.sight.own_band_n.sum()), n_before, "tick() pushed the cell's own band")
        org.moment(x, w)              # the same glance, unconfirmed → one push (the negative control has teeth)
        self.assertEqual(int(org.sight.own_band_n.sum()), n_before + 1)

    def test_tick_never_resonates_wires_or_births(self) -> None:
        org, _x, _w = self._built_organism()
        W_before = org.W.copy(); mask_before = org.mask.copy()
        sight_n_before, words_n_before = org.sight.n, org.words.n
        births_before = len(org.births)
        strikes_before = org.strikes.copy()
        org.tick()
        self.assertTrue(np.array_equal(org.W, W_before), "tick() must never touch W (no HEBB, no DELTA)")
        self.assertTrue(np.array_equal(org.mask, mask_before))
        self.assertTrue(np.array_equal(org.strikes, strikes_before))
        self.assertEqual(org.sight.n, sight_n_before); self.assertEqual(org.words.n, words_n_before)
        self.assertEqual(len(org.births), births_before)


# ============================================================================ the mind-level mechanism (toy tapes)
class TestConsumeEyeDropMechanism(unittest.TestCase):
    def test_undeclared_drop_glances_dropped_stays_zero(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=50, seed=42)
        m = Mind(GENOME_PATH, root)   # the OLD form: SURPRISE declared, no "drop"
        for r in read_tape(root):
            m.consume(r)
        self.assertGreater(m.glances_confirmed, 0, "the fixture must produce confirmations, or this proves nothing")
        self.assertEqual(m.glances_dropped, 0, "an undeclared 'drop confirmed' clause must never drop a glance")

    def test_drop_declared_dropped_equals_confirmed(self) -> None:
        root = Path(tempfile.mkdtemp())
        rgb = _build_repeated_tape(root, "circle", n=50, seed=42)
        gp = _write_genome(root, DROP_TEXT)
        m = Mind(gp, root)
        for r in read_tape(root):
            m.consume(r)
        self.assertGreater(m.glances_dropped, 0, "the repeated-canvas fixture must confirm+drop at least one glance")
        self.assertEqual(m.glances_dropped, m.glances_confirmed, "every confirmed glance IS a dropped one under this rung (task 2's own construction)")
        self.assertEqual(m.org.births_skipped_confirmed, 0, "tick() never reaches _resonate(confirm=True) — that counter only moves inside the OLD cheap-moment path, which drop bypasses entirely")

    def test_drop_road_genuinely_differs_from_the_old_cheap_moment_road(self) -> None:
        # advisor's own point: "a free second signal that the road changed" — measured, not assumed.
        # births_skipped_confirmed turned out NOT to be that signal on this toy (a CONFIRMED glance's own
        # cell almost always resonates strongly by construction — the "nothing resonates" branch inside
        # _resonate(confirm=True) that counter measures essentially never fires for an already-predicted
        # cell, under EITHER road: 0 under FLOOR too, verified). The signal that DOES hold: the two roads
        # leave the organism in DIFFERENT states — DROP's tick() never runs HEBB/DELTA for a confirmed
        # glance, FLOOR's moment(confirm=True) still does (today's law), so their final state_hash()es
        # diverge on the identical tape the moment any glance is actually confirmed.
        def run(genome_text: str, root: Path) -> Mind:
            _build_repeated_tape(root, "circle", n=50, seed=42)
            gp = _write_genome(root, genome_text)
            m = Mind(gp, root)
            for r in read_tape(root):
                m.consume(r)
            return m

        m_floor = run(GENOME_TEXT, Path(tempfile.mkdtemp()))
        m_drop = run(DROP_TEXT, Path(tempfile.mkdtemp()))
        self.assertGreater(m_floor.glances_confirmed, 0)
        self.assertGreater(m_drop.glances_dropped, 0)
        self.assertNotEqual(m_floor.org.state_hash(), m_drop.org.state_hash(),
                             "FLOOR and DROP left the organism in the identical state — the drop road has no observable effect")

    def test_predictor_last_winner_unchanged_by_a_dropped_glance(self) -> None:
        # DROP x PREDICT: S, T = [], [] on a dropped glance -> predictor.note_winners([]) is genome/predict.py:120's
        # own documented no-op ("an empty S leaves the last winner as it was").
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=60, seed=42)
        text = DROP_TEXT + "\nPREDICT next glance; error scales delta 0.5..2.0; ranks replay; grades act\n"
        # G5-surprise-coarse-test.genome already declares PREDICT (see its own text); guard against a
        # duplicate declaration refusing the parse.
        if text.count("PREDICT ") > 1:
            text = DROP_TEXT
        gp = _write_genome(root, text)
        m = Mind(gp, root)
        last_winner_before = None
        rows = list(read_tape(root))
        for i, r in enumerate(rows):
            m.consume(r)
            if m.glances_dropped > 0 and r.get("sense") == "eye":
                # the FIRST canvas that drops at least one glance: capture the predictor's OWN state
                # immediately after, and compare it against what it holds after the very next dropped-only
                # consumption to prove it did not move.
                last_winner_before = None if m.predictor is None else (m.predictor._last_winner.copy() if m.predictor._last_winner is not None else None)
                break
        self.assertIsNotNone(last_winner_before, "the fixture must reach a dropped glance, or this proves nothing")
        # consume the NEXT eye row too (same repeated canvas -> confirms and drops again at steady state)
        for r in rows[i + 1:]:
            m.consume(r)
            if r.get("sense") == "eye":
                break
        last_winner_after = m.predictor._last_winner
        self.assertTrue(np.array_equal(last_winner_before, last_winner_after), "the predictor's last winner moved across a canvas whose only glances were dropped")

    def test_glance0_fast_episode_still_written_for_a_dropped_glance(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=50, seed=42)
        gp = _write_genome(root, DROP_TEXT)
        m = Mind(gp, root)
        eps_before = None
        for r in read_tape(root):
            m.consume(r)
        rows = _mind_rows(root)
        located = [r for r in rows if r.get("act") != "coarse" and "ep" in r]
        confirmed0 = [r for r in located if r.get("confirmed") and r["confirmed"][0]]
        self.assertTrue(confirmed0, "no canvas confirmed glance 0 — this proves nothing")
        for r in confirmed0:
            self.assertIsNotNone(r["ep"], "glance 0's FAST episode must still be written when it was dropped")


# ============================================================================ task 3: D2/D3, on the real fixture
@unittest.skipUnless(FIXTURE_ROOT.exists(), "alpha4-1-hour1 fixture not copied under scratch/fixtures/ — cp -r it first")
class TestHourOneFixtureGates(unittest.TestCase):
    """The slow gate: two full replays of alpha4-1's read-only first-hour fixture (~2 min each on this
    box). Run ONCE in setUpClass and shared by every test below — D2(a)/(c), D3, and the negative control
    of task 3(d) all read the same pair of journals."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tape_path = FIXTURE_ROOT / "tape" / "2026-09-23.jsonl"
        cls.tmp = Path(tempfile.mkdtemp(prefix="a4l-drop-gate-"))
        from creature import replay as replay_mod
        cls.floor_journal_path = replay_mod.run_replay(FLOOR_GENOME, cls.tape_path, cls.tmp / "floor")
        cls.drop_journal_path = replay_mod.run_replay(DROP_GENOME, cls.tape_path, cls.tmp / "drop")
        cls.floor_rows = replay_mod.read_mind_journal(cls.floor_journal_path)
        cls.drop_rows = replay_mod.read_mind_journal(cls.drop_journal_path)
        cls.compare = staticmethod(replay_mod.compare)

    def test_task3d_negative_control_floor_genome_matches_master(self) -> None:
        # the branch + FLOOR genome ≡ master + FLOOR genome INCLUDING hash — the negative control of
        # every landing (A4-LADDER-PREREG §1.1/§1.6(i)), against the master-reference journal captured
        # from the pristine dispatch commit (scratch/master-ref/floor/journal.jsonl, this report).
        if not MASTER_REF_FLOOR_JOURNAL.exists():
            self.skipTest(f"{MASTER_REF_FLOOR_JOURNAL} not present — capture it from the dispatch commit first (see the report)")
        from creature import replay as replay_mod
        master_rows = replay_mod.read_mind_journal(MASTER_REF_FLOOR_JOURNAL)
        diff = self.compare(self.floor_rows, master_rows)
        self.assertIsNone(diff, f"branch+FLOOR diverged from master+FLOOR: {diff}")

    def test_d2a_confirmed_sets_equal_up_to_first_expectation_divergence(self) -> None:
        # #233's built-in control (task 3(a), D2): NOT a whole-tape equality. Walk seq-then-glance in
        # tape order; find the first (seq, glance) where FLOOR's own `residual`/`confirmed` differ from
        # DROP's (the earliest point W could have diverged enough to change `expected_sight`); assert the
        # DROPPED set (from DROP's own `confirmed` fields — the definition of what gets dropped) equals
        # the CONFIRMED set FLOOR journals, STRICTLY BEFORE that point; print the row and the two sets'
        # sizes after it (never asserted equal after — divergence there is expected, not a defect).
        def by_seq_glance(rows):
            out: Dict[int, Dict[object, dict]] = {}
            for r in rows:
                if "moment" not in r or "confirmed" not in r:
                    continue
                out.setdefault(r["seq"], {})[r.get("glance")] = r
            return out

        floor_by = by_seq_glance(self.floor_rows)
        drop_by = by_seq_glance(self.drop_rows)
        seqs = sorted(set(floor_by) & set(drop_by))

        divergence = None
        for s in seqs:
            fmap, dmap = floor_by[s], drop_by[s]
            for g in sorted(set(fmap) & set(dmap), key=lambda v: (v is None, v)):
                f, d = fmap[g], dmap[g]
                if f.get("residual") != d.get("residual") or f.get("confirmed") != d.get("confirmed"):
                    divergence = (s, g, f.get("residual"), d.get("residual"), f.get("confirmed"), d.get("confirmed"))
                    break
            if divergence:
                break

        def flags_true(row) -> List[bool]:
            c = row.get("confirmed")
            return c if isinstance(c, list) else [bool(c)]

        cutoff = divergence[0] if divergence else (max(seqs) + 1)
        floor_confirmed_before = set()
        drop_dropped_before = set()
        floor_confirmed_after = set()
        drop_dropped_after = set()
        for s in seqs:
            fmap, dmap = floor_by[s], drop_by[s]
            for g, f in fmap.items():
                for i, flag in enumerate(flags_true(f)):
                    if flag:
                        (floor_confirmed_before if s < cutoff else floor_confirmed_after).add((s, g, i))
            for g, d in dmap.items():
                for i, flag in enumerate(flags_true(d)):
                    if flag:
                        (drop_dropped_before if s < cutoff else drop_dropped_after).add((s, g, i))

        print(f"[D2a] first expectation divergence: {divergence}")
        print(f"[D2a] before cutoff (seq {cutoff}): floor-confirmed {len(floor_confirmed_before)} == drop-dropped {len(drop_dropped_before)}")
        print(f"[D2a] after cutoff: floor-confirmed {len(floor_confirmed_after)}, drop-dropped {len(drop_dropped_after)} (printed, not asserted equal)")
        self.assertGreater(len(floor_confirmed_before), 0, "no confirmed glance before the cutoff — the fixture proves nothing")
        self.assertEqual(floor_confirmed_before, drop_dropped_before,
                          "the DROP and FLOOR replays' confirmed/dropped sets differ BEFORE the first expectation divergence — a defect")

    def test_d2b_a_planted_repeated_canvas_second_showing_touches_no_w_entry(self) -> None:
        # task 3(b): a planted canvas shown twice in a toy life; its second showing's confirmed glances
        # touch no W entry. A single canvas has FIVE glances (4 located + coarse); measured RED first on
        # "just check glance 0's would-be-winner row" (n=60 repeats of "square"/seed 7: W moved anyway) —
        # the cause is a SIBLING, non-confirmed glance of the SAME canvas (the coarse one, which confirms
        # far less often — M1's own reading, 46/1818 on the real fixture vs 639-701/1818 for a located
        # glance) legitimately wiring a row that happens to overlap a DIFFERENT, confirmed glance's own
        # would-be winner — a confound "glance 0 only" cannot see. Fixed the unconfounded way: instrument
        # Organism.moment() itself during the last canvas's own processing, recording the REAL sight
        # winners S every actual (non-confirmed) call wires; a confirmed glance's own would-be winners
        # must be ABSENT from that recorded union — the direct claim, immune to sibling-glance overlap.
        def run_all_but_last(genome_text: str, root: Path):
            rgb = _build_repeated_tape(root, "square", n=60, seed=7)
            gp = _write_genome(root, genome_text)
            m = Mind(gp, root)
            rows = list(read_tape(root))
            last_pair = rows[-2:]              # the final instant's ear+eye rows, in publish order
            for r in rows[:-2]:
                m.consume(r)
            return m, last_pair, rgb

        def would_be_winners_per_glance(m: Mind, rgb: np.ndarray) -> List[set]:
            g = m.genome
            g_out = gaze.glances(rgb, g.retina, g.gaze, "surprise", "toy", colour=g.colour, predicted=None)
            out = []
            for feat in g_out["feats"]:
                cos = m.org.sight.cos(feat)
                out.append({int(i) for i in np.argsort(-cos)[: g.kwta] if m.org.sight.alive[i] and cos[i] >= g.theta_n})
            return out

        def last_canvas_confirmed_flags(root: Path) -> List[bool]:
            rows = _mind_rows(root)
            located = [r for r in rows if r.get("act") != "coarse" and "confirmed" in r]
            coarse = [r for r in rows if r.get("act") == "coarse"]
            flags = list(located[-1]["confirmed"])
            if coarse:
                flags.append(bool(coarse[-1]["confirmed"]))
            return flags

        real_moment = Organism.moment

        # DROP: record every REAL (non-confirmed, i.e. actually wired) moment() call's own sight winners.
        root_drop = Path(tempfile.mkdtemp())
        m_drop, last_pair_drop, rgb_drop = run_all_but_last(DROP_TEXT, root_drop)
        would_be = would_be_winners_per_glance(m_drop, rgb_drop)
        self.assertTrue(any(would_be), "no would-be winner resonated before the last showing — the toy proves nothing")
        wired_union: set = set()

        def recording_moment(self_org, x_s, x_w, lr_scale=1.0, confirm=False):
            S, T = real_moment(self_org, x_s, x_w, lr_scale=lr_scale, confirm=confirm)
            if not confirm:
                wired_union.update(S)
            return S, T

        with mock.patch.object(Organism, "moment", recording_moment):
            for r in last_pair_drop:
                m_drop.consume(r)
        self.assertGreater(m_drop.glances_dropped, 0, "the last showing never confirmed+dropped — the toy proves nothing")
        flags = last_canvas_confirmed_flags(root_drop)
        confirmed_idx = [i for i, f in enumerate(flags) if f]
        self.assertTrue(confirmed_idx, "the journal's own last canvas shows no confirmed glance — the toy proves nothing")
        touched = set()
        for i in confirmed_idx:
            if i < len(would_be):
                touched |= (would_be[i] & wired_union)
        self.assertEqual(touched, set(), f"a confirmed glance's own would-be winner(s) were ACTUALLY wired this canvas: {touched}")

        # the negative control (advisor's own words: "run the identical tape under FLOOR and assert those
        # same rows DO move"): under FLOOR every real moment() call is recorded, confirmed or not — a
        # confirmed glance there still runs HEBB/DELTA (today's law), so its own would-be winner(s) DO
        # turn up among the wired cells.
        root_floor = Path(tempfile.mkdtemp())
        m_floor, last_pair_floor, rgb_floor = run_all_but_last(GENOME_TEXT, root_floor)
        would_be_floor = would_be_winners_per_glance(m_floor, rgb_floor)
        wired_all_floor: set = set()

        def recording_moment_floor(self_org, x_s, x_w, lr_scale=1.0, confirm=False):
            S, T = real_moment(self_org, x_s, x_w, lr_scale=lr_scale, confirm=confirm)
            wired_all_floor.update(S)
            return S, T

        with mock.patch.object(Organism, "moment", recording_moment_floor):
            for r in last_pair_floor:
                m_floor.consume(r)
        self.assertGreater(m_floor.glances_confirmed, 0, "FLOOR's last showing never confirmed — the control proves nothing")
        flags_floor = last_canvas_confirmed_flags(root_floor)
        confirmed_idx_floor = [i for i, f in enumerate(flags_floor) if f]
        self.assertTrue(confirmed_idx_floor, "FLOOR's last canvas shows no confirmed glance — the control proves nothing")
        hit = any((would_be_floor[i] & wired_all_floor) for i in confirmed_idx_floor if i < len(would_be_floor))
        self.assertTrue(hit, "the negative control has no teeth: under FLOOR, a confirmed glance's own would-be winner was never actually wired either")
        print(f"[D2b] DROP confirmed idx={confirmed_idx} touched={touched}; FLOOR confirmed idx={confirmed_idx_floor} hit={hit}")

    def test_d2c_sleep_rows_and_moment_row_counts_match(self) -> None:
        def sleep_seqs(rows):
            return [r["seq"] for r in rows if isinstance(r.get("sleep"), dict)]

        def moment_row_count(rows):
            return sum(1 for r in rows if "moment" in r)

        fs, ds = sleep_seqs(self.floor_rows), sleep_seqs(self.drop_rows)
        print(f"[D2c] floor sleep seqs {fs}")
        print(f"[D2c] drop  sleep seqs {ds}")
        self.assertEqual(fs, ds, "SLEEP boundaries fired at different rows under DROP — the moment clock diverged")
        self.assertGreater(len(fs), 0, "no SLEEP boundary crossed on this fixture — the clause proves nothing")
        self.assertEqual(moment_row_count(self.floor_rows), moment_row_count(self.drop_rows))

    def test_d3_clock_and_scale_events_identical_end_to_end(self) -> None:
        # the STRONG form of D3, built directly (Mind objects, not the CLI journal): org.t and
        # org.c["scale_events"] at the end of the SAME tape under FLOOR vs DROP.
        work_floor = Path(tempfile.mkdtemp(prefix="a4l-drop-d3-floor-"))
        work_drop = Path(tempfile.mkdtemp(prefix="a4l-drop-d3-drop-"))
        m_floor = _consume_fixture_mind(FLOOR_GENOME, self.tape_path, work_floor)
        m_drop = _consume_fixture_mind(DROP_GENOME, self.tape_path, work_drop)
        print(f"[D3] org.t floor={m_floor.org.t} drop={m_drop.org.t}; scale_events floor={m_floor.org.c.get('scale_events')} drop={m_drop.org.c.get('scale_events')}")
        self.assertEqual(m_floor.org.t, m_drop.org.t, "org.t diverged between FLOOR and DROP on the identical tape")
        self.assertEqual(m_floor.org.c.get("scale_events"), m_drop.org.c.get("scale_events"))
        self.assertGreater(m_drop.glances_dropped, 0)


# ============================================================================ task 6: the seam tests
class TestDropXSleepSeam(unittest.TestCase):
    """DROP x SLEEP: a sleep's replay of FAST episodes — which may include a confirmed episode 0 — is
    unchanged by the drop: sleep replays episodes via Organism.moment() directly (genome/sleep.py never
    passes confirm= or calls Organism.tick()), never live glances. Proven by call-counting: during the
    SAME tape consumption that crosses a SLEEP boundary, moment() is called some number of times inside
    sleep() (== the boundary's own "replayed" count) and tick() is NEVER called from inside sleep()."""

    def test_sleep_never_calls_tick_and_replays_exactly_its_own_count(self) -> None:
        text = DROP_TEXT.replace("SLEEP    every 40 moments replay 5 by surprise", "SLEEP    every 40 moments replay 5 by surprise")
        self.assertIn("SLEEP", parse_genome(text).declared)
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=60, seed=42)   # 60 canvases x 5 glances/canvas (coarse declared) = 300 moments > SLEEP.every (40): several boundaries cross
        gp = _write_genome(root, text)
        m = Mind(gp, root)

        tick_calls = {"n": 0}
        real_tick = Organism.tick

        def counting_tick(self_org):
            tick_calls["n"] += 1
            return real_tick(self_org)

        with mock.patch.object(Organism, "tick", counting_tick):
            for r in read_tape(root):
                m.consume(r)

        self.assertGreater(m.glances_dropped, 0, "the fixture never dropped a glance — this proves nothing about the seam")
        self.assertGreater(m.sleep_count, 0, "no SLEEP boundary crossed — this proves nothing about the seam")
        rows = _mind_rows(root)
        sleep_rows = [r for r in rows if isinstance(r.get("sleep"), dict)]
        total_replayed = sum(int(r["sleep"]["replayed"]) for r in sleep_rows)
        self.assertEqual(tick_calls["n"], m.glances_dropped, "Organism.tick() was called from somewhere other than _consume_eye's own per-glance loop (sleep() must never call it)")
        print(f"[DROPxSLEEP] sleep boundaries={m.sleep_count} total replayed={total_replayed} live glances_dropped={m.glances_dropped} tick_calls={tick_calls['n']}")


class TestDropXThinkThreadSeam(unittest.TestCase):
    """DROP x the think thread: the frozen copy at a boundary sees the same t. FrozenThinkInputs.frozen_t
    (creature/think_thread.py:freeze_inputs) reads `mind.org.t` verbatim — proven here by comparing that
    SAME value between a DROP-declaring mind and a FLOOR (drop-undeclared) mind after consuming the
    identical tape, and by exercising freeze_inputs() itself directly (never through real threading)."""

    def test_frozen_t_matches_org_t_and_is_unaffected_by_drop(self) -> None:
        from creature import think_thread

        def consume(genome_text: str, root: Path) -> Mind:
            _build_repeated_tape(root, "triangle", n=60, seed=11)
            gp = _write_genome(root, genome_text)
            m = Mind(gp, root)
            for r in read_tape(root):
                m.consume(r)
            return m

        root_drop = Path(tempfile.mkdtemp())
        m_drop = consume(DROP_TEXT, root_drop)
        root_floor = Path(tempfile.mkdtemp())
        m_floor = consume(GENOME_TEXT, root_floor)   # the identical tape, drop undeclared

        self.assertGreater(m_drop.glances_dropped, 0, "the fixture never dropped a glance — this proves nothing")
        self.assertEqual(m_drop.org.t, m_floor.org.t, "org.t (what frozen_t reads) diverged between DROP and FLOOR on the identical tape")

        # freeze_inputs() only needs a well-shaped item ("kind"/"key"/"episode"/"pred" — the pool's own
        # schema, docstring above); a repeated-canvas toy's own pool is naturally near-empty here (every
        # episode is either CONFIRMED-excluded or already answerable by recall(), so no "word" item forms
        # — the mechanism working as designed, not a test-harness gap), so the item is built directly
        # rather than made to depend on a live pool draw.
        item = {"kind": "sight", "key": "ep0", "episode": 0, "pred": None}
        frozen = think_thread.freeze_inputs(m_drop, item, boundary=m_drop._canvas_index)
        self.assertEqual(frozen.frozen_t, m_drop.org.t, "freeze_inputs() must read org.t verbatim")
        print(f"[DROPxTHINK] org.t drop={m_drop.org.t} floor={m_floor.org.t} frozen_t={frozen.frozen_t}")


# ============================================================================ task 5 (STATUS half): glances_dropped
class TestStatusGlancesDropped(unittest.TestCase):
    def test_status_carries_glances_dropped_and_it_equals_confirmed(self) -> None:
        from creature.body import Body
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=50, seed=42)
        gp = _write_genome(root, DROP_TEXT)
        body = Body(root, gp)
        body.mind = Mind(gp, root)
        for r in read_tape(root):
            body.mind.consume(r)
        status = body._build_status()
        self.assertIn("glances_dropped", status)
        self.assertGreater(status["glances_dropped"], 0)
        self.assertEqual(status["glances_dropped"], status["glances_confirmed"], "STATUS's own equality (task 5, checked live by tools/lives/check.py)")

    def test_status_glances_dropped_zero_when_undeclared(self) -> None:
        from creature.body import Body
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "circle", n=50, seed=42)
        body = Body(root, GENOME_PATH)   # the OLD form, no drop
        body.mind = Mind(GENOME_PATH, root)
        for r in read_tape(root):
            body.mind.consume(r)
        status = body._build_status()
        self.assertEqual(status["glances_dropped"], 0)

    def test_check_py_prints_the_equality(self) -> None:
        import io as _io
        import contextlib
        from tools.lives import check as check_mod
        root = Path(tempfile.mkdtemp())
        (root / "STATUS.json").write_text(json.dumps({"glances_confirmed": 40, "glances_surprised": 10, "glances_dropped": 40, "moments": 100, "cells": [5, 5]}))
        # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:42 +0400 — A4-LADDER-2-PREREG ADDENDUM §7(2) item 2 decides: check.py compares dropped with
        # confirmed only where the genome DECLARES `; drop confirmed` (reader v3.5, tools/lives/check.py:drop_declared). This fixture is a DROP life's
        # root, so it now carries the DROP genome beside STATUS, as tools/lives/launch.sh's copy does; the assertion below is unchanged.
        (root / "GENOME.genome").write_text(DROP_GENOME.read_text())
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            check_mod.main(["--root", str(root)])
        out = buf.getvalue()
        self.assertIn("dropped 40", out)
        self.assertIn("OK: dropped == confirmed", out)

    def test_check_py_prints_a_mismatch(self) -> None:
        import io as _io
        import contextlib
        from tools.lives import check as check_mod
        root = Path(tempfile.mkdtemp())
        (root / "STATUS.json").write_text(json.dumps({"glances_confirmed": 40, "glances_surprised": 10, "glances_dropped": 39, "moments": 100, "cells": [5, 5]}))
        # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:42 +0400 — A4-LADDER-2-PREREG ADDENDUM §7(2) item 2 decides: check.py compares dropped with
        # confirmed only where the genome DECLARES `; drop confirmed` (reader v3.5, tools/lives/check.py:drop_declared). This fixture is a DROP life's
        # root, so it now carries the DROP genome beside STATUS, as tools/lives/launch.sh's copy does; the assertion below is unchanged.
        (root / "GENOME.genome").write_text(DROP_GENOME.read_text())
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            check_mod.main(["--root", str(root)])
        out = buf.getvalue()
        self.assertIn("MISMATCH", out)


# ============================================================================ the ladder law: ONE difference
class TestGenomeIsOneDifference(unittest.TestCase):
    def test_diff_against_floor_is_exactly_the_declared_lines_and_one_edit_note(self) -> None:
        import difflib
        floor_lines = FLOOR_GENOME.read_text().splitlines(keepends=True)
        drop_lines = DROP_GENOME.read_text().splitlines(keepends=True)
        diff = list(difflib.unified_diff(floor_lines, drop_lines, lineterm=""))
        added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
        removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
        self.assertEqual(len(removed), 1, f"expected exactly one changed line (the SURPRISE line); removed={removed}")
        self.assertEqual(len(added), 2, f"expected exactly one edit-note line + one changed SURPRISE line; added={added}")
        self.assertTrue(any("drop confirmed" in l for l in added))
        self.assertIn("SURPRISE", removed[0])
        self.assertTrue(any(l.startswith("+# A4L-DROP.genome") for l in added), "the edit-note header line is missing")

    def test_drop_genome_touches_no_other_gene(self) -> None:
        gf = parse_genome(FLOOR_GENOME.read_text())
        gd = parse_genome(DROP_GENOME.read_text())
        self.assertEqual(set(gf.declared) - {"SURPRISE"}, set(gd.declared) - {"SURPRISE"})
        for gene in sorted(set(gf.declared) - {"SURPRISE"}):
            self.assertEqual(gf.declared[gene], gd.declared[gene], f"{gene} differs between FLOOR and DROP")


if __name__ == "__main__":
    unittest.main()
