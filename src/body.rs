//! Alpha 7 Pure-Rust 5-Sense Embodied Interface (Eyes, Ears, Hands, Smell, Internal Senses)
//!
//! Phase 2 Upgrades:
//! - Phase 2A: Real Raw-Pixel V1/V2 Visual Cortex (`V1RetinaGlance`) decoding actual `.jpg`, `.png`,
//!   and `.ppm` files on disk into Sobel orientation energy (horizontal/vertical/diagonal),
//!   center-surround contrast, bilateral symmetry, chromatic family, 16x16 V1 cortical grid,
//!   and 4 salience saccade fixation windows.
//! - Phase 2A: Real Raw-Waveform Cochlear Audio Analyzer (`CochlearAnalysis`) parsing PCM `.wav`
//!   files into zero-crossing rate, RMS energy, 3-band spectral profile, and 32-bin envelope.
//! - Phase 2C: Enhanced Native Rust Code Sandbox in `HandsEffector` supporting multi-line variables,
//!   bounded `for` loops, arithmetic (`+`, `-`, `*`, `/`), and zero-division / syntax fault detection.

use image::GenericImageView;
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

/// Real V1/V2 visual cortex analysis extracted from raw image pixels on disk.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct V1RetinaGlance {
    pub source_path: String,
    pub width: u32,
    pub height: u32,
    pub mean_luminance: f32,
    pub contrast_std: f32,
    pub horizontal_edge_energy: f32,
    pub vertical_edge_energy: f32,
    pub diagonal_edge_energy: f32,
    pub center_surround_delta: f32,
    pub bilateral_symmetry: f32,
    pub dominant_hue_family: String,
    /// Top 4 saccade fixation windows `[top_pct, left_pct, side_pct]` in `[0.0, 100.0]`.
    pub fixation_windows: Vec<[f32; 3]>,
    /// 16x16 (256-element) downsampled V1 cortical luminance grid (`0..=255`).
    pub retina_grid_16x16: Vec<u8>,
    /// Grounded `eyes:*` traits computed directly from raw pixels.
    pub extracted_traits: Vec<String>,
}

/// Real cochlear waveform analysis extracted from raw `.wav` audio or acoustic streams.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CochlearAnalysis {
    pub source_path: String,
    pub sample_rate: u32,
    pub duration_ms: u32,
    pub rms_energy: f32,
    pub zero_crossing_rate: f32,
    pub low_band_energy: f32,
    pub mid_band_energy: f32,
    pub high_band_energy: f32,
    pub waveform_envelope_32: Vec<u8>,
    pub extracted_traits: Vec<String>,
}

/// A unified multi-modal sensory snapshot captured by Alpha 7's 5 senses on a single tick.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SensoryFrame {
    pub eyes: Vec<String>,
    pub ears: Vec<String>,
    pub hands: Vec<String>,
    pub smell: Vec<String>,
    pub senses: Vec<String>,
    pub spoken_words: Vec<String>,
}

impl SensoryFrame {
    pub fn new() -> Self {
        Self::default()
    }

    /// Flattens all 5 sensory streams into grounded modality-prefixed neural trait keys.
    pub fn to_neural_traits(&self) -> Vec<String> {
        let mut traits = Vec::with_capacity(
            self.eyes.len()
                + self.ears.len()
                + self.hands.len()
                + self.smell.len()
                + self.senses.len(),
        );
        for item in &self.eyes {
            traits.push(if item.starts_with("eyes:") {
                item.clone()
            } else {
                format!("eyes:{}", item)
            });
        }
        for item in &self.ears {
            traits.push(if item.starts_with("ears:") {
                item.clone()
            } else {
                format!("ears:{}", item)
            });
        }
        for item in &self.hands {
            traits.push(if item.starts_with("hands:") {
                item.clone()
            } else {
                format!("hands:{}", item)
            });
        }
        for item in &self.smell {
            traits.push(if item.starts_with("smell:") {
                item.clone()
            } else {
                format!("smell:{}", item)
            });
        }
        for item in &self.senses {
            traits.push(if item.starts_with("senses:") {
                item.clone()
            } else {
                format!("senses:{}", item)
            });
        }
        traits
    }
}

/// Visual processing organ: extracts structural traits from real images, 2D canvas fixations, and code.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EyesSensor {
    pub gaze_x: i32,
    pub gaze_y: i32,
    pub last_retina_glance: Option<V1RetinaGlance>,
}

impl EyesSensor {
    pub fn observe_entity(&self, features: &[&str]) -> Vec<String> {
        features
            .iter()
            .map(|f| {
                if f.starts_with("eyes:") {
                    (*f).to_string()
                } else {
                    format!("eyes:{}", f)
                }
            })
            .collect()
    }

    /// Phase 2A: Reads an actual `.jpg`, `.png`, or `.ppm` file from disk, projects it onto a
    /// 64x64 V1 working grid and 16x16 cortical display grid, and computes real edge orientations,
    /// center-surround contrast, bilateral symmetry, chromatic profile, and 4 saccade windows.
    pub fn analyze_image_file(&mut self, path: &str) -> Option<V1RetinaGlance> {
        let p = Path::new(path);
        if !p.is_file() {
            return None;
        }
        let img = image::open(p).ok()?;
        let (orig_w, orig_h) = img.dimensions();
        if orig_w == 0 || orig_h == 0 {
            return None;
        }

        // Sample onto a 64x64 V1 retinal patch for fast, deterministic feature extraction
        const N: usize = 64;
        let mut lum = [[0.0f32; N]; N];
        let mut r_sum = 0.0f32;
        let mut g_sum = 0.0f32;
        let mut b_sum = 0.0f32;
        let mut sat_sum = 0.0f32;
        let mut lum_sum = 0.0f32;

        for y in 0..N {
            let sy = ((y as u32) * orig_h / (N as u32)).min(orig_h - 1);
            for x in 0..N {
                let sx = ((x as u32) * orig_w / (N as u32)).min(orig_w - 1);
                let px = img.get_pixel(sx, sy).0;
                let r = (px[0] as f32) / 255.0;
                let g = (px[1] as f32) / 255.0;
                let b = (px[2] as f32) / 255.0;
                let l = (0.299 * r + 0.587 * g + 0.114 * b).clamp(0.0, 1.0);
                lum[y][x] = l;
                lum_sum += l;
                r_sum += r;
                g_sum += g;
                b_sum += b;
                let max_c = r.max(g).max(b);
                let min_c = r.min(g).min(b);
                sat_sum += max_c - min_c;
            }
        }

        let total_px = (N * N) as f32;
        let mean_lum = lum_sum / total_px;
        let mean_r = r_sum / total_px;
        let mean_g = g_sum / total_px;
        let mean_b = b_sum / total_px;
        let mean_sat = sat_sum / total_px;

        // Contrast (standard deviation) & Center-Surround difference
        let mut var_sum = 0.0f32;
        let mut center_sum = 0.0f32;
        let mut center_cnt = 0.0f32;
        let mut surround_sum = 0.0f32;
        let mut surround_cnt = 0.0f32;

        for y in 0..N {
            for x in 0..N {
                let d = lum[y][x] - mean_lum;
                var_sum += d * d;
                if (16..48).contains(&x) && (16..48).contains(&y) {
                    center_sum += lum[y][x];
                    center_cnt += 1.0;
                } else {
                    surround_sum += lum[y][x];
                    surround_cnt += 1.0;
                }
            }
        }
        let contrast_std = (var_sum / total_px).sqrt();
        let center_surround_delta =
            (center_sum / center_cnt.max(1.0)) - (surround_sum / surround_cnt.max(1.0));

        // Bilateral horizontal symmetry across vertical midline
        let mut sym_diff = 0.0f32;
        for y in 0..N {
            for x in 0..(N / 2) {
                sym_diff += (lum[y][x] - lum[y][N - 1 - x]).abs();
            }
        }
        let bilateral_symmetry = (1.0 - (sym_diff / ((N * (N / 2)) as f32))).clamp(0.0, 1.0);

        // V1 Simple Cell Sobel Edge Orientation Filters (Horizontal, Vertical, Diagonal)
        let mut horiz_e = 0.0f32;
        let mut vert_e = 0.0f32;
        let mut diag_e = 0.0f32;
        let mut salience_16 = [[0.0f32; 16]; 16];

        for y in 1..(N - 1) {
            for x in 1..(N - 1) {
                // Horizontal edge filter (gy)
                let gy = (lum[y - 1][x - 1] + 2.0 * lum[y - 1][x] + lum[y - 1][x + 1])
                    - (lum[y + 1][x - 1] + 2.0 * lum[y + 1][x] + lum[y + 1][x + 1]);
                // Vertical edge filter (gx)
                let gx = (lum[y - 1][x + 1] + 2.0 * lum[y][x + 1] + lum[y + 1][x + 1])
                    - (lum[y - 1][x - 1] + 2.0 * lum[y][x - 1] + lum[y + 1][x - 1]);
                // Diagonal edge filter
                let gd1 = (lum[y - 1][x] + lum[y][x + 1]) - (lum[y][x - 1] + lum[y + 1][x]);
                let gd2 = (lum[y - 1][x] + lum[y][x - 1]) - (lum[y][x + 1] + lum[y + 1][x]);

                let ah = gy.abs();
                let av = gx.abs();
                let ad = gd1.abs().max(gd2.abs());
                horiz_e += ah;
                vert_e += av;
                diag_e += ad;

                let cell_sal = ah + av + 0.5 * ad + (lum[y][x] - mean_lum).abs();
                salience_16[y / 4][x / 4] += cell_sal;
            }
        }

        let inner_px = ((N - 2) * (N - 2)) as f32;
        horiz_e /= inner_px;
        vert_e /= inner_px;
        diag_e /= inner_px;

        // Build 16x16 cortical retina grid (0..=255)
        let mut retina_grid_16x16 = Vec::with_capacity(256);
        for gy in 0..16 {
            for gx in 0..16 {
                let mut acc = 0.0f32;
                for dy in 0..4 {
                    for dx in 0..4 {
                        acc += lum[gy * 4 + dy][gx * 4 + dx];
                    }
                }
                let val = ((acc / 16.0) * 255.0).round().clamp(0.0, 255.0) as u8;
                retina_grid_16x16.push(val);
            }
        }

        // Top 4 non-overlapping salience windows for saccade fixations
        let mut cand_windows: Vec<(f32, usize, usize)> = Vec::new();
        for gy in 0..13 {
            for gx in 0..13 {
                let mut score = 0.0f32;
                for dy in 0..4 {
                    for dx in 0..4 {
                        score += salience_16[gy + dy][gx + dx];
                    }
                }
                cand_windows.push((score, gy, gx));
            }
        }
        cand_windows.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));

        let mut fixation_windows: Vec<[f32; 3]> = Vec::new();
        let mut chosen_coords: Vec<(i32, i32)> = Vec::new();
        for &(_sc, gy, gx) in &cand_windows {
            let iy = gy as i32;
            let ix = gx as i32;
            if chosen_coords
                .iter()
                .all(|&(cy, cx)| (iy - cy).abs() >= 3 || (ix - cx).abs() >= 3)
            {
                chosen_coords.push((iy, ix));
                let top_pct = ((gy as f32) / 16.0 * 100.0).clamp(0.0, 75.0);
                let left_pct = ((gx as f32) / 16.0 * 100.0).clamp(0.0, 75.0);
                fixation_windows.push([top_pct, left_pct, 25.0]);
                if fixation_windows.len() >= 4 {
                    break;
                }
            }
        }

        // Determine chromatic family
        let dominant_hue_family = if mean_sat < 0.08 {
            "achromatic_neutral".to_string()
        } else if mean_r > mean_g * 1.15 && mean_r > mean_b * 1.15 {
            "warm_red_amber".to_string()
        } else if mean_g > mean_r * 1.08 && mean_g > mean_b * 1.08 {
            "natural_green".to_string()
        } else if mean_b > mean_r * 1.12 && mean_b >= mean_g {
            "cool_blue_cyan".to_string()
        } else {
            "balanced_polychrome".to_string()
        };

        // Assemble grounded V1/V2 visual traits
        let mut extracted_traits = Vec::new();
        extracted_traits.push(format!("eyes:chroma_{}", dominant_hue_family));

        if horiz_e > vert_e * 1.12 && horiz_e >= diag_e {
            extracted_traits.push("eyes:v1_horiz_edges".to_string());
        } else if vert_e > horiz_e * 1.12 && vert_e >= diag_e {
            extracted_traits.push("eyes:v1_vert_edges".to_string());
        } else {
            extracted_traits.push("eyes:v1_multi_orientation_edges".to_string());
        }

        if contrast_std >= 0.22 {
            extracted_traits.push("eyes:v1_high_contrast".to_string());
        } else {
            extracted_traits.push("eyes:v1_soft_contrast".to_string());
        }

        if center_surround_delta.abs() >= 0.08 {
            extracted_traits.push("eyes:v2_figure_ground_separation".to_string());
        }
        if bilateral_symmetry >= 0.82 {
            extracted_traits.push("eyes:v2_bilateral_symmetry".to_string());
        }

        let ratio = (orig_w as f32) / (orig_h.max(1) as f32);
        if ratio > 1.18 {
            extracted_traits.push("eyes:aspect_landscape".to_string());
        } else if ratio < 0.85 {
            extracted_traits.push("eyes:aspect_portrait".to_string());
        } else {
            extracted_traits.push("eyes:aspect_square".to_string());
        }

        let glance = V1RetinaGlance {
            source_path: path.to_string(),
            width: orig_w,
            height: orig_h,
            mean_luminance: mean_lum,
            contrast_std,
            horizontal_edge_energy: horiz_e,
            vertical_edge_energy: vert_e,
            diagonal_edge_energy: diag_e,
            center_surround_delta,
            bilateral_symmetry,
            dominant_hue_family,
            fixation_windows,
            retina_grid_16x16,
            extracted_traits,
        };
        self.last_retina_glance = Some(glance.clone());
        Some(glance)
    }

    /// Extracts structural visual traits when Alpha 7 looks at a snippet of code.
    pub fn inspect_code(&self, code_str: &str) -> Vec<String> {
        let mut traits = vec!["eyes:code_block".to_string()];
        let trimmed = code_str.trim();

        // Check for obvious syntax errors (unbalanced parentheses, triple operators, trailing operators)
        let open_parens = trimmed.chars().filter(|&c| c == '(').count();
        let close_parens = trimmed.chars().filter(|&c| c == ')').count();
        let has_double_op = trimmed.contains("+ *")
            || trimmed.contains("* * *")
            || trimmed.contains("/ / /")
            || trimmed.ends_with('+')
            || trimmed.ends_with('*')
            || trimmed.ends_with('-');

        if open_parens != close_parens || has_double_op || trimmed.is_empty() {
            traits.push("eyes:syntax_typo".to_string());
            return traits;
        }

        traits.push("eyes:valid_syntax".to_string());
        if trimmed.contains("fn ") || trimmed.contains("def ") {
            traits.push("eyes:has_function_def".to_string());
        }
        if trimmed.contains("for ") || trimmed.contains("while ") {
            traits.push("eyes:has_loop".to_string());
        }
        if trimmed.contains("print") || trimmed.contains("println") {
            traits.push("eyes:calls_print".to_string());
        }
        if trimmed.contains('+') {
            traits.push("eyes:has_addition".to_string());
        }
        if trimmed.contains('*') {
            traits.push("eyes:has_multiplication".to_string());
        }
        if trimmed.contains('-') {
            traits.push("eyes:has_subtraction".to_string());
        }
        if trimmed.contains('/') {
            traits.push("eyes:has_division".to_string());
        }
        traits
    }
}

/// Auditory & lexical organ: perceives acoustic waveforms (`.wav`) and spoken words from the user.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EarsSensor {
    pub last_cochlear_analysis: Option<CochlearAnalysis>,
}

impl EarsSensor {
    pub fn listen(&self, sounds: &[&str], utterance: Option<&str>) -> (Vec<String>, Vec<String>) {
        let mut sound_traits: Vec<String> = sounds
            .iter()
            .map(|s| {
                if s.starts_with("ears:") {
                    (*s).to_string()
                } else {
                    format!("ears:{}", s)
                }
            })
            .collect();

        let mut words = Vec::new();
        if let Some(text) = utterance {
            for token in text.split(|c: char| !c.is_alphanumeric() && c != '_') {
                let clean = token.trim().to_lowercase();
                if !clean.is_empty() {
                    words.push(clean.clone());
                    sound_traits.push(format!("ears:heard_{}", clean));
                }
            }
        }
        (sound_traits, words)
    }

    /// Phase 2A: Native Rust RIFF/WAVE PCM cochlear analyzer.
    /// Reads `.wav` audio files, computes RMS energy, zero-crossing rate, 3-band spectral energy,
    /// and a 32-bin temporal envelope without any external audio C libraries.
    pub fn analyze_wav_file(&mut self, path: &str) -> Option<CochlearAnalysis> {
        let bytes = fs::read(path).ok()?;
        if bytes.len() < 44 || &bytes[0..4] != b"RIFF" || &bytes[8..12] != b"WAVE" {
            return None;
        }

        let channels = u16::from_le_bytes([bytes[22], bytes[23]]).max(1) as usize;
        let sample_rate =
            u32::from_le_bytes([bytes[24], bytes[25], bytes[26], bytes[27]]).max(8000);
        let bits_per_sample = u16::from_le_bytes([bytes[34], bytes[35]]);

        // Find the `data` chunk safely
        let mut pos = 12usize;
        let mut data_slice: &[u8] = &[];
        while pos + 8 <= bytes.len() {
            let chunk_id = &bytes[pos..pos + 4];
            let chunk_len = u32::from_le_bytes([
                bytes[pos + 4],
                bytes[pos + 5],
                bytes[pos + 6],
                bytes[pos + 7],
            ]) as usize;
            pos += 8;
            if chunk_id == b"data" {
                let end = (pos + chunk_len).min(bytes.len());
                data_slice = &bytes[pos..end];
                break;
            }
            pos = pos.saturating_add(chunk_len);
        }
        if data_slice.is_empty() {
            return None;
        }

        let mut samples: Vec<f32> = Vec::new();
        if bits_per_sample == 16 {
            let step = 2 * channels;
            let mut i = 0;
            while i + 1 < data_slice.len() {
                let s = i16::from_le_bytes([data_slice[i], data_slice[i + 1]]) as f32 / 32768.0;
                samples.push(s);
                i += step;
            }
        } else {
            let step = channels;
            let mut i = 0;
            while i < data_slice.len() {
                let s = ((data_slice[i] as f32) - 128.0) / 128.0;
                samples.push(s);
                i += step;
            }
        }

        if samples.is_empty() {
            return None;
        }

        let n = samples.len() as f32;
        let duration_ms = ((n / (sample_rate as f32)) * 1000.0).round() as u32;

        let mut sq_sum = 0.0f32;
        let mut zcr_count = 0usize;
        let mut diff1_sum = 0.0f32;
        let mut diff2_sum = 0.0f32;

        for i in 0..samples.len() {
            let s = samples[i];
            sq_sum += s * s;
            if i > 0 {
                if (samples[i - 1] >= 0.0 && s < 0.0) || (samples[i - 1] < 0.0 && s >= 0.0) {
                    zcr_count += 1;
                }
                let d1 = (s - samples[i - 1]).abs();
                diff1_sum += d1;
                if i > 1 {
                    let d2 = (s - 2.0 * samples[i - 1] + samples[i - 2]).abs();
                    diff2_sum += d2;
                }
            }
        }

        let rms_energy = (sq_sum / n).sqrt();
        let zero_crossing_rate = (zcr_count as f32) / n;
        let high_band = (diff2_sum / n).clamp(0.0, 1.0);
        let mid_band = (diff1_sum / n).clamp(0.0, 1.0);
        let low_band = (rms_energy * (1.0 - zero_crossing_rate)).clamp(0.0, 1.0);

        let mut waveform_envelope_32 = Vec::with_capacity(32);
        let chunk_sz = (samples.len() / 32).max(1);
        for b_idx in 0..32 {
            let start = (b_idx * chunk_sz).min(samples.len());
            let end = ((b_idx + 1) * chunk_sz).min(samples.len());
            if start >= end {
                waveform_envelope_32.push(0);
            } else {
                let peak = samples[start..end]
                    .iter()
                    .fold(0.0f32, |m, &v| m.max(v.abs()));
                waveform_envelope_32.push((peak * 255.0).round().clamp(0.0, 255.0) as u8);
            }
        }

        let mut extracted_traits = vec!["ears:cochlea_waveform_active".to_string()];
        if zero_crossing_rate < 0.12 {
            extracted_traits.push("ears:cochlea_voiced_harmonic".to_string());
        } else {
            extracted_traits.push("ears:cochlea_high_zcr_sibilant".to_string());
        }
        if rms_energy >= 0.10 {
            extracted_traits.push("ears:cochlea_strong_amplitude".to_string());
        } else {
            extracted_traits.push("ears:cochlea_soft_amplitude".to_string());
        }

        let analysis = CochlearAnalysis {
            source_path: path.to_string(),
            sample_rate,
            duration_ms,
            rms_energy,
            zero_crossing_rate,
            low_band_energy: low_band,
            mid_band_energy: mid_band,
            high_band_energy: high_band,
            waveform_envelope_32,
            extracted_traits,
        };
        self.last_cochlear_analysis = Some(analysis.clone());
        Some(analysis)
    }
}

/// Tactile & motor organ: touches objects, manipulates the 2D world, and executes/synthesizes small code.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct HandsEffector {
    pub hand_x: i32,
    pub hand_y: i32,
}

impl HandsEffector {
    pub fn touch(&self, tactile: &[&str]) -> Vec<String> {
        tactile
            .iter()
            .map(|t| {
                if t.starts_with("hands:") {
                    (*t).to_string()
                } else {
                    format!("hands:{}", t)
                }
            })
            .collect()
    }

    /// Native Rust evaluator for small code snippets practiced or synthesized by Alpha 7's hands.
    /// Supports multi-statement assignments (`x = 6`, `y = 7`, `result = x * y`), bounded loops
    /// (`for i in 1..=5: result = result + i`), and arithmetic (`+`, `-`, `*`, `/`) with safe
    /// syntax and zero-division guards.
    pub fn execute_small_code(&self, code_str: &str) -> Vec<String> {
        let visual = EyesSensor::default().inspect_code(code_str);
        if visual.iter().any(|t| t == "eyes:syntax_typo") {
            return vec![
                "eyes:syntax_error".to_string(),
                "hands:execution_halted".to_string(),
            ];
        }

        let mut env_vars: FxHashMap<String, i64> = FxHashMap::default();
        let mut div_by_zero = false;

        let eval_atom = |tok: &str, vars: &FxHashMap<String, i64>| -> Option<i64> {
            let clean = tok.trim();
            if let Ok(v) = clean.parse::<i64>() {
                Some(v)
            } else {
                vars.get(clean).copied()
            }
        };

        let eval_expr =
            |expr: &str, vars: &FxHashMap<String, i64>, div_zero: &mut bool| -> Option<i64> {
                let e = expr.trim().trim_end_matches(';').trim();
                if let Some((a, b)) = e.split_once('+') {
                    Some(eval_atom(a, vars)?.saturating_add(eval_atom(b, vars)?))
                } else if let Some((a, b)) = e.split_once('*') {
                    Some(eval_atom(a, vars)?.saturating_mul(eval_atom(b, vars)?))
                } else if let Some((a, b)) = e.split_once('-') {
                    if a.trim().is_empty() {
                        Some(-eval_atom(b, vars)?)
                    } else {
                        Some(eval_atom(a, vars)?.saturating_sub(eval_atom(b, vars)?))
                    }
                } else if let Some((a, b)) = e.split_once('/') {
                    let num = eval_atom(a, vars)?;
                    let den = eval_atom(b, vars)?;
                    if den == 0 {
                        *div_zero = true;
                        None
                    } else {
                        Some(num / den)
                    }
                } else {
                    eval_atom(e, vars)
                }
            };

        for raw_statement in code_str.split(|c| c == '\n' || c == ';') {
            let l = raw_statement.trim();
            if l.is_empty() || l.starts_with('#') || l.starts_with("//") {
                continue;
            }

            // Support bounded loop: `for i in A..=B { result = result + i }` or `for i in A..B: result = result + i`
            if let Some(rest) = l.strip_prefix("for ") {
                if let Some((header, body_stmt)) = rest.split_once(':').or_else(|| rest.split_once('{')) {
                    let body_clean = body_stmt.trim().trim_end_matches('}').trim();
                    let parts: Vec<&str> = header.split_whitespace().collect();
                    if parts.len() == 3 && parts[1] == "in" {
                        let loop_var = parts[0].trim();
                        let range_str = parts[2].trim();
                        let (start_opt, end_opt, inclusive) =
                            if let Some((s, e)) = range_str.split_once("..=") {
                                (s.parse::<i64>().ok(), e.parse::<i64>().ok(), true)
                            } else if let Some((s, e)) = range_str.split_once("..") {
                                (s.parse::<i64>().ok(), e.parse::<i64>().ok(), false)
                            } else {
                                (None, None, false)
                            };
                        if let (Some(s_val), Some(e_val)) = (start_opt, end_opt) {
                            let max_end = if inclusive { e_val } else { e_val - 1 };
                            let clamped_end = max_end.min(s_val + 256);
                            for idx_val in s_val..=clamped_end {
                                env_vars.insert(loop_var.to_string(), idx_val);
                                if let Some((lhs, rhs)) = body_clean.split_once('=') {
                                    let var_name =
                                        lhs.trim().strip_prefix("let ").unwrap_or(lhs.trim()).trim();
                                    if let Some(val) = eval_expr(rhs, &env_vars, &mut div_by_zero) {
                                        env_vars.insert(var_name.to_string(), val);
                                    }
                                }
                            }
                        }
                    }
                }
                continue;
            }

            if let Some((lhs, rhs)) = l.split_once('=') {
                if !lhs.ends_with('=') && !rhs.starts_with('=') {
                    let var_name = lhs.trim().strip_prefix("let ").unwrap_or(lhs.trim()).trim();
                    if let Some(val) = eval_expr(rhs, &env_vars, &mut div_by_zero) {
                        env_vars.insert(var_name.to_string(), val);
                    }
                }
            }
        }

        if div_by_zero {
            return vec![
                "eyes:zero_division_error".to_string(),
                "hands:execution_halted".to_string(),
            ];
        }

        let mut outcomes = vec!["eyes:code_ran_cleanly".to_string()];
        if let Some(&v) = env_vars.get("result") {
            if code_str.contains("print") {
                outcomes.push(format!("eyes:printed_{}", v));
            }
            outcomes.push(format!("eyes:result_{}", v));
        }
        outcomes
    }
}

/// Olfactory & chemical/context marker sensor.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SmellSensor;

impl SmellSensor {
    pub fn sniff(&self, scents: &[&str]) -> Vec<String> {
        scents
            .iter()
            .map(|s| {
                if s.starts_with("smell:") {
                    (*s).to_string()
                } else {
                    format!("smell:{}", s)
                }
            })
            .collect()
    }
}

/// Proprioception, surprise arousal, energy, and user bond sensor.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternalSenses {
    pub user_interactions: u32,
    pub last_surprise: f32,
}

impl Default for InternalSenses {
    fn default() -> Self {
        Self {
            user_interactions: 0,
            last_surprise: 0.0,
        }
    }
}

impl InternalSenses {
    pub fn read_state(&mut self, surprise: f32) -> Vec<String> {
        self.last_surprise = surprise;
        let mut traits = vec!["senses:awake".to_string()];
        if surprise >= 0.5 {
            traits.push("senses:high_surprise_alert".to_string());
        } else {
            traits.push("senses:calm_predictive_flow".to_string());
        }
        if self.user_interactions > 0 {
            traits.push("senses:user_bond_active".to_string());
        }
        traits
    }
}

/// Complete Pure-Rust 5-Sense Body for Alpha 7.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Alpha7Body {
    pub eyes: EyesSensor,
    pub ears: EarsSensor,
    pub hands: HandsEffector,
    pub smell: SmellSensor,
    pub internal: InternalSenses,
}

impl Alpha7Body {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn build_frame(
        &mut self,
        eyes: &[&str],
        ears: &[&str],
        hands: &[&str],
        smell: &[&str],
        utterance: Option<&str>,
    ) -> SensoryFrame {
        let (ear_traits, words) = self.ears.listen(ears, utterance);
        if utterance.is_some() {
            self.internal.user_interactions += 1;
        }
        let senses = self.internal.read_state(self.internal.last_surprise);
        SensoryFrame {
            eyes: self.eyes.observe_entity(eyes),
            ears: ear_traits,
            hands: self.hands.touch(hands),
            smell: self.smell.sniff(smell),
            senses,
            spoken_words: words,
        }
    }
}
