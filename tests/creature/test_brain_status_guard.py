# edit: Claude (Fable 5.1, the seat), 2026-09-28 21:43 +0400 — BRAIN-IN-BODY, the reviewer's R2: the STATUS thread survives a torn read of the brain.
"""tests/creature/test_brain_status_guard.py — `creature.body._brain_status_guarded`: a mind without the method → None; a
healthy mind → its status; a mind whose brain_status RAISES (the mind thread grew a dict under the reader) → the error is
carried on STATUS and nothing propagates. Control: the unguarded call DOES raise on the same mind."""
from __future__ import annotations

import types
import unittest

from creature import body as body_module


class _Torn:
    def brain_status(self):
        raise RuntimeError("dictionary changed size during iteration")


class _Healthy:
    def brain_status(self):
        return {"learned": 3, "asks_answered": 1}


class BrainStatusGuard(unittest.TestCase):
    def test_no_method_is_none(self):
        self.assertIsNone(body_module._brain_status_guarded(types.SimpleNamespace()))

    def test_healthy_passes_through(self):
        self.assertEqual(body_module._brain_status_guarded(_Healthy()), {"learned": 3, "asks_answered": 1})

    def test_torn_read_is_carried_never_raised(self):
        got = body_module._brain_status_guarded(_Torn())
        self.assertEqual(sorted(got), ["error"])
        self.assertIn("dictionary changed size", got["error"])

    def test_control_the_unguarded_call_raises(self):
        with self.assertRaises(RuntimeError):
            _Torn().brain_status()

    def test_build_status_uses_the_guard(self):
        import inspect
        src = inspect.getsource(body_module.Body._build_status)
        self.assertIn("_brain_status_guarded(self.mind)", src)
        self.assertNotIn("self.mind.brain_status()", src)


if __name__ == "__main__":
    unittest.main()
