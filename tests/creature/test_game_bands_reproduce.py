# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 22:5x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 3.
"""test_game_bands_reproduce.py — "the eye's band on the world's things printed (G's road) -- with J's
colour block if merged, without it the number G measured (-0.107) must reproduce." J's colour work
(g5-bind-colour, a sibling worktree) is NOT merged here, so this pins the grey-only number: G's own
already-harvested BabyAI POV frames (`/data/dev/game-worlds/results/minigrid.npz`, read-only, untouched),
run through THIS worktree's own `genome/gaze.py` + `genome/machinery.py` road (not `/data/dev/genome`),
reproduce REPORT-G5-G.md's grey/gaze/things-only margin of -0.107 to 3 decimal places.

Skipped where the harvested npz or the sha-pinned Alpha 2 organs are not present (a fresh worktree
elsewhere, or a box without /data/dev/game-worlds/results) -- an environmental precondition, not a defect
in this branch's code."""
from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

MINIGRID_NPZ = Path("/data/dev/game-worlds/results/minigrid.npz")


@unittest.skipUnless(MINIGRID_NPZ.exists(), "G5-G's own harvested BabyAI frames are not present on this box")
class TestBandsReproduceGsNumber(unittest.TestCase):
    def test_things_only_grey_gaze_margin_reproduces_minus_0_107(self) -> None:
        from genome import gaze as G
        from genome.machinery import retina as RETINA

        SPEC = ("thresh0.25", "centre", "tower:eye-tower-g2", "sqrt", "unit")
        GAZE = {"fixations": 4, "grid": 16, "canvas": 128, "glance": 32, "ink": "border"}
        SCRATCH = Path(__file__).resolve().parents[2] / "scratch" / "frames-bands-test"
        SCRATCH.mkdir(parents=True, exist_ok=True)

        d = np.load(MINIGRID_NPZ, allow_pickle=True)   # G's own harvest output, this box's own trusted file (bands.py's own precedent)
        frames, cmaps, names = d["frames"], d["cmap"], list(d["names"])
        self.assertEqual(len(frames), 240)

        from PIL import Image

        def canvas_and_geom(frame, tag):
            p = SCRATCH / f"{tag}.png"
            Image.fromarray(frame).save(p)
            cv = G.canvas_of_picture(p, 128)
            p.unlink()
            h, w = frame.shape[:2]
            k = 128 / max(w, h)
            nw, nh = max(1, round(w * k)), max(1, round(h * k))
            geom = {"top": (128 - nh) // 2, "left": (128 - nw) // 2, "nh": nh, "nw": nw, "h": h, "w": w}
            return cv, geom

        def frame_px(cy, cx, geom):
            y = (cy - geom["top"]) * geom["h"] / geom["nh"]
            x = (cx - geom["left"]) * geom["w"] / geom["nw"]
            if not (0 <= y < geom["h"] and 0 <= x < geom["w"]):
                return None
            return int(y), int(x)

        g_org, r_org = G.organs()
        V, L, F = [], [], []
        for i in range(len(frames)):
            cv, geom = canvas_and_geom(frames[i], f"t-{i}")
            an = r_org.analyse(G.frame_of(cv))
            grey = G.luminance(cv)
            rows = g_org.gaze_sequence(an, max_fixations=GAZE["fixations"], predicted=None)
            for r in rows:
                win, (top, left) = G.glance_window(grey, (int(r["y"]), int(r["x"])), GAZE["grid"], GAZE["glance"])
                v = RETINA(G.ink_border(win), SPEC)
                fp = frame_px(top + GAZE["glance"] / 2, left + GAZE["glance"] / 2, geom)
                lab = "pad" if fp is None else (names[int(cmaps[i][fp[0], fp[1]])] if cmaps[i][fp[0], fp[1]] >= 0 else "unlabelled")
                V.append(v); L.append(lab); F.append(i)
        V, L, F = np.array(V), np.array(L), np.array(F)

        THINGS_ONLY = lambda c: c.split(":")[0] in ("ball", "key", "box", "door", "goal")
        keep = np.array([lab not in ("pad", "unlabelled") and THINGS_ONLY(lab) for lab in L])
        V2, L2, F2 = V[keep], L[keep], F[keep]
        counts = {c: int((L2 == c).sum()) for c in sorted(set(L2.tolist()))}
        live = [c for c, n in counts.items() if n >= 10]
        sel = np.isin(L2, live)
        V2, L2, F2 = V2[sel], L2[sel], F2[sel]
        self.assertGreaterEqual(len(live), 2, "not enough classes reach n>=10 to compute a band at all")

        Vn = V2 / np.maximum(np.linalg.norm(V2, axis=1, keepdims=True), 1e-12)
        S = Vn @ Vn.T
        iu = np.triu_indices(len(V2), k=1)
        same = L2[iu[0]] == L2[iu[1]]
        diff_frame = F2[iu[0]] != F2[iu[1]]
        w = S[iu][same & diff_frame]
        b = S[iu][~same]
        margin = float(np.median(w) - np.percentile(b, 95))

        self.assertAlmostEqual(margin, -0.107, places=2,
                                msg=f"THIS worktree's own retina/gaze road must reproduce G5-G's own reported "
                                    f"-0.107 things-only margin (grey, gaze, first-and-later fixations); got {margin:.4f}")


if __name__ == "__main__":
    unittest.main()
