# edit: Claude (Fable 5.1), 2026-09-22 22:24 +0400 — the 8 h CHECK's counters against the journal shapes the builders LANDED (the advisor's
# read at the wrap: the checker counted a top-level `act_chosen` (builder F's hands row) and a top-level `self` nothing writes; builder D's
# game acts are a DICT under `act` — moment rows carry the STRING `act: "glance"`/`"coarse"` — and builder A's self beliefs are think rows of
# kind `self`). RED first: `journal_counts` / `births_by_hour` did not exist (the counting sat inline in main()). Sight births are split by
# the moment row's own `source` (maker / game / folder / hands), the input of PREREG §19.11's sizing rule.
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("lives_check", Path(__file__).resolve().parents[2] / "tools" / "lives" / "check.py")
check = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(check)


ROWS = [
    {"seq": 1, "moment": "m1", "when": "2026-09-23T08:00:01Z", "glance": 0, "act": "glance", "source": "maker", "word": "circle", "births": [["sight", 1], ["words", 2]], "confirmed": [True, False, False, False]},
    {"seq": 2, "moment": "m1", "when": "2026-09-23T08:00:01Z", "glance": 1, "act": "glance", "source": "maker", "births": [["sight", 3]]},
    {"seq": 3, "moment": "m2", "when": "2026-09-23T08:00:16Z", "glance": 0, "act": "glance", "source": "game", "births": [["sight", 4]]},
    {"seq": 3, "act": "coarse", "glance": 4, "births": []},
    {"seq": 4, "act": {"game": "babyai-gotolocal", "act": "left", "act_idx": 0, "seq": 4}},               # builder D: the mind's game act
    {"seq": 5, "think": {"item": "self", "kind": "self", "outcome": "belief", "parked": False}},           # builder A: a self think
    {"seq": 6, "think": {"item": "circle", "kind": "word", "outcome": "belief", "parked": False}, "act_chosen": {"act": "run", "program": "p1.py", "seq": 6}},   # builder F: hands
    {"seq": 7, "moment": "m3", "when": "2026-09-23T09:00:01Z", "glance": 0, "act": "glance", "source": "hands", "births": [["sight", 5], ["sight", 6]]},
    {"seq": 8, "question": {"q": "what-is", "args": ["x.png"]}},
    {"seq": 9, "say": {"said": "circle"}},
    {"event": "start", "at": "2026-09-23T08:00:00Z"},
]


class JournalCounts(unittest.TestCase):
    def test_counts_every_landed_shape_by_its_own_key(self):
        c = check.journal_counts(ROWS)
        self.assertEqual(c["acts_game"], 1, "builder D's game act is a DICT under `act`; the string `act: glance/coarse` on moment rows is not an act")
        self.assertEqual(c["hands_runs"], 1)
        self.assertEqual(c["self_thinks"], 1)
        self.assertEqual(c["think"], 2)
        self.assertEqual(c["question"], 1); self.assertEqual(c["say"], 1)
        self.assertNotIn("self", c, "nothing journals a top-level `self` key — a counter that can only read 0 is not printed")
        self.assertEqual(c["moments"], 4); self.assertEqual(c["canvases"], 3); self.assertEqual(c["coarse_rows"], 1)


class BirthsByHour(unittest.TestCase):
    def test_sight_births_per_hour_split_by_source(self):
        hours, by_hour, by_source = check.births_by_hour(ROWS)
        self.assertEqual(hours, ["2026-09-23T08", "2026-09-23T09"])
        self.assertEqual([by_hour[h] for h in hours], [3, 2], "sight births only (the words birth is not counted); every glance row counts")
        self.assertEqual(by_source["2026-09-23T08"], {"maker": 2, "game": 1})
        self.assertEqual(by_source["2026-09-23T09"], {"hands": 2})

    def test_confirmed_share_counts_glances_not_rows(self):
        share = check.confirmed_share_by_hour(ROWS)
        self.assertAlmostEqual(share["2026-09-23T08"], 0.25, places=6, msg="`confirmed` is a LIST per located glance: 1 of 4 confirmed reads 0.25, never 1.0")
        self.assertIsNone(share.get("2026-09-23T09"), "no `confirmed` field in that hour → no share (not 0.0)")


if __name__ == "__main__":
    unittest.main()
