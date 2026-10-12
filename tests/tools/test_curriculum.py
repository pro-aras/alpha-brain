# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 09:28 +0400 — PREREG-OPEN-WORLD-4 §2 build (the law
# signed at d7213d4; its sha256 dd605480…88ad5 carried by records/open-world-4/SEAT-LINE.txt). Tests FIRST, RED
# before tools/worlds/curriculum.py exists.
"""tests/tools/test_curriculum.py — the gates and planted truths of PREREG-OPEN-WORLD-4 (V3: the curriculum +
the co-reference channel) on tools/worlds/curriculum.py.

Fixtures, every truth known by construction, no network anywhere:
(i) hand-written SRTs and hand-built tapes (creature/tape.py's OWN writer) pin the caption stats, the sizing
    walk's three stop reasons, the gradient's declared order (type-token ratio ASC, words-per-second ASC, the
    shelf's own index last), and V1's concat form mirrored exactly (seq renumbered 1..N, payload files renamed
    to the new seq, meta.series — V1's own concat key — plus the law's ONE additive meta key `video`; `source`,
    `at`, meta.t, meta.moment untouched), byte-identical on regeneration;
(ii) the co-reference instrument's unit plants: a hand-made t_mass stream with a known median/MAD threshold, a
    two-video hand-built tape with DELIBERATE moment collisions across the videos (V1's concat form carries
    them) proving the token→canvas mapping is collision-free, the ±1-canvas edges (the law's named 1 Hz
    resolution limit), the same-video rule, and the shuffled-onset control deterministic at the law's own seed
    20261777;
(iii) G-PLANT (the law §3): a synthetic clip — PIL frames (a bright square on grey, jumping position for
    exactly the declared burst frames) packaged by ffmpeg, plus a planted SRT whose planted word's onset lands
    exactly on the burst — run through the SAME converter (video_door.convert, unchanged) and a REAL wired
    replay (the bench genome + vfront wired), the t_mass read off the journal: the burst frames are the motion
    events, the planted word IS marked synchronized, a non-burst word is NOT, and with the onsets shuffled at
    the law's seed the planted word is NOT synchronized (the instrument CAN fail). The fixture's geometry is
    DECLARED (the burst at frames 4–6 + the return edge at 7; the law's own seed's shuffled draw for this
    4-token/30-canvas fixture is [1, 25, 13, 13] — printed, never hidden: the planted word's shuffled onset
    lands at canvas 25, nowhere near the burst — the control distinguishes);
(iv) the tree gates as executable pins: the instruments of record's sha256 (G-FRONT: vfront.py; the cutter and
    the converter likewise) and the bench genome's (G-HEARS), never edited under this law.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.worlds import event_cutter as EC
from tools.worlds import video_door as VD
from tools.worlds import curriculum as CU

ROOT = Path(__file__).resolve().parents[2]
BENCH2 = ROOT / "docs" / "organism" / "whole" / "records" / "open-world-2" / "bench"
DATE = "2026-10-08"          # the curriculum date (the build's own day, from `date`), pinned in the fixtures

# the instruments of record, sha-pinned by the law (G-FRONT / G-HEARS) — never edited under this law
SHA_VFRONT = "e38676e5e88abefbed1eaabfd9439979679a0fed280da2425b300a8be958739d"   # == its bytes at h0-1012's wiring — PREREG-HOMEOSTASIS §2.3 (SIGNED; SEAT-LINE-H0.txt edda32e7…): the extra_fixations parameter (default 0, byte-identical behavior) — the pin moved under the law, never loosened (was: its bytes at 0f92281)
SHA_CUTTER = "d0bc0b6f7933a3a8746bada73a0e67d9f57d5a8d434dbf2cbc90b215f64b084b"
SHA_DOOR = "ebcd70c42c4dcad69e2e8f3fea782c10ba5a5554e1e7dff5d088c849f457d821"
SHA_GENOME = "0d064f864d9c4158e1d6b8d92e750501db153c23a6340b7abafb0e86d4560d54"

SRT_STATS = """1
00:00:01,000 --> 00:00:02,000
Red red apple

2
00:00:03,000 --> 00:00:04,500
Red apple 1!

3
00:00:08,000 --> 00:00:09,000
Bye
"""
# the fixture's own truth: kept tokens [red, red, apple, red, apple, bye] ("1" dropped AND counted);
# unique {red, apple, bye} = 3; ttr = 3/6; span = last cue end = 9.0; wps = 6/9


class CaptionStats(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="curriculum-stats-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.srt = self.tmp / "a.en.srt"
        self.srt.write_text(SRT_STATS)

    def test_stats_known_by_construction(self) -> None:
        s = CU.caption_stats(self.srt)
        self.assertEqual(s["tokens"], ["red", "red", "apple", "red", "apple", "bye"])
        self.assertEqual((s["n_tokens"], s["n_unique"]), (6, 3))
        self.assertAlmostEqual(s["ttr"], 3 / 6)                 # repetition is the simpler speech
        self.assertAlmostEqual(s["span_s"], 9.0)                # the caption stream's own span (captions alone)
        self.assertAlmostEqual(s["wps"], 6 / 9.0)
        self.assertEqual(s["dropped_nonword"], 1)               # the "1" token: dropped AND counted, never silent


class Gradient(unittest.TestCase):
    def test_type_token_ratio_ascending_then_slower_first(self) -> None:
        entries = [dict(name="c", ttr=0.40, wps=1.5, shelf_index=2),
                   dict(name="a", ttr=0.20, wps=1.5, shelf_index=0),
                   dict(name="b", ttr=0.40, wps=1.0, shelf_index=1),     # ttr tie with c, SLOWER first
                   dict(name="d", ttr=0.40, wps=1.0, shelf_index=3)]     # double tie: the shelf's own index decides
        self.assertEqual([e["name"] for e in CU.gradient_order(entries)], ["a", "b", "d", "c"])

    def test_never_hand_ranked_total_order_is_mechanical(self) -> None:
        entries = [dict(name=f"v{i}", ttr=0.5, wps=1.0, shelf_index=i) for i in range(5)]
        self.assertEqual([e["name"] for e in CU.gradient_order(list(reversed(entries)))],
                         [f"v{i}" for i in range(5)])                    # input order never decides; the shelf index does


class SizingWalk(unittest.TestCase):
    def test_sized_stop_at_the_target(self) -> None:
        cands = [dict(name=f"v{i}", worded=200, media_s=300.0, shelf_index=i) for i in range(5)]
        w = CU.sizing_walk(cands)
        self.assertEqual([c["name"] for c in w["taken"]], ["v0", "v1", "v2"])   # 200+200+200 = 600 ≥ 500, stop
        self.assertEqual((w["worded"], w["media_s"], w["stop"]), (600, 900.0, "sized"))
        self.assertTrue(w["sized"])

    def test_the_videos_cap_is_a_wall(self) -> None:
        cands = [dict(name=f"v{i}", worded=10, media_s=60.0, shelf_index=i) for i in range(40)]
        w = CU.sizing_walk(cands)
        self.assertEqual((len(w["taken"]), w["worded"], w["stop"]), (30, 300, "cap-videos"))
        self.assertFalse(w["sized"])                                       # the cap could not reach 500: FAIL-SIZE's row

    def test_the_media_cap_is_a_wall_the_next_video_never_skipped_to(self) -> None:
        cands = [dict(name="big", worded=100, media_s=4500.0, shelf_index=0),
                 dict(name="small", worded=490, media_s=60.0, shelf_index=1)]   # reachable only by skipping — never
        w = CU.sizing_walk(cands)
        self.assertEqual([c["name"] for c in w["taken"]], ["big"])
        self.assertEqual(w["stop"], "cap-media")                           # 4500 + 60 > 4500: the wall, the walk stops
        self.assertFalse(w["sized"])

    def test_shelf_exhaustion_named(self) -> None:
        w = CU.sizing_walk([dict(name="only", worded=69, media_s=251.0, shelf_index=0)])
        self.assertEqual((w["stop"], w["sized"], w["worded"]), ("shelf exhausted", False, 69))


def _publish_tape(tape_dir: Path, specs: list) -> None:
    """A hand-built tape by the format's OWN writer, in the converter's own row form: specs =
    ("eye", t) | ("eye", t, meta-extra) | ("ear", start, word, mapped_t) in row order — an ear row carries
    its MAPPED frame's moment (V0's declared caption→moment mapping), exactly as the converter writes it.
    `at` from DATE + t seconds (the converter's own clock form)."""
    from datetime import datetime, timedelta, timezone
    from creature.tape import Tape
    tape_dir = Path(tape_dir)
    tape = Tape(tape_dir.parent, tape_dir.name)
    base = datetime.strptime(DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    def at_of(t: float) -> str:
        return (base + timedelta(seconds=t)).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    for spec in specs:
        if spec[0] == "eye":
            t = spec[1]
            meta = {"moment": f"v{t:06.1f}", "source": "video", "t": float(t)}
            meta.update(spec[2] if len(spec) > 2 else {})
            tape.publish("eye", b"\x89PNG-fake-" + str(t).encode(), meta, "png", at=at_of(t))
        else:
            _, start, word, mapped = spec[:4]
            meta = {"moment": f"v{mapped:06.1f}", "word": word, "start": float(start), "duration": 1.0,
                    "track_kind": "authored", "source": "video-caption"}
            meta.update(spec[4] if len(spec) > 4 else {})
            tape.publish("ear", str(word).encode(), meta, "txt", at=at_of(start))


class WordedCanvases(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="curriculum-worded-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def test_distinct_frames_carrying_an_ear_token(self) -> None:
        tape = self.tmp / "v1"
        # frames at t=0,1,2,3; the tokens starting 1.0 and 1.2 BOTH map to the t=2 frame (V0's mapping:
        # the first sampled frame at-or-after the start), the token at 3.0 maps to t=3 — 2 worded canvases
        _publish_tape(tape, [("eye", 0.0), ("eye", 1.0), ("ear", 1.0, "red", 2.0), ("ear", 1.2, "apple", 2.0),
                             ("eye", 2.0), ("ear", 3.0, "bye", 3.0), ("eye", 3.0)])
        w = CU.worded_canvases(tape)
        self.assertEqual((w["frames"], w["ear_rows"], w["worded"]), (4, 3, 2))

    def test_v1s_own_numbers_reproduced(self) -> None:
        # V0's mapping on the hashed tapes of record: song1 36 + song2 33 = the 69 of V1/V2's readings
        tape1 = ROOT / "docs" / "organism" / "whole" / "records" / "open-world-1" / "bench" / "tape-a"
        tape2 = BENCH2 / "tape-2"
        self.assertEqual(CU.worded_canvases(tape1)["worded"], 36)
        self.assertEqual(CU.worded_canvases(tape2)["worded"], 33)


class MotionEvents(unittest.TestCase):
    def test_the_cutters_own_threshold_form(self) -> None:
        from statistics import median
        tmass = [0.10, 0.12, 0.09, 0.11, 4.0, 0.10, 0.12]     # one planted spike at frame 4
        ev = CU.motion_events(tmass)
        med, mad = median(tmass), median([abs(x - median(tmass)) for x in tmass])
        self.assertEqual(ev["events"], [4])
        self.assertAlmostEqual(ev["threshold"], med + EC.MAD_K * mad)   # median + 3×MAD, the cutter's DECLARED form
        self.assertEqual((ev["median"], ev["mad"]), (med, mad))

    def test_degenerate_all_still_stream_has_no_events(self) -> None:
        self.assertEqual(CU.motion_events([0.5] * 12)["events"], [])    # median + 3×MAD = 0.5; nothing exceeds


class TokenCanvases(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="curriculum-tokens-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def test_next_eye_row_is_v0s_mapping_and_collision_free(self) -> None:
        # TWO video blocks with DELIBERATELY identical moment strings (V1's concat form carries such collisions:
        # moments restart per source) — the mapping must follow the tape's own row order, never the string.
        tape = self.tmp / "pair"
        _publish_tape(tape, [("eye", 0.0), ("ear", 0.4, "red", 1.0), ("eye", 1.0), ("eye", 2.0),
                             ("eye", 0.0, {"video": "b"}), ("ear", 0.4, "blue", 1.0, {"video": "b"}),
                             ("eye", 1.0, {"video": "b"})])
        toks = CU.token_canvases(tape)
        # "red" (start 0.4) → video A's t=1.0 frame = canvas 1; "blue" → video B's t=1.0 frame = canvas 4
        # (the same moment strings appear in both videos; the canvases are distinct — collision-free)
        self.assertEqual([(t["word"], t["canvas"]) for t in toks], [("red", 1), ("blue", 4)])
        self.assertEqual([t["video"] for t in toks], [None, "b"])        # the concat's additive key where present

    def test_a_token_with_no_following_frame_is_a_finding_never_silent(self) -> None:
        tape = self.tmp / "bad"
        _publish_tape(tape, [("eye", 0.0), ("ear", 0.4, "orphan", 1.0)])     # no eye row after the ear row
        with self.assertRaises(RuntimeError):
            CU.token_canvases(tape)


class Synchronized(unittest.TestCase):
    def test_the_plus_minus_one_canvas_edges_and_the_same_video_rule(self) -> None:
        cvideos = ["a"] * 10 + ["b"] * 10
        events = [5]                                                     # one motion event, video a, canvas 5
        toks = [dict(word="far", canvas=2), dict(word="nearlo", canvas=4), dict(word="nearhi", canvas=6),
                dict(word="past", canvas=7)]
        s = CU.synchronized(toks, events, cvideos)
        self.assertEqual([toks[i]["word"] for i in s["token_ixs"]], ["nearlo", "nearhi"])
        self.assertEqual(s["canvases"], [4, 6])
        # an event in video b (canvas 10) never synchronizes video a's canvas 9 — |9−10| ≤ 1 but ACROSS videos;
        # and the same event DOES synchronize video b's own canvas 10 — both directions of the rule pinned
        s2 = CU.synchronized([dict(word="edgea", canvas=9), dict(word="firstb", canvas=10)], [10], cvideos)
        self.assertEqual(s2["token_ixs"], [1])
        s3 = CU.synchronized([dict(word="edgea", canvas=9), dict(word="firstb", canvas=10)], [9], cvideos)
        self.assertEqual(s3["token_ixs"], [0])


class ShuffledOnsets(unittest.TestCase):
    def test_deterministic_at_the_laws_own_seed(self) -> None:
        a = CU.shuffled_onsets(100, 3600)
        b = CU.shuffled_onsets(100, 3600)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 100)
        self.assertTrue(all(0 <= c < 3600 for c in a))
        self.assertEqual(CU.SHUFFLE_SEED, EC.SHUFFLE_SEED)               # the law's seed is the cutter's own constant


class SyncReading(unittest.TestCase):
    def test_the_whole_computation_on_a_known_stream(self) -> None:
        # 20 canvases, one video; a motion event at canvas 10; tokens at canvases 3, 10, 12; learning planted
        # at canvas 10 only (learns[10] = 2): the real synchronized side must out-learn its matched control,
        # and the shuffled control's numbers print beside (the pair, never one without the other).
        tmass = [0.1] * 20
        tmass[10] = 5.0
        learns = [0] * 20
        learns[10] = 2
        cvideos = ["a"] * 20
        toks = [dict(word="far", canvas=3), dict(word="on", canvas=10), dict(word="off", canvas=12)]
        r = CU.sync_reading(toks, tmass, learns, cvideos)
        self.assertEqual(r["motion"]["events"], [10])
        self.assertEqual([toks[i]["word"] for i in r["real"]["token_ixs"]], ["on"])
        self.assertEqual(r["real"]["canvases"], [10])
        self.assertEqual(r["real"]["share"], 1 / 3)                      # the synchronized share of tokens
        self.assertEqual((r["real"]["learning"]["total"], r["real"]["control"]["total"]), (2, 0))
        self.assertEqual(r["real"]["control"]["frames"], 1)              # the same count, nearest in time
        self.assertEqual(r["shuffled"]["learning"]["frames"], r["shuffled"]["control"]["frames"])
        self.assertEqual(r["seed"], EC.SHUFFLE_SEED)
        self.assertEqual(r["n_canvases"], 20)
        # the chance expectation printed: one event's ±1 neighborhood inside one video = 3 of 20 canvases
        self.assertAlmostEqual(r["chance_share"], 3 / 20)


class Concat(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="curriculum-concat-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        _publish_tape(self.tmp / "ta", [("eye", 0.0), ("ear", 0.4, "red", 1.0), ("eye", 1.0)])
        _publish_tape(self.tmp / "tb", [("eye", 0.0), ("eye", 1.0), ("ear", 1.2, "blue", 2.0), ("eye", 2.0)])

    def test_v1s_concat_form_mirrored_exactly_plus_the_one_additive_key(self) -> None:
        out = self.tmp / "cat"
        plan = CU.concat_plan([{"name": "song-a", "tape": self.tmp / "ta"},
                               {"name": "song-b", "tape": self.tmp / "tb"}], date=DATE)
        stats = CU.concat_tapes(plan, out)
        self.assertEqual((stats["rows"], stats["eye"], stats["ear"]), (7, 5, 2))
        days = sorted(out.glob("*.jsonl"))
        self.assertEqual([d.name for d in days], [f"{DATE}.jsonl"])      # the day file = the curriculum date
        rows = [json.loads(l) for l in days[0].read_text().splitlines() if l.strip()]
        self.assertEqual([r["seq"] for r in rows], list(range(1, 8)))    # seq reassigned 1..N in order
        self.assertEqual([r["payload"] for r in rows],
                         [f"payload/{i:09d}.{e}" for i, e in
                          zip(range(1, 8), ["png", "txt", "png", "png", "png", "txt", "png"])])
        for r in rows:                                                   # payload renamed to the new seq, bytes untouched
            self.assertEqual(hashlib.sha256((out / r["payload"]).read_bytes()).hexdigest(), r["sha"])
        # V1's form: `at` / meta.t / meta.moment per-source, UNTOUCHED (they restart at the second video);
        # meta.series is V1's own concat key; meta.video is the law's ONE additive key; `source` untouched.
        self.assertEqual([r["at"] for r in rows if r["sense"] == "eye"],
                         [f"{DATE}T00:00:0{t}.000Z" for t in (0, 1)] + [f"{DATE}T00:00:0{t}.000Z" for t in (0, 1, 2)])
        for r, name in zip(rows, ["song-a"] * 3 + ["song-b"] * 4):
            self.assertEqual(r["meta"]["series"], name)
            self.assertEqual(r["meta"]["video"], name)
            self.assertEqual(r["meta"]["source"], "video" if r["sense"] == "eye" else "video-caption")
        self.assertEqual([r["meta"]["t"] for r in rows if r["sense"] == "eye"], [0.0, 1.0, 0.0, 1.0, 2.0])
        # the collision V1's form carries: both videos' t=0 frames share one moment string — mirrored, declared
        self.assertEqual(rows[0]["meta"]["moment"], rows[3]["meta"]["moment"])

    def test_byte_identical_on_regeneration(self) -> None:
        plan = CU.concat_plan([{"name": "song-a", "tape": self.tmp / "ta"},
                               {"name": "song-b", "tape": self.tmp / "tb"}], date=DATE)
        CU.concat_tapes(plan, self.tmp / "c1")
        CU.concat_tapes(plan, self.tmp / "c2")
        self.assertEqual((self.tmp / "c1" / f"{DATE}.jsonl").read_bytes(),
                         (self.tmp / "c2" / f"{DATE}.jsonl").read_bytes())

    def test_a_mixed_date_set_is_refused(self) -> None:
        other = self.tmp / "tc"
        _publish_tape(other, [("eye", 0.0)])
        next(other.glob("*.jsonl")).rename(other / "1999-01-01.jsonl")   # a different day file: not this curriculum
        plan = CU.concat_plan([{"name": "song-a", "tape": self.tmp / "ta"},
                               {"name": "song-c", "tape": other}], date=DATE)
        with self.assertRaises(RuntimeError):
            CU.concat_tapes(plan, self.tmp / "cbad")


# ---------------------------------------------------------------- G-PLANT (the law §3): the planted burst, the planted word
PLANT_FRAMES = 30
PLANT_BASE = (16, 16)                  # the bright square's resting top-left
PLANT_MOVES = {4: (80, 16), 5: (80, 80), 6: (16, 80)}   # the DECLARED burst: a new position at each of these frames
PLANT_RETURN = 7                       # the jump back to base — a transient too, declared (the burst's own closing edge)
PLANT_EVENTS = sorted(PLANT_MOVES) + [PLANT_RETURN]
PLANT_WORD = "jumping"
PLANT_ONSET = 5.0                      # the planted word's onset lands EXACTLY on the burst (frame t=5)
PLANT_SRT = """1
00:00:02,000 --> 00:00:02,900
look

2
00:00:05,000 --> 00:00:05,900
jumping

3
00:00:10,000 --> 00:00:10,900
the

4
00:00:22,000 --> 00:00:22,900
square
"""
# the fixture's own truth at the law's seed 20261777: shuffled_onsets(4, 30) = [1, 25, 13, 13] — the planted
# word (index 1) redraws to canvas 25, nowhere near the burst {4,5,6,7}: the shuffle CANNOT mark it (printed,
# never hidden — the draw is the law's, the geometry this fixture's declared design)


def _plant_clip(path: Path) -> None:
    """PIL-generated frames (grey 128×128, a 32×32 white square — at the declared burst frames the square
    sits at a new position each frame), packaged by ffmpeg into an mp4 (the fixture's own encoding, declared:
    1 fps so the converter's 1 Hz samples land exactly on the source frames)."""
    tmp = Path(tempfile.mkdtemp(prefix="curriculum-plant-frames-"))
    try:
        for f in range(PLANT_FRAMES):
            pos = PLANT_MOVES.get(f, PLANT_BASE)
            im = Image.new("RGB", (128, 128), (96, 96, 96))
            for y in range(pos[1], pos[1] + 32):
                for x in range(pos[0], pos[0] + 32):
                    im.putpixel((x, y), (255, 255, 255))
            im.save(tmp / f"f{f:03d}.png")
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-framerate", "1", "-i", str(tmp / "f%03d.png"),
                            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(path)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise AssertionError(f"ffmpeg plant clip exit {p.returncode}: {p.stderr[-400:]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class GPlant(unittest.TestCase):
    """The law's G-PLANT: the SAME converter + a REAL wired replay (the bench genome + the front) + the SAME
    instrument. The planted word MUST be marked synchronized; with the onsets shuffled it MUST NOT."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="curriculum-plant-"))
        cls.video, cls.srt = cls.tmp / "plant.mp4", cls.tmp / "plant.en.srt"
        _plant_clip(cls.video)
        cls.srt.write_text(PLANT_SRT)
        cls.tape = cls.tmp / "tape"
        stats = VD.convert(cls.video, cls.srt, cls.tape, date=DATE)      # the SAME converter, UNCHANGED
        assert stats["scene_cuts"] == [], f"the plant clip must carry no scene cut, got {stats['scene_cuts']}"
        assert stats["eye_rows"] == PLANT_FRAMES, stats
        genome = cls.tmp / "GENOME.genome"
        shutil.copy(BENCH2 / "GENOME.genome", genome)                    # the bench genome, COPIED, never written
        from genome.machinery import parse_genome
        from creature.senses.vfront import VideoFront
        from creature.replay import run_replay
        g = parse_genome(genome.read_text())
        front = VideoFront(g.gaze, g.colour)                             # built fresh: the temporal state is this replay's own
        journal = run_replay(genome, cls.tape, cls.tmp / "out", eye_front=front)
        rows = EC.load_journal(journal)
        _, canvases = EC.err_series(rows)
        assert all("front" in c for c in canvases), "the wired journal carries the front on every canvas row"
        cls.tmass = [float(c["front"]["t_mass"]) for c in canvases]
        cls.learns = EC.learn_per_frame(rows, canvases)
        cls.tokens = CU.token_canvases(cls.tape)
        cls.cvideos = CU.canvas_videos(cls.tape)
        cls.motion = CU.motion_events(cls.tmass)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_planted_burst_is_the_motion_events(self) -> None:
        self.assertEqual(set(self.motion["events"]), set(PLANT_EVENTS))

    def test_the_planted_words_onset_lands_on_the_burst(self) -> None:
        planted = [t for t in self.tokens if t["word"] == PLANT_WORD]
        self.assertEqual([(t["start"], t["canvas"]) for t in planted], [(PLANT_ONSET, int(PLANT_ONSET))])

    def test_the_planted_word_is_synchronized_a_plain_word_is_not(self) -> None:
        s = CU.synchronized(self.tokens, self.motion["events"], self.cvideos)
        synced_words = [self.tokens[i]["word"] for i in s["token_ixs"]]
        self.assertEqual(synced_words, [PLANT_WORD])      # EXACTLY the planted word (the others sit ≥3 canvases off)
        r = CU.sync_reading(self.tokens, self.tmass, self.learns, self.cvideos)
        planted_ix = [i for i, t in enumerate(self.tokens) if t["word"] == PLANT_WORD][0]
        self.assertIn(planted_ix, r["real"]["token_ixs"])

    def test_shuffled_onsets_the_planted_word_is_not_synchronized(self) -> None:
        sh = CU.shuffled_onsets(len(self.tokens), PLANT_FRAMES)          # the law's own seed, never tuned
        planted_ix = [i for i, t in enumerate(self.tokens) if t["word"] == PLANT_WORD][0]
        shuffled_tokens = [dict(t, canvas=c) for t, c in zip(self.tokens, sh)]
        s = CU.synchronized(shuffled_tokens, self.motion["events"], self.cvideos)
        self.assertNotIn(planted_ix, s["token_ixs"])                     # MUST NOT be marked (the instrument CAN fail)
        self.assertEqual(s["token_ixs"], [])                             # this fixture at this seed: nothing at all


class GatesOfRecord(unittest.TestCase):
    """The instruments of record, sha-pinned by the law — executable G-FRONT / G-HEARS on the tree."""

    def test_g_front_and_the_tools_unchanged(self) -> None:
        self.assertEqual(hashlib.sha256((ROOT / "creature" / "senses" / "vfront.py").read_bytes()).hexdigest(),
                         SHA_VFRONT)
        self.assertEqual(hashlib.sha256((ROOT / "tools" / "worlds" / "event_cutter.py").read_bytes()).hexdigest(),
                         SHA_CUTTER)
        self.assertEqual(hashlib.sha256((ROOT / "tools" / "worlds" / "video_door.py").read_bytes()).hexdigest(),
                         SHA_DOOR)

    def test_g_hears_the_bench_genome_unchanged(self) -> None:
        self.assertEqual(hashlib.sha256((BENCH2 / "GENOME.genome").read_bytes()).hexdigest(), SHA_GENOME)


if __name__ == "__main__":
    unittest.main()
