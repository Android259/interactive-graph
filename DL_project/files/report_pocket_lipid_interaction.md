# Pocket–Lipid Interaction

*Report on the prediction of LTP–lipid binding from protein structure and lipid chemistry.
This file supersedes the earlier LaTeX report. Sections 1, 2, 6 and 7 revise it, answering the
questions its text left open wherever the pipeline answers them; sections 3, 4, 5, 8 and 9 are
new and cover the work of July–August 2026. Results are reported for the base configuration
only (§8) — the experiments run against it are not in this file yet.*

Contents

1. [Introduction](#1-introduction)
2. [Data](#2-data)
3. [Data splits](#3-data-splits)
4. [Marginals and the reference point](#4-marginals-and-the-reference-point)
5. [What the representations can and cannot carry](#5-what-the-representations-can-and-cannot-carry)
6. [Architecture of the base model](#6-architecture-of-the-base-model)
7. [Training](#7-training)
8. [Base configuration and its results](#8-base-configuration-and-its-results)
9. [Questions still open](#9-questions-still-open)

---

## 1. Introduction

Lipid transfer proteins (LTPs) are peripheral membrane proteins that move a lipid from a donor
to an acceptor membrane, with specificity for both the membranes and the lipid. Their structure
contains a hydrophobic cavity that envelops the lipid.

The dataset comes from a system-wide lipidomics screen of human LTPs (Titeca et al., 2023): each
measured protein was assayed against a panel of lipid species, and the lipids found inside the
protein are the positive observations. From this we build a binary task: given a protein and a
lipid, does this protein bind this lipid.

The protein side is treated structurally — a residue-level graph derived from the Voronoi
tessellation of the structure, processed with graph neural networks (PyTorch Geometric) and
conditioned on a protein language model embedding. The lipid side has no complex structure
available, so the lipid is represented by its SMILES string, embedded with a chemical language
model (MoLFormer). The two representations are joined by cross-attention and reduced to one
binary decision.

Everything below distinguishes two things carefully, because the whole difficulty of the project
sits in the distinction: what the model can predict from **each partner alone** (a marginal — one
number per lipid, or one per protein), and what it can predict only from **the pair**. The
project is about the pair; almost all of the measurable signal so far is marginal.

---

## 2. Data

### 2.1 The interaction table

One row is a (protein, lipid) pair with a 0/1 label. The active table is
`data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted.csv`
(row order is part of the data contract: original row positions are the pair IDs that the
Tanimoto sample weights and the auxiliary graph losses index by).

| | |
|---|---|
| rows | 11018 |
| proteins (`LTPProtein`) | 35 |
| families (`ProteinDomain`) | 9 |
| lipid species (`FullIdentityOfLipid`) | 312 |
| head-group classes | 34 |
| positives | 756 (0.069) |

Positives per family: CRAL-TRIO 204, START 200, lipocalin 90, GLTP 81, IP_trans 65,
LBP_BPI_CETP 55, scp2 43, ML 10, OSBP 8.

35 × 312 = 10920 cells against 11018 rows (98 pairs measured twice): **the matrix is filled
almost completely**. This is not a sparse set of observations, it is a full screening matrix, and
Section 3 shows why that single fact decides what a train/test split can and cannot mean here.

There are 34 classes rather than 36 because two entries carried a stray `': '` prefix that split
phosphatidylcholine and phosphatidylglycerol each in two; `lipid_class_series` in
[dataloader/sampler.py](../dataloader/sampler.py) strips the leading punctuation. Harmless for a
balancer, not harmless for a split by class — the real class would leave training while its twin
stayed in.

### 2.2 Protein structures

35 structures, one per protein: 32 experimental (PDB), 3 AlphaFold models where no experimental
structure without mutations was available (`data/esm3_input/is_predicted_manifest.csv`). Selection
was made on Uniprot family/domain annotation, mostly from PROSITE.

The questions that were open in the earlier draft, as the pipeline currently answers them
(audited in [preprocessing/build_consistent_esm3_pdb.py](../preprocessing/build_consistent_esm3_pdb.py)):

- **Alternate conformations.** Voronota already normalizes them: raw BPI has 474 CA records for
  456 residues (18 duplicated by altLoc), and the processed structure has exactly 456 — one
  conformer per residue. Nothing further is done downstream.
- **Selenomethionine.** MSE is a HETATM in the raw PDB and Voronota's protein filter *deleted*
  those residues. Fixed at the source: `preprocessing/convert_mse_to_met.py` rewrites MSE as MET
  and the two affected graphs (GM2A, PITPNA) were regenerated, so their node counts now equal
  their FASTA lengths (162 and 269).
- **Missing fragments.** Unresolved residues (e.g. CERT_6j81, gaps at 492–496 and 534–541) are a
  physical absence in the crystal, not a file artifact. They are simply absent from the graph; no
  placeholder residues are inserted and no gap is modelled.
- **Low-confidence regions.** Nothing is filtered by pLDDT. Only 3 of 35 structures are predicted
  at all. The per-residue confidence *is* recovered and stored
  (`data/esm3_input/<stem>_node_confidence.csv`: pLDDT/100 for AlphaFold stems,
  `1 - minmax(B-factor)` for experimental ones, so higher always means more ordered), but the base
  configuration does not read it — it is consumed only by the v2 ESM3 input path
  (`--use_esm3_v2_embeddings`).
- **Domain cropping.** None. The whole chain as deposited (after the normalizations above) enters
  the graph; there is no domain-level trimming step in the pipeline.

### 2.3 Pocket detection

Pockets are annotated with Voronota's `voronota-pocket` (Olechnovič & Venclovas, 2014), writing
pocket membership into the B-factor column of `data/graphs/<protein>/pocketness.pdb`. LTP cavities
are large and hydrophobic, so the parameter set has to separate the interior cavity from the
surface grooves; parameters were tested per protein
(`preprocessing/voronota_parameter_per_ltp.xlsx`) and the resulting annotations were inspected
visually in PyMOL for every protein in the set.

Two consequences worth stating, because they are easy to misread:

- `pocketness.pdb` is **not** the original structure file. Its B-factor column holds a binary
  pocket flag (only 0.00 and 1.00 occur), so the real B-factor/pLDDT is not recoverable from it —
  which is why the confidence files of §2.2 exist separately.
- The per-residue pocket flag used by the model is built from the **side-chain** atoms only
  (atoms named `C, CA, CB, O, N` — the backbone plus CB — are skipped): a residue counts as a
  pocket residue if any of its remaining atoms is marked. Buriedness is a separate, continuous per-residue quantity
  (`residue_mean_buriedness`), not a mask.

### 2.4 Protein graph construction

Graphs are generated by `voronota-js-receptor-data-graph`
(<https://github.com/kliment-olechnovic/generating-graphs-of-protein-receptors>) into
`data/graphs/<protein>/`, as node and edge tables. Atom-level tables carry no prefix, residue-level
tables carry the `coarse` prefix. **The model uses the coarse, residue-level graph**: with 35
structures the atomic description is too noisy to fit, and the residue level is also the level at
which PLM tokens live, so the two can be concatenated node by node.

Neighbours are **Voronoi contacts, not k-nearest neighbours and not a distance cutoff**: an edge
exists between two residues whose Voronoi cells touch. What reaches the model per graph:

| tensor | content |
|---|---|
| node features `[N, 3]` | `residue_type`, `residue_sas_area`, `residue_volume` |
| edge features `[E, 3]` | `distance`, contact `area`, `boundary` (the solvent-facing part of the contact) |
| buriedness `[N]` | `residue_mean_buriedness`, continuous |
| pocket mask `[N]` | boolean, from `pocketness.pdb` as described above |
| PLM `[N, 1536]` | ESM3 residue embedding, §2.5 |

Optional extras exist and are off in the base configuration: two more Voronota columns
(`residue_mean_ev28`, `residue_mean_ev56`) plus a Kyte–Doolittle hydropathy lookup
(`--protein_extra_node_features`), and 13 aggregate cavity descriptors broadcast to every residue
(`--pocket_descriptors`, see §5.2 for why they are off).

Edges are stored in one direction; `--bidirectional_edges` adds the reverse edges and is off by
default.

### 2.5 Protein embedding

The Voronota graph features alone were never enough to learn the task, so the sequence is embedded
with ESM3 (`esm3-sm-open-v1`, `preprocessing/EmbedProtein.py`) and the embedding is attached to
the structure, residue by residue. Embeddings live in `data/embedding_ESM3/` and have shape
`[N + 2, 1536]`: ESM3 adds `<BOS>` and `<EOS>`, which the loader trims (`esm3_tensor[1:-1]`), after
which there is exactly one row per graph node. This alignment is an invariant of the data contract
— node rows, embedding rows and `pocketness.pdb` residues must have equal length and order.

1536 dimensions next to 3 structural features would drown them, so the embedding is compressed by
a learned linear projection to `plm_compression_dim` *before* concatenation with the node features
and buriedness. In the base configuration that projection is aggressive (§8.1), and §5.1 explains
why that costs nothing.

The v1 embeddings are **sequence-only**. A structure-conditioned variant exists
(`data/embedding_ESM3_v2/`, built from `data/esm3_input/<stem>.pdb` with coordinates, SASA and
confidence) and so do frozen alternatives — ESM-IF1, ProteinMPNN, SaProt, RNA-BAnG — each behind
its own flag. None of them is part of the base configuration.

### 2.6 Lipid representation

The screen reports a head group and a chain description per lipid species
(`data/LTP-lipid_interaction.csv`); structures are fetched from LIPID MAPS by REST
(`data/lipid_maps_fetch.py`) as SMILES.

The chemistry is only partly determined by the measurement: the head group and the total mass are
known, the exact acyl composition frequently is not. That ambiguity is kept explicitly rather than
resolved by guessing — a lipid's SMILES field is a `;`-separated list of candidate structures
(sn-positional and double-bond isomers) for the same measured species. Parsing strips each part,
drops empty and `0` parts and de-duplicates by canonical SMILES; a candidate that parses but has
no embedding raises rather than being silently skipped.

Four treatments of that candidate list exist (`lipid_first_fragment_only` — the default, first
usable candidate only; `lipid_concat`; `lipid_random_choice`; `lipid_fragments_mask`). The base
configuration uses the default: one candidate per row. So the ambiguity is **represented in the
data and not yet exploited by the model**, and every result below inherits an input that is at
best similar to the molecule the mass spectrometer saw.

### 2.7 Lipid embedding

SMILES are tokenized and embedded with a pretrained MoLFormer (Ross et al., 2022), using the
IBM `pretrained_molformer` notebook adapted in `preprocessing/frozen_embedding.py`. A sequence
comes out as `[N, 768]` with a leading `<CLS>` token that can stand for the whole molecule instead
of pooling. MoLFormer was chosen as a chemical language model pretrained at scale on small
molecules, and it is used **frozen**: the whole embedding table is precomputed offline
(`data/lipid_SMILES_embedding.pkl`, plus an isomeric variant), so no gradient reaches it.

An alternative path represents the lipid as an actual atom/bond graph
(`data/build_lipid_isomer_graphs.py`, 11 node features and 6 edge features, both bond directions
written), selected by `--lipid_graph_isomers`. It is not used in the base configuration.

### 2.8 Positives, negatives and duplicates

Several rows of the original dataset describe the same interaction from different experiments;
profiles without side-chain detail were merged with profiles that have it.

**The screen reports only positives.** Every (protein, lipid) cell not reported positive is taken
as a negative. This is the single largest assumption in the dataset, and it has two consequences
that shape everything downstream: the label is 6.9 % positive, and an unknown share of those
negatives are false — lipids that simply were not detected.

Negatives are therefore subsampled rather than used whole, and *which* negatives are drawn changes
the result. The sampler is chosen by flags, most specific first
([dataloader/sampler.py](../dataloader/sampler.py)):

| flag | negatives drawn per positive, within | 1:1 achieved |
|---|---|---|
| `--balanced_lipid_classes` | (family, lipid class) cell | per family and class, globally; **not** per protein |
| `--balanced_proteins` | each `LTPProtein` | per protein, per family, globally |
| `--balance_negatives_by_family` | each `ProteinDomain` | per family, globally; not per protein |
| none | global 5.6 % random subsample | none |

`--negatives_per_positive` (default **2**) sets how many negatives are drawn per positive inside
each balancing group. The exact 1:1 match discards 86 % of the table — and the rows it discards are
precisely the record of which lipids a protein does *not* bind; ratio 2 keeps the grouping (so the
between-protein prior the grouping removes stays removed) and only coarsens the class ratio, to
about 33 % positives in train. Results produced before this default changed were 1:1 and are not
directly comparable.

The base configuration uses `--balanced_proteins --negatives_per_positive=2`.

---

## 3. Data splits

Three splits are in use. They differ in which axis of the screening matrix is held out, and
therefore in which question the metric answers. All three are group-disjoint (no random row
split), all three are implemented in `_split_interactions`
([dataloader/Dataloader.py](../dataloader/Dataloader.py)), and all three print their own
leakage check into the run log (§4.3).

### 3.1 Why the split decides the question

Because the matrix is essentially complete (§2.1), holding out a protein family is not "holding
out some observations" — it is **holding out whole rows of a fully known matrix, with every column
still in place**. A lipid that appears in the held-out block appears ~35 times in the table, once
per protein, and the other ~31 of those rows are in training. The pair is new; the lipid is not.

That is enough to predict the label without knowing anything about the held-out protein: answer
with the lipid's own training positive rate. Nothing illegitimate happens — the estimate uses only
training labels — the problem is that **the estimate is nearly sufficient**, so a metric measured
against 0.5 credits the model for a `groupby`.

### 3.2 Protein cold split (the baseline for all earlier experiments)

One or more whole protein families leave training (`--excluded_groups`); the held-out rows are
split 50/50 into validation and test. With `--test_group` (plus `--cold_split`) the validation and
test blocks are two *different* whole families instead of two halves of one.

Measured consequence, on the pool the model actually sees:

| | |
|---|---|
| test lipids already seen in training | 98.5 % |
| head-group classes seen in training | 100 % |
| per-lipid prior baseline (test) | 0.562 balanced accuracy, up to 0.70–0.77 on individual families |

The pairs genuinely do not repeat — no training row equals a validation row. What carries over is
the **marginal**, not the row (§4).

This split is the one every experiment predating the two-axis split was run on. Numbers from
those runs are not wrong, but they must be read against ~0.56, not against 0.50.

### 3.3 Lipid cold split

The mirror question: every protein stays in training and a whole chemical family of lipids leaves
it (`--lipid_coldsplit=<set>`). This is the question that matters when the screening panel grows
rather than the protein list — a lipid of a chemistry never seen arrives, which of the known
proteins bind it.

Four sets are defined (`LIPID_COLDSPLIT_SETS` in [dataloader/sampler.py](../dataloader/sampler.py)),
grouped by chemistry rather than by count, because a set is only cold if its close relatives leave
with it. Isolation is measured on the compact Tanimoto matrix as the mean over the set's structures
of the highest similarity to anything left in training:

| set | isolation | positives held out | content |
|---|---|---|---|
| `sphingolipids` | 0.458 | 85 (11.2 %) | sphingoid backbone, all of it |
| `phosphorus_free` | 0.553 | 61 (8.1 %) | neutral glycerolipids, free fatty acids, retinol |
| `choline` | 0.653 | 258 (34.1 %) | phosphocholine head, di- and lyso- |
| `anionic` | 0.766 | 228 (30.2 %) | anionic glycerophospholipid heads |

The first three are genuinely isolated. `anionic` is not and cannot be: PA, PI, PS, PG and their
relatives differ from the phosphatidylcholines that stay behind only in the head group, while a
fingerprint sees mostly the two acyl chains. It is kept as the hardest of the four precisely
because it asks whether the model reads the head group at all.

Every protein stays in training, so the protein marginal would be free here — except that
`--balanced_proteins` has already zeroed it by construction (§4.1).

### 3.4 Double cold split (the current default)

`--double_coldsplit` cuts both axes at once: a protein family leaves training **and** a set of
head-group classes leaves training **for every protein**, not only for the held-out family. A row
of the held-out family in a held-out class then has neither its protein nor its lipid class
anywhere in training, so there is nothing from which a per-lipid prior could be estimated.

**The class set is derived, not typed in.** Positives of a family sit in that family's own classes
(START in phosphatidylcholines, GLTP in sphingolipids), so any fixed partition is arbitrary for
whichever family is held out. `lipid_classes_for_holdout` scores each class by concentration,

```
score(class) = positives of the held-out family in the class / (positives of everyone else there + 1)
```

and takes classes in decreasing score until the covered share of the family's positives reaches
`--coldsplit_share` (default 0.7). The numerator is what the held-out block gains, the denominator
is what training loses, so what leaves is what the family owns. The chosen list is printed at load
time so the run log records it. Several held-out families take the union of their sets.

**Held-out-family rows in classes that stayed in training are dropped, not evaluated.** They
cannot go to training (their protein is out), and in evaluation they would be the only rows where
a lipid prior can still score. `--mixed_coldsplit` is the other answer to the same question: it
keeps them, giving a larger evaluation block at the cost of 6–39 % of its lipids being ones
training has seen (prior 0.498 rather than exactly 0.500).

`--coldsplit_share` is not cosmetic. At small values the selection stops at cheap classes and the
block ends up mostly familiar lipids — the split *looks* two-sided without being one. Sweeping
share over three seeds, the criterion being that both prior substitutions stay within 0.5 ± 0.03,
0.7 is the smallest value at which all seven runnable families pass (at 0.3 lipocalin still scores
0.618). A single value for all families is preferred to a per-family minimum: tuning share by the
same check that later validates the split would be fitting the split to its own criterion.

What this produces (share 0.7, `--negatives_per_positive=2`, `--balanced_proteins`):

| family | classes held out | positives in block | cost to train (positives) | train | valid | test | dropped |
|---|---|---|---|---|---|---|---|
| CRAL-TRIO | 6 | 157 | 127 | 1242 | 280 | 281 | 7 % |
| GLTP | 3 | 66 | **1** | 2011 | 67 | 67 | 2 % |
| IP_trans | 3 | 51 | 238 | 1359 | 356 | 357 | 2 % |
| LBP_BPI_CETP | 3 | 47 | 222 | 1437 | 322 | 323 | 1 % |
| lipocalin | 15 | 72 | 259 | 1212 | 422 | 423 | 3 % |
| scp2 | 9 | 36 | 175 | 1597 | 302 | 301 | 1 % |
| START | 4 | 142 | 138 | 1231 | 345 | 345 | 8 % |

ML and OSBP are not run: 10 and 8 positives in the whole family, no test block can be assembled at
any share. The positive share of train comes out at 0.333–0.342 for all seven — by construction,
not approximately, because negatives are matched per positive within each side of the split.

Two properties of this split to keep in mind when reading per-family numbers:

- **GLTP costs training one positive.** Its sphingolipids are taken by nobody else, so the model
  arrives at the GLTP block never having seen a positive sphingolipid. Its evaluation blocks are
  also the smallest (67 rows), because the classes it removes bring almost no other protein's rows
  with them.
- **Some proteins are absent from training but present in evaluation.** Those whose positives all
  lay in the held-out classes have nothing left to contribute (the sampler skips a protein with
  zero positives), yet their rows in the held-out classes form part of the lipid-cold block. For
  lipocalin that is 4 proteins out of 25.

**Ordering, not weighting, is what keeps the split balanced.** Removing classes cuts *across*
proteins: a protein whose positives sat in a removed class loses almost all its positives and
almost none of its negatives. Sampling negatives globally and then cutting produced proteins at
4 positives against 91 negatives, and proteins left in training with a single label value — which
no weight can repair, since the missing side has no rows to carry weight. The sampler therefore
receives a "class is held out" indicator and matches negatives per positive **within each side of
the coming split** (`_sample_group_balanced_negatives`, grouping by (protein, side)). After that,
zero one-sided proteins remain in any of the seven families and no row is discarded.

### 3.5 What each split guarantees

Prior baseline on test and coverage, seven families, three seeds
([preprocessing/lipid_marginal_baseline.py](../preprocessing/lipid_marginal_baseline.py)):

| split | prior baseline (test) | test lipids seen in train |
|---|---|---|
| protein cold split | 0.562 | 98.5 % |
| `--mixed_coldsplit` | 0.510 | 12 % |
| **`--double_coldsplit`** | **0.500** | **0 %** |
| **`--lipid_coldsplit`** | **0.500** | **0 %** |

---

## 4. Marginals and the reference point

This section defines what is being subtracted from every number in §8, and how it is computed.

### 4.1 Which marginal survives which treatment

A marginal here is a predictor that uses one axis only: P(label | lipid) or P(label | protein).
The share of label variance each factor explains (η², with the floor that random labels with the
same number of groups would give in brackets):

| factor | raw table | working pool under `--balanced_proteins` |
|---|---|---|
| protein | 0.095 (0.003) | **0.000** (0.023) |
| family | 0.040 (0.001) | **0.000** (0.005) |
| lipid species | 0.062 (0.028) | 0.294 (0.206) |
| lipid class | 0.020 (0.003) | 0.109 (0.023) |

Matching negatives per positive inside each protein zeroes the protein main effect by
construction — that is what the sampler is for. (The η² column was measured at ratio 1; ratio 2
keeps the property and only shifts the common ratio: the measured positive share per protein in
train is 0.500–0.605 across the seven splits, against a target of 0.500.) Nothing touches the lipid main effect, which is left as the only
working marginal in the data. `--balanced_lipid_classes` zeroes the class effect (class baseline
0.498) but raises the species prior to 0.614: within a class individual species stay skewed, and
the shortcut simply moves one level down. It is a trade, not a fix.

So: **the protein marginal is removed by the sampler, the lipid marginal is removed by the split.**
Under the double cold split both are gone, which is the point of it.

This also explains an effect that looked like a bug for a long time: ablating the protein branch on
a held-out family often *improved* the metric. With the protein marginal zeroed there is nothing to
extract from the protein except the interaction term; the training optimum is "answer by the lipid
prior", and any dependence on the protein is a deviation from it that pays off on training proteins
(by memorizing which protein it is) and cannot pay off on a new family.

### 4.2 The prior baseline: measuring the leak

The predictor is deliberately trivial: *the fraction of positives this lipid has in training is
above 0.5*. No chemistry, no protein — a `groupby` and a threshold. It is computed at both
granularities (lipid species, head-group class) by `_report_lipid_prior_baseline` and printed in
every run's log, right after the split sizes:

```
train : (1231, 12)
valid : (345, 12)
test  : (345, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test  : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
```

A split is only considered built once this reads 0.500 with 0 % coverage. The same code, run across
families, seeds and samplers, produces the comparison table of §3.5
([preprocessing/lipid_marginal_baseline.py](../preprocessing/lipid_marginal_baseline.py)).

### 4.3 What the split does not close: chemical neighbourhood

Closing the *lookup* does not close *extrapolation by chemistry*: a lipid never seen can still
resemble one that was, and "resembles a training positive" is again a prediction that needs no
protein. Proximity is measured as, for each positive row of the block, the highest Tanimoto
similarity (Morgan fingerprints, the same `data/Tanimoto_compact_isomeric_*` artifacts the loader
uses for `--tanimoto_weight`) to any lipid that is positive anywhere in training, averaged over the
block — computed on exactly the rows the model sees, not on the full table.

Across the seven families this proximity correlates with the model's validation sensitivity at
**r = +0.935** (n = 7; the significance bar at that n is |r| > 0.75, and this is the only family
characteristic that clears it — six others, including the number of proteins, the number of classes
and ESM3-neighbour agreement, do not). The table is in §8.4, since those sensitivities are the base
configuration's own.

The reading is not "the model is well calibrated where chemistry is close". It is that where the
held-out chemistry is isolated, the model has no example of a positive molecule of that type and
answers negative to everything; the threshold has nothing behind it to move.

### 4.4 The chemistry null model, and why AUC

Proximity explains whether the model calls anything positive; it does not say how well it *ranks*.
For ranking the reference is an explicit null model
([analysis/null_model.py](../analysis/null_model.py)):

> For a row (protein *p*, lipid *l*) it **ignores *p* entirely** and scores *l* by the
> similarity-weighted training positive rate of its *k* nearest training lipids, nearest by Morgan
> fingerprint Tanimoto (k = 15).

Under the double cold split no row of the block's classes is in training, so every neighbour is
necessarily from another class: this is extrapolation across chemistry, not the class lookup the
split already closed.

It is reported as **AUC, not balanced accuracy**. At a threshold fitted on training the same null
model scores BA 0.512 while ranking the block at AUC 0.565: nearly all of its apparent weakness is
threshold placement. Comparing a network to it at a fixed 0.5 threshold would credit the network
for a decision boundary rather than for information.

Networks do not write per-row scores during a run, so they are recovered afterwards:
[analysis/checkpoint_scores.py](../analysis/checkpoint_scores.py) rebuilds the configuration from
the run's argument file, reproduces the split (the loader is deterministic given the seed, so the
rows come back identical), loads the weights saved by `--save_model_in_dynamics`, and writes the
class-1 probability for every row. Verified: the reconstructed scp2/seed 0/epoch 120 reproduces the
logged validation balanced accuracy as 0.6090891361, digit for digit.

Two AUCs are then computed on those rows, and they answer different questions:

- **pooled AUC** — over all pairs of the block, including pairs from different proteins. Since
  cross-protein pairs outnumber within-protein pairs by an order of magnitude, this mostly answers
  "does this lipid bind anything at all", which is the marginal question the null model was built
  to answer.
- **within-protein AUC** (`per_protein_auc`) — the same quantity computed inside each protein and
  averaged over proteins. Here the protein marginal cannot help either side.

### 4.5 The increment: what the network adds on top of chemistry

Neither AUC alone answers "does the network carry anything the chemistry score does not already
say". That needs a regression ([analysis/interaction_increment.py](../analysis/interaction_increment.py)):

1. Logistic regression of the label on the **standardised chemistry score** alone;
2. then on **chemistry plus the network score**;
3. both fitted **on the held-out block itself** and compared by AUC. The increment is the
   difference.
4. A third variant adds **one intercept per protein**, so that a(p) is absorbed and only the pair
   term can move the fit — the within-protein reading of the same regression.

Fitting on the block being scored is deliberate and its direction is known: it is an **upper
bound**. A network that cannot beat chemistry even with a coefficient fitted on the answers has
nothing to contribute, and the optimistic direction of the bias is what makes that conclusion safe
to draw. (Solver: plain gradient descent over a few columns and a few hundred rows; the fit is only
ever read as an AUC, never as a coefficient to interpret.)

### 4.6 Reporting rule

Every number from training is reported next to the baseline for the **same family and the same
seed**, and only the difference is discussed. Since the move to `--double_coldsplit` that baseline
is 0.500, so absolute balanced accuracies can be read directly again — but the reference point for
*ranking* is no longer 0.5 either, it is the chemistry null model of §4.4, and the comparison must
be made by AUC.

A second rule follows from §8.3: **never average across families**. 0.53 does not exist as a
property of the model; it is a mixture of ~0.59 on three families and ~0.47 on four, and a change
evaluated on the mean is evaluated wrongly.

One command produces all three readings for one label:

```bash
python3 analysis/full_label_report.py --label <label> --split valid
```

---

## 5. What the representations can and cannot carry

These are measurements of the **inputs**, made outside training, and they bound what any
architecture on top of them can achieve. They are reported here rather than among the results
because they do not depend on a training configuration.

The test used throughout is the same one: predict the **binding profile** of a held-out object
(the vector of its labels over lipids/classes) from its neighbours in a representation, and score
it by cosine with the truth. Two reference points bracket every number: *ignore the protein
entirely* (predict the training mean profile) and *three nearest neighbours by mean-pooled ESM3*.

### 5.1 The protein embedding

Geometry of the representation the model actually receives (mean-pooled ESM3, 595 protein pairs):

| | median | range |
|---|---|---|
| ESM3 cosine between two proteins | **0.974** | 0.905 … 1.000 |
| cosine between their binding profiles | **0.000** | 0.000 … 1.000 |

All 35 proteins sit in one point while their behaviour is maximally different; the correlation
between the two similarities is +0.227.

Profile prediction (cosine with truth):

| | one protein held out | one family held out |
|---|---|---|
| ignore the protein (training mean) | 0.259 | **0.169** |
| three nearest by ESM3 | **0.335** | **0.190** |

The model works in the second regime. There, knowing which protein it is adds 0.169 → 0.190, and
for four families out of seven the ESM3 neighbours are *worse* than ignoring the protein
altogether. That is the ceiling the protein branch operates under — before any question about
architecture.

Two further measurements, both negative:

- **Pocket-only pooling of ESM3** (mean over pocket residues instead of the chain) *lowers* the
  correlation with the profile: +0.192 against +0.227.
- **Centring and whitening** the embeddings widens the cosine range but adds no information
  (0.227 → 0.201); the first linear layer can already do this.

A side observation from §8: compressing the PLM projection hard did not prevent the protein branch
from encoding protein identity — it made that encoding *cleaner* (between-protein variance
0.866 → 0.980). The identity of a few dozen objects fits in one real dimension; a branch with nothing else to
encode will encode it whatever its width.

### 5.2 Structure-derived descriptors of the cavity

Several ways of reducing the cavity to numbers were measured against the same references. None
reached ESM3, and most did not reach "ignore the protein":

| representation | profile prediction (one protein held out) | correlation with profile |
|---|---|---|
| ESM3, mean over chain | **0.335** | **+0.227** |
| ESM3, mean over pocket | — | +0.192 |
| 13 cavity descriptors | 0.284 | +0.094 |
| 4 cavity shape numbers | 0.228 | −0.029 |
| ESM3 PCA5 + 13 descriptors | 0.291 | — |
| ignore the protein | 0.259 | — |

Adding descriptors to ESM3 makes it worse than ESM3 alone.

A further attempt was different in kind and worth reporting separately, because the literature on
pocket comparison is about **pairwise geometric matching**, not about summarising one pocket in a
few numbers. Implemented in the spirit of PocketMatch (Yeturu & Chandra, 2008) and measured in
[analysis/pocket_shape_similarity.py](../analysis/pocket_shape_similarity.py): a pocket is
described by the sorted list of all pairwise distances between its side-chain atoms, re-expressed
as 50 quantiles so that pockets with different atom counts (38 to 141 here) become comparable; the
distance between two pockets is the L2 distance between their quantile profiles. Sorting removes
the need for structural alignment, the list is rotation- and translation-invariant by construction
(verified to 1e-8 on a synthetic point cloud), and the ångström scale is deliberately not
normalised, since absolute size is what decides whether an acyl chain fits.

At k = 3, the same k as the ESM3 reference, pocket shape gives **0.144** — worse than ESM3 (0.190)
and worse than ignoring the protein (0.169), beating the latter on 2 families out of 7. Other k
values move it more than the difference from the baselines does (k = 1: 0.202; k = 5: 0.218; 100
quantiles at k = 3: 0.140). With seven families and 2–10 proteins each, neighbour selection is a
very small sample; this is not "works at a lucky k", it is a measure the data cannot support.

**Consequence.** With 35 proteins, no change of *protein representation* can be expected to produce
a significant result, and further work on the pocket description (atom chemistry as well as
geometry, a learned rather than heuristic descriptor) is not worth starting before the protein axis
itself is larger. That is a data problem, and the candidate external sources (BioDolphin,
SwissLipids) are discussed in [marginals_and_cold_split.md](marginals_and_cold_split.md) §11.3.

### 5.3 The lipid side

The lipid axis is the larger one (312 species, 34 classes) and the representations are stronger,
but two limits are structural:

- **Fingerprints and language models both read mostly the acyl chains.** This is why the `anionic`
  cold-split set cannot be isolated beyond 0.766 (§3.3): its members differ from the
  phosphatidylcholines that stay in training essentially in the head group only. Splitting it
  further makes it worse, not better (PG+LPG+PGP alone: 0.872; BMP+cardiolipin alone: 0.946).
- **The chemistry itself is uncertain.** The measurement fixes the head group and the total mass,
  not the chain composition (§2.6), so each row's SMILES is a plausible representative rather than
  the molecule that was measured. The candidate lists are carried through the pipeline, but the
  base configuration collapses them to one candidate per row.

### 5.4 What this bounds

Combining §5.1–5.3: the protein axis carries little transferable information at this sample size,
the lipid axis carries a real chemical signal that a fingerprint-nearest-neighbour predictor
already extracts, and the pair term — the object of the project — has to be demonstrated *above*
that chemical predictor, per family, by AUC. That is exactly the measurement of §8.5.

---

## 6. Architecture of the base model

Parameter values are deliberately absent here; they are given with the configuration in §8.1.

```
protein graph ─► Protein_encoder ─┐
                                  ├─► CrossAttention ─► pooling ─► Final_Layer ─► [batch, 2] logits
lipid tokens  ─► Lipid_encoder  ──┘
```

Both partners are `torch_geometric.data.Data` objects, so a batch is a block-diagonal union of
graphs and every attention site is restricted to nodes of the same sample. Boolean attention masks
are `[query_nodes, key_nodes]` with `True` meaning "forbidden pair"; `prot_batch` and `lip_batch`
identify the sample a node belongs to.

### 6.1 Protein track

`Protein_encoder` ([architecture/protein_encoder.py](../architecture/protein_encoder.py)) builds
one vector per residue:

1. **Input assembly.** The three node features (§2.4) are concatenated with the ESM3 embedding
   compressed by a learned linear projection, and with the per-residue buriedness. So the PLM,
   the local geometry and the burial all enter at the same point and share one representation.
2. **Graph convolution.** A GATv2 layer over the Voronoi contact graph, with the three edge
   features as edge attributes and self-loops added; multi-head, the heads concatenated. The code
   also contains a second convolution, but under the current default (`single_gat_layer`) it is
   not built at all rather than built and skipped — an allocated but unreachable module would
   still count toward the parameter total that names run directories and identifies past runs.
3. **MLP.** Expand–activate–project back to the working width, with dropout.
4. **Self-attention.** Multi-head self-attention over the residues of the same protein, in a
   post-norm residual block (attention → add → norm → feed-forward → add → norm). Its keys carry a
   **learnable additive bias on pocket residues**: the default protein mode does not remove
   non-pocket residues, it makes pocket residues preferentially attended, and the same bias is
   applied in the direction of cross-attention where the lipid queries the protein. Two stricter
   modes exist — hard restriction of attention to pocket nodes, and pooling over pocket nodes only.
5. **Optional post-attention MLP**, disabled in the base configuration.

### 6.2 Lipid track

`Lipid_encoder` ([architecture/lipid_encoder.py](../architecture/lipid_encoder.py)) is deliberately
thin, because the MoLFormer embedding is already a trained representation: a linear projection of
each token to the working width, then multi-head self-attention over the tokens of the same
molecule, then an optional post-attention MLP (disabled in the base configuration).

On the earlier draft's question — *why call it a graph if neither the feed-forward nor the
self-attention uses edges*: they do not, and the object is a `Data` only for batching. The complete
edge index that used to be built over the 768 embedding columns was removed once it was established
that nothing read it (it cost 77 of the 89.5 ms spent per sample and 76 MB of worker transfer per
batch). Real lipid edges exist only on the atom/bond graph path (`--lipid_graph_isomers`), where a
GATv2 stack with bond features replaces the linear projection.

The chemical ambiguity of the input (§2.6) is handled at this boundary: the candidate SMILES of one
measured species can be concatenated along the token axis, drawn from at random per access, or
concatenated with a per-token fragment id that further restricts attention. The base configuration
takes the first candidate only.

### 6.3 Cross-attention

`CrossAttention` ([architecture/cross_attention.py](../architecture/cross_attention.py)) is one
symmetric block with two multi-head attentions:

- lipid tokens as queries over protein residues as keys/values (`[N_lipid, N_protein]`);
- protein residues as queries over lipid tokens (`[N_protein, N_lipid]`).

Each side then goes through the same post-norm residual pattern as the self-attention blocks:
add the attention output, LayerNorm, feed-forward, add, LayerNorm. Both directions are restricted
to the same sample, and the direction in which the lipid queries the protein carries the same
learnable pocket key bias as the protein self-attention (§6.1).

The design comes from a multimodal antibody–antigen interaction model, which uses a combination of
cross- and self-attention to build a joint representation. `--double_attention` runs the block
twice with a second pair of encoders in between; it is not part of the base configuration.

### 6.4 Pooling and classifier

`Final_Layer` ([architecture/final_layer.py](../architecture/final_layer.py)) reduces each partner
to one vector per sample and decides:

- **Pooling** is generalised-mean (GeM) with a learnable, sign-preserving exponent, initialised at
  mean pooling and free to move toward max-like behaviour, so the choice between mean and max is
  not fixed in advance. Max, sum, add_max, learned-query attention pooling and sliced-Wasserstein
  pooling are the alternatives.
- **Fusion** is concatenation of the two pooled vectors (a bilinear alternative exists, which
  forces the decision to be multiplicative in both partners).
- **Classifier**: an MLP over the fused vector ending in **two logits**, so the output is
  `[batch, 2]` aligned one-to-one with the labels.

The layer also hosts the diagnostic machinery used in §8: `--lipid_only` and `--protein_only` zero
one pooled partner before the classifier (and disable cross-attention), and two independent
gradient-reversal heads exist — a per-partner anti-shortcut adversary reading each partner *before*
cross-attention, and a family DANN reading the fused vector after it. All are off in the base
configuration.

### 6.5 Attention implementation

`--fast_attention` computes the same three attention sites on a dense `(graphs, max_nodes, dim)`
layout instead of masking an `N × N` matrix over the whole batch. On a real batch of 16 the masked
form builds 18.84 M logits of which 2.09 M are within a graph — a 9× waste that grows quadratically
with batch size. The projections come from the same modules, so parameters and state dicts are
unchanged; only the order of arithmetic differs, which matches the default path to ~6e-08 absolute
rather than bitwise. That is why it is a flag and not a replacement.

---

## 7. Training

**Loss.** The task is binary and the head emits two logits, so the loss is cross-entropy over two
classes. Class weights are on by default, computed from the training counts as
`N / (2 · n_class)`, which brings the gradient mass of each class to 1.000. With
`--negatives_per_positive=2` the training pool is ~33 % positive, and because the negatives are
matched per positive inside each protein, one global class weight also balances every protein
individually (measured 0.972–1.061 against a target of 1.0) — no separate between-protein weight is
needed. Alternatives implemented and not used in the base configuration: focal loss, logit
adjustment, non-negative PU learning, a Tanimoto-similarity sample weight, a graph-regularised
loss over pairs of training rows (GRAB), and a pairwise ranking (RankNet-style) loss that optimises
pooled AUC directly.

**Optimiser.** Adam, constant learning rate (warmup + cosine and SWA exist behind flags),
weight decay passed to Adam. Batches are drawn by a class-balanced batch sampler
(`--balanced_batches`): every row is seen once per epoch, each class split into the same number of
chunks, so at ratio 2 the batches inherit the pool proportion rather than being forced to 1:1, and
the printed `balanced batches :` line records the actual composition.

**Seeding.** `seed_everything` runs before the model and the DataLoaders are built; train,
validation and test loaders keep independent generators and each worker derives a reproducible
Python/NumPy seed. This reproduces CPU-side sampling, splitting and loader order exactly; it does
not by itself make CUDA execution bitwise identical. `num_workers` is not a free knob — changing it
shifts the shuffle stream and moves the metrics from the second epoch onward.

**Epoch loop and checkpointing.** Metrics are computed every epoch on train and validation. The
kept checkpoint is the one maximising a **rolling mean of validation balanced accuracy** over a
window of epochs, not the single best epoch; early stopping is disabled by default so a run is
scored on its whole curve. The test block is evaluated with the restored checkpoint.

That checkpoint rule is itself a measured source of optimism and must be reported with the result.
Measured on the 14 double-cold-split runs of the 1 014 406-parameter configuration: the epoch of the
validation maximum is scattered uniformly over the whole schedule (2, 4, 4, 4, 7, 12, 18, 28, 38,
39, 63, 76, 76, 99), while validation does not improve over training (epochs 1–30 average 0.534,
epochs 91–120 average 0.529). The maximum is therefore mostly the argmax of noise, and the premium
it buys scales with how much a model varies its output — +0.011 for a constant predictor, +0.032
for the lipid half alone, +0.083 for the full model — which is larger than the entire excess over
the baseline. For the base configuration of §8 the same premium is +0.05. This is why §8 reports
the mean over the last epochs alongside the checkpointed number.

**Reproducibility of the run record.** Per-epoch training state (adversary reversal strengths and
similar) lives on the model, never on the config object: the run report dumps `vars(conf)`, so
anything written there would be recorded as a hyperparameter of the whole run. Adversary penalties
are excluded from the logged task loss and logged as their own scalars, so `epoch/train loss` stays
comparable across configurations.

---

## 8. Base configuration and its results

The configuration below is the current reference point: the smallest model that still contains
every block of §6, run on the double cold split. Every other configuration is compared against it
one flag at a time, and their results are not reported here.

### 8.1 The configuration

The run label is also the name of its argument file
([scripts/arg_files/bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120.md](../scripts/arg_files/bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120.md))
and of every output directory it produces (`run/<label>/`, `test_metrics/<label>/`,
`graphics/<label>/`). Read left to right:

| token | meaning |
|---|---|
| `bbp` | balanced batches + balanced proteins |
| `dcs` | double cold split |
| `smd` | save model in dynamics (milestone checkpoints) |
| `fa` | fast attention |
| `nps` | no post-self-attention MLPs, on both tracks |
| `dpt01` | dropout 0.1 |
| `gm` | GeM pooling |
| `plm8` | PLM compression dimension 8 |
| `hid8` | hidden width 8 |
| `wd001` | weight decay 0.01 |
| `ep120` | 120 epochs |

Set explicitly:

| flag | value | what it decides |
|---|---|---|
| `--double_coldsplit` | on | split of §3.4; class set derived per family, `--coldsplit_share` at its default 0.7 |
| `--balanced_proteins` | on | negatives matched per positive within each protein and each side of the split |
| `--balanced_batches` | on | class-balanced batch sampler |
| `--hiddim` | 8 | working width of both encoders, cross-attention and fusion |
| `--plm_compression_dim` | 8 | width the 1536-d ESM3 vector is projected to before concatenation |
| `--dropout` | 0.1 | encoder and cross-attention MLPs (final MLP inherits 0.1) |
| `--weight_decay` | 0.01 | Adam, three orders above the 1e-5 default |
| `--pool_type` | `gem` | generalised-mean pooling with learnable exponent |
| `--protein_disable_post_sa_mlp`, `--lipid_disable_post_sa_mlp` | on | the MLPs after each self-attention block are removed |
| `--fast_attention` | on | dense block-diagonal attention, same parameters |
| `--ep` | 120 | epochs |
| `--save_model_in_dynamics` | on | weights kept at epochs 1, 10, 49, 51, 120 for the per-row score probes of §4.4 |

Inherited from the defaults: learning rate 1e-4, batch 16, Adam, cross-entropy with class weights,
`--negatives_per_positive=2`, 8 attention heads, MLP expansion factor 4, a single GATv2 layer,
protein and lipid self-attention on, cross-attention on (single block), the learnable pocket key
bias on, LeakyReLU, first-candidate-only lipid SMILES, checkpoint by the rolling validation mean
over a 5-epoch window, early stopping disabled.

Scale and cost:

| | |
|---|---|
| trainable parameters | **27 286** |
| runs | 7 families × 2 seeds = 14 |
| hardware | one Tesla V100-SXM2-32GB (Bigfoot) per run |
| time per epoch | 6.0 s on average (5.3–8.1 across families) |
| time per run | ~12 min (10.6–16.2) |

The size is the point of this configuration. The predecessor at 1 014 406 parameters had ~2400
parameters per positive training row, and the hypothesis was that memorisation was drowning a real
signal. This model is 37× smaller, and it did reduce memorisation (training balanced accuracy ~0.87
against ~0.94, validation loss nearly flat instead of tripling) — §8.6 reports what that bought
and what it did not.

### 8.2 The blocks being evaluated

Split sizes, held-out classes and the cost to training are the per-family table of §3.4. Two
properties of that table matter for reading the results: GLTP is evaluated on 67 rows and arrives
without a single positive sphingolipid in training, and each family's block contains a few proteins
that were absent from training entirely.

### 8.3 Decision metrics

Test block, checkpointed model, mean of the two seeds. The prior baseline is exactly 0.500 on every
one of these blocks, verified in each run's log.

| family | group | test BA | sensitivity | specificity | validation BA, last 10 epochs | train BA, final epoch |
|---|---|---|---|---|---|---|
| LBP_BPI_CETP | above chance on validation | 0.636 | 0.417 | 0.855 | **0.599** | 0.865 |
| scp2 | above chance on validation | 0.560 | 0.441 | 0.678 | **0.595** | 0.928 |
| IP_trans | above chance on validation | 0.581 | 0.557 | 0.606 | **0.563** | 0.855 |
| CRAL-TRIO | at chance | 0.569 | 0.578 | 0.560 | 0.503 | 0.919 |
| GLTP | at chance | 0.523 | 0.061 | 0.985 | 0.503 | 0.859 |
| START | at chance | 0.524 | 0.149 | 0.898 | 0.468 | 0.841 |
| lipocalin | at chance | 0.524 | 0.439 | 0.609 | 0.464 | 0.868 |
| **all seven** | | **0.560** | 0.377 | 0.742 | 0.528 | 0.876 |

The grouping in the second column is defined on **validation**, where the sign is consistent across
both seeds of every family, not on the test column: CRAL-TRIO's test balanced accuracy sits with
the first three while its validation lies at chance, which is what a test block of 281 rows scored
by a checkpoint chosen on noise looks like. Every ranking measurement below (§8.5) separates the
same two groups far more sharply than these decision metrics do.

Summary quantities over the 14 runs:

| | |
|---|---|
| validation BA, mean of last 10 epochs | 0.528 |
| validation BA at the kept checkpoint | 0.578 (premium over the last-10 mean: **+0.050**) |
| best single validation epoch | 0.596 |
| train − validation gap, mean over epochs | 0.292 |
| final validation loss, the three families above | 0.86 |
| final validation loss, the other four | 1.63 |

The split by family is the most stable structure in these results and it must not be averaged away.
Both seeds agree on it without exception: LBP_BPI_CETP, scp2 and IP_trans end above 0.55 validation
balanced accuracy in each of their two runs (0.591/0.607, 0.605/0.584, 0.568/0.557), the other four
below 0.52 in each (0.487/0.519, 0.489/0.518, 0.473/0.462, 0.468/0.460). The 0.560 test average is
a mixture of 0.592 on the first three and 0.535 on the other four, and the same split shows in the
validation loss above and, far more sharply, in the ranking measurements below.

Each run also writes a per-protein breakdown of the test block (`test_metrics/<label>/<group>/…`),
which is where the degenerate cases are visible individually — e.g. within the scp2 block, PITPNB
predicts no positive at all while RLBP1 predicts almost everything positive.

### 8.4 Sensitivity is set by chemical distance, not by calibration

Validation sensitivity, mean of the last 30 epochs over both seeds, next to the chemical proximity
of each held-out block to the training positives (§4.3):

| family | classes held out | proximity to train | validation sensitivity |
|---|---|---|---|
| GLTP | sphingomyelin, hexosyl ceramide, ceramide phosphate | 0.630 | **0.029** |
| START | ceramide, TAG, PC, LPC | 0.649 | **0.081** |
| lipocalin | fatty acids, retinol, lyso-lipids, PC | 0.693 | **0.018** |
| IP_trans | PA, PI, PC | 0.852 | 0.491 |
| LBP_BPI_CETP | PS, PI, PC | 0.856 | 0.456 |
| CRAL-TRIO | cardiolipin, PGP, DAG, PA, PE, PG | 0.901 | 0.455 |
| scp2 | lyso-lipids, TAG, BMP, PG, fatty acids | 0.956 | 0.451 |

**r = +0.935** (n = 7), and the separation is clean: below 0.70 proximity the sensitivity is ≤ 0.08,
above 0.85 it is ~0.45. This is not a threshold problem: the class weights bias the decision toward
positives if anything — on training, sensitivity exceeds specificity (0.967 against 0.907, measured
on the predecessor configuration) — and the collapse appears only on the isolated blocks. Where the
held-out chemistry has no relative among the training positives, the model has no example of a
positive molecule of that type, and moving the threshold finds nothing behind it.

### 8.5 Ranking against the chemistry null model

Validation block, epoch 120, both seeds, k = 15 neighbours, computed on exactly the rows the model
was scored on and matched by `pair_id`
([analysis/full_label_report.py](../analysis/full_label_report.py)). Pooled AUC:

| family | chemistry null model | this model |
|---|---|---|
| scp2 | 0.419 | **0.663** |
| IP_trans | 0.532 | **0.597** |
| LBP_BPI_CETP | 0.628 | 0.632 |
| GLTP | 0.525 | 0.503 |
| lipocalin | 0.594 | 0.494 |
| CRAL-TRIO | 0.616 | 0.497 |
| START | 0.641 | 0.411 |
| **the three families** | **0.526** | **0.631** |
| **the other four** | **0.594** | **0.476** |
| all seven | 0.565 | 0.542 |

On the test block the same picture: the three families 0.586 against 0.524 for chemistry, the other
four 0.495 against 0.591, all seven 0.534 against 0.562.

Pooled AUC mixes the marginal question with the pair question (§4.4), so the same comparison inside
each protein (155 protein-blocks over the 14 splits):

| | this model, pooled | this model, within protein | chemistry, pooled | chemistry, within protein |
|---|---|---|---|---|
| the three families | 0.629 | 0.575 | 0.538 | **0.594** |
| the other four | 0.476 | 0.521 | 0.593 | 0.580 |
| all seven | 0.542 | 0.544 | 0.569 | **0.586** |

And the increment of §4.5 — the upper bound on what the model adds on top of the chemistry score:

| | all seven | the three families | the other four | scp2 |
|---|---|---|---|---|
| increment, pooled | 0.051 | 0.084 | 0.027 | **0.116** |
| increment, within protein | 0.038 | 0.030 | 0.044 | **0.085** |

Learning curve of the ranking, from the milestone checkpoints:

| epoch | the three families | the other four |
|---|---|---|
| 1 | 0.530 | 0.504 |
| 10 | 0.582 | 0.572 |
| 49 | **0.634** | 0.528 |
| 51 | **0.634** | 0.520 |
| 120 | 0.630 | **0.476** |

### 8.6 Reading of the result

1. **The leak of the one-axis split is closed and stays closed.** All 14 runs print a prior baseline
   of exactly 0.500 with 0 % lipid coverage, so the balanced accuracies of §8.3 can be read against
   0.5 directly — unlike every result predating the two-axis split, which must be read against
   ~0.56.
2. **Two curves hide under one flat metric.** On LBP_BPI_CETP, IP_trans and scp2 the model does
   learn something over the run (pooled AUC 0.530 → 0.634 by epoch 49, then a plateau); on the other
   four it *un*-learns after epoch 10, down to 0.476, below chance. Balanced accuracy shows neither,
   because on those four it sits on the floor of the threshold the whole time.
3. **Most of the visible advantage on the working three is marginal.** Pooled, the model leads
   chemistry by +0.105 and the sign holds in all six runs; within protein, where neither side can
   use the lipid marginal, it *trails* chemistry by 0.019. Of the three, only **scp2** beats
   chemistry inside protein convincingly (0.581 against 0.453, and on test 0.586 against 0.423, both
   seeds in the same direction); IP_trans is level; LBP_BPI_CETP is chemistry — all predictors score
   ~0.63 there.
4. **The increment is positive almost everywhere but small**, concentrated on scp2, and it is an
   upper bound fitted on the answers. Within protein it grows to epoch 49–51 and falls back by 120
   — the same overfitting story as point 2, seen on a quantity with the marginal already removed.
5. **Compression fixed calibration, not the metric.** Against the 1 014 406-parameter predecessor,
   on matched families and seeds: train BA 0.871 vs 0.937; validation loss nearly flat (0.69 → 0.84
   on the three families, 0.71 → 1.59 on the other four) instead of rising to 2.00 and 3.68;
   checkpoint premium down from +0.083 to +0.05–0.067. Decision metrics did not move by a
   hundredth. Memorisation was real and is now largely gone; the signal it was supposed to be
   hiding was not there.
6. **What can be claimed.** In the setting "new protein family *and* new lipid chemistry", with 35
   proteins and 756 positives, this model ranks the held-out block **no better on average than a
   protein-blind nearest-lipid search** (0.542 against 0.565), winning on three families and losing
   on four; inside protein it wins convincingly on one family out of seven. What is *not* claimed:
   that the pair signal is absent (on scp2 it is present and reproducible across seeds), that the
   loader or the metric is wrong (both were audited), or that the task is unsolvable — only that at
   this sample size and under this split it is not solved.

---

## 9. Questions still open

Recorded here rather than answered, because the pipeline does not answer them:

- **Accuracy of the experimental labels.** How the binding events were detected and with what false
  negative rate is not derivable from the data we hold, yet it sets the ceiling on any metric — the
  negative class is an assumption (§2.8), not a measurement.
- **Stereochemistry in the lipid embedding.** The pipeline can carry isomeric SMILES and has an
  isomeric embedding table, but whether MoLFormer's representation actually distinguishes the
  stereoisomers we hand it has not been tested here.
- **Which negatives to use.** The complement-of-positives assumption is convenient and known to be
  biased; PU learning was implemented and did not raise balanced accuracy, and the right
  alternative is not established.
- **Whether a coarser target helps.** Predicting (protein, lipid *class*) instead of (protein,
  species) would rest each label on tens of measurements instead of one; it has not been run.
- **Whether the protein axis can be enlarged.** Every negative result of §5 is bounded by 35
  proteins. External sources (BioDolphin, SwissLipids) are the only way to change that, and their
  compatibility with this table has not yet been checked.

---

## References

- Titeca et al., *A system-wide analysis of lipid transfer proteins delineates lipid mobility in
  human cells*, 2023 — the interaction dataset.
- Olechnovič & Venclovas, *Voronota: a fast and reliable tool for computing the vertices of the
  Voronoi diagram of atomic balls*, J. Comput. Chem., 2014 — pockets and graphs.
- Hayes et al., *Simulating 500 million years of evolution with a language model* (ESM3), 2024 —
  protein embeddings.
- Ross et al., *Large-scale chemical language representations capture molecular structure and
  properties* (MoLFormer), 2022 — lipid embeddings.
- Conroy et al., *LIPID MAPS: update to databases and tools for the lipidomics community*, NAR,
  2023 — lipid structures.
- Yeturu & Chandra, *PocketMatch: a new algorithm to compare binding sites in protein structures*,
  BMC Bioinformatics, 2008 — the pocket-shape comparison of §5.2.
- Fey & Lenssen, *Fast graph representation learning with PyTorch Geometric*, 2019; Paszke et al.,
  *PyTorch*, 2019.

## Where the numbers come from

| quantity | script |
|---|---|
| prior baseline, in every run's log | `_report_lipid_prior_baseline`, [dataloader/Dataloader.py](../dataloader/Dataloader.py) |
| prior baseline across families, samplers and splits | [preprocessing/lipid_marginal_baseline.py](../preprocessing/lipid_marginal_baseline.py) |
| which classes a double cold split holds out, and its cost | [preprocessing/lipid_class_holdout.py](../preprocessing/lipid_class_holdout.py) |
| per-row scores of saved checkpoints | [analysis/checkpoint_scores.py](../analysis/checkpoint_scores.py) |
| chemical proximity, null model, AUC pooled and within protein | [analysis/null_model.py](../analysis/null_model.py) |
| increment of the network over chemistry | [analysis/interaction_increment.py](../analysis/interaction_increment.py) |
| all three of the above for one label, in one run | [analysis/full_label_report.py](../analysis/full_label_report.py) |
| pocket-shape similarity of §5.2 | [analysis/pocket_shape_similarity.py](../analysis/pocket_shape_similarity.py) |
| aggregated run metrics | `metrics_summary.csv`, built by [analysis/build_metrics_table.py](../analysis/build_metrics_table.py) |

Longer internal notes behind sections 3–5: [double_cold_split.md](double_cold_split.md) (how the
split is built), [marginals_and_cold_split.md](marginals_and_cold_split.md) (marginals, null model,
what is closed and what is not), [signal_state.md](signal_state.md) (what the model does and does
not learn).
