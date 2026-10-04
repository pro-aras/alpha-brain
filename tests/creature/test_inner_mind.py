# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:30 +0400 — PREREG-INNER-1 §2 + §3 G1 / G4 + AMENDMENT 1 A2/A3/A7 (the law: research-1003 @
# 9c589b2, file sha256 127b063c…168d; the co-signed TEXT 857e07b2…faa82), test-first: red on f123190 (the mind knows no INNER).
"""tests/creature/test_inner_mind.py — the gene INNER in the MIND: the brain's inner turn on a SENSE body row whose backlog is 0.

One fixture tape of the scene world (120 training scenes, the LEAN body + a SENSE body line) with body rows PUBLISHED on the tape
right after chosen scenes (a reading with backlog 0 or 1), lived OFF (no INNER line) and ON. The brain calibrates at 20, 40 and 80
scenes, so the body row after scene 5 arrives before the first calibration (it must journal nothing and be counted), the rows after
scenes 31, 61 and 91 carry backlog 1 (never a turn), the eight others fire exactly once each.

THE PLANTED WEB. 120 scenes consolidate NO web edge (the scene world's words are nearly independent — the real web's 5,440
consolidated edges came from 192,795 hearings), so a first run of these tests saw every hop find no candidate and restart at the
self (chain positions all 1). The wiring under test needs candidates, so at the brain's FIRST calibration every life here swaps its
web L for a REAL genome.web.Web (built as tests/creature/test_inner_walk.py builds them) whose consolidated edges join the brain's
mature words; the mind keeps hearing into it. What these tests pin is the MIND's wiring (eligibility, the chain, the draw, the scene,
the row, the ledger, the resume); the real web's walk is the bench's (PREREG-INNER-1 G3)."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import creature.mind as MM
from brain.scene import world as W
from creature.tape import Tape
from genome.machinery import GenomeError, parse_genome
from tests.creature import _scene_tape as S

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
AT = "calibrate at 250 500 1000 2000 5000 10000"
INNER_LINE = "INNER    every body row when idle; walk lift; inhibit 2; restart 5"
BODY_LINE = "SENSE    body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss backlog refused_nmax"
N_TRAIN = 120
BODY_AT: Dict[int, int] = {5: 0, 30: 0, 31: 1, 45: 0, 60: 0, 61: 1, 75: 0, 90: 0, 91: 1, 100: 0, 110: 0, 119: 0}   # scene -> backlog
ELIGIBLE = [i for i, b in BODY_AT.items() if b == 0 and i >= 19]        # the 20th learn (scene 19) is the first calibration


def genome_text(inner: str = "", brain: bool = True, body: bool = True) -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), _TEMPLATE, count=1, flags=re.M)
    assert text != _TEMPLATE and text.count(AT) == 1
    text = text.replace(AT, "calibrate at 20 40 80")
    if not brain:
        text, n = re.subn(r"^BRAIN    .*$", "", text, count=1, flags=re.M)
        assert n == 1
        text, n = re.subn(r"^DRIVE    .*$", "", text, count=1, flags=re.M)
        assert n == 1
    lines = ([BODY_LINE] if body else []) + ([inner] if inner else [])
    return text + "\n" + "\n".join(lines) + ("\n" if lines else "")


def reading(backlog: int) -> Dict[str, object]:
    return {"moments": 0, "births": 0, "arrivals": 0, "budget_left": 400, "refused": 0, "restarts": 0, "mind_ms": None, "rss": 100.0,
            "backlog": int(backlog), "refused_nmax": 0}


def build_tape(root: Path, n_train: int, body_at: Dict[int, int]) -> List[int]:
    """The scene world's training rows (as tests/creature/_scene_tape.build writes them) with a BODY row published right after the
    chosen scenes' eye rows. Returns the body rows' seqs in order."""
    tape = Tape(root)
    clock = S._Clock(S.T0)
    seqs: List[int] = []
    for i in range(n_train):
        scene = W.train_scene(S.WS, i)
        rgb = W.render_scene(scene)[0]
        moment = f"sc{S.WS}t{i:06d}"
        for w in scene.words:
            tape.publish("ear", w.encode(), {"moment": moment, "source": "scene", "word": w, "scene": i}, "txt", at=clock())
        row = tape.publish("eye", S.png(rgb), {"moment": moment, "source": "scene", "kind": "train", "scene": i, "world_seed": S.WS},
                           "png", at=clock())
        S._truth(root, int(row["seq"]), {"kind": "train", "scene": i, "world_seed": S.WS, "scene_dict": scene.to_dict(), "said": list(scene.words)})
        if i in body_at:
            r = reading(body_at[i])
            b = tape.publish("body", json.dumps(r).encode("utf-8"), {"moment": f"body{i}", "source": "body", "reading": r}, "json", at=clock())
            seqs.append(int(b["seq"]))
    return seqs


def is_inner(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "inner"


def plant_web(m: "MM.Mind") -> None:
    """At the first calibration: web L becomes a real Web whose consolidated edges join EVERY word the brain has heard so far (a ring plus
    two chords, counts 3…), the node counts the real web's; the mind keeps hearing into it (a word matures later and its edges are
    already there — inner.candidates filters by maturity at the draw). Deterministic in the brain's heard vocabulary."""
    from tests.creature.test_inner_walk import web_of
    real = m.webs["L"]
    words = sorted({str(w) for o in range(m.brain.n_learned) for w in m.brain.seen[o][1]})
    assert len(words) >= 4, f"the fixture's brain has heard {len(words)} words at its first calibration; the planted web needs 4"
    nodes = {w: int(real.nodes.get(w, {}).get("n", 5)) or 5 for w in words}
    edges = [(words[i], words[(i + 1) % len(words)], 3 + i) for i in range(len(words))]
    edges += [(words[0], words[2], 9), (words[1], words[3], 7)]
    m.webs["L"] = web_of(nodes, edges, t=max(int(real.t), 100))


def drive(m: "MM.Mind", rows, on_eligible=None) -> None:
    """Consume `rows` as the body does, planting the web the moment the brain has calibrated once. `on_eligible(m, row)`, when given,
    REPLACES consume() for an eligible body row with consume's own body-branch order (the test's seam for the read-only pin)."""
    planted = False
    for row in rows:
        if not planted and m.brain is not None and m.brain.n_calibrations >= 1 and m.webs is not None:
            plant_web(m)
            planted = True
        if on_eligible is not None and row["sense"] == "body" and planted and row["meta"]["reading"]["backlog"] == 0:
            on_eligible(m, row)
        else:
            m.consume(row)


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="inner-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.body_seqs = build_tape(cls.tape_root, N_TRAIN, BODY_AT)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.off, cls.off_root = cls.live(genome_text())
        cls.on, cls.on_root = cls.live(genome_text(INNER_LINE))
        cls.J_off, cls.J_on = S.journal(cls.off_root), S.journal(cls.on_root)
        cls.inner = [r for r in cls.J_on if is_inner(r)]

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, text: str, rows=None, blind=frozenset()):
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root, blind=blind)
        drive(m, cls.rows if rows is None else rows)
        return m, root

    def body_rows(self):
        return [r for r in self.rows if r["sense"] == "body"]


class Fires(_Lives):
    def test_exactly_one_inner_row_per_eligible_body_row(self) -> None:
        body = self.body_rows()
        self.assertEqual(len(body), len(BODY_AT))
        eligible = [r for r in body if r["meta"]["reading"]["backlog"] == 0 and int(r["meta"]["moment"][4:]) >= 19]
        self.assertEqual(len(eligible), len(ELIGIBLE))
        self.assertEqual([r["seq"] for r in self.inner], [r["seq"] for r in eligible])
        self.assertEqual([r["n"] for r in self.inner], list(range(len(eligible))))
        self.assertEqual([r["chain"] for r in self.inner], [1, 2, 3, 4, 5, 1, 2, 3])

    def test_the_counts_name_every_skipped_row_by_reason(self) -> None:
        st = self.on.brain_status()["inner"]
        self.assertEqual(st["turns"], len(ELIGIBLE))
        self.assertEqual(st["skipped"], {"not calibrated": 1, "backlog": 3})
        self.assertNotIn("inner", self.off.brain_status() or {})

    def test_on_is_off_plus_the_inner_rows(self) -> None:
        self.assertGreater(len(self.inner), 0, "no inner row: this test would pass by absence (#243 (4))")
        on_minus = [json.dumps(r) for r in self.J_on if not is_inner(r)]
        self.assertEqual(on_minus, [json.dumps(r) for r in self.J_off])
        self.assertGreater(len(self.J_off), 0)

    def test_absent_the_line_nothing_is_written(self) -> None:
        self.assertEqual(sum(is_inner(r) for r in self.J_off), 0)
        self.off.snapshot()
        ledger = json.loads((self.off_root / "state" / "ledger.json").read_text())
        self.assertNotIn("inner", ledger)
        self.on.snapshot()
        ledger_on = json.loads((self.on_root / "state" / "ledger.json").read_text())
        self.assertEqual(ledger_on["inner"]["state"]["n"], len(ELIGIBLE))


class TheChain(_Lives):
    def test_every_row_re_sees_a_scene_that_carried_its_topic(self) -> None:
        self.assertEqual(len(self.inner), len(ELIGIBLE), "the presence count: the loop below is over every inner row")
        b = self.on.brain
        for r in self.inner:
            with self.subTest(n=r["n"]):
                self.assertIn(r["topic"], r["heard"])
                self.assertLess(r["learned"], b.n_learned)
                self.assertEqual(r["moment"], b.moments[r["learned"]])
                self.assertEqual(r["scene"], b.scenes[r["learned"]])
                self.assertEqual((r["world"], r["world_seed"]), ("scene", S.WS))
                self.assertIn(r["learned"], b.scenes_with(r["topic"]))
                for k in ("say", "ask", "expected", "held", "n_hyp", "surprise", "candidates", "topic_source"):
                    self.assertIn(k, r)
                if r["surprise"] is not None:
                    self.assertTrue(0.0 <= r["surprise"] <= 1.0)

    def test_the_first_thought_of_a_chain_is_the_self_s_least_reliable_word(self) -> None:
        first = [r for r in self.inner if r["chain"] == 1]
        self.assertEqual(len(first), 2)
        # the self AT that moment: a life stopped right at the row, read through the production rule
        from creature import inner as I
        for r in first:
            idx = next(i for i, row in enumerate(self.rows) if row["seq"] == r["seq"])
            m, _root = self.live(genome_text(INNER_LINE), rows=self.rows[:idx])
            topic, source, _table = I.first_topic(m.self_node, set(m.brain.L.mature_words()))
            self.assertEqual((r["topic"], r["topic_source"]), (topic, source), f"n {r['n']}")
            self.assertTrue(r["topic_source"].startswith("self"))

    def test_the_hops_follow_the_web_or_say_why_not(self) -> None:
        hops = [r for r in self.inner if r["chain"] > 1]
        self.assertEqual(len(hops), len(self.inner) - 2)
        sources = [r["topic_source"] for r in hops]
        for r, prev in zip(hops, [x for x in self.inner if x["n"] in {h["n"] - 1 for h in hops}]):
            with self.subTest(n=r["n"]):
                self.assertEqual(prev["n"], r["n"] - 1)
                said = prev["say"]["words"] if prev["say"] else [prev["topic"]]
                self.assertEqual(r["from"], said)
                if r["topic_source"].startswith("web"):
                    names = [c[0] for c in r["candidates"]]
                    self.assertIn(r["topic"], names)
                    if r["topic_source"] == "web":
                        last2 = [x["topic"] for x in self.inner if x["n"] in (r["n"] - 1, r["n"] - 2) and x["chain"] < r["chain"]]
                        self.assertNotIn(r["topic"], last2)
                else:
                    self.assertEqual(r["candidates"], [])
                    self.assertEqual(r["topic_source"], "self (restart: no candidate)")
        # the presence count of web hops is printed by the mind's own counts; a fixture with no consolidated edge among mature words
        # could not test the walk here — the walk's mechanics are tests/creature/test_inner_walk.py's on a hand-built web
        print(f"[inner-mind] hops {len(hops)} · sources {dict((s, sources.count(s)) for s in set(sources))}")


class Determinism(_Lives):
    def test_two_lives_write_the_same_inner_rows(self) -> None:
        _m, root = self.live(genome_text(INNER_LINE))
        again = [json.dumps(r) for r in S.journal(root) if is_inner(r)]
        self.assertEqual(again, [json.dumps(r) for r in self.inner])
        self.assertGreater(len(again), 0)

    def test_the_brain_the_web_and_the_self_are_what_they_were_around_every_inner_turn(self) -> None:
        """The pin is on _inner_turn ITSELF: consume()'s body branch first journals the reading and lets the SELF observe its claim B1
        (the self legitimately moves there — a first draft measured around the whole consume and read that as the inner turn's)."""
        root = S.link_root(self.tape_root, self.tmp / "ro" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text(INNER_LINE))
        m = MM.Mind(gp, root)
        checked = []

        def eligible(mind, row):
            mind._consume_body(row)                      # consume()'s own body-branch order, step by step
            if mind.self_node is not None:
                mind._self_body(row)
            h, wd, sd = mind.brain.state_hash(), mind.webs["L"].dumps(), json.dumps(mind.self_node.to_dict(), sort_keys=True)
            n0 = mind.inner_state["n"]
            mind._inner_turn(row)
            self.assertEqual((mind.brain.state_hash(), mind.webs["L"].dumps(), json.dumps(mind.self_node.to_dict(), sort_keys=True)), (h, wd, sd))
            checked.append(mind.inner_state["n"] - n0)

        drive(m, self.rows, on_eligible=eligible)
        self.assertEqual(len(checked), len(ELIGIBLE))
        self.assertEqual(sum(checked), len(ELIGIBLE), "every checked row took its turn (the pin was read around a real turn)")


class Resume(_Lives):
    def test_a_resume_mid_chain_writes_the_same_inner_rows(self) -> None:
        # the life is cut right after its 2nd inner turn (chain position 2), snapshotted, resumed, and fed the rest of the tape
        cut_seq = self.inner[1]["seq"]
        idx = next(i for i, row in enumerate(self.rows) if row["seq"] == cut_seq)
        root = S.link_root(self.tape_root, self.tmp / "resume" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text(INNER_LINE))
        m = MM.Mind(gp, root)
        drive(m, self.rows[: idx + 1])
        m.snapshot()
        self.assertEqual(json.loads((root / "state" / "ledger.json").read_text())["inner"]["state"]["pos"], 2)
        r2, last_seq = MM.Mind.resume(gp, root)
        self.assertEqual(last_seq, cut_seq)
        self.assertEqual(r2.inner_state["n"], 2)
        self.assertTrue(r2.web_restored, "the planted web came back with the snapshot")
        for row in self.rows[idx + 1:]:                 # the web is restored, so no second planting here
            r2.consume(row)
        got = {r["n"]: json.dumps(r) for r in S.journal(root) if is_inner(r)}     # AMENDMENT 1 A7: read by inner index n
        want = {r["n"]: json.dumps(r) for r in self.inner}
        self.assertEqual(got, want)


class Refusals(_Lives):
    def test_refused_beside_no_brain_line_by_name(self) -> None:
        with self.assertRaises(GenomeError) as e:
            self.live(genome_text(INNER_LINE, brain=False), rows=self.rows[:5])
        self.assertIn("INNER", str(e.exception))
        self.assertIn("BRAIN", str(e.exception))

    def test_refused_beside_no_sense_body_line_by_name(self) -> None:
        with self.assertRaises(GenomeError) as e:
            self.live(genome_text(INNER_LINE, body=False), rows=self.rows[:5])
        self.assertIn("INNER", str(e.exception))
        self.assertIn("SENSE body", str(e.exception))

    def test_the_same_genomes_without_the_line_start(self) -> None:
        self.live(genome_text(brain=False), rows=self.rows[:5])
        self.live(genome_text(body=False), rows=self.rows[:5])

    def test_under_blind_brain_there_is_no_brain_and_no_inner_turn(self) -> None:
        m, root = self.live(genome_text(INNER_LINE), blind=frozenset({"brain"}))
        self.assertIsNone(m.brain)
        self.assertEqual(sum(is_inner(r) for r in S.journal(root)), 0)
        self.assertEqual(m.inner_counts["skipped"], {"no brain": len(BODY_AT)})

    def test_the_declared_values_are_read(self) -> None:
        d = parse_genome(genome_text(INNER_LINE)).declared["INNER"]
        self.assertEqual(d, {"trigger": "body idle", "walk": "lift", "inhibit": 2, "restart": 5})


if __name__ == "__main__":
    unittest.main()
