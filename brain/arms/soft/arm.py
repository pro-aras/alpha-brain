# edit: Claude (Fable 5.1), 2026-09-24 18:42 +0400 — R24: Answer.raw['forced'] on the three abstain sites (the would-be answer for the FORCED-ANSWER twin); size() below.
# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 18:25 +0400 — the Arm-conforming wrapper
#   for A1 and every one of Builder 3's soft-gate variants, written AFTER brain/protocol.py
#   froze at ac7d2ff. ONE class (ArmA1) driven entirely by `config["variant"]`: A1, A1-FIXED,
#   A1-NO-SLEEP, A1-LOCAL, A1-BPTT-AWAKE, A1-MLC (identical code to A1 — it differs only in
#   what stream the HARNESS feeds it, per B1-PREREG.md §4's A1-MLC row; nothing here special-
#   cases it), A1-ATT, A1-MA — "seven arms are switches" (the advisor's framing this build
#   followed from the start).
#
# Declared choices (continuing D1-D14 from engine.py / steps.py):
#   D15. `answer()` NEVER mutates persisted state (engine/head parameters, `self.h`, growth
#        counters) regardless of `learn` — it always computes from a DETACHED CLONE of the
#        current hidden state. This makes control 0e's invariant (state_sha unchanged under
#        learn=False) TRUE BY CONSTRUCTION rather than by careful bookkeeping, and it is also
#        what makes `learn=True` vs `learn=False` differ ONLY in whether a pending-feedback
#        entry and the abstention-band histories are recorded (PREREG: "what learn=True is
#        allowed to change here is bookkeeping/context state").
#   D16. The REAL commit of an ASK's steps into the persistent recurrent state happens in
#        `fit_event(ask_row)` (called by HarnessContract right after `answer`), which reprocesses
#        the SAME cue+operand steps a second time -- once as a side-effect-free peek in
#        `answer`, once as the real state advance in `fit_event`. Deliberately not shared/
#        cached between the two calls: the peek's graph is rooted at a detached clone and must
#        never leak into the persisted graph (D15), so the two forward passes are independent
#        by construction, at the cost of computing the row's steps twice per training ask.
#   D17. FEEDBACK's gradient target is always the SHOWN `right` value (never inferred from
#        `valence` alone, since `right` is present on every FEEDBACK row regardless of valence,
#        §2.6) — PREREG's "reward: the given answer's target; no: the right answer is the
#        target and the wrong answer's logit is pushed down" is implemented as: loss =
#        CE(logits, index_of(right)) always, PLUS, when valence==VALENCE_NO, an extra term
#        that directly penalises the WRONGLY GIVEN answer's own logit (a second, explicit
#        third-factor term — pushing the right answer up does not by itself guarantee the
#        specific wrong one the arm gave moves down in a >2-way softmax).
#   D18. WORLD-head next-step loss is computed WITHIN one row's own step list only (teacher-
#        forced next-step prediction across that row's steps; the last step's "next" would
#        cross into the FOLLOWING row and is skipped) — a declared simplification, RAISED in
#        docs/briefs/B1-BUILDER3-REPORT.md rather than adding cross-row lookahead state.
#   D19. The sleep-replay ring stores RAW ROWS (not pre-encoded steps) plus the arrival index
#        each row belongs to; a replay window re-encodes on demand via the SAME StepEncoder
#        (deterministic, cache-backed) — "half from the latest arrival, half from older events"
#        is implemented by splitting ring INDICES by their stored arrival id, each half sampled
#        uniformly via a generator keyed (seed, "replay", sleep_index) (PREREG §4 row A1).
#   D20. Attention (A1-ATT/A1-MA) and growth are mutually exclusive by the PREREG's own words
#        ("both twins at FIXED width, no births") — ArmA1 forces hmax=h0=config["fixed_h"] and
#        arrival_budget=0 whenever `variant` is A1-ATT/A1-MA, so growth is structurally
#        impossible rather than merely unused.
from __future__ import annotations

import collections
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import torch
import torch.nn.functional as F

from brain.arms.soft.engine import (
    BPTTTrainer,
    CausalAttentionReadout,
    GrowingGRUEngine,
    LocalEligibilityTrainer,
    MemoryAttentionReadout,
    NameAnswerHead,
    PickScorer,
    WorldHead,
    YesNoHead,
    new_generator,
)
from brain.arms.soft.steps import (
    GLANCE_DIM, GLANCE_IDX_DIM, KIND_DIM, LETTER_DIM, STEP_DIM, SlotTable, StepEncoder, token_id_of_step,
)
from brain.glance_cache import Cache
from brain.protocol import Answer, AnswerKind, VALENCE_NO, VALENCE_REWARD, canonical_json

RING_CAPACITY = 20000  # PREREG §4 row A1: "sampled from its own event ring (the last 20,000 events)"


class RunningQuantile:
    """A bounded-history quantile tracker for the two abstention bands (PREREG §4 row A1:
    'the p95 of its own errors on taught glyphs' / 'the p5 of its own confidences ... both
    bands recomputed at each sleep'). Recompute is O(n log n) on <=2000 floats — cheap enough
    to call at every sleep without its own budget."""

    def __init__(self, maxlen: int = 2000):
        self.hist: collections.deque = collections.deque(maxlen=maxlen)

    def observe(self, x: float) -> None:
        self.hist.append(float(x))

    def quantile(self, q: float, default: float = 0.0) -> float:
        if not self.hist:
            return default
        return float(torch.quantile(torch.tensor(list(self.hist)), q))

    def to_list(self) -> List[float]:
        return list(self.hist)

    def load_list(self, xs: List[float], maxlen: int) -> None:
        self.hist = collections.deque(xs, maxlen=maxlen)


class ArmA1:
    """Conforms to `brain.protocol.Arm`. See module docstring for the variant switch and
    D15-D20 for the design decisions the PREREG leaves to the builder."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        variant = self.config.get("variant", "A1")
        self.variant = variant

        h0 = int(self.config.get("h0", 64))
        hmax = int(self.config.get("hmax", 1024))
        arrival_budget = int(self.config.get("arrival_budget", 16))
        arrival_regen = int(self.config.get("arrival_regen", 500))
        self.attention_mode: Optional[str] = None

        if variant == "A1-FIXED":
            hmax = h0
            arrival_budget = 0
        elif variant in ("A1-ATT", "A1-MA"):
            fixed_h = int(self.config["fixed_h"])  # required (§4.1's matched-parameter solve)
            h0 = hmax = fixed_h
            arrival_budget = 0
            self.attention_mode = "att" if variant == "A1-ATT" else "ma"

        self.engine = GrowingGRUEngine(
            input_dim=STEP_DIM, h0=h0, hmax=hmax, seed=self.seed,
            arrival_budget=arrival_budget, arrival_regen=arrival_regen,
        )

        att_d = int(self.config.get("att_d", 64))
        att_window = int(self.config.get("att_window", 256))
        head_hmax = hmax + (att_d if self.attention_mode else 0)
        self.head_hmax = head_hmax
        self.growable = self.attention_mode is None and variant != "A1-FIXED"

        # WorldHead reads the RAW engine trajectory only (never the attention-augmented query
        # state — PREREG says the read-out is "concatenated into the ANSWER head's input",
        # naming ANSWER, not WORLD); it is always sized to hmax and called at engine.active,
        # regardless of attention_mode. A real bug this file's own variant-conformance test
        # caught: it was first sized to head_hmax (hmax+att_d) and called with active_h=
        # head_hmax against an hmax-wide h_next, a shape mismatch check_arm's own smoke (via
        # fit_event on a plain TEACH) surfaced immediately for A1-ATT/A1-MA.
        self.world = WorldHead(hmax, GLANCE_DIM, LETTER_DIM, KIND_DIM)
        self.names = NameAnswerHead(head_hmax, out_cap=int(self.config.get("n_names_cap", 64)))
        self.yesno = YesNoHead(head_hmax)
        self.pick = PickScorer(head_hmax)

        gen = new_generator(self.seed, "head_init", 0)
        self.world.init_all(head_hmax, gen)
        self.names.init_block(h0 if False else head_hmax, gen)  # NAME head starts with 0 outputs; block is columns
        self.yesno.init_block(head_hmax, gen)
        self.pick.init_block(head_hmax, gen)

        if self.growable:
            for obj in (self.world, self.yesno):
                self.engine.register_growth_listener(obj)
            # NameAnswerHead / PickScorer: growing hidden columns needs no action (D3: new
            # columns are already zero in the pre-allocated buffer); registered anyway so a
            # future consumer that DOES need a hook (e.g. re-normalising) has one place to add it.
            self.engine.register_growth_listener(self.names)
            self.engine.register_growth_listener(self.pick)

        self.readout = None
        if self.attention_mode == "att":
            self.readout = CausalAttentionReadout(hmax, d=att_d, window=att_window)
            self.readout.init_block(hmax, gen)
        elif self.attention_mode == "ma":
            n_tokens = int(self.config["ma_n_tokens"])
            self.readout = MemoryAttentionReadout(hmax, n_tokens=n_tokens, d=att_d, window=att_window)
            self.readout.init_block(hmax, gen)

        self.awake_mode = "bptt" if variant == "A1-BPTT-AWAKE" else "local"
        self.sleep_mode = {"A1-NO-SLEEP": "none", "A1-LOCAL": "local"}.get(variant, "bptt")

        params = (
            list(self.engine.parameters())
            + list(self.world.parameters())
            + list(self.names.parameters())
            + list(self.yesno.parameters())
            + list(self.pick.parameters())
        )
        if self.readout is not None:
            params += list(self.readout.parameters())
        self._params = params
        self.local_trainer = LocalEligibilityTrainer(params, lam=float(self.config.get("lam", 0.9)), lr=float(self.config.get("lr", 0.01)))
        self.bptt_trainer = BPTTTrainer(params, lr=float(self.config.get("lr", 0.01)), momentum=0.9, clip=1.0)

        self.cache: Optional[Cache] = None
        cache_dir = self.config.get("cache_dir")
        if cache_dir:
            self.cache = Cache(cache_dir)
        self.slots = SlotTable()
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None

        self.h = self.engine.zero_state()
        # bounded causal history for the attention read-outs (A1-ATT/A1-MA only; plain A1 never
        # populates these — see _advance_steps): every low-level REAL committed step's hidden
        # state and A1-MA's token id (PREREG §4.1: "over its own last 256 steps").
        self.hist_h: collections.deque = collections.deque(maxlen=att_window if self.attention_mode else 1)
        self.hist_tokens: collections.deque = collections.deque(maxlen=att_window if self.attention_mode else 1)

        self._pending: Dict[int, Dict[str, Any]] = {}
        self._ring: collections.deque = collections.deque(maxlen=RING_CAPACITY)
        self._arrival_id = 0
        self._sleep_index = 0
        self._step_count = 0
        self._arrival_started_at = 0
        self.engine.start_arrival(0)  # D-earlier (engine.py's GrowthBudget.reset_arrival RAISED item):
        # the implicit "arrival 0" stand-in for the missing pre-L1 ARRIVAL row (RAISED to the seat).

        self._world_err_hist = RunningQuantile()
        self._answer_conf_hist = RunningQuantile()

        self._events = 0
        self._ms = 0.0

    # ================================================================================= encoding helpers
    def _require_encoder(self) -> StepEncoder:
        if self.encoder is None:
            raise RuntimeError("ArmA1 constructed without config['cache_dir'] — cannot encode any row")
        return self.encoder

    # ================================================================================= fit_event
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        kind = row["kind"]
        if kind == "TEACH":
            self._fit_teach(row)
        elif kind == "ASK":
            self._fit_ask_world_event(row)
        elif kind == "FEEDBACK":
            self._fit_feedback(row, valence)
        elif kind == "ARRIVAL":
            self._arrival_id += 1
            self._arrival_started_at = self._step_count
            self.engine.start_arrival(self._step_count)
        elif kind in ("TEST_BEGIN", "TEST_END"):
            pass  # no learning signal; the harness never calls fit_event for these anyway
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    def _advance_steps(self, steps: List[torch.Tensor], detach_between: bool) -> torch.Tensor:
        """Advance self.h through `steps`, IN PLACE, learning as it goes via the awake rule.
        Returns the final h. This is the ONLY place self.h and the real parameters change."""
        loss_acc = torch.zeros(())
        h = self.h
        n = len(steps)
        for i, x in enumerate(steps):
            h_next = self.engine.step(x, h)
            if self.attention_mode:
                # the REAL committed history (D-earlier: attention's causal window is over
                # actually-lived steps, never the answer()/feedback peeks' own transient ones).
                self.hist_h.append(h_next.detach())
                self.hist_tokens.append(token_id_of_step(x))
            if i + 1 < n:
                pred = self.world(h_next, active_h=self.engine.active)
                nxt = steps[i + 1]
                target_glance = nxt[:GLANCE_DIM] if float(nxt[:GLANCE_DIM].abs().sum()) > 0 else None
                letter_block = nxt[GLANCE_DIM + GLANCE_IDX_DIM : GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM]
                target_letter = torch.argmax(letter_block) if float(letter_block.abs().sum()) > 0 else None
                kind_block = nxt[-KIND_DIM:]
                target_kind = torch.argmax(kind_block)
                step_loss = WorldHead.loss(pred, target_glance=target_glance, target_letter=target_letter, target_kind=target_kind)
                loss_acc = loss_acc + step_loss
                self.engine.observe_world_error(float(step_loss.detach()), self._step_count, self._arrival_started_at)
                if self.awake_mode == "local":
                    self.local_trainer.step(step_loss, valence=1.0)
                    h_next = h_next.detach()
                    if self.growable:
                        self.engine.maybe_grow(self._step_count, self._arrival_started_at)
            self._step_count += 1
            h = h_next
        if self.awake_mode == "bptt" and n > 1:
            self.bptt_trainer.step(loss_acc)
            h = h.detach()
            if self.growable:
                self.engine.maybe_grow(self._step_count, self._arrival_started_at)
        self.h = h.detach()
        return self.h

    def _fit_teach(self, row: Mapping[str, Any]) -> None:
        enc = self._require_encoder()
        steps = enc.teach_steps(row["payload"])
        self._advance_steps(steps, detach_between=(self.awake_mode == "local"))
        self._ring.append({"row": dict(row), "arrival_id": self._arrival_id})

    def _fit_ask_world_event(self, row: Mapping[str, Any]) -> None:
        # D16: the REAL commit — reprocesses the same steps `answer()` peeked at, this time
        # advancing self.h for real.
        enc = self._require_encoder()
        steps = enc.ask_steps(row["payload"])
        self._advance_steps(steps, detach_between=(self.awake_mode == "local"))
        self._ring.append({"row": dict(row), "arrival_id": self._arrival_id})

    def _query_state_fresh(self, entry: Dict[str, Any]):
        """Rebuild the query state (and, for PICK, every candidate's score) from the RAW
        materials `_answer_impl` stashed (h_start, the ask's own steps, candidate rows) using
        WHATEVER PARAMETERS ARE CURRENT — a brand new autograd graph every call. This is the
        fix for a real bug this file's own test caught (see the module's D16 note and the
        commit message): retaining `answer()`'s ORIGINAL graph and backing through it later,
        after `fit_event(ask_row)` had already run its own in-place parameter update on the
        SAME tensors that graph referenced, raised PyTorch's own version-counter error
        ('modified by an inplace operation') — the graph was stale the instant fit_event ran,
        which HarnessContract.training_ask does UNCONDITIONALLY, immediately after `answer`.
        Recomputing fresh here means there is never a stale graph to protect: the number this
        produces reflects the CURRENT weights on the SAME scenario, which is what an on-policy
        credit assignment wants anyway."""
        h = entry["h_start"]
        for x in entry["ask_steps"]:
            h = self.engine.step(x, h)
        active_h = entry["active_h_at_ask"]
        h_for_heads = h
        if self.attention_mode == "att":
            hist = entry["hist_h"] + [h]
            ro = self.readout(h, torch.stack(hist), active_h=active_h)
            h_for_heads = torch.cat([h, ro])
        elif self.attention_mode == "ma":
            hist = entry["hist_h"] + [h]
            ids = torch.tensor(entry["hist_tokens"] + [0])
            ro = self.readout.forward_tokens(h, torch.stack(hist), ids, active_h=active_h)
            h_for_heads = torch.cat([h, ro])
        family = entry["answer_kind"]
        if family == "NAME":
            return self.names(h_for_heads, active_h=entry["head_active_h"])
        if family == "YESNO":
            return self.yesno(h_for_heads, active_h=entry["head_active_h"])
        if family == "PICK":
            scores = []
            for cr in entry["candidate_rows"]:
                cand_steps = self.encoder.candidate_steps(int(cr))
                hc = h
                for x in cand_steps:
                    hc = self.engine.step(x, hc)
                scores.append(self.pick.score(h, hc, active_h=active_h))
            return torch.stack(scores) if scores else torch.zeros(0)
        raise AssertionError(f"unknown answer_kind family {family!r}")

    def _fit_feedback(self, row: Mapping[str, Any], valence: Optional[str]) -> None:
        p = row["payload"]
        ask_seq = int(p["ask_seq"])
        entry = self._pending.pop(ask_seq, None)
        if entry is None:
            return  # a FEEDBACK for an ask we never held (e.g. constructed mid-tape) — nothing to reinforce
        right = p["right"]
        family = entry["answer_kind"]
        given_idx = entry.get("given_index")
        if family == "NAME":
            if right not in self.names.names:
                return  # a name never heard cannot be a target; nothing to reinforce (D17)
            target_idx = self.names.names.index(right)
        elif family == "YESNO":
            target_idx = 1 if right == "YES" else 0
        elif family == "PICK":
            target_idx = int(right)
        else:
            return
        logits = self._query_state_fresh(entry)
        if logits.numel() == 0 or target_idx >= logits.shape[-1]:
            return
        loss = F.cross_entropy(logits.unsqueeze(0), torch.tensor([target_idx]))
        if valence == VALENCE_NO and given_idx is not None and given_idx != target_idx and given_idx < logits.shape[-1]:
            # D17: an explicit third term pushing the WRONGLY GIVEN logit down, beyond what
            # pushing the right one up already implies in an N-way softmax.
            loss = loss + torch.clamp(logits[given_idx], min=-10.0)
        if self.awake_mode == "local":
            self.local_trainer.step(loss, valence=1.0)
        else:
            self.bptt_trainer.step(loss)

    # ================================================================================= answer (D15)
    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            return self._answer_impl(ask_row, learn)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def _answer_impl(self, ask_row: Mapping[str, Any], learn: bool) -> Answer:
        enc = self._require_encoder()
        p = ask_row["payload"]
        family = p["answer_kind"]
        with torch.no_grad():  # D15: the DECISION never needs a graph; see _query_state_fresh
            h_start = self.h.detach().clone()
            steps = enc.ask_steps(p)
            h = h_start
            for x in steps:
                h = self.engine.step(x, h)
            active_h = self.engine.active
            head_active_h = self.head_hmax if self.attention_mode else active_h
            hist_h_snapshot = list(self.hist_h)
            hist_tokens_snapshot = list(self.hist_tokens)
            h_for_heads = h
            if self.attention_mode == "att":
                ro = self.readout(h, torch.stack(hist_h_snapshot + [h]), active_h=active_h)
                h_for_heads = torch.cat([h, ro])
            elif self.attention_mode == "ma":
                ids = torch.tensor(hist_tokens_snapshot + [0])
                ro = self.readout.forward_tokens(h, torch.stack(hist_h_snapshot + [h]), ids, active_h=active_h)
                h_for_heads = torch.cat([h, ro])

            entry: Dict[str, Any] = {
                "answer_kind": family, "h_start": h_start, "ask_steps": steps,
                "active_h_at_ask": active_h, "head_active_h": head_active_h,
                "hist_h": hist_h_snapshot, "hist_tokens": hist_tokens_snapshot,
            }
            ans: Answer

            if family == "NAME":
                if not self.names.names:
                    ans = Answer(kind=AnswerKind.UNKNOWN)
                else:
                    logits = self.names(h_for_heads, active_h=head_active_h)
                    probs = torch.softmax(logits, dim=-1)
                    conf = float(probs.max())
                    given_idx = int(logits.argmax())
                    novelty = float(self._recent_world_error())
                    forced = {"kind": AnswerKind.NAME, "value": self.names.names[given_idx]}   # R24: the would-be answer, for FORCED-ANSWER
                    if self._world_err_hist.hist and novelty > self._world_err_hist.quantile(0.95, default=float("inf")):
                        ans = Answer(kind=AnswerKind.UNKNOWN, raw={"conf": conf, "novelty": novelty, "forced": forced})
                    elif self._answer_conf_hist.hist and conf < self._answer_conf_hist.quantile(0.05, default=0.0):
                        ans = Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": forced})
                    else:
                        ans = Answer(kind=AnswerKind.NAME, value=self.names.names[given_idx], raw={"conf": conf})
                    entry["given_index"] = given_idx
                    if learn:
                        self._answer_conf_hist.observe(conf)
                        self._world_err_hist.observe(novelty)
            elif family == "YESNO":
                logits = self.yesno(h_for_heads, active_h=head_active_h)
                probs = torch.softmax(logits, dim=-1)
                conf = float(probs.max())
                given_idx = int(logits.argmax())
                if self._answer_conf_hist.hist and conf < self._answer_conf_hist.quantile(0.05, default=0.0):
                    ans = Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": {"kind": (AnswerKind.YES if given_idx == 1 else AnswerKind.NO), "value": None}})
                else:
                    ans = Answer(kind=(AnswerKind.YES if given_idx == 1 else AnswerKind.NO), raw={"conf": conf})
                entry["given_index"] = given_idx
                if learn:
                    self._answer_conf_hist.observe(conf)
            elif family == "PICK":
                cand_rows = list(p["candidate_rows"] or [])
                entry["candidate_rows"] = cand_rows
                scores = []
                for cr in cand_rows:
                    hc = h
                    for x in enc.candidate_steps(int(cr)):
                        hc = self.engine.step(x, hc)
                    scores.append(self.pick.score(h, hc, active_h=active_h))
                scores_t = torch.stack(scores) if scores else torch.zeros(0)
                if scores_t.numel() == 0:
                    ans = Answer(kind=AnswerKind.NOTHING)
                else:
                    probs = torch.softmax(scores_t, dim=-1)
                    conf = float(probs.max())
                    given_idx = int(scores_t.argmax())
                    if self._answer_conf_hist.hist and conf < self._answer_conf_hist.quantile(0.05, default=0.0):
                        ans = Answer(kind=AnswerKind.NOTHING, raw={"conf": conf, "forced": {"kind": AnswerKind.PICK, "value": given_idx}})
                    else:
                        ans = Answer(kind=AnswerKind.PICK, value=given_idx, raw={"conf": conf})
                    entry["given_index"] = given_idx
                    if learn:
                        self._answer_conf_hist.observe(conf)
            else:
                ans = Answer(kind=AnswerKind.NOTHING)

        if learn and ans.kind not in (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT):
            self._pending[int(ask_row["seq"])] = entry
        return ans

    def _recent_world_error(self) -> float:
        return self.engine._err_window[-1] if self.engine._err_window else 0.0

    # ================================================================================= sleep
    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        if self.sleep_mode != "none" and len(self._ring) > 0 and self.encoder is not None:
            self._replay(steps)
        self._sleep_index += 1
        self._events += int(steps)
        self._ms += (time.perf_counter() - t0) * 1000.0

    def _replay(self, steps: int, R: int = 64, W: int = 32) -> None:
        ring = list(self._ring)
        cur_arrival = self._arrival_id
        latest = [i for i, e in enumerate(ring) if e["arrival_id"] == cur_arrival]
        older = [i for i, e in enumerate(ring) if e["arrival_id"] != cur_arrival]
        gen = new_generator(self.seed, "replay", self._sleep_index)
        n_latest = R // 2
        n_older = R - n_latest
        picks: List[int] = []
        if latest:
            picks += [latest[int(torch.randint(0, len(latest), (1,), generator=gen))] for _ in range(n_latest)]
        if older:
            picks += [older[int(torch.randint(0, len(older), (1,), generator=gen))] for _ in range(n_older)]
        if not picks:
            return
        for center in picks:
            lo = max(0, center - W // 2)
            window_rows = ring[lo : lo + W] or ring[lo : lo + 1]
            step_seq: List[torch.Tensor] = []
            for e in window_rows:
                r = e["row"]
                if r["kind"] == "TEACH":
                    step_seq.extend(self.encoder.teach_steps(r["payload"]))
                elif r["kind"] == "ASK":
                    step_seq.extend(self.encoder.ask_steps(r["payload"]))
            if len(step_seq) < 2:
                continue
            h = self.h.detach().clone()
            loss_acc = torch.zeros(())
            for i in range(len(step_seq) - 1):
                h = self.engine.step(step_seq[i], h)
                pred = self.world(h, active_h=self.engine.active)
                nxt = step_seq[i + 1]
                tg = nxt[:GLANCE_DIM] if float(nxt[:GLANCE_DIM].abs().sum()) > 0 else None
                lb = nxt[GLANCE_DIM + GLANCE_IDX_DIM : GLANCE_DIM + GLANCE_IDX_DIM + LETTER_DIM]
                tl = torch.argmax(lb) if float(lb.abs().sum()) > 0 else None
                loss_acc = loss_acc + WorldHead.loss(pred, target_glance=tg, target_letter=tl, target_kind=torch.argmax(nxt[-KIND_DIM:]))
            if self.sleep_mode == "local":
                self.local_trainer.step(loss_acc, valence=1.0)
            else:
                self.bptt_trainer.step(loss_acc)

    # ================================================================================= identity
    def state_sha(self) -> str:
        parts = [self.engine.state_sha_bytes()]
        for mod in (self.world, self.names, self.yesno, self.pick):
            for name, t in sorted(mod.state_dict().items()):
                parts.append(f"{mod.__class__.__name__}.{name}".encode())
                parts.append(t.detach().contiguous().numpy().tobytes())
        if self.readout is not None:
            for name, t in sorted(self.readout.state_dict().items()):
                parts.append(f"readout.{name}".encode())
                parts.append(t.detach().contiguous().numpy().tobytes())
        parts.append(b"names=" + canonical_json(self.names.names).encode())
        parts.append(b"slots=" + self.slots.state_bytes())
        parts.append(f"h={self.h.detach().numpy().tobytes()}".encode())
        if self.attention_mode:
            parts.append(b"hist_tokens=" + canonical_json(list(self.hist_tokens)).encode())
            parts.append(b"hist_h=" + b"".join(t.detach().numpy().tobytes() for t in self.hist_h))
        parts.append(canonical_json({"world_err": self._world_err_hist.to_list(), "conf": self._answer_conf_hist.to_list()}).encode())
        import hashlib

        return hashlib.sha256(b"|".join(parts)).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "engine": self.engine.state_dict(),
                "engine_extra": self.engine.extra_state(),
                "world": self.world.state_dict(),
                "names": self.names.state_dict(),
                "names_list": self.names.names,
                "names_n_out": self.names.n_out,
                "yesno": self.yesno.state_dict(),
                "pick": self.pick.state_dict(),
                "readout": self.readout.state_dict() if self.readout is not None else None,
                "h": self.h,
                "hist_h": list(self.hist_h),
                "hist_tokens": list(self.hist_tokens),
                "slots": self.slots.to_dict(),
                "ring": list(self._ring),
                "arrival_id": self._arrival_id,
                "sleep_index": self._sleep_index,
                "step_count": self._step_count,
                "arrival_started_at": self._arrival_started_at,
                "world_err_hist": self._world_err_hist.to_list(),
                "answer_conf_hist": self._answer_conf_hist.to_list(),
                "events": self._events,
                "ms": self._ms,
                "local_trainer": self.local_trainer.state_dict(),
                "bptt_trainer": self.bptt_trainer.state_dict(),
                # `_pending` is NOT snapshotted: B1-PREREG.md's L4 schedule always pairs a
                # training ASK with its own FEEDBACK adjacently (§2.7: "each ask followed by
                # its FEEDBACK"), so nothing should be pending across a SLEEP boundary in the
                # real tape; if it ever is, a resumed run drops that one credit-assignment
                # silently rather than crashing — RAISED in docs/briefs/B1-BUILDER3-REPORT.md
                # as a known gap rather than hidden.
            },
            path / "state.pt",
        )

    def load(self, path: Union[str, Path]) -> None:
        # weights_only=False is deliberate: this snapshot carries plain Python objects beside
        # tensors (the names list, the replay ring's raw tape-row dicts, plain ints/floats) that
        # weights_only=True's restricted unpickler would refuse. The file is never untrusted
        # input — it is written by THIS SAME CLASS's snapshot() under the harness's own run
        # directory (brain.protocol.Arm's own contract: "an arm never writes outside" its
        # run_dir) and read back only by itself or its own conformance/identity tests, never
        # from a network or user-supplied path.
        d = torch.load(Path(path) / "state.pt", weights_only=False)
        self.engine.load_state_dict(d["engine"])
        self.engine.load_extra_state(d["engine_extra"])
        self.world.load_state_dict(d["world"])
        self.names.load_state_dict(d["names"])
        self.names.names = list(d["names_list"])
        self.names.n_out = d["names_n_out"]
        self.yesno.load_state_dict(d["yesno"])
        self.pick.load_state_dict(d["pick"])
        if self.readout is not None and d["readout"] is not None:
            self.readout.load_state_dict(d["readout"])
        self.h = d["h"]
        att_window = int(self.config.get("att_window", 256))
        self.hist_h = collections.deque(d.get("hist_h", []), maxlen=att_window if self.attention_mode else 1)
        self.hist_tokens = collections.deque(d.get("hist_tokens", []), maxlen=att_window if self.attention_mode else 1)
        self.slots = SlotTable.from_dict(d["slots"])
        self.encoder = StepEncoder(self.cache, self.slots) if self.cache is not None else None
        self._ring = collections.deque(d["ring"], maxlen=RING_CAPACITY)
        self._arrival_id = d["arrival_id"]
        self._sleep_index = d["sleep_index"]
        self._step_count = d["step_count"]
        self._arrival_started_at = d["arrival_started_at"]
        self._world_err_hist.load_list(d["world_err_hist"], maxlen=2000)
        self._answer_conf_hist.load_list(d["answer_conf_hist"], maxlen=2000)
        self._events = d["events"]
        self._ms = d["ms"]
        self.local_trainer.load_state_dict(d["local_trainer"])
        self.bptt_trainer.load_state_dict(d["bptt_trainer"])
        self._pending = {}

    def size(self) -> Dict[str, Any]:
        """The arm's size for the record (R27; §4.1's matched-parameter twins solve against `n_params_active`):
        the ALIVE hidden width, the declared ceiling, the names heard, and the total parameter count at the
        alive width by the engine's own formula (`a1_total_params`) — never a raw `numel()` over HMAX-wide
        tensors, whose zero columns are not parameters the arm uses."""
        from brain.arms.soft.engine import a1_total_params
        from brain.arms.soft.steps import STEP_DIM, GLANCE_DIM, LETTER_DIM, KIND_DIM
        h = int(self.engine.active)
        n_names = len(self.names.names)
        return {"h_alive": h, "hmax": int(self.engine.hmax), "h0": int(getattr(self.engine, "h0", h)), "n_names": n_names,
                "n_params_active": int(a1_total_params(STEP_DIM, h, GLANCE_DIM, LETTER_DIM, KIND_DIM, n_names)),
                "variant": self.config.get("variant", "A1")}

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}
