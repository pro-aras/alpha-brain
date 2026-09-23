# edit: Claude (Fable 5.1), 2026-09-22 18:29 +0400 — THE ONE LIFE plan §4 L-1 / Appendix A «what is owed»: REPLAY's `hash` is a declared VOLATILE
# field when the reader's commit is not the life's (life 3b's REPLAY FAIL was that definition, 16:49); and the reader's version
# string must name the reader that read a record (every verdict-8h-v31/results.json said «v3»). Written RED first.
import unittest


class CompareIgnore(unittest.TestCase):
    def test_hash_difference_is_a_divergence_by_default(self):
        from creature.replay import compare
        got = [{"seq": 1, "moment": "a", "hash": "x"}]; want = [{"seq": 1, "moment": "a", "hash": "y"}]
        self.assertEqual(compare(got, want), (1, "hash"))

    def test_ignored_field_does_not_diverge_but_another_field_still_does(self):
        from creature.replay import compare
        got = [{"seq": 1, "moment": "a", "hash": "x"}, {"seq": 2, "moment": "b", "hash": "x"}]
        want = [{"seq": 1, "moment": "a", "hash": "y"}, {"seq": 2, "moment": "c", "hash": "y"}]
        self.assertEqual(compare(got[:1], want[:1], ignore={"hash"}), None)
        self.assertEqual(compare(got, want, ignore={"hash"}), (2, "moment"))


class ReaderVolatileFields(unittest.TestCase):
    def test_hash_is_volatile_only_across_commits(self):
        from tools.verdict_g4 import replay_ignore_fields
        self.assertEqual(replay_ignore_fields("abc1234", "abc1234"), set())
        self.assertEqual(replay_ignore_fields("abc1234", "def5678"), {"hash"})
        self.assertEqual(replay_ignore_fields("abc1234", None), {"hash"})      # a life whose commit is not on its root: unknown = not the same

    def test_reader_version_names_v32(self):
        from tools.verdict_g4 import READER_VERSION
        self.assertIn("v3.3", READER_VERSION)   # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 bumped the reader to v3.3 (#237 (j))


if __name__ == "__main__":
    unittest.main()
