# B1 Builder 2 — report (Sonnet 5, docs/brain/B1-PREREG.md §9 row 1)

Branch: `b1-harness` (worktree `/data/dev/genome-wt-b1-harness`, off master 94546ce).

## Step 1 — the `Arm` protocol: FROZEN, commit `ac7d2ff724e492c0e189d48c7965c001fe6ed66d`

**Builders 1 and 3 may start against this commit.** Import `brain.protocol` and `brain.glance_cache`.

Files: `brain/protocol.py`, `brain/glance_cache.py`, `brain/harness/dummy_arm.py`,
`tests/brain/harness/{test_protocol,test_glance_cache}.py`, package `__init__.py` markers.

Suite: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19
/data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain/harness -t .` — log's own line:
**`Ran 39 tests in 0.133s` / `OK`** (log: `/data/dev/brain-runs/tmp/b1-protocol-test-1.log`, this
session's scratch, not committed).

### The protocol's signature (what to import and build against)

```python
from brain.protocol import (
    Arm, Answer, AnswerKind,                    # the structural protocol + its return type
    CUE_MARKS, RELATION_CUES,                   # the 14-mark vocabulary; relation cues = all but NAME/POINT/IS
    TAPE_KINDS, EXAMPLE_ROWS,                   # one worked row per kind, sha computed
    op_row, op_name, is_row_operand, is_name_operand,
    make_row, row_sha, verify_row, validate_tape_row,
    VALENCE_REWARD, VALENCE_NO,
    right_matches, HarnessContract,             # the learn=True / fit_event dispatch, as code
    make_arm, has_why, has_rule,
    check_arm,                                  # conformance checker; ships with a planted-mutation control
)
from brain.glance_cache import Cache, CacheWriter   # read-only reader; only brain/world/build_cache.py writes
```

**Construction is `make_arm(YourArmClass, seed, config)`** — never `YourArmClass(seed, config)` directly
(one call site for the whole estate). `config` always carries `cache_dir`, `run_dir`, `seed`, `interpreter`
(`RESERVED_CONFIG_KEYS`); read any other key your arm declares.

**Required methods** (see `brain/harness/dummy_arm.py` for a working, minimal implementation of all of
them): `__init__(seed, config)` (called via `make_arm`, never directly) · `fit_event(row, valence=None)` ·
`answer(ask_row, learn=False) -> Answer` · `sleep(steps)` · `state_sha() -> str` · `snapshot(path)` ·
`load(path)` · `cost() -> {"events": int, "ms": float}`.

**Optional:** `why(ask_row) -> List[int]` (tape seqs, U4a) · `rule(cue: List[str]) -> {"text": str,
"executable": Callable[[dict], Answer]}` (U4b — `cue` is the SAME list shape an ASK row's `cues` field
carries, so CHAIN's `["AFTER","OTHER_CASE"]` is one call). Absence is detected by `has_why`/`has_rule`, not
by `hasattr` in your own code — use the helpers so a future detection change has one call site.

**The row shapes** (full detail in `brain/protocol.py`'s own docstring and comments, and in
`EXAMPLE_ROWS`): `TEACH {glance_row:int, name:str}` · `ASK {cues:[str,...], operands:[op,...],
candidate_rows: List[int]|None, answer_kind: "NAME"|"PICK"|"YESNO"}` · `FEEDBACK {ask_seq:int, right:Any}` ·
`ARRIVAL {what:str}` · `SLEEP {steps:int}` · `TEST_BEGIN/TEST_END {sitting:str}`. **Operands are glyph rows
(`op_row`) for every cue except POINT/IS, which carry a heard name (`op_name`)** — enforced by
`validate_tape_row`, not just documented.

**`Answer.value` per kind:** NAME→str, PICK→**int index into that ask's own `candidate_rows`** (never a
cache row id), YES/NO/UNKNOWN/NOTHING/SILENT→None, RESEMBLES→str.

**`valence`** is one of the two string literals `VALENCE_REWARD="reward"` / `VALENCE_NO="no"`, computed by
the HARNESS from your arm's own prior answer to the training ASK — an arm never sees `right` directly, only
the derived valence on the matching FEEDBACK row's `fit_event` call.

**The `learn=True`/`fit_event` split** (pinned as code in `HarnessContract`, not prose): TEACH/ARRIVAL →
`fit_event(row, valence=None)`. SLEEP → `arm.sleep(steps)`, never `fit_event`. Training ASK → `answer(row,
learn=True)` (may mutate bookkeeping/context state; the actual weight update is expected on the FEEDBACK
that follows) THEN `fit_event(row, valence=None)`. FEEDBACK → `fit_event(row, valence=REWARD|NO)`. TEST-
sitting ASK → `answer(row, learn=False)`, and **`state_sha()` must not move** — `HarnessContract.test_ask`
raises `ProtocolError` if it does (§5.1 control 0e, INSTRUMENT-VOID).

### What I could not settle myself (raised here, not worked around)

None yet at this step — §4's table left the shapes above genuinely open (not contradictory), so pinning
them was Builder 2's own call per the PREREG's "the seam first, by the third hand" framing, not a clause
that needed the seat's decision. If Builders 1 or 3 hit a case this file doesn't cover, RAISE it — do not
silently extend the protocol in your own arm's folder.

---

*(this file grows as the remaining steps land; see the bottom for the final branch tip, file sizes, every
suite's `Ran` line, stage −1's status and the three hardest clauses — B1-PREREG.md's own ask of this
report.)*
