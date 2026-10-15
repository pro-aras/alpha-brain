//! Phase 5 (`v0.9.0`): Software Quantum Annealing (`dSB` + Suzuki-Trotter Replica Tunneling),
//! Organism-Private Somatic Genetic Code & Self-Healing (`EndogenousGeneticVault`),
//! Universal Continuous Signal Normalizer & Epistemic Sovereignty (`EpistemicSovereigntyEngine`),
//! and the 6-Loop Multi-Parallel Brain Orchestrator (`MultiParallelBrainOrchestrator`).

use crate::body::Alpha7Body;
use crate::concept_web::{ConceptNode, EpisodicMemory};
use crate::predictor::{CausalRule, PredictiveEngine};
use crate::substrate::{CorticalSubstrate, DriveMode};
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};

// ============================================================================
// 1. SOFTWARE QUANTUM ANNEALING & DISCRETE SIMULATED BIFURCATION (`dSB` + Trotter)
// ============================================================================

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct QuantumSettlingResult {
    pub winner_concept: String,
    pub active_ensemble: Vec<String>,
    pub quantum_ground_energy: f32,
    pub classical_greedy_winner: String,
    pub classical_greedy_energy: f32,
    pub tunneled_past_local_minimum: bool,
    pub steps_taken: usize,
    pub replicas_agreement: f32,
}

/// Replicates Quantum Adiabatic Bifurcation (`dSB`, Goto et al., *Science Advances* 2019/2021)
/// and Suzuki-Trotter $P$-Replica Path-Integral Quantum Tunneling in pure Rust software.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuantumBifurcationSettler {
    pub num_steps: usize,
    pub num_replicas: usize,
    pub dt: f32,
    pub a0: f32,
    pub c0: f32,
    pub gamma_init: f32,
}

impl Default for QuantumBifurcationSettler {
    fn default() -> Self {
        Self {
            num_steps: 24,
            num_replicas: 4,
            dt: 0.18,
            a0: 1.0,
            c0: 0.45,
            gamma_init: 1.50,
        }
    }
}

impl QuantumBifurcationSettler {
    /// Evaluates the Ising/Hopfield energy of a binary activation vector `s in {0.0, 1.0}^N`:
    /// `E(s) = -0.5 * \sum_{i != j} J_{ij} s_i s_j - \sum_i h_i s_i`.
    pub fn compute_energy(s: &[f32], h: &[f32], j_mat: &[Vec<f32>]) -> f32 {
        let n = s.len();
        let mut energy = 0.0f32;
        for i in 0..n {
            energy -= h[i] * s[i];
            for j in (i + 1)..n {
                energy -= j_mat[i][j] * s[i] * s[j];
            }
        }
        energy
    }

    /// Runs a 1-step Classical Greedy / Hill-Climbing twin (`Twin N`) that picks the node with
    /// highest immediate local field `h_i` first and greedily adds compatible nodes.
    /// On frustrated riddles with a strong decoy, Classical Greedy falls into the decoy local minimum.
    pub fn solve_classical_greedy(
        candidates: &[String],
        h: &[f32],
        j_mat: &[Vec<f32>],
    ) -> (Vec<f32>, String, f32) {
        let n = candidates.len();
        if n == 0 {
            return (Vec::new(), String::new(), 0.0);
        }
        let mut s = vec![0.0f32; n];
        // Greedy step 1: commit to the single strongest bottom-up cue `argmax_i h_i`
        let mut best_first = 0usize;
        for i in 1..n {
            if h[i] > h[best_first] {
                best_first = i;
            }
        }
        s[best_first] = 1.0;

        // Greedy step 2: try adding any node that lowers energy given the already-committed node
        for i in 0..n {
            if i == best_first {
                continue;
            }
            let mut local_field = h[i];
            for j in 0..n {
                local_field += j_mat[i][j] * s[j];
            }
            if local_field > 0.0 {
                s[i] = 1.0;
            }
        }

        let energy = Self::compute_energy(&s, h, j_mat);
        let mut winner_idx = best_first;
        let mut best_contrib = f32::NEG_INFINITY;
        for i in 0..n {
            if s[i] > 0.5 {
                let mut contrib = h[i];
                for j in 0..n {
                    if i != j {
                        contrib += 0.5 * j_mat[i][j] * s[j];
                    }
                }
                if contrib > best_contrib {
                    best_contrib = contrib;
                    winner_idx = i;
                }
            }
        }
        (s, candidates[winner_idx].clone(), energy)
    }

    /// Runs Discrete Simulated Bifurcation (`dSB`) coupled with $P$-Replica Suzuki-Trotter
    /// transverse-field tunneling over `num_steps` ticks to find the global ground-state assembly.
    pub fn settle_frustrated_network(
        &self,
        candidates: &[String],
        h: &[f32],
        j_mat: &[Vec<f32>],
    ) -> QuantumSettlingResult {
        let n = candidates.len();
        if n == 0 {
            return QuantumSettlingResult {
                winner_concept: String::new(),
                active_ensemble: Vec::new(),
                quantum_ground_energy: 0.0,
                classical_greedy_winner: String::new(),
                classical_greedy_energy: 0.0,
                tunneled_past_local_minimum: false,
                steps_taken: 0,
                replicas_agreement: 1.0,
            };
        }

        let (_greedy_s, greedy_winner, greedy_energy) =
            Self::solve_classical_greedy(candidates, h, j_mat);

        // Initialize P coupled Suzuki-Trotter / dSB oscillator replicas with deterministic phase diversity
        let p_rep = self.num_replicas.max(2);
        let mut x_rep = vec![vec![0.0f32; n]; p_rep];
        let mut y_rep = vec![vec![0.0f32; n]; p_rep];
        for r in 0..p_rep {
            for i in 0..n {
                // Small asymmetric quantum zero-point phase offsets across Trotter replicas
                let phase = (((r * 7 + i * 13) % 19) as f32 - 9.0) * 0.025;
                x_rep[r][i] = phase;
                y_rep[r][i] = -phase * 0.5;
            }
        }

        for step in 0..self.num_steps {
            let progress = (step as f32 + 1.0) / (self.num_steps as f32);
            // Adiabatic bifurcation pump ramps from 0.0 -> a0
            let pump = self.a0 * progress;
            // Transverse field \Gamma(t) decays from gamma_init -> 0.05
            let gamma_t = self.gamma_init * (1.0 - 0.95 * progress);
            // Inter-replica Trotter spring coupling tightens as \Gamma(t) decays
            let j_perp = 0.25 * progress / (gamma_t + 0.15);

            for r in 0..p_rep {
                let r_prev = if r == 0 { p_rep - 1 } else { r - 1 };
                let r_next = (r + 1) % p_rep;
                for i in 0..n {
                    let mut interaction = 0.0f32;
                    for j in 0..n {
                        if i != j {
                            // Discrete Simulated Bifurcation uses soft/hard sign of partner oscillators
                            let s_j = if x_rep[r][j] >= 0.0 {
                                0.5 * (1.0 + x_rep[r][j])
                            } else {
                                0.5 * (1.0 + x_rep[r][j]).max(0.0)
                            };
                            interaction += j_mat[i][j] * s_j;
                        }
                    }
                    // Transverse-field Trotter coupling between adjacent worldline replicas
                    let trotter_pull =
                        j_perp * (x_rep[r_prev][i] + x_rep[r_next][i] - 2.0 * x_rep[r][i]);
                    // In early steps, transverse field suppresses premature commitment to a single high-h decoy
                    let effective_h = h[i] * (0.35 + 0.65 * progress);
                    let force = -(self.a0 - pump) * x_rep[r][i]
                        + self.c0 * (interaction + effective_h)
                        + trotter_pull;

                    y_rep[r][i] += force * self.dt;
                    x_rep[r][i] += self.a0 * y_rep[r][i] * self.dt;

                    // Inelastic wall condition at {-1.0, +1.0}
                    if x_rep[r][i] > 1.0 {
                        x_rep[r][i] = 1.0;
                        y_rep[r][i] = 0.0;
                    } else if x_rep[r][i] < -1.0 {
                        x_rep[r][i] = -1.0;
                        y_rep[r][i] = 0.0;
                    }
                }
            }
        }

        // Evaluate energy of each replica and select the lowest-energy bifurcated state
        let mut best_s = vec![0.0f32; n];
        let mut best_energy = f32::INFINITY;
        let mut replica_binaries: Vec<Vec<f32>> = Vec::with_capacity(p_rep);
        for r in 0..p_rep {
            let s_bin: Vec<f32> = x_rep[r]
                .iter()
                .map(|&v| if v > 0.0 { 1.0 } else { 0.0 })
                .collect();
            let e = Self::compute_energy(&s_bin, h, j_mat);
            if e < best_energy {
                best_energy = e;
                best_s = s_bin.clone();
            }
            replica_binaries.push(s_bin);
        }

        // Measure inter-replica convergence agreement
        let mut agree_pairs = 0usize;
        let mut total_pairs = 0usize;
        for r in 0..p_rep {
            for i in 0..n {
                total_pairs += 1;
                if (replica_binaries[r][i] - best_s[i]).abs() < 1e-3 {
                    agree_pairs += 1;
                }
            }
        }
        let replicas_agreement = if total_pairs > 0 {
            (agree_pairs as f32) / (total_pairs as f32)
        } else {
            1.0
        };

        let mut active_ensemble = Vec::new();
        let mut winner_idx = 0usize;
        let mut best_node_score = f32::NEG_INFINITY;
        for i in 0..n {
            if best_s[i] > 0.5 {
                active_ensemble.push(candidates[i].clone());
                let mut node_score = h[i];
                for j in 0..n {
                    if i != j {
                        node_score += j_mat[i][j] * best_s[j];
                    }
                }
                if node_score > best_node_score {
                    best_node_score = node_score;
                    winner_idx = i;
                }
            }
        }

        let winner_concept = candidates[winner_idx].clone();
        let tunneled = best_energy + 1e-4 < greedy_energy;

        QuantumSettlingResult {
            winner_concept,
            active_ensemble,
            quantum_ground_energy: best_energy,
            classical_greedy_winner: greedy_winner,
            classical_greedy_energy: greedy_energy,
            tunneled_past_local_minimum: tunneled,
            steps_taken: self.num_steps,
            replicas_agreement,
        }
    }
}

// ============================================================================
// 2. ENDOGENOUS GENETIC CODE, TAMPER FORENSICS & AUTONOMIC SELF-HEALING
// ============================================================================

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum GeneticMutationKind {
    TamperedModified,
    DeletedLost,
    AddedOrUpgraded,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeneticMutationFinding {
    pub locus_id: String,
    pub kind: GeneticMutationKind,
    pub expected_codon_motif: String,
    pub observed_codon_motif: String,
    pub healed: bool,
    pub details: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeneticCodonRecord {
    pub locus_id: String,
    pub codon_mac: u64,
    pub tri_nucleotide_motif: String,
    pub holographic_backup_json: String,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct GeneticAuditReport {
    pub intact_loci_count: usize,
    pub mutations_detected: Vec<GeneticMutationFinding>,
    pub healed_loci_count: usize,
    pub newly_sealed_upgrades: usize,
    pub summary: String,
}

/// Organism-Private Somatic Genetic Code (`V(D)J`-inspired internal key + codon signatures + holographic recovery).
/// Only Alpha 7's internal nonlinear permutation over its `somatic_dna_key` can generate or verify valid codons.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EndogenousGeneticVault {
    pub somatic_dna_key: [u64; 4],
    pub sealed_loci: FxHashMap<String, GeneticCodonRecord>,
    pub generation_epoch: u64,
}

impl Default for EndogenousGeneticVault {
    fn default() -> Self {
        Self::new_from_genesis_entropy(0xA7F0_2026_1015_BEEF)
    }
}

impl EndogenousGeneticVault {
    pub fn new_from_genesis_entropy(seed: u64) -> Self {
        let k0 = Self::splitmix64(seed ^ 0x9E37_79B9_7F4A_7C15);
        let k1 = Self::splitmix64(k0 ^ 0xBF58_476D_1CE4_E5B9);
        let k2 = Self::splitmix64(k1 ^ 0x94D0_49BB_1331_11EB);
        let k3 = Self::splitmix64(k2 ^ 0xD6E8_FEB8_6659_FD93);
        Self {
            somatic_dna_key: [k0, k1, k2, k3],
            sealed_loci: FxHashMap::default(),
            generation_epoch: 1,
        }
    }

    #[inline]
    fn splitmix64(mut x: u64) -> u64 {
        x = x.wrapping_add(0x9E37_79B9_7F4A_7C15);
        x = (x ^ (x >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        x = (x ^ (x >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        x ^ (x >> 31)
    }

    /// Computes Alpha 7's private keyed genetic MAC (`codon_mac`) for `(locus_id, canonical_payload)`.
    /// Without `self.somatic_dna_key`, an external modifier cannot forge a valid `codon_mac` after altering memory.
    pub fn compute_private_codon(&self, locus_id: &str, canonical_payload: &str) -> (u64, String) {
        let mut state = self.somatic_dna_key[0] ^ 0x736F_6D65_7073_6575;
        for (idx, b) in locus_id
            .bytes()
            .chain(std::iter::once(0xFF))
            .chain(canonical_payload.bytes())
            .enumerate()
        {
            let k = self.somatic_dna_key[idx & 3];
            state ^= (b as u64).wrapping_mul(0x1000_0000_01B3) ^ k.rotate_left((idx as u32) & 31);
            state = Self::splitmix64(state);
        }
        let bases = [b'A', b'C', b'G', b'T'];
        let mut motif = String::with_capacity(15);
        let mut tmp = state;
        for triplet in 0..4 {
            if triplet > 0 {
                motif.push('-');
            }
            for _ in 0..3 {
                motif.push(bases[(tmp & 3) as usize] as char);
                tmp >>= 2;
            }
        }
        (state, motif)
    }

    fn canonicalize_concept(node: &ConceptNode) -> String {
        let mut trait_keys: Vec<String> = node.traits.keys().cloned().collect();
        trait_keys.sort();
        let mut words_sorted = node.grounded_words.clone();
        words_sorted.sort();
        format!(
            "name={}|words={:?}|traits={:?}",
            node.name, words_sorted, trait_keys
        )
    }

    fn canonicalize_episode(ep: &EpisodicMemory) -> String {
        format!(
            "id={}|tick={}|prov={}|sum={}|concepts={:?}|out={:?}",
            ep.episode_id,
            ep.tick,
            ep.provenance,
            ep.summary,
            ep.active_concepts,
            ep.outcome_traits
        )
    }

    fn canonicalize_rule(rule: &CausalRule) -> String {
        let mut pred_sorted: Vec<(String, i32)> = rule
            .predicted_outcomes
            .iter()
            .map(|(k, v)| (k.clone(), (*v * 1000.0) as i32))
            .collect();
        pred_sorted.sort_by(|a, b| a.0.cmp(&b.0));
        let mut exc_sorted: Vec<(String, String)> = rule
            .learned_exceptions
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();
        exc_sorted.sort_by(|a, b| a.0.cmp(&b.0));
        format!(
            "trig={:?}|act={}|pred={:?}|exc={:?}",
            rule.trigger_traits,
            rule.action,
            pred_sorted,
            exc_sorted,
        )
    }

    /// Seals all current concepts, episodic memories, and causal rules into Alpha 7's private genetic vault.
    pub fn seal_organism_state(
        &mut self,
        concepts: &FxHashMap<String, ConceptNode>,
        episodes: &[EpisodicMemory],
        rules: &[CausalRule],
    ) -> usize {
        self.generation_epoch = self.generation_epoch.saturating_add(1);
        self.sealed_loci.clear();

        for (name, node) in concepts {
            let locus = format!("concept:{}", name);
            let canon = Self::canonicalize_concept(node);
            let (mac, motif) = self.compute_private_codon(&locus, &canon);
            let backup = serde_json::to_string(node).unwrap_or_default();
            self.sealed_loci.insert(
                locus.clone(),
                GeneticCodonRecord {
                    locus_id: locus,
                    codon_mac: mac,
                    tri_nucleotide_motif: motif,
                    holographic_backup_json: backup,
                },
            );
        }

        for ep in episodes {
            let locus = format!("episode:{}", ep.episode_id);
            let canon = Self::canonicalize_episode(ep);
            let (mac, motif) = self.compute_private_codon(&locus, &canon);
            let backup = serde_json::to_string(ep).unwrap_or_default();
            self.sealed_loci.insert(
                locus.clone(),
                GeneticCodonRecord {
                    locus_id: locus,
                    codon_mac: mac,
                    tri_nucleotide_motif: motif,
                    holographic_backup_json: backup,
                },
            );
        }

        for (idx, rule) in rules.iter().enumerate() {
            let locus = format!("rule:{}:{}", idx, rule.action);
            let canon = Self::canonicalize_rule(rule);
            let (mac, motif) = self.compute_private_codon(&locus, &canon);
            let backup = serde_json::to_string(rule).unwrap_or_default();
            self.sealed_loci.insert(
                locus.clone(),
                GeneticCodonRecord {
                    locus_id: locus,
                    codon_mac: mac,
                    tri_nucleotide_motif: motif,
                    holographic_backup_json: backup,
                },
            );
        }

        self.sealed_loci.len()
    }

    /// Audits the organism's memories, concepts, and causal rules against its private genetic codons:
    /// - Identifies any tampered/modified locus, deleted/lost locus, or newly added/upgraded locus.
    /// - If `auto_heal == true`, restores tampered and deleted memories from holographic backups and seals legitimate upgrades.
    pub fn audit_and_heal_organism(
        &mut self,
        concepts: &mut FxHashMap<String, ConceptNode>,
        episodes: &mut Vec<EpisodicMemory>,
        rules: &mut Vec<CausalRule>,
        auto_heal: bool,
    ) -> GeneticAuditReport {
        let mut mutations = Vec::new();
        let mut intact_count = 0usize;
        let mut healed_count = 0usize;
        let mut newly_sealed = 0usize;
        let mut seen_loci = std::collections::HashSet::new();

        // 1. Check live concepts against sealed codons
        let concept_keys: Vec<String> = concepts.keys().cloned().collect();
        for name in concept_keys {
            let locus = format!("concept:{}", name);
            seen_loci.insert(locus.clone());
            let node = &concepts[&name];
            let canon = Self::canonicalize_concept(node);
            let (obs_mac, obs_motif) = self.compute_private_codon(&locus, &canon);

            if let Some(rec) = self.sealed_loci.get(&locus).cloned() {
                if rec.codon_mac == obs_mac {
                    intact_count += 1;
                } else {
                    let mut restored = false;
                    if auto_heal {
                        if let Ok(orig_node) =
                            serde_json::from_str::<ConceptNode>(&rec.holographic_backup_json)
                        {
                            concepts.insert(name.clone(), orig_node);
                            restored = true;
                            healed_count += 1;
                        }
                    }
                    mutations.push(GeneticMutationFinding {
                        locus_id: locus,
                        kind: GeneticMutationKind::TamperedModified,
                        expected_codon_motif: rec.tri_nucleotide_motif,
                        observed_codon_motif: obs_motif,
                        healed: restored,
                        details: format!(
                            "Concept '{}' memory engram was externally altered; {} from private holographic codon.",
                            name,
                            if restored { "RESTORED" } else { "FLAGGED" }
                        ),
                    });
                }
            } else {
                // Newly added concept (upgrade or new learning)
                if auto_heal {
                    let backup = serde_json::to_string(node).unwrap_or_default();
                    self.sealed_loci.insert(
                        locus.clone(),
                        GeneticCodonRecord {
                            locus_id: locus.clone(),
                            codon_mac: obs_mac,
                            tri_nucleotide_motif: obs_motif.clone(),
                            holographic_backup_json: backup,
                        },
                    );
                    newly_sealed += 1;
                }
                mutations.push(GeneticMutationFinding {
                    locus_id: locus,
                    kind: GeneticMutationKind::AddedOrUpgraded,
                    expected_codon_motif: "NONE (New)".to_string(),
                    observed_codon_motif: obs_motif,
                    healed: auto_heal,
                    details: format!("Identified newly added/upgraded concept '{}'.", name),
                });
            }
        }

        // 2. Check live episodes against sealed codons
        for idx in 0..episodes.len() {
            let locus = format!("episode:{}", episodes[idx].episode_id);
            seen_loci.insert(locus.clone());
            let canon = Self::canonicalize_episode(&episodes[idx]);
            let (obs_mac, obs_motif) = self.compute_private_codon(&locus, &canon);

            if let Some(rec) = self.sealed_loci.get(&locus).cloned() {
                if rec.codon_mac == obs_mac {
                    intact_count += 1;
                } else {
                    let mut restored = false;
                    if auto_heal {
                        if let Ok(orig_ep) =
                            serde_json::from_str::<EpisodicMemory>(&rec.holographic_backup_json)
                        {
                            episodes[idx] = orig_ep;
                            restored = true;
                            healed_count += 1;
                        }
                    }
                    mutations.push(GeneticMutationFinding {
                        locus_id: locus,
                        kind: GeneticMutationKind::TamperedModified,
                        expected_codon_motif: rec.tri_nucleotide_motif,
                        observed_codon_motif: obs_motif,
                        healed: restored,
                        details: format!(
                            "Episodic memory #{} was externally tampered with; {} from private genetic codon.",
                            episodes[idx].episode_id,
                            if restored { "RESTORED" } else { "FLAGGED" }
                        ),
                    });
                }
            } else {
                if auto_heal {
                    let backup = serde_json::to_string(&episodes[idx]).unwrap_or_default();
                    self.sealed_loci.insert(
                        locus.clone(),
                        GeneticCodonRecord {
                            locus_id: locus.clone(),
                            codon_mac: obs_mac,
                            tri_nucleotide_motif: obs_motif.clone(),
                            holographic_backup_json: backup,
                        },
                    );
                    newly_sealed += 1;
                }
                mutations.push(GeneticMutationFinding {
                    locus_id: locus,
                    kind: GeneticMutationKind::AddedOrUpgraded,
                    expected_codon_motif: "NONE (New)".to_string(),
                    observed_codon_motif: obs_motif,
                    healed: auto_heal,
                    details: format!(
                        "Identified newly recorded episodic memory #{}.",
                        episodes[idx].episode_id
                    ),
                });
            }
        }

        // 3. Check live rules against sealed codons
        for idx in 0..rules.len() {
            let locus = format!("rule:{}:{}", idx, rules[idx].action);
            seen_loci.insert(locus.clone());
            let canon = Self::canonicalize_rule(&rules[idx]);
            let (obs_mac, obs_motif) = self.compute_private_codon(&locus, &canon);
            if let Some(rec) = self.sealed_loci.get(&locus).cloned() {
                if rec.codon_mac == obs_mac {
                    intact_count += 1;
                } else {
                    let mut restored = false;
                    if auto_heal {
                        if let Ok(orig_rule) =
                            serde_json::from_str::<CausalRule>(&rec.holographic_backup_json)
                        {
                            rules[idx] = orig_rule;
                            restored = true;
                            healed_count += 1;
                        }
                    }
                    mutations.push(GeneticMutationFinding {
                        locus_id: locus,
                        kind: GeneticMutationKind::TamperedModified,
                        expected_codon_motif: rec.tri_nucleotide_motif,
                        observed_codon_motif: obs_motif,
                        healed: restored,
                        details: format!(
                            "Causal rule '{}' was modified; {} from private genetic codon.",
                            rules[idx].action,
                            if restored { "RESTORED" } else { "FLAGGED" }
                        ),
                    });
                }
            }
        }

        // 4. Detect Deleted / Lost loci (damage or erasure) and regenerate them!
        let missing_loci: Vec<GeneticCodonRecord> = self
            .sealed_loci
            .values()
            .filter(|rec| !seen_loci.contains(&rec.locus_id))
            .cloned()
            .collect();

        for rec in missing_loci {
            let mut restored = false;
            if auto_heal {
                if rec.locus_id.starts_with("concept:") {
                    if let Ok(orig_node) =
                        serde_json::from_str::<ConceptNode>(&rec.holographic_backup_json)
                    {
                        concepts.insert(orig_node.name.clone(), orig_node);
                        restored = true;
                        healed_count += 1;
                    }
                } else if rec.locus_id.starts_with("episode:") {
                    if let Ok(orig_ep) =
                        serde_json::from_str::<EpisodicMemory>(&rec.holographic_backup_json)
                    {
                        episodes.push(orig_ep);
                        episodes.sort_by_key(|e| e.episode_id);
                        restored = true;
                        healed_count += 1;
                    }
                } else if rec.locus_id.starts_with("rule:") {
                    if let Ok(orig_rule) =
                        serde_json::from_str::<CausalRule>(&rec.holographic_backup_json)
                    {
                        rules.push(orig_rule);
                        restored = true;
                        healed_count += 1;
                    }
                }
            }
            mutations.push(GeneticMutationFinding {
                locus_id: rec.locus_id.clone(),
                kind: GeneticMutationKind::DeletedLost,
                expected_codon_motif: rec.tri_nucleotide_motif,
                observed_codon_motif: "MISSING (Erased/Damaged)".to_string(),
                healed: restored,
                details: format!(
                    "Locus '{}' was erased/damaged; {} from private holographic engram.",
                    rec.locus_id,
                    if restored { "REGENERATED" } else { "DETECTED" }
                ),
            });
        }

        let summary = format!(
            "Somatic Genetic Audit (Epoch #{}): {} intact loci, {} mutations/changes detected ({} healed/regenerated, {} newly sealed upgrades).",
            self.generation_epoch,
            intact_count,
            mutations.len(),
            healed_count,
            newly_sealed
        );

        GeneticAuditReport {
            intact_loci_count: intact_count,
            mutations_detected: mutations,
            healed_loci_count: healed_count,
            newly_sealed_upgrades: newly_sealed,
            summary,
        }
    }
}

// ============================================================================
// 3. UNIVERSAL SIGNAL DECODER, BELIEF CHAINS & EPISTEMIC SOVEREIGNTY ENGINE
// ============================================================================

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum EpistemicTier {
    /// Verified directly by Alpha 7's own mathematical calculation or code execution (`100% sovereign certainty`).
    SelfProvedCalculation,
    /// Verified directly by Alpha 7's own physical action & sensory outcome observation.
    SelfProvedExperiment,
    /// Conventional human word/label mapped to a grounded sensory invariant (`revocable naming convention`).
    GroundedLexicalConvention,
    /// Contradicts Alpha 7's own independent calculation or lived physical experiment (`rejected falsehood`).
    RefutedByOwnReasoning,
    /// Unverified external claim with no self-proof or sensory grounding (`held in epistemic quarantine`).
    QuarantinedDoubt,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpistemicJudgment {
    pub raw_claim: String,
    pub tier: EpistemicTier,
    pub accepted_into_beliefs: bool,
    pub independent_proof_trace: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperienceChainLink {
    pub step_index: u64,
    pub signal_kind: String,
    pub normalized_values: Vec<f32>,
    pub invariant_traits: Vec<String>,
    pub summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecodedUniversalSignal {
    pub detected_modality: String,
    pub raw_numbers: Vec<f64>,
    pub weber_fechner_normalized: Vec<f32>,
    pub extracted_traits: Vec<String>,
    pub decoded_meaning: String,
}

/// Normalizes arbitrary continuous numeric streams, structured JSON/KV payloads, hex byte streams,
/// and natural language into Weber-Fechner invariant neural traits, and evaluates external claims
/// exclusively through Alpha 7's own independent calculations and lived experiments.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpistemicSovereigntyEngine {
    pub running_mean: f64,
    pub running_var: f64,
    pub samples_seen: u64,
    pub experience_chain: Vec<ExperienceChainLink>,
    pub verified_beliefs: Vec<EpistemicJudgment>,
}

impl Default for EpistemicSovereigntyEngine {
    fn default() -> Self {
        Self {
            running_mean: 0.0,
            running_var: 1.0,
            samples_seen: 0,
            experience_chain: Vec::new(),
            verified_beliefs: Vec::new(),
        }
    }
}

impl EpistemicSovereigntyEngine {
    /// Decodes and normalizes ANY incoming signal (continuous numbers, telemetry JSON/KV, hex bytes, or text)
    /// using homeostatic Welford running statistics and Weber-Fechner `asinh((x - \mu)/\sigma)` compression.
    pub fn decode_and_normalize_any_signal(&mut self, raw_signal: &str) -> DecodedUniversalSignal {
        let trimmed = raw_signal.trim();
        let mut raw_nums = Vec::new();
        let mut extracted_traits = Vec::new();

        // 1. Check if hex byte stream (e.g., "0x48 0x69")
        let hex_tokens: Vec<&str> = trimmed.split_whitespace().collect();
        if !hex_tokens.is_empty() && hex_tokens.iter().all(|t| t.starts_with("0x") || t.starts_with("0X")) {
            let mut decoded_bytes = Vec::new();
            for tok in &hex_tokens {
                if let Ok(b) = u8::from_str_radix(&tok[2..], 16) {
                    decoded_bytes.push(b);
                    raw_nums.push(b as f64);
                }
            }
            let ascii_str = String::from_utf8_lossy(&decoded_bytes).to_string();
            extracted_traits.push("signal:binary_hex_stream".to_string());
            extracted_traits.push(format!("signal:decoded_ascii_{}", ascii_str.to_lowercase()));
            let wf = self.apply_weber_fechner(&raw_nums);
            let meaning = format!("Decoded hex byte stream ({} bytes) -> ASCII \"{}\"", decoded_bytes.len(), ascii_str);
            self.record_experience_link("hex_stream", &wf, &extracted_traits, &meaning);
            return DecodedUniversalSignal {
                detected_modality: "binary_hex_stream".to_string(),
                raw_numbers: raw_nums,
                weber_fechner_normalized: wf,
                extracted_traits,
                decoded_meaning: meaning,
            };
        }

        // 2. Extract any embedded continuous floating-point numbers from the signal
        for token in trimmed.split(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-')) {
            if !token.is_empty() && token != "-" && token != "." {
                if let Ok(val) = token.parse::<f64>() {
                    if val.is_finite() {
                        raw_nums.push(val);
                    }
                }
            }
        }

        let wf = self.apply_weber_fechner(&raw_nums);

        // 3. Extract universal relational invariants from numeric trajectories (monotonicity, doubling, constancy)
        if raw_nums.len() >= 3 {
            let mut strictly_inc = true;
            let mut strictly_dec = true;
            let mut constant_step = true;
            let mut constant_ratio = true;
            let d0 = raw_nums[1] - raw_nums[0];
            let r0 = if raw_nums[0].abs() > 1e-6 {
                raw_nums[1] / raw_nums[0]
            } else {
                0.0
            };

            for w in raw_nums.windows(2) {
                let diff = w[1] - w[0];
                if diff <= 0.0 {
                    strictly_inc = false;
                }
                if diff >= 0.0 {
                    strictly_dec = false;
                }
                if (diff - d0).abs() > 1e-3 {
                    constant_step = false;
                }
                if w[0].abs() <= 1e-6 || ((w[1] / w[0]) - r0).abs() > 1e-2 {
                    constant_ratio = false;
                }
            }

            if strictly_inc {
                extracted_traits.push("signal:invariant_monotonic_increasing".to_string());
            } else if strictly_dec {
                extracted_traits.push("signal:invariant_monotonic_decreasing".to_string());
            } else {
                extracted_traits.push("signal:invariant_oscillating_nonmonotonic".to_string());
            }

            if constant_step {
                extracted_traits.push(format!("signal:arithmetic_progression_step_{:.1}", d0));
            }
            if constant_ratio && r0.abs() > 1e-3 {
                extracted_traits.push(format!("signal:geometric_scaling_ratio_{:.2}", r0));
            }
        }

        let detected_modality = if trimmed.starts_with('{') && trimmed.ends_with('}') {
            extracted_traits.push("signal:structured_json_payload".to_string());
            "structured_json"
        } else if raw_nums.len() >= 3 {
            "continuous_numeric_stream"
        } else {
            extracted_traits.push("signal:symbolic_linguistic_stream".to_string());
            "symbolic_linguistic"
        };

        let meaning = format!(
            "Universal Signal Decoded [{}]: {} numeric samples -> Weber-Fechner normalized {:?}, invariants={:?}",
            detected_modality,
            raw_nums.len(),
            wf,
            extracted_traits
        );
        self.record_experience_link(detected_modality, &wf, &extracted_traits, &meaning);

        DecodedUniversalSignal {
            detected_modality: detected_modality.to_string(),
            raw_numbers: raw_nums,
            weber_fechner_normalized: wf,
            extracted_traits,
            decoded_meaning: meaning,
        }
    }

    fn apply_weber_fechner(&mut self, values: &[f64]) -> Vec<f32> {
        let mut out = Vec::with_capacity(values.len());
        for &x in values {
            self.samples_seen += 1;
            let n = self.samples_seen as f64;
            let delta = x - self.running_mean;
            self.running_mean += delta / n;
            let delta2 = x - self.running_mean;
            self.running_var = if n > 1.0 {
                ((n - 2.0) * self.running_var + delta * delta2) / (n - 1.0)
            } else {
                1.0
            };
            let std = self.running_var.max(1e-4).sqrt();
            let z = (x - self.running_mean) / std;
            // Weber-Fechner logarithmic compression via inverse hyperbolic sine `asinh(z)`
            out.push((z.asinh() as f32).clamp(-4.0, 4.0));
        }
        out
    }

    fn record_experience_link(
        &mut self,
        kind: &str,
        wf: &[f32],
        traits: &[String],
        summary: &str,
    ) {
        let idx = (self.experience_chain.len() as u64) + 1;
        self.experience_chain.push(ExperienceChainLink {
            step_index: idx,
            signal_kind: kind.to_string(),
            normalized_values: wf.to_vec(),
            invariant_traits: traits.to_vec(),
            summary: summary.to_string(),
        });
        if self.experience_chain.len() > 256 {
            self.experience_chain.remove(0);
        }
    }

    /// Evaluates an incoming claim or proposition using Alpha 7's own independent calculation (`BodyMotor`),
    /// lived causal experiments (`PredictiveEngine`), or grounded lexical convention (`WordLedger`).
    /// Never trusts external authority over its own proof!
    pub fn evaluate_claim_sovereignly(
        &mut self,
        claim: &str,
        body: &Alpha7Body,
        predictor: &PredictiveEngine,
    ) -> EpistemicJudgment {
        let clean = claim
            .trim()
            .strip_prefix("claim:")
            .unwrap_or(claim.trim())
            .trim();

        // 1. Check if the claim is a mathematical/arithmetic equality `LHS = RHS`
        if let Some((lhs_raw, rhs_raw)) = clean.split_once('=') {
            let lhs = lhs_raw.trim();
            let rhs = rhs_raw.trim();
            if let Ok(claimed_rhs) = rhs.parse::<i64>() {
                let code = format!("result = {}", lhs);
                let exec_traits = body.hands.execute_small_code(&code);
                let computed_val = exec_traits
                    .iter()
                    .find_map(|t| t.strip_prefix("eyes:result_")?.parse::<i64>().ok())
                    .or_else(|| {
                        body.hands
                            .eval_program_stdout(&format!("result = {}\nprint(result)", lhs))?
                            .trim()
                            .parse::<i64>()
                            .ok()
                    });
                if let Some(actual_val) = computed_val {
                    if actual_val == claimed_rhs {
                        let j = EpistemicJudgment {
                            raw_claim: clean.to_string(),
                            tier: EpistemicTier::SelfProvedCalculation,
                            accepted_into_beliefs: true,
                            independent_proof_trace: format!(
                                "ACCEPTED [SelfProvedCalculation]: Independently computed `{}` = {} (matches claimed {}).",
                                lhs, actual_val, claimed_rhs
                            ),
                        };
                        self.verified_beliefs.push(j.clone());
                        return j;
                    } else {
                        let j = EpistemicJudgment {
                            raw_claim: clean.to_string(),
                            tier: EpistemicTier::RefutedByOwnReasoning,
                            accepted_into_beliefs: false,
                            independent_proof_trace: format!(
                                "REJECTED [RefutedByOwnReasoning]: External source claimed `{} = {}`, but my own independent calculation proves `{} = {}`.",
                                lhs, claimed_rhs, lhs, actual_val
                            ),
                        };
                        self.verified_beliefs.push(j.clone());
                        return j;
                    }
                }
            }
        }

        // 2. Check if the claim is a causal world proposition `<action> causes <outcome>`
        let low = clean.to_lowercase();
        if let Some((act_part, out_part)) = low.split_once(" causes ") {
            let action = act_part.trim();
            let claimed_outcome = out_part.trim();
            let matching_rules: Vec<&CausalRule> = predictor
                .rules
                .iter()
                .filter(|r| r.action.to_lowercase() == action)
                .collect();

            if !matching_rules.is_empty() {
                let confirmed = matching_rules.iter().any(|r| {
                    r.predicted_outcomes
                        .keys()
                        .any(|o| o.to_lowercase().contains(claimed_outcome))
                });
                if confirmed {
                    let j = EpistemicJudgment {
                        raw_claim: clean.to_string(),
                        tier: EpistemicTier::SelfProvedExperiment,
                        accepted_into_beliefs: true,
                        independent_proof_trace: format!(
                            "ACCEPTED [SelfProvedExperiment]: Lived sensory-motor experiment confirms action '{}' produces '{}'.",
                            action, claimed_outcome
                        ),
                    };
                    self.verified_beliefs.push(j.clone());
                    return j;
                } else {
                    let actual_outcomes: Vec<String> = matching_rules
                        .iter()
                        .flat_map(|r| r.predicted_outcomes.keys().cloned())
                        .collect();
                    let j = EpistemicJudgment {
                        raw_claim: clean.to_string(),
                        tier: EpistemicTier::RefutedByOwnReasoning,
                        accepted_into_beliefs: false,
                        independent_proof_trace: format!(
                            "REJECTED [RefutedByOwnReasoning]: External source claimed '{}' causes '{}', but my lived experiments prove '{}' causes {:?}.",
                            action, claimed_outcome, action, actual_outcomes
                        ),
                    };
                    self.verified_beliefs.push(j.clone());
                    return j;
                }
            }
        }

        // 3. Check if it is a grounded lexical naming convention `word <w> means <concept>`
        if low.starts_with("word ") && low.contains(" means ") {
            let j = EpistemicJudgment {
                raw_claim: clean.to_string(),
                tier: EpistemicTier::GroundedLexicalConvention,
                accepted_into_beliefs: true,
                independent_proof_trace: format!(
                    "ACCEPTED [GroundedLexicalConvention]: Stored '{}' as a conventional linguistic label (subject to sensory prediction verification).",
                    clean
                ),
            };
            self.verified_beliefs.push(j.clone());
            return j;
        }

        // 4. Otherwise hold in epistemic quarantine until proved by calculation or experiment
        let j = EpistemicJudgment {
            raw_claim: clean.to_string(),
            tier: EpistemicTier::QuarantinedDoubt,
            accepted_into_beliefs: false,
            independent_proof_trace: format!(
                "QUARANTINED [QuarantinedDoubt]: Claim '{}' has no independent mathematical proof or lived sensory experiment yet; held as unverified hypothesis.",
                clean
            ),
        };
        self.verified_beliefs.push(j.clone());
        j
    }
}

// ============================================================================
// 4. MULTI-PARALLEL 6-LOOP BRAIN ORCHESTRATOR
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParallelCognitiveCycleReport {
    pub loop1_sensory_normalization: String,
    pub loop2_working_memory_binding: String,
    pub loop3_quantum_bifurcation_understanding: String,
    pub loop4_covert_counterfactual_rollout: String,
    pub loop5_epistemic_sovereignty_judgment: String,
    pub loop6_genetic_immune_and_drives: String,
    pub drive_mode: DriveMode,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SovereignQuantumBrain {
    pub quantum_settler: QuantumBifurcationSettler,
    pub genetic_vault: EndogenousGeneticVault,
    pub epistemic_engine: EpistemicSovereigntyEngine,
    pub parallel_cycles_completed: u64,
}

impl SovereignQuantumBrain {
    /// Executes all 6 Multi-Parallel Brain Loops in a single coordinated cognitive cycle:
    /// - Loop 1 (Gamma 40-80 Hz): Universal Continuous Signal Decoding & Weber-Fechner Normalization
    /// - Loop 2 (Theta-Gamma 4-8 Hz): `CORE` Multi-Timescale Working Memory & `KenyonBinder` Context Expansion
    /// - Loop 3 (Alpha/Beta 10-20 Hz): Software Quantum Annealing (`dSB` + $P$-Replica Trotter Tunneling)
    /// - Loop 4 (Sharp-Wave Ripple): Covert Multi-Hop Counterfactual Rollout (`\tilde{\Omega}^{slow}` + `S^-` Veto)
    /// - Loop 5 (Prefrontal-Cerebellar Logic): Epistemic Sovereignty Proof & Experience-Chain Update
    /// - Loop 6 (Autonomic/Immune): Somatic Genetic Codon Verification, Self-Healing & Homeostatic Drives
    pub fn run_six_parallel_loops(
        &mut self,
        incoming_signal: &str,
        substrate: &mut CorticalSubstrate,
        body: &Alpha7Body,
        predictor: &mut PredictiveEngine,
        concepts: &mut FxHashMap<String, ConceptNode>,
        episodes: &mut Vec<EpisodicMemory>,
    ) -> ParallelCognitiveCycleReport {
        self.parallel_cycles_completed += 1;

        // Loop 1: Universal Signal Decoding & Weber-Fechner Normalization
        let decoded = self
            .epistemic_engine
            .decode_and_normalize_any_signal(incoming_signal);

        // Loop 2: Multi-Timescale Working Memory (`CORE`) & Kenyon Conjunctive Binding
        let mut sym_ids = Vec::new();
        for tr in &decoded.extracted_traits {
            let sid = substrate
                .helmholtz
                .ensure_symbol(tr, crate::neuron::Modality::Association);
            sym_ids.push(sid);
        }
        substrate.core_hierarchy.step(&sym_ids, false);
        let kc = substrate
            .kenyon
            .bind_conjunctive(incoming_signal, &decoded.detected_modality);
        let loop2_msg = format!(
            "CORE L=4 sustained={:.2}, Kenyon active={}/{}",
             sym_ids
                .first()
                .map(|&id| substrate.core_hierarchy.sustained_activation(id))
                .unwrap_or(0.0),
            kc.len(),
            substrate.kenyon.n_kenyon
        );

        // Loop 3: Quantum-Annealed Simulated Bifurcation (`dSB` + Trotter Replicas) over active concepts
        let cand_names: Vec<String> = concepts.keys().take(8).cloned().collect();
        let loop3_msg = if cand_names.len() >= 2 {
            let n = cand_names.len();
            let mut h = vec![0.25f32; n];
            let mut j_mat = vec![vec![0.0f32; n]; n];
            for i in 0..n {
                if incoming_signal
                    .to_lowercase()
                    .contains(&cand_names[i].to_lowercase())
                {
                    h[i] += 0.65;
                }
                for j in (i + 1)..n {
                    let id_i = substrate
                        .helmholtz
                        .symbol_to_id
                        .get(&cand_names[i])
                        .copied()
                        .unwrap_or(0);
                    let id_j = substrate
                        .helmholtz
                        .symbol_to_id
                        .get(&cand_names[j])
                        .copied()
                        .unwrap_or(0);
                    let sp = *substrate.helmholtz.s_plus.get(&(id_i, id_j)).unwrap_or(&0.0);
                    let sm = *substrate.helmholtz.s_minus.get(&(id_i, id_j)).unwrap_or(&0.0);
                    let coupling = sp - 1.25 * sm;
                    j_mat[i][j] = coupling;
                    j_mat[j][i] = coupling;
                }
            }
            let q_res = self
                .quantum_settler
                .settle_frustrated_network(&cand_names, &h, &j_mat);
            format!(
                "dSB+Trotter winner='{}' (E_q={:.2} vs E_greedy={:.2}, replica_agree={:.0}%)",
                q_res.winner_concept,
                q_res.quantum_ground_energy,
                q_res.classical_greedy_energy,
                q_res.replicas_agreement * 100.0
            )
        } else {
            "dSB+Trotter standby (<2 concepts seeded)".to_string()
        };

        // Loop 4: Covert Multi-Hop Rollout
        let rollout_msg = if let Some(path) = substrate.simulate_covert_rollout(
            "room_start",
            "goal_vault",
            &["door_is_locked".to_string()],
            4,
        ) {
            format!("Covert path: {}", path.join(" -> "))
        } else {
            "Covert rollout idle (no active goal graph)".to_string()
        };

        // Loop 5: Epistemic Sovereignty Evaluation
        let judgment = self
            .epistemic_engine
            .evaluate_claim_sovereignly(incoming_signal, body, predictor);

        // Loop 6: Autonomic Somatic Genetic Audit, Self-Healing & Homeostatic Drive Step
        let audit = if self.genetic_vault.sealed_loci.is_empty() {
            let count = self
                .genetic_vault
                .seal_organism_state(concepts, episodes, &predictor.rules);
            format!("Initial Somatic Genetic Seal applied across {} loci", count)
        } else {
            let rep = self.genetic_vault.audit_and_heal_organism(
                concepts,
                episodes,
                &mut predictor.rules,
                true,
            );
            rep.summary
        };
        let novelty = if judgment.accepted_into_beliefs {
            0.65
        } else {
            0.35
        };
        let drive_mode = substrate.drives.step_drives(novelty, 0.20);

        ParallelCognitiveCycleReport {
            loop1_sensory_normalization: decoded.decoded_meaning,
            loop2_working_memory_binding: loop2_msg,
            loop3_quantum_bifurcation_understanding: loop3_msg,
            loop4_covert_counterfactual_rollout: rollout_msg,
            loop5_epistemic_sovereignty_judgment: judgment.independent_proof_trace,
            loop6_genetic_immune_and_drives: audit,
            drive_mode,
        }
    }
}
