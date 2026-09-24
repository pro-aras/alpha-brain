# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:3x +0400 — tests for brain/harness/env.py. The
# record_environment() test shells out to BOTH real interpreters (a few seconds); run_suite is tested
# against a small synthetic test package written to a temp dir, not the real (slow) tests/genome.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain.harness import env


class TestParseUnittestLog(unittest.TestCase):
    def test_parses_ok(self) -> None:
        text = "....\n----------------------------------------------------------------------\nRan 4 tests in 0.012s\n\nOK\n"
        v = env.parse_unittest_log(text)
        self.assertEqual(v, {"ran": 4, "seconds": 0.012, "ok": True, "result_line": "OK"})

    def test_parses_failed(self) -> None:
        text = "F...\n----\nRan 4 tests in 0.5s\n\nFAILED (failures=1)\n"
        v = env.parse_unittest_log(text)
        self.assertFalse(v["ok"])
        self.assertEqual(v["ran"], 4)

    def test_raises_on_garbage(self) -> None:
        with self.assertRaises(env.EnvError):
            env.parse_unittest_log("Traceback (most recent call last):\nImportError: no module named brain\n")

    def test_a_traceback_quoting_ran_does_not_fool_it_without_a_real_result_line(self) -> None:
        # #191's trap in miniature: the word "Ran" appearing in noise must not manufacture a false pass.
        text = "NameError: name 'Ran' is not defined\n"
        with self.assertRaises(env.EnvError):
            env.parse_unittest_log(text)


class TestRecordEnvironment(unittest.TestCase):
    def test_both_interpreters_probed_and_no_sklearn(self) -> None:
        info = env.record_environment()
        self.assertIn("numpy", info["system_python"])
        self.assertIn("torch", info["venv_python"])
        self.assertIsNotNone(info["venv_python"]["torch"])
        self.assertFalse(info["system_python"]["sklearn_present"])
        self.assertFalse(info["venv_python"]["sklearn_present"])

    def test_differ_in_lists_the_declared_mismatches(self) -> None:
        info = env.record_environment()
        # §3.0: "The two interpreters differ in numpy, scipy AND PIL"
        self.assertEqual(set(info["differ_in"]), {"numpy", "scipy", "PIL"})


class TestRunSuite(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        pkg = self.root / "tpkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "test_ok.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertEqual(1, 1)\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_run_suite_reads_the_logs_own_line(self) -> None:
        log_path = self.root / "run.log"
        v = env.run_suite(env.SYSTEM_PYTHON, "tpkg", self.root, log_path)
        self.assertTrue(v["ok"])
        self.assertEqual(v["ran"], 1)
        self.assertEqual(v["returncode"], 0)
        self.assertTrue(Path(v["log_path"]).exists())


if __name__ == "__main__":
    unittest.main()
