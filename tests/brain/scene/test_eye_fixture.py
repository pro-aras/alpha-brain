# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:00 +0400 — S1a step 0 (PREREG-R3-TONIGHT §S1a «The eye»): the builder's FIRST
# test re-runs the seat's docs/brain/r3/seat_eye_fixture.py under /usr/bin/python3 against THIS tree's brain/genome and
# must reproduce B1.1's cached glances byte for byte (3/3 rows) before any scene is rendered. The fixture is run through
# runpy with THIS repo first on sys.path, and the modules' own __file__ are checked, so no other tree answers for ours
# (#199, #242: a script run by path puts its own folder on sys.path). -B: nothing written into the seat's tree.
from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURE = Path("/data/dev/genome-wt-brain3/docs/brain/r3/seat_eye_fixture.py")
B11_CACHE = Path("/data/dev/brain-runs/b1.1/cache/20261001")
SYSTEM_PYTHON = Path("/usr/bin/python3")

_WRAP = r"""
import sys, runpy
sys.path.insert(0, {repo!r})
runpy.run_path({fixture!r}, run_name="__main__")
import brain, genome
print("MODULE brain", brain.__file__)
print("MODULE genome", genome.__file__)
"""


@unittest.skipUnless(FIXTURE.exists() and B11_CACHE.exists() and SYSTEM_PYTHON.exists(),
                     "the seat's eye fixture or B1.1's cache is not on this box")
class TestEyeFixture(unittest.TestCase):
    def test_b11_glances_reproduced_byte_for_byte_3_of_3(self) -> None:
        env = dict(os.environ)
        env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        env.pop("PYTHONPATH", None)
        code = _WRAP.format(repo=str(REPO), fixture=str(FIXTURE))
        out = subprocess.run([str(SYSTEM_PYTHON), "-B", "-c", code], capture_output=True, text=True, env=env,
                             cwd=str(REPO), timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr[-3000:])
        lines = out.stdout.splitlines()
        self.assertTrue(any(l.startswith("interpreter /usr/bin/python3 ") for l in lines), out.stdout)
        rows = [l for l in lines if l.startswith("row ")]
        self.assertEqual(len(rows), 3, out.stdout)
        for l in rows:
            self.assertTrue(l.endswith("png-sha match True · glances byte-equal True"), l)
        mods = dict(l.split(" ", 2)[1:] for l in lines if l.startswith("MODULE "))
        self.assertEqual(Path(mods["brain"]).resolve(), (REPO / "brain" / "__init__.py").resolve())
        self.assertEqual(Path(mods["genome"]).resolve(), (REPO / "genome" / "__init__.py").resolve())


if __name__ == "__main__":
    unittest.main()
