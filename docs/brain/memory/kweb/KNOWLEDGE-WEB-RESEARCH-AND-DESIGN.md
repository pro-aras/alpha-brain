# THE KNOWLEDGE WEB — how a brain stores, works, grows and uses its memories, and what the organism takes from it

*Claude (Opus 5.5, the seat, alone), 2026-09-29 22:38 +0400. A RESEARCH AND DESIGN document: no bar is set here and nothing is built from it; the law is `PREREG-KW-1.md` beside it. It follows `../MEMORY-SURGERY-RESEARCH-AND-DESIGN.md` (the memory line's design, his 20:41 word) and answers his 22:20 word.*

**His word (2026-09-29 22:20 +0400, verbatim):** «These memories and knowledge web and conceptual metadata, how is it stored, work and grow and used by brain, research on that and try adding similar memories of self awareness and some random growth mechanisms and test it on small scale. For the organism»

**How the sources were read.** Through a search engine's summaries and, for Knoblauch et al. 2014 (open, PLOS ONE), Vetere et al. 2019 (PMC) and Beckage et al. 2011 (PMC), through a summarising reader of the full text. No paper was read line by line tonight. Every number below names its source; a number a law will rest on is re-read in the paper's own text before that law is signed.

## 1 · The four questions, answered for the human brain

### 1.1 How it is STORED

| Store | What it holds | How it is held | Source |
|---|---|---|---|
| **The engram** | One experience | A sparse set of cells that were active at encoding and changed lastingly. Reactivating them recalls the memory; a memory can be «silent»: present, but not reachable by natural cues. | Josselyn & Tonegawa 2020, Science 367:eaaw4325 |
| **The hippocampal index** | Where the pieces of an episode live | The hippocampus does not store the episode's content. It stores an INDEX: a pointer to the pattern of cortical activity the episode made. A partial cue reactivates the index, the index reactivates the whole cortical pattern. | Teyler & DiScenna 1986; Teyler & Rudy 2007, Hippocampus 17:1158 |
| **The knowledge web (semantic memory)** | What things are, and how concepts relate | A HUB (the anterior temporal lobes) joined to SPOKES (the regions of each sense: shape, colour, sound, action, word). A concept is the hub's pattern that binds its spokes. | Lambon Ralph, Jefferies, Patterson & Rogers 2017, Nat Rev Neurosci 18:42 |
| **Concept cells** | One concept, whatever the sense | Single cells in the human medial temporal lobe that fire for one person or place in any picture or its written name. They link to each other: a new association between two concepts forms in ONE trial. | Quian Quiroga 2012, Nat Rev Neurosci; Ison, Quian Quiroga & Fried 2015, Neuron |
| **Two learning systems** | Fast episodes and slow structure | The hippocampus learns fast and keeps episodes apart; the cortex learns slowly and extracts what episodes share. Replay (in rest and sleep) teaches the cortex from the hippocampus, interleaved, so new learning does not erase old. | McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis & McClelland 2016, TICS 20:512 |
| **The wiring itself** | Much of long memory | Synapses and spines appear and disappear all life. Most new spines are transient; learning STABILISES some, and those last. In motor learning 10.6 % new spines formed within an hour of training; 42.3 % of those persisted months later. | Holtmaat & Svoboda 2009, Nat Rev Neurosci 10:647; Xu et al. 2009, Nature 462:915 |

**The shape of it.** A memory is not a record in a table. It is a change in which cells connect and how strongly, with an index that can find it again.

### 1.2 How its METADATA is kept

A brain keeps facts ABOUT a memory, but mostly not as a separate tag. The facts are bound into the trace or read from it at recall.

| Metadata | How the brain has it | Source |
|---|---|---|
| **When** | A slowly drifting «temporal context» is bound into every memory; memories made close in time share context, so one recalls the next. Memories made within a day even share CELLS (the excitability left by the first biases who takes the second). | Howard & Kahana 2002 (the temporal context model); Cai et al. 2016, Nature 534:115 |
| **Where it came from (source)** | NOT stored as a tag. Inferred at recall from the memory's features (how vivid, how detailed, what effort it carries), and so often wrong (a dream taken for a memory). | Johnson, Hashtroudi & Lindsay 1993, Psychol Bull 114:3 |
| **How important** | A LITERAL tag: a strong event sets a «tag» at the synapses it used, which captures the proteins that make the change last. A weak memory made near a strong or NOVEL event lasts, because the event supplies the proteins (behavioural tagging). | Frey & Morris 1997; Redondo & Morris 2011, Nat Rev Neurosci 12:17 |
| **How sure** | Metamemory: a second level MONITORS the first (feeling of knowing, confidence) and CONTROLS it (study more, answer or withhold). Monitoring and control can come apart. How well confidence tracks being right is measurable (the area under the type-2 curve) and differs between people with equal accuracy. | Nelson & Narens 1990; Fleming & Dolan 2012, Phil Trans R Soc B 367:1338 |
| **How it fits** | A new fact that fits a known framework (a schema) is learned in one trial and becomes independent of the hippocampus fast. | Tse et al. 2007, Science 316:76 |
| **Self-relevance** | Anything encoded in relation to oneself is remembered better: the strongest of all encoding strategies over 129 studies. | Symons & Johnson 1997, Psychol Bull 121:371 |

**What this means for a machine.** A brain infers source and pays for it with errors. The organism can do better by STORING the source (METADATA 1 does). But a brain also keeps metadata the organism does not have: when (a context that links neighbours in time), how important (a tag that decides what lasts), how sure (a monitor of its own reliability).

### 1.3 How it GROWS

| Growth | What happens | Source |
|---|---|---|
| **Random wiring, kept by use** | New synapses form at RANDOM among the places where an axon passes near a dendrite (potential synapses). A new synapse that is used while the memory is being made is consolidated; one that is not is removed. In a model of this, **structural plasticity stores far more per synapse than changing weights alone** (a fixed binary network: about 0.5 bits a synapse), and it explains the spacing effect (spread-out practice consolidates more) and why OLD memories survive while recent ones degrade when the network is full (Ribot's gradient), instead of a catastrophic collapse. | Knoblauch, Körner, Körner & Sommer 2014, PLOS ONE 9:e96485; Chklovskii, Mel & Svoboda 2004, Nature 431:782 |
| **Overgrow, then prune** | The young brain makes far more synapses than it keeps, then removes the weakest. Under a fixed energy budget, memory is best when synapses are first overgrown and then pruned by «minimal value» deletion. | Chechik, Meilijson & Ruppin 1998, Neural Comput 10:1759 |
| **New neurons** | The adult dentate gyrus keeps adding neurons. Young ones are excitable and join what is being learned now, so events close in time share them (they INTEGRATE); older ones keep similar events apart (they SEPARATE). | Aimone, Deng & Gage 2011, Neuron 70:589 |
| **The web of words** | Adult semantic networks are small worlds (most concepts a few steps apart) with a few hubs. A growth model in which each new concept attaches by copying the links of an existing, well-linked concept reproduces that shape. In real children, new words enter where the LEARNING ENVIRONMENT is well connected («preferential acquisition»), not where the child's own web is («preferential attachment»). Toddler webs are small worlds with as few as 55 words; late talkers' webs are less clustered. | Steyvers & Tenenbaum 2005, Cogn Sci 29:41; Hills et al. 2009, Psychol Sci 20:729; Beckage, Smith & Hills 2011, PLOS ONE 6:e19348 |
| **Consolidation in sleep** | Replay moves episodes into the slow system and keeps what matters (tagged, novel, rewarded). | Kumaran, Hassabis & McClelland 2016 |

**The shape of it.** Growth is partly RANDOM (which synapses appear, which new cells join) and made selective by USE (what is kept). Randomness proposes; experience disposes.

### 1.4 How it is USED

| Use | How | Source |
|---|---|---|
| **Recall from a part** | A partial cue completes the whole pattern through the index. | Teyler & Rudy 2007 |
| **Spreading to neighbours** | Activating a concept activates its linked concepts, strongest links first; this is why a word primes its associates. | Collins & Loftus 1975 |
| **Prediction and imagination** | The same stores that recall the past build expected futures (engrams support «imagining the future»). | Josselyn & Tonegawa 2020 |
| **Knowing what you know** | Monitoring decides whether to answer, withhold, or learn more. | Nelson & Narens 1990 |
| **Recall changes the memory** | A recalled memory becomes changeable again and is saved anew (reconsolidation); recalling also strengthens it (the testing effect). | Nader, Schafe & LeDoux 2000; Roediger & Karpicke 2006 |

### 1.5 Memories of the SELF

| Kind of self | What it is | Source |
|---|---|---|
| **The ecological self** | The self perceived in its surroundings: this body, here, moving, seeing from here. | Neisser 1988 (five kinds of self-knowledge) |
| **The minimal self: agency** | «I did that»: the brain predicts the result of its own act from a copy of the command; when the result matches the prediction, the act is felt as one's own. | Frith, Blakemore & Wolpert 2000 (the comparator model); Gallagher 2000 |
| **The extended (narrative) self** | The self across time: an autobiographical knowledge base (lifetime periods, general events, specific events) kept consistent with the «working self»'s goals. | Conway & Pleydell-Pearce 2000, Psychol Rev 107:261; Neisser 1988 |
| **The self as a knower** | Metacognition: a model of one's own reliability. | Fleming & Dolan 2012 |

## 2 · The software state of the art

| Method | What it does | Its limit |
|---|---|---|
| Growing Neural Gas (Fritzke 1995) | A graph that grows a node where error accumulates; edges between co-winning nodes are made, AGED and removed when old. | A map of one input space, not of relations between concepts |
| A-MEM, agentic memory (Xu et al. 2025, NeurIPS) | Every memory is a note with keywords, tags, a context, a time, links; a new note updates its linked old notes («memory evolution»). | Text notes judged by a language model; nothing ties a note to a sense |
| Knowledge editing (ROME, MEMIT) | A fact written into a network's weights | Many edits damage the network (see the memory surgery design) |

No method found stores a web grown from the organism's OWN senses, with its source and its confirmations kept, under a fixed budget that random growth and use keep sparse.

## 3 · What the organism has today (read from its code and its records)

| Store in the organism | Human counterpart | What it lacks |
|---|---|---|
| The brain's word map, prototypes and per-word episodes (`brain/scene/learners.py`) | Concept + spokes (sight features) | Links between concepts beyond «which words are of one kind» |
| The brain's saved scenes and runs (METADATA 1) | The index + source | When-context, importance, confirmation, use |
| The ear's co-occurrence counts | A proto-web | Only words said together; no budget; nothing is ever dropped |
| The census | Metamemory (what I hold) | How RELIABLE each holding is |
| The body's cells: birth by novelty, HEBB, PRUNE, MERGE, SLEEP replay (`genome/machinery.py`) | Growth, pruning, consolidation | Unbounded growth: the cost per canvas grows with the cells (the sleep A/B's arms cost 8 CPU-h each instead of the 1 priced, #247 (3); the long life reads 606 ms a canvas at 12,500 cells) |
| SELF (body numbers), the turn's `surprise` (DRIVE) | A body sense and a prediction error | No MEMORIES about itself: nothing kept about what it is, what it did, how reliable it is |

**Two measured facts from its own records (read tonight):**
- In the lean life `inh-b-t10000` (DRIVE on, 10,000 scenes), the brain's expectation of the parent's words failed to hold (`surprise` > 0) on 21.7 % of canvases after it began to expect, and on 16.5 % it was surprised by half the words or more. That is lived evidence about ITSELF, never kept today.
- In the full organism's first 12 hours (`alpha4-1`, seq ≤ 50,094), the shelf gave 15,222 heard words, 1,152 distinct, over 9,767 moments: a real stream of language, from which a web of word associations can grow.

## 4 · The design: THE KNOWLEDGE WEB, small

### 4.1 What is stored

- **Nodes:** concepts (a heard word; later a thing, a kind), and ONE `SELF` node.
- **Edges:** typed relations (`heard-near`: two words heard within a short window, the temporal-context link of 1.2; later `said-with`, `seen-with`, `kind-of`, `looks-like`).
- **Metadata on every node and edge**, kept, never inferred: `source` (lived, implanted, inherited), `author`, `first`, `last` (the order of life), `n` (evidence), `state` (silent, consolidated, demoted), `confirmed`, `contradicted`, `uses`.

### 4.2 How it grows: four rules, one difference each

| Rule | What it does | Human counterpart |
|---|---|---|
| **H**, Hebbian, unbounded | Every pair heard near each other gets an edge; nothing is dropped | The ceiling of information and the floor of economy: what the organism's ear does today |
| **F**, first come, budget B | As H until B edges exist, then no new edge ever | A brain without turnover |
| **L**, least used out, budget B | As H; when full, the edge with the least evidence (then the oldest) leaves for the new one | A smart deterministic rule: the bar random growth must clear |
| **S**, structural plasticity, budget B | A heard pair's edge is REALISED only with probability p (random, a seeded stream); a realised edge counts evidence while it lives; an edge reaching k evidence is CONSOLIDATED; an unconsolidated edge is removed after W events without evidence; when the budget is full, a new realisation takes the place of the silent edge with the least evidence | Random synaptogenesis kept by use (Knoblauch 2014; Holtmaat & Svoboda 2009) |

And its null, **S0**: S with the evidence counted for a RANDOM pair instead of the heard one. It must consolidate nothing true.

### 4.3 How it is used

- **Recall a neighbour:** «what goes with X?» = X's consolidated edges, strongest first.
- **Predict:** the web's edges, grown from the past, predict which pairs occur together in speech the organism has NOT heard yet.

### 4.4 The self

- **Implanted self-memories** (surgically placed, source `implanted-knowledge`, author «the seat»): predicates about the organism that life can check. Three true, two false, written before any record is read (the law lists them).
- **Lived self-memories:** the same predicates' rates as the life measures them, and the organism's own reliability per word (how often its expectation of that word was confirmed by the parent's next words).
- **Confirm and contradict** (the METADATA 2 sketch of `../MEMORY-SURGERY-RESEARCH-AND-DESIGN.md` §13.3): every lived event either confirms or contradicts an implanted self-memory; one whose contradictions outnumber its confirmations is DEMOTED, never deleted.
- **Knowing what it knows:** does its lived reliability per word predict whether it answers an exam item right (the type-2 area of 1.2)?

## 5 · What is tested tonight, and at what scale

`PREREG-KW-1.md`: a synthetic toy with planted associations and a null world; the organism's own shelf hearing (the first 60 % of the 12 h stream grows the web, the last 40 % is the held-out truth); the lean scene life's utterances as a second null; the self-memories on the lean life's own journal. Nothing runs inside a living body tonight: the web is grown from the organism's RECORDS. A law that wires it into a life comes after.

## Sources

- Josselyn & Tonegawa 2020: https://www.science.org/doi/10.1126/science.aaw4325
- Teyler & Rudy 2007: https://pubmed.ncbi.nlm.nih.gov/17696170/
- Lambon Ralph et al. 2017: https://www.nature.com/articles/nrn.2016.150
- Ison, Quian Quiroga & Fried 2015: https://www.cell.com/neuron/fulltext/S0896-6273(15)00559-0
- Kumaran, Hassabis & McClelland 2016: Trends Cogn Sci 20:512 (via https://sites.google.com/site/dharshankumaran1/publications)
- Holtmaat & Svoboda 2009: https://www.nature.com/articles/nrn2699 · Xu et al. 2009: https://www.nature.com/articles/nature08389
- Howard & Kahana 2002: https://www.researchgate.net/publication/222827636_A_Distributed_Representation_of_Temporal_Context · Cai et al. 2016: https://www.nature.com/articles/nature17955
- Johnson, Hashtroudi & Lindsay 1993: https://www.researchgate.net/publication/14853629_Source_Monitoring
- Redondo & Morris 2011: https://www.nature.com/articles/nrn2963
- Nelson & Narens 1990 (as described in https://arxiv.org/html/2604.15702v2) · Fleming & Dolan 2012: https://pmc.ncbi.nlm.nih.gov/articles/PMC3318765/
- Tse et al. 2007: https://www.research.ed.ac.uk/en/publications/schemas-and-memory-consolidation/
- Symons & Johnson 1997: https://pubmed.ncbi.nlm.nih.gov/9136641/
- Knoblauch et al. 2014: https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0096485 · Chklovskii, Mel & Svoboda 2004: https://www.nature.com/articles/nature03012
- Chechik, Meilijson & Ruppin 1998: https://direct.mit.edu/neco/article/10/7/1759/6200/Synaptic-Pruning-in-Development-A-Computational
- Aimone, Deng & Gage 2011: https://pubmed.ncbi.nlm.nih.gov/21609818/
- Steyvers & Tenenbaum 2005: https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2901_3 · Hills et al. 2009: https://pubmed.ncbi.nlm.nih.gov/19470123/ · Beckage, Smith & Hills 2011: https://pmc.ncbi.nlm.nih.gov/articles/PMC3092758/
- Neisser 1988: https://www.tandfonline.com/doi/abs/10.1080/09515088808572924 · Conway & Pleydell-Pearce 2000: https://www.researchgate.net/publication/12528554_The_Construction_of_Autobiographical_Memories_in_the_Self-Memory_System
- Frith, Blakemore & Wolpert 2000 (the comparator model, as described in https://pmc.ncbi.nlm.nih.gov/articles/PMC11141391) · Gallagher 2000: https://www.academia.edu/2363112/Gallagher_S_2000_Philosophical_conceptions_of_the_self_implications_for_cognitive_science
- Fritzke 1995: https://proceedings.neurips.cc/paper/1994/file/d56b9fc4b0f1be8871f5e1c40c0067e7-Paper.pdf
- A-MEM: https://arxiv.org/abs/2502.12110
