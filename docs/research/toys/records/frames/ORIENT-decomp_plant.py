"""Decomposition of the planted frame's gain (a record cited by AMENDMENT-1; committed under docs/research/toys/records/frames/ORIENT-decomp_plant.py).

saving = bits0 - bitsF is a sum over the held-out tokens. Under F = {(zzq, xxv)} only the tokens whose COUNT changes differ in cost beyond the denominator:
  (1) the held-out PLANT moments: [zzq, xxv, END] under the empty set -> [FRAME, END] under F;
  (2) any REAL held-out occurrence of zzq or xxv outside a plant (the law calls both «in no vocabulary»; on alpha4-1 xxv is a real word, a chapter heading: 4 moments);
  (3) every OTHER held-out token: the same count under both parses, so it differs only through the denominator, by delta = log2((N0 + K0) / (NF + KF)).
The parts are summed and checked against the Scorer's bits0 - bitsF.
"""
import math
from collections import Counter

from tools.toys.frames import compress as CO, plants as PL, streams as ST


def decompose(ms, every):
    tr, he = PL.condition_parts(ms, "plant", every)
    train, held = PL.words_of(tr), PL.words_of(he)
    sc = CO.Scorer(train, held)
    F = {ST.PLANT}
    g = sc.gain(F)
    c0, cF = Counter(), Counter()
    for m in train:
        c0.update(CO.parse_moment(m, set()))
        cF.update(CO.parse_moment(m, F))
    n0, k0 = sum(c0.values()), sc.V + 2
    nF, kF = sum(cF.values()), sc.V + 1 + 2
    z, x = ST.PLANT

    def cost(counts, t, n, k):
        return -math.log2((counts.get(t, 0) + 1) / (n + k))

    plant_moments = [m for m in he if m.source == "plant"]
    plants_held = len(plant_moments)
    cost0 = cost(c0, z, n0, k0) + cost(c0, x, n0, k0) + cost(c0, CO.END, n0, k0)
    costF = cost(cF, ST.PLANT, nF, kF) + cost(cF, CO.END, nF, kF)
    part1 = plants_held * (cost0 - costF)
    real = [(m.source, m.name, w) for m in he if m.source != "plant" for w in m.words if w in (z, x)]
    part2 = sum(cost(c0, w, n0, k0) - cost(cF, w, nF, kF) for _s, _n, w in real)
    n_held_tokens = sum(len(m) + 1 for m in held)
    n_other = n_held_tokens - 3 * plants_held - len(real)
    delta = math.log2(n0 + k0) - math.log2(nF + kF)
    part3 = n_other * delta
    return {"plants_train": PL.n_plants(tr), "plants_held": plants_held, "N0": n0, "NF": nF, "K0": k0, "KF": kF,
            "train_count_of_zzq_as_word_under_empty": c0.get(z, 0), "train_count_of_xxv_as_word_under_empty": c0.get(x, 0), "train_count_of_xxv_as_word_under_F": cF.get(x, 0),
            "real_held_out_occurrences_of_plant_tokens": len(real), "merge_saving_per_plant_bits": cost0 - costF, "delta_bits_per_other_token": delta, "n_other_held_tokens": n_other,
            "part1_plants_merge": part1, "part2_real_occurrences_of_plant_tokens": part2, "part3_denominator_effect": part3, "sum_of_parts": part1 + part2 + part3,
            "scorer_bits0_minus_bitsF": g.bits0 - g.bitsF, "L": g.L, "G": g.G, "expected_first_order": PL.first_order_saving(plants_held, sc.n0, PL.n_plants(tr), sc.V)}


if __name__ == "__main__":
    a4 = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
    scn = ST.scene_moments(ST.load_moments(sorted((ST.COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))))
    for name, ms, every in (("ALPHA4", a4, 100), ("SCENE", scn, 10)):
        d = decompose(ms, every)
        print(f"{name}+PLANT: " + ", ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in d.items()))
        print(f"  check: part1 {d['part1_plants_merge']:.4f} + part2 {d['part2_real_occurrences_of_plant_tokens']:.4f} + part3 {d['part3_denominator_effect']:.4f} = {d['sum_of_parts']:.4f} "
              f"vs the Scorer's bits0 - bitsF {d['scorer_bits0_minus_bitsF']:.4f} (difference {d['sum_of_parts'] - d['scorer_bits0_minus_bitsF']:.2e})")
