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
        self.fail("fill at the landing: the think thread's frozen copy carries the coarse moments and their confirmed flags")

    @unittest.skipUnless(_wired("MOUTH") and _worker_obeys(), "C x D not landed")
    def test_CxD_a_say_row_is_an_act_with_an_outcome_and_both_mission_words_reach_the_frame_road(self):
        self.fail("fill at the landing: a say journals an act row and an outcome episode; a game manifest's two ear rows land in words_in_instant")

    @unittest.skipUnless(_wired("ANSWER", "QUESTION"), "A x C not landed")
    def test_AxC_a_questions_what_is_answer_carries_the_grade(self):
        self.fail("fill at the landing: the world door's answer to a what-is question is journaled with the grade (sure/unsure/unknown)")

    @unittest.skipUnless(_worker_obeys() and "lands next boundary" in (TREE / "genome" / "machinery.py").read_text(errors="replace"), "D x E not landed")
    def test_DxE_the_act_is_chosen_on_the_mind_thread_never_the_think_thread(self):
        self.fail("fill at the landing: the act decision row is written by the mind at consume; the think thread writes nothing (the writer sweep's planted offender)")

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
