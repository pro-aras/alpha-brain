# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 22:0x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 2.
"""creature/senses/ear.py — the sound ear door.

A sense thread listening at a folder for audio files (`SENSE ear-sound wav 16000 mono`, EAR.md §4's whole
chain) exactly the way `creature/senses/folder.py` watches for pictures: at most one new wav per scan (by
sha256, never mtime), deterministic filename order, a seen-set cursor written AFTER the row(s) it names
are durable (#230). The DSP itself -- COCHLEA -> HAIRCELL -> AGC -> ONSET -> MODBANK -> EVENT -- lives in
`genome/cochlea.py` (the FIXED organ, sha-pinned to E52's own gammatone/front code); this module is the
thin sense-thread wrapper that turns its events into tape rows.

**While silent it publishes nothing** (EAR.md §4, §5 Q1's own recommendation): a folder with no wav file
in it publishes 0 rows over any polling period (structurally -- there is no file to read); a wav file that
IS silence (digital zero, or any signal whose broadband onset never clears the EVENT rule's own prominence
bar) also publishes 0 rows -- `genome.cochlea.analyse()` returns `{"events": []}` and this sense thread's
loop then has nothing to publish for that file (still marks it seen, so it is never re-scanned).

Each event becomes ONE tape row, sense name `ear-sound`, meta carrying the fields EAR.md §4's `TRAIT`/
`WHEN`/`PROVENANCE` lines name: `when` (the onset instant, sample-exact, seconds from the file's own
start), `band`/`onset_shape`/`level` (the raw sub-vectors, for a reader that wants them un-normalised),
and `provenance` (front name, source file, sample offset, the front's own fixed parameters) -- WHERE
(ITD/ILD) is NOT delivered: the declared line is `wav 16000 MONO` (machinery.py's own parser refuses
"stereo"), and a directional cue needs two channels this organ does not have (RAISED in the builder
report, not worked around). OWNVOICE is likewise not computed: it needs a top-down prediction from the
mind (ADAPTS, BRIEF.md's own bin) and no such prediction exists on this branch (SENTENCE and the mouth are
`#OFF` in G4.genome) -- every event's `meta["ownvoice"]` is `None`, an honest "not computed", never a
guessed False.

`AREA sound from cochlea` / `MEET sight sound` / `MEET sound words` are NOT wired here: this file only
PUBLISHES; `creature/mind.py:consume` reads only "ear"/"eye" senses today and falls through "ear-sound"
untouched (harmless dead weight on this branch, exactly like the game door's "outcome" rows -- see
creature/senses/game.py's own docstring for the same shape of claim).

A pure SENSE (G4-1's writer sweep): never touches state/journal/memory, never imports Organism/machinery.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, List, Tuple

from genome import cochlea

AUDIO_SUFFIXES = (".wav",)

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists; --ear-sound-dir stays an explicit override for tests regardless of this constant.
EAR_SOUND_DOOR_GATED = True


def _load_seen(seen_path: Path) -> set:
    if not seen_path.exists():
        return set()
    try:
        return set(json.loads(seen_path.read_text()))
    except (json.JSONDecodeError, OSError):
        return set()   # a torn/partial SEEN.json from a crash mid-write is "nothing seen yet", never fatal


def _candidate_files(audio_dir: Path) -> List[Path]:
    """Every `.wav` directly under `audio_dir`, sorted BYTEWISE by filename -- the same deterministic
    order rule the folder door uses (folder.py's own C2 pacing discipline), applied here one level
    simpler (this door does not nest by word-folder; a filename is just a filename)."""
    if not audio_dir.exists():
        return []
    return sorted(p for p in audio_dir.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES)


def sense(publish: Callable, stop_event, audio_dir: Path, root: Path, rate: int = 16000,
          period: float = 1.0) -> None:
    """`rate`: the declared `SENSE ear-sound wav <rate> mono` sample rate (genome.ear_sound["rate"]) --
    every file is resampled to it (genome.cochlea.read_wav_mono) so the front's fixed ERB spacing always
    sees the rate it was designed for, regardless of what rate a dropped-in file happens to carry."""
    audio_dir = Path(audio_dir)
    seen_path = Path(root) / "ear_sound" / "SEEN.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    seen = _load_seen(seen_path)

    while not stop_event.is_set():
        for pic in _candidate_files(audio_dir):
            try:
                data = pic.read_bytes()
            except OSError:
                continue
            sha = hashlib.sha256(data).hexdigest()
            if sha in seen:
                continue
            try:
                x = cochlea.read_wav_mono(pic, target_rate=rate)
                result = cochlea.analyse(x, fs=rate)
            except cochlea.CochleaError:
                seen.add(sha)   # a file this organ cannot read (stereo, an unsupported sample width) is
                seen_path.write_text(json.dumps(sorted(seen)))   # marked seen so it is never retried forever, never fatal to the thread
                break
            except Exception:
                continue   # an unreadable/corrupt file: skip this scan, retry next period (SenseThread's own restart law covers a real crash)

            for i, ev in enumerate(result["events"]):
                moment = f"a{sha[:10]}e{i:04d}"
                trait = ev["trait"]
                publish("ear-sound",
                        trait.astype("float32").tobytes(),
                        {"moment": moment, "source": "ear_sound", "file": pic.name, "sha_file": sha,
                         "event_index": i, "when": ev["t_s"], "level": ev["level"],
                         "band": [round(float(v), 6) for v in ev["band"]],
                         "onset_shape": [round(float(v), 6) for v in ev["onset_shape"]],
                         "ownvoice": None,   # ADAPTS, no top-down prediction wired on this branch -- honest "not computed"
                         "provenance": {"front": "cochlea:gammatone-erb32-50-7800",
                                        "file": pic.name, "offset_s": ev["t_s"], "rate": rate}},
                        "f32")
            seen.add(sha)
            seen_path.write_text(json.dumps(sorted(seen)))   # AFTER the row(s) (zero or more) are durable -- the cursor law (#230)
            break   # one file per scan, the folder door's own pacing convention
        stop_event.wait(period)
