# MEMORY SURGERY — research and design: authored memories, their metadata, and a census

*Claude (Fable 5.1, the seat, alone), 2026-09-29 20:44 +0400. A RESEARCH AND DESIGN document. No bar is set here and nothing is built from it; each part gets its own signed law with its bench read first. Every figure about the brain is read from the file it names.*

## 1 · His words

- 2026-09-29 20:22 +0400: «why don't we synthetically place the memories and the raw knowledge there in the brain to start and begin with? … That would be more like human mechanism as we are trying to replicate here»
- 2026-09-29 20:41 +0400: «No, the memories part is much more then that. Don't take it easy. It is seriously a gap and we need to fix it. We can create the memories and experiences from our own side and surgically place them in brain. Giving it a cognitive metadata and census as well. This is very deep gap and we need to bring it together with deep research and development of it. So take it seriously»

## 2 · What the seat got wrong at 20:30

The seat answered with the smallest form: a newborn copies a parent's brain (INHERIT). It also said the lineage's words «cannot be placed». Both were too small. His ask is AUTHORED memory: experiences we write, placed by us, each carrying what it is and where it came from. INHERIT stays as the baseline arm, nothing more.

## 3 · What a memory IS in this brain today

Read from `/data/dev/genome-lives/brain-lean-nearest-20261102/state/brain.json` (a brain after 10,000 scenes).

| Store | Field | Size in that brain | What it is |
|---|---|---|---|
| The word map | `V`, `b` | 14 words × 146 features | What each word expects to see. Semantic memory. |
| The prototypes | `proto_sum`, `proto_w`, `meetings` | 14 × 146 | The average look of what each word named. |
| The episodes of each word | `store_x`, `store_z`, `store_r`, `store_t` | one list per word | Each meeting kept: the raw look, the standardised look, how sure the brain was that the word meant this thing, and its order in life. Episodic memory. |
| The ear | `ear` | counts | Which words were said alone and together. From it the brain learns the KINDS (shape, colour, size). |
| The statistics | `stats` | n 15,271 | The mean and spread of everything the eye delivered. |
| The thresholds | `tau_point`, `tau_word`, `tau_none`, `refusal` | per word | Where «I don't know» begins. |
| The life's lists | `seen`, `moments`, `scenes`, `canvas` | 10,000 each | Every scene learned, in order. |
| The citations | `episodes` | 20,006 | What the brain points to when asked «why». |

**The gap, stated exactly.** No field in any store says WHERE a memory came from, WHO wrote it, HOW SURE it is beyond one number, how often life CONFIRMED it, or when it was last USED. The brain cannot tell a thing it lived from a thing it was given. It has no census: nothing counts what it holds. The organism's other mind (the cells) has the same gap.

## 4 · The human mechanism (sources read 2026-09-29)

| Finding | Source | What it means for the build |
|---|---|---|
| A baby is not born blank. Systems for objects, number, space, actions and social partners are present before experience. Newly hatched chicks with no visual experience show them. | Spelke & Kinzler 2007, «Core knowledge», Developmental Science; Vallortigara's chick studies | Some knowledge is PLACED before life. His idea is the human mechanism. |
| Before the eyes open, the retina makes its own waves. They flow in the pattern that real forward motion will make days later, and they tune the brain's motion cells. | Ge et al. 2021, Science, «Retinal waves prime visual motion detection by simulating future optic flow» | The body AUTHORS synthetic experience for itself before birth, in the code of its own sense. |
| A memory was made with NO experience: a smell's own input cells were driven by light, paired with reward or aversion. The mice later approached or avoided the REAL smell. The memory depended on the pairing and used the same circuits as a natural one. | Vetere et al. 2019, Nature Neuroscience 22:933, «Memory formation in the absence of experience» | Surgery works when the memory is written in the brain's OWN code and with the same contingency life would give. |
| A false memory was created by reactivating the cells of one place during a shock in another. The mice feared the place where nothing had happened. | Ramirez et al. 2013, Science 341:387 | An implant can be FALSE and is then believed like a true one. Surgery needs a safety test. |
| With a prior schema, a new fact is learned in ONE trial and consolidates fast. | Tse et al. 2007, Science 316:76 | A placed framework should make later learning faster. This is the measurable gain. |
| Humans store no tag for a memory's source. They infer it from the memory's features, and they err. | Johnson, Hashtroudi & Lindsay 1993, Psychological Bulletin 114:3 | A machine can do better than the human here: it can STORE the source. |

## 5 · The software state of the art

| Method | What it does | Its known limit |
|---|---|---|
| Generative replay / pseudo-rehearsal (Shin et al. 2017 and after) | Synthetic samples are made and learned beside the real ones | Only as good as the generator |
| Pre-training on retinal waves (ReWaRD 2023; PLOS Comput Biol 2025) | Networks are trained on simulated waves before real images | A prior for the eye, not knowledge of words |
| Knowledge editing, ROME and MEMIT (Meng et al. 2022) | A fact is written straight into the weights as a key and a value | Many edits degrade the model («Model Editing at Scale leads to Gradual and Catastrophic Forgetting», ACL 2024); edits do not ripple to related facts (TACL 2024) |
| The memory stream of Generative Agents (Park et al. 2023) | Every memory is a record with metadata; retrieval scores recency, importance and relevance | Records are text; nothing ties them to a sense |

No method found joins all three: a memory written in the learner's own sensory code, carrying its source, and counted. That is the build.

## 6 · The design: the roads of surgery, from the gentlest cut to the deepest

| Road | The cut | The human parallel | What is written | The risk the law must test |
|---|---|---|---|---|
| **1 · PRENATAL LIFE** | Authored scenes are shown to the brain's own eye before birth and learned by its own rule | Retinal waves | Everything, by the brain itself | None to consistency; costs time |
| **2 · EPISODE IMPLANT** | An authored experience is rendered and read once by the eye to get its code. It is then learned by the brain's OWN rule (`RWLearner.train_scene`) with the named thing GIVEN. Life never gives it: the parent names a thing and the child must work out which. That gift is the surgery. | Vetere 2019: the input was driven and the brain's own plasticity made the memory | Every store and the word map, by the brain's rule | Consistent by construction. The risk is a wrong gift: see M-3 |
| **2b · THE RAW WRITE** | The episode is written DIRECTLY into the word's episode store and prototype, and the learning rule is skipped | Ramirez 2013: the false-memory shape | `store_x/z/r/t`, `proto_*`, `meetings` | The word map `V` was not trained on it, so the stores and the map may disagree. Used ONLY inside M-3, never as a birth road |
| **3 · KNOWLEDGE IMPLANT** | A word's expectation is written with NO episode behind it | Core knowledge; ROME | `V`, `b`, the prototype, the thresholds | It cites nothing; many such edits may damage neighbours |
| **4 · INHERIT** | A parent's whole brain is copied | Not a human mechanism | The state | The baseline. Built tonight; its lives are running |

The same four roads apply later to the organism's cells.

## 7 · COGNITIVE METADATA: what every memory carries

One record per episode, kept beside the store at the same index, and one summary per word.

| Field | Values | Used for |
|---|---|---|
| `source` | lived · prenatal · implanted-episode · implanted-knowledge · inherited | «Why» says which; the census counts by it |
| `author` | the life's own name · the parent's name · the seat · Ahmad | Who is answerable |
| `written_at` | the clock, and the life's own count | Age |
| `origin` | world seed and scene, or the authored scene's own text | The memory can be shown again |
| `confidence` | the responsibility at writing | How sure |
| `confirmed` | how many LIVED meetings agreed with it since | An implant that life confirms becomes trusted |
| `contradicted` | how many lived meetings disagreed | An implant that life refutes is demoted, never deleted |
| `last_used`, `uses` | count | What the brain leans on |

**Three behaviours that read the metadata:**
1. Asked «why», the brain names the source: «I lived it», «I was born with it», «I was given it».
2. A given memory that life never confirmed is held with less weight than a lived one.
3. A contradicted implant opens a clash and is demoted. It is never silently overwritten (the BELIEF law of the genome).

## 8 · THE CENSUS

The seat reads «census» as a full count of what the brain holds. To be corrected by him if he meant another thing.

- Per word: meetings by source, episodes by source, maturity, its kind, confirmations, contradictions, last use.
- Per brain: words, episodes, the share lived and the share given, implants never confirmed, implants contradicted, the oldest and the newest memory.
- Written to STATUS and the journal at every calibration, and as a file at birth and at close. One format for every life, so the lineage can be compared census to census.
- Its test: the census must equal a recount from the stores, and a planted record must move it by exactly one.

## 9 · The experiments, each with its twin and its null

| Name | Question | Arms | The null |
|---|---|---|---|
| **M-1 · the four roads** | At birth and after a childhood, which road gives the most, and does any harm? | Blank · inherit · prenatal · episode implant · knowledge implant | The same implants with the words shuffled |
| **M-2 · a thing the world never names** | Can a word the parent never says be given? The world draws a moon and says its name once in 10,000 scenes («dax») | «dax» implanted by roads 1, 2 and 3 | The blank brain's one meeting |
| **M-3 · a FALSE memory** | If a wrong memory is placed (circles called «square»), does life correct it, how fast, and does the metadata demote it? Does the raw write (road 2b) leave the stores and the word map in disagreement? | 10, 100 and 1,000 false episodes, by road 2 and by road 2b | The same number of true ones |
| **M-4 · the schema gain** | Does a placed framework make the NEXT word faster to learn (Tse 2007)? | The kinds (shape, colour, size) implanted, then a new colour taught | No framework |
| **M-5 · the metadata and the census** | Does «why» tell lived from given every time? Does the census equal the recount? | One life with every source mixed | A planted record |
| **M-6 · the lineage** | Which of Alpha 3's words can be tied to a sight this eye can take? | His dictionary's words as WRITTEN forms (the reading sense shows a word as a picture of itself) with their gloss words | The same forms with glosses shuffled |

M-6 states its own limit: it gives the look of a written word and its neighbours. It does not give the meaning in things. That needs pictures, which is the road to his offer of videos.

## 10 · The order of the build

1. **The metadata and the census first** (§7, §8). Surgery without a record of what was placed is the one thing not to do: after it, nobody can tell what the brain lived.
2. Road 1, prenatal life. It needs no new writing code, only an author and the tag.
3. Road 2, the episode implant, with M-3 (the false memory) as its safety gate. Road 2b lives only inside M-3.
4. Road 3, the knowledge implant.
5. M-1 to M-6 read on the ladder, one difference at a time.

## 11 · Decided by the seat under his delegation, his to overturn

1. «Census» is read as a full count of what the brain holds, by source (§8).
2. The first authored memories: the three kinds (shape, colour, size), the fourteen words, and the never-named moon.
3. The false-memory test M-3 RUNS. It is the safety gate of the surgery.

## 12 · What the build must not break

- The metadata adds fields to the brain's saved state, so the state's version and hash change. An OLD state loads under the new code with every record marked `source: lived` and `author:` the life's own name. The law carries this migration clause and its test.
- The order of life is already kept in `store_t`. The metadata refers to it and does not copy it.
- A running life is not touched: `brain-long-1` lives on its own checkout.

## Sources

- Spelke & Kinzler 2007: https://www.harvardlds.org/wp-content/uploads/2017/01/SpelkeKinzler07-1.pdf
- Ge et al. 2021: https://www.science.org/doi/10.1126/science.abd0830
- Vetere et al. 2019: https://www.nature.com/articles/s41593-019-0389-0
- Ramirez et al. 2013: https://www.science.org/doi/10.1126/science.1239073
- Tse et al. 2007: https://www.research.ed.ac.uk/en/publications/schemas-and-memory-consolidation/
- Johnson, Hashtroudi & Lindsay 1993: https://www.researchgate.net/publication/14853629_Source_Monitoring
- ReWaRD: https://arxiv.org/html/2311.17232 · PLOS Comput Biol: https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1012830
- MEMIT: https://arxiv.org/pdf/2210.07229 · editing at scale: https://aclanthology.org/2024.findings-acl.902.pdf · ripple effects: https://aclanthology.org/2024.tacl-1.16.pdf
- Generative Agents: https://arxiv.org/pdf/2304.03442

*The seat read the search summaries and abstracts of these sources tonight, not the full papers. Each is to be read whole before its law is signed.*
