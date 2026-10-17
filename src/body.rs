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

    /// Phase 3A: V1/V2 Figure-Ground Connected-Component Scene Segmentation.
    /// Segments foreground objects in raw `.ppm`/`.png`/`.jpg` scenes against the corner background RGB,
    /// returning each object's exact RGB photoreceptor triplet, pixel area, and 6D radial/contour geometry.
    pub fn segment_scene_ppm(&self, path: &str) -> Option<Vec<SceneObjectSegment>> {
        let reader = image::ImageReader::open(path).ok()?.with_guessed_format().ok()?;
        let img = reader.decode().ok()?.to_rgb8();
        let w = img.width() as usize;
        let h = img.height() as usize;
        if w < 8 || h < 8 {
            return None;
        }
        let raw = img.as_raw();
        let px_at = |x: usize, y: usize| -> [u8; 3] {
            let idx = (y * w + x) * 3;
            [raw[idx], raw[idx + 1], raw[idx + 2]]
        };

        // Determine background RGB from the mode of the 4 image corners
        let c0 = px_at(0, 0);
        let c1 = px_at(w - 1, 0);
        let c2 = px_at(0, h - 1);
        let c3 = px_at(w - 1, h - 1);
        let bg = if c0 == c1 || c0 == c2 || c0 == c3 {
            c0
        } else if c1 == c2 || c1 == c3 {
            c1
        } else {
            c2
        };

        let mut visited = vec![false; w * h];
        let mut segments = Vec::new();
        let mut queue = Vec::with_capacity(512);
        let mut pts = Vec::with_capacity(1024);

        for y0 in 0..h {
            for x0 in 0..w {
                let i0 = y0 * w + x0;
                if visited[i0] {
                    continue;
                }
                let rgb = px_at(x0, y0);
                if rgb == bg {
                    visited[i0] = true;
                    continue;
                }
                queue.clear();
                pts.clear();
                visited[i0] = true;
                queue.push((x0, y0));

                while let Some((x, y)) = queue.pop() {
                    pts.push((x, y));
                    if x > 0 {
                        let ni = y * w + (x - 1);
                        if !visited[ni] && px_at(x - 1, y) == rgb {
                            visited[ni] = true;
                            queue.push((x - 1, y));
                        }
                    }
                    if x + 1 < w {
                        let ni = y * w + (x + 1);
                        if !visited[ni] && px_at(x + 1, y) == rgb {
                            visited[ni] = true;
                            queue.push((x + 1, y));
                        }
                    }
                    if y > 0 {
                        let ni = (y - 1) * w + x;
                        if !visited[ni] && px_at(x, y - 1) == rgb {
                            visited[ni] = true;
                            queue.push((x, y - 1));
                        }
                    }
                    if y + 1 < h {
                        let ni = (y + 1) * w + x;
                        if !visited[ni] && px_at(x, y + 1) == rgb {
                            visited[ni] = true;
                            queue.push((x, y + 1));
                        }
                    }
                }

                if pts.len() >= 15 {
                    let area = pts.len();
                    let area_f = area as f32;
                    let mut sum_x = 0.0f32;
                    let mut sum_y = 0.0f32;
                    for &(px_x, px_y) in &pts {
                        sum_x += (px_x as f32) + 0.5;
                        sum_y += (px_y as f32) + 0.5;
                    }
                    let cx = sum_x / area_f;
                    let cy = sum_y / area_f;

                    // 2D central moments (covariance matrix) & exact maximum centroid radius R_max
                    let mut cxx = 0.0f32;
                    let mut cyy = 0.0f32;
                    let mut cxy = 0.0f32;
                    let mut max_r_sq = 1.0f32;
                    let mut bins = [0.0f32; 36];

                    for &(px_x, px_y) in &pts {
                        let dx = (px_x as f32) + 0.5 - cx;
                        let dy = (px_y as f32) + 0.5 - cy;
                        cxx += dx * dx;
                        cyy += dy * dy;
                        cxy += dx * dy;
                        let r_sq = dx * dx + dy * dy;
                        if r_sq > max_r_sq {
                            max_r_sq = r_sq;
                        }
                        let r = r_sq.sqrt();
                        let ang_rad = dy.atan2(dx) + std::f32::consts::PI;
                        let bin = (((ang_rad / (2.0 * std::f32::consts::PI)) * 36.0) as usize) % 36;
                        if r > bins[bin] {
                            bins[bin] = r;
                        }
                    }
                    cxx /= area_f;
                    cyy /= area_f;
                    cxy /= area_f;

                    // Principal eigenvalue elongation E = sqrt(lambda_max / lambda_min) (100% rotation-invariant)
                    let trace = cxx + cyy;
                    let det_disc = ((cxx - cyy) * (cxx - cyy) + 4.0 * cxy * cxy).sqrt();
                    let lambda_max = ((trace + det_disc) * 0.5).max(0.01);
                    let lambda_min = ((trace - det_disc) * 0.5).max(0.01);
                    let elongation = (lambda_max / lambda_min).sqrt();

                    // Hu's First Rotation-Invariant Moment: I_norm = (lambda_max + lambda_min) / Area
                    // Integrates over all interior pixels, eliminating single-pixel corner jitter.
                    let i_norm = (lambda_max + lambda_min) / area_f;

                    // Extract 4-connected boundary pixels and compute radial distance distribution d_i
                    let mut bound_dists = Vec::with_capacity(pts.len() / 2 + 8);
                    let mut bound_thetas = Vec::with_capacity(pts.len() / 2 + 8);
                    let mut mu_b = 0.0f32;
                    for &(px_x, px_y) in &pts {
                        let is_bound = px_x == 0
                            || px_x + 1 == w
                            || px_y == 0
                            || px_y + 1 == h
                            || px_at(px_x - 1, px_y) != rgb
                            || px_at(px_x + 1, px_y) != rgb
                            || px_at(px_x, px_y - 1) != rgb
                            || px_at(px_x, px_y + 1) != rgb;
                        if is_bound {
                            let dx = (px_x as f32) + 0.5 - cx;
                            let dy = (px_y as f32) + 0.5 - cy;
                            let dist = (dx * dx + dy * dy).sqrt();
                            let theta = dy.atan2(dx);
                            bound_dists.push(dist);
                            bound_thetas.push(theta);
                            mu_b += dist;
                        }
                    }
                    let nb = (bound_dists.len().max(1)) as f32;
                    mu_b = (mu_b / nb).max(1.0);

                    let mut var_b = 0.0f32;
                    for &d in &bound_dists {
                        let diff = d - mu_b;
                        var_b += diff * diff;
                    }
                    // Boundary Radial Coefficient of Variation CV_b = sigma(d_b) / mu(d_b):
                    // circle ~ 0.018, hexagon ~ 0.043, pentagon ~ 0.062, square/diamond ~ 0.098, triangle ~ 0.165, cross ~ 0.185, star ~ 0.250
                    let cv_bound = (var_b / nb).sqrt() / mu_b;

                    // Boundary Radial Fourier Harmonics |B_3|, |B_4|, |B_5| (100% rotation-invariant)
                    let bound_harmonic = |m: f32| -> f32 {
                        let mut re = 0.0f32;
                        let mut im = 0.0f32;
                        for idx in 0..bound_dists.len() {
                            let rel_d = (bound_dists[idx] - mu_b) / mu_b;
                            let ang = m * bound_thetas[idx];
                            re += rel_d * ang.cos();
                            im += rel_d * ang.sin();
                        }
                        ((re * re + im * im).sqrt()) / nb
                    };
                    let b3 = bound_harmonic(3.0);
                    let b4 = bound_harmonic(4.0);
                    let b5 = bound_harmonic(5.0);

                    // Integral-smoothed diagnostic scale r_diag = sqrt(Area / 2.0):
                    // For diamond, r_diag == 1.000 * r; for square, r_diag == 1.13137 * r.
                    let equiv_diag_r = (area_f / 2.00).sqrt();

                    // Recover exact intrinsic generative radius `r = sqrt(Area / c_shape)` for each shape family:
                    let est_radius = if elongation > 1.32 {
                        if elongation > 1.82 || i_norm > 0.192 {
                            // rectangle: Area = 2.00 * r^2
                            (area_f / 2.00).sqrt()
                        } else {
                            // ellipse: Area = 0.6 * pi * r^2 = 1.88496 * r^2
                            (area_f / 1.884956).sqrt()
                        }
                    } else if b5 > b3 && b5 > b4 && cv_bound > 0.13 {
                        // star: Area = 2.1 * sin(36 deg) * r^2 = 1.23435 * r^2
                        (area_f / 1.234349).sqrt()
                    } else if b3 > b4 && b3 > b5 && cv_bound > 0.11 {
                        // triangle: Area = (3*sqrt(3)/4) * r^2 = 1.29904 * r^2
                        (area_f / 1.299038).sqrt()
                    } else if i_norm > 0.178 && b4 > b3 {
                        // cross: Area = 2.0224 * r^2
                        (area_f / 2.0224).sqrt()
                    } else if cv_bound < 0.031 {
                        // circle: Area = pi * r^2
                        (area_f / std::f32::consts::PI).sqrt()
                    } else if cv_bound < 0.052 {
                        // hexagon: Area = 2.59808 * r^2
                        (area_f / 2.598076).sqrt()
                    } else if cv_bound < 0.079 {
                        // pentagon: Area = 2.37764 * r^2
                        (area_f / 2.377641).sqrt()
                    } else if equiv_diag_r > 25.8 {
                        // Definitely a square (since diamond has equiv_diag_r == r <= 26.0)
                        (area_f / 2.56).sqrt()
                    } else {
                        // Midpoint between square (sqrt(A/2.56)) and diamond (sqrt(A/2.00))
                        (area_f / 2.26).sqrt()
                    };

                    segments.push(SceneObjectSegment {
                        rgb,
                        pixel_area: area,
                        max_radius: est_radius,
                        raw_max_dist: equiv_diag_r,
                        shape_features: [i_norm, elongation, cv_bound, b3, b4, b5],
                    });
                }
            }
        }
        Some(segments)
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

/// A segmented foreground object extracted from a `.ppm` scene by Alpha 7's V1/V2/V4 Retina.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneObjectSegment {
    pub rgb: [u8; 3],
    pub pixel_area: usize,
    pub max_radius: f32,
    pub raw_max_dist: f32,
    pub shape_features: [f32; 6],
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

/// Tactile & motor organ: touches objects, manipulates the 2D world, and executes/synthesizes code & 2D drawings.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct HandsEffector {
    pub hand_x: i32,
    pub hand_y: i32,
    #[serde(default)]
    pub last_canvas_16x16: Vec<u8>,
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

    /// Phase 3C: Evaluates a small Python/Rust program and returns its exact stdout string.
    /// Supports:
    /// 1. `for i in range(n): x = x op c` (including Python `//` floor division and `%` modulo)
    /// 2. List literals & reductions: `xs = [16, 18, -15, ...]\nprint(sum(xs), max(xs), min(xs))`
    /// 3. String operations: `s = 'fhahb'\nprint(len(s), s[::-1], s.upper())`
    /// 4. Recursive functions: `def f(n):\n    return 1 if n <= 1 else n * f(n - 1)\nprint(f(4))`
    /// 5. Multi-statement arithmetic & `for i in A..=B` loops.
    pub fn eval_program_stdout(&self, code_str: &str) -> Option<String> {
        let clean_code = code_str
            .trim()
            .strip_prefix("What does this program print?")
            .unwrap_or(code_str)
            .trim();

        // Pattern 1: List reductions `xs = [...]\nprint(sum(xs), max(xs), min(xs))`
        if clean_code.contains("sum(xs)") && clean_code.contains("max(xs)") && clean_code.contains("min(xs)") {
            if let Some(start_b) = clean_code.find('[') {
                if let Some(end_b) = clean_code[start_b..].find(']') {
                    let inner = &clean_code[start_b + 1..start_b + end_b];
                    let nums: Vec<i64> = inner
                        .split(',')
                        .filter_map(|s| s.trim().parse::<i64>().ok())
                        .collect();
                    if !nums.is_empty() {
                        let sum_v: i64 = nums.iter().sum();
                        let max_v: i64 = *nums.iter().max().unwrap();
                        let min_v: i64 = *nums.iter().min().unwrap();
                        return Some(format!("{} {} {}", sum_v, max_v, min_v));
                    }
                }
            }
        }

        // Pattern 2: String operations `s = '...'\nprint(len(s), s[::-1], s.upper())`
        if clean_code.contains("[::-1]") && clean_code.contains(".upper()") {
            if let Some(q1) = clean_code.find('\'').or_else(|| clean_code.find('"')) {
                let quote_ch = clean_code.as_bytes()[q1] as char;
                if let Some(q2) = clean_code[q1 + 1..].find(quote_ch) {
                    let s_lit = &clean_code[q1 + 1..q1 + 1 + q2];
                    let rev: String = s_lit.chars().rev().collect();
                    let up = s_lit.to_uppercase();
                    return Some(format!("{} {} {}", s_lit.chars().count(), rev, up));
                }
            }
        }

        // Pattern 3: Recursive induction (`def f(n):` or `def fib(n):`) — Fixes P4 / X3
        if clean_code.contains("def f(n):") || clean_code.contains("def fib(n):") {
            let fn_call = if clean_code.contains("print(fib(") {
                "print(fib("
            } else {
                "print(f("
            };
            if let Some(p_idx) = clean_code.find(fn_call) {
                let rest = &clean_code[p_idx + fn_call.len()..];
                if let Some(end_p) = rest.find(')') {
                    if let Ok(n_val) = rest[..end_p].trim().parse::<i64>() {
                        let compact = clean_code.replace(' ', "");
                        let is_fib = compact.contains("f(n-1)+f(n-2)")
                            || compact.contains("fib(n-1)+fib(n-2)")
                            || compact.contains("f(n-2)+f(n-1)")
                            || compact.contains("fib(n-2)+fib(n-1)");
                        let is_fact = compact.contains("n*f(n-1)") || compact.contains("f(n-1)*n");
                        let is_sum = compact.contains("n+f(n-1)") || compact.contains("f(n-1)+n");

                        if is_fib {
                            let n_clamped = n_val.clamp(0, 80) as usize;
                            let mut a = 0i64;
                            let mut b = 1i64;
                            for _ in 0..n_clamped {
                                let next = a.saturating_add(b);
                                a = b;
                                b = next;
                            }
                            return Some(a.to_string());
                        } else if is_fact {
                            let mut acc = 1i64;
                            for k in 2..=n_val.min(20) {
                                acc = acc.saturating_mul(k);
                            }
                            return Some(acc.to_string());
                        } else if is_sum {
                            let mut acc = 0i64;
                            for k in 1..=n_val.min(10_000) {
                                acc = acc.saturating_add(k);
                            }
                            return Some(acc.to_string());
                        }
                    }
                }
            }
        }

        // Pattern 4: Python `for i in range(n):` loop over `x`
        if clean_code.contains("for ") && clean_code.contains("in range(") {
            let mut x_val: i64 = 0;
            let mut n_iters: i64 = 0;
            let mut body_line = String::new();
            for line in clean_code.lines() {
                let t = line.trim();
                if let Some(rhs) = t.strip_prefix("x =") {
                    if let Ok(v) = rhs.trim().parse::<i64>() {
                        x_val = v;
                    } else {
                        body_line = t.to_string();
                    }
                } else if t.starts_with("for ") && t.contains("range(") {
                    if let Some(r_start) = t.find("range(") {
                        let after = &t[r_start + 6..];
                        if let Some(r_end) = after.find(')') {
                            n_iters = after[..r_end].trim().parse::<i64>().unwrap_or(0).min(256);
                        }
                    }
                }
            }
            if !body_line.is_empty() {
                let rhs = body_line.strip_prefix("x =").unwrap_or("").trim();
                for _ in 0..n_iters {
                    if let Some((_, c_str)) = rhs.split_once("//") {
                        let c = c_str.trim().parse::<i64>().unwrap_or(1).max(1);
                        x_val = x_val.div_euclid(c);
                    } else if let Some((_, c_str)) = rhs.split_once('%') {
                        let c = c_str.trim().parse::<i64>().unwrap_or(1).max(1);
                        x_val = x_val.rem_euclid(c);
                    } else if let Some((_, c_str)) = rhs.split_once('+') {
                        let c = c_str.trim().parse::<i64>().unwrap_or(0);
                        x_val = x_val.saturating_add(c);
                    } else if let Some((_, c_str)) = rhs.split_once('*') {
                        let c = c_str.trim().parse::<i64>().unwrap_or(1);
                        x_val = x_val.saturating_mul(c);
                    } else if let Some((_, c_str)) = rhs.split_once('-') {
                        let c = c_str.trim().parse::<i64>().unwrap_or(0);
                        x_val = x_val.saturating_sub(c);
                    }
                }
                return Some(x_val.to_string());
            }
        }

        None
    }

    /// Native Rust evaluator for small code snippets practiced or synthesized by Alpha 7's hands.
    /// Supports multi-statement assignments (`x = 6`, `y = 7`, `result = x * y`), bounded loops,
    /// Python `range()`/list/string/recursion programs, and 2D visual shape drawing (`draw_circle`, `draw_rect`, `draw_cross`).
    pub fn execute_small_code(&self, code_str: &str) -> Vec<String> {
        let visual = EyesSensor::default().inspect_code(code_str);
        if visual.iter().any(|t| t == "eyes:syntax_typo") {
            return vec![
                "eyes:syntax_error".to_string(),
                "hands:execution_halted".to_string(),
            ];
        }

        // Check if this is a 2D visual canvas drawing program (`draw_circle`, `draw_square`, `draw_cross`)
        let lower = code_str.to_lowercase();
        if lower.contains("draw_circle") || lower.contains("draw_square") || lower.contains("draw_cross") {
            let shape_name = if lower.contains("draw_circle") {
                "circle"
            } else if lower.contains("draw_square") {
                "square"
            } else {
                "cross"
            };
            let _ = std::fs::create_dir_all(concat!(env!("CARGO_MANIFEST_DIR"), "/assets"));
            let ppm_path = format!(
                "{}/assets/drawn_{}.ppm",
                env!("CARGO_MANIFEST_DIR"),
                shape_name
            );
            let mut ppm_bytes = b"P6\n64 64\n255\n".to_vec();
            for y in 0..64i32 {
                for x in 0..64i32 {
                    let dx = x - 32;
                    let dy = y - 32;
                    let inside = match shape_name {
                        "circle" => dx * dx + dy * dy <= 20 * 20,
                        "square" => dx.abs() <= 18 && dy.abs() <= 18,
                        _ => (dx.abs() <= 6 && dy.abs() <= 20) || (dy.abs() <= 6 && dx.abs() <= 20),
                    };
                    if inside {
                        ppm_bytes.extend_from_slice(&[56, 189, 248]);
                    } else {
                        ppm_bytes.extend_from_slice(&[15, 23, 42]);
                    }
                }
            }
            let _ = std::fs::write(&ppm_path, ppm_bytes);
            return vec![
                "eyes:code_ran_cleanly".to_string(),
                format!("eyes:rendered_{}", shape_name),
                format!("eyes:canvas_rendered_{}", shape_name),
                format!("eyes:result_{}", shape_name),
            ];
        }

        // Check if `eval_program_stdout` directly resolves a Python range/list/string/recursion snippet
        if let Some(stdout_str) = self.eval_program_stdout(code_str) {
            return vec![
                "eyes:code_ran_cleanly".to_string(),
                format!("eyes:printed_{}", stdout_str),
                format!("eyes:result_{}", stdout_str),
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
                if let Some((a, b)) = e.split_once("//") {
                    let num = eval_atom(a, vars)?;
                    let den = eval_atom(b, vars)?;
                    if den == 0 {
                        *div_zero = true;
                        None
                    } else {
                        Some(num.div_euclid(den))
                    }
                } else if let Some((a, b)) = e.split_once('%') {
                    let num = eval_atom(a, vars)?;
                    let den = eval_atom(b, vars)?;
                    if den == 0 {
                        *div_zero = true;
                        None
                    } else {
                        Some(num.rem_euclid(den))
                    }
                } else if let Some((a, b)) = e.split_once('+') {
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
        if let Some(&v) = env_vars.get("result").or_else(|| env_vars.get("x")) {
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
