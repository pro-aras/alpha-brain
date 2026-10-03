# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 15:52 +0400 — PREREG-RESIT-READER (law text b02cf10, sha256 f6390b0d…): the ANSWER child and the GRADE child of tools/brain/resit.py, tested against a STUB
# code tree (a tiny genome / creature / brain package written into a temp dir): the children's plumbing — the mind's own order, held asks, begin switching the state, the glance cache, the realpath
# assertion (R11), the eye pin (R13), the turn pin (R14) — is exercised fast and under planted defects. The real code is exercised by R1 itself, on the real closed life.
"""tests/tools/test_resit_children.py — the re-sit reader's children, run BY PATH as the unit and the orchestrator run them."""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tests.tools.test_resit import write_tape
from tools.brain import resit as R

REPO = Path(__file__).resolve().parents[2]
RESIT_PY = REPO / "tools" / "brain" / "resit.py"
ENV = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}


def png(r: int, g: int, b: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (r, g, b)).save(buf, format="PNG")
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------ the stub tree
STUB_FILES = {
    "genome/__init__.py": "",
    "creature/__init__.py": "",
    "genome/machinery.py": '''
class Genome:
    def __init__(self, retina, gaze, colour, declared):
        self.retina, self.gaze, self.colour, self.declared = retina, gaze, colour, declared

def parse_genome(text):
    declared, retina, gaze, colour = {}, [], {}, None
    for line in text.splitlines():
        s = line.split("#", 1)[0].strip()
        if not s:
            continue
        w = s.split()
        if w[0] == "RETINA":
            retina = w[1:]
        elif w[0] == "GAZE":
            gaze = {"spec": w[1:]}
        elif w[0] == "SENSE" and len(w) > 1 and w[1] == "colour":
            colour = {"spec": w[2:]}
        elif w[0] == "BRAIN":
            declared["BRAIN"] = {"lr": 0.01}
        elif w[0] == "TAPE":
            declared["TAPE"] = {"path": w[1]}
    return Genome(retina, gaze, colour, declared)
''',
    "genome/gaze.py": '''
import numpy as np

def glances(rgb, spec, gaze, mode="surprise", pic_id="", colour=None, predicted=None):
    s = float(np.asarray(rgb, dtype=np.float64).sum())
    feats = [np.array([s % 7.0, s % 3.0, float(len(pic_id))]) for _ in range(2)]
    return {"feats": feats, "fix": [(1, 2), (3, 4)], "windows": [(0, 0), (1, 1)], "residual": [None, None]}
''',
    "genome/brain.py": '''
import hashlib, json
from pathlib import Path
import numpy as np

TURN_MUTATES = %(turn_mutates)s

class BrainError(Exception):
    pass

class Brain:
    def __init__(self, cfg):
        self.cfg = cfg
        self.n_learned = 0
        self.calibrated_at = None
        self.n_calibrations = 0
        self.v = np.zeros(3)

    @classmethod
    def load(cls, base, cfg):
        base = Path(base)
        meta = json.loads(Path(str(base) + ".json").read_text())
        with np.load(str(base) + ".npz") as z:
            v = z["v"]
        if hashlib.sha256(v.tobytes()).hexdigest() != meta["state_hash"]:
            raise BrainError("load: the state's files do not hash to the hash they carry")
        b = cls(cfg)
        b.n_learned, b.calibrated_at, b.n_calibrations, b.v = int(meta["n_learned"]), meta["calibrated_at"], int(meta["n_calibrations"]), v
        return b

    def state_hash(self):
        return hashlib.sha256(self.v.tobytes() + str(self.n_learned).encode()).hexdigest()

    def calibrate(self):
        self.n_calibrations += 1
        self.calibrated_at = self.n_learned
        return {"at": self.n_learned}

    def ask(self, payload, glance):
        form = payload.get("form")
        if form == "begin":
            did = False
            if self.n_learned > 0 and self.calibrated_at != self.n_learned:
                self.calibrate()
                did = True
            a = {"kind": "begin", "calibrated": did, "at": self.n_learned}
            return {**a, "raw": dict(a)}
        if form == "end":
            return {"kind": "end", "raw": {"kind": "end"}}
        if form == "why":
            a = {"kind": "why", "word": str(payload.get("word")), "n": float(self.v.sum())}
            return {**a, "raw": dict(a)}
        if glance is None:
            raise BrainError("ask: form %%r needs its canvas's glance" %% (form,))
        if payload.get("test_seed") is None:
            raise BrainError("ask: needs test_seed")
        s = float(sum(np.asarray(f).sum() for f in glance["feats"]))
        x = float(self.v.sum()) + s
        return {"kind": "thing", "hyp": int(abs(x) * 1000) %% 3, "raw": {"p": x %% 1.0, "item": payload.get("item")}}

    def turn(self, glance, *, scene, world_seed, says=1, asks=1):
        if TURN_MUTATES:
            self.v = self.v + 1.0
        return {"scene": scene, "n_hyp": 2, "say": None, "ask": None}
''',
    "creature/tape.py": '''
import json
from pathlib import Path

def _resolve_tape_dir(root, declared_path):
    root = Path(root)
    if not declared_path:
        return root / "tape"
    parts = Path(declared_path).parts
    if parts and parts[0] == "run":
        parts = parts[1:]
    return root / Path(*parts) if parts else root / "tape"

def read_tape(root, declared_path=None):
    tape = _resolve_tape_dir(root, declared_path)
    for f in sorted(tape.glob("*.jsonl")):
        for line in f.open():
            if line.strip():
                yield json.loads(line)
''',
    "creature/organs_road.py": '''
import numpy as np

class _H:
    def __init__(self, members):
        self.members = members

def eye_view(g):
    fix = [(int(y), int(x)) for (y, x) in (g.get("fix") or [])]
    if not fix:
        return fix, np.zeros((0, 0)), []
    return fix, np.zeros((len(fix), 1)), [_H([0]), _H([1])]
''',
    "creature/genes.py": '''
MUTABLE_KEYS = %(mutable)s
''',
}

GENOME = "TAPE run/tape\nRETINA a b\nGAZE g 4\nSENSE colour rg\nBRAIN lr 0.01\n"


def build_stub(root: Path, *, turn_mutates: bool = False, mutable=("DELTA.lr", "KWTA.k")) -> Path:
    for rel, body in STUB_FILES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        text = body
        if "%(" in body:
            text = body % {"turn_mutates": "True" if turn_mutates else "False", "mutable": repr(tuple(mutable))}
        p.write_text(textwrap.dedent(text) if rel.endswith(".py") and body.startswith("\n") else text)
    return root


def write_state(d: Path, v=(1.0, 2.0, 3.0), n_learned=10, calibrated_at=10, bad_hash=False) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    arr = np.array(v, dtype=np.float64)
    with open(d / "brain.npz", "wb") as f:
        np.savez(f, v=arr)
    h = hashlib.sha256(arr.tobytes()).hexdigest()
    if bad_hash:
        h = "0" * 64
    (d / "brain.json").write_text(json.dumps({"state_hash": h, "n_learned": n_learned, "calibrated_at": calibrated_at, "n_calibrations": 1}))
    return d


def sitting_spec() -> list:
    """Two sets: begin, two held asks on one canvas, a why, an end — the shape of the real sittings."""
    spec = [("ear", "m-other", "bar"), ("eye", "m-other", None, png(9, 9, 9))]
    for k, s in enumerate(("fresh", "s1b1")):
        spec += [("ask", f"sc-{s}-begin", {"form": "begin", "set": s, "test_seed": 7}),
                 ("ask", f"sc-{s}-0", {"form": "point", "item": f"M1:{s}:0", "mark": "M1", "phrase": ["small", "green", "circle"], "test_seed": 7,
                                       "box": None, "centroid": None, "word": None}),
                 ("ask", f"sc-{s}-0", {"form": "point", "item": f"M2a:{s}:0", "mark": "M2a", "phrase": ["green", "star"], "test_seed": 7,
                                       "box": None, "centroid": None, "word": None}),
                 ("eye", f"sc-{s}-0", "sitting", png(10 + k, 20, 30)),
                 ("ask", f"sc-{s}-why", {"form": "why", "item": "M4:red", "mark": "M4", "word": "red", "test_seed": 7}),
                 ("ask", f"sc-{s}-end", {"form": "end", "set": s, "test_seed": 7})]
    return spec


class Tmp(unittest.TestCase):
    def mk(self, prefix: str = "resit-c-") -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d


def run_child(kind: str, spec: dict, workdir: Path, *, wrapper: str = "", dash_i: bool = True):
    specp = workdir / f"{kind}-spec.json"
    specp.write_text(json.dumps(spec))
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update(ENV)
    argv = [sys.executable, "-B"] + (["-I"] if dash_i else [])
    if wrapper:
        wp = workdir / "wrapper.py"
        wp.write_text(wrapper)
        argv += [str(wp), str(RESIT_PY), kind, "--spec", str(specp)]
    else:
        argv += [str(RESIT_PY), kind, "--spec", str(specp)]
    p = subprocess.run(argv, capture_output=True, text=True, cwd=str(workdir), env=env)
    return p


def last_json(stdout: str) -> dict:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    return {}


class AnswerChildBase(Tmp):
    def setUp(self) -> None:
        self.work = self.mk()
        self.code = build_stub(self.work / "code")
        self.items = self.work / "items"
        self.items.mkdir()
        write_tape(self.items, sitting_spec(), seq0=1000)
        (self.items / "GENOME.genome").write_text(GENOME)
        self.state = write_state(self.work / "state")
        self.out = self.work / "out"
        self.out.mkdir()
        self.genome_path = self.items / "GENOME.genome"

    def spec(self, **over) -> dict:
        s = {"code": str(self.code), "items_root": str(self.items), "tape_decl": "run/tape",
             "states": [{"name": "*", "dir": str(self.state), "genome": str(self.genome_path)}],
             "out_dir": str(self.out), "glance_cache": None, "check_turn": None}
        s.update(over)
        return s

    def rows(self) -> list:
        return [json.loads(l) for l in (self.out / "answers.jsonl").read_text().splitlines()]

    def meta(self) -> dict:
        return json.loads((self.out / "answer-meta.json").read_text())


class TestAnswerChild(AnswerChildBase):
    def test_the_rows_are_the_minds_own_shape_and_order(self) -> None:
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        rows = self.rows()
        self.assertEqual(len(rows), 10)
        want_keys = {"kind", "by", "item", "mark", "form", "answer", "moment", "seq", "eye_seq", "at", "fix", "hyps", "detail"}
        for r in rows:
            self.assertEqual(set(r), want_keys)
            self.assertEqual((r["kind"], r["by"]), ("answer", "brain"))
        # the tape says: ask begin; ask point M1 and point M2a (HELD for their moment); eye row of that moment; ask why; ask end — and the same for s1b1.
        # The mind answers a canvas-less form at once and a held form AT the eye row, in the order held: so begin, the two points, why, end, twice.
        order = [(r["form"], r["item"]) for r in rows]
        self.assertEqual(order, [("begin", None), ("point", "M1:fresh:0"), ("point", "M2a:fresh:0"), ("why", "M4:red"), ("end", None),
                                 ("begin", None), ("point", "M1:s1b1:0"), ("point", "M2a:s1b1:0"), ("why", "M4:red"), ("end", None)])

    def test_a_canvas_less_form_is_answered_at_its_ask_row_a_held_form_at_its_eye_row(self) -> None:
        run_child("answer", self.spec(), self.work)
        rows = self.rows()
        tape = [json.loads(l) for f in sorted((self.items / "tape").glob("*.jsonl")) for l in f.read_text().splitlines()]
        asks = {r["seq"]: r for r in tape if r["sense"] == "ask"}
        eyes = {r["meta"]["moment"]: r for r in tape if r["sense"] == "eye"}
        for r in rows:
            ask = asks[r["seq"]]
            self.assertEqual(r["moment"], ask["meta"]["moment"])
            if r["form"] in ("begin", "end", "why"):
                self.assertIsNone(r["eye_seq"])
                self.assertEqual(r["at"], ask["at"])
                self.assertIsNone(r["fix"])
                self.assertIsNone(r["hyps"])
            else:
                eye = eyes[r["moment"]]
                self.assertEqual(r["eye_seq"], eye["seq"])
                self.assertEqual(r["at"], eye["at"])
                self.assertEqual(r["fix"], [[1, 2], [3, 4]])
                self.assertEqual(r["hyps"], [[0], [1]])
            self.assertLess(r["seq"], r["eye_seq"] if r["eye_seq"] is not None else 10**12)

    def test_the_answers_are_a_function_of_the_brain_and_the_canvas_and_nothing_is_learned(self) -> None:
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, p.stderr)
        st = self.meta()["states"][0]
        self.assertEqual(st["n_learned"], 10)
        self.assertEqual(st["state_hash_end"], st["state_hash"], "no ask changes the brain's learned state")
        # the stub's formula, recomputed by hand: png(10,20,30) is 64 pixels of (10,20,30) -> pixel sum 3840; the glance feature sum is
        # (3840 % 7) + (3840 % 3) + len(sha) = 4 + 0 + 64 = 68, twice; the state v = (1,2,3) sums to 6
        x = 6.0 + 2 * (3840 % 7 + 3840 % 3 + 64)
        r = next(x_ for x_ in self.rows() if x_["item"] == "M1:fresh:0")
        self.assertEqual(r["answer"]["hyp"], int(abs(x) * 1000) % 3)
        self.assertAlmostEqual(r["answer"]["raw"]["p"], x % 1.0)

    def test_two_sets_switch_to_their_own_state_at_begin(self) -> None:
        sa = write_state(self.work / "sa", v=(1.0, 2.0, 3.0))
        sb = write_state(self.work / "sb", v=(50.0, 60.0, 70.0))
        spec = self.spec(states=[{"name": "fresh", "dir": str(sa), "genome": str(self.genome_path)},
                                 {"name": "s1b1", "dir": str(sb), "genome": str(self.genome_path)}])
        p = run_child("answer", spec, self.work)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        rows = {r["item"]: r for r in self.rows() if r["item"]}
        why = [r for r in self.rows() if r["form"] == "why"]
        self.assertEqual([w["answer"]["n"] for w in why], [6.0, 180.0], "the why of each set is answered by that set's own state")
        self.assertEqual(len(self.meta()["states"]), 2)

    def test_begin_calibrates_the_copy_when_the_brain_owes_a_calibration_and_says_so(self) -> None:
        owes = write_state(self.work / "owes", n_learned=10, calibrated_at=5)
        p = run_child("answer", self.spec(states=[{"name": "*", "dir": str(owes), "genome": str(self.genome_path)}]), self.work)
        self.assertEqual(p.returncode, 0, p.stderr)
        begins = [r for r in self.rows() if r["form"] == "begin"]
        self.assertTrue(begins[0]["answer"]["calibrated"])
        self.assertFalse(begins[1]["answer"]["calibrated"], "calibrated once; the second begin owes nothing")
        st = self.meta()["states"][0]
        self.assertEqual((st["calibrated_at_load"], st["calibrated_at_end"]), (5, 10))

    def test_a_brain_error_is_answered_refused_by_name_never_a_crash(self) -> None:
        spec = []
        for it in sitting_spec():
            if it[0] == "ask" and it[2].get("item") == "M1:fresh:0":
                it = ("ask", it[1], {k: v for k, v in it[2].items() if k != "test_seed"})
            spec.append(it)
        shutil.rmtree(self.items / "tape")
        write_tape(self.items, spec, seq0=1000)
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r = next(x for x in self.rows() if x["item"] == "M1:fresh:0")
        self.assertEqual(r["answer"]["kind"], "refused")
        self.assertIn("test_seed", r["answer"]["reason"])
        self.assertEqual(r["answer"]["raw"], {"refused": r["answer"]["reason"]})

    def test_an_ask_whose_canvas_never_comes_is_counted_unanswered(self) -> None:
        spec = [it for it in sitting_spec() if not (it[0] == "eye" and it[1] == "sc-s1b1-0")]
        shutil.rmtree(self.items / "tape")
        write_tape(self.items, spec, seq0=1000)
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, p.stderr)
        m = self.meta()
        self.assertEqual(m["asks_seen"], 10)
        self.assertEqual(m["answered"], 8)
        self.assertEqual(m["unanswered"], 2)
        self.assertEqual(len(self.rows()), 8)

    def test_the_glance_cache_cold_then_warm_is_byte_identical_and_hits_are_counted(self) -> None:
        cache = self.work / "glances.pkl"
        p1 = run_child("answer", self.spec(glance_cache=str(cache)), self.work)
        self.assertEqual(p1.returncode, 0, p1.stderr)
        a1, m1 = (self.out / "answers.jsonl").read_bytes(), self.meta()
        self.assertTrue(cache.exists())
        self.assertEqual((m1["glance_cache"]["hits"], m1["glance_cache"]["misses"]), (0, 2))
        p2 = run_child("answer", self.spec(glance_cache=str(cache)), self.work)
        self.assertEqual(p2.returncode, 0, p2.stderr)
        a2, m2 = (self.out / "answers.jsonl").read_bytes(), self.meta()
        self.assertEqual(a1, a2, "a warm run answers byte for byte as the cold one")
        self.assertEqual((m2["glance_cache"]["hits"], m2["glance_cache"]["misses"]), (2, 0))

    def test_a_cache_drawn_under_other_code_is_never_reused(self) -> None:
        cache = self.work / "glances.pkl"
        run_child("answer", self.spec(glance_cache=str(cache)), self.work)
        gz = self.code / "genome" / "gaze.py"
        before = gz.read_bytes()
        gz.write_text(gz.read_text() + "\n# a changed byte in the module that draws the glance\n")
        self.assertNotEqual(before, gz.read_bytes(), "the plant must change the bytes")
        p = run_child("answer", self.spec(glance_cache=str(cache)), self.work)
        self.assertEqual(p.returncode, 0, p.stderr)
        g = self.meta()["glance_cache"]
        self.assertEqual((g["hits"], g["misses"]), (0, 2), "the key carries the digest of the code that draws the glance")

    def test_a_corrupt_cache_file_is_ignored_and_said(self) -> None:
        cache = self.work / "glances.pkl"
        cache.write_bytes(b"not a pickle")
        p = run_child("answer", self.spec(glance_cache=str(cache)), self.work)
        self.assertEqual(p.returncode, 0, p.stderr)
        g = self.meta()["glance_cache"]
        self.assertEqual(g["hits"], 0)
        self.assertIn("unreadable", g["note"])

    def test_the_loaded_modules_are_recorded_with_their_sha256_and_all_lie_under_the_code(self) -> None:
        run_child("answer", self.spec(), self.work)
        m = self.meta()
        self.assertTrue(m["modules"])
        code = os.path.realpath(self.code)
        for mod in m["modules"]:
            f = Path(code) / mod["rel"]
            self.assertTrue(f.exists(), mod["rel"])
            self.assertEqual(mod["sha256"], hashlib.sha256(f.read_bytes()).hexdigest())
        rels = {x["rel"] for x in m["modules"]}
        for need in ("genome/gaze.py", "genome/brain.py", "creature/tape.py", "creature/organs_road.py", "creature/genes.py"):
            self.assertIn(need, rels)
        self.assertNotIn("creature/mind.py", rels, "the reader never imports the mind")

    def test_the_eye_pin_reads_the_lifes_own_mutable_keys_R13(self) -> None:
        run_child("answer", self.spec(), self.work)
        self.assertEqual(self.meta()["eye_pin"], {"n_mutable": 2, "eye_or_brain": 0})

    def test_a_mutable_eye_key_is_caught_and_the_run_refused_R13(self) -> None:
        build_stub(self.code, mutable=("DELTA.lr", "GAZE.grid"))
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        res = last_json(p.stdout)
        self.assertIn("GAZE.grid", res["refused"])
        self.assertIn("R13", res["refused"])
        self.assertFalse((self.out / "answers.jsonl").exists(), "a refused run writes no answers")

    def test_every_eye_and_brain_prefix_is_caught(self) -> None:
        for key in ("RETINA", "GAZE.fixations", "SENSE.colour", "BRAIN.lr"):
            with self.subTest(key=key):
                build_stub(self.code, mutable=("DELTA.lr", key))
                p = run_child("answer", self.spec(), self.work)
                self.assertEqual(p.returncode, 2)
                self.assertIn(key, last_json(p.stdout)["refused"])
        build_stub(self.code, mutable=("SENSE.ear_letters", "DELTA.lr"))
        p = run_child("answer", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, "SENSE.ear_letters is not one of the four lines the law holds fixed")

    def test_a_pre_imported_module_of_another_tree_is_refused_naming_it_R11(self) -> None:
        # the planted shadow: a package of MASTER is imported before the reader's import step (what `python -m tools.brain.resit` does by accident)
        wrapper = textwrap.dedent(f'''
            import sys, runpy
            sys.path.insert(0, {str(REPO)!r})
            import genome.gaze          # master's genome package, now in sys.modules
            sys.argv = sys.argv[1:]
            runpy.run_path(sys.argv[0], run_name="__main__")
        ''')
        p = run_child("answer", self.spec(), self.work, wrapper=wrapper)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        res = last_json(p.stdout)
        self.assertIn("R11", res["refused"])
        self.assertIn("genome", res["refused"])
        self.assertFalse((self.out / "answers.jsonl").exists())

    def test_the_turn_pin_passes_a_read_only_turn_and_records_it_R14(self) -> None:
        p = run_child("answer", self.spec(check_turn={"world_seed": 5, "n_asks": 3}), self.work)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        t = self.meta()["turn_check"]
        self.assertTrue(t["state_hash_equal"])
        self.assertTrue(t["answers_equal"])
        self.assertGreaterEqual(t["n_asks"], 1)

    def test_a_turn_that_mutates_the_brain_is_caught_R14(self) -> None:
        build_stub(self.code, turn_mutates=True)
        p = run_child("answer", self.spec(check_turn={"world_seed": 5, "n_asks": 3}), self.work)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        res = last_json(p.stdout)
        self.assertIn("R14", res["refused"])
        self.assertIn("turn", res["refused"])

    def test_a_state_whose_files_do_not_hash_to_their_hash_is_refused_R4a(self) -> None:
        bad = write_state(self.work / "bad", bad_hash=True)
        p = run_child("answer", self.spec(states=[{"name": "*", "dir": str(bad), "genome": str(self.genome_path)}]), self.work)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("hash", last_json(p.stdout)["refused"])

    def test_a_run_without_dash_B_or_dash_I_is_refused_by_the_orchestrator_command(self) -> None:
        # the children check their own flags too: a child started without -I refuses (a PYTHON* variable could shadow the life's modules)
        p = run_child("answer", self.spec(), self.work, dash_i=False)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("-I", last_json(p.stdout)["refused"])


class TestGradeChild(Tmp):
    """A stub GRADER tree: tools/brain/grade_life.py with the one function the child calls."""

    def setUp(self) -> None:
        self.work = self.mk()
        self.gcode = self.work / "grader"
        (self.gcode / "tools" / "brain").mkdir(parents=True)
        (self.gcode / "tools" / "brain" / "grade_life.py").write_text(textwrap.dedent('''
            import json
            from pathlib import Path
            def grade(root, journal, scored, label, genome=None):
                rows = [json.loads(l) for l in Path(journal).read_text().splitlines() if l.strip()]
                return {"label": label, "n_answers": len(rows), "root": str(root), "scored": str(scored), "genome": str(genome),
                        "sets": {"fresh": {"marks": {}}}, "items": {}}
        '''))
        self.journal = self.work / "answers.jsonl"
        self.journal.write_text(json.dumps({"kind": "answer", "item": "a"}) + "\n" + json.dumps({"kind": "answer", "item": "b"}) + "\n")
        self.out = self.work / "out"
        self.out.mkdir()

    def spec(self, **over) -> dict:
        s = {"grader_code": str(self.gcode), "items_root": str(self.work / "items"), "journal": str(self.journal), "scored": str(self.work / "scored"),
             "label": "t", "genome": str(self.work / "items" / "GENOME.genome"), "out_dir": str(self.out), "m2a_rows": False}
        s.update(over)
        return s

    def test_the_grade_is_taken_by_the_pinned_graders_own_function_and_written(self) -> None:
        p = run_child("grade", self.spec(), self.work)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        g = json.loads((self.out / "grade.json").read_text())
        self.assertEqual(g["n_answers"], 2)
        self.assertEqual(g["label"], "t")
        meta = json.loads((self.out / "grade-meta.json").read_text())
        self.assertIn("tools/brain/grade_life.py", {m["rel"] for m in meta["modules"]})
        self.assertEqual(meta["grader_sha256"], hashlib.sha256((self.gcode / "tools/brain/grade_life.py").read_bytes()).hexdigest())

    def test_the_grade_json_is_written_as_the_graders_own_main_writes_it(self) -> None:
        run_child("grade", self.spec(), self.work)
        text = (self.out / "grade.json").read_text()
        self.assertEqual(text, json.dumps(json.loads(text), indent=1, sort_keys=True))

    def test_nothing_is_written_under_the_items_root(self) -> None:
        (self.work / "items").mkdir()
        before = sorted(p.name for p in (self.work / "items").iterdir())
        run_child("grade", self.spec(), self.work)
        self.assertEqual(sorted(p.name for p in (self.work / "items").iterdir()), before)

    def test_a_pre_imported_module_of_another_tree_is_refused_for_the_grader_too_R11(self) -> None:
        wrapper = textwrap.dedent(f'''
            import sys, runpy
            sys.path.insert(0, {str(REPO)!r})
            import tools.brain.hears_read      # master's `tools` namespace, in sys.modules
            sys.argv = sys.argv[1:]
            runpy.run_path(sys.argv[0], run_name="__main__")
        ''')
        p = run_child("grade", self.spec(), self.work, wrapper=wrapper)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("R11", last_json(p.stdout)["refused"])

    def test_a_grader_that_raises_is_a_named_failure_not_a_silent_one(self) -> None:
        (self.gcode / "tools" / "brain" / "grade_life.py").write_text("def grade(*a, **k):\n    raise RuntimeError('boom')\n")
        p = run_child("grade", self.spec(), self.work)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse((self.out / "grade.json").exists())


if __name__ == "__main__":
    unittest.main()
