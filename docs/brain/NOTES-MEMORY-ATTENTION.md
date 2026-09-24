# Memory Attention (Jiale Kang, arXiv 2609.28399, submitted 2026-09-23) — a design note for THE BRAIN, 2026-09-24 16:01 +0400 (the seat)

**Ahmad's ask (15:59 +04, verbatim):** «I found an interesting topic. Check this out. Memory Attention. Could this already be here in our Alpha system or it's something new and we should add?»

## What the paper does (read from its HTML today; numbers as printed)
- Replaces attention's VALUE projection with a per-layer, token-indexed memory: **V = K + M**, where **M = Norm(E_ℓ[s])** — E_ℓ an embedding table per layer (N tokens × d_v), s the token ids at the key positions, RMSNorm per head. At inference the norm is folded into the table: value construction = a lookup + an add. Token-indexed retrieval allows the tables to live on CPU/SSD with prefetch (MA-Offload).
- Experiments: 24 layers, hidden 1,024 (10 B tokens) and 2,048 (20 B tokens), FineWeb-10BT; MHA / GQA / MQA. Gains: WikiText PPL 31.55 → 28.64 (small MHA), LAMBADA 50.46 → 43.68, average downstream +0.7 %; large MHA 21.52 → 20.79, +1.16 %. Offload: GPU memory 5,410 → 2,410 MiB (−55 %) at unchanged latency (prefill −0.31 %, decode −2.53 %).
- **The confound the author states himself:** the memory tables add parameters — the small MHA model goes from 373 M to 1,135 M (3×) — and there is NO matched-parameter control: «these results do not isolate the contribution of its structure from the increase in parameter capacity». Retrieval degrades beyond the 2 K training window for both methods. Single author, no affiliation given, code on GitHub (Joluck/memory-attention).

## Is it in the Alpha system? — No, and yes in spirit
- **No:** the creature has no attention and no value projection; nothing to replace.
- **Yes in spirit:** MA's memory table is an IDENTITY-indexed store that supplies the content while context (the keys) supplies the where and when. That is the division our cells already make: a cell per thing or word (content, born on one glance), with the moment's other senses as context. MA is that idea inside a transformer.

## What it means for THE BRAIN (CONCLUSION §3, the partnership)
1. **A candidate INTERFACE between the fast store and the slow network:** the network's keys come from context (order, the moment), its values from the cells' rows — the cells' embeddings ARE the memory table. This is a concrete, testable form of «the cells answer content, the network answers order» that the conclusion left open.
2. **A continual-learning property worth measuring:** a per-token row is updated only when that token is present (sparse gradients), and a new token is a new row — growth without touching the old. That is the shape of our budgeted birth and E48's «never eat the least-used» — and a possible mechanism against the interference Dohare 2024 and E48 measured. Unproven for continual learning by the paper (it trains once); our B2 can measure it.
3. **A cost property that fits this PC:** lookup + add instead of a projection; the tables can live in ordinary RAM — the CPU-only box loses nothing here.

## What we do with it
- **Not** into the creature now (no attention there).
- **Into B1 as a twin: A1-MA** — the soft network's attention with token-indexed values (V = K + Norm(E[s])), at MATCHED PARAMETERS against A1 (the paper's own missing control), graded on the same six tests; and as the designer's first candidate for the cells↔network interface in the hybrid F.
- **Into B2** if A1-MA passes at letters: the sparse-row update as an arm against forgetting.
- The claim to hold it to: a matched-parameter A1-MA ≥ A1 on U3 (composition) and ≤ A1 on cost, at both seeds; else it is a parameter increase wearing a new name.
