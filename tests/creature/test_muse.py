# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 06:50 +0400 — G-UNIT of PREREG-CONTEMPLATE-1
# (docs/brain/muse/PREREG-CONTEMPLATE-1.md, signed 2026-10-09 23:01), the MIND half: the muse behind
# Mind(..., muse: bool = False). Test-first (RED on 823c02d: creature/muse.py and the flag do not exist).
"""tests/creature/test_muse.py — the law's §2 G-UNIT (a)-(e) + G-PLANT, mind level:

  (a) flag OFF: a scripted chat stream (the law's own planted sentence inside it) consumes
      byte-identical to the no-argument construction — zero muse rows, zero statused beliefs, zero
      muse wants, the muse counters untouched;
  (b) the trigger fires ONLY on the declared classes — the law's own sentences: «you are alpha»
      fires (a self word in the web), «the circle is big» does not (all-known, self-free), a
      once-heard word does not, a twice-heard never-consolidated word fires (class (b));
  (c) the 25-sentence budget holds — 26 distinct self-touching sentences spawn exactly 2 chains
      (heard 1 and 26), every skip journaled;
  (d) tentative rows are invisible to every trusted read — the store (both modes), the standing
      chain, the SELF's claims, the brain (hash-pinned), the composer (a re-ask while tentative
      still abstains) — presence counts printed beside every "0 of N" (SOLUTIONS #168);
  (e) determinism ×2 to the last digit — journal, beliefs file, ask/out, ASKED.json, world/questions.

The fixture: 60 scene-world training scenes (the brain learns, the webs hear), then a PLANTED web
(test_inner_mind's own precedent — 60 scenes consolidate nothing real) carrying the vocabulary's
consolidated ring + alpha (n=1, the name, heard — one consolidated chord to «circle» so the walk can
walk) + zog (n=2, silent) + vex (n=1); the SELF gains the hearsay claim «you are alpha.» (the KW-1
implanted-knowledge form). Chat rows are published by the door's own scan_once at fixture build.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path
from typing import Dict, List, Optional

import creature.muse as MUSE
from brain.scene import world as W
from creature.mind import Mind
from creature.senses import chat as chat_sense
from creature.tape import Tape
from genome import think, web as _web
from tests.creature import _scene_tape as S
from tests.creature.test_inner_walk import web_of

ROOT = Path(__file__).resolve().parents[2]
N_TRAIN = 60
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3 nearest; "
              "calibrate at 20 40 60 and before a sitting; replay none; hears scene")
WORLD_LINE = S.scene_line(train=N_TRAIN)
VOCAB = ["big", "blue", "circle", "cross", "dax", "green", "red", "ring", "small", "square", "star",
         "triangle", "white", "yellow"]
CHAT_TEXTS = {"planted": "you are alpha", "control": "the circle is big",
              "once": "the vex is here", "twice": "the zog is here"}
BUDGET_TEXTS = ([f"you are alpha {v}" for v in VOCAB] + [f"are you alpha {v}" for v in VOCAB[:12]])
HEARD = {"planted": ["you", "are", "alpha"], "control": ["the", "circle", "is", "big"],
         "once": ["the", "vex", "is", "here"], "twice": ["the", "zog", "is", "here"]}


def genome_text() -> str:
    text = (ROOT / "genome" / "ladder" / "A4L-LANG.genome").read_text()
    return text + "\n" + BRAIN_LINE + "\n" + WORLD_LINE + "\n"


def build_fixture(root: Path) -> None:
    """The shared tape: 60 scene moments (ear words in the parent's order + the eye row), then every
    chat the tests consume, published by the door's own road (chat/in + scan_once)."""
    tape = Tape(root)
    clock = S._Clock(S.T0)
    for i in range(N_TRAIN):
        scene = W.train_scene(S.WS, i)
        rgb = W.render_scene(scene)[0]
        moment = f"sc{S.WS}t{i:06d}"
        for w in scene.words:
            tape.publish("ear", w.encode(), {"moment": moment, "source": "scene", "word": w, "scene": i}, "txt", at=clock())
        tape.publish("eye", S.png(rgb), {"moment": moment, "source": "scene", "kind": "train", "scene": i, "world_seed": S.WS},
                     "png", at=clock())
    (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
    texts = dict(CHAT_TEXTS)
    for k, t in enumerate(BUDGET_TEXTS):
        texts[f"b{k:03d}"] = t
    for cid, text in texts.items():
        (root / "chat" / "in" / f"{cid}.json").write_text(json.dumps({"id": cid, "text": text}))

    def pub(sense, payload, meta, ext):
        return tape.publish(sense, payload, meta, ext, at=clock())

    for _ in texts:
        chat_sense.scan_once(pub, root, canvas=128, letters=8)


def plant(m: Mind) -> None:
    """The planted web + the hearsay claim (test_inner_mind's precedent): the mind keeps hearing into
    the planted web. alpha carries one consolidated chord to «circle» so the chain's walk has a road."""
    real = m.webs["L"]
    words = sorted({str(w) for o in range(m.brain.n_learned) for w in m.brain.seen[o][1]})
    assert len(words) >= 4, f"the fixture's brain heard {len(words)} words; the planted web needs the vocabulary"
    nodes = {w: int(real.nodes.get(w, {}).get("n", 5)) or 5 for w in words}
    nodes["alpha"] = 1                      # the organism's name, heard once
    nodes["zog"] = 2                        # heard twice, never consolidated (class (b))
    nodes["vex"] = 1                        # heard once: neither class
    edges = [(words[i], words[(i + 1) % len(words)], 3 + i) for i in range(len(words))]
    edges += [(words[0], words[2], 9), (words[1], words[3], 7), ("alpha", "star", 9)]   # star: the walk's road — and
    # NEVER a word of the law's control («the circle is big»), which must stay self-free (one edge from the self fires)
    m.webs["L"] = web_of(nodes, edges, t=max(int(real.t), 100))
    m.self_node.place(_web.Claim("HEAR-1", "you are alpha.", "usually", 0.5,
                                 source="implanted-knowledge", author="toy-parent"))


def muse_rows(root: Path) -> List[dict]:
    return [r for r in S.journal(root) if r.get("kind") == "muse"]


def out_answer(root: Path, cid: str) -> Optional[list]:
    p = root / "chat" / "out" / f"{cid}.json"
    return json.loads(p.read_text())["answer"] if p.exists() else None


class _Lives(unittest.TestCase):
    """One shared fixture tape per class; every test drives fresh minds over the rows it needs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="muse-gunit-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        build_fixture(cls.tape_root)
        cls.rows = S.rows(cls.tape_root)
        cls._n = 0

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def live(self, muse_flag: bool, chat_cids: Optional[List[str]] = None, close: bool = True):
        """A fresh mind over the fixture rows: every non-chat row, plus the named chats (None = all),
        in tape order; the web + claim are planted between the last scene row and the first chat."""
        type(self)._n += 1
        root = S.link_root(self.tape_root, self.tmp / f"run{type(self)._n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text())
        m = Mind(gp, root, muse=muse_flag)
        wanted = None if chat_cids is None else set(chat_cids)
        planted = False
        for row in self.rows:
            if row["sense"] == "chat":
                if not planted:
                    plant(m)
                    planted = True
                if wanted is not None and str((row.get("meta") or {}).get("id")) not in wanted:
                    continue
            m.consume(row)
        self.assertTrue(planted, "presence: the plant ran before the chats")
        if close:
            m.close()
        return m, root


class TriggerPure(_Lives):
    def test_the_declared_classes_and_only_they_fire(self) -> None:
        m, _root = self.live(False, chat_cids=[])      # any mind: the web/self fixtures are what is read
        web = m.webs["L"]
        self_ws = MUSE.self_words(m.self_node)
        mature = {str(w) for w in m.brain.L.mature_words()}
        cases = {cid: MUSE.trigger(HEARD[cid], web, self_ws, mature) for cid in ("planted", "control", "once", "twice")}
        print(f"[muse-trigger] self words {sorted(self_ws)} · matrix "
              f"{ {k: (v['fire'], v['anchors'], v['classes']) for k, v in cases.items()} }")
        self.assertEqual(cases["planted"]["anchors"], ["alpha"])
        self.assertEqual(cases["planted"]["classes"], ["self"])
        self.assertTrue(cases["planted"]["fire"])
        self.assertFalse(cases["control"]["fire"], "the law's own control must not fire")
        self.assertFalse(cases["once"]["fire"], "a once-heard word (n=1) is neither class")
        self.assertTrue(cases["twice"]["fire"])
        self.assertEqual(cases["twice"]["anchors"], ["zog"])
        self.assertEqual(cases["twice"]["classes"], ["novel"])
        self.assertIn("alpha", self_ws, "presence: the hearsay claim carries the name")


class FlagOffByteIdentical(_Lives):
    def test_a_the_scripted_chat_stream_consumes_byte_identical(self) -> None:
        m_off, root_off = self.live(False)
        m_noarg_root = S.link_root(self.tape_root, self.tmp / "run-noarg" / "r")
        gp = m_noarg_root.parent / "g.genome"
        gp.write_text(genome_text())
        m_plain = Mind(gp, m_noarg_root)               # no muse argument at all: the old road
        planted = False
        for row in self.rows:
            if row["sense"] == "chat" and not planted:
                plant(m_plain)
                planted = True
            m_plain.consume(row)
        m_plain.close()
        self.assertEqual(S.journal_bytes(root_off), S.journal_bytes(m_noarg_root),
                         "flag OFF (and no arg) is byte-identical")
        out_off = sorted((root_off / "chat" / "out").glob("*.json"))
        out_plain = sorted((m_noarg_root / "chat" / "out").glob("*.json"))
        self.assertEqual([p.name for p in out_off], [p.name for p in out_plain])
        for a, b in zip(out_off, out_plain):
            self.assertEqual(a.read_bytes(), b.read_bytes(), a.name)
        self.assertEqual(muse_rows(root_off), [], "OFF: zero muse rows in the journal")
        self.assertEqual(m_off._muse, {"heard": 0, "chains_started": 0, "chains": {}, "skipped": {}},
                         "OFF: the muse state was never touched")
        bel = root_off / "state" / "beliefs.jsonl"
        statused = [r for r in (think.read_considered(bel) if bel.exists() else [])]
        print(f"[muse-gunit a] chats {len(CHAT_TEXTS) + len(BUDGET_TEXTS)} · journal bytes equal · "
              f"statused rows {len(statused)} · muse rows 0")
        self.assertEqual(statused, [])
        self.assertFalse((root_off / "ask" / "out" / "ASKED.json").exists() and
                         any(str(k).startswith("muse:") for k in
                             json.loads((root_off / "ask" / "out" / "ASKED.json").read_text())),
                         "OFF: no muse want was ever formed")


class TriggerClasses(_Lives):
    def test_b_self_touching_fires_and_the_same_breath_answer_abstains(self) -> None:
        m, root = self.live(True, chat_cids=["planted"])
        chains = m._muse["chains"]
        steps = [r for r in muse_rows(root) if r.get("act") == "step"]
        print(f"[muse-gunit b] chains {len(chains)} · steps {len(steps)} · heard {m._muse['heard']}")
        self.assertEqual(m._muse["heard"], 1)
        self.assertEqual(len(chains), 1, "the planted sentence spawns exactly one chain")
        cid, chain = next(iter(chains.items()))
        self.assertEqual(cid, MUSE.seed_of(HEARD["planted"]))
        self.assertEqual(chain["heard"], HEARD["planted"])
        self.assertGreaterEqual(len(chain["beliefs"]), 1, "M-CHAIN's unit half: ≥ 1 tentative belief")
        self.assertGreaterEqual(len(chain["questions"]), 1, "M-CHAIN's unit half: ≥ 1 counter-question")
        self.assertGreaterEqual(len(steps), 1)
        self.assertLessEqual(len(steps), MUSE.MUSE_STEPS)
        self.assertEqual(steps[0]["topic"], "alpha")
        self.assertEqual(steps[0]["topic_source"], "heard")
        # M-HONEST at unit scale: the same-breath answer stays an abstention
        self.assertIsNone(out_answer(root, "planted"), "the chain never speaks; the composer abstains")

    def test_b_all_known_self_free_does_not_fire(self) -> None:
        m, root = self.live(True, chat_cids=["control"])
        print(f"[muse-gunit b] control: heard {m._muse['heard']} · chains {m._muse['chains_started']} · "
              f"muse rows {len(muse_rows(root))}")
        self.assertEqual(m._muse["heard"], 1, "the sentence was heard (the budget's own count)")
        self.assertEqual(m._muse["chains_started"], 0)
        self.assertEqual(muse_rows(root), [], "a trigger-negative sentence journals nothing")

    def test_b_once_heard_does_not_fire(self) -> None:
        m, root = self.live(True, chat_cids=["once"])
        self.assertEqual(m._muse["heard"], 1)
        self.assertEqual(m._muse["chains_started"], 0)
        self.assertEqual(muse_rows(root), [])

    def test_b_twice_heard_never_consolidated_fires(self) -> None:
        m, root = self.live(True, chat_cids=["twice"])
        self.assertEqual(m._muse["chains_started"], 1)
        chain = next(iter(m._muse["chains"].values()))
        self.assertEqual(chain["anchors"], ["zog"])
        self.assertEqual(chain["classes"], ["novel"])


class Budget(_Lives):
    def test_c_one_chain_per_25_heard_sentences(self) -> None:
        cids = [f"b{k:03d}" for k in range(26)]
        m, root = self.live(True, chat_cids=cids)
        skips = [r for r in muse_rows(root) if r.get("act") == "budget-skip"]
        print(f"[muse-gunit c] heard {m._muse['heard']} · chains {m._muse['chains_started']} · "
              f"budget-skip rows {len(skips)}")
        self.assertEqual(m._muse["heard"], 26)
        self.assertEqual(m._muse["chains_started"], 2, "chains at heard 1 and heard 26")
        self.assertEqual(len(skips), 24, "every suppressed firing is journaled, never silent")
        heard_at = sorted(r["heard_n"] for r in skips)
        self.assertEqual(heard_at, list(range(2, 26)))


class TrustedReads(_Lives):
    def test_d_tentatives_are_invisible_to_every_trusted_read(self) -> None:
        m, root = self.live(True, chat_cids=["planted"], close=False)
        bel = root / "state" / "beliefs.jsonl"
        raw = [json.loads(l) for l in bel.read_text().splitlines() if l.strip()]
        n_statused = sum(1 for r in raw if "status" in r)
        self.assertGreater(n_statused, 0, "presence: the chain actually filed statused rows")
        flat, folded = think.read_beliefs(bel), think.read_beliefs(bel, fold=True)
        leaks = [r for r in flat + folded if "status" in r]
        print(f"[muse-gunit d] store: {len(leaks)} of {n_statused} statused rows visible to trusted reads")
        self.assertEqual(leaks, [])
        # the standing chain never sees a tentative: a trusted believe() on the same word files fresh
        row = think.believe("alpha", [1], [123], m.org.t, bel)
        self.assertEqual(row["kind"], "belief", "a fresh standing belief, never a revisit of the tentative")
        self.assertNotIn("status", row)
        # the SELF's trusted claims carry no muse content (the chain never touches the self)
        claims = m.self_node.claims
        museish = [k for k, c in claims.items() if "muse" in (c.source or "") or k.startswith("muse")]
        print(f"[muse-gunit d] self: {len(museish)} muse-sourced claims of {len(claims)} present")
        self.assertEqual(museish, [])
        self.assertIn("HEAR-1", claims, "presence: the hearsay claim is there to be read")
        # the composer (a re-ask while every row is tentative) still abstains: candidacy only may speak
        self.assertIsNone(out_answer(root, "planted"))
        m.close()


class Determinism(_Lives):
    def test_e_two_runs_byte_identical_to_the_last_digit(self) -> None:
        m1, root1 = self.live(True)
        m2, root2 = self.live(True)
        self.assertEqual(S.journal_bytes(root1), S.journal_bytes(root2), "the journals are byte-identical")
        b1 = (root1 / "state" / "beliefs.jsonl").read_bytes()
        b2 = (root2 / "state" / "beliefs.jsonl").read_bytes()
        self.assertEqual(b1, b2, "the belief stores are byte-identical")
        self.assertGreater(len(b1), 0, "presence: beliefs were filed")
        for sub in ("ask/out", "world/questions"):
            d1, d2 = root1 / sub, root2 / sub
            f1 = sorted(p.name for p in d1.glob("*")) if d1.exists() else []
            f2 = sorted(p.name for p in d2.glob("*")) if d2.exists() else []
            self.assertEqual(f1, f2, sub)
            for name in f1:
                self.assertEqual((d1 / name).read_bytes(), (d2 / name).read_bytes(), f"{sub}/{name}")
        n_muse = len(muse_rows(root1))
        print(f"[muse-gunit e] two runs · journal bytes equal · beliefs bytes equal ({len(b1)} B) · "
              f"muse rows {n_muse} · question files {f1}")
        self.assertGreater(n_muse, 0, "presence: the muse actually ran in this stream")


class Plant(_Lives):
    def test_g_plant_a_doctored_trigger_is_caught_by_the_control_check(self) -> None:
        calls = {"n": 0}
        real = MUSE.trigger

        def doctored(words, web, self_ws, mature):
            calls["n"] += 1
            out = dict(real(words, web, self_ws, mature))
            out.update({"fire": True, "anchors": [str(w) for w in dict.fromkeys(words)], "classes": ["planted"]})
            return out

        with mock.patch.object(MUSE, "trigger", doctored):
            m, root = self.live(True, chat_cids=["control"])
        control_chains = m._muse["chains_started"]
        print(f"[muse-gunit plant] doctored trigger calls {calls['n']} · control chains {control_chains}")
        self.assertGreater(calls["n"], 0, "the plant asserts it ran")
        self.assertGreater(control_chains, 0, "the plant asserts it changed the bytes: "
                                             "the control sentence spawned a chain")
        # ... and the control-sentence check (G-UNIT b's own) CATCHES it:
        with self.assertRaises(AssertionError, msg="the doctored trigger must be caught by the control check"):
            self.assertEqual(m._muse["chains_started"], 0, "control spawns NONE")
        self.assertGreater(len(muse_rows(root)), 0, "the plant's chain rows are on the record")


if __name__ == "__main__":
    unittest.main()
