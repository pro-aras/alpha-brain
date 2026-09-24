# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:55 +0400 — package marker so
# `python3 -m unittest discover -s tests/brain/arms_soft -t .` (and arms_logic, arms_clauses)
# can import tests.brain.arms_*.* (Python 3.14's unittest loader refuses a start directory
# that isn't importable as a regular package, even though a plain `-m unittest <module.path>`
# invocation resolves namespace packages fine — the two loaders disagree; this repo's own
# convention already solves it the same way, see tests/genome/__init__.py). A SHARED ancestor
# across all three B1 builders (Builder 1: tests/brain/arms_library/; Builder 2:
# tests/brain/harness/; Builder 3, here: tests/brain/arms_{soft,logic,clauses}/) — kept
# deliberately empty (no logic, only this comment) so a three-way touch on this exact file
# merges without a real conflict.
