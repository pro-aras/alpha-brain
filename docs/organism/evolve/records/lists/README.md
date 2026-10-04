# The queue lists — which slice and checkpoint each list runs on

`launch_queue.sh <sha> <list> <out-root> <unit-suffix> [cp] [slice] [from-seq] [to-seq] [slot-mem]`; the defaults are S1 on checkpoint 32 (seq 304002 … 308667). Staged scratch: `/data/dev/swarm/2026-10-03/evolve-cal-scratch/`.

| list | slice (staged mini tape) | checkpoint | from-seq … to-seq |
|---|---|---|---|
| `N1-A0.tsv`, `N1-A0plus.tsv`, `N1-seeds.tsv`, `N1-stageA-eps.tsv`, `P-BAD-S1.tsv`, `P-GOOD-S1-probe{1,2,3}.tsv` | `slices/S1` | `cps/32` | 304002 … 308667 (the defaults) |
| `N2-S2.tsv` | `slices/S2` | `cps/8` | 202026 … 208101 |
| `R5-S2next.tsv` | `slices/S2next` | `cps/10` | 210626 … 214924 |
| P-GOOD's second slice (written once probe 1 has chosen the degradation) | `slices/S1next` | `cps/34` | 312375 … 316561 |

Nothing here runs before the verifier's co-signature and the seat's signature on AMENDMENT 3; the order and the branches are A3.6's.
