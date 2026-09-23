# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 00:20 +0400 — A8: gate G4-1, the writer sweep (docs/G4-PREREG.md
# §4). An AST walk (not a text grep, #113/#191): no open()/Path.write_*/np.save whose first argument's text
# contains "state", "journal" or "memory"; no import of genome.machinery.Organism in a true SENSE module.
#
# Reading (docs/G4-PREREG.md §4's own row, cross-checked against §2.7 and G4-DESIGN.md §2/B3): the walked file
# set is creature/senses/*.py, creature/world_maker.py, creature/ask.py for the writer check (senses AND the
# voice must never write memory -- PREREG §2.7 says the voice "never writes memory" in as many words). The
# "no Organism import" check applies only to creature/senses/*.py and creature/world_maker.py: those are the
# actual SENSES (I1, B3: "a sense publishes an immutable snapshot ... the mind is the only reader of the tape
# and the only writer of memory") -- creature/ask.py is the voice, not a sense, and PREREG §2.7 explicitly
# requires it to load a private Organism ("Organism.load + ledger) into a private Organism"), so barring
# Organism from ask.py would contradict its own contract. This reading is called out for Claude to overturn
# if it disagrees; the writer check (no state/journal/memory paths) applies to all three regardless.
from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = ("state", "journal", "memory")
WRITE_METHODS = {"write_text", "write_bytes", "save", "savez", "savez_compressed"}


def _flatten(node: ast.AST, env: Optional[dict] = None) -> Optional[str]:
    """Best-effort static text of a path-like expression: string/f-string literals, `a / b` chains,
    `Path(...)` calls, `.attr` chains (the attribute name itself is ignored, e.g. `.parent`), and a
    bare local variable resolved against `env` (a same-module `name -> flattened text` map, built by
    `_build_env` from simple `x = <flattenable>` assignments — not full dataflow, but enough to catch
    `p = Path(root) / "state" / "x.json"; open(p, "w")`, which a purely-inline walk would miss)."""
    env = env or {}
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            else:
                parts.append("")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _flatten(node.left, env)
        right = _flatten(node.right, env)
        if left is None and right is None:
            return None
        return f"{left or ''}/{right or ''}"
    if isinstance(node, ast.Call):
        callee = node.func
        name = callee.id if isinstance(callee, ast.Name) else (callee.attr if isinstance(callee, ast.Attribute) else None)
        if name == "Path" and node.args:
            return _flatten(node.args[0], env)
        return None
    if isinstance(node, ast.Attribute):
        return _flatten(node.value, env)
    if isinstance(node, ast.Name):
        return env.get(node.id)
    return None


def _first_arg_text(call: ast.Call, env: dict) -> Optional[str]:
    if not call.args:
        return None
    return _flatten(call.args[0], env)


# edit: Claude (Fable 5.1), 2026-09-23 17:00 +0400 — SIT-ATOMIC-SWEEP-0923 FIX 2 (docs/briefs/SEAM5-WITNESS-SOUND-REPORT.md item 5): the env is
# built PER FUNCTION SCOPE — the same change, line for line in its logic, as tools/gate_g4.py's `_scope_map`/`_build_env` (see the note
# there): one flat module-wide env let a same-named local in another function hide a planted leak from this walker too. A def's env is
# seeded from its enclosing scope's finished env and takes only its own simple assignments, in source order; a sibling's locals never
# enter it; class bodies stay transparent (a widening only). `_flatten` is unchanged.
_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def _scope_map(tree: ast.AST) -> dict:
    """node -> its nearest enclosing function scope (the Module node for top-level code). A def/lambda node itself belongs
    to the scope it is written in; everything under it belongs to the def."""
    scope_of: dict = {tree: tree}

    def visit(node, scope):
        for child in ast.iter_child_nodes(node):
            scope_of[child] = scope
            visit(child, child if isinstance(child, _SCOPE_NODES) else scope)

    visit(tree, tree)
    return scope_of


def _build_env(tree: ast.AST, scope_of: Optional[dict] = None) -> dict:
    """`{scope_node: name -> flattened text}` — one env for the Module and one for every def/lambda, from simple
    `x = <expr>` assignments (last write wins WITHIN a scope, in source order; adequate for this codebase's straight-line
    style, not real dataflow). A def's env starts as a copy of its enclosing scope's COMPLETE env, then takes the def's own
    assignments; a sibling function's locals never reach it."""
    scope_of = scope_of if scope_of is not None else _scope_map(tree)
    own: dict = {}
    assigns = (n for n in ast.walk(tree) if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name))
    for node in sorted(assigns, key=lambda n: (n.lineno, n.col_offset)):
        own.setdefault(scope_of[node], []).append(node)
    envs: dict = {}

    def env_of(scope) -> dict:
        if scope in envs:
            return envs[scope]
        env = {} if scope is tree else dict(env_of(scope_of[scope]))     # the enclosing scope's finished env, copied
        envs[scope] = env
        for node in own.get(scope, []):
            text = _flatten(node.value, env)
            if text is not None:
                env[node.targets[0].id] = text
        return env

    env_of(tree)
    for node in ast.walk(tree):
        if isinstance(node, _SCOPE_NODES):
            env_of(node)
    return envs


def find_offenders(path: Path, check_organism_import: bool) -> List[Tuple[str, str]]:
    """[(kind, detail), ...] for one file. kind: "write" | "organism_import"."""
    tree = ast.parse(path.read_text(), filename=str(path))
    scope_of = _scope_map(tree)
    envs = _build_env(tree, scope_of)
    offenders: List[Tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            callee = node.func
            is_open = isinstance(callee, ast.Name) and callee.id == "open"
            is_write_attr = isinstance(callee, ast.Attribute) and callee.attr in WRITE_METHODS
            if is_open or is_write_attr:
                env = envs[scope_of[node]]          # FIX 2: the env of THIS call's own scope, not one flat module-wide map
                text = _first_arg_text(node, env) if is_open else _flatten(callee.value, env)
                if text and any(bad in text for bad in FORBIDDEN):
                    offenders.append(("write", f"{path.name}: {ast.unparse(node)[:120]}"))
        if check_organism_import and isinstance(node, ast.ImportFrom):
            names = [a.name for a in node.names]
            module = node.module or ""
            if "Organism" in names and module.endswith("machinery"):
                offenders.append(("organism_import", f"{path.name}: from {module} import Organism"))
            if "machinery" in names:   # `from genome import machinery` -> Organism reachable via machinery.Organism
                offenders.append(("organism_import", f"{path.name}: from {module} import machinery"))
        if check_organism_import and isinstance(node, ast.Import):
            for a in node.names:
                if a.name.endswith("machinery"):
                    offenders.append(("organism_import", f"{path.name}: import {a.name} (Organism reachable via it)"))
    return offenders


def sense_module_paths() -> List[Path]:
    paths = sorted((ROOT / "creature" / "senses").glob("*.py"))
    paths = [p for p in paths if p.name != "__init__.py"]
    paths.append(ROOT / "creature" / "world_maker.py")
    return paths


def writer_check_paths() -> List[Path]:
    return sense_module_paths() + [ROOT / "creature" / "ask.py"]


class TestWriterSweepG41(unittest.TestCase):
    def test_no_state_journal_memory_writes(self) -> None:
        offenders: List[Tuple[str, str]] = []
        for p in writer_check_paths():
            offenders += find_offenders(p, check_organism_import=False)
        self.assertEqual(offenders, [], f"writer sweep found forbidden writes: {offenders}")

    def test_no_organism_import_in_true_sense_modules(self) -> None:
        offenders: List[Tuple[str, str]] = []
        for p in sense_module_paths():
            offenders += find_offenders(p, check_organism_import=True)
        self.assertEqual(offenders, [], f"a sense module must never import Organism: {offenders}")

    def test_ask_py_may_import_organism(self) -> None:
        """The voice is not a sense (PREREG §2.7 requires it to load a private Organism) -- confirm the
        walker's exemption is deliberate, not merely "we never checked"."""
        text = (ROOT / "creature" / "ask.py").read_text()
        self.assertIn("Organism", text)

    def test_planted_offender_is_caught(self) -> None:
        """Control: a planted offender module (writes under a 'state' path, and imports Organism) in a
        temp dir must be caught by the same walker -- proving find_offenders is not a vacuous pass."""
        tmp_dir = Path(tempfile.mkdtemp())
        offender = tmp_dir / "planted_sense.py"
        offender.write_text(
            "from pathlib import Path\n"
            "from genome.machinery import Organism\n"
            "def sense(publish, stop_event, root):\n"
            "    p = Path(root) / 'state' / 'hack.json'\n"
            "    open(p, 'w').write('{}')\n"
        )
        write_offenders = find_offenders(offender, check_organism_import=False)
        self.assertTrue(write_offenders, "the planted write-to-state offender must be caught")
        import_offenders = find_offenders(offender, check_organism_import=True)
        self.assertTrue(import_offenders, "the planted Organism import must be caught")

    # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md's own instruction
    # (via the brief): "a planted offender: a web sense that writes memory" — a plant SHAPED like this
    # builder's own module (a `sense(publish, stop_event, root, ...)` signature, the same imports web.py
    # actually uses), caught by BOTH this file's own `find_offenders` AND `tools/gate_g4.py`'s independent
    # `sweep()` (SOLUTIONS #214: the orchestrator keeps its own checker, and a builder's own control must
    # pass under it too, not only under the file it happens to be editing).
    def test_planted_web_sense_that_writes_memory_is_caught_by_both_sweeps(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        plant = tmp_dir / "planted_web_sense.py"
        plant.write_text(
            "from pathlib import Path\n"
            "def sense(publish, stop_event, root, questions_dir=None, hold_file=None, floor_s=2.0):\n"
            "    p = Path(root) / 'memory' / 'web_cache.json'\n"
            "    p.write_text('{}')\n"
        )
        offenders = find_offenders(plant, check_organism_import=False)
        self.assertTrue(offenders, "a web-shaped sense writing under 'memory' must be caught by this file's own walker")

        import importlib
        gate_g4 = importlib.import_module("tools.gate_g4")
        g4_offenders = gate_g4.sweep([plant])
        self.assertTrue(g4_offenders, "the SAME plant must be caught by tools/gate_g4.py's own independent sweep() too")

    def test_the_real_web_and_grade_modules_pass_both_sweeps(self) -> None:
        """The negative control's positive twin: the actual, shipped web.py/grade.py must NOT be flagged by
        either sweep — a sweep that catches everything proves nothing (#91)."""
        real = [ROOT / "creature" / "senses" / "web.py", ROOT / "creature" / "senses" / "grade.py"]
        for p in real:
            self.assertEqual(find_offenders(p, check_organism_import=False), [], f"{p} must be clean under this file's own walker")
            self.assertEqual(find_offenders(p, check_organism_import=True), [], f"{p} must not import Organism")
        import importlib
        gate_g4 = importlib.import_module("tools.gate_g4")
        self.assertEqual(gate_g4.sweep(real), [], "the real modules must be clean under tools/gate_g4.py's own sweep() too")

    def test_planted_clean_write_is_not_flagged(self) -> None:
        """Negative control for the negative control (#91): a write OUTSIDE state/journal/memory must
        NOT be flagged, or the sweep would be trivially "catch everything"."""
        tmp_dir = Path(tempfile.mkdtemp())
        clean = tmp_dir / "planted_clean_sense.py"
        clean.write_text(
            "from pathlib import Path\n"
            "def sense(publish, stop_event, root):\n"
            "    p = Path(root) / 'truth' / 'x.json'\n"
            "    open(p, 'w').write('{}')\n"
        )
        self.assertEqual(find_offenders(clean, check_organism_import=False), [])
        self.assertEqual(find_offenders(clean, check_organism_import=True), [])

    # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:46 +0400 — A4L-VOICE (docs/briefs/A4L-VOICE.md, the writer law):
    # a planted offender SHAPED like this branch's new module (genome/voice.py's `wav_bytes`, the maker's `_publish_voice` writing the
    # chord's audit wav) that writes the wav under `state/` instead of `truth/voice/` and imports machinery — caught by BOTH sweeps;
    # the real genome/voice.py and creature/world_maker.py (which now writes truth/voice/<word>.wav) are clean under both.
    def test_planted_voice_module_that_writes_memory_is_caught_by_both_sweeps(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        plant = tmp_dir / "planted_voice.py"
        plant.write_text(
            "from pathlib import Path\n"
            "from genome import machinery\n"
            "def _publish_voice(publish, root, moment, thing, answering=None):\n"
            "    wav_dir = Path(root) / 'state' / 'voice'\n"
            "    wav_path = wav_dir / (thing + '.wav')\n"
            "    wav_path.write_bytes(b'RIFF')\n"
        )
        self.assertTrue(find_offenders(plant, check_organism_import=False), "a voice-shaped module writing under 'state' must be caught")
        self.assertTrue(find_offenders(plant, check_organism_import=True), "and its machinery import too")
        import importlib
        gate_g4 = importlib.import_module("tools.gate_g4")
        self.assertTrue(gate_g4.sweep([plant]), "the SAME plant must be caught by tools/gate_g4.py's own sweep()")
        self.assertIn("genome/voice.py", gate_g4.SENSE_FILES, "the orchestrator's gate walks the voice module")

    def test_the_real_voice_module_and_the_voiced_maker_pass_both_sweeps(self) -> None:
        real = [ROOT / "genome" / "voice.py", ROOT / "creature" / "world_maker.py"]
        for p in real:
            self.assertEqual(find_offenders(p, check_organism_import=False), [], f"{p} must be clean under this file's own walker")
            self.assertEqual(find_offenders(p, check_organism_import=True), [], f"{p} must not import Organism/machinery")
        import importlib
        gate_g4 = importlib.import_module("tools.gate_g4")
        self.assertEqual(gate_g4.sweep(real), [])

    # edit: Claude (Fable 5.1), 2026-09-23 16:56 +0400 — SIT-ATOMIC-SWEEP-0923 FIX 2 (docs/briefs/SEAM5-WITNESS-SOUND-REPORT.md item 5): both
    # sweeps built ONE flat name->text env for the whole module (`ast.walk` over every Assign, last write wins), so a same-named local in a
    # DIFFERENT function overwrote a leak's binding — the seam-5 builder's own edit (a local `p` in another function) hid COST's planted leak
    # (`p = root/'state'/'witness.json'; p.write_text(...)`) from BOTH sweeps. The env is now built per function scope (seeded from the
    # enclosing scope; a sibling's locals never leak in). This plant is the seam-5 shape in miniature. The ORDER is load-bearing for the
    # control: with the leak FIRST and the innocent binding SECOND the old flat env read [] from both sweeps (the RED, logged in
    # docs/briefs/SIT-ATOMIC-SWEEP-0923-REPORT.md); with the innocent binding first the old env flagged BOTH writes (a false positive on the
    # clean one). The fix must read exactly ONE offender — the leak's own line — in either order.
    @staticmethod
    def _shadowed_plant(leak_first: bool) -> str:
        leak = ("def leak(root):\n"
                "    p = Path(root) / 'state' / 'witness.json'\n"
                "    p.write_text('{}')\n")
        clean = ("def clean(root):\n"
                 "    p = Path(root) / 'truth' / 'note.json'\n"
                 "    p.write_text('{}')\n")
        return "from pathlib import Path\n" + (leak + clean if leak_first else clean + leak)

    def test_a_leak_shadowed_by_a_same_named_local_in_another_function_is_caught_by_both_sweeps(self) -> None:
        import importlib
        gate_g4 = importlib.import_module("tools.gate_g4")
        tmp_dir = Path(tempfile.mkdtemp())
        for leak_first, leak_line in ((True, 4), (False, 7)):
            plant = tmp_dir / f"planted_shadowed_leak_{leak_first}.py"
            plant.write_text(self._shadowed_plant(leak_first))
            mine = find_offenders(plant, check_organism_import=False)
            self.assertEqual(len(mine), 1, f"leak_first={leak_first}: exactly the leak, never the innocent write, under this file's walker: {mine}")
            g4 = gate_g4.sweep([plant])
            self.assertEqual([o[1] for o in g4], [leak_line],
                             f"leak_first={leak_first}: tools/gate_g4.py's sweep must flag exactly line {leak_line} (the leak), never the clean write: {g4}")
            self.assertIn("state", g4[0][2])


if __name__ == "__main__":
    unittest.main()
