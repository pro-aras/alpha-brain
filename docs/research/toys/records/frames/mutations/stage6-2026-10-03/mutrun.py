"""mutrun.py — run ONE or SEVERAL unittest modules against ONE module whose source is replaced IN MEMORY (the worktree file is never written).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:28 +0400 — new mutation-sweep runner for TOY C's gates.py (the relaunched lane's sweep).
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:54 +0400 — the unittest argument may be a COMMA-SEPARATED list of modules (report.py is tested by two files); with ONE module the behaviour is unchanged (the gates sweep's).

usage: PYTHONPATH=. python3 -B -u scratch/mutgates2/mutrun.py <dotted module> <source file to load as that module> <dotted unittest module>[,<dotted unittest module>...]

The module under test is loaded from <source file> under its real dotted name (so its relative imports resolve), registered in sys.modules AND set as the attribute of its package, so that
`from tools.toys.frames import gates as GT` in the tests gets THE MUTANT. The runner prints `MUTANT-LOADED: <name> from <path>` and `TESTS-USE-THE-MUTANT: True|False` (EVERY test module's own binding must be the
object just loaded: a harness that tests the unmutated file would read every mutant as SURVIVED, and a harness that did not load the mutant at all could never read one as CAUGHT); exit 0 = every test
passed (the mutant SURVIVED), 1 = some test failed or errored (CAUGHT), 3 = the harness itself is wrong (a test module does not use the mutant).
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
import unittest


def main(argv) -> int:
    name, path, testmods = argv
    pkg_name, _, leaf = name.rpartition(".")
    pkg = importlib.import_module(pkg_name)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    setattr(pkg, leaf, mod)
    print(f"MUTANT-LOADED: {name} from {path}", flush=True)
    tms = [importlib.import_module(t) for t in testmods.split(",")]
    uses = [[k for k, v in vars(tm).items() if v is mod] for tm in tms]
    print(f"TESTS-USE-THE-MUTANT: {all(bool(u) for u in uses)} (as {uses})", flush=True)
    if not all(bool(u) for u in uses):
        return 3
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(tm) for tm in tms])
    res = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
