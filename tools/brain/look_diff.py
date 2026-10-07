# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 23:26 +0400 — PREREG-EYE-1 §2 item 6 (the instrument)
# + §3 G-DUAL-LOOK: the chosen look's replay reader — the flag-on replay, the look rows extracted, the tee proof.
"""tools/brain/look_diff.py — replay a closed tape under the E1 code with the chosen look ON (the instrument's knob:
`mind._look` set after construction, never a genome line of this law's), writing DIR/journal.jsonl (the E1 replay's own)
and DIR/look-rows.jsonl (one row per fired look, extracted from the journal — the instrument only observes).
With `--plain DIR2` a second run of the same replay WITHOUT the extraction is compared byte-for-byte (G-DUAL-LOOK).

Usage: PYTHONPATH=. python3 -m tools.brain.look_diff --genome G --tape T --out DIR [--limit-canvases N] [--plain DIR2]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from creature import replay as _replay                      # noqa: E402
from creature.mind import Mind                              # noqa: E402


def _install_look() -> None:
    orig_init = Mind.__init__

    def patched(self, *a, **kw):
        orig_init(self, *a, **kw)
        self._look = {"on": True, "instrument": "tools/brain/look_diff.py"}

    Mind.__init__ = patched


def _cut(tape: Path, n: int, work: Path) -> Path:
    files = sorted(tape.glob("2026-*.jsonl")) if tape.is_dir() else [tape]
    cut_dir = work / "_prefix_tape"
    cut_dir.mkdir(parents=True, exist_ok=True)
    src_payload = (tape / "payload") if tape.is_dir() else (tape.parent / "payload")
    if src_payload.exists() and not (cut_dir / "payload").exists():
        import os
        os.symlink(src_payload.resolve(), cut_dir / "payload")
    cut = cut_dir / "cut.jsonl"
    eye = 0
    with cut.open("w") as cf:
        done = False
        for f in files:
            if done:
                break
            for line in f.open():
                if done:
                    break
                cf.write(line)
                r = json.loads(line)
                if r.get("sense") == "eye":
                    eye += 1
                    if eye >= n:
                        done = True
    return cut


def run(genome: Path, tape: Path, out: Path, limit: int = 0) -> Path:
    _install_look()
    out.mkdir(parents=True, exist_ok=True)
    src = _cut(tape, limit, out) if limit > 0 else tape
    journal = _replay.run_replay(Path(genome), src, out, close=(limit == 0))
    rows = []
    for line in journal.read_text().splitlines():
        r = json.loads(line)
        if r.get("kind") == "brain" and r.get("act") == "turn" and "look" in r:
            rows.append({"seq": r.get("seq"), "moment": (r.get("moment")),
                         "scene": r.get("scene"), **r["look"],
                         "said": [w for w in (r.get("say") or {}).get("words", [])] if r.get("say") else None})
    with (out / "look-rows.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return journal


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genome", required=True)
    ap.add_argument("--tape", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit-canvases", type=int, default=0)
    ap.add_argument("--plain", default="")
    args = ap.parse_args(argv)
    journal = run(Path(args.genome), Path(args.tape), Path(args.out), args.limit_canvases)
    print(f"look_diff wrote {journal} and {Path(args.out) / 'look-rows.jsonl'}")
    if args.plain:
        plain_out = Path(args.plain)
        plain_out.mkdir(parents=True, exist_ok=True)
        plain_journal = run(Path(args.genome), Path(args.tape), plain_out, args.limit_canvases)
        same = journal.read_bytes() == plain_journal.read_bytes()
        print(f"G-DUAL-LOOK: journal {'BYTE-IDENTICAL' if same else 'DIFFERS'} to the plain run")
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
