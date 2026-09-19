"""train_eye.py — G2: the eye for photographs, GROWN by the estate's trainer road (docs/G2-EYE-PREREG.md §1–§3).

  python3 -m genome.train_eye gradcheck   float64 finite differences vs the backward (20 weights, rel. err < 1e-4)
  python3 -m genome.train_eye toy         G-1: circle vs bar canvases through the same road → head 100 % within 5 epochs
  python3 -m genome.train_eye views       cut the training views once (92 held-in folders; the 4 gaze windows + mirrors), cached u8
  python3 -m genome.train_eye probe       G-2: 20 timed steps → epochs by the declared rule
  python3 -m genome.train_eye train       train by the journal, seal judge/eye-photo-g1 (+ the untrained twin), G-3
  python3 -m genome.train_eye gate        G-4: gate G-a on the eleven UNSEEN words through the new eye, the glyph eye, the untrained twin
  python3 -m genome.train_eye replay      G-5: a second run from the same seed → journal + bytes compared

edit: Claude (Fable 5.1), 2026-09-19 18:10 +0400. Mirrors experiments/E09c-grounding-tower/code/conv.py layer for layer (im2col by a flat
index + a sparse scatter for col2im, float32, momentum 0.9, the ×0.5 schedule at 60 % and 85 %); three conv layers, 64-px input,
the layer list written into the seal. Nothing here touches the organism.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs" / "eye-photo-g1"; OUT.mkdir(parents=True, exist_ok=True)
SEAL_DIR = ROOT / "judge" / "eye-photo-g1"
TWIN_DIR = ROOT / "judge" / "eye-photo-g1-untrained"
SRC = Path("/data/datasets/caltech-101/caltech-101/101_ObjectCategories")
RUNG1_WORDS = ["anchor", "ant", "barrel", "bass", "beaver", "bonsai", "brain", "buddha", "camera", "cannon"]   # + ahmad: never trained on
SEED = 20260919
SIDE, CANVAS, GRID, GLANCE, FIX = 64, 128, 16, 64, 4
ARCH = [{"type": "conv", "f": 16, "k": 5}, {"type": "max", "p": 2}, {"type": "conv", "f": 32, "k": 3}, {"type": "max", "p": 2}, {"type": "conv", "f": 48, "k": 3}, {"type": "mean", "p": 4}]
BATCH, LR0, MOM = 64, 0.02, 0.9
EPOCH_CHOICES, COST_BAR_S = (8, 12, 16, 20), 45 * 60
GAZE = {"fixations": FIX, "grid": GRID, "canvas": CANVAS, "glance": GLANCE, "ink": "border"}
DT = np.float32


def _idx(C: int, H: int, W: int, k: int, pad: int):
    """E09c's index road: (H*W, C*k*k) into the flat padded (C, H+2p, W+2p) tensor + the sparse scatter for col2im."""
    Hp, Wp = H + 2 * pad, W + 2 * pad
    r = np.arange(H)[:, None] + np.arange(k)[None, :]
    c = np.arange(W)[:, None] + np.arange(k)[None, :]
    base = (r[:, None, :, None] * Wp + c[None, :, None, :]).reshape(H * W, k * k)
    idx = ((np.arange(C)[:, None] * Hp * Wp)[None, :, :] + base[:, None, :]).reshape(H * W, C * k * k)
    n = idx.size
    S = scipy.sparse.csr_matrix((np.ones(n, dtype=np.float32), (idx.ravel(), np.arange(n))), shape=(C * Hp * Wp, n))
    return idx, S, Hp, Wp


class Net:
    """A tower of ARCH's layers + a softmax head; float32 (DT) — float64 for the gradient check."""

    def __init__(self, arch: List[Dict[str, object]], side: int, n_classes: int, seed: int, dt=DT):
        self.arch, self.side, self.dt = arch, side, dt
        rng = np.random.default_rng(seed)
        self.params: Dict[str, np.ndarray] = {}; self.geom = []; C = 1; H = side; i = 0
        for layer in arch:
            if layer["type"] == "conv":
                i += 1; f, k = int(layer["f"]), int(layer["k"])
                self.params[f"W{i}"] = (rng.standard_normal((f, C * k * k)) * np.sqrt(2.0 / (C * k * k))).astype(dt)
                self.params[f"b{i}"] = np.zeros(f, dt)
                self.geom.append(("conv", i, C, H, k, k // 2) + _idx(C, H, H, k, k // 2)); C = f
            elif layer["type"] == "max":
                p = int(layer["p"]); self.geom.append(("max", p, C, H)); H //= p
            elif layer["type"] == "mean":
                p = int(layer["p"]); self.geom.append(("mean", p, C, H)); H //= p
        self.n_feat = C * H * H; self.H_out = H; self.C_out = C
        self.params["Wh"] = (rng.standard_normal((self.n_feat, n_classes)) * np.sqrt(2.0 / self.n_feat)).astype(dt)
        self.params["bh"] = np.zeros(n_classes, dt)
        self.mom = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.n_conv = i

    def features(self, X: np.ndarray, cache: Optional[list] = None) -> np.ndarray:
        n = len(X); x = X.astype(self.dt).reshape(n, self.side, self.side, 1)     # (n, H, W, C)
        for g in self.geom:
            if g[0] == "conv":
                _t, i, C, H, k, pad, idx, S, Hp, Wp = g
                xp = np.zeros((n, C, Hp, Wp), self.dt); xp[:, :, pad:pad + H, pad:pad + H] = x.transpose(0, 3, 1, 2)
                cols = xp.reshape(n, -1)[:, idx]                                     # (n, HW, Ckk)
                z = cols @ self.params[f"W{i}"].T + self.params[f"b{i}"]           # (n, HW, F)
                a = np.maximum(z, 0)
                if cache is not None: cache.append(("conv", cols, z))
                x = a.reshape(n, H, H, -1)
            elif g[0] == "max":
                _t, p, C, H = g
                r = x.reshape(n, H // p, p, H // p, p, C).transpose(0, 1, 3, 5, 2, 4).reshape(n, H // p, H // p, C, p * p)
                am = r.argmax(-1); x = np.take_along_axis(r, am[..., None], -1)[..., 0]
                if cache is not None: cache.append(("max", am))
            elif g[0] == "mean":
                _t, p, C, H = g
                x = x.reshape(n, H // p, p, H // p, p, C).mean(axis=(2, 4))
                if cache is not None: cache.append(("mean", None))
        return x.reshape(n, self.n_feat)

    def logits(self, f: np.ndarray) -> np.ndarray:
        return f @ self.params["Wh"] + self.params["bh"]

    def loss_and_grads(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, Dict[str, np.ndarray]]:
        cache: list = []; f = self.features(X, cache); n = len(X)
        L = self.logits(f).astype(np.float64); L -= L.max(1, keepdims=True); P = np.exp(L); P /= P.sum(1, keepdims=True)
        loss = float(-np.log(np.maximum(P[np.arange(n), y], 1e-12)).mean())
        dL = P; dL[np.arange(n), y] -= 1.0; dL = (dL / n).astype(self.dt)
        G = {"Wh": f.T @ dL, "bh": dL.sum(0)}
        dx = (dL @ self.params["Wh"].T).reshape(n, self.H_out, self.H_out, self.C_out)
        for g, c in zip(reversed(self.geom), reversed(cache)):
            if g[0] == "mean":
                _t, p, C, H = g
                dx = np.repeat(np.repeat(dx, p, axis=1), p, axis=2) / self.dt(p * p)
            elif g[0] == "max":
                _t, p, C, H = g; am = c[1]
                dr = np.zeros((n, H // p, H // p, C, p * p), self.dt)
                np.put_along_axis(dr, am[..., None], dx[..., None], -1)
                dx = dr.reshape(n, H // p, H // p, C, p, p).transpose(0, 1, 4, 2, 5, 3).reshape(n, H, H, C)
            elif g[0] == "conv":
                _t, i, C, H, k, pad, idx, S, Hp, Wp = g; cols, z = c[1], c[2]; F = z.shape[-1]
                dz = np.ascontiguousarray((dx.reshape(n, H * H, F) * (z > 0)).astype(self.dt))
                G[f"W{i}"] = dz.reshape(-1, F).T @ cols.reshape(-1, C * k * k); G[f"b{i}"] = dz.sum((0, 1))
                dcols = dz @ self.params[f"W{i}"]                                    # (n, HW, Ckk)
                dxp = (S @ dcols.reshape(n, -1).T).T.reshape(n, C, Hp, Wp)
                dx = np.ascontiguousarray(dxp[:, :, pad:pad + H, pad:pad + H].transpose(0, 2, 3, 1))
        return loss, G

    def step(self, X: np.ndarray, y: np.ndarray, lr: float) -> float:
        loss, G = self.loss_and_grads(X, y)
        for k, g in G.items():
            self.mom[k] = self.dt(MOM) * self.mom[k] - self.dt(lr) * g
            self.params[k] = self.params[k] + self.mom[k]
        return loss

    def acc(self, X: np.ndarray, y: np.ndarray, chunk: int = 256) -> float:
        ok = 0
        for i in range(0, len(X), chunk):
            ok += int((np.argmax(self.logits(self.features(X[i:i + chunk])), 1) == y[i:i + chunk]).sum())
        return ok / len(X)


def lr_at(ep: int, e_max: int) -> float:
    return LR0 * (0.5 if ep > 0.6 * e_max else 1.0) * (0.5 if ep > 0.85 * e_max else 1.0)


# ----------------------------------------------------------------------------- the road: picture → the gaze's windows → INK border → u8
def views_of(rgb: np.ndarray, mirrors: bool = True) -> List[np.ndarray]:
    from . import gaze
    grey = gaze.luminance(rgb); out = []
    for cell in gaze.fixations(rgb, FIX, "surprise"):
        win, _tl = gaze.glance_window(grey, cell, GRID, GLANCE)
        ink = gaze.ink_border(win); u8 = np.clip(np.rint(ink * 255.0), 0, 255).astype(np.uint8)
        out.append(u8)
        if mirrors: out.append(u8[:, ::-1].copy())
    return out


def first_view_u8(rgb: np.ndarray) -> np.ndarray:
    return views_of(rgb, mirrors=False)[0]


# ----------------------------------------------------------------------------- seal
ORDER_BASE = ["W1", "b1", "W2", "b2", "W3", "b3", "Wh", "bh"]


def write_seal(d: Path, net: Net, component: str, labels: List[str], extra: Dict[str, object]) -> str:
    d.mkdir(parents=True, exist_ok=True)
    names = [f"{p}{i}" for i in range(1, net.n_conv + 1) for p in ("W", "b")] + ["Wh", "bh"]
    with (d / "tower.bin").open("wb") as f:
        f.write(b"A3EYE1\0\0")
        for k in names:
            a = np.ascontiguousarray(net.params[k], dtype=np.float32)
            f.write(struct.pack("<i", a.ndim))
            for dd in a.shape: f.write(struct.pack("<i", int(dd)))
            f.write(a.tobytes(order="C"))
    sha = hashlib.sha256((d / "tower.bin").read_bytes()).hexdigest()
    seal = {"component": component, "seed": SEED, "source": "G2 (docs/G2-EYE-PREREG.md): E09c's trainer road mirrored in genome/train_eye.py", "arrays": names,
            "shapes": {k: list(net.params[k].shape) for k in names}, "n_params": int(sum(int(np.prod(net.params[k].shape)) for k in names)),
            "arch": ARCH, "input_side": SIDE, "input": f"{SIDE}x{SIDE} grey in [0,1]: the gaze's {GLANCE}-px window on a {CANVAS} canvas through INK border (G1 §6)",
            "labels": labels, "tower_bin_sha256": sha, "sealed_at": time.strftime("%Y-%m-%d %H:%M %z"), **extra}
    (d / "SEAL.json").write_text(json.dumps(seal, indent=1))
    return sha


# ----------------------------------------------------------------------------- stages
def stage_gradcheck() -> None:
    net = Net(ARCH, SIDE, 5, SEED, dt=np.float64)
    rng = np.random.default_rng(3); X = rng.random((4, SIDE, SIDE)); y = rng.integers(0, 5, size=4)
    loss, G = net.loss_and_grads(X, y); worst = 0.0; rows = []
    for k in ("W1", "b1", "W2", "b2", "W3", "b3", "Wh", "bh"):
        flat = net.params[k].reshape(-1)
        for _ in range(3 if k.startswith("W") else 2):
            j = int(rng.integers(0, flat.size)); old = flat[j]; h = 1e-5
            flat[j] = old + h; lp, _ = net.loss_and_grads(X, y); flat[j] = old - h; lm, _ = net.loss_and_grads(X, y); flat[j] = old
            num = (lp - lm) / (2 * h); ana = float(G[k].reshape(-1)[j]); rel = abs(num - ana) / max(1e-8, abs(num) + abs(ana))
            worst = max(worst, rel); rows.append((k, j, round(num, 8), round(ana, 8), rel))
    print(f"gradcheck: {len(rows)} weights, worst relative error {worst:.2e} (bar 1e-4): {'PASS' if worst < 1e-4 else 'FAIL'}")
    (OUT / "gradcheck.json").write_text(json.dumps({"worst_rel": worst, "pass": worst < 1e-4, "rows": rows}, default=str))
    if worst >= 1e-4: raise SystemExit("gradient check FAILED — the trainer is wrong")


def stage_toy() -> None:
    from . import world
    rng = np.random.default_rng(11); Xs, ys = [], []
    things = ["circle", "bar"]
    for t in things:
        for _ in range(60):
            rgb, _tr = world.render_canvas(t, rng)
            for v in views_of(rgb): Xs.append(v); ys.append(things.index(t))
    rng2 = np.random.default_rng(12); Xh, yh = [], []
    for t in things:
        for _ in range(20):
            rgb, _tr = world.render_canvas(t, rng2); Xh.append(first_view_u8(rgb)); yh.append(things.index(t))
    X = np.stack(Xs).astype(DT) / DT(255.0); y = np.array(ys); Xh = np.stack(Xh).astype(DT) / DT(255.0); yh = np.array(yh)
    net = Net(ARCH, SIDE, 2, SEED); r = np.random.default_rng(5); hist = []
    for ep in range(1, 6):
        order = r.permutation(len(X)); tot = 0.0
        for i in range(0, len(X), BATCH):
            b = order[i:i + BATCH]; tot += net.step(X[b], y[b], LR0) * len(b)
        a = net.acc(Xh, yh); hist.append({"epoch": ep, "loss": round(tot / len(X), 5), "held_acc": a}); print(f"toy ep {ep} loss {tot / len(X):.4f} held-out {a:.3f}")
        if a == 1.0: break
    ok = hist[-1]["held_acc"] == 1.0
    (OUT / "toy.json").write_text(json.dumps({"pass": ok, "history": hist}))
    print(f"G-1 toy: {'PASS' if ok else 'FAIL'} ({len(X)} views, 40 held-out canvases)")
    if not ok: raise SystemExit("G-1 FAILED")


def stage_views() -> None:
    from . import gaze
    folders = sorted(d.name for d in SRC.iterdir() if d.is_dir() and d.name not in RUNG1_WORDS)
    assert len(folders) == 92, len(folders)
    Xtr, ytr, Xva, yva = [], [], [], []; t0 = time.perf_counter(); unreadable = []
    for li, name in enumerate(folders):
        pics = sorted(p for p in (SRC / name).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
        for j, p in enumerate(pics):
            try:
                rgb = gaze.canvas_of_picture(p, CANVAS)
            except Exception as e:
                unreadable.append((str(p), str(e))); continue
            if j % 5 == 4:
                Xva.append(first_view_u8(rgb)); yva.append(li)
            else:
                for v in views_of(rgb): Xtr.append(v); ytr.append(li)
        if li % 10 == 0: print(f"  views: {li + 1}/92 folders, {len(Xtr)} train views, {len(Xva)} val, {time.perf_counter() - t0:.0f} s", flush=True)
    np.savez_compressed(OUT / "views.npz", Xtr=np.stack(Xtr), ytr=np.array(ytr, dtype=np.int32), Xva=np.stack(Xva), yva=np.array(yva, dtype=np.int32), labels=np.array(folders))
    (OUT / "views.json").write_text(json.dumps({"folders": folders, "n_train_views": len(Xtr), "n_val": len(Xva), "unreadable": unreadable, "seconds": round(time.perf_counter() - t0, 1)}))
    print(f"views: {len(Xtr)} training views (8 per picture), {len(Xva)} validation pictures, {len(folders)} classes, unreadable {len(unreadable)}, {time.perf_counter() - t0:.0f} s")


def _load_views():
    z = np.load(OUT / "views.npz"); return z["Xtr"], z["ytr"], z["Xva"], z["yva"], [str(x) for x in z["labels"]]


def stage_probe() -> None:
    Xtr, ytr, _Xva, _yva, labels = _load_views()
    net = Net(ARCH, SIDE, len(labels), SEED); rng = np.random.default_rng(1)
    for _ in range(3):
        b = rng.integers(0, len(Xtr), size=BATCH); net.step(Xtr[b].astype(DT) / DT(255.0), ytr[b], LR0)     # warm
    t0 = time.perf_counter()
    for _ in range(20):
        b = rng.integers(0, len(Xtr), size=BATCH); net.step(Xtr[b].astype(DT) / DT(255.0), ytr[b], LR0)
    s_step = (time.perf_counter() - t0) / 20; steps = int(np.ceil(len(Xtr) / BATCH)); epoch_s = s_step * steps
    fit = [e for e in EPOCH_CHOICES if e * epoch_s <= COST_BAR_S]; epochs = max(fit) if fit else None
    rep = {"s_per_step": s_step, "steps_per_epoch": steps, "s_per_epoch": epoch_s, "threads": os.environ.get("OPENBLAS_NUM_THREADS"), "epochs_by_rule": epochs, "choices": EPOCH_CHOICES, "cost_bar_s": COST_BAR_S}
    (OUT / "probe.json").write_text(json.dumps(rep))
    print(f"G-2 probe: {s_step:.3f} s a step × {steps} steps = {epoch_s / 60:.1f} min an epoch (threads {rep['threads']}) → epochs by the rule: {epochs} ({[e for e in EPOCH_CHOICES]} within {COST_BAR_S // 60} min: {fit})")
    if epochs is None: raise SystemExit("G-2: not even 8 epochs fit the cost bar — a finding, not a reason to widen it")


def stage_train(replay: bool = False) -> None:
    Xtr, ytr, Xva, yva, labels = _load_views()
    probe = json.loads((OUT / "probe.json").read_text()); e_max = int(probe["epochs_by_rule"])
    net = Net(ARCH, SIDE, len(labels), SEED); untrained = Net(ARCH, SIDE, len(labels), SEED)
    rng = np.random.default_rng(SEED + 1); n = len(Xtr); hist = []; t0 = time.perf_counter()
    Xva_f = Xva.astype(DT) / DT(255.0)
    for ep in range(1, e_max + 1):
        lr = lr_at(ep, e_max); order = rng.permutation(n); tot = 0.0
        for i in range(0, n, BATCH):
            b = order[i:i + BATCH]; tot += net.step(Xtr[b].astype(DT) / DT(255.0), ytr[b], lr) * len(b)
        a = net.acc(Xva_f, yva); hist.append({"epoch": ep, "loss": round(tot / n, 5), "val_top1": round(a, 4), "lr": lr, "seconds": round(time.perf_counter() - t0, 1)})
        print(f"  ep {ep:2d}/{e_max} loss {tot / n:.4f} val top-1 {a:.4f} lr {lr} ({time.perf_counter() - t0:.0f} s)", flush=True)
    journal = {"epochs": e_max, "batch": BATCH, "lr0": LR0, "momentum": MOM, "seed": SEED, "history": hist, "seconds": round(time.perf_counter() - t0, 1), "threads": os.environ.get("OPENBLAS_NUM_THREADS")}
    if replay:
        (OUT / "journal-replay.json").write_text(json.dumps(journal)); np.savez(OUT / "params-replay.npz", **net.params); return
    (OUT / "journal.json").write_text(json.dumps(journal)); np.savez(OUT / "params.npz", **net.params)
    top1 = hist[-1]["val_top1"]; g3 = top1 >= 0.20
    sha = write_seal(SEAL_DIR, net, "G2 eye-photo-g1: a 3-layer tower GROWN on Caltech-101's 92 held-in folders through the genome's own gaze road; the eleven rung-1 words never seen", labels, {"journal": journal, "G3_val_top1": top1, "G3_pass": g3})
    sha_t = write_seal(TWIN_DIR, untrained, "G2 twin: the SAME shape and seed, UNTRAINED (random weights) — is the separation from the training or from the shape?", labels, {"untrained": True})
    print(f"G-3 sanity floor: val top-1 {top1:.4f} (bar ≥ 0.20, chance {1 / len(labels):.3f}): {'PASS' if g3 else 'FAIL'} · sealed {SEAL_DIR.name} sha {sha[:16]} · twin sha {sha_t[:16]} · {journal['seconds']} s")
    if not g3: raise SystemExit("G-3 FAILED — the eye learned nothing worth sealing")


def stage_gate() -> None:
    from . import gate_ga, gaze
    from .machinery import parse_genome
    from .run_g1 import load_his
    his_genome = (ROOT / "genome" / "G1-his.genome").read_text()
    g2 = his_genome.replace("SENSE  eye    32x32 grey", "SENSE  eye    64x64 grey").replace("RETINA thresh0.25 centre tower:eye-tower-g2 sqrt unit", "RETINA tower:eye-photo-g1 sqrt unit").replace("glance 32 ink border", "glance 64 ink border")
    g2 = g2.replace("# G1-his.genome — G1.genome with the thetas re-written by gate G-a on HIS pictures' glances (G1 §5 step 7)", "# G2-his.genome — G1-his.genome with the EYE FOR PHOTOGRAPHS (judge/eye-photo-g1, docs/G2-EYE-PREREG.md): SENSE eye 64x64, RETINA tower:eye-photo-g1 sqrt unit, GAZE glance 64")
    import re
    g2 = re.sub(r"cos<[0-9.]+", "cos<THETA_N", g2); g2 = re.sub(r"cos>[0-9.]+ same-answer", "cos>THETA_M same-answer", g2); g2 = re.sub(r"\n# gate G-a wrote.*", "", g2)
    assert "tower:eye-photo-g1" in g2 and "64x64" in g2 and "glance 64" in g2
    (ROOT / "genome" / "G2-his.genome").write_text(g2)
    twin_text = g2.replace("tower:eye-photo-g1", "tower:eye-photo-g1-untrained")
    ph = lambda t: parse_genome(t.replace("cos<THETA_N", "cos<0.5").replace("cos>THETA_M", "cos>0.99"))
    gens = {"eye-photo-g1 (trained)": ph(g2), "untrained twin": ph(twin_text), "glyph eye (G1-his)": parse_genome(his_genome)}
    H = load_his(gens["eye-photo-g1 (trained)"]); words = H["things"] + [H["withheld"]]
    rows = {w: [rgb for ww, rgb, _t in H["dev"] if ww == w] for w in H["things"]}
    rows[H["withheld"]] = [rgb for rgb, _t in H["held"][H["withheld"]]]
    report = {}
    for name, g in gens.items():
        feats = {w: np.stack([gaze.glances(rgb, g.retina, g.gaze, "surprise", "")["feats"][0] for rgb in rgbs]) for w, rgbs in rows.items()}   # the genome's own road, first fixation
        b = gate_ga.bands_feats(feats, np.random.default_rng(1)); b["within"].pop("all")
        ear = gate_ga.ear_band(words, False); floor = max(b["between"]["p95"], ear["max_between"])
        med = b["within"]["median"]; margin = med - floor
        A = feats["ahmad"]; C = A @ A.T; iu = np.triu_indices(len(A), 1); a_within = float(np.median(C[iu]))
        a_between = np.concatenate([(A @ feats[w].T).ravel() for w in rows if w != "ahmad"]); a_p95 = float(np.percentile(a_between, 95))
        report[name] = {"within_median": med, "within_p5": b["within"]["p5"], "between_median": b["between"]["median"], "between_p95": b["between"]["p95"], "floor": floor, "margin": margin, "met": margin > 0,
                        "closest_pair": b["closest_pair"], "ahmad_within_median": a_within, "ahmad_between_p95": a_p95, "ahmad_separates": a_within > a_p95, "n_feat": int(next(iter(feats.values())).shape[1])}
        print(f"G-4 [{name:24s}] within-median {med:.3f} (p5 {b['within']['p5']:.3f}) · between median {b['between']['median']:.3f} p95 {b['between']['p95']:.3f} · margin {margin:+.3f} {'MET' if margin > 0 else 'not met'} · ahmad within {a_within:.3f} vs between-p95 {a_p95:.3f} {'separates' if a_within > a_p95 else 'overlaps'} · closest {b['closest_pair']['pair']} {b['closest_pair']['p95']:.3f}")
    tr, un = report["eye-photo-g1 (trained)"], report["untrained twin"]
    g4 = tr["met"] and tr["ahmad_separates"] and (tr["margin"] - un["margin"] >= 0.05)
    report["G4"] = {"pass": g4, "trained_margin": tr["margin"], "untrained_margin": un["margin"], "delta_vs_untrained": tr["margin"] - un["margin"], "bar": "p95 rule met · ahmad separates · margin − untrained ≥ 0.05"}
    (OUT / "gate.json").write_text(json.dumps(report, indent=1, default=str))
    print(f"G-4 THE MARK: {'PASS' if g4 else 'FAIL'} — trained margin {tr['margin']:+.3f}, untrained {un['margin']:+.3f}, delta {tr['margin'] - un['margin']:+.3f}, ahmad {'separates' if tr['ahmad_separates'] else 'overlaps'}")


def stage_replay() -> None:
    stage_train(replay=True)
    j1 = json.loads((OUT / "journal.json").read_text()); j2 = json.loads((OUT / "journal-replay.json").read_text())
    p1 = np.load(OUT / "params.npz"); p2 = np.load(OUT / "params-replay.npz")
    same_bytes = all(np.array_equal(p1[k], p2[k]) for k in p1.files)
    loss3 = all(round(a["loss"], 3) == round(b["loss"], 3) for a, b in zip(j1["history"], j2["history"]))
    loss5 = all(a["loss"] == b["loss"] and a["val_top1"] == b["val_top1"] for a, b in zip(j1["history"], j2["history"]))
    rep = {"bytes_identical": same_bytes, "journal_identical_5dp": loss5, "journal_agrees_3dp": loss3, "threads": os.environ.get("OPENBLAS_NUM_THREADS"), "pass": same_bytes or loss3}
    (OUT / "replay.json").write_text(json.dumps(rep))
    print(f"G-5 replay: bytes identical {same_bytes} · journal identical to 5 dp {loss5} · agrees to 3 dp {loss3} → {'PASS' if rep['pass'] else 'FAIL'}")


if __name__ == "__main__":
    {"gradcheck": stage_gradcheck, "toy": stage_toy, "views": stage_views, "probe": stage_probe, "train": stage_train, "gate": stage_gate, "replay": stage_replay}[sys.argv[1]]()
