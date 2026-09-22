# edit: Claude (Fable 5.1), 2026-09-22 18:34 +0400 — THE SEAM TESTS of the ONE life's landings (plan §7; SOLUTIONS #232 add. 2, #235: two builders' modules
# are tested AT THE SEAM by the third hand). Each is a SKELETON that runs only once both sides have landed (skipUnless on the registry or
# on the landed file); the orchestrator fills the body at the landing from the builders' actual names — a skipped seam is a landing not
# yet made, never a pass. (A first draft in an unquoted heredoc lost a backticked word to the shell — #232's lesson — rewritten quoted.)
import unittest
from pathlib import Path

TREE = Path(__file__).resolve().parent.parent.parent


def _wired(*genes):
    from creature import genes as G
    wired = {g for layer in G.RUNS.values() for g, site in layer.items() if site is not None}
    return all(g in wired for g in genes)


def _worker_obeys():
    return "--act-file" in (TREE / "tools" / "game_worker_babyai.py").read_text(errors="replace")


class LifeSeams(unittest.TestCase):
    @unittest.skipUnless(_wired("THRESH", "SURPRISE"), "A x B not landed")
    def test_AxB_a_confirmed_glance_does_not_update_a_cells_own_band(self):
        # filled at A's landing (Claude (Fable 5.1), 2026-09-22 19:51 +0400): a CONFIRMED moment (B's cheap moment) is not an ANSWER (A's band push) —
        # the cell's own band must be untouched by confirmations, or the band fills with the confirmed (high) cosines and the p5 floor
        # drifts up, turning honest answers into hedges. The same moment unconfirmed, with the cell's established answer, DOES push.
        import numpy as np
        from genome.machinery import parse_genome, Organism
        text = (TREE / "genome" / "G5.genome").read_text().replace("NMAX     2000", "NMAX     64").replace("#OFF SURPRISE floor 0.05", "SURPRISE floor 0.05 predicted mind-cell") + "\nTHRESH   cell own band history 30\n"
        g = parse_genome(text); org = Organism(g)
        rng = np.random.default_rng(3); x = rng.standard_normal(g.sight_dim()).astype(np.float32); x /= np.linalg.norm(x)
        w = np.zeros(g.words_dim(), dtype=np.float32); w[0] = 1.0
        org.t = int(g.stage2_start)                      # past STAGE 1 so the wiring runs
        for _ in range(6): org.moment(x, w)              # births + wires: the cell's established answer becomes word 0
        n_before = int(org.sight.own_band_n.sum())
        org.moment(x, w, confirm=True)                   # B's cheap moment on the same glance
        self.assertEqual(int(org.sight.own_band_n.sum()), n_before, "a confirmed glance pushed the cell's own band")
        org.moment(x, w)                                 # the same glance, unconfirmed, answered correctly → one push
        self.assertEqual(int(org.sight.own_band_n.sum()), n_before + 1)

    @unittest.skipUnless(_wired("SURPRISE", "SELF") and "lands next boundary" in (TREE / "genome" / "machinery.py").read_text(errors="replace"), "B x E not landed")
    def test_BxE_the_coarse_row_and_the_confirmed_flag_are_in_the_thinks_frozen_copy(self):
        # filled at E's landing (Claude (Sonnet 5, LIFE builder E), 2026-09-22 21:3x +0400): B's L-4 (SURPRISE/CONFIRM) law is
        # "a CONFIRMED glance is NO think-pool item" (creature/mind.py `_think_pool`'s `if eid in self._confirmed_episodes:
        # continue`), enforced BEFORE a candidate ever reaches `_think_choose`/the frozen copy the think thread receives —
        # so the seam this test proves is that E's threaded road never widens that exclusion: (1) a real tape under
        # SURPRISE+coarse+THINK-threaded produces at least one CONFIRMED episode (the positive control: confirmations really
        # happen on this front) and (2) not one item the LIVE pool offers `_think_choose` — the same pool a "word"/"sight"
        # item bound for the think thread's frozen copy is drawn from — names a confirmed episode id. A regression here
        # would let a confirmed (cheap, expected) glance form a belief/prediction as if it had been a real surprise.
        import io, tempfile
        import numpy as np
        from PIL import Image
        from creature.mind import Mind
        from creature.tape import Tape, read_tape
        from genome import world

        text = (TREE / "genome" / "G5.genome").read_text().replace("NMAX     2000", "NMAX     300")
        text = text.replace("#OFF SURPRISE floor 0.05", "SURPRISE floor 0.9 predicted mind-cell")
        text = text.replace(
            "GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border   # G1 §6 (the proven value; PREREG §1 correction)",
            "GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border coarse 32",
        )
        text = text.replace(
            "BODY     service creature threads eye ear door mind voice",
            "BODY     service creature threads eye ear door mind think voice",
        )
        text = text.replace(
            "THINK    every 10 canvases                        # §11.1 step 3: the pool → CURIOSITY chooses → work → PARK/FILE",
            "THINK    every 10 canvases; on its own thread; lands next boundary",
        )
        root = Path(tempfile.mkdtemp(prefix="seamBE-"))
        gp = root / "g.genome"
        gp.write_text(text)

        def png(rgb):
            b = io.BytesIO(); Image.fromarray(rgb).save(b, format="PNG"); return b.getvalue()

        tape = Tape(root)
        rng = np.random.default_rng(5)
        things = ["circle", "square", "triangle"]
        for i in range(150):
            thing = things[i % len(things)]
            rgb, _truth = world.render_canvas(thing, rng)
            m = f"m{i:05d}"
            # every canvas repeats its OWN thing's word from its own last showing -- a high SURPRISE floor
            # (0.9) still confirms the REPEATS of a thing already met a few times (its expected cell gets close).
            tape.publish("ear", thing.encode(), {"moment": m, "source": "test", "word": thing}, "txt")
            tape.publish("eye", png(rgb), {"moment": m, "source": "test"}, "png")

        mind = Mind(gp, root)
        for r in read_tape(root):
            mind.consume(r)
        mind.close()

        self.assertGreater(len(mind._confirmed_episodes), 0,
                            "fixture produced no confirmed episode -- the positive control never fired, test proves nothing")
        pool = mind._think_pool()
        pool_episode_ids = {it["episode"] for it in pool if it.get("episode") is not None}
        confirmed_in_pool = pool_episode_ids & mind._confirmed_episodes
        self.assertEqual(confirmed_in_pool, set(),
                          "a CONFIRMED episode reached the think pool -- it could be chosen and handed to the think thread's frozen copy")

    @unittest.skipUnless(_wired("MOUTH") and _worker_obeys(), "C x D not landed")
    def test_CxD_a_say_row_is_an_act_with_an_outcome_and_both_mission_words_reach_the_frame_road(self):
        # filled at C's landing (Claude (Fable 5.1), 2026-09-22 20:07 +0400): (1) the mission's two words (C) reach the instant the frame road reads;
        # (2) a SAY (C's mouth) is an ACT with an OUTCOME (D's census and K's reflex ring) — the plan's L-8/L-11 seam: an utterance the
        # creature makes counts among its acts and its being heard is the act's residual. RED on the merged bytes until the seam is built.
        import json, tempfile
        import numpy as np
        from creature.mind import Mind
        from creature.senses.game import mission_words
        self.assertEqual(mission_words("go to the red ball"), ("red", "ball"))
        text = (TREE / "genome" / "G5.genome").read_text().replace("NMAX     2000", "NMAX     64")
        text = text.replace("#OFF SENTENCE two-word frames is near under-judge", "SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token")
        text = text.replace("ACT      glance open ask ", "ACT      glance open ask say ")
        text += "\nMOUTH    say one frame per think; journaled\nQUESTION from wants; forms what-is is which; to the world door\n"
        root = Path(tempfile.mkdtemp(prefix="seamCD-")); gp = root / "g.genome"; gp.write_text(text)
        for d in ("journal", "state", "tape", "ask/out"): (root / d).mkdir(parents=True, exist_ok=True)
        mind = Mind(gp, root)
        mind._frames = {"red|ball": {"w1": "red", "w2": "ball", "episodes": [1, 2]}}
        mind._last_words_in_instant = ["red", "ball"]
        mind._last_glance = np.zeros(mind.genome.sight_dim(), dtype=np.float32)
        row = {"seq": 7, "at": "2026-09-23T00:00:00.000Z", "meta": {"moment": "gseam0000001"}}
        mind._maybe_say(row)
        self.assertEqual(mind.think_counters["said"], 1)
        self.assertEqual(mind.acts_chosen.get("say"), 1, "a say is not counted among the creature's acts")
        ring = mind.outcome_episodes
        self.assertIsNotNone(ring); self.assertGreaterEqual(len(ring), 1)
        self.assertIn("say", set(ring.word.tolist()), "a say wrote no outcome episode")

    @unittest.skipUnless(_wired("ANSWER", "QUESTION"), "A x C not landed")
    def test_AxC_a_questions_what_is_answer_carries_the_grade(self):
        # filled at C's landing (Claude (Fable 5.1), 2026-09-22 20:07 +0400): a question the MIND writes (C's ask/out row) has the shape the ASK door
        # answers (A's graded rendering) — the same JSON the inbox takes, and the rendering of a graded recall names its grade.
        from creature import ask
        from genome.machinery import parse_genome, Organism
        q = {"q": "what-is", "args": ["deadbeef.png"], "from": "mind", "seq": 9, "at": "2026-09-23T00:00:00Z", "why": {}}
        self.assertEqual(ask._args_for(q), ["deadbeef.png"])
        text = (TREE / "genome" / "G5.genome").read_text().replace("NMAX     2000", "NMAX     64") + "\nTHRESH   cell own band history 30\nANSWER   resembles under own-band; unknown below 0.911\n"
        org = Organism(parse_genome(text)); Lw = {0: {"ring"}}
        r = {"cell": 0, "reason": "answer", "lit": 0, "best": 0.5, "second": 0.0, "cos": 0.953, "grade": "unsure", "own_floor": 0.961, "resembles_cell": 0}
        sentence = ask.render_what_is("deadbeef.png", r, org, Lw)
        self.assertIn("resembles ring", sentence)
        r2 = dict(r, grade="sure"); self.assertNotIn("resembles", ask.render_what_is("deadbeef.png", r2, org, Lw))

    @unittest.skipUnless(_worker_obeys() and "lands next boundary" in (TREE / "genome" / "machinery.py").read_text(errors="replace"), "D x E not landed")
    def test_DxE_the_act_is_chosen_on_the_mind_thread_never_the_think_thread(self):
        # filled at E's landing (Claude (Sonnet 5, LIFE builder E), 2026-09-22 21:3x +0400): D's L-8 act
        # choice (`Mind._maybe_choose_act`, writing `run/game/ACT`) is called from `_consume_eye` directly,
        # never from `_maybe_think`/`_maybe_think_threaded`/`creature/think_thread.py` -- it is a MIND-thread
        # act, unconditionally, whether or not THINK itself is threaded. Proved three ways: (1) static --
        # creature/think_thread.py (the ONE module that runs on the think thread) names neither
        # `_maybe_choose_act` nor `game/ACT` anywhere in its source; (2) the writer sweep (item 4's own gate,
        # tools/gate_g4.py's SENSE_FILES, which now includes creature/think_thread.py) already refuses ANY
        # write under a forbidden dir from that file, and `run/game/ACT` -- while not itself one of
        # state/journal/memory -- is written by `Path.write_text`/`os.replace` calls the sweep's own AST walk
        # would catch from ANY of its swept files were they present in creature/think_thread.py, which they
        # are not (the planted-offender control in TestWriterSweepReachesTheThinkModule proves the sweep DOES
        # catch a write call of this exact shape); (3) live -- a genome that drives the game AND threads THINK
        # still gets a `run/game/ACT` write on the FIRST game eye row, before any THINK boundary is even
        # reached (ACT's own cadence is per-eye-row, THINK's is per `every` canvases) -- proving the write
        # path is independent of whether THINK itself is threaded.
        think_thread_src = (TREE / "creature" / "think_thread.py").read_text()
        self.assertNotIn("_maybe_choose_act", think_thread_src)
        self.assertNotIn("game/ACT", think_thread_src)
        self.assertNotIn("game\" / \"ACT\"", think_thread_src)

        import tempfile
        from creature.mind import Mind
        genome_text = (
            "SEED 20260923\n"
            "BODY     service creature threads eye ear door mind think voice\n"
            "TAPE     run/tape\nHEART    every 10 s\nCRASH    sense restart journal; mind page\n"
            "SENSE    eye    32x32 grey\nRETINA   thresh0.25 centre tower:eye-tower-g2 sqrt unit\n"
            "GAZE     surprise fixations 4 grid 16 canvas 128 glance 32 ink border\n"
            "SENSE    ear    letters 8\nAREA     sight  from retina\nAREA     words  from ear\nMEET     sight  words\n"
            "BIRTH    novelty  cos<0.952\nBIRTH    error    misfires 3\nBUDGET   400 per arrival\nNMAX     64\nKWTA     5\n"
            "HEBB     window 1\nDELTA    lr 0.05\nPRUNE    w<0.02 after 3 chances\nMERGE    cos>0.9969 same-answer\n"
            "SCALE    every 1000 moments\nRECALL   k=3\nABSTAIN  second/best > 0.85\nASK      what-is show is which next why\n"
            "STAGE    1 senses   moments 0..0\nSTAGE    2 meet     moments 0..\n"
            "ACT      glance open ask turn step\n"
            "THINK    every 10 canvases; on its own thread; lands next boundary\n"
        )
        root = Path(tempfile.mkdtemp(prefix="seamDE-"))
        gp = root / "g.genome"; gp.write_text(genome_text)
        for d in ("journal", "state", "tape/payload", "game"):
            (root / d).mkdir(parents=True, exist_ok=True)
        mind = Mind(gp, root)
        self.assertTrue(mind._act_policy_on, "fixture's ACT vocabulary (turn+step) must drive the game -- test premise broken")
        row = {"seq": 1, "at": "2026-09-23T00:00:00.000Z",
               "meta": {"moment": "gm0", "source": "game", "n_actions": 3, "act_names": ["left", "right", "forward"], "game": "toy"}}
        mind._maybe_choose_act(row)   # the mind thread's own call -- exactly what _consume_eye makes, before THINK ever runs
        act_path = root / "game" / "ACT"
        self.assertTrue(act_path.exists(), "the mind-thread act choice never wrote run/game/ACT")
        import json
        self.assertEqual(json.loads(act_path.read_text())["seq"], 1)
        mind.close()

    @unittest.skipUnless(_worker_obeys(), "D not landed")
    def test_D_the_workers_act_wait_checks_the_stop_file(self):
        # filled at D's landing (Claude (Fable 5.1), 2026-09-22 19:04 +0400): a worker blocked on ACT must leave within a few polls of the stop
        # file appearing, or `systemctl stop` orphans the venv subprocess (the advisor's finding on the brief's «no timeout»).
        import tempfile, threading, time
        from tools.game_worker_babyai import _wait_for_act, ACT_FILE_POLL_S
        d = Path(tempfile.mkdtemp(prefix="seamD-")); act = d / "ACT"; stop = d / "STOP"
        threading.Timer(0.25, lambda: stop.write_text("stop")).start()
        t0 = time.perf_counter(); got = _wait_for_act(act, 0, stop); dt = time.perf_counter() - t0
        self.assertIsNone(got)
        self.assertLess(dt, 0.25 + 10 * ACT_FILE_POLL_S + 0.5)
        stop.unlink(); act.write_text('{"seq": 7, "act": 2, "at": "now"}')
        self.assertEqual(int(_wait_for_act(act, 0, stop)["seq"]), 7)      # and an act newer than last_seq is returned


if __name__ == "__main__":
    unittest.main()
