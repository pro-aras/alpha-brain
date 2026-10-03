from collections import Counter
from tools.toys.frames import compress as CO, plants as PL, streams as ST
a4 = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
tr, he = PL.condition_parts(a4, "plant", 100)
train, held = PL.words_of(tr), PL.words_of(he)
sc = CO.Scorer(train, held)
g = sc.gain({ST.PLANT})
s = CO.slow_gain(train, held, {ST.PLANT})
print("fast", {k: getattr(g, k) for k in ("G", "bits0", "bitsF", "L", "N", "K", "V", "n_held_words")})
print("slow", s)
print("diff G", g.G - s["G"], "bits0", g.bits0 - s["bits0"], "bitsF", g.bitsF - s["bitsF"])
# which held tokens are UNK, and how many
vocab = sc.vocab
unk = sum(1 for m in held for w in m if w not in vocab)
print("held words not in the train vocabulary (UNK):", unk, "of", sum(len(m) for m in held))
# any word of a held plant moment that is not zzq / xxv?
odd = [m for m in he if m.source == "plant" and m.words != ST.PLANT]
print("odd plant moments", len(odd))
# is zzq or xxv anywhere outside plants?
out = sum(1 for m in tr + he if m.source != "plant" and ("zzq" in m.words or "xxv" in m.words))
print("zzq/xxv outside plants:", out)
