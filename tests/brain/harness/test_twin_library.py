# edit: Claude (Opus 5.5), 2026-09-26 17:11 +0400 — a TAPE twin of a hybrid must load a library searched on ITS OWN tape
# (SEAT-DECISIONS R36). Before this, SHUFFLED-RELATION:E′ and :F resolved `library_load_from` to the REAL D's run: the null
# fed a shuffled tape answered relations with rules learned from the TRUE relation answers, so its 95 % band would sit at
# E′'s own score and U3 could never pass for E′ or F — a control blind to nothing (#228's fifth gate).
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from brain.harness import run as R

KEY = "part_config.lib.library_load_from"


class TestTwinLibrary(unittest.TestCase):
    def test_shuffled_relation_hybrids_load_the_twin_library(self) -> None:
        for arm in ("E′", "F"):
            spec = R.spec_for(f"SHUFFLED-RELATION:{arm}")
            self.assertEqual(spec.config_from[KEY], ("SHUFFLED-RELATION:D", "arm_dir"), arm)

    def test_the_rule_is_every_tape_transform(self) -> None:
        self.assertEqual(R.spec_for("SHUFFLED-NAME:E′").config_from[KEY], ("SHUFFLED-NAME:D", "arm_dir"))

    def test_the_real_arm_and_a_wrapper_twin_keep_the_real_library(self) -> None:
        """FORCED is a wrapper over the SAME tape: the real D's library is the right one there."""
        self.assertEqual(R.spec_for("E′").config_from[KEY], ("D", "arm_dir"))
        self.assertEqual(R.spec_for("FORCED:E′").config_from[KEY], ("D", "arm_dir"))

    def test_a_size_match_stays_on_the_base_arm(self) -> None:
        """A capacity match is not learned content: SHUFFLED-NAME:A1-ATT still matches A1's parameter count."""
        spec = R.spec_for("SHUFFLED-NAME:A1-ATT")
        self.assertEqual(spec.config_from["match_params"], ("A1", "size.n_params_active"))

    def test_spec_for_does_not_mutate_the_registry(self) -> None:
        R.spec_for("SHUFFLED-RELATION:E′")
        self.assertEqual(R._BASE["E′"].config_from[KEY], ("D", "arm_dir"))

    def _summary(self, root: Path, dirname: str) -> Path:
        d = root / dirname
        (d / "arm").mkdir(parents=True)
        (d / "summary.json").write_text(json.dumps({"arm_dir": str(d / "arm")}))
        return d / "arm"

    def test_the_twin_never_falls_back_to_the_real_library(self) -> None:
        """Only the REAL D has run: resolving the twin must refuse, never load D's snapshots."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._summary(root, "D")
            spec = R.spec_for("SHUFFLED-RELATION:E′")
            with self.assertRaises(R.RunError):
                R._resolve_config_from(spec, root)

    def test_the_twin_resolves_to_its_own_d_directory(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            real = self._summary(root, "D")
            twin = self._summary(root, "SHUFFLED-RELATION_D")
            spec = R.spec_for("SHUFFLED-RELATION:F")
            R._resolve_config_from(spec, root)
            self.assertEqual(spec.config["part_config"]["lib"]["library_load_from"], str(twin))
            self.assertNotEqual(str(real), str(twin))
            real_spec = R.spec_for("F")
            R._resolve_config_from(real_spec, root)
            self.assertEqual(real_spec.config["part_config"]["lib"]["library_load_from"], str(real))


if __name__ == "__main__":
    unittest.main()
