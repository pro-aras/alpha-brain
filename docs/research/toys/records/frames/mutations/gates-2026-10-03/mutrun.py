"""mutrun.py — run ONE unittest module against ONE module whose source is replaced IN MEMORY (the worktree file is never written).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:28 +0400 — new mutation-sweep runner for TOY C's gates.py (the relaunched lane's sweep).

usage: PYTHONPATH=. python3 -B -u scratch/mutgates2/mutrun.py <dotted module> <source file to load as that module> <dotted unittest module>

The module under test is loaded from <source file> under its real dotted name (so its relative imports resolve), registered in sys.modules AND set as the attribute of its package, so that
`from tools.toys.frames import gates as GT` in the tests gets THE MUTANT. The runner prints `MUTANT-LOADED: <name> from <path>` and `TESTS-USE-THE-MUTANT: True|False` (the tests' own `GT` must be the
object just loaded: a harness that tests the unmutated file would read every mutant as SURVIVED, and a harness that did not load the mutant at all could never read one as CAUGHT); exit 0 = every test
passed (the mutant SURVIVED), 1 = some test failed or errored (CAUGHT), 3 = the harness itself is wrong (the tests do not use the mutant).
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest


def main(argv) -> int:
    name, path, testmod = argv
    pkg_name, _, leaf = name.rpartition(".")
    pkg = importlib.import_module(pkg_name)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    setattr(pkg, leaf, mod)
    print(f"MUTANT-LOADED: {name} from {path}", flush=True)
    tm = importlib.import_module(testmod)
    uses = [k for k, v in vars(tm).items() if v is mod]
    print(f"TESTS-USE-THE-MUTANT: {bool(uses)} (as {uses})", flush=True)
    if not uses:
        return 3
    suite = unittest.defaultTestLoader.loadTestsFromModule(tm)
    res = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
