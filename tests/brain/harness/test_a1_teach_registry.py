# edit: Claude (Sonnet 5, A1-TEACH builder), 2026-09-27 13:54 +0400 — R46 (docs/brain/b1/SEAT-DECISIONS.md; brief
#   docs/dev/briefs/a1-teach.md, Tests item 6): the registry entry and its three twins resolve through
#   `spec_for` with no special-casing. Red on the old code: `RunError: unknown arm 'A1-TEACH'; ...`.
from __future__ import annotations

import unittest

from brain.harness import run as R


class TestA1TeachRegistry(unittest.TestCase):
    def test_a1_teach_carries_variant_and_the_switch(self) -> None:
        spec = R.spec_for("A1-TEACH")
        self.assertEqual(spec.config.get("variant"), "A1")
        self.assertIs(spec.config.get("teach_trains_answer"), True)
        self.assertEqual(spec.module, "brain.arms.soft.arm")
        self.assertEqual(spec.cls, "ArmA1")

    def test_the_three_twins_resolve_with_no_special_casing(self) -> None:
        for prefix in ("SHUFFLED-NAME", "SHUFFLED-RELATION", "FORCED"):
            spec = R.spec_for(f"{prefix}:A1-TEACH")
            self.assertEqual(spec.name, f"{prefix}:A1-TEACH")
            self.assertEqual(spec.config.get("variant"), "A1")
            self.assertIs(spec.config.get("teach_trains_answer"), True)

    def test_spec_for_does_not_mutate_the_registry(self) -> None:
        R.spec_for("SHUFFLED-RELATION:A1-TEACH")
        self.assertEqual(R._BASE["A1-TEACH"].config.get("teach_trains_answer"), True)
        self.assertIsNone(R._BASE["A1-TEACH"].transform)

    def test_a1_teach_is_named_in_the_known_arms_listing(self) -> None:
        self.assertIn("A1-TEACH", R.known_arm_names())


if __name__ == "__main__":
    unittest.main()
