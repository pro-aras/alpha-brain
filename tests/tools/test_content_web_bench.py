# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 15:0x +0400 — the CONTENT-WEB bench's own
# tests (PREREG-CONTENT-WEB §2's instrument discipline, the muse bench's test form): the tape build is
# deterministic, DOOR ISOLATION holds at the tape level (the planted names never touch the ear), the
# planted arc's chat rows sit EXACTLY after the named things' canvases, the derangement twins keep the
# slots and the per-sense multisets, the token module's forms are the law's, and one short-scale ON/OFF
# arm pair proves the feed end-to-end (M-CHAT's unit form). The full bench runs as records, never
# inside the unit suite.
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

import creature.contentweb as cw
from tools.brain import content_web_bench as B
from tools.brain.content_web_bench import (CHAT_ARC_N, PLANTED, THING_ROUNDS, TOY_THINGS, arc_after,
                                           build_tape, deranged, drive, genome_text)


class TestGenomeAndToy(unittest.TestCase):
    def test_genome_text_is_deterministic_and_carries_the_bench_lines(self) -> None:
        a, b = genome_text(), genome_text()
        self.assertEqual(a, b)
        self.assertIn("hears toy", a)
        self.assertIn("every 2500 moments", a, "D-sleep: the stock SLEEP line, never re-declared")

    def test_door_isolation_holds_at_the_tape_level(self) -> None:
        """The planted names NEVER arrive on the ear (the law §3's door-isolation form): no ear row
        carries «alpha»/«zeta»; the chat rows carry them, ONE word each, each EXACTLY after the named
        thing's canvas (the cross-channel crossing is forced to be cross-channel)."""
        root = Path(tempfile.mkdtemp())
        try:
            build_tape(root, B._Clock())
            rows = B._rows(root)
            ear_words = [(r.get("meta") or {}).get("word") for r in rows if r["sense"] == "ear"]
            self.assertTrue(ear_words, "presence: the tape carries ear rows")
            for name in PLANTED:
                self.assertNotIn(name, ear_words, f"door isolation: «{name}» never on the ear")
            chats = [r for r in rows if r["sense"] == "chat"]
            self.assertEqual(len(chats), 2 * CHAT_ARC_N, "the planted arc's chat rows, both names")
            for r in chats:
                words = (r.get("meta") or {}).get("words")
                self.assertEqual(len(words), 1, "the law §1's one-word naming")
                name = words[0]
                self.assertIn(name, PLANTED)
            # each chat sits EXACTLY after the named thing's eye row (the arc's window)
            by_seq = {int(r["seq"]): r for r in rows}
            for r in chats:
                name = (r.get("meta") or {}).get("words")[0]
                prev = by_seq[int(r["seq"]) - 1]
                self.assertEqual(prev["sense"], "eye")
                self.assertTrue(str((prev.get("meta") or {}).get("moment", "")).startswith("toy"))
                self.assertEqual(B.thing_of(prev["meta"]["moment"]), PLANTED[name],
                                 f"the «{name}» chat follows a {PLANTED[name]} canvas")
            # the arc's window is the named things' LAST CHAT_ARC_N moments (the sticky tail)
            for name, thing in PLANTED.items():
                n_after = sum(1 for r in chats
                              if (r.get("meta") or {}).get("words") == [name]
                              and int(str(by_seq[int(r["seq"]) - 1]["meta"]["moment"])[3:]) in arc_after(thing))
                self.assertEqual(n_after, CHAT_ARC_N, f"«{name}» is heard on every window moment")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_tape_build_deterministic(self) -> None:
        r1 = Path(tempfile.mkdtemp())
        r2 = Path(tempfile.mkdtemp())
        try:
            build_tape(r1, B._Clock())
            build_tape(r2, B._Clock())
            d1 = sorted((r1 / "tape").glob("*.jsonl"))
            d2 = sorted((r2 / "tape").glob("*.jsonl"))
            self.assertEqual(len(d1), 1)
            self.assertEqual(d1[0].read_bytes(), d2[0].read_bytes(), "the bench tape is byte-identical")
            rows = B._rows(r1)
            senses = {}
            for r in rows:
                senses[r["sense"]] = senses.get(r["sense"], 0) + 1
            self.assertEqual(senses.get("ear"), THING_ROUNDS * len(TOY_THINGS))
            self.assertEqual(senses.get("eye"), THING_ROUNDS * len(TOY_THINGS))
            self.assertEqual(senses.get("outcome"), THING_ROUNDS, "the game channel's rows (D-game)")
        finally:
            shutil.rmtree(r1, ignore_errors=True)
            shutil.rmtree(r2, ignore_errors=True)


class TestTokens(unittest.TestCase):
    def test_the_token_forms_are_the_laws(self) -> None:
        self.assertEqual(cw.word_token("alpha"), "w:alpha")
        self.assertEqual(cw.game_token("step", 1.0), "g:step:+")
        self.assertEqual(cw.game_token("step", -0.5), "g:step:-")
        self.assertEqual(cw.game_token("step", 0.0), "g:step:0")
        self.assertEqual(cw.game_token("run", None), "g:run:none")
        self.assertEqual(cw.ear_tokens("star"), ["w:star"])
        self.assertEqual(cw.words_tokens(["you", "are", "alpha"]), ["w:you", "w:are", "w:alpha"])
        self.assertEqual(cw.TOKEN_SENSES, ("ear", "eye", "chat", "ask", "outcome"),
                         "the armed senses of v1, the law §1's own list")

    def test_the_recognition_token_form(self) -> None:
        """AMENDMENT 1's s: form at the organism level: an EMPTY store emits NO token (the declared
        floor — the first canvas, whose feed reads the store on arrival, is silent); from the SECOND
        read of the same canvas the token is s:c<id> — deterministic across two fresh minds."""
        import re as _re
        from creature.mind import Mind
        from creature.tape import Tape
        from genome import world
        from tests.creature import _scene_tape as S
        rgb, _t = world.render_canvas("circle", np.random.default_rng([B.BENCH_SEED, 0]))
        node_sets = []
        censuses = []
        for _k in range(2):
            tape_root = Path(tempfile.mkdtemp())
            work = Path(tempfile.mkdtemp()) / "r"
            try:
                tape = Tape(tape_root)
                clock = B._Clock()
                for moment in ("m0", "m1"):          # the SAME canvas twice: m0 births, m1 re-reads
                    tape.publish("ear", b"circle", {"moment": moment, "source": "toy", "word": "circle"},
                                 "txt", at=clock())
                    tape.publish("eye", S.png(rgb), {"moment": moment, "source": "toy"}, "png", at=clock())
                work.mkdir(parents=True)
                (work / "tape").symlink_to((tape_root / "tape").resolve(), target_is_directory=True)
                gp = work.parent / "g.genome"
                gp.write_text(genome_text())
                m = Mind(gp, work, content_web=True)
                feat = np.full(int(m.genome.sight_dim()), 1.0 / 12.0)
                self.assertIsNone(cw.sight_token(m.org, feat), "the floor: an empty store yields NO token")
                self.assertEqual(cw.eye_tokens(m.org, [feat]), [])
                for row in B._rows(tape_root):
                    m.consume(row)
                m.close()
                censuses.append(dict(m._cweb_counts))
                node_sets.append(sorted(n for n in (m.webs["L"].nodes if m.webs else {})
                                        if str(n).startswith("s:")))
            finally:
                shutil.rmtree(tape_root, ignore_errors=True)
                shutil.rmtree(work.parent, ignore_errors=True)
        print(f"[cweb-bench-unit tokens] censuses {censuses} · s: nodes {node_sets[0]}")
        self.assertEqual(censuses[0], censuses[1], "deterministic x2")
        self.assertTrue(node_sets[0], "presence: the re-read canvas left s: nodes")
        self.assertTrue(all(_re.fullmatch(r"s:c\d+", n) for n in node_sets[0]),
                        "every s: node is the recognition form s:c<cell id>")
        self.assertEqual(node_sets[0], node_sets[1])


class TestDerangement(unittest.TestCase):
    def test_twins_keep_slots_and_multisets_destroy_order(self) -> None:
        stream = []
        for i in range(40):
            stream.append({"row": 2 * i, "sense": "ear", "token": f"w:t{i % 8}"})
            stream.append({"row": 2 * i + 1, "sense": "eye", "token": f"s:{i:08x}"})
        for k in range(B.TWINS_N):
            twin = deranged(stream, B.BENCH_SEED, k)
            self.assertEqual(len(twin), len(stream))
            self.assertEqual([(e["row"], e["sense"]) for e in twin], [(e["row"], e["sense"]) for e in stream],
                             "the slots (moments and senses) are kept")
            for sense in ("ear", "eye"):
                before = sorted(e["token"] for e in stream if e["sense"] == sense)
                after = sorted(e["token"] for e in twin if e["sense"] == sense)
                self.assertEqual(before, after, f"the {sense} multiset is invariant (marginals kept)")
            self.assertNotEqual([e["token"] for e in twin], [e["token"] for e in stream],
                                "non-identity: the order is destroyed")
        self.assertEqual(deranged(stream, B.BENCH_SEED, 3), deranged(stream, B.BENCH_SEED, 3),
                         "the seeded draws are deterministic")


class TestShortArm(unittest.TestCase):
    def test_a_short_on_off_pair_end_to_end(self) -> None:
        """The feed end-to-end at short scale (4 rounds, the arc's last 2 windows): ON — w:alpha/w:zeta
        ARE nodes, s:/g: nodes present, the census accounts for every token; OFF — no alpha/zeta, zero
        s:/g: nodes (M-CHAT + M-CROSS's OFF half at unit scale)."""
        tape_root = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp())
        try:
            build_tape(tape_root, B._Clock(), rounds=4, arc_n=2)
            on = drive(tape_root, True, work / "on")
            off = drive(tape_root, False, work / "off")
            print(f"[cweb-bench-unit] ON census {on['census']} · nodes {len(on['web_nodes'])} · "
                  f"OFF nodes {len(off['web_nodes'])} · cpu on {on['cpu_s']:.2f}s off {off['cpu_s']:.2f}s")
            self.assertIn("w:alpha", on["web_nodes"])
            self.assertIn("w:zeta", on["web_nodes"])
            self.assertTrue(any(n.startswith("s:") for n in on["web_nodes"]), "presence: s: nodes ON")
            self.assertTrue(any(n.startswith("g:") for n in on["web_nodes"]), "presence: g: nodes ON")
            self.assertGreater(on["census"]["eye"], 0)
            self.assertEqual(on["census"]["chat"], 4, "the arc's one-word chat rows (2 + 2 at short scale)")
            self.assertEqual(sum(on["census"].values()), len(on["stream"]),
                             "the census accounts for every captured token")
            self.assertNotIn("alpha", off["web_nodes"])
            self.assertNotIn("zeta", off["web_nodes"])
            self.assertFalse(any(n.startswith(("s:", "g:")) for n in off["web_nodes"]))
            self.assertEqual(off["web_json_s_nodes"], 0)
            self.assertEqual(off["web_json_g_nodes"], 0)
            self.assertGreater(on["web_json_s_nodes"], 0, "the byte difference exists to be proven")
        finally:
            shutil.rmtree(tape_root, ignore_errors=True)
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
