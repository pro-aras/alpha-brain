# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 17:5x +0400 — PREREG-MOUTH-INCREMENTAL §2 item 7 (the
# instrument) + §3 G-DUAL: the dual-mouth replay — the turn speaks the OLD mouth, the instrument only OBSERVES.
"""tools/brain/mouth_diff.py — replay a closed tape with produce_believed dispatched through BOTH mouths:
the turn still speaks the OLD mouth (produce_believed — the journal is byte-identical to the plain replay,
G-DUAL's assertion), and every call is ALSO computed by produce_incremental; one side row per call lands in
DIR/mouth-diff.jsonl: {seq, moment, source, target, old, new, equal, old_len, new_len, n_candidates, n_readbacks}.

Usage: PYTHONPATH=. python3 -m tools.brain.mouth_diff --genome G --tape T --out DIR [--limit-canvases N]
(a mid-tape cut after the Nth eye row, close=False). The R-DIFF reading aggregates the side rows."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from brain.scene import learners as Lr                      # noqa: E402
from creature import replay as _replay                      # noqa: E402
from creature.mind import Mind                              # noqa: E402

_CURRENT: dict = {"row": None}


def _install_dispatcher(side_out) -> None:
    original = Lr.produce_believed

    def dispatched(road, X, target, rng_factory, budget=Lr.MOUTH_BUDGET):
        old = original(road, X, target, rng_factory, budget)
        new = Lr.produce_incremental(road, X, target, rng_factory, budget)
        row = _CURRENT.get("row") or {}
        meta = row.get("meta") or {}
        side_out.write(json.dumps({
            "seq": row.get("seq"), "moment": meta.get("moment"), "source": meta.get("source"),
            "scene": meta.get("scene"), "target": int(target),
            "old": old.get("spoken"), "new": new.get("spoken"),
            "equal": old.get("spoken") == new.get("spoken"),
            "old_len": len(old.get("spoken") or []), "new_len": len(new.get("spoken") or []),
            "n_candidates": old.get("n_candidates"), "n_readbacks": new.get("n_readbacks"),
            "old_reason": old.get("reason"), "new_reason": new.get("reason"),
        }) + "\n")
        return old

    Lr.produce_believed = dispatched

    orig_consume = Mind.consume

    def consume_spy(self, row):
        _CURRENT["row"] = row
        try:
            return orig_consume(self, row)
        finally:
            _CURRENT["row"] = None

    Mind.consume = consume_spy


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genome", required=True)
    ap.add_argument("--tape", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit-canvases", type=int, default=0)
    args = ap.parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    side = (out_dir / "mouth-diff.jsonl").open("w")
    _install_dispatcher(side)
    try:
        if args.limit_canvases > 0:
            # a mid-tape cut: rows through the Nth eye row, close=False (replay.py's own rule); the cut file lives in
            # its own tape dir whose payload is a SYMLINK to the source tape's (replay.py's own form, read-only)
            rows_path = Path(args.tape)
            files = sorted(rows_path.glob("2026-*.jsonl")) if rows_path.is_dir() else [rows_path]
            cut_dir = out_dir / "_prefix_tape"
            cut_dir.mkdir(exist_ok=True)
            src_payload = (rows_path / "payload") if rows_path.is_dir() else (rows_path.parent / "payload")
            link = cut_dir / "payload"
            if src_payload.exists() and not link.exists():
                import os
                os.symlink(src_payload.resolve(), link)
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
                            if eye >= args.limit_canvases:
                                done = True
            journal = _replay.run_replay(Path(args.genome), cut, out_dir, close=False)
        else:
            journal = _replay.run_replay(Path(args.genome), Path(args.tape), out_dir, close=True)
    finally:
        side.close()
    print(f"mouth_diff wrote {journal} and {out_dir / 'mouth-diff.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
