# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:5x +0400 — PREREG-INHERIT §5 + AMENDMENT 1: the reader of the eight lives' grades.
"""read_inherit.py <out.md> — reads /data/dev/genome-lives/inh-<arm>-t<T>/grade/grade.json and prints the marks.
A life whose grade is missing reads MISSING by name; a mark that needs it reads NOT GRADABLE (never pass by absence, #243 (4))."""
import json, math, sys
from pathlib import Path

LIVES = Path("/data/dev/genome-lives")
ARMS = {"C": "c", "B": "b", "N": "n"}
TS = (1, 1000, 10000)


def grade(arm, T):
    p = LIVES / f"inh-{ARMS[arm]}-t{T}" / "grade" / "grade.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def m(g, mark):
    """(value, n) by AMENDMENT 1: M1 and M3 = «over ALL» (forced), M2a = the refusal rate."""
    if g is None or mark not in g.get("bars", {}):
        return None
    b = g["bars"][mark]
    if mark in ("M1", "M3"):
        return (b.get("all"), b.get("n_all"), b.get("value"), b.get("n"))
    return (b.get("value"), b.get("n"), b.get("false_refusal"), b.get("n_fr"))


def sign_test(ga, gb, mark="M1"):
    """exact one-sided sign test on the items both lives carry: a right where b wrong, against b right where a wrong."""
    if ga is None or gb is None:
        return None
    ia = {x["item_id"]: bool(x["correct"]) for x in ga["items"]["fresh"][mark] if "item_id" in x}
    ib = {x["item_id"]: bool(x["correct"]) for x in gb["items"]["fresh"][mark] if "item_id" in x}
    both = sorted(set(ia) & set(ib))
    up = sum(1 for k in both if ia[k] and not ib[k]); dn = sum(1 for k in both if ib[k] and not ia[k])
    n = up + dn
    p = sum(math.comb(n, k) for k in range(up, n + 1)) / 2 ** n if n else None
    return {"paired": len(both), "a_only": up, "b_only": dn, "p": p}


def decide(a, b, margin, kind):
    """kind 'not_below': a >= b - margin ; kind 'gap': a - b >= margin. UNDERPOWERED under n 100; NOT GRADABLE when missing."""
    if a is None or b is None or a[0] is None or b[0] is None:
        return "NOT GRADABLE (a grade is missing)"
    if min(a[1] or 0, b[1] or 0) < 100:
        return f"UNDERPOWERED (n {a[1]} / {b[1]}) reading {a[0]:.3f} vs {b[0]:.3f}"
    ok = (a[0] >= b[0] - margin) if kind == "not_below" else (a[0] - b[0] >= margin)
    return f"{'PASS' if ok else 'FAIL'}: {a[0]:.3f} (n {a[1]}) vs {b[0]:.3f} (n {b[1]}), difference {a[0]-b[0]:+.3f}, bar {'≥ −' if kind=='not_below' else '≥ '}{margin}"


def main(out):
    G = {(a, T): grade(a, T) for a in ARMS for T in TS}
    L = ["# INHERIT — the readings (written by read_inherit.py; nothing here is typed by hand)", ""]
    L += ["| Life | M1 over all (n) | M1 covered (n) | M2a refusal (n) | false refusal | M3 over all (n) | M2b | M6 pooled covered (n) |", "|---|---|---|---|---|---|---|---|"]
    for a in ARMS:
        for T in TS:
            g = G[(a, T)]
            if g is None:
                L.append(f"| {a} T {T} | MISSING | | | | | | |"); continue
            m1, m2, m3 = m(g, "M1"), m(g, "M2a"), m(g, "M3")
            f = lambda v: "absent" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
            m6 = g.get("M6_pooled", {})
            L.append(f"| {a} T {T} | {f(m1[0])} ({m1[1]}) | {f(m1[2])} ({m1[3]}) | {f(m2[0])} ({m2[1]}) | {f(m2[2])} | {f(m3[0])} ({m3[1]}) | {f(g['bars'].get('M2b',{}).get('value'))} | {f(m6.get('covered'))} ({m6.get('n_covered')}) |")
    L += ["", "## The marks", ""]
    c1, b1, n1, c4, b4 = G[("C", 1)], G[("B", 1)], G[("N", 1)], G[("C", 10000)], G[("B", 10000)]
    for mk in ("M1", "M2a", "M3"):
        L.append(f"- **I1 BORN KNOWING, {mk}** (C at T 1 against B at T 10,000): {decide(m(c1, mk), m(b4, mk), 0.05, 'not_below')}")
    L.append(f"- **I2 THE KICK, M1** (C at T 1 against B at T 1; bar by AMENDMENT 1): {decide(m(c1,'M1'), m(b1,'M1'), 0.15, 'gap')} · sign test {sign_test(c1, b1)}")
    L.append(f"- **I3 THE PARENT'S KNOWLEDGE, M1** (C at T 1 against N at T 1): {decide(m(c1,'M1'), m(n1,'M1'), 0.15, 'gap')} · sign test {sign_test(c1, n1)}")
    for mk in ("M1", "M2a", "M3"):
        L.append(f"- **I4 NO HARM, {mk}** (C against B, both at T 10,000): {decide(m(c4, mk), m(b4, mk), 0.02, 'not_below')}")
    L.append("")
    Path(out).write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
