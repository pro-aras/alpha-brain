# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:32 +0400 — A4L-LANG task 2 (docs/briefs/A4L-LANG.md;
# docs/A4-LADDER-PREREG.md §3.2 item 1): creature/senses/chat.py, the chat door — a pure SENSE, test-first.
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import tempfile
import threading
import time
import unittest
import unittest.mock as mock
from pathlib import Path

import numpy as np
from PIL import Image

from creature.senses import chat as chat_sense
from creature.senses import read_common
from creature.tape import Tape, read_tape

ROOT = Path(__file__).resolve().parents[2]


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(b, format="PNG"); return b.getvalue()


def _decode(root: Path, row: dict) -> np.ndarray:
    return np.asarray(Image.open(root / "tape" / row["payload"]).convert("RGB"), dtype=np.uint8)


class _Rec:
    """A recording publish: the rows it was handed, in order (the Tape's own shape is exercised by the live tests)."""
    def __init__(self):
        self.rows = []
    def __call__(self, sense, payload, meta, ext):
        self.rows.append({"sense": sense, "payload": payload, "meta": meta, "ext": ext})
        return {"seq": len(self.rows)}


class TestScanOnce(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "chat" / "in").mkdir(parents=True)
        (self.root / "chat" / "pics").mkdir(parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def _drop(self, name: str, obj: dict) -> None:
        (self.root / "chat" / "in" / f"{name}.json").write_text(json.dumps(obj))

    def test_a_free_line_is_one_chat_row_its_canvas_the_readers_own_render(self) -> None:
        self._drop("s0001", {"id": "s0001", "text": "What is THIS, now?"})
        rec = _Rec()
        n = chat_sense.scan_once(rec, self.root, canvas=128, letters=8)
        self.assertEqual(n, 1)
        self.assertEqual([r["sense"] for r in rec.rows], ["chat"])
        meta = rec.rows[0]["meta"]
        words = read_common.words_of("What is THIS, now?", max_words=chat_sense.MAX_WORDS, letters=8)
        self.assertEqual(meta["words"], words)
        self.assertEqual(meta["id"], "s0001")
        self.assertEqual(meta["moment"], "chat-s0001")
        want = read_common.render_line(" ".join(words), 128, read_common.DEFAULT_FONT_PATH)
        got = np.asarray(Image.open(io.BytesIO(rec.rows[0]["payload"])).convert("RGB"), dtype=np.uint8)
        self.assertTrue(np.array_equal(got, want), "a free line is rendered exactly as the shelf reader renders a line")
        self.assertEqual(rec.rows[0]["ext"], "png")

    def test_a_picture_chat_carries_the_picture_never_text_on_it(self) -> None:
        rng = np.random.default_rng(3)
        pic = rng.integers(0, 255, size=(128, 128, 3), dtype=np.uint8)
        (self.root / "chat" / "pics" / "c0001.png").write_bytes(_png(pic))
        self._drop("c0001", {"id": "c0001", "text": "what is this", "picture": "c0001.png"})
        rec = _Rec()
        chat_sense.scan_once(rec, self.root, canvas=128, letters=8)
        got = np.asarray(Image.open(io.BytesIO(rec.rows[0]["payload"])).convert("RGB"), dtype=np.uint8)
        self.assertTrue(np.array_equal(got, pic))
        self.assertEqual(rec.rows[0]["meta"]["words"], ["what", "is", "this"])
        self.assertEqual(rec.rows[0]["meta"]["shown"], "picture")

    def test_one_chat_per_scan_in_bytewise_order(self) -> None:
        self._drop("b", {"id": "b", "text": "second"})
        self._drop("a", {"id": "a", "text": "first"})
        rec = _Rec()
        self.assertEqual(chat_sense.scan_once(rec, self.root), 1)
        self.assertEqual(rec.rows[0]["meta"]["id"], "a")
        self.assertEqual(chat_sense.scan_once(rec, self.root), 1)
        self.assertEqual(rec.rows[1]["meta"]["id"], "b")
        self.assertEqual(chat_sense.scan_once(rec, self.root), 0, "nothing left")

    def test_the_seen_cursor_is_written_after_the_row_and_survives_a_restart(self) -> None:
        self._drop("a", {"id": "a", "text": "first"})
        order = []
        def pub(sense, payload, meta, ext):
            order.append(("row", (self.root / "chat" / "SEEN.json").exists()))
            return {"seq": 1}
        chat_sense.scan_once(pub, self.root)
        self.assertEqual(order, [("row", False)], "SEEN.json must not exist before the row is published (#230)")
        self.assertEqual(json.loads((self.root / "chat" / "SEEN.json").read_text()), ["a"])
        rec = _Rec()
        self.assertEqual(chat_sense.scan_once(rec, self.root), 0, "a restarted door never republishes a seen chat")

    def test_never_an_ear_or_eye_row_and_never_the_family(self) -> None:
        self._drop("a", {"id": "a", "text": "is this a ring", "family": "yes-no", "thing": "ring"})
        rec = _Rec()
        chat_sense.scan_once(rec, self.root)
        self.assertEqual([r["sense"] for r in rec.rows], ["chat"])
        for key in ("family", "thing", "lure", "truth"):
            self.assertNotIn(key, rec.rows[0]["meta"])

    def test_a_torn_chat_is_skipped_never_fatal_and_read_once_whole(self) -> None:
        (self.root / "chat" / "in" / "a.json").write_text('{"id": "a", "te')
        rec = _Rec()
        self.assertEqual(chat_sense.scan_once(rec, self.root), 0)
        self._drop("a", {"id": "a", "text": "whole now"})
        self.assertEqual(chat_sense.scan_once(rec, self.root), 1)

    def test_a_missing_picture_waits_and_never_blocks_the_next_chat(self) -> None:
        self._drop("a", {"id": "a", "text": "what is this", "picture": "nope.png"})
        self._drop("b", {"id": "b", "text": "hello"})
        rec = _Rec()
        self.assertEqual(chat_sense.scan_once(rec, self.root), 1)
        self.assertEqual(rec.rows[0]["meta"]["id"], "b")

    def test_a_picture_of_the_wrong_size_is_refused_by_the_door(self) -> None:
        (self.root / "chat" / "pics" / "a.png").write_bytes(_png(np.zeros((64, 64, 3), dtype=np.uint8)))
        self._drop("a", {"id": "a", "text": "what is this", "picture": "a.png"})
        self.assertEqual(chat_sense.scan_once(_Rec(), self.root, canvas=128), 0)

    def test_an_unsafe_id_falls_back_to_the_file_stem(self) -> None:
        self._drop("c0007", {"id": "../../state/x", "text": "hi"})
        rec = _Rec()
        chat_sense.scan_once(rec, self.root)
        self.assertEqual(rec.rows[0]["meta"]["id"], "c0007")

    def test_the_seats_grades_become_kind_chat_grade_rows(self) -> None:
        (self.root / "chat" / "graded").mkdir(parents=True)
        (self.root / "chat" / "graded" / "c0001.json").write_text(json.dumps({"id": "c0001", "right": True, "novel": False}))
        (self.root / "chat" / "graded" / "s0001.json").write_text(json.dumps({"id": "s0001", "right": False, "novel": True}))
        rec = _Rec()
        chat_sense.scan_once(rec, self.root)
        grades = [r for r in rec.rows if r["sense"] == "grade"]
        self.assertEqual([(g["meta"]["id"], g["meta"]["right"], g["meta"]["novel"], g["meta"]["kind"]) for g in grades],
                         [("c0001", True, False, "chat"), ("s0001", False, True, "chat")])
        self.assertEqual(chat_sense.scan_once(_Rec(), self.root), 0, "a grade is published once (its own cursor)")


class TestRenderAnswer(unittest.TestCase):
    def test_an_answer_is_its_words(self) -> None:
        self.assertEqual(chat_sense.render_answer({"answer": ["it", "is", "ring"]}), "it is ring")

    def test_an_abstention_is_rendered_by_the_door_never_by_the_creature(self) -> None:
        s = chat_sense.render_answer({"answer": None, "abstain_reason": "novel", "resembles": "dot"})
        self.assertTrue(s.startswith("(I do not know)"))
        self.assertIn("novel", s); self.assertIn("dot", s)


class TestLiveSense(unittest.TestCase):
    def test_the_loop_publishes_onto_a_real_tape(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "chat" / "in").mkdir(parents=True)
        (root / "chat" / "in" / "a.json").write_text(json.dumps({"id": "a", "text": "what is this"}))
        tape = Tape(root); stop = threading.Event()
        t = threading.Thread(target=lambda: chat_sense.sense(tape.publish, stop, root=root, canvas=128, letters=8, period=0.05), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while not [r for r in read_tape(root) if r["sense"] == "chat"] and time.time() < deadline:
            time.sleep(0.05)
        stop.set(); t.join(timeout=5.0)
        rows = [r for r in read_tape(root) if r["sense"] == "chat"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(_decode(root, rows[0]).shape, (128, 128, 3))
        shutil.rmtree(root, ignore_errors=True)


class TestArming(unittest.TestCase):
    def test_gated_true(self) -> None:
        self.assertTrue(chat_sense.CHAT_DOOR_GATED)

    def test_declared_chat_config_arms_from_the_genomes_own_line(self) -> None:
        from creature import body as body_module
        d = {"CHAT": {"in": "chat/in", "out": "chat/out", "links_adjacent": 5, "pivot_distinct": 10,
                      "pivot_instants": 20, "max_words": 6, "teaches": False}}
        self.assertEqual(body_module._declared_chat_config(d), d["CHAT"])

    def test_undeclared_arms_nothing(self) -> None:
        from creature import body as body_module
        self.assertIsNone(body_module._declared_chat_config({}))

    def test_gated_false_arms_nothing(self) -> None:
        from creature import body as body_module
        with mock.patch.object(chat_sense, "CHAT_DOOR_GATED", False):
            self.assertIsNone(body_module._declared_chat_config({"CHAT": {"in": "chat/in", "out": "chat/out"}}))

    def test_the_sense_fn_binds_root_the_in_dir_the_canvas_and_the_ears_letters(self) -> None:
        """The LAST link of the arming (#180): the partial main() hands add_sense carries every keyword the door needs —
        builder I's web door once lacked `root` and restarted once a second for a whole pre-flight."""
        from creature import body as body_module
        fn = body_module._chat_sense_fn(Path("/r"), {"in": "chat/in", "out": "chat/out"}, canvas=128, letters=8)
        self.assertEqual(fn.keywords["root"], Path("/r"))
        self.assertEqual(fn.keywords["in_dir"], Path("/r/chat/in"))
        self.assertEqual((fn.keywords["canvas"], fn.keywords["letters"]), (128, 8))


class TestPlantedChatOffender(unittest.TestCase):
    """The brief's gate line: a planted offender for the writer sweep — a chat-shaped sense writing its cursor under
    root/state/ instead of root/chat/, in both the inline and the variable-built forms (test_read_door.py's pattern)."""

    def _text(self, inline: bool) -> str:
        if inline:
            return ("from pathlib import Path\n"
                    "def sense(publish, stop_event, root, in_dir=None, canvas=128, letters=8, period=1.0):\n"
                    "    (Path(root) / 'state' / 'SEEN.json').write_text('[]')\n")
        return ("from pathlib import Path\n"
                "def sense(publish, stop_event, root, in_dir=None, canvas=128, letters=8, period=1.0):\n"
                "    seen_path = Path(root) / 'state' / 'SEEN.json'\n"
                "    seen_path.write_text('[]')\n")

    def _gate(self):
        spec = importlib.util.spec_from_file_location("gate_g4_for_chat", ROOT / "tools" / "gate_g4.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

    def test_both_forms_are_caught_by_both_walkers(self) -> None:
        from tests.creature.test_writer_sweep import find_offenders
        gate = self._gate()
        d = Path(tempfile.mkdtemp())
        for inline in (True, False):
            p = d / f"planted_chat_{inline}.py"; p.write_text(self._text(inline))
            self.assertTrue(find_offenders(p, check_organism_import=False), inline)
            self.assertTrue(gate.sweep([p]), inline)
        shutil.rmtree(d, ignore_errors=True)

    def test_a_chat_sense_importing_organism_is_caught(self) -> None:
        gate = self._gate()
        d = Path(tempfile.mkdtemp()) / "senses"; d.mkdir()
        p = d / "chat_planted.py"; p.write_text("from genome.machinery import Organism\n")
        self.assertTrue(gate.sweep([p]))
        shutil.rmtree(d.parent, ignore_errors=True)

    def test_the_real_chat_module_is_never_flagged(self) -> None:
        from tests.creature.test_writer_sweep import find_offenders
        real = ROOT / "creature" / "senses" / "chat.py"
        self.assertEqual(find_offenders(real, check_organism_import=True), [])
        self.assertEqual(self._gate().sweep([real]), [])

    def test_gate_g4_step_1_carries_the_chat_plant(self) -> None:
        """gate_g4.py's own step 1 plants a chat-shaped offender and prints its catch (the landing reads it)."""
        src = (ROOT / "tools" / "gate_g4.py").read_text()
        self.assertIn("chat sense's planted offender", src)


if __name__ == "__main__":
    unittest.main()
