# PREREG-OPEN-WORLD-1 (V0) — THE VIDEO DOOR'S CONVERTER AND THE FIRST BENCH

*Law before code (RULES law 1). Author: Kimi K3 (kimi-code, acting seat, alone — Ahmad's words of 2026-10-05).
Ordered by Ahmad's word of 2026-10-07 («Deep research on it and start this part» — the world opens to the organism:
real videos, kids' learning first). Read first: `docs/brain/RESEARCH-OPEN-WORLD.md` WHOLE (the human mechanism and
its warnings) and `docs/brain/RESEARCH-HUMAN-PREDICTIVE-NORMALIZATION.md` (the absorbing machinery's road).*

## 0 · The question, what a pass settles, what it cannot

**The question.** Can the organism's own machinery live through a tape synthesized from a REAL kids'-learning video
— the world's first non-generated input — with the tape format's own gates green, the births/surprise behaving, the
caption stream's statistics measured, and every number honest? Nothing more is claimed.

**A pass settles:** (i) the converter is deterministic and truthful (the same video + the same parameters → the same
tape, byte-identical; a corrupted source frame is CAUGHT by the tape's own hash); (ii) a fresh mind replays the
video tape end to end, exit 0, with births, surprise and learning rows honest (presence counts, never a silent
zero); (iii) the caption stream's segmentation statistics are printed beside an EXTERNAL check; (iv) the price is
measured and inside §6's bounds. **A pass opens:** V1 (the organism's own cutter) and the road to V2/V3.

**It cannot settle (each said now):** that the organism LEARNS anything meaningful from one clip (a content claim
needs V3's curriculum and its own laws); any contingent-learning claim from a non-contingent tape (the Kuhl warning,
carried verbatim from the research doc); any claim about a LIFE (no life is launched by this law — the bench only);
any permanence of the caption supply (a revocable sensor, named).

## 1 · The source and its honesty

- ONE kids'-learning video, chosen at the build and NAMED here at the amendment if changed: a short (≤ 10 min)
  colours-and-shapes learning video with an English caption track (authored preferred; ASR flagged
  `trackKind="ASR"` in the tape's meta, never hidden).
- The source files (the video file + the caption file) are downloaded ONCE into the bench's records dir with their
  sha256 recorded in the record; the tape must regenerate byte-identical FROM THE FILES, never from the network
  (the network is a sensor, the files are the record). If a re-download ever differs, that is a finding, printed.
- The conversion parameters (the frame rule, the grid, the caption mapping) are constants of the law, in §2.

## 2 · The build (tools/worlds/video_door.py, tests first)

1. **The eye rows:** ffmpeg's scene-cut detector finds candidate cuts; frames are sampled at 1 Hz between cuts (a
   constant of the law); each frame is letterboxed to the eye's own 128×128 RGB PNG (the scene world's canvas
   format, `brain/scene/world.py:539`'s form); one eye row per sampled frame, the payload written under
   `tape/payload/`, the row's `sha` the payload's own.
2. **The ear rows:** the caption track's `{text, start, duration}` triples → the tape's own ear-row form
   (`sense: "ear"`, `meta.word` per token, the caption's timing carried in the row's `meta` as `start`/`duration`,
   `source: "video-caption"`, the provenance flag `track_kind`). Caption text is split on whitespace into word
   tokens, lowercased, punctuation stripped — the tape's word form (letters only, the organism's own rule; digits
   and symbols dropped, counted).
3. **The tape:** day-file `2026-10-07.jsonl` (the conversion date) under the bench's own tape dir, rows ordered by
   `start` time then frame time, `seq` assigned 1..N in order, plus `payload/`. The organism's replay reader
   (`creature/replay.py`) must parse it with zero special-casing.
4. **The TP-dip reader** (the research's W1 machine form): running unigram/bigram counters over the caption token
   stream; a boundary where TP(Y|X) = count(XY)/count(X) dips below the stream's own median TP by ≥ 2× the median
   absolute deviation (a declared, never-tuned threshold). Printed: the dip boundaries beside ffmpeg's scene cuts —
   the OVERLAP printed as a reading, NO bar (the two cutters answer different questions; disagreement is the
   expected science, not a failure).

## 3 · The gates (instrument)

| gate | asserts | read on |
|---|---|---|
| **G-FORMAT** | the tape parses by `creature/replay.py`'s own reader unchanged; every eye row's `sha` == its payload's sha; every ear row's word matches the tape's word form | the bench |
| **G-IDENTITY** | two independent conversions of the same source files → byte-identical tapes; two replays of the tape → byte-identical journals | the bench |
| **G-PLANT** | a corrupted source frame (one bit flipped) changes the tape's hash and the converter's own check CATCHES it; a planted non-word caption token (digits/symbols) is dropped and COUNTED | the bench |

## 4 · The marks

| # | mark | what is read | bar |
|---|---|---|---|
| **M-BIRTH** | the fresh mind's births (cells, words) over the video tape, with presence counts | births > 0 (never a silent zero; the exact count printed) |
| **M-SURPRISE** | the surprise profile over the tape (the replay's own rows) | printed; the first-vs-repeat-exposure contrast printed (the repetition-suppression instrument of N1's road, printed here as a reading) |
| **M-SEG** | the TP-dip boundaries vs ffmpeg's scene cuts | a READING, no bar: the counts, the overlap, both directions |
| **M-COST** | conversion wall + replay CPU, from the slot ledger | measured, printed; inside §6's bounds |

## 5 · The verdict rule (TOTAL and ORDERED)

| # | the marks read (in this order) | verdict |
|---|---|---|
| 1 | a gate fails (G-FORMAT, G-IDENTITY, G-PLANT) | **VOID** — an AMENDMENT names the cause |
| 2 | M-BIRTH fails (zero births over a non-empty video tape) | **FAIL-SENSE** — the video tape teaches the organism nothing at all; named, the road re-thinks |
| 3 | M-COST fails | **FAIL-COST** — re-priced in a NEW law, never shipped silent |
| 4 | the gates hold, M-BIRTH/M-SURPRISE/M-SEG/M-COST printed inside their bounds | **PASS** — the video door exists as an instrument; V1's law may be written with this bench as its planning input |

## 6 · The price and the stop rules

- The clip: ≤ 10 min; at 1 Hz ≈ ≤ 600 frames; conversion ≈ minutes (ffmpeg, measured 2009-era costs are trivially
  met); the replay of ≤ 600 canvases ≈ CPU-minutes at 4G (the OFF replay's measured per-canvas rate scaled by the
  store's size — printed, not assumed). **STOP rules:** S1 the replay's CPU > 2 CPU-h → STOP; S2 the converter's
  peak > 3,500 MB or the replay's > 3,800 MB under SLOT_MEM 4G → STOP; S3 an instrument fault (a gate) → VOID,
  an AMENDMENT names it.
- Every job through `slot` (RULES); never beside a quiet window; the live life and the ON replay are untouched
  (the bench is minutes-scale; it yields to them).
- The network is used ONCE (the download), at the build, by the seat's own hand; the bench thereafter runs from the
  hashed files only.

## 7 · Never

No borrowed pretrained weights; no LM anywhere; no caption content written into the organism's mind by hand (the
ear rows are the organism's own to learn); no silent zero counts; no tuned threshold after a reading; a FAIL told
honestly is a result.

Signed: **Kimi K3 (kimi-code, author and acting seat, alone — Ahmad's words of 2026-10-05; this build ordered by his
word of 2026-10-07)**, 2026-10-07 15:53 +0400 (from `date` at signing) (from `date` at signing), on this file's sha256 carried by the
SEAT-LINE file beside it in the records dir at the verdict.
