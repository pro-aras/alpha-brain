# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:0x +0400 — G-UNIT of PREREG-CONTENT-WEB
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27, cweb-1010 @ 35ea7e8), the MIND
# half: every consumed row feeds the knowledge webs its OWN tokens behind Mind(..., content_web: bool =
# False) (default OFF = byte-identical; the N1/muse wiring form). Test-first (RED on 35ea7e8:
# creature/contentweb.py and the flag do not exist).
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:0x +0400 — AMENDMENT 1 (signed, same
# folder, 2026-10-10 15:3x): the s: token re-priced from the failed render-quantization (the verdict
# of record's FAIL-FORM stands, never deleted) to the organism's OWN RECOGNITION: s:c<id> = the nearest
# alive sight cell by raw cosine (genome/think.py's _nearest_sight_cell — reused, never re-implemented).
# G-UNIT(c) re-aimed to the recognition form; G-PLANT gains the third plant (always-cell-0); every
# other row stands. Test-first again: RED on 50863ac (the amendment's own commit — sight_token takes a
# feat alone there; cell_of does not exist).
"""tests/creature/test_content_web.py — the law's §2 G-UNIT (a)-(f) + G-PLANT (three plants), mind level:

  (a) flag OFF: a scripted MIXED-sense stream (ear/eye/chat/ask/outcome + the tokenless senses
      web/grade) consumes byte-identical to the no-argument construction — journal bytes AND the
      persisted web state (state/web.json) byte-equal, the content census never touched;
  (b) the token forms per sense: each eye row yields EXACTLY its declared tokens (one s:c<id> per
      hypothesis of the glance, the glance's own order — recomputed by the law's own path:
      gaze.glances -> things_in_view -> think._nearest_in over a per-row snapshot of the alive sight
      store taken at the feed's own read point — and deterministic x2), the ear w:-prefixed in tape
      order, a chat row yields w: words, an ask row its w: word, an outcome row its g: token;
  (c) AMENDMENT 1's recognition form: a canvas re-read WHILE the sight store is primed maps to the
      SAME s:c<id> (the fixture primes with rep-a1, then re-reads rep-a2/rep-a3 — determinism); the
      arrival-read semantics printed (a novel canvas keys to the nearest OLD cell — the organism's
      recognition ON ARRIVAL, never to its own newborn); two genuinely different things map to
      DIFFERENT cells OR the collision is printed and counted (the organism's resolution is a
      measured fact); the hard global floor (>= 2 distinct tokens across the fixture's genuinely
      different canvases) is the distinctness instrument the plants are thrown against; and the
      DECLARED floor: an empty sight store yields ZERO tokens (pinned at the pure level AND
      end-to-end — the fixture's first eye row emits none);
  (d) OFF vs ON divergence is EXACTLY the new tokens: the ON ear stream is the OFF stream with the
      w: prefix (byte-checkable), the per-sense token census accounts for every ON token, and the ON
      web's nodes are the OFF nodes' w: forms UNION exactly the new-token nodes (s:c*/g:/door w:);
  (e) the muse-composition row (the law §1): the trigger's self/novel classes unchanged under content
      tokens — pinned pure (bare web vs w: web vs w: web carrying s:c*/g: nodes and a SILENT cross
      edge) and end-to-end (an ON+muse mind fires the chain with bare anchors/classes);
  (f) determinism x2 of every web metric: two ON runs, journal + web state byte-equal.

G-PLANT: (i) a doctored extractor emitting the EAR tokens twice is CAUGHT by the accounting of (d);
(ii) the one-bin form re-priced (a doctored cell read collapsing every canvas to ONE alive cell) is
caught by (c)'s distinctness floor; (iii) the amendment's named plant — a doctored extractor that
always returns cell 0 — is caught by (c)'s distinctness floor AND by the declared empty-store floor
(it emits s:c0 where no token may exist).

The fixture (one shared tape per class): 24 toy moments (ear word + maker canvas, the muse bench's own
TOY_THINGS cycle), then the (c) canvases (the SAME bytes three times + one different thing), three
outcome rows (+, -, none), one canvas-less why ask, one web row and one grade row (NO tokens — the
law §1's named-absent senses), and ONE chat row («you are alpha») by the chat door's own road.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
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
from genome.think import _nearest_in              # the hoisted twin of _nearest_sight_cell (bit-identical, pinned by tests/genome/test_induce_hoist.py)
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
REP_LABELS = ("rep-a1", "rep-a2", "rep-a3", "rep-b1")         # the SAME bytes x3, then a different thing


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
    # (c)'s canvases: the SAME bytes re-shown twice (rep-a1 primes the store; rep-a2/rep-a3 re-read it),
    # then a different thing
    rgb_a, _ = world.render_canvas(REPEAT_THING, np.random.default_rng([FIXTURE_SEED, 900]))
    rgb_b, _ = world.render_canvas(OTHER_THING, np.random.default_rng([FIXTURE_SEED, 901]))
    png_a, png_b = S.png(rgb_a), S.png(rgb_b)
    for label, png in (("rep-a1", png_a), ("rep-a2", png_a), ("rep-a3", png_a), ("rep-b1", png_b)):
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


def glance_feats(genome, png: bytes) -> list:
    """The law's own path to a canvas's hypothesis feature rows: the payload's sha -> the gaze's
    deterministic glance (predicted never touches fixation selection, gaze.py:209-217) ->
    things_in_view, in the glance's own order."""
    from genome import gaze
    rgb = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"), dtype=np.uint8)
    sha = hashlib.sha256(png).hexdigest()
    g = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", sha, colour=genome.colour)
    hyps, _X = things_in_view(g)
    return [h.feat for h in hyps]


def expected_eye_tokens(store: Dict[str, object], feats: list) -> List[str]:
    """AMENDMENT 1's recomputation of an eye row's declared tokens: ONE s:c<id> per hypothesis — the
    nearest alive sight cell by raw cosine (think._nearest_in over the store snapshot taken at the
    feed's own read point, BEFORE the row's own learning road) — and the DECLARED floor: an empty
    store yields ZERO tokens (never an invented key)."""
    ids, M = store["ids"], store["cells"]
    out = []
    for f in feats:
        cid = _nearest_in(ids, M, f)
        if cid is not None:
            out.append("s:c" + str(cid))
    return out


def spy_web_hear(store: List[str]):
    """Capture every token the webs hear (the OFF road's single funnel)."""
    real = Mind._web_hear

    def wrapped(self, word):
        store.append(str(word))
        return real(self, word)

    return mock.patch.object(Mind, "_web_hear", wrapped)


def spy_cweb_hear(store: List[Tuple[int, str, str]], cur: Dict[str, int]):
    """Capture every content token WITH its row seq and sense (the ON road's single funnel — the
    census's own granularity, the accounting's instrument; the seq attributes the declared floor)."""
    real = Mind._cweb_hear

    def wrapped(self, sense, token):
        store.append((int(cur["seq"]), str(sense), str(token)))
        return real(self, sense, token)

    return mock.patch.object(Mind, "_cweb_hear", wrapped)


def accounting(off_stream: List[str], on_stream: List[Tuple[int, str, str]], census: Dict[str, int]) -> None:
    """G-UNIT(d)'s accounting, a standalone instrument so G-PLANT(i) can be thrown against it.
    Raises AssertionError unless: the ON ear tokens are EXACTLY the OFF stream with the w: prefix
    (byte-checkable subsequence), and the per-sense census accounts for every ON token."""
    on_ear = [t for _q, s, t in on_stream if s == "ear"]
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
    for _q, s, _t in on_stream:
        per_sense[s] = per_sense.get(s, 0) + 1
    if {k: int(v) for k, v in census.items() if v} != per_sense:
        raise AssertionError(f"the census {census} disagrees with the stream's own per-sense counts {per_sense}")


def recognition_check(tc: unittest.TestCase, reread_a: List[str], reread_b: List[str],
                      other: List[str], all_eye_tokens: List[str]) -> Dict[str, object]:
    """G-UNIT(c)'s AMENDMENT-1 form, a standalone instrument so the plants can be thrown against it:
    the re-reads of one canvas under a primed store map to the SAME s:c<id> (hard); a genuinely
    different thing maps to DIFFERENT cells OR the collision is printed and counted (the organism's
    resolution, measured never assumed); and the hard global floor — >= 2 distinct tokens across
    genuinely different canvases — the degenerate-extractor catch."""
    tc.assertEqual(reread_a, reread_b, "a canvas re-read while the store is primed maps to the SAME s:c<id>")
    collision = sorted(set(reread_a) & set(other))
    distinct = sorted(set(all_eye_tokens))
    tc.assertGreater(len(distinct), 1, "the organism resolves the fixture's canvases into >= 2 cells "
                                       "(the degenerate-extractor floor — the plants' catch)")
    return {"collision": collision, "distinct": distinct}


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
        old road); True/False the flag's two arms. Returns (mind, root, captured token stream, trace).
        The trace: BEFORE each eye row's consume, a snapshot of the alive sight store (ids + cells) —
        exactly the store the feed reads (the organism road that can birth comes later in the row;
        ear/chat/outcome rows never touch sight cells). Read-only: never a byte of the mind's road."""
        type(self)._n += 1
        root = S.link_root(self.tape_root, self.tmp / f"live{type(self)._n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text())
        if content_web is None:
            m = Mind(gp, root, muse=muse)
        else:
            m = Mind(gp, root, muse=muse, content_web=content_web)
        captured: list = []
        cur: Dict[str, int] = {"seq": 0}
        trace: list = []
        spy = spy_cweb_hear(captured, cur) if content_web else spy_web_hear(captured)
        with spy:
            for row in self.rows:
                cur["seq"] = int(row["seq"])
                if row["sense"] == "eye":
                    ids = m.org.sight.alive_ids()
                    trace.append({"seq": int(row["seq"]),
                                  "moment": str((row.get("meta") or {}).get("moment")),
                                  "ids": ids.copy(),
                                  "cells": (m.org.sight.cells[ids].copy() if len(ids)
                                            else np.zeros((0, self.genome.sight_dim())))})
                m.consume(row)
            if close:
                m.close()
        return m, root, captured, trace


class FlagOffByteIdentical(_Lives):
    def test_a_off_consumes_byte_identical_journal_and_web_state(self) -> None:
        m_off, root_off, off_stream, _tr = self.live(False)
        m_plain, root_plain, plain_stream, _tr2 = self.live(None)
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
        m, _root, on, trace = self.live(True)
        by_sense: Dict[str, List[str]] = {}
        for _q, s, t in on:
            by_sense.setdefault(s, []).append(t)
        # the eye: every row yields EXACTLY the law's recomputed tokens against the store it was fed
        # from (the trace's pre-row snapshot = the feed's own read point), in the glance's own order
        expected_eye: List[str] = []
        for tr in trace:
            expected_eye.extend(expected_eye_tokens(tr, glance_feats(self.genome, self.canvases[tr["moment"]])))
        self.assertEqual(by_sense.get("eye"), expected_eye,
                         "the eye rows yield exactly their declared s:c<id> tokens (the law's own "
                         "recomputation against the traced store)")
        n_s = len(by_sense.get("eye", []))
        self.assertGreater(n_s, 0, "presence: the canvases produced s: tokens (the store primes itself)")
        self.assertTrue(all(re.fullmatch(r"s:c\d+", t) for t in by_sense["eye"]),
                        "every s: token is the recognition form s:c<cell id>")
        # the DECLARED floor, end-to-end: the fixture's FIRST eye row saw an empty store -> zero tokens
        first_eye_seq = int(next(r["seq"] for r in self.rows if r["sense"] == "eye"))
        self.assertFalse(any(s == "eye" and q == first_eye_seq for q, s, _t in on),
                         "the declared floor: the empty store emits zero s: tokens (the first eye row)")
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
        print(f"[cweb-gunit b] census {census} · s: tokens {n_s} from {len(trace)} eye rows (the first "
              f"row silent — the floor) · chat {by_sense.get('chat')} · outcome {by_sense.get('outcome')}")
        self.assertEqual(census.get("eye"), n_s)

    def test_b_deterministic_twice(self) -> None:
        _m1, _r1, on1, _t1 = self.live(True)
        _m2, _r2, on2, _t2 = self.live(True)
        self.assertEqual(on1, on2, "the token stream is deterministic x2")
        print(f"[cweb-gunit b] determinism x2: {len(on1)} tokens identical")


class RecognitionForm(_Lives):
    def test_c_the_recognition_form(self) -> None:
        _m, _root, on, trace = self.live(True)
        eye = [t for _q, s, t in on if s == "eye"]
        tr = {t_["moment"]: t_ for t_ in trace}
        toks = {label: [t for q, s, t in on if s == "eye" and q == int(tr[label]["seq"])]
                for label in REP_LABELS}
        # the arrival-read semantics, printed (never hidden): rep-a1's read is the nearest OLD cell
        # (the store as it stood ON ARRIVAL); a1's own road may then birth — the re-reads rep-a2/rep-a3
        # read the store primed BY a1 and must agree
        print(f"[cweb-gunit c] arrival vs re-read: a1 {toks['rep-a1']} · a2 {toks['rep-a2']} · "
              f"a3 {toks['rep-a3']} · b {toks['rep-b1']}")
        read = recognition_check(self, toks["rep-a2"], toks["rep-a3"], toks["rep-b1"], eye)
        print(f"[cweb-gunit c] collision a-vs-b: {read['collision']} · distinct tokens across "
              f"{len(trace)} canvases: {len(read['distinct'])} (the organism's resolution, measured)")
        # the fixture's re-read pairs are sane: a2/a3 carry exactly one token (one hypothesis)
        self.assertEqual(len(toks["rep-a2"]), 1)
        self.assertEqual(len(toks["rep-b1"]), 1, "presence: the other canvas carried a hypothesis")
        # the floor at the pure level too: a fresh mind's empty store yields NO token
        type(self)._n += 1
        root0 = S.link_root(self.tape_root, self.tmp / f"live{type(self)._n}" / "r")
        gp0 = root0.parent / "g.genome"
        gp0.write_text(genome_text())
        m0 = Mind(gp0, root0)          # never consumes: the sight store is empty
        import creature.contentweb as cw
        feat = np.full(self.genome.sight_dim(), 1.0 / 12.0)
        self.assertIsNone(cw.sight_token(m0.org, feat), "the declared floor: an empty store yields NO token")
        self.assertEqual(cw.eye_tokens(m0.org, [feat, feat]), [], "zero tokens, never an invented key")
        self.assertIsNone(cw.cell_of(m0.org, feat), "the extractor's own floor (think's form: None)")

    def test_c_arrival_read_is_the_recognition_on_arrival(self) -> None:
        """The amendment's semantics, pinned: a NOVEL canvas keys to the nearest OLD cell (what the
        organism recognized it as on arrival) — never to the cell its own road may then birth. The
        fixture's re-read triplet shows it: after rep-a1's read, rep-a2/rep-a3 agree (the primed
        re-read), and rep-a1's own token is printed beside them (it may differ by the birth — the
        mechanism's honest arrival form, not a churn)."""
        _m, _root, on, trace = self.live(True)
        tr = {t_["moment"]: t_ for t_ in trace}
        a1 = expected_eye_tokens(tr["rep-a1"], glance_feats(self.genome, self.canvases["rep-a1"]))
        a2 = expected_eye_tokens(tr["rep-a2"], glance_feats(self.genome, self.canvases["rep-a2"]))
        a3 = expected_eye_tokens(tr["rep-a3"], glance_feats(self.genome, self.canvases["rep-a3"]))
        store_grew = len(tr["rep-a2"]["ids"]) > len(tr["rep-a1"]["ids"])
        print(f"[cweb-gunit c2] a1 {a1} (store {len(tr['rep-a1']['ids'])}) -> a2 {a2} "
              f"(store {len(tr['rep-a2']['ids'])}, grew {store_grew}) -> a3 {a3} · a1==a2 {a1 == a2}")
        self.assertEqual(a2, a3, "the re-reads under the primed store agree (the recognition form)")
        self.assertEqual(len(a2), 1, "one hypothesis on the rep canvas — the token is the read of it")


class AccountingOnOff(_Lives):
    def test_d_divergence_is_exactly_the_new_tokens(self) -> None:
        m_off, root_off, off_stream, _tr = self.live(False)
        m_on, root_on, on_stream, _tr2 = self.live(True)
        accounting(off_stream, on_stream, m_on._cweb_counts)
        # the node-level accounting: ON nodes == the OFF nodes' w: forms UNION exactly the new-token nodes
        web_off = json.loads((root_off / "state" / "web.json").read_text())["webs"]["L"]
        web_on = json.loads((root_on / "state" / "web.json").read_text())["webs"]["L"]
        off_nodes = set(web_off["nodes"])
        on_nodes = set(web_on["nodes"])
        ear_w = {"w:" + w for w in off_nodes}
        door_w = {"w:" + t[2:] for _q, s, t in on_stream if s in ("chat", "ask")}
        s_nodes = {t for _q, s, t in on_stream if s == "eye"}
        g_nodes = {t for _q, s, t in on_stream if s == "outcome"}
        expected_on = ear_w | door_w | s_nodes | g_nodes
        self.assertEqual(on_nodes, expected_on,
                         "the ON web's nodes are EXACTLY the w:-prefixed OFF vocabulary + the door w: words "
                         "+ the s:c*/g: content nodes")
        self.assertTrue(off_nodes, "presence: the OFF web heard words")
        self.assertFalse(any(n.startswith(("s:", "g:")) for n in off_nodes),
                         "OFF reads exactly 0 s:/g: nodes (M-CROSS's unit half)")
        print(f"[cweb-gunit d] OFF nodes {len(off_nodes)} · ON nodes {len(on_nodes)} "
              f"(ear-w {len(ear_w)} · door-w {len(door_w)} · s: {len(s_nodes)} · g: {len(g_nodes)}) · "
              f"census {m_on._cweb_counts} · the prefix stream is the OFF stream, byte-checked")


class MuseComposition(_Lives):
    def test_e_trigger_classes_unchanged_under_content_tokens(self) -> None:
        """The law §1's composition, the pure pin: the same readings on the bare web (OFF's form), the
        w:-prefixed web (ON's vocabulary), and the w: web CARRYING content nodes (s:c*/g: nodes, their
        own edges, and a SILENT s:c<->w: cross edge — an unconsolidated crossing must not move a class)."""
        vocab = ["big", "circle", "square", "star", "you", "are", "alpha", "zog", "vex"]
        nodes_bare = {w: 5 for w in vocab}
        nodes_bare.update({"alpha": 1, "zog": 2, "vex": 1})
        edges_bare = [("alpha", "star", 9), ("you", "are", 7), ("big", "circle", 6)]
        wb = web_of(nodes_bare, edges_bare, t=100)
        nodes_w = {"w:" + w: n for w, n in nodes_bare.items()}
        edges_w = [("w:" + a, "w:" + b, c) for a, b, c in edges_bare]
        ww = web_of(nodes_w, edges_w, t=100)
        # the content-carrying web: s:c*/g: nodes + an s:<->s: edge + a SILENT s:<->w: cross edge
        s_tok = "s:c7"
        nodes_wc = dict(nodes_w)
        nodes_wc.update({s_tok: 4, "g:step:+": 3})
        base = ww.to_dict()
        base["nodes"] = {w: {"n": int(n), "first": 1, "last": 100, "source": "lived", "author": "toy"}
                         for w, n in nodes_wc.items()}
        base["order"] = list(nodes_wc)
        base["edges"] = base["edges"] + [
            [*_web._key(s_tok, "s:c9"), {"c": 5, "occ": 3, "t0": 1, "last": 100, "touch": 100, "miss": [0, 0],
                                         "state": "consolidated", "consolidated_at": 2, "source": "lived",
                                         "author": "toy", "looks": 0}],
            [*_web._key(s_tok, "w:zog"), {"c": 1, "occ": 1, "t0": 90, "last": 99, "touch": 99, "miss": [0, 0],
                                          "state": "silent", "consolidated_at": None, "source": "lived",
                                          "author": "toy", "looks": 0}]]
        base["nodes"]["s:c9"] = {"n": 2, "first": 1, "last": 100, "source": "lived", "author": "toy"}
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
        m1, root1, on1, _t1 = self.live(True)
        m2, root2, on2, _t2 = self.live(True)
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
        _m_off, _root_off, off_stream, _tr = self.live(False)
        real = cw.ear_tokens

        def doctored(word):
            return real(word) + real(word)        # the EAR channel's tokens emitted TWICE

        with mock.patch.object(cw, "ear_tokens", doctored):
            m_on, _root_on, on_stream, _tr2 = self.live(True)
        n_ear = sum(1 for _q, s, _t in on_stream if s == "ear")
        print(f"[cweb-gunit plant-i] doctored ear tokens {n_ear} vs the OFF stream's {len(off_stream)} "
              f"(census {m_on._cweb_counts})")
        self.assertEqual(n_ear, 2 * len(off_stream), "the plant asserts it changed the bytes")
        with self.assertRaises(AssertionError, msg="the accounting must catch the double ear feed"):
            accounting(off_stream, on_stream, m_on._cweb_counts)

    def test_g_plant_ii_the_one_bin_collapse_is_caught_by_distinctness(self) -> None:
        """The one-bin quantizer's re-priced form (the quantizer itself died with the failed token):
        a doctored cell read that collapses EVERY canvas onto ONE alive cell — the distinctness
        floor of (c) must catch it."""
        import creature.contentweb as cw

        def doctored(org, feats):                      # every canvas -> the same FIRST alive cell
            ids = org.sight.alive_ids()
            return [] if len(ids) == 0 else ["s:c%d" % int(ids[0])] * len(feats)
            # edit: Kimi Code (K3, kimi-code, the seat), 2026-10-10 18:5x +0400 — the M-COST hoist moved
            # the doctoring seam to the ROW extractor (the law's own word: «a doctored extractor»);
            # cell_of is bypassed by the hoisted path, so the plant patches eye_tokens itself.

        with mock.patch.object(cw, "eye_tokens", doctored):
            _m, _root, on, trace = self.live(True)
        tr = {t_["moment"]: t_ for t_ in trace}
        eye = [t for _q, s, t in on if s == "eye"]
        a2 = [t for q, s, t in on if s == "eye" and q == int(tr["rep-a2"]["seq"])]
        a3 = [t for q, s, t in on if s == "eye" and q == int(tr["rep-a3"]["seq"])]
        b = [t for q, s, t in on if s == "eye" and q == int(tr["rep-b1"]["seq"])]
        print(f"[cweb-gunit plant-ii] collapsed eye stream: distinct {sorted(set(eye))} "
              f"(a2 {a2}, b {b})")
        self.assertEqual(len(set(eye)), 1, "the plant asserts it changed the bytes: one bin for all")
        with self.assertRaises(AssertionError, msg="the distinctness floor must catch the one-bin collapse"):
            recognition_check(self, a2, a3, b, eye)

    def test_g_plant_iii_always_cell_0_is_caught(self) -> None:
        """AMENDMENT 1's named third plant: the extractor always returns cell 0. Caught TWICE: by the
        distinctness floor (one token for every canvas) AND by the declared empty-store floor (the
        first eye row emits s:c0 where NO token may exist)."""
        import creature.contentweb as cw

        with mock.patch.object(cw, "eye_tokens", lambda org, feats: ["s:c0"] * len(feats)):
            # edit: Kimi Code (K3, kimi-code, the seat), 2026-10-10 18:5x +0400 — the seam is the ROW
            # extractor (the M-COST hoist bypasses cell_of); the plant always emits cell 0 per
            # hypothesis, the two catches stand unchanged.
            _m, _root, on, trace = self.live(True)
        eye = [t for _q, s, t in on if s == "eye"]
        self.assertTrue(eye, "the plant asserts it ran (tokens were emitted)")
        self.assertEqual(set(eye), {"s:c0"}, "the plant asserts it changed the bytes: always cell 0")
        # catch 1: the distinctness floor
        tr = {t_["moment"]: t_ for t_ in trace}
        a2 = [t for q, s, t in on if s == "eye" and q == int(tr["rep-a2"]["seq"])]
        a3 = [t for q, s, t in on if s == "eye" and q == int(tr["rep-a3"]["seq"])]
        b = [t for q, s, t in on if s == "eye" and q == int(tr["rep-b1"]["seq"])]
        with self.assertRaises(AssertionError, msg="distinctness must catch always-cell-0"):
            recognition_check(self, a2, a3, b, eye)
        # catch 2: the DECLARED floor — the fixture's first eye row saw an empty store, yet a token exists
        first_eye_seq = int(next(r["seq"] for r in self.rows if r["sense"] == "eye"))
        floor_violated = any(s == "eye" and q == first_eye_seq for q, s, _t in on)
        print(f"[cweb-gunit plant-iii] always-cell-0 · floor violated at seq {first_eye_seq}: {floor_violated}")
        self.assertTrue(floor_violated, "the plant emits s:c0 where the honest floor emits nothing — "
                                        "the floor check of (b) catches it")


if __name__ == "__main__":
    unittest.main()
