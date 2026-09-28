# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:42 +0400 — BRAIN-IN-BODY §5's own pin: the scene door's
# arming and the maker's unchanged-behaviour grep count.
"""tests/creature/test_scene_arming.py — creature/body.py:_declared_scene_config and _maker_should_arm."""
from __future__ import annotations

import glob
import unittest
from pathlib import Path

from creature import body as B
from creature.senses import scene as scene_sense

REPO_ROOT = Path(__file__).resolve().parents[2]


def _every_genome_text():
    paths = sorted(set(glob.glob(str(REPO_ROOT / "genome" / "**" / "*.genome"), recursive=True))
                    | set(glob.glob(str(REPO_ROOT / "tests" / "**" / "*.genome"), recursive=True)))
    return [(p, Path(p).read_text()) for p in paths]


class DeclaredSceneConfig(unittest.TestCase):
    def test_undeclared_arms_nothing(self):
        self.assertIsNone(B._declared_scene_config({}))

    def test_declared_returns_its_own_dict(self):
        cfg = {"seed": 20261101}
        self.assertEqual(B._declared_scene_config({"WORLD_SCENE": cfg}), cfg)

    def test_gated_on_the_module_constant(self):
        self.assertTrue(scene_sense.SCENE_DOOR_GATED, "the gate must be True for _declared_scene_config to return anything")


class MakerShouldArm(unittest.TestCase):
    def test_no_maker_flag_always_wins(self):
        self.assertFalse(B._maker_should_arm({"WORLD": {}}, ["--no-maker"]))
        self.assertFalse(B._maker_should_arm({}, ["--no-maker"]))

    def test_scene_only_genome_suppresses_the_maker(self):
        self.assertFalse(B._maker_should_arm({"WORLD_SCENE": {}}, []))

    def test_maker_flag_forces_it_back_on_for_a_scene_only_genome(self):
        self.assertTrue(B._maker_should_arm({"WORLD_SCENE": {}}, ["--maker"]))

    def test_a_genome_with_both_world_and_world_scene_still_arms_the_maker(self):
        self.assertTrue(B._maker_should_arm({"WORLD": {}, "WORLD_SCENE": {}}, []))

    def test_a_genome_declaring_neither_still_arms_the_maker_todays_behaviour(self):
        self.assertTrue(B._maker_should_arm({}, []))

    def test_a_genome_declaring_world_game_but_not_world_still_arms_the_maker(self):
        self.assertTrue(B._maker_should_arm({"WORLD_GAME": {}}, []))

    def test_every_real_genome_files_maker_arming_is_unchanged(self):
        """Every genome/**/*.genome and test fixture genome that carries a drawn `^WORLD ` line today keeps its
        maker armed under the new gate (none of them declare WORLD_SCENE — verified by count, both printed)."""
        from genome.machinery import parse_genome
        files = _every_genome_text()
        self.assertGreater(len(files), 0, "no genome files found — the glob is broken")
        drawn_world_lines = sum(1 for _p, text in files
                                 for line in text.splitlines() if line.startswith("WORLD ") or line.startswith("WORLD\t"))
        unchanged = 0
        checked = 0
        for path, text in files:
            try:
                declared = parse_genome(text).declared
            except Exception:
                continue   # a deliberately-broken fixture genome (parse-error tests) — not this test's concern
            checked += 1
            old_would_arm = True   # the OLD code: `if not no_maker: arm` — unconditional
            new_would_arm = B._maker_should_arm(declared, [])
            if "WORLD_SCENE" not in declared:
                self.assertEqual(old_would_arm, new_would_arm, msg=f"{path}: behaviour changed for a non-scene genome")
                unchanged += 1
        print(f"maker-arming count: {len(files)} genome files, {drawn_world_lines} carry a `WORLD ` line, "
              f"{checked} parsed, {unchanged} non-scene genomes verified byte-for-byte unchanged")
        self.assertEqual(unchanged, checked, "every parseable genome here declares no WORLD_SCENE, so all must be unchanged")


if __name__ == "__main__":
    unittest.main()
