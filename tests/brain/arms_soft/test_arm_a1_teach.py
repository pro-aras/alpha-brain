# edit: Claude (Sonnet 5, A1-TEACH builder), 2026-09-27 13:54 +0400 — R46 (docs/brain/b1/SEAT-DECISIONS.md; B1-PREREG.md §4 row A1 and
#   §12's 2026-09-27 13:33 line; brief docs/dev/briefs/a1-teach.md). Tests 1-5 of the brief's Tests section: the
#   positive control, the identity/negative-control pair, nothing-committed, the growth edge case, and the attention
#   refusal. Each was run against the pre-R46 arm (no `teach_trains_answer` switch existed) and its failure line is
#   pasted into docs/brain/b1/A1-TEACH-HANDBACK.md.
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.soft.arm import ArmA1  # noqa: E402
from brain.protocol import HarnessContract, make_row, op_row  # noqa: E402
from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache, _config, _run_tape  # noqa: E402

SMOKE_SEED = 20261001
# R46's own worktree (b1-a1teach) — sanctioned write area (the brief: "Your smoke runs write under
# /data/dev/brain-runs/scratch-a1teach/ only"). Persisted deliberately (never cleaned up by tearDownModule): the
# Gates section's smoke run (A1 vs A1-TEACH over the whole tape) reuses this SAME tape+cache, so the ~5 minute
# real render (brain.world.tape.build_tape, the same code test_tape.py's setUpModule uses) is paid once.
# edit: Claude (Opus 5.5), 2026-09-27 15:08 +0400 — the builder's flag at merge (R46 hand-back, «For the seat» 2): the fixture lived in the
# builder's scratch path, and it REUSED any tape found there — after R47 changed the schedule it would have tested a stale
# old-schedule world. The cache now lives under TMPDIR, keyed by the world code's own bytes (schedule.py + tape.py).
import hashlib as _hashlib
import os as _os
_REPO = Path(__file__).resolve().parents[3]
_WORLD_SRC = _hashlib.sha256(b"".join((_REPO / "brain" / "world" / f).read_bytes() for f in ("schedule.py", "tape.py"))).hexdigest()[:12]
SMOKE_DIR = Path(_os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp")) / f"b1-a1teach-smoke-{_WORLD_SRC}"

_SHARED: Dict[str, object] = {}


def _ensure_smoke_tape() -> Path:
    """Build the SMOKE world (test_tape.py's own setUpModule code path) into SMOKE_DIR if it is not already
    there; reuse it otherwise. Never touches /data/dev/brain-runs/b1/runs or /data/dev/brain-runs/b1/<seed>."""
    if (SMOKE_DIR / "tape.jsonl").exists() and (SMOKE_DIR / "tape.sha256").exists():
        return SMOKE_DIR
    from brain.world import schedule as S
    from brain.world import tape as T

    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    world = T.smoke_world(SMOKE_SEED)
    T.build_tape(SMOKE_SEED, SMOKE_DIR, SMOKE_DIR / "cache", world, S.SMOKE, log=lambda *_a: None)
    return SMOKE_DIR


def setUpModule() -> None:
    from brain.harness.run import load_tape

    tape_dir = _ensure_smoke_tape()
    rows, _sha = load_tape(tape_dir)
    sleep_idx = next(i for i, r in enumerate(rows) if r["kind"] == "SLEEP")
    n = max(300, sleep_idx + 1)
    prefix = rows[:n]
    kinds = {r["kind"] for r in prefix}
    assert {"TEACH", "ASK", "FEEDBACK", "SLEEP"} <= kinds, f"the smoke prefix is missing a kind: has {kinds}"
    _SHARED["tape_dir"] = tape_dir
    _SHARED["cache_dir"] = str(tape_dir / "cache")
    _SHARED["prefix"] = prefix
    _SHARED["n"] = n


class TestA1TeachPositiveControl(unittest.TestCase):
    """Brief item 1 — R46's own positive control: a TEACH-only stream, no FEEDBACK, several names each taught
    N times. `NameAnswerHead.hear_name` -> `GrowableLinear.add_output` (engine.py) only appends a row index —
    it never touches `self.W`/`self.b`, which are pre-allocated at `torch.zeros(...)` (GrowableLinear.__init__)
    and `init_block` only initialises rows [:n_out] that existed BEFORE hear_name was ever called (n_out starts
    at 0 for NameAnswerHead) — so every heard name's row stays weight-ZERO, bias-ZERO until something trains it.
    With no FEEDBACK, the WORLD loss is the only thing `_advance_steps` back-propagates, and NameAnswerHead's
    parameters get `grad=None` from it (`allow_unused=True` in LocalEligibilityTrainer.step just decays their
    trace) — so every name's logit stays EXACTLY 0 and softmax over n equal logits is EXACTLY 1/n."""

    def setUp(self) -> None:
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_teach_pc_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _teach_only(self, switch: bool, repeats: int) -> ArmA1:
        cfg = _config(self.cache_dir, teach_trains_answer=switch)
        arm = ArmA1(seed=999, config=cfg)
        seq = 0
        for _ in range(repeats):
            for ch in "abc":
                seq += 1
                HarnessContract.teach(arm, make_row(seq, "TEACH", "L1", ch, {"glance_row": self.rows[ch][0], "name": ch}))
        return arm

    def _prob(self, arm: ArmA1, ch: str) -> float:
        """The taught name's OWN softmax probability at a NAME ask on its taught glyph — exactly the peek
        `_query_state_fresh`/`_answer_impl` compute for family NAME on a non-attention variant (self.names(h,
        active_h=engine.active)), read directly rather than through Answer.raw['conf'] (the MAX prob over all
        names, not necessarily `ch`'s own — the wrong number to check the positive control against)."""
        with torch.no_grad():
            h = arm.h.detach().clone()
            for x in arm.encoder.ask_steps({"cues": ["NAME"], "operands": [op_row(self.rows[ch][0])]}):
                h = arm.engine.step(x, h)
            logits = arm.names(h, active_h=arm.engine.active)
            probs = torch.softmax(logits, dim=-1)
            return float(probs[arm.names.names.index(ch)])

    def test_switch_off_stays_at_the_init_uniform(self) -> None:
        arm = self._teach_only(switch=False, repeats=10)
        n = len(arm.names.names)
        self.assertEqual(n, 3)
        for ch in "abc":
            self.assertAlmostEqual(self._prob(arm, ch), 1.0 / n, places=6,
                                    msg=f"{ch}: TEACH alone (no FEEDBACK, switch OFF) must not move the NAME head")

    def test_switch_on_rises_clearly_above_the_uniform(self) -> None:
        arm = self._teach_only(switch=True, repeats=10)
        n = len(arm.names.names)
        for ch in "abc":
            p = self._prob(arm, ch)
            self.assertGreater(p, 1.0 / n + 0.05, f"{ch}: p={p} did not rise clearly above 1/{n} after 10 TEACH repeats")


class TestA1TeachIdentityAndNegativeControl(unittest.TestCase):
    """Brief item 2 — Identity: with the switch False, the arm is A1 byte for byte (the same state_sha series)
    over a real tape prefix (>=300 rows, TEACH/ASK/FEEDBACK/SLEEP all present) from the smoke fixture. Carries
    its own negative control (#91's rule: a check with no way to fail proves nothing) — a third arm with the
    switch ON over the SAME prefix must DIFFER; on the pre-R46 arm the switch does nothing, so all three sha
    series are identical and this half goes red."""

    def _run(self, switch) -> ArmA1:
        cfg = _config(_SHARED["cache_dir"], teach_trains_answer=switch, h0=8, hmax=16, arrival_budget=4, arrival_regen=20)
        arm = ArmA1(seed=20261001, config=cfg)
        _run_tape(arm, _SHARED["prefix"])
        return arm

    def test_switch_false_is_byte_for_byte_a1_and_switch_true_differs(self) -> None:
        baseline_cfg = _config(_SHARED["cache_dir"], h0=8, hmax=16, arrival_budget=4, arrival_regen=20)
        baseline_cfg.pop("teach_trains_answer", None)
        baseline = ArmA1(seed=20261001, config=baseline_cfg)
        _run_tape(baseline, _SHARED["prefix"])

        explicit_off = self._run(switch=False)
        self.assertEqual(baseline.state_sha(), explicit_off.state_sha(),
                          f"switch False (explicit) must match A1 with no such key at all, over {_SHARED['n']} real rows")

        switch_on = self._run(switch=True)
        self.assertNotEqual(baseline.state_sha(), switch_on.state_sha(),
                             "the negative control: switch True over the SAME prefix must diverge from A1")


class TestA1TeachNothingCommitted(unittest.TestCase):
    """Brief item 3: build one arm state and copy it twice (switch OFF / switch ON, identical otherwise); feed
    the SAME single TEACH row to each; self.h must be EQUAL (the virtual ask never assigns/advances self.h) and
    the NAME head's parameters must DIFFER (R46's own trainer call reaches self.names' weights and bias — see
    the module docstring's D21: it also reaches engine/world/yesno/pick, since local_trainer.step shares ONE
    eligibility-trace buffer over every registered parameter, exactly as a real FEEDBACK row does; this test
    pins the NAME head specifically, which is where R46 says the difference must be).

    "One arm state, copied twice" is built via snapshot/load rather than by literally feeding both arms
    identical rows from empty: a NAME ask's cross-entropy loss over n=1 heard name is mathematically constant
    (softmax of a single logit is always 1.0, so its gradient is exactly zero regardless of the switch) — the
    first-ever TEACH row is a degenerate case that would pass this test for the wrong reason. So the shared
    state hears TWO names first (n=2, non-degenerate), is snapshotted once, loaded into both copies, and only
    THEN do the two copies see the SAME single (third) TEACH row this test is actually about."""

    def setUp(self) -> None:
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_teach_nc_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_h_equal_names_differ(self) -> None:
        base = ArmA1(seed=42, config=_config(self.cache_dir))
        HarnessContract.teach(base, make_row(1, "TEACH", "L1", "a", {"glance_row": self.rows["a"][0], "name": "a"}))
        HarnessContract.teach(base, make_row(2, "TEACH", "L1", "b", {"glance_row": self.rows["b"][0], "name": "b"}))
        snap = os.path.join(self.tmp, "base_snap")
        base.snapshot(snap)

        arm_off = ArmA1(seed=42, config=_config(self.cache_dir, teach_trains_answer=False))
        arm_on = ArmA1(seed=42, config=_config(self.cache_dir, teach_trains_answer=True))
        arm_off.load(snap)
        arm_on.load(snap)
        self.assertEqual(arm_off.state_sha(), arm_on.state_sha(), "both copies must start identical")

        row = make_row(3, "TEACH", "L1", "c", {"glance_row": self.rows["c"][0], "name": "c"})
        HarnessContract.teach(arm_off, row)
        HarnessContract.teach(arm_on, row)

        self.assertTrue(torch.equal(arm_off.h, arm_on.h), "the virtual ask must never assign or advance self.h")
        w_off, w_on = arm_off.names.state_dict()["W"], arm_on.names.state_dict()["W"]
        b_off, b_on = arm_off.names.state_dict()["b"], arm_on.names.state_dict()["b"]
        self.assertFalse(torch.equal(w_off, w_on) and torch.equal(b_off, b_on),
                          "the NAME head's parameters must differ between switch OFF and switch ON after the SAME new TEACH row")


class TestA1TeachGrowth(unittest.TestCase):
    """Brief item 4: a TEACH row during which a birth happens runs, and h_before needs no widening (it is
    already hmax-wide — engine.py's GrowingGRUEngine.step always returns an hmax-wide tensor whose tail beyond
    `active` is the unborn units' zero padding, and self.h/h_before are built from engine.zero_state(), also
    hmax-wide, from construction — see the module's D21 / arm.py's item-4 comment). The birth is forced
    deterministically (no need to wait out the natural 200-step error-window criterion): fill the engine's own
    error window and baseline so should_birth() reads True before this row's own first intermediate step."""

    def setUp(self) -> None:
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_teach_growth_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_birth_during_a_teach_row_does_not_crash_and_still_trains(self) -> None:
        cfg = _config(self.cache_dir, teach_trains_answer=True, h0=8, hmax=16, arrival_budget=4, arrival_regen=20)
        arm = ArmA1(seed=7, config=cfg)
        HarnessContract.teach(arm, make_row(1, "TEACH", "L1", "a", {"glance_row": self.rows["a"][0], "name": "a"}))
        HarnessContract.teach(arm, make_row(2, "TEACH", "L1", "b", {"glance_row": self.rows["b"][0], "name": "b"}))

        active_before = arm.engine.active
        self.assertEqual(arm.h.shape[-1], arm.engine.hmax, "h is always hmax-wide by construction")
        arm.engine._err_window.extend([1.0] * 200)      # force should_birth() True on the very next observation
        arm.engine._arrival_baseline = 1e-9

        row3 = make_row(3, "TEACH", "L1", "c", {"glance_row": self.rows["c"][0], "name": "c"})
        HarnessContract.teach(arm, row3)                # must not raise (the shape pin)

        self.assertGreater(arm.engine.active, active_before, "the forced birth must actually have grown the engine")
        self.assertEqual(arm.h.shape[-1], arm.engine.hmax, "h stays hmax-wide across the birth")
        w = arm.names.state_dict()["W"]
        self.assertFalse(bool(torch.isnan(w).any()) or bool(torch.isinf(w).any()), "no NaN/Inf reached the NAME head across the birth")
        idx_c = arm.names.names.index("c")
        self.assertTrue(bool((w[idx_c] != 0).any()) or bool(arm.names.state_dict()["b"][idx_c] != 0),
                        "the virtual ask on row 3 must have actually trained c's row despite the birth mid-row")


class TestA1TeachAttentionRefusal(unittest.TestCase):
    """Brief item 5: A1-ATT / A1-MA with the switch raise ValueError at construction — never silently ignored,
    never lazily deferred to the first TEACH row."""

    def setUp(self) -> None:
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_a1_teach_att_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a1_att_with_switch_raises(self) -> None:
        cfg = _config(self.cache_dir, variant="A1-ATT", teach_trains_answer=True, fixed_h=8, arrival_budget=0)
        with self.assertRaises(ValueError):
            ArmA1(seed=1, config=cfg)

    def test_a1_ma_with_switch_raises(self) -> None:
        cfg = _config(self.cache_dir, variant="A1-MA", teach_trains_answer=True, fixed_h=8, arrival_budget=0, ma_n_tokens=63)
        with self.assertRaises(ValueError):
            ArmA1(seed=1, config=cfg)

    def test_a1_att_without_the_switch_still_constructs(self) -> None:
        """Negative control: the refusal is keyed to the switch, not to the variant alone."""
        cfg = _config(self.cache_dir, variant="A1-ATT", fixed_h=8, arrival_budget=0)
        ArmA1(seed=1, config=cfg)  # must not raise


if __name__ == "__main__":
    unittest.main()
