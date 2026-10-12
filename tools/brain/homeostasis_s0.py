#!/usr/bin/env python3
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §0(b): the bench reader.
# Streams a bench life's journal and prints the §0 baseline table: per-1000-canvas windows of the measured
# streams (err, lr, says, asks, fixations, sleep boundaries) PLUS the three SHADOW drives (arousal/boredom/
# fatigue — the prereg §2.2's candidate rules) computed OFFLINE over the real tape: the organism's code is
# untouched. --selftest: the instrument's planted control (RULES §11) — a synthetic tape with a planted err
# ramp + a zero-surprise stretch must move the shadow series in the declared directions, else the instrument
# is refused. Usage: homeostasis_s0.py <journal-dir-or-file>... | --selftest
import json
import statistics
import sys

REST_A, ALPHA, BETA = 0.3, 0.25, 0.02        # arousal: a ← clip(a + α(s−a) + β(REST−a))
GAMMA, DELTA, KAPPA, SLOW = 0.04, 0.10, 0.8, 0.01   # boredom: +γ while s < κ·s̄, else decay δ; s̄ EMA rate
EPS_F, ZETA = 0.001, 0.6                     # fatigue: +ε per canvas; ×(1−ζ) at a sleep boundary


def clip(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def rows(paths):
    for p in paths:
        op = open
        if p.is_dir():
            for f in sorted(p.glob("*.jsonl")):
                yield from lines(f)
        else:
            yield from lines(p)


def lines(f):
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def walk(paths):
    """One pass. Yields ('canvas', err, lr, nfix) | ('say',) | ('ask',) | ('sleep',) rows in order."""
    for d in rows(paths):
        k = d.get("kind", d.get("event", "?"))
        if "cells" in d and "err" in d:
            yield ("canvas", d.get("err"), d.get("lr"), len(d.get("windows") or []))
        elif k == "brain" and d.get("act") == "turn":
            s = d.get("say") or {}
            if s.get("words"):
                yield ("say",)
            if d.get("ask"):
                yield ("ask",)
        elif k == "snapshot" or "replay" in json.dumps(d)[:120]:
            yield ("sleep",)


def table(paths, out):
    a = b = f = slow = None
    slow = 0.0
    a, b, f = REST_A, 0.0, 0.0
    win = []
    wins = []
    n = 0
    win_canvases = 0
    for ev in walk(paths):
        if ev[0] == "canvas":
            _, err, lr, nfix = ev
            s = float(err) if isinstance(err, (int, float)) else 0.0
            a = clip(a + ALPHA * (s - a) + BETA * (REST_A - a))
            slow = slow + SLOW * (s - slow)
            b = clip(b + GAMMA) if s < KAPPA * slow else clip(b - DELTA * b)
            f = clip(f + EPS_F)
            win.append((s, lr if isinstance(lr, (int, float)) else None, nfix, a, b, f))
            n += 1
            win_canvases += 1
            if win_canvases >= 1000:
                wins.append(win)
                win = []
                win_canvases = 0
        elif ev[0] == "sleep":
            f = clip(f * (1 - ZETA))
            win.append(("sleep",))
        else:
            win.append(ev)
    if win:
        wins.append(win)
    print("window  canvases  says  asks  fix/row  err_mean  err_std   lr_mean   arousal[min/max/mean]        boredom[min/max/mean]        fatigue[min/max/mean]   sleeps", file=out)
    for i, w in enumerate(wins):
        cs = [r for r in w if isinstance(r, tuple) and len(r) == 6]
        if not cs:
            continue
        errs = [r[0] for r in cs]
        lrs = [r[1] for r in cs if r[1] is not None]
        fixs = [r[2] for r in cs]
        aa = [r[3] for r in cs]
        bb = [r[4] for r in cs]
        ff = [r[5] for r in cs]
        says = sum(1 for r in w if isinstance(r, tuple) and r and r[0] == "say")
        asks = sum(1 for r in w if isinstance(r, tuple) and r and r[0] == "ask")
        sleeps = sum(1 for r in w if isinstance(r, tuple) and r and r[0] == "sleep")
        print(f"{i:6d}  {len(cs):8d}  {says:4d}  {asks:4d}  {statistics.mean(fixs):8.2f}  "
              f"{statistics.mean(errs):8.4f}  {(statistics.pstdev(errs) if len(errs) > 1 else 0):7.4f}  "
              f"{(statistics.mean(lrs) if lrs else float('nan')):7.3f}  "
              f"{min(aa):.3f}/{max(aa):.3f}/{statistics.mean(aa):.3f}      "
              f"{min(bb):.3f}/{max(bb):.3f}/{statistics.mean(bb):.3f}      "
              f"{min(ff):.3f}/{max(ff):.3f}/{statistics.mean(ff):.3f}   {sleeps:5d}", file=out)
    print(f"total canvases: {n}", file=out)


def selftest():
    """The planted control: a ramp then a flat-zero stretch must move the shadows as declared."""
    import io
    import tempfile
    from pathlib import Path
    tmp = Path(tempfile.mkdtemp(prefix="h0s0-selftest-")) / "synthetic.jsonl"
    with open(tmp, "w") as fh:
        for i in range(3000):
            err = min(1.0, i / 1500.0) if i < 1500 else 0.0   # planted ramp to 1.0, then planted zero surprise
            fh.write(json.dumps({"cells": 1, "err": err, "lr": 1.0, "windows": [1, 2, 3, 4]}) + "\n")
            if i % 500 == 499:
                fh.write(json.dumps({"event": "snapshot"}) + "\n")
    buf = io.StringIO()
    table([tmp], buf)
    text = buf.getvalue()
    lines_out = [l for l in (l2.lstrip() for l2 in text.splitlines()) if l and l[0].isdigit()]
    assert len(lines_out) == 3, f"expected 3 windows, got {len(lines_out)}"
    def triple(line, idx):
        return [float(x) for x in line.split()[idx].split("/")]
    a_hi = triple(lines_out[1], 8)[1]               # window 2 (index 1): arousal max at the ramp top
    b_end = triple(lines_out[2], 9)[1]              # window 3: boredom max after 1500 zero-surprise canvases
    assert a_hi >= 0.6, f"PLANT MISS: arousal did not track the ramp (max {a_hi})"
    assert b_end >= 0.95, f"PLANT MISS: boredom did not hit ceiling on zero surprise (max {b_end})"
    print("SELFTEST PASS — the plant moved the shadows as declared (arousal ramp max "
          f"{a_hi:.3f} ≥ 0.6; boredom after the zero stretch {b_end:.3f} ≥ 0.95)")
    print(text)
    return 0


if __name__ == "__main__":
    from pathlib import Path
    args = sys.argv[1:]
    if args == ["--selftest"]:
        sys.exit(selftest())
    if not args:
        print(__doc__)
        sys.exit(2)
    table([Path(a) for a in args], sys.stdout)
