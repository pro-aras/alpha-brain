#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-22 18:32 +0400 — THE INVENTORY AS A SCRIPT (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-2; his 23:08 rule): walks
# every declared line of a genome to (1) a consumer call site in creature/genes.py's RUNS registry, (2) the parser's own value fields
# (every `g["<attr>"] = ...` the parser writes inside that gene's branch) to a READ of `.<attr>` outside the parser and the dataclass,
# and (3) for every SENSE line of the genome TEXT, a branch naming that sense in creature/mind.py:consume. One row per line:
# MADE / VALUE-UNREAD / DECLARED-ONLY / OFF; exit 1 when any DECLARED-ONLY row exists (a pre-flight refuses on it). POSITIVE CONTROL:
# on genome/G5.genome at 0b51288 it must find the 11:16 inventory's three rows — SENSE ear-sound (no mind branch; row 15),
# HEBB window (row 27) and RECALL k (row 53) value-unread. A first draft written in an UNQUOTED heredoc lost its backticks to the shell
# (#232's lesson, again) and counted the parser's own `g["recall_k"] < 1` validation as a read — both fixed here.
"""The inventory: declared line -> consumer, by script."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path


def parser_attrs(machinery_src: str) -> dict:
    """gene -> the g['<attr>'] names the parser assigns inside that gene's branch (read from the source, never guessed)."""
    out = {}; gene = None
    for line in machinery_src.splitlines():
        m = re.search(r'gene == "([A-Z_-]+)"', line)
        if m and ("elif" in line or "if " in line):
            gene = m.group(1)
        if gene:
            for a in re.findall(r'g\["([a-z_0-9]+)"\]\s*=', line):
                if a != "declared":
                    out.setdefault(gene, set()).add(a)
    return out


def source_files(tree: Path):
    for d in ("genome", "creature", "creature/senses", "tools"):
        for f in sorted((tree / d).glob("*.py")):
            yield f


def grep_reads(tree: Path, attr: str) -> int:
    """Lines that READ the attribute (`.attr` / `['attr']` / `["attr"]`) outside the parser's own dict-building, the dataclass field
    and the `required` list in genome/machinery.py. A value with 0 reads is declared, not consumed (#180)."""
    n = 0
    for f in source_files(tree):
        for line in f.read_text(errors="replace").splitlines():
            s = line.strip()
            if s.startswith("#") or f.name == "inventory.py":
                continue
            if f.name == "machinery.py" and (re.search(r'g\["' + attr + r'"\]', line) or re.match(attr + r'\s*:', s) or re.search(r'"' + attr + r'",', line)):
                continue
            if re.search(r'\.' + attr + r'\b', line) or re.search(r"\['" + attr + r"'\]", line) or re.search(r'\["' + attr + r'"\]', line):
                n += 1
    return n


def consume_text(tree: Path) -> str:
    src = (tree / "creature" / "mind.py").read_text(errors="replace")
    i = src.find("def consume("); j = src.find("\n    def ", i + 10)
    return src[i:j if j > 0 else None]


def sense_names(genome_text: str):
    for line in genome_text.splitlines():
        if line.startswith("SENSE "):
            parts = line.split()
            if len(parts) > 1:
                yield parts[1]


# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2.6 (A4L-EXPLORE-REPORT §0 item 10 (a)): a declared key resolves through
# its OWN RUNS row only. The old rule also accepted the key's BASE (`ACT_VALUE` through `ACT`'s row), so a key the Mind's refusal law
# refuses (creature/genes.py:unwired — exact keys) read MADE here: the inventory's MADE proved less than it said. The two agree now by
# construction (tests/creature/test_a42_b1.py: the real registry with WORLD_GAME's own row removed — WORLD's stays — must read NO SITE).
def site_of(gene: str, wired) -> str:
    """The RUNS site of one declared key, by its own row only — never its base's."""
    return "genes.RUNS" if gene in wired else "NO SITE in genes.RUNS"


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("genome"); ap.add_argument("--tree", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args(argv); tree = Path(a.tree); sys.path.insert(0, str(tree))
    from genome.machinery import parse_genome
    from creature import genes
    text = Path(a.genome).read_text()
    off = [l for l in text.splitlines() if l.startswith("#OFF")]
    try:
        g = parse_genome(text)
    except Exception as e:
        print(f"[inventory] {a.genome}: REFUSED by the parser - {str(e)[:160]}"); return 2
    attrs = parser_attrs((tree / "genome" / "machinery.py").read_text())
    wired = {gene for layer in genes.RUNS.values() for gene, site in layer.items() if site is not None}
    ctext = consume_text(tree)
    rows = []; bad = 0
    for gene in sorted(g.declared):
        base = gene.split("_")[0]          # the parser's attrs are keyed by the base branch; the RUNS row is the key's own (site_of)
        site = site_of(gene, wired)
        unread = [x for x in sorted(attrs.get(base, set())) if grep_reads(tree, x) == 0]
        status = "DECLARED-ONLY" if site.startswith("NO") else ("VALUE-UNREAD" if unread else "MADE")
        bad += status == "DECLARED-ONLY"
        rows.append((gene, status, site, ",".join(unread) or "-"))
    published = set()
    for f in source_files(tree):
        published |= set(re.findall(r'publish\("([a-z_-]+)"', f.read_text(errors="replace")))
    for name in sense_names(text):
        if name in ("eye", "ear"):
            continue
        if name not in published:
            rows.append((f"SENSE {name}", "MADE", "a channel, not a tape row (no publish() names it); its value is read where the parser's field is", "-"))
        elif ('"' + name + '"') in ctext:
            rows.append((f"SENSE {name}", "MADE", "published by a sense thread and named in creature/mind.py:consume", "-"))
        else:
            rows.append((f"SENSE {name}", "DECLARED-ONLY", "published by a sense thread; NO branch naming \"" + name + "\" in creature/mind.py:consume", "-")); bad += 1
    for gene in sorted(set(attrs) - set(k.split("_")[0] for k in g.declared) - {"SENSE", "WORLD"}):
        if re.search(r"^" + gene + r"\s", text, re.M):
            unread = [x for x in sorted(attrs[gene]) if grep_reads(tree, x) == 0]
            rows.append((gene, "VALUE-UNREAD" if unread else "MADE", "parsed into Genome fields", ",".join(unread) or "-"))
    w = max(len(r[0]) for r in rows) + 2
    for r in rows:
        print(f"[inventory] {r[0]:<{w}} {r[1]:<14} {r[2][:70]:<72} unread: {r[3]}")
    for l in off:
        print(f"[inventory] OFF  {l[:110]}")
    vu = sum(1 for r in rows if r[1] == "VALUE-UNREAD")
    print(f"[inventory] {a.genome}: {len(rows)} rows - DECLARED-ONLY {bad} - VALUE-UNREAD {vu} - OFF {len(off)} -> {'REFUSE (a DECLARED-ONLY organ)' if bad else 'clear'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
