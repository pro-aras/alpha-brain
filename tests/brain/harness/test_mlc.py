# edit: Claude (Fable 5.1), 2026-09-24 18:17 +0400 — the MLC side tape's validator and the 0g LEAK CHECK, with its planted
# +2 episode (the negative control the PREREG names: "a planted +2 episode must be caught").
from __future__ import annotations

import unittest

from brain.world import mlc as M
from brain.world.families import LETTER_NAMES


def _rows(pairs, slot: int = 0, episode: int = 0, after_seq: int = 10):
    """pairs: [(x_name, y_name)] → ASK+FEEDBACK rows whose operand cache row encodes x (row = its index)."""
    rows = []
    n = 0
    for x, y in pairs:
        n += 1
        ask = M.make_mlc_row(n, after_seq, episode, "ASK", "L4", f"MLC:{episode}:study:{x}",
                             {"cues": [f"MLC{slot}"], "operands": [{"kind": "row", "value": LETTER_NAMES.index(x)}],
                              "candidate_rows": None, "answer_kind": "NAME"})
        n += 1
        fb = M.make_mlc_row(n, after_seq, episode, "FEEDBACK", "L4", f"MLC:{episode}:study:{x}", {"ask_seq": ask["seq"], "right": y})
        rows += [ask, fb]
    return rows


def _char_of_row(row: int):
    return ("latin-lower", LETTER_NAMES[row])


class TestMlc(unittest.TestCase):
    def test_shift_3_passes(self) -> None:
        pairs = [(LETTER_NAMES[i], LETTER_NAMES[(i + 3) % 26]) for i in (0, 5, 9, 12, 20, 23)]
        r = M.leak_check(_rows(pairs), _char_of_row)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["n_pairs"], 6)

    def test_planted_plus_two_is_caught(self) -> None:
        pairs = [(LETTER_NAMES[i], LETTER_NAMES[(i + 2) % 26]) for i in (0, 5, 9)]
        r = M.leak_check(_rows(pairs), _char_of_row)
        self.assertFalse(r["pass"])
        self.assertEqual({v["kind"] for v in r["violations"]}, {"order_family_pair"})
        self.assertTrue(all(v["diff"] == 2 for v in r["violations"]))

    def test_plus_one_and_identity_are_caught(self) -> None:
        r = M.leak_check(_rows([("a", "b"), ("c", "c"), ("f", "e")]), _char_of_row)
        self.assertEqual(sorted(v["diff"] for v in r["violations"]), [0, 1, 1])

    def test_real_cue_mark_is_refused(self) -> None:
        with self.assertRaises(M.MlcError):
            M.make_mlc_row(1, 10, 0, "ASK", "L4", "x", {"cues": ["TWO_AFTER"], "operands": [{"kind": "row", "value": 0}],
                                                       "candidate_rows": None, "answer_kind": "NAME"})

    def test_seq_offset_and_sha(self) -> None:
        rows = _rows([("a", "d")])
        self.assertGreaterEqual(rows[0]["seq"], M.MLC_SEQ_BASE)
        self.assertEqual(rows[1]["payload"]["ask_seq"], rows[0]["seq"])
        bad = dict(rows[1]); bad["payload"] = dict(bad["payload"]); bad["payload"]["right"] = "e"
        with self.assertRaises(M.MlcError):
            M.validate_mlc_row(bad)


if __name__ == "__main__":
    unittest.main()
