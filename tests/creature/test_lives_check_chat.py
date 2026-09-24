# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:50 +0400 — A4L-LANG task 10 (docs/briefs/A4L-LANG.md): the
# 8 h check prints the ten chat STATUS keys, and counts a chat `say` row APART from the think-mouth's `say` rows (#180: two
# mechanisms, two names) — against the shapes LANDED by creature/mind.py:_consume_chat/_consume_grade.
import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("lives_check_chat", Path(__file__).resolve().parents[2] / "tools" / "lives" / "check.py")
check = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(check)

ROWS = [
    {"seq": 9, "say": {"frame": "red box", "seq": 9, "heard": "yes", "episodes": [1, 2]}},                       # the think-mouth
    {"seq": 10, "say": {"kind": "chat", "id": "c0001", "heard": ["what", "is", "this"], "chain": ["it", "is", "ring"]}},
    {"seq": 11, "say": {"kind": "chat", "id": "c0002", "heard": ["what", "is", "this"], "chain": []}},
    {"seq": 12, "grade": {"id": "c0001", "right": True, "novel": False, "kind": "chat"}},
    {"seq": 13, "grade": {"id": "q1", "right": True, "novel": False}},
]
KEYS = ("chats", "chat_answered", "chat_abstained", "chat_refused_form", "chat_refused_content", "chat_words_mean",
        "chat_longest", "chat_graded", "chat_graded_right", "chat_graded_novel")


class ChatCounts(unittest.TestCase):
    def test_a_chat_say_is_never_counted_as_the_mouths_say(self):
        c = check.journal_counts(ROWS)
        self.assertEqual(c["say"], 1)
        self.assertEqual(c["chat_say"], 2)
        self.assertEqual(c["chat_grade"], 1)


class ChatStatusLine(unittest.TestCase):
    def test_the_line_names_all_ten_keys(self):
        st = {k: i for i, k in enumerate(KEYS)}
        line = check.chat_status_line(st)
        for k in KEYS:
            self.assertIn(f"{k} {st[k]}", line)

    def test_an_older_body_reads_not_recorded(self):
        self.assertIn("chats not recorded", check.chat_status_line({}))

    def test_main_prints_the_chat_line(self):
        root = Path(tempfile.mkdtemp())
        (root / "STATUS.json").write_text(json.dumps({"moments": 1, "chats": 3, "chat_answered": 2}))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            check.main(["--root", str(root)])
        self.assertIn("[check] chat: chats 3 · chat_answered 2", buf.getvalue())
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
