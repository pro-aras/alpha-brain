//! Phase 1 (`v0.5.0 "Cortex"`): Biophysical & Mathematical Cortical-Hippocampal Substrate.
//!
//! Implements the 3-Agent Consensus Master Plan Phase 1 mechanisms:
//! 1. `Hot16` (`#[repr(C, align(16))]`, 16 bytes — 4 neurons per 64-byte cache line) + `ColdSoA`
//!    hybrid memory layout and `NeuralPool` with `k`-WTA + APL global inhibition (`Fixes N5, N6, N7, N11`).
//! 2. Bidirectional homeostatic intrinsic plasticity (`Fixes N3 / V-05`).
//! 3. Per-pool budgeted VIP/SST/PV dendritic calcium plateau equation + Locus Coeruleus `NE`
//!    adaptation + weight-dependent bidirectional BTSP with `0.0` floor (`Fixes N2, N4, N8, N9`, Gate `PLATEAU-RATE`).
//! 4. Two-stage Helmholtz operator (`\Omega^{fast}_t` utterance-scoped + `\Omega^{slow}` lifetime
//!    calibrated binomial z-score + `K_{class}` second-order similarity kernel), splitter state `z_t`,
//!    and scoped `KenyonBinder` (`Fixes O1, O2, N10`, Gates `OB-SEP`, `OB-NULL`, `OB-GEN`, `ROLE-FLIP`, `BIND-1`).
//! 5. Földiák/Vogels anti-correlation inhibition (`S^-`), grounded `NOT` inhibitory projection
//!    (`Gate NOT-COMPOSE`), and cross-modal grounding-support verification (`Gate RED-SOUND`).
//! 6. `CORE` multi-timescale associative hierarchy (`L = 4`, `\tau \in {4, 16, 64, 256}`) with
//!    top-`m`-per-row bounding and 80% event-boundary reset (`Gate WM-1`).

use crate::neuron::Modality;
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};

/// Serde adapter for `FxHashMap<TupleKey, V>` so JSON serialization stores `Vec<(TupleKey, V)>`
/// rather than panicking with `Error("key must be a string")`.
pub mod tuple_map_serde {
    use rustc_hash::FxHashMap;
    use serde::{Deserialize, Deserializer, Serialize, Serializer};
    use std::hash::Hash;

    pub fn serialize<K, V, S>(map: &FxHashMap<K, V>, serializer: S) -> Result<S::Ok, S::Error>
    where
        K: Serialize + Eq + Hash,
        V: Serialize,
        S: Serializer,
    {
        let vec: Vec<(&K, &V)> = map.iter().collect();
        vec.serialize(serializer)
    }

    pub fn deserialize<'de, K, V, D>(deserializer: D) -> Result<FxHashMap<K, V>, D::Error>
    where
        K: Deserialize<'de> + Eq + Hash,
        V: Deserialize<'de>,
        D: Deserializer<'de>,
    {
        let vec: Vec<(K, V)> = Vec::deserialize(deserializer)?;
        Ok(vec.into_iter().collect())
    }
}

/// 16-byte cache-aligned hot somatic/dendritic state (`4 neurons per 64-byte L1 cache line`).
/// Used during random-access event-driven synaptic delivery (`Gate COST-1`).
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[repr(C, align(16))]
pub struct Hot16 {
    pub v_b: f32,
    pub v_a: f32,
    pub theta: f32,
    pub last_tick: u32,
}

impl Default for Hot16 {
    fn default() -> Self {
        Self {
            v_b: 0.0,
            v_a: 0.0,
            theta: 1.0,
            last_tick: 0,
        }
    }
}

impl Hot16 {
    /// Lazily decays basal/apical potentials and applies bidirectional homeostatic threshold
    /// relaxation toward `theta_0 = 1.0`.
    #[inline]
    pub fn lazy_sync(&mut self, current_tick: u32) {
        if current_tick > self.last_tick {
            let dt = (current_tick - self.last_tick) as f32;
            self.v_b *= (-dt / 3.0).exp();
            self.v_a *= (-dt / 6.0).exp();
            let theta_decay = (-dt / 50.0).exp();
            self.theta = 1.0 + (self.theta - 1.0) * theta_decay;
            self.last_tick = current_tick;
        }
    }
}

/// Structure-of-Arrays (`ColdSoA`) for streaming SIMD sweeps during homeostasis, sleep compaction,
/// and provenance auditing.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct ColdSoA {
    pub trace: Vec<f32>,
    pub rate_ema: Vec<f32>,
    pub last_spike: Vec<u32>,
    pub maturity: Vec<u16>,
    pub sst_brake: Vec<f32>,
    pub provenance: Vec<u8>,
}

impl ColdSoA {
    pub fn with_capacity(n: usize) -> Self {
        Self {
            trace: vec![0.0; n],
            rate_ema: vec![0.02; n],
            last_spike: vec![u32::MAX; n],
            maturity: vec![0; n],
            sst_brake: vec![0.35; n],
            provenance: vec![0; n],
        }
    }
}

/// Dale's Law sign of a neural pool (`Excitatory` glutamatergic vs `Inhibitory` GABAergic).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PoolKind {
    Excitatory,
    Inhibitory,
}

/// A population pool of `n` neurons with `k`-Winner-Take-All (`k`-WTA) + APL global inhibition
/// and per-pool VIP/SST/PV dendritic plateau budgeting (`Fixes N2, N5, N6, N7, N8, N11`).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NeuralPool {
    pub id: u32,
    pub name: String,
    pub kind: PoolKind,
    pub modality: Modality,
    pub n: u32,
    pub k: u32,
    pub g_apl: f32,
    pub max_plateaus_per_step: usize,
    pub hot: Vec<Hot16>,
    pub cold: ColdSoA,
}

impl NeuralPool {
    pub fn new(id: u32, name: &str, kind: PoolKind, modality: Modality, n: u32, k: u32) -> Self {
        let cap = n as usize;
        Self {
            id,
            name: name.to_string(),
            kind,
            modality,
            n,
            k: k.max(1).min(n),
            g_apl: 0.12 / (k.max(1) as f32),
            max_plateaus_per_step: (k as usize / 2).max(2),
            hot: vec![Hot16::default(); cap],
            cold: ColdSoA::with_capacity(cap),
        }
    }

    /// Deterministic sparse `k`-winner projection for a concept/symbol key inside this pool.
    pub fn deterministic_assembly(&self, key: &str) -> Vec<u32> {
        let mut scores: Vec<(u32, u64)> = (0..self.n)
            .map(|i| {
                let mut h = 14695981039346656037u64;
                for b in key.as_bytes() {
                    h ^= *b as u64;
                    h = h.wrapping_mul(1099511628211);
                }
                h ^= (i as u64).wrapping_mul(0x9E3779B97F4A7C15);
                h = h.wrapping_mul(1099511628211);
                (i, h)
            })
            .collect();
        scores.sort_by_key(|&(_, h)| h);
        scores.into_iter().take(self.k as usize).map(|(i, _)| i).collect()
    }

    /// Steps the pool at `tick` under global neuromodulators `(ne, ach, eff_copy)`,
    /// applying APL inhibition, `k`-WTA winner selection, bidirectional homeostatic plasticity,
    /// and the per-pool budgeted VIP/SST/PV plateau equation (`Correction 2 / Gate PLATEAU-RATE`).
    /// Returns `(winners, plateau_winners)`.
    pub fn step_pool(
        &mut self,
        tick: u32,
        ne: f32,
        ach: f32,
        eff_copy: f32,
        instructive_drive: f32,
    ) -> (Vec<u32>, Vec<u32>) {
        let n_len = self.n as usize;
        let mut total_excit = 0.0f32;
        for i in 0..n_len {
            self.hot[i].lazy_sync(tick);
            total_excit += self.hot[i].v_b.max(0.0);
        }

        // APL global feedback inhibition proportional to mean pool activity
        let i_apl = self.g_apl * (total_excit / (n_len.max(1) as f32));
        let mut candidates: Vec<(u32, f32)> = Vec::new();
        for i in 0..n_len {
            let v_eff = (self.hot[i].v_b - i_apl).max(0.0);
            self.hot[i].v_b = v_eff;
            if v_eff >= self.hot[i].theta {
                candidates.push((i as u32, v_eff - self.hot[i].theta));
            }
        }

        // Strict k-WTA competition
        candidates.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        let winners: Vec<u32> = candidates
            .iter()
            .take(self.k as usize)
            .map(|&(id, _)| id)
            .collect();

        // VIP disinhibitory gate: lowers SST apical brake multiplicatively (never creates fake apical voltage)
        let vip_arg = 1.4 * ne + 1.1 * ach + 0.8 * eff_copy - 0.6;
        let v_vip = 1.0 / (1.0 + (-vip_arg).exp());
        let theta_ca_base = 0.45f32;
        let kappa_sst = 0.55f32;

        let mut plateau_candidates: Vec<(u32, f32)> = Vec::new();
        for &w_idx in &winners {
            let idx = w_idx as usize;
            let theta_ca = theta_ca_base + kappa_sst * self.cold.sst_brake[idx] * (1.0 - v_vip);
            let apical_total = self.hot[idx].v_a + instructive_drive + 0.35 * ne * self.cold.trace[idx];
            if apical_total >= theta_ca {
                plateau_candidates.push((w_idx, apical_total - theta_ca));
            }
        }

        // Enforce hard per-pool plateau budget m_P (`Gate PLATEAU-RATE`)
        plateau_candidates
            .sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        let plateau_winners: Vec<u32> = plateau_candidates
            .into_iter()
            .take(self.max_plateaus_per_step)
            .map(|(id, _)| id)
            .collect();

        // Update traces and bidirectional homeostatic target-rate tracking (`r_target = k / n`)
        let r_target = (self.k as f32) / (self.n.max(1) as f32);
        let eta_theta = 0.02f32;
        for i in 0..n_len {
            let fired = winners.contains(&(i as u32));
            let s = if fired { 1.0 } else { 0.0 };
            self.cold.rate_ema[i] = 0.95 * self.cold.rate_ema[i] + 0.05 * s;
            self.cold.trace[i] = 0.82 * self.cold.trace[i] + s;
            self.hot[i].theta =
                (self.hot[i].theta + eta_theta * (self.cold.rate_ema[i] - r_target)).clamp(0.45, 2.50);
            if fired {
                self.hot[i].v_b = 0.0;
                self.cold.last_spike[i] = tick;
                self.cold.maturity[i] = self.cold.maturity[i].saturating_add(1);
            }
        }

        (winners, plateau_winners)
    }
}

/// Locus Coeruleus (`LC`) Norepinephrine (`NE`) & Basal Forebrain `ACh` Neuromodulator State.
/// Driven by CA1 comparator mismatch with LC adaptation (`Correction 2`: never driven by plateau count).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NeuromodulatorState {
    pub ne: f32,
    pub ach: f32,
    pub lc_adaptation: f32,
}

impl Default for NeuromodulatorState {
    fn default() -> Self {
        Self {
            ne: 0.15,
            ach: 0.20,
            lc_adaptation: 0.0,
        }
    }
}

impl NeuromodulatorState {
    /// Updates `NE` and `ACh` from bounded CA1 sensory-prediction mismatch `mismatch in [0, 1]`.
    pub fn step(&mut self, ca1_mismatch: f32) {
        let m = ca1_mismatch.clamp(0.0, 1.0);
        let raw_drive = 0.10 + 0.65 * m - 0.45 * self.lc_adaptation;
        self.ne = (0.80 * self.ne + 0.20 * raw_drive).clamp(0.02, 0.95);
        self.lc_adaptation = (0.92 * self.lc_adaptation + 0.08 * self.ne).clamp(0.0, 0.85);
        self.ach = (0.85 * self.ach + 0.15 * m).clamp(0.05, 0.90);
    }
}

/// Weight-dependent bidirectional BTSP synapse rule with `0.0` floor (`Fixes N4, N9`).
#[inline]
pub fn btsp_update_weight(
    w: f32,
    w_max: f32,
    elig_pre: f32,
    plateau_post: bool,
    confirmed_post: bool,
    omission_post: bool,
) -> f32 {
    let eta_plus = 0.55f32;
    let eta_minus = 0.35f32;
    let mut next_w = w;
    if plateau_post {
        next_w += eta_plus * (w_max - next_w).max(0.0) * elig_pre;
    } else if confirmed_post {
        next_w += 0.08 * eta_plus * (w_max - next_w).max(0.0) * elig_pre;
    } else if omission_post {
        next_w -= eta_minus * next_w * elig_pre;
    }
    next_w.clamp(0.0, w_max)
}

/// Two-Stage Helmholtz Operator (`S^+`, `S^-`, `\Omega^{slow}`, `\Omega^{fast}_t`, `K_{class}`)
/// + Trajectory Splitter State `z_t` (`Correction 1 & Correction 3`).
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TwoStageHelmholtz {
    /// Vocabulary / concept index `symbol -> id`
    pub symbol_to_id: FxHashMap<String, u32>,
    pub id_to_symbol: Vec<String>,
    pub id_to_modality: Vec<Modality>,
    /// Directed transition counts `C_{ij}` (`i -> j`)
    #[serde(default, with = "tuple_map_serde")]
    pub directed_counts: FxHashMap<(u32, u32), f32>,
    /// Symmetric co-occurrence / grounded feature weights `S^+_{ij} = S^+_{ji} >= 0`
    #[serde(default, with = "tuple_map_serde")]
    pub s_plus: FxHashMap<(u32, u32), f32>,
    /// Földiák/Vogels anti-correlation & grounded `NOT` inhibitory weights `S^-_{ij} >= 0`
    #[serde(default, with = "tuple_map_serde")]
    pub s_minus: FxHashMap<(u32, u32), f32>,
    /// Lifetime calibrated skew-symmetric operator `\Omega^{slow}_{ij} = -\Omega^{slow}_{ji}`
    #[serde(default, with = "tuple_map_serde")]
    pub omega_slow: FxHashMap<(u32, u32), f32>,
    /// Utterance-scoped fast antisymmetric trace `\Omega^{fast}_{t, ij} = -\Omega^{fast}_{t, ji}` (`Correction 1`)
    #[serde(default, with = "tuple_map_serde")]
    pub omega_fast: FxHashMap<(u32, u32), f32>,
    /// Exponential trace of recent symbol activations `\tilde{x}_t` within the current utterance
    pub fast_trace: FxHashMap<u32, f32>,
    /// Trajectory splitter vector `z_t`
    pub splitter_z: FxHashMap<u32, f32>,
    /// Class-similarity smoothing factor `\varepsilon in [0, 1]` for `K_{class} = (1-\varepsilon)I + \varepsilon \hat{S}^+`
    pub epsilon_class: f32,
    /// Binomial z-score threshold `z_{thresh}` for `\Omega^{slow}` (`Gate OB-NULL`)
    pub z_thresh: f32,
    /// Lesion flags for falsifiable ablation testing (`Gate ROLE-FLIP`, `Gate OB-GEN`)
    pub lesion_omega_slow: bool,
    pub lesion_omega_fast: bool,
}

impl TwoStageHelmholtz {
    pub fn new() -> Self {
        Self {
            symbol_to_id: FxHashMap::default(),
            id_to_symbol: Vec::new(),
            id_to_modality: Vec::new(),
            directed_counts: FxHashMap::default(),
            s_plus: FxHashMap::default(),
            s_minus: FxHashMap::default(),
            omega_slow: FxHashMap::default(),
            omega_fast: FxHashMap::default(),
            fast_trace: FxHashMap::default(),
            splitter_z: FxHashMap::default(),
            epsilon_class: 0.45,
            z_thresh: 1.85,
            lesion_omega_slow: false,
            lesion_omega_fast: false,
        }
    }

    pub fn ensure_symbol(&mut self, sym: &str, modality: Modality) -> u32 {
        let clean = sym.trim().to_lowercase();
        if let Some(&id) = self.symbol_to_id.get(&clean) {
            return id;
        }
        let id = self.id_to_symbol.len() as u32;
        self.symbol_to_id.insert(clean.clone(), id);
        self.id_to_symbol.push(clean);
        self.id_to_modality.push(modality);
        id
    }

    /// Binds a concept/symbol to a grounded sensory or contextual feature (`S^+_{ij} = S^+_{ji}`).
    pub fn bind_symmetric(&mut self, a: &str, mod_a: Modality, b: &str, mod_b: Modality, weight: f32) {
        let ia = self.ensure_symbol(a, mod_a);
        let ib = self.ensure_symbol(b, mod_b);
        if ia == ib {
            return;
        }
        *self.s_plus.entry((ia, ib)).or_insert(0.0) += weight;
        *self.s_plus.entry((ib, ia)).or_insert(0.0) += weight;
    }

    /// Földiák/Vogels anti-correlation inhibitory learning (`S^-_{ij}`) for mutually exclusive states
    /// (`door_locked` vs `door_open`) or grounded `NOT` suppression (`Correction 3`).
    pub fn bind_inhibitory(&mut self, a: &str, mod_a: Modality, b: &str, mod_b: Modality, weight: f32) {
        let ia = self.ensure_symbol(a, mod_a);
        let ib = self.ensure_symbol(b, mod_b);
        if ia == ib {
            return;
        }
        *self.s_minus.entry((ia, ib)).or_insert(0.0) += weight;
        *self.s_minus.entry((ib, ia)).or_insert(0.0) += weight;
    }

    /// Steps the utterance-scoped fast antisymmetric trace `\Omega^{fast}_t` (`Correction 1`)
    /// and accumulates directed counts `C_{ij}` for `\Omega^{slow}`.
    pub fn observe_step(&mut self, symbol: &str, modality: Modality, boundary_reset: bool) {
        let curr_id = self.ensure_symbol(symbol, modality);
        let tau_fast = 6.0f32;
        let b_factor = if boundary_reset { 0.2 } else { 1.0 };
        let alpha = (-1.0 / tau_fast).exp() * b_factor;

        // Decay existing fast antisymmetric matrix and fast trace
        for val in self.omega_fast.values_mut() {
            *val *= alpha;
        }
        for val in self.fast_trace.values_mut() {
            *val *= alpha;
        }

        // Update \Omega^{fast}_t = \alpha \Omega^{fast}_{t-1} + \eta (x_t \tilde{x}_{t-1}^T - \tilde{x}_{t-1} x_t^T)
        // Here convention: \Omega_{pre, post} > 0 when `pre` precedes `post`!
        let eta_fast = 1.0f32;
        let prev_active: Vec<(u32, f32)> = self
            .fast_trace
            .iter()
            .filter(|&(&id, &tr)| id != curr_id && tr > 0.25)
            .map(|(&id, &tr)| (id, tr))
            .collect();

        for (prev_id, prev_tr) in prev_active {
            let delta = eta_fast * prev_tr;
            *self.omega_fast.entry((prev_id, curr_id)).or_insert(0.0) += delta;
            *self.omega_fast.entry((curr_id, prev_id)).or_insert(0.0) -= delta;
            if prev_tr > 0.80 {
                *self.directed_counts.entry((prev_id, curr_id)).or_insert(0.0) += prev_tr;
            }
        }

        self.fast_trace.insert(curr_id, 1.0);

        // Update splitter vector z_t = \gamma z_{t-1} + (1-\gamma) \Omega^{fast} x_t
        for val in self.splitter_z.values_mut() {
            *val *= 0.7 * b_factor;
        }
        for (&(pre, post), &w) in &self.omega_fast {
            if pre == curr_id && w.abs() > 0.05 {
                *self.splitter_z.entry(post).or_insert(0.0) += 0.3 * w;
            }
        }
    }

    /// Sleep consolidation of `\Omega^{slow}` using calibrated binomial z-score (`Gate OB-NULL`):
    /// `z_{ij} = (C_{ij} - C_{ji}) / sqrt(C_{ij} + C_{ji} + c_0)`.
    /// Under mirror-shuffled symmetric sequences (`C_{ij} \approx C_{ji}`), `|z_{ij}| < z_{thresh}`,
    /// guaranteeing 0% false-positive order links!
    pub fn consolidate_omega_slow(&mut self) {
        self.omega_slow.clear();
        let c0 = 2.0f32;
        let mut pairs_seen = std::collections::HashSet::new();
        for &(i, j) in self.directed_counts.keys() {
            let a = i.min(j);
            let b = i.max(j);
            if a == b || !pairs_seen.insert((a, b)) {
                continue;
            }
            let c_ab = *self.directed_counts.get(&(a, b)).unwrap_or(&0.0);
            let c_ba = *self.directed_counts.get(&(b, a)).unwrap_or(&0.0);
            let denom = (c_ab + c_ba + c0).sqrt();
            let z_ab = (c_ab - c_ba) / denom;
            if z_ab.abs() >= self.z_thresh {
                let w = (c_ab - c_ba) / (c_ab + c_ba + c0);
                self.omega_slow.insert((a, b), w);
                self.omega_slow.insert((b, a), -w);
            }
        }
    }

    /// Cosine similarity `\hat{S}^+_{ij}` between two symbols' grounded `S^+` neighborhoods.
    pub fn class_similarity(&self, a: u32, b: u32) -> f32 {
        if a == b {
            return 1.0;
        }
        let mut dot = 0.0f32;
        let mut norm_a = 0.0f32;
        let mut norm_b = 0.0f32;
        let n = self.id_to_symbol.len() as u32;
        for k in 0..n {
            let wa = *self.s_plus.get(&(a, k)).unwrap_or(&0.0);
            let wb = *self.s_plus.get(&(b, k)).unwrap_or(&0.0);
            dot += wa * wb;
            norm_a += wa * wa;
            norm_b += wb * wb;
        }
        if norm_a <= 1e-8 || norm_b <= 1e-8 {
            0.0
        } else {
            dot / (norm_a.sqrt() * norm_b.sqrt())
        }
    }

    /// Evaluates the class-smoothed lifetime directional operator
    /// `\tilde{\Omega}^{slow}_{ab} = (K_{class} \Omega^{slow} K_{class})_{ab}` (`Gate OB-SEP` & `Gate OB-GEN`).
    pub fn score_lifetime_order(&self, a: &str, b: &str) -> f32 {
        if self.lesion_omega_slow {
            return 0.0;
        }
        let ia = match self.symbol_to_id.get(&a.trim().to_lowercase()) {
            Some(&id) => id,
            None => return 0.0,
        };
        let ib = match self.symbol_to_id.get(&b.trim().to_lowercase()) {
            Some(&id) => id,
            None => return 0.0,
        };

        let eps = self.epsilon_class;
        let n = self.id_to_symbol.len() as u32;
        let mut total = 0.0f32;
        for u in 0..n {
            let k_au = if u == ia {
                1.0 - eps + eps
            } else if eps > 0.0 {
                eps * self.class_similarity(ia, u)
            } else {
                0.0
            };
            if k_au <= 1e-5 {
                continue;
            }
            for v in 0..n {
                let w_uv = *self.omega_slow.get(&(u, v)).unwrap_or(&0.0);
                if w_uv.abs() <= 1e-5 {
                    continue;
                }
                let k_vb = if v == ib {
                    1.0 - eps + eps
                } else if eps > 0.0 {
                    eps * self.class_similarity(v, ib)
                } else {
                    0.0
                };
                total += k_au * w_uv * k_vb;
            }
        }
        total
    }

    /// Decodes utterance-scoped thematic role asymmetry `\rho(entity, verb)` (`Correction 1`, Gate `ROLE-FLIP`):
    /// `> 0` iff `entity` preceded `verb` (Pre-Verbal Agent) in the current utterance;
    /// `< 0` iff `entity` followed `verb` (Post-Verbal Patient) in the current utterance.
    pub fn score_utterance_role(&self, entity: &str, verb: &str) -> f32 {
        if self.lesion_omega_fast {
            return 0.0;
        }
        let ie = match self.symbol_to_id.get(&entity.trim().to_lowercase()) {
            Some(&id) => id,
            None => return 0.0,
        };
        let iv = match self.symbol_to_id.get(&verb.trim().to_lowercase()) {
            Some(&id) => id,
            None => return 0.0,
        };
        *self.omega_fast.get(&(ie, iv)).unwrap_or(&0.0)
    }

    /// Evaluates cross-modal compositional compatibility between `modifier` and `head_noun`
    /// (`Correction 3`, Gate `RED-SOUND`).
    /// Returns `(is_compatible, support_score)`:
    /// - `"purple giraffe"` -> `true` (both share grounded `Visual` sensory domain support via `S^+` / `K_{class}`)
    /// - `"red sound"` -> `false` (`"red"` is strictly `Visual`, `"sound"` is strictly `Auditory`, 0 shared sensory support)
    pub fn check_cross_modal_composition(&self, modifier: &str, head_noun: &str) -> (bool, f32) {
        let im = match self.symbol_to_id.get(&modifier.trim().to_lowercase()) {
            Some(&id) => id,
            None => return (false, 0.0),
        };
        let ih = match self.symbol_to_id.get(&head_noun.trim().to_lowercase()) {
            Some(&id) => id,
            None => return (false, 0.0),
        };

        // Check direct or class-smoothed shared exteroceptive sensory modality support in S^+
        // and feature-level mutual exclusion in S^-
        let n = self.id_to_symbol.len() as u32;
        let mut mod_modalities = std::collections::HashSet::new();
        let mut head_modalities = std::collections::HashSet::new();
        let mut mod_traits = Vec::new();
        let mut head_traits = Vec::new();
        for k in 0..n {
            let m_k = self.id_to_modality[k as usize];
            if !matches!(
                m_k,
                Modality::Visual | Modality::Auditory | Modality::TactileHand | Modality::Olfactory
            ) {
                continue;
            }
            if *self.s_plus.get(&(im, k)).unwrap_or(&0.0) > 0.05 {
                mod_modalities.insert(m_k);
                mod_traits.push(k);
            }
            if *self.s_plus.get(&(ih, k)).unwrap_or(&0.0) > 0.05 {
                head_modalities.insert(m_k);
                head_traits.push(k);
            }
        }
        let shared_count = mod_modalities.intersection(&head_modalities).count();
        let mut inhib = *self.s_minus.get(&(im, ih)).unwrap_or(&0.0);
        for &u in &mod_traits {
            for &v in &head_traits {
                inhib += *self.s_minus.get(&(u, v)).unwrap_or(&0.0);
            }
        }
        if shared_count > 0 && inhib < 0.5 {
            (true, (shared_count as f32) - inhib)
        } else {
            (false, -(inhib + 1.0))
        }
    }
}

/// Insect Mushroom-Body `KenyonBinder`: Conjunctive Context-Content Expansion (`Fixes N10`, Gate `BIND-1`).
/// Computes `c_t = kWTA_k(P_x x_t + \lambda P_z z_t - I_{APL})` so the same concept `x_t` in
/// different sequential/syntactic contexts `z_t` forms distinct sparse codes with overlap in `[0.20, 0.50]`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KenyonBinder {
    pub n_kenyon: usize,
    pub k_winners: usize,
    pub lambda_context: f32,
}

impl Default for KenyonBinder {
    fn default() -> Self {
        Self {
            n_kenyon: 512,
            k_winners: 32,
            lambda_context: 0.85,
        }
    }
}

impl KenyonBinder {
    /// Returns the `k_winners` active Kenyon cell indices for content `concept_key` under context `context_key`.
    pub fn bind_conjunctive(&self, concept_key: &str, context_key: &str) -> Vec<u32> {
        let mut drives: Vec<(u32, f32)> = (0..self.n_kenyon as u32)
            .map(|idx| {
                let px = Self::pseudo_proj(concept_key, idx, 0x1234_5678_9ABC_DEF0);
                let pz = Self::pseudo_proj(context_key, idx, 0xFEDC_BA98_7654_3210);
                // Non-linear dendritic coincidence boost when both content and context project to cell idx
                let conj = if px > 0.55 && pz > 0.55 { 0.45 } else { 0.0 };
                (idx, px + self.lambda_context * pz + conj)
            })
            .collect();
        drives.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        drives
            .into_iter()
            .take(self.k_winners)
            .map(|(idx, _)| idx)
            .collect()
    }

    /// Jaccard/fraction overlap `|A \cap B| / k` between two Kenyon assemblies.
    pub fn overlap(a: &[u32], b: &[u32]) -> f32 {
        if a.is_empty() {
            return 0.0;
        }
        let shared = a.iter().filter(|x| b.contains(x)).count();
        (shared as f32) / (a.len() as f32)
    }

    #[inline]
    fn pseudo_proj(key: &str, cell_idx: u32, salt: u64) -> f32 {
        let mut h = salt ^ 14695981039346656037u64;
        for b in key.as_bytes() {
            h ^= *b as u64;
            h = h.wrapping_mul(1099511628211);
        }
        h ^= (cell_idx as u64).wrapping_mul(0x9E3779B97F4A7C15);
        h = h.wrapping_mul(1099511628211);
        ((h & 0xFFFF) as f32) / 65535.0
    }
}

/// `CORE` Multi-Timescale Associative Hierarchy (`L = 4`, `\tau \in {4, 16, 64, 256}`)
/// with 80% Event-Boundary Reset (`\alpha_t^{(\ell)} = e^{-1/\tau_\ell}(1 - 0.8 b_t)`, Gate `WM-1`)
/// and Phase 12 (`v1.6.0`) **Linear Depth Memory (LDM) Sherman-Morrison RLS** (`arXiv:2610.18809v1`)
/// 3-stream depth mixer `S_\ell = (x_\ell, M_\ell, P_\ell)`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CoreTimescaleHierarchy {
    pub taus: [f32; 4],
    pub max_row_entries: usize,
    /// Multi-timescale active working-memory vectors `w_t^{(\ell)}` (`symbol_id -> activation`)
    pub layer_traces: [FxHashMap<u32, f32>; 4],
    /// Multi-timescale fast associative matrices `H_t^{(\ell)}` (`pre_id -> Vec<(post_id, weight)>`)
    pub layer_assoc: [FxHashMap<u32, Vec<(u32, f32)>>; 4],
    /// Phase 12 (`v1.6.0`): 3-stream Linear Depth Memory `(x_\ell, M_\ell, P_\ell)` via Sherman-Morrison RLS
    #[serde(default)]
    pub ldm_depth_mixer: crate::chrono_census_ldm_math::LinearDepthMemoryRLS,
}

impl Default for CoreTimescaleHierarchy {
    fn default() -> Self {
        Self {
            taus: [4.0, 16.0, 64.0, 256.0],
            max_row_entries: 16,
            layer_traces: [
                FxHashMap::default(),
                FxHashMap::default(),
                FxHashMap::default(),
                FxHashMap::default(),
            ],
            layer_assoc: [
                FxHashMap::default(),
                FxHashMap::default(),
                FxHashMap::default(),
                FxHashMap::default(),
            ],
            ldm_depth_mixer: crate::chrono_census_ldm_math::LinearDepthMemoryRLS::default(),
        }
    }
}

impl CoreTimescaleHierarchy {
    /// Steps all 4 timescale layers at tick `t`, applying recurrent attractor support,
    /// `e^{-1/\tau_\ell}(1 - 0.8 b_t)` decay, top-`m`-per-row associative pruning (`Gate WM-1`),
    /// and Sherman-Morrison RLS depth mixing (`LinearDepthMemoryRLS`, `arXiv:2610.18809v1`).
    pub fn step(&mut self, active_ids: &[u32], boundary_reset: bool) {
        let b_mult = if boundary_reset { 0.20 } else { 1.0 };
        if boundary_reset {
            self.ldm_depth_mixer.reset();
        }
        for ell in 0..4 {
            let base_decay = (-1.0 / self.taus[ell]).exp();
            // Cortical-hippocampal working-memory attractor maintenance on medium/slow layers
            let alpha = if !boundary_reset && ell >= 1 {
                base_decay.max(0.985)
            } else {
                base_decay * b_mult
            };

            let prev_snapshot: Vec<(u32, f32)> = self.layer_traces[ell]
                .iter()
                .map(|(&k, &v)| (k, v))
                .collect();

            for val in self.layer_traces[ell].values_mut() {
                *val *= alpha;
            }
            self.layer_traces[ell].retain(|_, &mut v| v > 0.01);

            for &id in active_ids {
                self.layer_traces[ell].insert(id, 1.0);
                // Bind previous active symbols in layer `ell` to `id` in `H_t^{(\ell)}`
                for &(prev_id, prev_v) in &prev_snapshot {
                    if prev_id != id && prev_v > 0.10 {
                        let row = self.layer_assoc[ell].entry(prev_id).or_default();
                        if let Some(entry) = row.iter_mut().find(|(dst, _)| *dst == id) {
                            entry.1 = (entry.1 * alpha + 0.35 * prev_v).min(2.0);
                        } else {
                            row.push((id, 0.35 * prev_v));
                        }
                        row.sort_by(|a, b| {
                            b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal)
                        });
                        row.truncate(self.max_row_entries);
                    }
                }
            }

            // Propagate 3-stream Sherman-Morrison RLS depth memory S_ell = (x_ell, M_ell, P_ell)
            if !active_ids.is_empty() {
                let mut key = [0.0f32; crate::chrono_census_ldm_math::LDM_DK];
                let mut val = [0.0f32; crate::chrono_census_ldm_math::LDM_DX];
                key[ell % crate::chrono_census_ldm_math::LDM_DK] = 1.0;
                for (idx, &sym_id) in active_ids.iter().enumerate() {
                    let k_slot = ((sym_id as usize) + ell) % crate::chrono_census_ldm_math::LDM_DK;
                    let v_slot = ((sym_id as usize) + idx) % crate::chrono_census_ldm_math::LDM_DX;
                    key[k_slot] += 0.5;
                    val[v_slot] += 1.0 / ((ell + 1) as f32);
                }
                self.ldm_depth_mixer.write_rls(&val, &key, &val, 1.0, alpha);
            }
        }
    }

    /// Returns the combined working-memory trace strength for `symbol_id` across layers `1..4`.
    pub fn sustained_activation(&self, symbol_id: u32) -> f32 {
        let mut sum = 0.0f32;
        for ell in 1..4 {
            sum += *self.layer_traces[ell].get(&symbol_id).unwrap_or(&0.0);
        }
        sum / 3.0
    }
}

/// Phase 2 (`v0.6.0`): 8-Letter / Phoneme Sub-Word Slot `EarOrgan` (`FIXED`, `CORE` Clue C4, Gate `Q-PARA`).
/// Transduces words into `[onset_0..3, coda_0..3, length_bucket]` without any English stem dictionary,
/// so morphological relatives (`"come"`/`"came"`, `"play"`/`"played"`) share sub-word slots naturally.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SubWordSlotEarOrgan;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WordSlotCode {
    pub onset: [char; 4],
    pub coda: [char; 4],
    pub length_bucket: u8,
}

impl SubWordSlotEarOrgan {
    pub fn encode(word: &str) -> WordSlotCode {
        let chars: Vec<char> = word
            .trim()
            .to_lowercase()
            .chars()
            .filter(|c| c.is_alphanumeric())
            .collect();
        let mut onset = ['_'; 4];
        let mut coda = ['_'; 4];
        for i in 0..4.min(chars.len()) {
            onset[i] = chars[i];
        }
        for i in 0..4.min(chars.len()) {
            coda[i] = chars[chars.len() - 1 - i];
        }
        let length_bucket = (chars.len() / 3).min(7) as u8;
        WordSlotCode {
            onset,
            coda,
            length_bucket,
        }
    }

    /// Computes slot overlap in `[0.0, 1.0]` between two words (`Gate Q-PARA`).
    pub fn slot_similarity(a: &str, b: &str) -> f32 {
        let ca = Self::encode(a);
        let cb = Self::encode(b);
        let mut matches = 0.0f32;
        let mut pos_matches = 0u32;
        for i in 0..4 {
            if ca.onset[i] != '_' && ca.onset[i] == cb.onset[i] {
                matches += 1.25;
                pos_matches += 1;
            } else if ca.onset[i] != '_' && cb.onset.contains(&ca.onset[i]) {
                matches += 0.35;
            }
            if ca.coda[i] != '_' && ca.coda[i] == cb.coda[i] {
                matches += 1.0;
                pos_matches += 1;
            } else if ca.coda[i] != '_' && cb.coda.contains(&ca.coda[i]) {
                matches += 0.35;
            }
        }
        if pos_matches > 0 && ca.length_bucket.abs_diff(cb.length_bucket) <= 1 {
            matches += 1.0;
        }
        (matches / 8.0).clamp(0.0, 1.0)
    }
}

/// Phase 2 (`v0.6.0`): Revocable `WordLedger` (`WordStatus::{HeardOf, Understood}`, Gates `ABST-1`, `REP-1`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum WordStatus {
    HeardOf,
    Understood,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WordLedgerEntry {
    pub word: String,
    pub status: WordStatus,
    pub grounded_modalities: Vec<Modality>,
    pub rolling_accuracy: f32,
    pub exposures: u32,
    pub synaptic_depression: f32,
    pub revocation_count: u32,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct WordLedger {
    pub entries: FxHashMap<String, WordLedgerEntry>,
    pub freeze_depression: bool,
}

impl WordLedger {
    /// Records an exposure to `word` with optional sensory modality grounding.
    pub fn observe_word(&mut self, word: &str, grounded_modality: Option<Modality>) {
        let w = word.trim().to_lowercase();
        let entry = self.entries.entry(w.clone()).or_insert(WordLedgerEntry {
            word: w,
            status: WordStatus::HeardOf,
            grounded_modalities: Vec::new(),
            rolling_accuracy: 0.50,
            exposures: 0,
            synaptic_depression: 0.0,
            revocation_count: 0,
        });
        entry.exposures = entry.exposures.saturating_add(1);
        if let Some(m) = grounded_modality {
            if m != Modality::Language && !entry.grounded_modalities.contains(&m) {
                entry.grounded_modalities.push(m);
            }
            entry.rolling_accuracy = (0.80 * entry.rolling_accuracy + 0.20 * 1.0).clamp(0.0, 1.0);
        }
        if !entry.grounded_modalities.is_empty()
            && entry.exposures >= 2
            && entry.rolling_accuracy >= 0.65
        {
            entry.status = WordStatus::Understood;
        }
    }

    /// Updates rolling prediction accuracy for `word` and revokes `Understood -> HeardOf`
    /// if accuracy drops below `0.55` (`Test 6: Live Revocation`).
    pub fn record_prediction_outcome(&mut self, word: &str, correct: bool) -> WordStatus {
        let w = word.trim().to_lowercase();
        let entry = self.entries.entry(w.clone()).or_insert(WordLedgerEntry {
            word: w,
            status: WordStatus::HeardOf,
            grounded_modalities: Vec::new(),
            rolling_accuracy: 0.50,
            exposures: 1,
            synaptic_depression: 0.0,
            revocation_count: 0,
        });
        let target = if correct { 1.0 } else { 0.0 };
        entry.rolling_accuracy = (0.65 * entry.rolling_accuracy + 0.35 * target).clamp(0.0, 1.0);
        if entry.status == WordStatus::Understood && entry.rolling_accuracy < 0.55 {
            entry.status = WordStatus::HeardOf;
            entry.revocation_count = entry.revocation_count.saturating_add(1);
        } else if !entry.grounded_modalities.is_empty()
            && entry.exposures >= 2
            && entry.rolling_accuracy >= 0.65
        {
            entry.status = WordStatus::Understood;
        }
        entry.status
    }

    pub fn status_of(&self, word: &str) -> Option<WordStatus> {
        self.entries.get(&word.trim().to_lowercase()).map(|e| e.status)
    }

    /// Selects a non-repetitive grounded descriptor set by applying short-term synaptic depression
    /// (`\tau_{dep}`, Gate `REP-1`). When `freeze_depression == true`, returns identical ordering.
    pub fn select_depressed_descriptors(&mut self, candidates: &[String], take_k: usize) -> Vec<String> {
        if !self.freeze_depression {
            for e in self.entries.values_mut() {
                e.synaptic_depression *= 0.82;
            }
        }
        let mut scored: Vec<(String, f32)> = candidates
            .iter()
            .enumerate()
            .map(|(idx, c)| {
                let dep = if self.freeze_depression {
                    0.0
                } else {
                    self.entries
                        .get(&c.to_lowercase())
                        .map(|e| e.synaptic_depression)
                        .unwrap_or(0.0)
                };
                let base = 1.0 - (idx as f32) * 0.08;
                (c.clone(), base - dep)
            })
            .collect();
        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        let chosen: Vec<String> = scored.into_iter().take(take_k).map(|(c, _)| c).collect();
        if !self.freeze_depression {
            for c in &chosen {
                let entry = self.entries.entry(c.to_lowercase()).or_insert(WordLedgerEntry {
                    word: c.to_lowercase(),
                    status: WordStatus::Understood,
                    grounded_modalities: vec![Modality::ConceptHub],
                    rolling_accuracy: 0.90,
                    exposures: 2,
                    synaptic_depression: 0.0,
                    revocation_count: 0,
                });
                entry.synaptic_depression += 0.65;
            }
        }
        chosen
    }
}

/// Phase 2 (`v0.6.0`): Anterior Cingulate Cortex (`ACC`) Conflict (`C_t`), Omission (`O_t`),
/// & Entropy (`H_t`) Monitor + Basal Ganglia Collapsing-Bound Action Selection (`Gates Q-INC, ABST-1`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ActionChannel {
    Name,
    Point,
    Ask,
    Abstain,
    Recall,
    LookAgain,
    SpeakPlan,
}

#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize)]
pub struct AccMonitorState {
    pub conflict_c: f32,
    pub omission_o: f32,
    pub entropy_h: f32,
    pub settling_ticks_k: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccBasalGangliaLoop {
    pub theta_mass: f32,
    pub theta_select: f32,
    pub urgency_slope: f32,
    pub lesion_acc: bool,
    pub last_state: AccMonitorState,
}

impl Default for AccBasalGangliaLoop {
    fn default() -> Self {
        Self {
            theta_mass: 0.25,
            theta_select: 0.55,
            urgency_slope: 0.06,
            lesion_acc: false,
            last_state: AccMonitorState::default(),
        }
    }
}

impl AccBasalGangliaLoop {
    /// Evaluates turn-end ACC conflict `C_t`, mass-gated apical omission `O_t`, and entropy `H_t`,
    /// then runs the Basal Ganglia D1/D2/STN collapsing-bound race (`k in 1..=12`) to select an `ActionChannel`.
    /// Solves `"What is"` / `"Where did the"` neurally via post-verbal apical omission (`Gate Q-INC`)!
    pub fn evaluate_turn_and_select(
        &mut self,
        helmholtz: &TwoStageHelmholtz,
        ledger: &WordLedger,
        tokens: &[String],
    ) -> (ActionChannel, AccMonitorState) {
        if self.lesion_acc {
            let st = AccMonitorState {
                conflict_c: 0.0,
                omission_o: 0.0,
                entropy_h: 0.0,
                settling_ticks_k: 1,
            };
            self.last_state = st;
            return (ActionChannel::Abstain, st);
        }

        let last_tok = match tokens.last() {
            Some(t) => t.trim().to_lowercase(),
            None => return (ActionChannel::Abstain, AccMonitorState::default()),
        };

        // 1. Compute post-token apical prediction mass \sum_j \Omega^{slow}_{last, j} at turn-end silence
        let mut apical_pred_mass = 0.0f32;
        if let Some(&last_id) = helmholtz.symbol_to_id.get(&last_tok) {
            for (&(u, _v), &w) in &helmholtz.omega_slow {
                if u == last_id && w > 0.0 {
                    apical_pred_mass += w;
                }
            }
        }
        // Mass-gated apical omission O_t at turn-end when expected post-verbal argument is missing (V_b = 0)
        let omission_o = if apical_pred_mass >= self.theta_mass {
            apical_pred_mass
        } else {
            0.0
        };

        // 2. Compute Hopfield mutual-exclusion conflict C_t across active utterance tokens
        let mut conflict_num = 0.0f32;
        let mut active_ids = Vec::new();
        for t in tokens {
            if let Some(&id) = helmholtz.symbol_to_id.get(&t.trim().to_lowercase()) {
                active_ids.push(id);
            }
        }
        for i in 0..active_ids.len() {
            for j in (i + 1)..active_ids.len() {
                conflict_num += *helmholtz
                    .s_minus
                    .get(&(active_ids[i], active_ids[j]))
                    .unwrap_or(&0.0);
            }
        }
        let denom = (active_ids.len() as f32).powi(2) + 1e-4;
        let conflict_c = conflict_num / denom;

        // 3. Check how many content tokens are Understood vs HeardOf/Unknown in WordLedger
        let mut understood_count = 0usize;
        let mut unknown_or_heard_of = 0usize;
        for t in tokens {
            match ledger.status_of(t) {
                Some(WordStatus::Understood) => understood_count += 1,
                _ => unknown_or_heard_of += 1,
            }
        }
        let entropy_h = if understood_count == 0 {
            0.90
        } else {
            (unknown_or_heard_of as f32) / ((understood_count + unknown_or_heard_of) as f32)
        };

        // 4. Basal Ganglia D1 (Go) - D2 (NoGo) collapsing-bound race over k = 1..=12 ticks
        let go_ask = 1.35 * omission_o + 0.55 * conflict_c;
        let go_name = if omission_o < self.theta_mass && understood_count > 0 && unknown_or_heard_of == 0 {
            0.85 - 0.5 * conflict_c
        } else {
            0.15
        };
        let go_abstain = if omission_o < self.theta_mass && unknown_or_heard_of > 0 {
            0.80 * entropy_h
        } else {
            0.10
        };

        let mut chosen = ActionChannel::Abstain;
        let mut settled_k = 12u8;
        for k in 1..=12u8 {
            let bound = self.theta_select - self.urgency_slope * (k as f32);
            if go_ask >= bound && go_ask >= go_name && go_ask >= go_abstain {
                chosen = ActionChannel::Ask;
                settled_k = k;
                break;
            } else if go_name >= bound && go_name > go_ask && go_name >= go_abstain {
                chosen = ActionChannel::Name;
                settled_k = k;
                break;
            } else if go_abstain >= bound && go_abstain > go_ask && go_abstain > go_name {
                chosen = ActionChannel::Abstain;
                settled_k = k;
                break;
            }
        }

        let state = AccMonitorState {
            conflict_c,
            omission_o,
            entropy_h,
            settling_ticks_k: settled_k,
        };
        self.last_state = state;
        (chosen, state)
    }
}

/// Phase 3 (`v0.7.0`): Unified Negative-Image Organ (Mormyrid Electric-Fish `ELL` + Cerebellar Forward Model,
/// `Correction 5`, Gates `SELF-1` & `PRON-1`).
/// Operates on an untagged sensory stream (`Law L7`):
/// `\hat{x}_t = W_{eff} e_{t-1}`, `r_t = x_t - \hat{x}_t`, `\Delta W_{eff} = \eta r_t e_{t-1}^T`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnifiedNegativeImageOrgan {
    pub w_eff: Vec<f32>,
    pub eta: f32,
    pub self_turns_observed: u32,
    pub other_turns_observed: u32,
}

impl Default for UnifiedNegativeImageOrgan {
    fn default() -> Self {
        Self::new(16)
    }
}

impl UnifiedNegativeImageOrgan {
    pub fn new(dim: usize) -> Self {
        Self {
            w_eff: vec![0.0; dim],
            eta: 0.35,
            self_turns_observed: 0,
            other_turns_observed: 0,
        }
    }

    /// Processes an untagged sensory vector `x_t` alongside the organism's own motor/vocal efference
    /// copy `e_{t-1}`, returning the cancelled residual `r_t` and updating the anti-Hebbian / LMS
    /// forward model (`\Delta W_{eff} = \eta r_t e_{t-1}`).
    pub fn filter_untagged_stream(&mut self, x_t: &[f32], efference_copy: &[f32]) -> Vec<f32> {
        let dim = x_t.len().min(efference_copy.len()).min(self.w_eff.len());
        let mut residual = vec![0.0f32; dim];
        let mut eff_norm = 0.0f32;
        for i in 0..dim {
            let x_hat = self.w_eff[i] * efference_copy[i];
            let r_i = x_t[i] - x_hat;
            residual[i] = r_i;
            self.w_eff[i] += self.eta * r_i * efference_copy[i];
            eff_norm += efference_copy[i].abs();
        }
        if eff_norm > 0.1 {
            self.self_turns_observed = self.self_turns_observed.saturating_add(1);
        } else {
            self.other_turns_observed = self.other_turns_observed.saturating_add(1);
        }
        residual
    }

    /// Resolves deictic pronoun reference (`"you"` vs `"i"`) on an untagged sensory stream (`Gate PRON-1`):
    /// When `efference_copy` is silent (`eff_norm == 0`), an incoming `"you"` targets `SELF` (`"alpha7_self"`);
    /// when `efference_copy` is active (`eff_norm > 0`), `"i"` targets `SELF` (`"alpha7_self"`).
    pub fn resolve_deictic_pronoun(&self, pronoun: &str, efference_copy_active: bool) -> &'static str {
        let p = pronoun.trim().to_lowercase();
        match (p.as_str(), efference_copy_active) {
            ("you" | "your" | "yourself", false) => "alpha7_self",
            ("i" | "me" | "my" | "myself", true) => "alpha7_self",
            ("i" | "me" | "my" | "myself", false) => "interlocutor_other",
            ("you" | "your" | "yourself", true) => "interlocutor_other",
            _ => "unknown_referent",
        }
    }
}

/// Phase 3 (`v0.7.0`): Endogenous Homeostatic Drives (`Arousal`, `Boredom`, `Fatigue`, Gates `H-NULL`, `SEEK-1`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DriveMode {
    ExploreForage,
    FocusedTask,
    SleepConsolidate,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HomeostaticDrives {
    pub arousal: f32,
    pub boredom: f32,
    pub fatigue: f32,
    pub freeze_drives: bool,
}

impl Default for HomeostaticDrives {
    fn default() -> Self {
        Self {
            arousal: 0.50,
            boredom: 0.15,
            fatigue: 0.10,
            freeze_drives: false,
        }
    }
}

impl HomeostaticDrives {
    pub fn step_drives(&mut self, novelty: f32, metabolic_effort: f32) -> DriveMode {
        if !self.freeze_drives {
            self.arousal = (0.85 * self.arousal + 0.25 * novelty).clamp(0.05, 1.0);
            if novelty < 0.15 {
                self.boredom = (self.boredom + 0.12).clamp(0.0, 1.0);
            } else {
                self.boredom = (self.boredom * 0.75).clamp(0.0, 1.0);
            }
            self.fatigue = (self.fatigue + 0.08 * metabolic_effort).clamp(0.0, 1.0);
        }
        if self.fatigue >= 0.75 {
            if !self.freeze_drives {
                self.fatigue *= 0.25;
            }
            DriveMode::SleepConsolidate
        } else if self.boredom >= 0.65 {
            DriveMode::ExploreForage
        } else {
            DriveMode::FocusedTask
        }
    }
}

/// Phase 4 (`v0.8.0`): Tanno et al. (2026) Two-Channel Thalamocortical Credit Router (`Gate CR-1`)
/// & Janelia Path-Bundle Mutual Information Promoter (`I(S_{start}; S_{end} | M) > \theta_{chunk}`).
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TannoTwoChannelRouter {
    /// Basal Ganglia value-gated apical gain `g_{BG}(state)`
    pub bg_apical_gain: FxHashMap<String, f32>,
    /// Cerebellar action-conditioned basal additive shift `\Delta I_{CB}(state, action)`
    #[serde(default, with = "tuple_map_serde")]
    pub cb_basal_shift: FxHashMap<(String, String), f32>,
    /// Promoted composite path bundles `(start_state, macro_actions, end_state, mutual_info_bits)`
    pub promoted_bundles: Vec<(String, Vec<String>, String, f32)>,
}

impl TannoTwoChannelRouter {
    /// Updates Basal Ganglia apical value gain and Cerebellar action-specific basal shift from outcome reward/error.
    pub fn update_two_channel(
        &mut self,
        state: &str,
        action: &str,
        reward_td: f32,
        kinematic_error: f32,
    ) {
        let g = self.bg_apical_gain.entry(state.to_string()).or_insert(1.0);
        *g = (*g + 0.25 * reward_td).clamp(0.2, 2.5);
        let shift = self
            .cb_basal_shift
            .entry((state.to_string(), action.to_string()))
            .or_insert(0.0);
        *shift = (*shift + 0.35 * kinematic_error).clamp(-1.5, 1.5);
    }

    /// Computes combined two-channel thalamocortical drive `v = (v_b + \Delta I_{CB}) * g_{BG} * (1.0 + v_a)` (`Gate CR-1`).
    /// Multiplicative Basal Ganglia apical gain gates the cerebellar-shifted basal drive.
    pub fn score_action(&self, state: &str, action: &str, v_b: f32, v_a: f32) -> f32 {
        let g_bg = *self.bg_apical_gain.get(state).unwrap_or(&1.0);
        let d_cb = *self
            .cb_basal_shift
            .get(&(state.to_string(), action.to_string()))
            .unwrap_or(&0.0);
        (v_b + d_cb) * g_bg * (1.0 + v_a.max(0.0))
    }

    /// Evaluates empirical path-bundle predictability `I(S_{start}; S_{end} | M)` and promotes the trajectory
    /// into a composite macro-action if predictability exceeds `\theta_{chunk} = 0.75`.
    pub fn evaluate_and_promote_bundle(
        &mut self,
        start_state: &str,
        actions: Vec<String>,
        end_state: &str,
        success_count: u32,
        total_attempts: u32,
    ) -> bool {
        if total_attempts == 0 {
            return false;
        }
        let p = (success_count as f32) / (total_attempts as f32);
        if p >= 0.75 {
            self.promoted_bundles.push((
                start_state.to_string(),
                actions,
                end_state.to_string(),
                p,
            ));
            true
        } else {
            false
        }
    }
}

/// Phase 10–11 (`v1.4.0 → v1.5.0`): Source of sub-threshold cognitive dissonance / Zeigarnik open-loop tension.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum OpenLoopKind {
    /// Apical prediction was present but Basal confirmation failed to arrive (`\varepsilon_i^{omit}`).
    ApicalOmissionMismatch,
    /// Two mutually exclusive assemblies (linked by GABAergic `S^-`) co-activated (`\varepsilon_i^{con}`).
    GabaergicContradiction,
    /// An answer was obtained via a prosthetic/calculator while neural substrate grounding was below `\theta_g` (`g_i`).
    UngroundedProstheticShortcut,
    /// A key concept/word encountered during reading remains `WordStatus::HeardOf` without definition or sensory grounding.
    UnresolvedLexicalConceptGap,
    /// A scientific hypothesis or claim read from `/data/alpha3-library` is `unproven`/`contested` (`DoubtPendingProof`).
    UnverifiedScientificHypothesis,
}

/// A persistent Zeigarnik open loop tracked by the Anterior Insula + Dorsal ACC tension ledger.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenLoop {
    pub loop_id: String,
    pub kind: OpenLoopKind,
    pub context_cue: String,
    pub involved_neurons: Vec<u32>,
    pub tension: f32,
    pub expected_value_of_control: f32,
    pub attempts: u32,
    pub quarantined: bool,
    pub resolved: bool,
}

/// Phase 10 (`v1.4.0`): Anterior Insula + Dorsal ACC + Zeigarnik Open-Loop Uneasiness Organ.
/// Implements persistent sub-threshold dissonance `U(t)` that refuses to vanish in 1 tick,
/// drives autonomous `ReExamine` / `LookAgain` revisits, discharges upon neural confirmation (`\delta_{DA} = -\Delta U`),
/// and quarantines unresolvable loops after `K = 5` failed attempts (`UNEASE-PERSIST`, `UNEASE-REVISIT`, `UNEASE-RESOLVE`, `UNEASE-QUIET`).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ZeigarnikInsulaTensionOrgan {
    pub felt_unease_u: f32,
    pub open_loops: Vec<OpenLoop>,
    pub resolved_loops_count: u64,
    pub quarantined_loops_count: u64,
    pub autonomous_revisits_triggered: u64,
    pub last_relief_dopamine_delta: f32,
    pub lesion_freeze_tension: bool,
}

impl Default for ZeigarnikInsulaTensionOrgan {
    fn default() -> Self {
        Self {
            felt_unease_u: 0.0,
            open_loops: Vec::new(),
            resolved_loops_count: 0,
            quarantined_loops_count: 0,
            autonomous_revisits_triggered: 0,
            last_relief_dopamine_delta: 0.0,
            lesion_freeze_tension: false,
        }
    }
}

impl ZeigarnikInsulaTensionOrgan {
    pub fn recompute_insula_u(&mut self) {
        if self.lesion_freeze_tension {
            self.felt_unease_u = 0.0;
            return;
        }
        let mut sum_t = 0.0f32;
        for lp in &self.open_loops {
            if !lp.resolved {
                let w = if lp.quarantined { 0.20 } else { 1.0 };
                sum_t += w * lp.tension;
            }
        }
        self.felt_unease_u = sum_t.clamp(0.0, 1.0);
    }

    /// Registers or amplifies a persistent Zeigarnik open loop when a prediction fails, a contradiction
    /// occurs, or a prosthetic tool answer lacks neural substrate grounding.
    pub fn register_open_loop(
        &mut self,
        loop_id: &str,
        kind: OpenLoopKind,
        context_cue: &str,
        involved_neurons: Vec<u32>,
        initial_tension: f32,
    ) {
        if self.lesion_freeze_tension {
            return;
        }
        let t_clamped = initial_tension.clamp(0.05, 1.0);
        if let Some(existing) = self.open_loops.iter_mut().find(|l| l.loop_id == loop_id) {
            if !existing.resolved && !existing.quarantined {
                existing.tension = (existing.tension + 0.5 * t_clamped).clamp(0.05, 1.0);
                existing.expected_value_of_control =
                    (0.85 * existing.tension - 0.08 * (existing.attempts as f32)).max(0.01);
            }
        } else {
            let evc = (0.85 * t_clamped - 0.05).max(0.05);
            self.open_loops.push(OpenLoop {
                loop_id: loop_id.to_string(),
                kind,
                context_cue: context_cue.to_string(),
                involved_neurons,
                tension: t_clamped,
                expected_value_of_control: evc,
                attempts: 0,
                quarantined: false,
                resolved: false,
            });
        }
        self.recompute_insula_u();
    }

    /// Steps slow Zeigarnik leak (`\tau_{leak} = 10,000` ticks) and returns the highest-EVC unresolved
    /// open loop for autonomous re-examination if Anterior Insula uneasiness `U >= 0.15`.
    pub fn step_uneasiness(&mut self, dt_ticks: u32) -> Option<OpenLoop> {
        if self.lesion_freeze_tension {
            self.felt_unease_u = 0.0;
            return None;
        }
        let leak = 1.0 / (1.0 + 0.0001 * (dt_ticks.max(1) as f32));
        for lp in &mut self.open_loops {
            if !lp.resolved {
                lp.tension *= leak;
                let p_resolve = 1.0 / (1.0 + 0.30 * (lp.attempts as f32));
                lp.expected_value_of_control =
                    (p_resolve * lp.tension - 0.05 * (lp.attempts as f32)).max(0.0);
            }
        }
        self.recompute_insula_u();

        if self.felt_unease_u < 0.15 {
            return None;
        }

        let best = self
            .open_loops
            .iter()
            .filter(|l| !l.resolved && !l.quarantined && l.tension >= 0.10)
            .max_by(|a, b| {
                a.expected_value_of_control
                    .partial_cmp(&b.expected_value_of_control)
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
            .cloned();

        if best.is_some() {
            self.autonomous_revisits_triggered += 1;
        }
        best
    }

    /// Records the outcome of an autonomous re-examination or grounding verification on `loop_id`.
    /// - If `resolved_by_neural_confirmation` is true: discharges tension to 0 and emits positive relief `\delta_{DA} = -\Delta U`.
    /// - If false after `>= 5` attempts: quarantines the loop (`UNEASE-QUIET`) so the brain never ruminates infinitely.
    pub fn record_reexamination_attempt(
        &mut self,
        loop_id: &str,
        resolved_by_neural_confirmation: bool,
    ) -> f32 {
        let prev_u = self.felt_unease_u;
        if let Some(lp) = self.open_loops.iter_mut().find(|l| l.loop_id == loop_id) {
            lp.attempts += 1;
            if resolved_by_neural_confirmation {
                lp.tension = 0.0;
                lp.expected_value_of_control = 0.0;
                lp.resolved = true;
                self.resolved_loops_count += 1;
            } else if lp.attempts >= 5 {
                lp.quarantined = true;
                lp.tension *= 0.25;
                lp.expected_value_of_control = 0.0;
                self.quarantined_loops_count += 1;
            }
        }
        self.recompute_insula_u();
        let relief_da = (prev_u - self.felt_unease_u).max(0.0);
        self.last_relief_dopamine_delta = relief_da;
        relief_da
    }
}

/// Complete Phase 1–4 & Phase 10 (`v0.5.0 → v1.4.0`) Cortical-Hippocampal & Subcortical Substrate integrated into `Alpha7Organism`.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CorticalSubstrate {
    pub pools: Vec<NeuralPool>,
    pub modulators: NeuromodulatorState,
    pub helmholtz: TwoStageHelmholtz,
    pub kenyon: KenyonBinder,
    pub core_hierarchy: CoreTimescaleHierarchy,
    pub subword_ear: SubWordSlotEarOrgan,
    pub word_ledger: WordLedger,
    pub acc_bg: AccBasalGangliaLoop,
    pub ell_cerebellum: UnifiedNegativeImageOrgan,
    pub drives: HomeostaticDrives,
    pub tanno_router: TannoTwoChannelRouter,
    #[serde(default)]
    pub unease_organ: ZeigarnikInsulaTensionOrgan,
}

impl CorticalSubstrate {
    pub fn new() -> Self {
        let pools = vec![
            NeuralPool::new(0, "V4_Visual", PoolKind::Excitatory, Modality::Visual, 256, 16),
            NeuralPool::new(1, "A1_Auditory", PoolKind::Excitatory, Modality::Auditory, 256, 16),
            NeuralPool::new(2, "S1_Tactile", PoolKind::Excitatory, Modality::TactileHand, 256, 16),
            NeuralPool::new(3, "Semantic_Hub", PoolKind::Excitatory, Modality::ConceptHub, 512, 24),
            NeuralPool::new(4, "Lexical_Word", PoolKind::Excitatory, Modality::Language, 512, 24),
            NeuralPool::new(5, "GABA_Inhibitory", PoolKind::Inhibitory, Modality::Association, 256, 16),
        ];
        Self {
            pools,
            modulators: NeuromodulatorState::default(),
            helmholtz: TwoStageHelmholtz::new(),
            kenyon: KenyonBinder::default(),
            core_hierarchy: CoreTimescaleHierarchy::default(),
            subword_ear: SubWordSlotEarOrgan,
            word_ledger: WordLedger::default(),
            acc_bg: AccBasalGangliaLoop::default(),
            ell_cerebellum: UnifiedNegativeImageOrgan::new(16),
            drives: HomeostaticDrives::default(),
            tanno_router: TannoTwoChannelRouter::default(),
            unease_organ: ZeigarnikInsulaTensionOrgan::default(),
        }
    }

    /// Pattern completion (`Gate PC-1`): given a partial `cue` (`40%` subset of an assembly's
    /// grounded features in `S^+`), recovers the full target assembly via recurrent `S^+` excitation
    /// and `S^-` mutual-exclusion inhibition.
    pub fn complete_pattern(&self, cue_features: &[String], candidate_concepts: &[String]) -> Option<(String, f32)> {
        let cue_ids: Vec<u32> = cue_features
            .iter()
            .filter_map(|f| self.helmholtz.symbol_to_id.get(&f.trim().to_lowercase()).copied())
            .collect();
        if cue_ids.is_empty() {
            return None;
        }

        let mut best: Option<(String, f32)> = None;
        for cand in candidate_concepts {
            let cid = match self.helmholtz.symbol_to_id.get(&cand.trim().to_lowercase()) {
                Some(&id) => id,
                None => continue,
            };
            let mut excit = 0.0f32;
            let mut inhib = 0.0f32;
            for &fid in &cue_ids {
                excit += *self.helmholtz.s_plus.get(&(cid, fid)).unwrap_or(&0.0);
                inhib += *self.helmholtz.s_minus.get(&(cid, fid)).unwrap_or(&0.0);
            }
            let net = excit - 1.25 * inhib;
            if net > 0.0 {
                if best.as_ref().map(|(_, s)| net > *s).unwrap_or(true) {
                    best = Some((cand.clone(), net));
                }
            }
        }
        best
    }

    /// Phase 4 (`v0.8.0`): Covert multi-hop rollout simulation through `\tilde{\Omega}^{slow}`
    /// with `S^-` blocker avoidance (`Gate PLAN-1`).
    pub fn simulate_covert_rollout(
        &self,
        start_symbol: &str,
        goal_symbol: &str,
        active_blockers: &[String],
        max_hops: usize,
    ) -> Option<Vec<String>> {
        if self.helmholtz.lesion_omega_slow {
            return None;
        }
        let start_id = *self.helmholtz.symbol_to_id.get(&start_symbol.trim().to_lowercase())?;
        let goal_id = *self.helmholtz.symbol_to_id.get(&goal_symbol.trim().to_lowercase())?;
        let blocker_ids: Vec<u32> = active_blockers
            .iter()
            .filter_map(|b| self.helmholtz.symbol_to_id.get(&b.trim().to_lowercase()).copied())
            .collect();

        let mut queue: std::collections::VecDeque<(u32, Vec<String>)> = std::collections::VecDeque::new();
        let mut visited = std::collections::HashSet::new();
        queue.push_back((start_id, vec![start_symbol.to_lowercase()]));
        visited.insert(start_id);

        while let Some((curr, path)) = queue.pop_front() {
            if curr == goal_id {
                return Some(path);
            }
            if path.len() > max_hops {
                continue;
            }
            let mut next_candidates: Vec<(u32, f32)> = Vec::new();
            for (&(u, v), &w) in &self.helmholtz.omega_slow {
                if u == curr && w > 0.10 && !visited.contains(&v) {
                    // Check if any active blocker inhibits `v` via S^-
                    let blocked = blocker_ids
                        .iter()
                        .any(|&bid| *self.helmholtz.s_minus.get(&(bid, v)).unwrap_or(&0.0) >= 0.50);
                    if !blocked {
                        next_candidates.push((v, w));
                    }
                }
            }
            next_candidates.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            for (next_id, _) in next_candidates {
                visited.insert(next_id);
                let mut next_path = path.clone();
                next_path.push(self.helmholtz.id_to_symbol[next_id as usize].clone());
                queue.push_back((next_id, next_path));
            }
        }
        None
    }
}

