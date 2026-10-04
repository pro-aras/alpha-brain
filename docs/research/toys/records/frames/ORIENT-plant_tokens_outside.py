from tools.toys.frames import streams as ST
ms = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
n_train = ST.split_index(len(ms))
print("ALPHA4 plain moments", len(ms), "plain split index", n_train)
for i, m in enumerate(ms):
    if "zzq" in m.words or "xxv" in m.words:
        print(i, "train" if i < n_train else "held", m.source, m.name, m.words, m.seqs)
sc = ST.scene_moments(ST.load_moments(sorted((ST.COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))))
print("SCENE moments", len(sc), "with zzq/xxv:", sum(1 for m in sc if "zzq" in m.words or "xxv" in m.words))
