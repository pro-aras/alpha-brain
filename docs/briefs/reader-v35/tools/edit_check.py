import sys
p = "/data/dev/genome-wt-reader35/tools/lives/check.py"
s = open(p).read()
STAMP = sys.argv[1]

# 1) helpers after sizing_wording
anchor = "def main(argv) -> int:\n"
helpers = f'''# edit: Claude (Opus 5.5, reader v3.5 builder), {STAMP} — A4-LADDER-2-PREREG ADDENDUM §7(2) item 2: the «MISMATCH: dropped 0 != confirmed N»
# line fired on FLOOR', COST, ACT, LINE and NURSERY — genomes that never declare `; drop confirmed` (only A4L2-ALL does). The body writes
# `glances_dropped 0` on EVERY write (creature/body.py, #164), so the key's presence says nothing about the clause: the comparison is
# gated on the genome's OWN SURPRISE clause (genome.machinery.parse_genome's declared["SURPRISE"]["drop"] == "confirmed", the key
# creature/genes.py RUNS for the drop) read from $ROOT/GENOME.genome (tools/lives/launch.sh's copy), else unit.env's GENOME= path.
def genome_text(root):
    """The run's genome text: $ROOT/GENOME.genome, else the file unit.env's GENOME= names; None when neither is readable."""
    root = Path(root)
    p = root / "GENOME.genome"
    if p.exists():
        try:
            return p.read_text()
        except OSError:
            return None
    env = root / "unit.env"
    if env.exists():
        try:
            for line in env.read_text().splitlines():
                if line.startswith("GENOME="):
                    g = Path(line.split("=", 1)[1].strip())
                    return g.read_text() if g.exists() else None
        except OSError:
            return None
    return None


def drop_declared(root):
    """True / False: the genome declares SURPRISE's `; drop confirmed` clause; None when the genome is absent or refuses to parse."""
    text = genome_text(root)
    if text is None:
        return None
    try:
        tree = str(Path(__file__).resolve().parents[2])
        if tree not in sys.path:
            sys.path.insert(0, tree)
        from genome.machinery import parse_genome
        return (parse_genome(text).declared.get("SURPRISE") or {{}}).get("drop") == "confirmed"
    except Exception:
        return None


def glances_line(status, declared) -> str:
    """The glances line: MISMATCH only when the genome DECLARES `; drop confirmed` AND dropped != confirmed; «not declared» when it does
    not (dropped 0 is the ordinary reading there); «not recorded» when the body never wrote the key (an older body)."""
    gc, gd = status.get("glances_confirmed"), status.get("glances_dropped")
    if gd is None:
        eq = "not recorded (glances_dropped absent — an older body)"
    elif declared is True:
        eq = "OK: dropped == confirmed (declared: `; drop confirmed`)" if gd == gc else f"MISMATCH: dropped {{gd}} != confirmed {{gc}} (the genome declares `; drop confirmed`)"
    elif declared is False:
        eq = "not declared (no `; drop confirmed` in the genome; dropped 0 is the ordinary reading)"
        if gd != 0:
            eq += f" — UNEXPECTED: dropped {{gd}} under an undeclared clause (an undeclared drop must never drop a glance)"
    else:
        eq = "genome unknown (no parseable GENOME.genome / unit.env genome at the root): the drop clause not read, dropped vs confirmed not compared"
    return (f"[check] glances confirmed {{status.get('glances_confirmed', 'not recorded')}} "
            f"surprised {{status.get('glances_surprised', 'not recorded')}} dropped {{status.get('glances_dropped', 'not recorded')}} — {{eq}}")


'''
assert s.count(anchor) == 1
s = s.replace(anchor, helpers + anchor)

# 2) main(): the old four lines -> one call
old = '''    gc, gd = status.get("glances_confirmed"), status.get("glances_dropped")
    eq = "not recorded (glances_dropped absent — an older body, or the clause is undeclared)" if gd is None \\
        else ("OK: dropped == confirmed" if gd == gc else f"MISMATCH: dropped {gd} != confirmed {gc}")
    print(f"[check] glances confirmed {status.get('glances_confirmed', 'not recorded')} "
          f"surprised {status.get('glances_surprised', 'not recorded')} dropped {status.get('glances_dropped', 'not recorded')} — {eq}")
'''
assert s.count(old) == 1, "old glances block not found"
new = f'''    print(glances_line(status, drop_declared(root)))   # edit: Claude (Opus 5.5, reader v3.5 builder), {STAMP} — gated on the genome's own clause (ADDENDUM §7(2) item 2)
'''
s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
