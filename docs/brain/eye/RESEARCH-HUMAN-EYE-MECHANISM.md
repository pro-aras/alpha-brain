# RESEARCH-HUMAN-EYE-MECHANISM — the human visual mechanism whole, our eye today measured against it, and the advancement road

*Research under his standing word (memory `feedback_2026-10-05_human_mechanism_never_cheat.md`) and his 2026-10-05 evening order: «check the brain and organs interconntivity and also the eyes. Especially the eyes. Because eyes are not upgraded to match the real human or even more advanced mechanism yet. Deep research our current organs, and there working, brain and eyes. And see how it can be further improved to the advance level. And then start editing or building it.» — Kimi K3 (kimi-code), 2026-10-05. The code read is genome master 5b0942c (the mouthcap worktree). The lives read are quoted from the record.*

**Sources and read-status (the house rule):**
1. **Jiang & Rao, *Predictive Coding Theories of Cortical Function*** (Oxford Research Encyclopedia) — [arXiv:2112.10048](https://arxiv.org/pdf/2112.10048). Read whole through the visual-system and endstopping sections (the Rao–Ballard model, its equations, the evidence review); the later empirical sections partially.
2. **Olshausen & Field 1996**, *Emergence of simple-cell receptive field properties by learning a sparse code for natural images*, Nature 381 — [doi:10.1038/381607a0](https://www.nature.com/articles/381607a0.pdf). Abstract and full reference list read (paywalled body); its content cross-read inside source 1 («Sparse Coding as a Special Case of Predictive Coding», read whole).
3. **Itti, Koch & Niebur 1998**, *A model of saliency-based visual attention for rapid scene analysis*, IEEE PAMI 20(11) — abstract and its well-quoted mechanism (multiscale features → one saliency map → winner-take-all with inhibition of return); body not fetched, flagged. Our gaze organ was BUILT to this form (its own docstring), so the primary's role here is checking, not discovery.
4. Hubel & Wiesel / Gabor V1 descriptions; Srinivasan, Laughlin & Dubs 1982 (the fly-eye predictive-coding result); DiCarlo ventral-stream reviews — via source 1's account (read whole there), flagged secondary.
5. Dale & Reiter and the mouth research — `docs/brain/mouth/RESEARCH-HUMAN-MOUTH-MECHANISM.md` (this repo), for the loop's mouth end.
6. **HUMAN-MECHANISM-MAP-2026-09-29.md** (this repo) — the 09-29 map, re-read whole today; its EYES row's three named gaps re-verified against today's code (§3).

---

## 1 · The human visual mechanism, the whole loop (as the evidence has it)

1. **The retina sends errors, not intensities.** Centre–surround receptive fields exist to remove what is predictable: retinal and LGN cells convey the DIFFERENCE between the local intensity and a prediction of it from the surround (Srinivasan et al. 1982; Dong & Atick 1995 — «whitened residual errors»). Colour is opponent (red–green, blue–yellow). The split into parallel fast/coarse (magnocellular) and detail/colour (parvocellular) channels begins here.
2. **LGN whitens in time and is gated from above.** Temporal decorrelation of natural statistics (Dan et al. 1996); and the LGN receives massive cortical feedback — the brain turns the tap by what it expects and wants (attention).
3. **V1's filters are local, oriented, bandpass — and they are LEARNED, not designed.** Simple cells look like Gabor/wavelet kernels; and a network that learns SPARSE linear codes of natural images develops exactly that family (Olshausen & Field 1996): the cortex wires itself for efficient coding of what it actually sees. This is the crucial point for us: the human eye's front is not a sealed hand-designed front — it is fitted to the organism's input by experience.
4. **The hierarchy predicts downward; errors flow upward.** Feedback connections carry predictions; feedforward connections carry prediction errors (Rao & Ballard 1999). Extra-classical effects (endstopping: a cell silenced when its stimulus extends into the surround) fall out of error minimization. Each level's receptive fields grow (convergence) — edges → parts → things.
5. **Attention is precision-weighting of errors, and the LOOK is the error-guided act.** In robust predictive coding (Rao 1998) a gain term gates prediction errors by how well the current hypothesis explains them: the system focuses where its hypothesis is good and, crucially, moves to where error remains. Perception is a LOOP: predict → look where the error is expected → update → repeat (active inference).
6. **The fovea is tiny; saccades are chosen.** A sharp centre, a coarse surround; ~3 saccades a second. Bottom-up: multiscale feature contrast → one saliency map → winner-take-all with inhibition of return (Itti & Koch 1998). Top-down: the task and the doubt steer the same map. Fixational micro-movements keep the world from fading.
7. **Ventral «what», dorsal «where/how»** — and «What–Where» predictive coding absorbs transformations in a separate channel so the «what» stays stable (Rao & Ruderman; equivariance).

## 2 · Our eye today, measured at machine level (code:lines)

- **The retina grid** (Alpha 2 V0.1, sha-pinned): 16×16 cells; per cell luminance, R–G and B–Y opponency, centre–surround contrast (radius 1, signed), four finite-difference orientation energies; saliency = their hand-weighted sum (`organs/retina.py:69-93`).
- **The gaze** (Alpha 2 V0.1, sha-pinned): first fixation at the saliency peak, then the most-surprising unvisited cell (within-frame prediction = the previous fixation's map — on a still canvas, residual saliency), inhibition of return, ≤ 4 fixations (`organs/gaze.py:45-66`). **Already the Itti & Koch form, single-scale.**
- **The per-glance descriptor** (the G0b eye, sealed): the 32×32 window → the declared INK rule → `machinery.retina`'s fixed steps (thresh/centre/blur/pool3/hog8/hogcells8x6/unit — a HOG tower of 112) + 32 raw colour numbers = **144** (`genome/gaze.py:203-267`, `genome/machinery.py:1004`). A fifth whole-canvas «coarse» glance (the periphery) of the same 144.
- **SURPRISE**: the mind's predicted 144-vector is compared per glance (`residual = 1 − cos`) and REPORTED — and then deliberately never used: «NEVER forwarded into `gaze_sequence`'s own `predicted=` argument, which would move FIXATION selection» (`genome/gaze.py:6-8`, `:209-217`). **The error is computed and filed; it steers nothing.**
- **Things**: nearby fixations (≤ 2 cells) join by union-find; a thing = the unit mean of its members' glances (`brain/scene/eye.py:75-109`). The brain learns words over thing features; the turn (DRIVE) expects/says/asks; the mouth voices the brain's phrase (W1, live in brain-long-4); the eye's forced road (`forced_glance`, `:120-135`) can place a window at any centroid — **built, pinned, and unused by any loop.**
- The 09-29 map's EYES row, re-verified today: (i) the look is never chosen by the mind — STILL TRUE (no `look`/`look-again` anywhere in creature code, grep 2026-10-05); (ii) no motion sense — still true (all channels are within-frame); (iii) photographs do not band — still true (the fixed front is fitted to drawn ink, not to natural images).

## 3 · The gap map — every part of the human loop against ours

| the human part (evidence §1) | ours (§2) | verdict |
|---|---|---|
| retina sends prediction errors (centre–surround), one mechanism at one scale | signed centre–surround at radius 1 on a 16×16 grid; absolute value used in saliency | **PART** — the right spirit, one scale, no ON/OFF split |
| colour opponency | R–G and B–Y channels + a 32-number raw block | **PRESENT** |
| oriented filters (Gabor family) | 4 finite-difference energies at the grid + a HOG tower at the window | **PART** — two hand-designed orientation systems where the human has one learned family |
| **the front is LEARNED from what the organism sees** (O&F 1996) | the descriptor is SEALED (fixed steps; HOG bins; never learned) | **MISSING — the «advanced level» his word points at** |
| multiscale (8 scales, Itti & Koch) | one scale (16×16; the 32×32 window) | **MISSING** |
| temporal channel (magno; LGN whitening) | nothing reads across moments | **MISSING** (the game world moves) |
| saliency map → WTA + IOR | the same form, single-scale | **PRESENT** |
| fovea + periphery | the 32×32 glance + the coarse whole | **PRESENT in form** |
| **attention steers the look; perception is the predict→look→update loop** (Rao 1998; active inference) | the residual is computed and filed; fixations are bottom-up only; the forced road exists unused | **MISSING — the loop's return arrow, the 09-29 gap, still open** |
| feedback predictions modulate lower areas | SURPRISE reports downstream only | **MISSING** (one loop above E1) |
| fixational refresh | static canvases | **N/A by world, named** |
| photographs (natural images) are read | the fixed front bands drawn ink (956/1000 record); natural images do not band (record) | **the fixed front's own limit — a LEARNED front is the human answer** |

## 4 · The advancement road (each step its own law, the human mechanism at machine level)

**E1 · THE CHOSEN LOOK (the loop's return arrow).** The human form: when the current hypothesis does not explain what is in view, LOOK AGAIN at the thing it doubts. Our organs already carry every piece: the brain's turn reports the leading hypothesis and its held words (`genome/brain.py:_turn_core`); the eye's `forced_glance` places a window at any centroid with byte-identity at fixation cells pinned (`brain/scene/eye.py:120-135`). The act: after the turn, where the leading hypothesis holds NO word (its own ask condition — B7's doubt), one forced glance at that hypothesis's locus re-feeds the eye's row before the learn. The bench's own 09-29 numbers (DIAG-LOOK-AGAIN): one more look takes the named-thing-seen rate from 0.89–0.90 to 0.98–0.99. Byte-identity on the record: replays differ where a doubt fires (a behaviour change — measured first as an R-LOOK reading over the closed tapes, the R-DIFF form, THEN a rung). **First, because it closes the loop he asked about («interconntivity»): eye → cells → brain → doubt → eye.**

**E2 · THE LEARNED EYE (the «even more advanced»).** The human form (O&F 1996): the front's filters are LEARNED for efficient coding of what the organism actually sees. Ours: learn a sparse dictionary over the organism's OWN canvases (the closed lives' payloads — pure: from scratch, no borrowed anything, its own worlds), and let each glance's feature be the sparse code (with the tower kept beside it through the gates). The TESTABLE PREDICTION the law makes first: on HIS drawn worlds, learned filters emerge localized/oriented/bandpass (the O&F family, measured by the same fits) — and the learned front must name the record's own held-out items at least as well as the sealed tower (a twin on the record, never a tuned race). Vector change → a rung; the gates are the mouth-cap law's identity forms reused.

**E3 · THE CHANGE CHANNEL.** The human form (magno; LGN temporal whitening): a channel that reads what MOVED. Ours: the game world is the one world that moves; the channel compares the moment's grid with the previous one's (the oracle's own `predicted=` periphery form, unused today) and feeds its saliency share. Scoped to the game first, with the still worlds proven unmoved.

**E4 · THE PYRAMID.** Multiscale grid (the Itti & Koch 8-scale form) — only if E1/E2's measurements say scale binds (a reading, never an assumption).

## 5 · What would show this map wrong (each checkable)

1. A chosen look does NOT raise the named-thing-seen rate on the record (the 09-29 bench's 0.98–0.99 was a toy's, not the life's) → E1 is refused, the loop stays open by evidence.
2. The learned filters on our canvases do NOT come out localized/oriented/bandpass (the drawn world is too poor for the O&F statistics) → E2's premise fails honestly, and the sealed tower stands by evidence.
3. The learned front names held-out record items WORSE than the sealed tower at equal cost → the «advanced» front buys nothing on the real task; refused.
4. The chosen look's fire rate is so high the canvas cost breaks the life's cadence (priced in E1's law) → the form is re-priced, never shipped silent.

*(edit: Kimi K3 (kimi-code), 2026-10-05 23:13 +0400 — first version, on the sources named in the header with their read-status flags)*
