# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:20 +0400 — package marker (see tests/__init__.py).
# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:55 +0400 — same marker, independently
# added on the arms side before this merge (see brain/arms/soft/engine.py's commit): so
# `python3 -m unittest discover -s tests/brain/arms_soft -t .` (and arms_logic, arms_clauses)
# can import tests.brain.arms_*.* (Python 3.14's unittest loader refuses a start directory
# that isn't importable as a regular package, even though a plain `-m unittest <module.path>`
# invocation resolves namespace packages fine). A SHARED ancestor across all three B1 builders
# (Builder 1: tests/brain/arms_library/; Builder 2: tests/brain/harness/; Builder 3:
# tests/brain/arms_{soft,logic,clauses}/) — kept comment-only on purpose, which is why this
# add/add conflict merged by keeping both notes rather than picking one.
