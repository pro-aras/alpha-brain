# edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 23:23 +0400 — PREREG-EYE-1 §3/§4 (G-LOOK-UNIT, M-FIRE):
# the chosen look's unit corpus — fires only on the doubt, at the locus, once a canvas; flag-off byte-identity.
"""tests/creature/test_look_mind.py — PREREG-EYE-1's THE CHOSEN LOOK in the MIND: after the DRIVE turn, a leading
hypothesis holding NO word gets ONE forced glance at its locus, the turn is re-read, and the learn runs on it.
The fixture is test_drive_mind.py's own (the 120-scene lean life), ON the DRIVE line, with mind._look set after
construction (the instrument's knob — every organism caller keeps None)."""
from __future__ import annotations

import json
import unittest

from tests.creature import test_drive_mind as D


def is_turn(r):
    return r.get("kind") == "brain" and r.get("act") == "turn"


def is_learn(r):
    return r.get("kind") == "brain" and r.get("act") == "learn"


class TestChosenLook(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = D.Path(D.tempfile.mkdtemp(prefix="look-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = D.S.build(cls.tape_root, n_train=D.N_TRAIN)
        cls.rows = D.S.rows(cls.tape_root)
        cls.n = 0
        cls.off_root = cls.live(look=False)
        cls.on_root = cls.live(look=True)
        cls.plain_root = cls.live(look=False)
        cls.J_off = D.S.journal(cls.off_root)
        cls.J_on = D.S.journal(cls.on_root)
        cls.J_plain = D.S.journal(cls.plain_root)

    @classmethod
    def tearDownClass(cls) -> None:
        D.shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, look: bool):
        cls.n += 1
        root = D.S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(D.lean_text(D.DRIVE_LINE))
        m = D.MM.Mind(gp, root, blind=frozenset())
        if look:
            m._look = {"on": True}
        try:
            for row in cls.rows:
                m.consume(row)
        finally:
            m.close()
        return root

    def test_flag_off_byte_identical_to_plain(self) -> None:
        # the knob's zero form: _look = None anywhere ⇒ the journal is byte-identical to a life that never heard of it
        self.assertEqual([json.dumps(r, sort_keys=True) for r in self.J_off],
                         [json.dumps(r, sort_keys=True) for r in self.J_plain])
        self.assertFalse(any("look" in r for r in self.J_off))

    def test_look_fires_only_on_the_doubt_at_most_once(self) -> None:
        turns = [r for r in self.J_on if is_turn(r)]
        looks = [r for r in turns if "look" in r]
        self.assertTrue(looks, "no look fired in 120 scenes — the instrument must fire somewhere (a silent gate proves nothing)")
        by_moment = {}
        for r in looks:
            rec = r["look"]
            self.assertTrue(rec["looked"])
            self.assertEqual(rec["held_before"], [])
            self.assertIn("at", rec)
            self.assertNotIn(r["moment"], by_moment, "a second look on one canvas")
            by_moment[r["moment"]] = rec

    def test_the_look_lands_at_the_doubted_thing_and_refeeds(self) -> None:
        learns = {(r["moment"], r["seq"]): r for r in self.J_on if is_learn(r)}
        turns = [r for r in self.J_on if is_turn(r)]
        for t in turns:
            if "look" not in t:
                continue
            rec = t["look"]
            # the learn row of the same moment carries the forced cell among its fixations (the re-feed)
            cand = [r for (m, _s), r in learns.items() if m == t["moment"]]
            self.assertTrue(cand, f"no learn row for the looked canvas {t['moment']}")
            self.assertIn(list(rec["at"]), [list(f) for f in cand[0]["fix"]],
                          f"the look's cell {rec['at']} is not in the learn row's fix {cand[0]['fix']}")
            # and the re-read turn's held_after is the re-read record's own (never the stale empty one)
            self.assertIn("held_after", rec)

    def test_no_look_where_a_word_is_held(self) -> None:
        # every looked turn had its leading held EMPTY before the look (held_before is the law's own record)
        for r in [r for r in self.J_on if is_turn(r) and "look" in r]:
            self.assertEqual(r["look"]["held_before"], [])


if __name__ == "__main__":
    unittest.main()
