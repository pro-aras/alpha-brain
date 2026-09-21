# edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:2x +0400 — the "Also" item of W3-BUILDER-A.md
# (Mind.think_counters gains revisits/extensions/clashes) plus the coordinator's integration note on
# Builder B's landed W3-1 interface (g4-wave3-b @ 04a302a, worktree genome-wt-e — read there ONLY,
# never imported here; this branch owns creature/, not genome/). Two things pinned:
#   1. `_think_work`'s "word" branch counts by the returned dict's "kind" (default/unknown -> "beliefs"),
#      coded against believe()'s NEW keyword-only interface (`ledgers`, `clash_enabled`) via runtime
#      introspection of whatever `believe` this tree actually has (creature/mind.py's `_BELIEVE_KWARGS`),
#      so the exact same call site works before AND after genome/think.py gains those parameters.
#   2. It never breaks today's 5-positional-parameter believe() (test_wave2_belief_path.py's real,
#      unstubbed belief formation is the backward-compatibility half of this pin).
from __future__ import annotations

import inspect
import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import creature.mind as mind_module
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
GENOME = ROOT / "genome" / "G4.genome"   # declares BELIEF -> clash_enabled must read True


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO()
    Image.fromarray(rgb).save(b, format="PNG")
    return b.getvalue()


def _build_mind_with_a_belief_item() -> "tuple[Mind, dict]":
    """The exact fixture tests/creature/test_wave2_belief_path.py already proves reliably forms a real
    belief (150 canvases, 3 things) — reused rather than re-invented so this test's premise (some word
    item really does reach believe()) is not a new, unverified assumption.

    The pool item that reaches "belief" is one THINK finds AUTOMATICALLY mid-stream, via `_maybe_think`'s
    own scheduling (a word whose SINGLE-glance recall abstains at that point) — computing `_think_pool()`
    fresh only after all 150 canvases are consumed finds no such item (by then most words resonate on one
    glance, so they never even enter the pool). `_think_work` is spied on during the real run to capture
    the actual item(s) THINK worked that resolved to "belief", then re-verified once more (read-only:
    recall_many/build_ledgers touch no state) before being handed to a caller that will re-run it under a
    stub."""
    root = Path(tempfile.mkdtemp()) / "run"
    tape = Tape(root)
    things = ["circle", "square", "triangle"]
    for i in range(150):
        t = things[i % 3]
        rgb, _truth = world.render_canvas(t, np.random.default_rng([4242, i]))
        at = f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z"
        tape.publish("ear", t.encode(), {"moment": f"m{i}", "source": "maker", "word": t}, "txt", at=at)
        tape.publish("eye", _png(rgb), {"moment": f"m{i}", "source": "maker"}, "png", at=at)
    mind = Mind(GENOME, root)

    captured: list = []
    real_think_work = mind._think_work

    def _spy(item):
        result = real_think_work(item)
        if item.get("kind") == "word" and result.get("outcome") == "belief":
            captured.append(item)
        return result

    mind._think_work = _spy
    for row in read_tape(root):
        mind.consume(row)
    mind._think_work = real_think_work

    for item in reversed(captured):   # latest first: the most mature org state, least likely to have drifted
        if mind._think_work(item)["outcome"] == "belief":
            return mind, item
    raise AssertionError("fixture produced no word item that forms a real, re-verifiable belief -- test premise broken")


class TestBackwardCompatibleWithTodaysBelieve(unittest.TestCase):
    """Written by Builder A against the pre-W3-1 believe() (5 positional parameters, always kind="belief");
    reconciled at the staging merge — edit: Claude (Fable 5.1), 2026-09-20 23:56 +0400 — because Builder B's W3-1 (the
    scope law, genome/think.py) makes a SECOND believe() of a word whose cells are unchanged a REVISIT, and a
    changed cell set an EXTENSION: the plumbing's contract on the merged tree is that the think outcome is still
    "belief" and exactly one of the kind counters moves (#232 addendum (c): a test that pins the absence of a
    feature another lane is building is a merge-time failure by design)."""

    def test_rethinking_a_believed_word_moves_exactly_one_kind_counter(self) -> None:
        mind, item = _build_mind_with_a_belief_item()
        before = dict(mind.think_counters)
        result = mind._think_work(item)
        self.assertEqual(result["outcome"], "belief")
        after = mind.think_counters
        moved = {k: after[k] - before[k] for k in ("beliefs", "revisits", "extensions", "clashes")}
        self.assertEqual(sum(moved.values()), 1, moved)
        self.assertEqual(moved["clashes"], 0, moved)          # re-thinking the same evidence is never a contradiction
        self.assertIn(1, (moved["revisits"], moved["extensions"], moved["beliefs"]), moved)


class _StubThinkLaws:
    """A fake `think_laws` module-alike carrying only `believe`, matching the shape mind.py imports it
    as (`from genome import think as think_laws`, used as `think_laws.believe(...)`)."""

    def __init__(self, believe_fn):
        self.believe = believe_fn


class TestKindToCounterMapping(unittest.TestCase):
    """Stubs, per the brief's own instruction ("test with a stub", "do not wait for B"). Each stub matches
    Builder B's NEW interface (ledgers=None, clash_enabled=True) so `_BELIEVE_KWARGS` — recomputed here
    against the STUB, exactly as creature/mind.py computes it against whatever believe() it imports —
    detects and passes both kwargs; the plumbing test for that is separate, below."""

    def setUp(self) -> None:
        self.mind, self.item = _build_mind_with_a_belief_item()
        self._orig_think_laws = mind_module.think_laws
        self._orig_kwargs = mind_module._BELIEVE_KWARGS

    def tearDown(self) -> None:
        mind_module.think_laws = self._orig_think_laws
        mind_module._BELIEVE_KWARGS = self._orig_kwargs

    def _install_stub(self, kind, extra=None):
        def fake_believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True):
            row = {"line": 0, "word": word, "cells": cells, "episodes": episode_ids, "moment": moment, "clashes": []}
            if kind is not None:
                row["kind"] = kind
            if extra:
                row.update(extra)
            return row
        mind_module.think_laws = _StubThinkLaws(fake_believe)
        mind_module._BELIEVE_KWARGS = frozenset(inspect.signature(fake_believe).parameters)

    def _delta(self, before):
        after = self.mind.think_counters
        return {k: after[k] - before.get(k, 0) for k in ("beliefs", "revisits", "extensions", "clashes")}

    def test_kind_belief_counts_beliefs(self) -> None:
        self._install_stub("belief")
        before = dict(self.mind.think_counters)
        result = self.mind._think_work(self.item)
        self.assertEqual(result["outcome"], "belief")
        self.assertEqual(self._delta(before), {"beliefs": 1, "revisits": 0, "extensions": 0, "clashes": 0})

    def test_kind_revisit_counts_revisits(self) -> None:
        self._install_stub("revisit")
        before = dict(self.mind.think_counters)
        self.mind._think_work(self.item)
        self.assertEqual(self._delta(before), {"beliefs": 0, "revisits": 1, "extensions": 0, "clashes": 0})

    def test_kind_extension_counts_extensions(self) -> None:
        self._install_stub("extension", extra={"of": 3, "added": [7, 8]})
        before = dict(self.mind.think_counters)
        self.mind._think_work(self.item)
        self.assertEqual(self._delta(before), {"beliefs": 0, "revisits": 0, "extensions": 1, "clashes": 0})

    def test_kind_clash_counts_clashes(self) -> None:
        self._install_stub("clash")
        before = dict(self.mind.think_counters)
        self.mind._think_work(self.item)
        self.assertEqual(self._delta(before), {"beliefs": 0, "revisits": 0, "extensions": 0, "clashes": 1})

    def test_missing_kind_defaults_to_beliefs(self) -> None:
        """A stub matching the OLD shape (no "kind" key at all) — the exact thing today's real believe()
        does NOT do (it always sets "kind": "belief" explicitly) but a future or third-party stub might."""
        self._install_stub(None)
        before = dict(self.mind.think_counters)
        self.mind._think_work(self.item)
        self.assertEqual(self._delta(before), {"beliefs": 1, "revisits": 0, "extensions": 0, "clashes": 0})

    def test_unknown_kind_does_not_crash_and_counts_as_belief(self) -> None:
        self._install_stub("something-nobody-named-yet")
        before = dict(self.mind.think_counters)
        self.mind._think_work(self.item)   # must not raise KeyError
        self.assertEqual(self._delta(before), {"beliefs": 1, "revisits": 0, "extensions": 0, "clashes": 0})


class TestLedgersAndClashEnabledPassthrough(unittest.TestCase):
    """The coordinator's two integration facts: `ledgers` (already computed above the call) is passed
    through, and `clash_enabled` reads G4.genome's own BELIEF declaration (True here)."""

    def test_ledgers_and_clash_enabled_are_passed_when_the_signature_accepts_them(self) -> None:
        mind, item = _build_mind_with_a_belief_item()
        self.assertIn("BELIEF", mind.genome.declared, "G4.genome must declare BELIEF for this to test anything")

        captured = {}

        def fake_believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True):
            captured["ledgers"] = ledgers
            captured["clash_enabled"] = clash_enabled
            return {"line": 0, "kind": "extension"}

        orig_think_laws, orig_kwargs = mind_module.think_laws, mind_module._BELIEVE_KWARGS
        mind_module.think_laws = _StubThinkLaws(fake_believe)
        mind_module._BELIEVE_KWARGS = frozenset(inspect.signature(fake_believe).parameters)
        try:
            mind._think_work(item)
        finally:
            mind_module.think_laws = orig_think_laws
            mind_module._BELIEVE_KWARGS = orig_kwargs

        self.assertIn("ledgers", captured)
        self.assertIsNotNone(captured["ledgers"], "ledgers must be the same build_ledgers() output _think_work already computed")
        self.assertIn("sight", captured["ledgers"])
        self.assertIn("words", captured["ledgers"])
        self.assertTrue(captured["clash_enabled"], "BELIEF is declared on G4.genome -> clash_enabled must be True")

    def test_clash_enabled_false_when_belief_undeclared(self) -> None:
        """edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 12:xx +0400 — W3-0b (docs/G4-WAVE3-CLAUSES.md;
        docs/briefs/W3-BUILDER-D.md's own verbatim clause): "think_laws.believe() only when 'BELIEF' in
        declared (a word item without BELIEF -> dead end no_belief_gene)". Before this clause landed on
        this branch, BELIEF undeclared still called believe() (with clash_enabled=False) — the ORIGINAL
        premise this test pinned. That premise is superseded by design: believe() is now gated on BELIEF's
        OWN presence and is never reached at all when it is undeclared — the same merge-time flip
        SOLUTIONS #232 addendum (c) names (a test pinning the ABSENCE of a feature another lane's clause
        changes at merge time; pin the presence with the value, or pin nothing). Flipped to assert the new
        law: a dead end named "no_belief_gene", and the stub never called at all (there is no
        ledgers/clash_enabled kwarg to observe on a call that never happens)."""
        mind, item = _build_mind_with_a_belief_item()
        del mind.genome.declared["BELIEF"]

        captured = {}

        def fake_believe(word, cells, episode_ids, moment, path, ledgers=None, clash_enabled=True):
            captured["clash_enabled"] = clash_enabled
            return {"line": 0, "kind": "belief"}

        orig_think_laws, orig_kwargs = mind_module.think_laws, mind_module._BELIEVE_KWARGS
        mind_module.think_laws = _StubThinkLaws(fake_believe)
        mind_module._BELIEVE_KWARGS = frozenset(inspect.signature(fake_believe).parameters)
        try:
            result = mind._think_work(item)
        finally:
            mind_module.think_laws = orig_think_laws
            mind_module._BELIEVE_KWARGS = orig_kwargs

        self.assertEqual(result["outcome"], "no_belief_gene")
        self.assertEqual(captured, {},
                          "believe() must never be called when BELIEF is undeclared -- W3-0b gates the call itself")

    def test_old_signature_receives_no_extra_kwargs(self) -> None:
        """A stub matching TODAY's real signature exactly (no ledgers/clash_enabled parameters) must not
        be called with them -- a TypeError here would mean the introspection guard is broken."""
        mind, item = _build_mind_with_a_belief_item()

        def old_style_believe(word, cells, episode_ids, moment, path):
            return {"line": 0, "kind": "belief"}

        orig_think_laws, orig_kwargs = mind_module.think_laws, mind_module._BELIEVE_KWARGS
        mind_module.think_laws = _StubThinkLaws(old_style_believe)
        mind_module._BELIEVE_KWARGS = frozenset(inspect.signature(old_style_believe).parameters)
        try:
            result = mind._think_work(item)   # must not raise TypeError
        finally:
            mind_module.think_laws = orig_think_laws
            mind_module._BELIEVE_KWARGS = orig_kwargs
        self.assertEqual(result["outcome"], "belief")


if __name__ == "__main__":
    unittest.main()
