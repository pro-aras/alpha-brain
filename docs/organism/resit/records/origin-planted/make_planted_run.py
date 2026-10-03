# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:06 +0400 (from `date`) — the planted runs the VERIFIER asked to SEE (his 20:39 ask on c887b50): the origin ROW, the RESIT.jsonl line and RESIT.md of a run in which one sitting set has
# no tested EARLY item (a learn right after the fresh begin), beside a fully tested control. The runs are the test suite's own fixtures (stub lives; tests/tools/test_resit_origin.py OriginBase) driven through the real
# `resit.py run --mode origin` by path with -B -I. Run from the worktree root:  TMPDIR=<a scratch dir> PYTHONPATH=. python3 -B docs/organism/resit/records/origin-planted/make_planted_run.py <OUTDIR>
"""make_planted_run.py — run the stub origin twice (planted UNTESTED set; fully tested control) and keep the three files each run writes."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from tests.tools.test_resit import brain
from tests.tools.test_resit_origin import OriginBase


class _Run(OriginBase):
    def runTest(self) -> None:           # a TestCase needs one; nothing runs under it
        pass


def one(label: str, outdir: Path, plant: bool) -> dict:
    t = _Run()
    t.setUp()
    try:
        if plant:
            before = t.life.journal_file.read_bytes()
            t.life.rewrite_journal(lambda rows: rows + [brain(1004, "learn")])     # right after the fresh begin (seq 1003): every held item and the why of that set read LATE
            assert before != t.life.journal_file.read_bytes(), "the plant must change the bytes"
        p, res, att, stamp = t.run_origin(states=t.both())
        assert p.returncode == 0, p.stderr + p.stdout
        d = outdir / label
        d.mkdir(parents=True)
        for n in ("ORIGIN.json", "RESIT.jsonl", "RESIT.md"):
            shutil.copy(t.out / n, d / n)
        return json.loads((t.out / "ORIGIN.json").read_text())
    finally:
        t.doCleanups()


def main() -> int:
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    lines = []
    for label, plant in (("planted-untested-set", True), ("control-fully-tested", False)):
        o = one(label, outdir, plant)
        md = (outdir / label / "RESIT.md").read_text().splitlines()[-1]
        jl = json.loads((outdir / label / "RESIT.jsonl").read_text().splitlines()[-1])
        lines += [f"== {label}",
                  f"ORIGIN.json  r9_untested_sets = {o['r9_untested_sets']}",
                  f"ORIGIN.json  r9_reading       = {o['r9_reading']}",
                  f"RESIT.jsonl  r9_untested_sets = {jl['r9_untested_sets']}   r9_reading identical to ORIGIN.json: {jl['r9_reading'] == o['r9_reading']}",
                  f"RESIT.md     {md}",
                  f"r9.by_set    {json.dumps(o['r9']['by_set'])}", ""]
    (outdir / "READINGS.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
