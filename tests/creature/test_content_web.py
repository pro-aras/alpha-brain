# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 13:5x +0400 — G-UNIT of PREREG-CONTENT-WEB
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010 @ 35ea7e8), the MIND
# half: every consumed row feeds the knowledge webs its OWN tokens behind Mind(..., content_web: bool =
# False) (default OFF = byte-identical; the N1/muse wiring form). Test-first (RED on 35ea7e8:
# creature/contentweb.py and the flag do not exist).
"""tests/creature/test_content_web.py — the law's §2 G-UNIT (a)-(f) + G-PLANT, mind level:

  (a) flag OFF: a scripted MIXED-sense stream (ear/eye/chat/ask/outcome + the tokenless senses
      web/grade) consumes byte-identical to the no-argument construction — journal bytes AND the
      persisted web state (state/web.json) byte-equal, the content census never touched;
  (b) the token forms per sense: a scripted canvas yields EXACTLY its declared s: tokens (per
      hypothesis, the glance's own order, recomputed from the canvas bytes by the law's own path —
      gaze.glances -> things_in_view -> the 0.05 quantization -> blake2b-32 — and deterministic x2),
      a chat row yields w: words, an ask row its w: word, an outcome row its g: token;
  (c) the same content re-seen yields the SAME s: token, a different thing a DIFFERENT one (the
      identity/collision check, presence counts printed);
  (d) OFF vs ON divergence is EXACTLY the new tokens: the ON ear stream is the OFF stream with the
      w: prefix (byte-checkable), the per-sense token census accounts for every ON token, and the ON
      web's nodes are the OFF nodes' w: forms UNION exactly the new-token nodes (s:/g:/door w:);
  (e) the muse-composition row (the law §1): the trigger's self/novel classes are unchanged under
      content tokens — pinned pure (bare web vs w: web vs w: web carrying s:/g: nodes and a SILENT
      cross edge) and end-to-end (an ON+muse mind fires the planted sentence's chain with bare
      anchors/classes exactly as the OFF form does);
  (f) determinism x2 of every web metric: two ON runs, journal + web state byte-equal.

G-PLANT (the law §2): (i) a doctored extractor emitting the EAR tokens twice is CAUGHT by the
accounting of (d); (ii) a one-bin quantizer is caught by (c)'s distinctness check.

The fixture (one shared tape per class): 24 toy moments (ear word + maker canvas, the muse bench's own
TOY_THINGS cycle), then the (c) canvases (the SAME bytes twice + one different thing), three outcome
rows (+, -, none), one canvas-less why ask, one web row and one grade row (NO tokens — the law §1's
named-absent senses), and ONE chat row («you are alpha») published by the chat door's own road.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

import creature.muse as MUSE
from creature.mind import Mind
from creature.senses import chat as chat_sense
from creature.tape import Tape
from genome import web as _web, world
from genome.brain import things_in_view
from genome.machinery import parse_genome
from tests.creature import _scene_tape as S
from tests.creature.test_inner_walk import web_of

ROOT = Path(__file__).resolve().parents[2]
TOY_THINGS = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star"]   # the muse bench's own 8
FIXTURE_SEED = 20261010
N_TOY = 24
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3 nearest; "
              "calibrate at 20 40 60 and before a sitting; replay none; hears toy")
CHAT_TEXT = "you are alpha"
ASK_WORD = "circle"
OUTCOMES = [("step", 1.0), ("step", -0.5), ("run", None)]     # the g: token's sign forms: +, -, none
REPEAT_THING, OTHER_THING = "circle", "square"


def genome_text() -> str:
    """A4L-LANG's own body + the BRAIN line (hears the toy hand) — the muse bench's genome minus its
    SLEEP re-declare (no consolidation pass is needed at unit scale; the web consolidates online)."""
    return (ROOT / "genome" / "ladder" / "A4L-LANG.genome").read_text() + "\n" + BRAIN_LINE + "\n"


def build_fixture(root: Path) -> Dict[str, bytes]:
    """The shared tape; returns {canvas_label: png_bytes} for the (b)/(c) recomputations."""
    tape = Tape(root)
    clock = S._Clock(S.T0)
    canvases: Dict[str, bytes] = {}
    k = 0
    for i in range(N_TOY):
        thing = TOY_THINGS[i % len(TOY_THINGS)]
        moment = f"toy{i:06d}"
        tape.publish("ear", thing.encode(), {"moment": moment, "source": "toy", "word": thing}, "txt", at=clock())
        rgb, _truth = world.render_canvas(thing, np.random.default_rng([FIXTURE_SEED, k]))
        k += 1
        png = S.png(rgb)
        canvases[moment] = png
        tape.publish("eye", png, {"moment": moment, "source": "toy"}, "png", at=clock())
    # (c)'s canvases: the SAME bytes re-shown (rep-a1 == rep-a2), then a different thing
    rgb_a, _ = world.render_canvas(REPEAT_THING, np.random.default_rng([FIXTURE_SEED, 900]))
    rgb_b, _ = world.render_canvas(OTHER_THING, np.random.default_rng([FIXTURE_SEED, 901]))
    png_a, png_b = S.png(rgb_a), S.png(rgb_b)
    for label, png in (("rep-a1", png_a), ("rep-a2", png_a), ("rep-b1", png_b)):
        canvases[label] = png
        tape.publish("eye", png, {"moment": label, "source": "toy"}, "png", at=clock())
    # the outcome rows (the game channel's token forms)
    for j, (act, got) in enumerate(OUTCOMES):
        meta: Dict[str, object] = {"moment": f"oc{j}", "source": "toy", "act": act}
        if got is not None:
            meta["got"] = got
        tape.publish("outcome", b"{}", meta, "json", at=clock())
    # a canvas-less why ask (the ask door's own w: form)
    tape.publish("ask", json.dumps({"form": "why", "item": f"M4:{ASK_WORD}", "mark": "M4", "word": ASK_WORD}).encode(),
                 {"moment": "ask1", "source": "toy", "form": "why"}, "json", at=clock())
    # the named-absent senses (the law §1: NO tokens in v1) — consumed, never heard by the web
    tape.publish("web", json.dumps({"q": "x"}).encode(), {"moment": "web1", "source": "web", "status": "ok"},
                 "json", at=clock())
    tape.publish("grade", json.dumps({"v": 1}).encode(), {"moment": "gr1", "source": "grade", "kind": "exam",
                                                          "right": True}, "json", at=clock())
    # the chat row, published by the door's own road
    (root / "chat" / "in").mkdir(parents=True, exist_ok=True)
    (root / "chat" / "in" / "c01planted.json").write_text(json.dumps({"id": "c01planted", "text": CHAT_TEXT}))
    chat_sense.scan_once(lambda s, p, m, e: tape.publish(s, p, m, e, at=clock()), root, canvas=128, letters=8)
    return canvases


def expected_eye_tokens(genome, png: bytes) -> List[str]:
    """The law's own recomputation of a canvas's declared s: tokens: the payload's sha -> the gaze's
    deterministic glance (predicted never touches fixation selection, gaze.py:209-217) ->
    things_in_view -> the 0.05 quantization -> blake2b-32, in the glance's own order."""
    import creature.contentweb as cw
    from genome import gaze
    rgb = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"), dtype=np.uint8)
    sha = hashlib.sha256(png).hexdigest()
    g = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", sha, colour=genome.colour)
    hyps, _X = things_in_view(g)
    return [cw.sight_token(h.feat) for h in hyps]


def spy_web_hear(store: List[str]):
    """Capture every token the webs hear (the OFF road's single funnel)."""
    real = Mind._web_hear

    def wrapped(self, word):
        store.append(str(word))
        return real(self, word)

    return mock.patch.object(Mind, "_web_hear", wrapped)


def spy_cweb_hear(store: List[Tuple[str, str]]):
    """Capture every content token WITH its sense (the ON road's single funnel — the census's own
    granularity, the accounting's instrument)."""
    real = Mind._cweb_hear

    def wrapped(self, sense, token):
        store.append((str(sense), str(token)))
        return real(self, sense, token)

    return mock.patch.object(Mind, "_cweb_hear", wrapped)


def accounting(off_stream: List[str], on_stream: List[Tuple[str, str]], census: Dict[str, int]) -> None:
    """G-UNIT(d)'s accounting, a standalone instrument so G-PLANT(i) can be thrown against it.
    Raises AssertionError unless: the ON ear tokens are EXACTLY the OFF stream with the w: prefix
    (byte-checkable subsequence), and the per-sense census accounts for every ON token."""
    on_ear = [t for s, t in on_stream if s == "ear"]
    if on_ear != ["w:" + w for w in off_stream]:
        raise AssertionError(f"the ON ear stream is not the OFF stream prefixed: {len(on_ear)} vs {len(off_stream)} "
                             f"tokens, first diff at "
                             f"{next((i for i, (a, b) in enumerate(zip(on_ear, ['w:' + w for w in off_stream])) if a != b), 'length')}")
    if int(census.get("ear", 0)) != len(off_stream):
        raise AssertionError(f"the ear census {census.get('ear')} does not account for the OFF stream's {len(off_stream)}")
    if sum(int(v) for v in census.values()) != len(on_stream):
        raise AssertionError(f"the census total {sum(int(v) for v in census.values())} does not account for "
                             f"the ON stream's {len(on_stream)}")
    per_sense: Dict[str, int] = {}
    for s, _t in on_stream:
        per_sense[s] = per_sense.get(s, 0) + 1
    if {k: int(v) for k, v in census.items() if v} != per_sense:
        raise AssertionError(f"the census {census} disagrees with the stream's own per-sense counts {per_sense}")


def assert_distinct_content(tc: unittest.TestCase, tok_a1: List[str], tok_a2: List[str], tok_b: List[str]) -> None:
    """G-UNIT(c)'s identity/collision check, a standalone instrument so G-PLANT(ii) can be thrown
    against it: the same content re-seen yields the SAME s: tokens; a different thing DIFFERENT ones."""
    tc.assertGreater(len(tok_a1), 0, "presence: the first canvas carried hypotheses")
    tc.assertEqual(tok_a1, tok_a2, "the same content re-seen maps to the SAME s: tokens")
    tc.assertGreater(len(tok_b), 0, "presence: the other canvas carried hypotheses")
    tc.assertTrue(set(tok_a1).isdisjoint(set(tok_b)),
                  f"a different thing must yield DIFFERENT tokens (collision: {set(tok_a1) & set(tok_b)})")


class _Lives(unittest.TestCase):
    """One shared fixture tape per class; every test drives fresh minds over it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="cweb-gunit-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.canvases = build_fixture(cls.tape_root)
        cls.rows = S.rows(cls.tape_root)
        cls.genome = parse_genome(genome_text())
        cls._n = 0

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def live(self, content_web: Optional[bool], muse: bool = False, close: bool = True):
        """A fresh mind over the fixture rows. content_web None = the no-argument construction (the
        old road); True/False the flag's two arms. Returns (mind, root, captured ON/OFF token stream)."""
        type(self)._n += 1
        root = S.link_root(self.tape_root, self.tmp / f"live{type(self)._n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text())
        if content_web is None:
            m = Mind(gp, root, muse=muse)
        else:
            m = Mind(gp, root, muse=muse, content_web=content_web)
        captured: list = []
        spy = spy_cweb_hear(captured) if content_web else spy_web_hear(captured)
        with spy:
            for row in self.rows:
                m.consume(row)
            if close:
                m.close()
        return m, root, captured


class FlagOffByteIdentical(_Lives):
    def test_a_off_consumes_byte_identical_journal_and_web_state(self) -> None:
        m_off, root_off, off_stream = self.live(False)
        m_plain, root_plain, plain_stream = self.live(None)
        self.assertEqual(S.journal_bytes(root_off), S.journal_bytes(root_plain),
                         "flag OFF is byte-identical to the no-argument construction (the journal)")
        web_off = (root_off / "state" / "web.json").read_bytes()
        web_plain = (root_plain / "state" / "web.json").read_bytes()
        self.assertEqual(web_off, web_plain, "flag OFF: the persisted web state is byte-equal")
        self.assertGreater(len(web_off), 0, "presence: the web state exists to be compared")
        self.assertEqual(off_stream, plain_stream, "flag OFF: the webs hear exactly the old ear stream")
        self.assertGreater(len(off_stream), 0, "presence: the stream carried ear words")
        self.assertTrue(all(not t.startswith(("w:", "s:", "g:")) for t in off_stream),
                        "OFF: the node keys stay bare (no prefixes)")
        self.assertEqual({k: int(v) for k, v in m_off._cweb_counts.items() if v}, {},
                         "OFF: the content census was never touched")
        out_a = sorted((root_off / "chat" / "out").glob("*.json"))
        out_b = sorted((root_plain / "chat" / "out").glob("*.json"))
        self.assertEqual([p.name for p in out_a], [p.name for p in out_b])
        for a, b in zip(out_a, out_b):
            self.assertEqual(a.read_bytes(), b.read_bytes(), a.name)
        senses = {}
        for row in self.rows:
            senses[row["sense"]] = senses.get(row["sense"], 0) + 1
        print(f"[cweb-gunit a] rows {len(self.rows)} senses {senses} · journal + web.json byte-equal · "
              f"off tokens {len(off_stream)} · census untouched")


class TokenForms(_Lives):
    def test_b_the_declared_forms_per_sense(self) -> None:
        m, _root, on = self.live(True)
        by_sense: Dict[str, List[str]] = {}
        for s, t in on:
            by_sense.setdefault(s, []).append(t)
        # the eye: every canvas yields EXACTLY the law's recomputed tokens, in the glance's own order
        expected_eye: List[str] = []
        for label, png in self.canvases.items():
            expected_eye.extend(expected_eye_tokens(self.genome, png))
        self.assertEqual(by_sense.get("eye"), expected_eye,
                         "the canvases yield exactly their declared s: tokens (the law's own recomputation)")
        n_s = len(by_sense.get("eye", []))
        self.assertGreater(n_s, 0, "presence: the canvases produced s: tokens")
        self.assertTrue(all(t.startswith("s:") for t in by_sense["eye"]))
        # the ear: the 24 toy words, w:-prefixed, in tape order
        ear_words = [TOY_THINGS[i % len(TOY_THINGS)] for i in range(N_TOY)]
        self.assertEqual(by_sense.get("ear"), ["w:" + w for w in ear_words])
        # the chat door: the consumed sentence's words
        self.assertEqual(by_sense.get("chat"), ["w:you", "w:are", "w:alpha"])
        # the ask door: the why word
        self.assertEqual(by_sense.get("ask"), ["w:" + ASK_WORD])
        # the outcome channel: the declared g: forms (kind + reward sign)
        self.assertEqual(by_sense.get("outcome"), ["g:step:+", "g:step:-", "g:run:none"])
        # the named-absent senses: NEVER tokens (consumed rows, zero contribution)
        self.assertNotIn("web", by_sense)
        self.assertNotIn("grade", by_sense)
        census = {k: int(v) for k, v in m._cweb_counts.items()}
        print(f"[cweb-gunit b] census {census} · s: tokens {n_s} from {len(self.canvases)} canvases · "
              f"chat {by_sense.get('chat')} · outcome {by_sense.get('outcome')}")
        self.assertEqual(census.get("eye"), n_s)

    def test_b_deterministic_twice(self) -> None:
        _m1, _r1, on1 = self.live(True)
        _m2, _r2, on2 = self.live(True)
        self.assertEqual(on1, on2, "the token stream is deterministic x2")
        print(f"[cweb-gunit b] determinism x2: {len(on1)} tokens identical")


class SameContentSameToken(_Lives):
    def test_c_identity_and_collision(self) -> None:
        _m, _root, on = self.live(True)
        eye = [t for s, t in on if s == "eye"]
        tok_a1 = expected_eye_tokens(self.genome, self.canvases["rep-a1"])
        tok_a2 = expected_eye_tokens(self.genome, self.canvases["rep-a2"])
        tok_b = expected_eye_tokens(self.genome, self.canvases["rep-b1"])
        n_distinct = len(set(eye))
        # the fixture's all-pairs collision reading (the law §6's knife-edge, printed either way) — a
        # collision is the SAME token from DIFFERENT bytes (the rep pair's shared token is recurrence,
        # the check's own positive control, not a collision)
        labels = list(self.canvases)
        seen: Dict[str, str] = {}
        collisions = 0
        for label in labels:
            for t in expected_eye_tokens(self.genome, self.canvases[label]):
                if t in seen and seen[t] != label and self.canvases[seen[t]] != self.canvases[label]:
                    collisions += 1
                seen.setdefault(t, label)
        print(f"[cweb-gunit c] eye tokens {len(eye)} · distinct {n_distinct} · rep canvases "
              f"a1 {tok_a1} a2 {tok_a2} b {tok_b} · all-pairs collisions over {len(labels)} canvases: {collisions}")
        assert_distinct_content(self, tok_a1, tok_a2, tok_b)
        # the FED stream carries the same-content pair identically (the fed positions of rep-a1/rep-a2)
        per_canvas: List[List[str]] = []
        for label in labels:
            per_canvas.append(expected_eye_tokens(self.genome, self.canvases[label]))
        flat = [t for toks in per_canvas for t in toks]
        self.assertEqual(eye, flat, "the fed eye stream is the canvases' tokens in tape order")


class AccountingOnOff(_Lives):
    def test_d_divergence_is_exactly_the_new_tokens(self) -> None:
        m_off, root_off, off_stream = self.live(False)
        m_on, root_on, on_stream = self.live(True)
        accounting(off_stream, on_stream, m_on._cweb_counts)
        # the node-level accounting: ON nodes == the OFF nodes' w: forms UNION exactly the new-token nodes
        web_off = json.loads((root_off / "state" / "web.json").read_text())["webs"]["L"]
        web_on = json.loads((root_on / "state" / "web.json").read_text())["webs"]["L"]
        off_nodes = set(web_off["nodes"])
        on_nodes = set(web_on["nodes"])
        ear_w = {"w:" + w for w in off_nodes}
        door_w = {"w:" + t[2:] for s, t in on_stream if s in ("chat", "ask")}
        s_nodes = {t for s, t in on_stream if s == "eye"}
        g_nodes = {t for s, t in on_stream if s == "outcome"}
        expected_on = ear_w | door_w | s_nodes | g_nodes
        self.assertEqual(on_nodes, expected_on,
                         "the ON web's nodes are EXACTLY the w:-prefixed OFF vocabulary + the door w: words "
                         "+ the s:/g: content nodes")
        self.assertTrue(off_nodes, "presence: the OFF web heard words")
        self.assertFalse(any(n.startswith(("s:", "g:")) for n in off_nodes),
                         "OFF reads exactly 0 s:/g: nodes (M-CROSS's unit half)")
        print(f"[cweb-gunit d] OFF nodes {len(off_nodes)} · ON nodes {len(on_nodes)} "
              f"(ear-w {len(ear_w)} · door-w {len(door_w)} · s: {len(s_nodes)} · g: {len(g_nodes)}) · "
              f"census {m_on._cweb_counts} · the prefix stream is the OFF stream, byte-checked")


class MuseComposition(_Lives):
    def test_e_trigger_classes_unchanged_under_content_tokens(self) -> None:
        """The law §1's composition, the pure pin: the same readings on the bare web (OFF's form), the
        w:-prefixed web (ON's vocabulary), and the w: web CARRYING content nodes (s:/g: nodes, their own
        edges, and a SILENT s:<->w: cross edge — an unconsolidated crossing must not move a class)."""
        import creature.contentweb as cw
        vocab = ["big", "circle", "square", "star", "you", "are", "alpha", "zog", "vex"]
        nodes_bare = {w: 5 for w in vocab}
        nodes_bare.update({"alpha": 1, "zog": 2, "vex": 1})
        edges_bare = [("alpha", "star", 9), ("you", "are", 7), ("big", "circle", 6)]
        wb = web_of(nodes_bare, edges_bare, t=100)
        nodes_w = {"w:" + w: n for w, n in nodes_bare.items()}
        edges_w = [("w:" + a, "w:" + b, c) for a, b, c in edges_bare]
        ww = web_of(nodes_w, edges_w, t=100)
        # the content-carrying web: s:/g: nodes + an s:<->s: edge + a SILENT s:<->w: cross edge
        s_tok = cw.sight_token(np.linspace(-0.2, 0.2, 144))
        nodes_wc = dict(nodes_w)
        nodes_wc.update({s_tok: 4, "g:step:+": 3})
        base = ww.to_dict()
        base["nodes"] = {w: {"n": int(n), "first": 1, "last": 100, "source": "lived", "author": "toy"}
                         for w, n in nodes_wc.items()}
        base["order"] = list(nodes_wc)
        base["edges"] = base["edges"] + [
            [*_web._key(s_tok, "s:00000000"), {"c": 5, "occ": 3, "t0": 1, "last": 100, "touch": 100, "miss": [0, 0],
                                               "state": "consolidated", "consolidated_at": 2, "source": "lived",
                                               "author": "toy", "looks": 0}],
            [*_web._key(s_tok, "w:zog"), {"c": 1, "occ": 1, "t0": 90, "last": 99, "touch": 99, "miss": [0, 0],
                                          "state": "silent", "consolidated_at": None, "source": "lived",
                                          "author": "toy", "looks": 0}]]
        base["nodes"]["s:00000000"] = {"n": 2, "first": 1, "last": 100, "source": "lived", "author": "toy"}
        wc = _web.Web.from_dict(base)
        self_node = _web.SelfNode(author="toy")
        self_node.place(_web.Claim("HEAR-1", "you are alpha.", "usually", 0.5,
                                   source="implanted-knowledge", author="toy-parent"))
        self_bare = MUSE.self_words(self_node)
        self_w = {"w:" + w for w in self_bare}
        mature_bare = {"big", "circle", "square", "star"}
        mature_w = {"w:" + w for w in mature_bare}
        cases = {"self": ["you", "are", "alpha"], "novel": ["the", "zog", "is", "here"],
                 "control": ["the", "circle", "is", "big"]}
        reads = {}
        for name, words in cases.items():
            bare = MUSE.trigger(words, wb, self_bare, mature_bare)
            wform = MUSE.trigger(["w:" + w for w in words], ww, self_w, mature_w)
            wcontent = MUSE.trigger(["w:" + w for w in words], wc, self_w, mature_w)
            reads[name] = (bare, wform, wcontent)
            self.assertEqual(wform["classes"], bare["classes"], f"{name}: the w: web reads as the bare web")
            self.assertEqual(wcontent["classes"], bare["classes"], f"{name}: content tokens alter no class")
            self.assertEqual(wcontent["anchors"], ["w:" + a for a in bare["anchors"]],
                             f"{name}: the anchors are the bare anchors' w: forms")
        print(f"[cweb-gunit e] pure pin: "
              f"{ {k: (v[0]['fire'], v[0]['classes'], v[0]['anchors']) for k, v in reads.items()} } "
              f"· identical on bare / w: / w:+content webs (the silent cross edge moved nothing)")
        self.assertEqual(reads["self"][0]["classes"], ["self"])
        self.assertEqual(reads["novel"][0]["classes"], ["novel"])
        self.assertFalse(reads["control"][0]["fire"])

    def test_e_end_to_end_the_muse_reads_the_w_web(self) -> None:
        """The composition at the mind level: an ON+muse mind over the fixture (the planted w: web in
        place before the chat) fires the chain with BARE anchors/classes — the w: mapping lives at the
        trigger's call site, the chain machinery and the doors never see a prefix."""
        import creature.contentweb as cw  # noqa: F401 — the module must exist (RED's own proof)
        # the plant goes in BEFORE the chat is consumed (the fixture's chat is the LAST row)
        type(self)._n += 1
        root2 = S.link_root(self.tape_root, self.tmp / f"live{type(self)._n}" / "r")
        gp = root2.parent / "g.genome"
        gp.write_text(genome_text())
        m2 = Mind(gp, root2, muse=True, content_web=True)
        planted = False
        for row in self.rows:
            if row["sense"] == "chat" and not planted:
                real = m2.webs["L"]
                nodes = {"w:" + w: max(2, int(real.nodes.get("w:" + w, {}).get("n", 0))) for w in TOY_THINGS}
                nodes.update({"w:you": 5, "w:are": 5, "w:alpha": 1})
                edges = [("w:" + TOY_THINGS[i], "w:" + TOY_THINGS[(i + 1) % len(TOY_THINGS)], 3 + i)
                         for i in range(len(TOY_THINGS))] + [("w:alpha", "w:star", 9)]
                m2.webs["L"] = web_of(nodes, edges, t=max(int(real.t), 100))
                m2.self_node.place(_web.Claim("HEAR-1", "you are alpha.", "usually", 0.5,
                                              source="implanted-knowledge", author="toy-parent"))
                planted = True
            m2.consume(row)
        self.assertTrue(planted, "presence: the w: web was planted before the chat")
        m2.close()
        chains = m2._muse["chains"]
        self.assertEqual(m2._muse["chains_started"], 1, "the planted sentence spawns exactly one chain")
        chain = next(iter(chains.values()))
        print(f"[cweb-gunit e2e] chain anchors {chain['anchors']} classes {chain['classes']} "
              f"steps {[s['topic'] for s in chain['steps']]} · heard {chain['heard']}")
        self.assertEqual(chain["classes"], ["self"], "the self class, read off the w: web exactly as before")
        self.assertEqual(chain["anchors"], ["you", "are", "alpha"],
                         "BARE anchors (every self word the planted w: web carries) — the w: mapping never "
                         "reaches the chain")
        self.assertEqual(chain["heard"], ["you", "are", "alpha"])
        self.assertEqual([s["topic"] for s in chain["steps"]][:3], ["you", "are", "alpha"],
                         "the anchor steps, in heard order, bare")
        for q in chain["questions"]:
            self.assertFalse(str(q["word"]).startswith("w:"), "the question door never sees a prefix")


class Determinism(_Lives):
    def test_f_two_on_runs_byte_identical(self) -> None:
        m1, root1, on1 = self.live(True)
        m2, root2, on2 = self.live(True)
        self.assertEqual(S.journal_bytes(root1), S.journal_bytes(root2), "ON: the journals are byte-identical")
        w1 = (root1 / "state" / "web.json").read_bytes()
        w2 = (root2 / "state" / "web.json").read_bytes()
        self.assertEqual(w1, w2, "ON: the persisted web state (every node/edge/stat) is byte-identical")
        self.assertGreater(len(w1), 0, "presence: web state exists")
        self.assertEqual(on1, on2)
        self.assertEqual(m1._cweb_counts, m2._cweb_counts)
        stats = json.loads(w1.decode())["webs"]["L"]["stats"]
        print(f"[cweb-gunit f] two ON runs · journal + web.json byte-equal ({len(w1)} B) · "
              f"web L stats {stats} · census {m1._cweb_counts}")


class Plant(_Lives):
    def test_g_plant_i_the_double_ear_extractor_is_caught_by_the_accounting(self) -> None:
        import creature.contentweb as cw
        _m_off, _root_off, off_stream = self.live(False)
        real = cw.ear_tokens

        def doctored(word):
            return real(word) + real(word)        # the EAR channel's tokens emitted TWICE

        with mock.patch.object(cw, "ear_tokens", doctored):
            m_on, _root_on, on_stream = self.live(True)
        n_ear = sum(1 for s, _t in on_stream if s == "ear")
        print(f"[cweb-gunit plant-i] doctored ear tokens {n_ear} vs the OFF stream's {len(off_stream)} "
              f"(census {m_on._cweb_counts})")
        self.assertEqual(n_ear, 2 * len(off_stream), "the plant asserts it changed the bytes")
        with self.assertRaises(AssertionError, msg="the accounting must catch the double ear feed"):
            accounting(off_stream, on_stream, m_on._cweb_counts)

    def test_g_plant_ii_the_one_bin_quantizer_is_caught_by_distinctness(self) -> None:
        import creature.contentweb as cw
        with mock.patch.object(cw, "QUANT_WIDTH", 1e9):       # everything lands in ONE bin
            tok_a1 = expected_eye_tokens(self.genome, self.canvases["rep-a1"])
            tok_a2 = expected_eye_tokens(self.genome, self.canvases["rep-a2"])
            tok_b = expected_eye_tokens(self.genome, self.canvases["rep-b1"])
        print(f"[cweb-gunit plant-ii] one-bin tokens: a1 {tok_a1} b {tok_b} (identical: {tok_a1 == tok_b})")
        self.assertEqual(tok_a1, tok_b, "the plant asserts it changed the bytes: distinct things collide")
        with self.assertRaises(AssertionError, msg="the distinctness check must catch the one-bin quantizer"):
            assert_distinct_content(self, tok_a1, tok_a2, tok_b)


if __name__ == "__main__":
    unittest.main()
