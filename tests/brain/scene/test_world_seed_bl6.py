# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 18:4x +0400 — PREREG-BRAIN-LONG-6 §2 B2
# (the law SIGNED; SEAT-LINE sha256 2c6bb22b…; test-first): the scene world made lawful at brain-long-6's
# seed 20261211 — WORLD_SEEDS gains it and the three TEST maps gain its splits (s1b1 20261321 · fresh
# 20261521 · held 20261621 — the +100/+300/+400 pattern's own discipline, all three verified never used
# anywhere before the law). The scene generator (train_scene) is untouched: the new seed is a new draw of
# the SAME world form, never a new world.
"""tests/brain/scene/test_world_seed_bl6.py — the scene seed 20261211 (PREREG-BRAIN-LONG-6 §1.2/§2 B2)."""
from __future__ import annotations

import unittest

from brain.scene import world as W


class TheSeedIsLawful(unittest.TestCase):
    def test_world_seeds_gains_20261211(self) -> None:
        self.assertIn(20261211, W.WORLD_SEEDS)

    def test_the_old_seeds_stand(self) -> None:
        for s in (20261101, 20261102, 20261103):
            with self.subTest(seed=s):
                self.assertIn(s, W.WORLD_SEEDS)

    def test_the_test_maps_gain_the_declared_splits(self) -> None:
        self.assertEqual(W.TEST_SEEDS[20261211], 20261321)
        self.assertEqual(W.FRESH_TEST_SEEDS[20261211], 20261521)
        self.assertEqual(W.HELD_TEST_SEEDS[20261211], 20261621)

    def test_the_old_splits_stand(self) -> None:
        for s in (20261101, 20261102, 20261103):
            with self.subTest(seed=s):
                self.assertEqual(W.TEST_SEEDS[s], s + 100)
                self.assertEqual(W.FRESH_TEST_SEEDS[s], s + 300)
                self.assertEqual(W.HELD_TEST_SEEDS[s], s + 400)

    def test_the_new_split_seeds_are_distinct_from_every_old_split(self) -> None:
        old = {W.TEST_SEEDS[s] for s in (20261101, 20261102, 20261103)}
        old |= {W.FRESH_TEST_SEEDS[s] for s in (20261101, 20261102, 20261103)}
        old |= {W.HELD_TEST_SEEDS[s] for s in (20261101, 20261102, 20261103)}
        for new in (20261321, 20261521, 20261621):
            with self.subTest(split=new):
                self.assertNotIn(new, old)

    def test_train_scene_draws_at_the_new_seed(self) -> None:
        """The generator itself is untouched: a scene draws at 20261211, deterministic twice, and its form
        is the same world form (a Scene with the world's own fields — the law: a new draw, never a new world)."""
        a = W.train_scene(20261211, 0)
        b = W.train_scene(20261211, 0)
        self.assertEqual(a.to_dict(), b.to_dict(), "the draw is deterministic at the new seed")
        old = W.train_scene(20261101, 0)
        self.assertEqual(set(a.to_dict()), set(old.to_dict()),
                         "the scene's fields are the same world's fields at any seed")

    def test_a_never_declared_seed_still_refuses(self) -> None:
        """The validation keeps its teeth: a seed nobody declared is refused by name (the bl5 item's
        other half — the refusal exists, and it now names only what is truly not a world seed)."""
        from creature.senses.scene import plan
        with self.assertRaises(ValueError) as cm:
            plan({"seed": 20999999, "train": 1, "sitting": [], "utterance": True})
        self.assertIn("20999999", str(cm.exception))

    def test_plan_at_20261211_returns_moments(self) -> None:
        from creature.senses.scene import plan
        moments = plan({"seed": 20261211, "train": 2, "sitting": [], "utterance": True})
        self.assertGreater(len(moments), 0, "presence: the scene world publishes at the life's seed")


if __name__ == "__main__":
    unittest.main()
