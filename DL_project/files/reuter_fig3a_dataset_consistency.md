# Reuter et al. Figure 3a vs. this project's interaction table

## Source and method

Reuter et al. (bioRxiv, `files/Reuter.pdf`, page 22), Figure 3a: a protein x
lipid-subclass matrix of MS-measured LTP-lipid interactions (in cellulo /
in vitro screens, HPTLC triangles, "novel complex" circles). The 35 proteins
in this project's dataset (`data/Processed_Negative_Interaction_Corrected_
Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv`, `LTPProtein`
column) are an exact subset of Reuter's 39-protein panel, and the 9
`ProteinDomain` family groups used by `--double_coldsplit`
(`dataloader/Dataloader.py:78`) match Reuter's family blocks column-for-
column (CRAL-TRIO 9, GLTP 2, IP_trans/PITP 3, START 3, LBP_BPI_CETP/BPI 2,
ML 1, lipocalin 10, scp2 3 -- all identical membership; only OSBP differs,
this dataset carries 2 of Reuter's 6 OSBP proteins: OSBPL9, OSBPL5).

The table below was extracted by rendering page 22 at 600 DPI and sampling
pixel colour at each cell's centre (grid geometry recovered from the
figure's own horizontal/vertical border lines: 29 rows at ~55.5 px pitch,
39 columns grouped into the 9 family blocks at the exact sizes above). A
cell is marked `X` if it carries any colour fill (in cellulo/in vitro
intensity, including HPTLC hatching) or a "novel complex" circle; blank
otherwise. Calibration was verified by cross-checking ~15 cells against
this project's own known positives (e.g. RLBP1/TTPAL PA+PC+PE+PG+CL,
PITPNA/PITPNB PC+PI+PG) -- every check matched before the table below was
trusted for the consistency check in the next section.

Lipid class codes match `dataloader/sampler.py`'s `LIPID_COLDSPLIT_SETS`
naming (PC, PC-O, PE, PE-O, LPC, LPE, LPE-O, LPG, PA, PI, PS, PG, PGP, BMP,
CL, DAG, TAG, FA, FAL, VA, Cer, CerP, HexCer, Hex2Cer, SHexCer, SM), plus
`PG/BMP`, Reuter's own row for MS-isobaric PG/BMP species that this
project's `Lipid` column also names literally as `PG/BMP(chain:unsat)`.

## Table: documented LTP -- lipid-subclass pairs (Reuter Fig 3a), this project's 35 proteins

#### CRAL-TRIO

| lipid class | SEC14L5 | SEC14L2 | SEC14L4 | SEC14L6 | TTPA | TTPAL | RLBP1 | ATCAY | BNIPL |
|---|---|---|---|---|---|---|---|---|---|
| Cer |  |  |  |  |  |  |  |  |  |
| CerP |  |  |  |  |  |  |  |  |  |
| HexCer |  |  |  |  |  |  |  |  |  |
| Hex2Cer |  |  |  |  |  |  |  |  |  |
| SHexCer |  |  |  |  |  |  |  |  |  |
| SM |  |  |  |  |  |  |  |  |  |
| FA |  |  | X |  |  | X | X |  |  |
| FAL |  |  |  |  |  |  |  |  |  |
| LPC |  |  |  |  |  | X |  |  |  |
| LPE | X |  |  |  |  | X |  |  |  |
| LPE-O |  |  |  |  |  |  |  |  |  |
| LPG |  |  |  |  |  | X |  |  |  |
| PA |  |  |  |  | X | X | X |  |  |
| PC |  |  |  | X |  | X | X | X |  |
| PC-O |  |  |  | X |  |  |  |  | X |
| PE | X |  |  | X |  | X | X |  |  |
| PE-O |  |  |  |  |  |  |  |  |  |
| PI |  | X |  |  |  |  |  |  |  |
| PIPs |  |  |  |  |  |  |  |  |  |
| PS |  |  |  |  |  |  |  |  |  |
| PGP |  |  |  |  |  |  | X |  |  |
| PG |  |  |  |  | X | X | X |  |  |
| PG/BMP |  |  |  |  | X | X | X |  |  |
| BMP |  |  |  |  |  |  |  |  |  |
| CL |  |  |  |  |  | X | X |  |  |
| DAG |  | X |  |  |  |  |  |  |  |
| TAG |  |  |  |  |  |  |  |  |  |
| VA |  |  |  |  |  |  |  |  |  |

#### GLTP

| lipid class | GLTP | GLTPD1 |
|---|---|---|
| Cer |  |  |
| CerP |  | X |
| HexCer | X |  |
| Hex2Cer | X |  |
| SHexCer | X |  |
| SM |  | X |
| FA | X |  |
| FAL | X |  |
| LPC |  |  |
| LPE | X |  |
| LPE-O | X |  |
| LPG | X |  |
| PA |  |  |
| PC |  |  |
| PC-O |  |  |
| PE |  |  |
| PE-O |  |  |
| PI |  |  |
| PIPs |  |  |
| PS |  |  |
| PGP |  |  |
| PG |  |  |
| PG/BMP |  | X |
| BMP |  |  |
| CL |  |  |
| DAG |  |  |
| TAG |  |  |
| VA |  |  |

#### IP_trans (PITP)

| lipid class | PITPNA | PITPNB | PITPNC1 |
|---|---|---|---|
| PA |  |  | X |
| PC | X | X |  |
| PI | X | X | X |
| PG |  | X |  |
| PG/BMP |  | X |  |

(all other lipid classes blank for this family)

#### START

| lipid class | STARD2 | STARD10 | STARD11 |
|---|---|---|---|
| Cer |  |  | X |
| PC | X | X | X |
| PC-O | X | X |  |
| PE |  | X |  |
| PE-O |  | X |  |
| PG |  | X |  |
| PG/BMP |  | X |  |
| TAG |  |  | X |

(all other lipid classes blank for this family)

#### OSBP (subset in dataset: 2 of Reuter's 6)

| lipid class | OSBPL9 | OSBPL5 |
|---|---|---|
| PE |  | X |
| PS | X |  |

(all other lipid classes blank for this family)

#### LBP_BPI_CETP (BPI)

| lipid class | BPIFB2 | BPI |
|---|---|---|
| PC | X | X |
| PC-O | X | X |
| PE |  | X |
| PI |  | X |
| PS |  | X |
| PG/BMP | X |  |
| BMP | X |  |

(all other lipid classes blank for this family)

#### ML

| lipid class | GM2A |
|---|---|
| PC | X |
| PC-O | X |
| PE | X |
| PI | X |
| PG/BMP | X |

(all other lipid classes blank for this family)

#### lipocalin

| lipid class | LCN1 | LCN15 | RBP4 | RBP1 | RBP5 | PMP2 | FABP1 | FABP7 | FABP5 | CRABP2 |
|---|---|---|---|---|---|---|---|---|---|---|
| SM | X |  |  |  |  |  |  |  |  |  |
| FA |  |  |  |  | X | X | X | X | X | X |
| LPC |  |  |  |  |  |  | X |  |  |  |
| LPE |  |  |  |  |  |  | X |  |  |  |
| LPG |  |  |  |  |  |  | X |  |  |  |
| PC | X |  |  |  |  |  |  |  |  |  |
| PC-O | X |  |  |  |  |  |  |  |  |  |
| PE |  |  |  |  |  |  | X |  |  |  |
| PG |  | X |  |  |  |  | X |  |  |  |
| PG/BMP |  | X |  |  |  |  |  |  |  |  |
| VA |  |  | X | X |  |  |  |  |  |  |

(all other lipid classes blank for this family)

#### scp2

| lipid class | SCP2D1 | HSDL2 | SCP2 |
|---|---|---|---|
| FA | X | X |  |
| LPC | X |  |  |
| LPE | X |  |  |
| LPG | X |  | X |
| PE | X |  | X |
| PG |  | X | X |
| PG/BMP | X |  | X |
| TAG |  | X |  |

(all other lipid classes blank for this family)

## Consistency check against the 634 positive pairs

`data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_
CandidatesCompleted_Deduplicated.csv` has 634 `Interaction==1` rows, which
collapse (species -> lipid class) to 104 unique (protein, lipid-class)
positive pairs. Every ambiguous `PG/BMP(...)`-named species was checked
against Reuter's own `PG/BMP` row, not the plain `PG` row (11 proteins have
`PG/BMP`-format positives -- BPIFB2, GLTPD1, GM2A, LCN15, PITPNB, RLBP1,
SCP2, SCP2D1, STARD10, TTPA, TTPAL -- and all 11 are exactly the 11 proteins
whose `PG/BMP` row Figure 3a marks, an exact set match with zero gaps
either direction).

The same ambiguity pattern shows up for ether species: this dataset names
isobaric PC-ether/lyso-PC and PE-ether/lyso-PE pairs literally as
`PC(O-n:m)/LPC(n:m)` and `PE(O-n:m)/LPE(n:m)`, and Reuter's row list keeps
`PC-O`/`LPC` and `PE-O`/`LPE` as separate rows (no merged row the way
`PG`/`BMP` has `PG/BMP`). An initial pass here checked only the `PC-O`/
`PE-O` side of each ambiguous species and flagged 5 pairs (7 rows: FABP1,
GLTP x2, SCP2D1 x2, TTPAL) as "positive here, blank in Figure 3a" --
**that pass was wrong**: re-checking the `LPC`/`LPE` alternative for the
same 5 (protein, class) pairs finds all 5 documented there instead:

| protein | class checked (blank) | alternative | Figure 3a |
|---|---|---|---|
| FABP1 | PC-O | LPC | X |
| GLTP | PE-O | LPE | X |
| SCP2D1 | PE-O | LPE | X |
| SCP2D1 | PC-O | LPC | X |
| TTPAL | PC-O | LPC | X |

So there are **zero** confirmed positive-but-undocumented pairs. Every one
of the 104 unique (protein, lipid-class) positive pairs in the 634-row
positive set is documented in Figure 3a once isobaric-ambiguous species are
checked against both of their candidate rows.

One soft residual: TTPAL and FABP1 each carry a `PC(O-18:1)/LPC(18:1)`
positive (bucketed as `PC-O` by this project's class extraction) plus five
further, unambiguous `LPC(18:2/20:4/22:5/18:0/18:1)` rows labelled negative.
Figure 3a's `LPC` mark for both proteins may be fully explained by that one
already-positive ambiguous species -- Reuter's screen does not obviously
imply the other five chain lengths must also bind -- so this is not treated
as a confirmed false negative, just a residue of the same isobaric
ambiguity, worth a literature spot-check but not an actionable label fix on
its own.

### Scope requested: lipid_coldsplit subclass vs. double_coldsplit

Moot after the correction above: with zero confirmed contradictions, none
fall inside a `--lipid_coldsplit` set (`sphingolipids`, `phosphorus_free`,
`choline`, `anionic` -- `dataloader/sampler.py:245`) or inside any
`--double_coldsplit` family-exclusion group. The one soft residual (TTPAL/
FABP1 `LPC`) would sit in the `choline` lipid_coldsplit block and in the
CRAL-TRIO/lipocalin double_coldsplit groups respectively if it were ever
promoted from "residue of an ambiguity" to a confirmed relabelling
candidate -- it is not, on the evidence gathered here.

### Bottom line

- The 634-positive table is consistent with Reuter Figure 3a: 104/104
  unique (protein, lipid-class) positive pairs are documented there once
  isobaric-ambiguous species (`PG/BMP`, `PC-O/LPC`, `PE-O/LPE`) are checked
  against both of their candidate rows instead of just one.
- No confirmed false positives, no confirmed false negatives. The only
  loose end is TTPAL/FABP1's five extra `LPC` chain-length variants, which
  read as an artifact of the same isobaric ambiguity rather than an
  independent labelling gap.
- This is a small-scale, manual figure-reading check (pixel classification
  of one figure page), not a systematic reannotation -- treat a "consistent"
  verdict as reassurance about this one figure, not as a full audit of
  `preprocessing/`'s positive/negative assignment against the whole Reuter
  supplement.

## The other direction: Figure 3a marks it, this table does not (2026-10-01)

Everything above checks one direction -- *is every positive here documented
there* -- and answers yes, 104/104 (128 unique (protein, class) cells on the
current table). The reverse direction was never written down, although the
artefact that encodes it has existed all along:
`data/fig3a_disputed_negative_pair_ids.csv`, 1159 rows, read by
`--relabel_fig3a_disputed_negatives` (`dataloader/Dataloader.py:159-190`).

**Correction 2026-10-01, second pass.** An earlier version of this section said these
are cells "where this table carries no positive at all". That was wrong, and it was an
unverified gloss rather than a measurement. Checked directly: **all 1159 rows sit in
cells where this table already records a positive of the same class** -- 1159 of 1159,
none in an empty cell. The dispute is therefore at the SPECIES level, not the cell
level.

The exact rule the artefact encodes, reproduced from the matrix above
(1159 of 1159 verified, see "How the rows are selected" below):

> a row is listed when it is labelled `Interaction=0`, its (protein, Figure-3a-row)
> cell carries a mark, and -- in practice -- that cell also already holds a positive of
> this table's own.

| | |
|---|---|
| distinct (protein, Figure-3a-row) cells | **81** |
| rows they cover | **1159**, all labelled `Interaction=0` |
| of those, in cells that already hold a positive | **1159 (all)** |
| share of the table's 9271 negatives | **12.5%** |
| proteins affected | 30 of 35 |
| Figure-3a rows affected | 15 |

What this means for how strongly the rows are "disputed": Figure 3a does **not**
contradict any of these labels. It records that the protein binds *something* in the
class, which this table also records. It says nothing about the particular chain length
on the listed row. So the set is best read as **negatives that are unverified inside a
class the protein demonstrably binds** -- the subpopulation most likely to contain
hidden positives -- and not as documented false negatives.

By protein family:

| family | cells | proteins | rows |
|---|---:|---:|---:|
| CRAL-TRIO | 10 | 8 | 383 |
| lipocalin | 9 | 8 | 179 |
| LBP_BPI_CETP | 5 | 2 | 133 |
| START | 6 | 3 | 124 |
| scp2 | 7 | 3 | 119 |
| ML | 4 | 1 | 96 |
| IP_trans | 4 | 3 | 88 |
| OSBP | 1 | 1 | 19 |
| GLTP | 3 | 1 | 18 |

By lipid subclass: PC 430 rows / 13 proteins, PC-O 188/8, PE 164/11, PG 130/9,
FA 96/12, LPC 34/3, LPE 28/5, PI 26/5, PA 18/4, SM 16/1, LPG 11/5, TAG 8/2.

Worst single proteins: GM2A 96 rows over 4 subclasses, TTPAL 92 over 9,
SEC14L6 84 over 3, BPI 79 over 5, RLBP1 67 over 5, LCN1 66 over 3,
STARD10 66 over 5, FABP1 60 over 6.

### Why this is not simply "1159 missing positives"

The asymmetry is explainable and is not evidence that the table is wrong.
Figure 3a's unit is a (protein, SUBCLASS) cell: one mark says the protein was
seen to bind *something* in that subclass. This table's unit is a (protein,
SPECIES) pair. A protein that binds `PC(34:1)` and nothing else in PC produces
one Figure 3a mark and, correctly, dozens of negative PC rows here. Promoting
every row of a marked cell to positive would assert something Figure 3a never
claims.

What the number does measure is **how much of the negative class is unverified
rather than verified**: 12.5% of negatives sit in cells where the article
documents binding, so their negativity rests on "this particular chain length
was not among the hits", not on "this protein does not bind this chemistry".

### How much of the measured metrics rests on them

Measured on `ge_s15_prothid32_hid64_noreg` (`--lipid_species_coldsplit=0.15`,
`--balanced_proteins`), pooled over the five standard seeds -- the sampler draws
negatives, so the share in the evaluated pool is not the table's 12.5%:

| split | rows | negatives | disputed | of negatives | of all rows |
|---|---:|---:|---:|---:|---:|
| train | 8058 | 5372 | 1088 | **20.3%** | 13.5% |
| valid | 724 | 482 | 102 | **21.2%** | 14.1% |
| test | 723 | 481 | 83 | **17.3%** | 11.5% |

So roughly **one negative in five**, on both sides of the split, is a row that sits in
a class the protein is documented to bind. That is the practically relevant figure:
specificity, F1 and the (protein, subclass) planka all read partly off labels
the source publication disputes, and the planka is affected in the same
direction as the model, since both are keyed on the same cells.

Nothing here is a reason to relabel: see the previous subsection for why the
cell-vs-species grain makes a blanket flip wrong. It is a reason to report
`--relabel_fig3a_disputed_negatives` as a sensitivity check alongside any
headline specificity number, which no run on the current table has done.

### How the rows are selected

No script in the repository builds `data/fig3a_disputed_negative_pair_ids.csv` -- it is
only ever read (`dataloader/Dataloader.py:159-190`, `training/read_configuration.py`).
The selection rule was therefore recovered by reproducing the file from the matrix in
this document, and it reproduces exactly:

1. **The matrix.** The 108 `X` marks of the table above, over 35 proteins and 27
   Figure-3a rows. (One of the 108 has no corresponding row in this table at all.)
2. **The class of a row.** Taken from the `Lipid` column, not `FullIdentityOfLipid`:
   the head before the parenthesis, with `(O-...)` promoting it to the ether row --
   `PC(O-34:1)` -> `PC-O`, not `PC`. A naive prefix gets 933 of the 1159 right and the
   other 226 wrong, so this step is load-bearing.
3. **Isobaric combined names contribute BOTH candidate rows.** `PC(O-30:0)/LPC(30:0)`
   is a candidate for `PC-O` and for `LPC`; `PG/BMP(34:1)` is a candidate for the
   single `PG/BMP` row. This is the same both-rows rule the consistency check above
   uses in the other direction.
4. **Keep the negatives whose (protein, candidate row) is marked.** That yields 1321
   rows.
5. **Drop the `PG/BMP` ones.** The 162 rows that 1321 has over 1159 are *all* of class
   `PG/BMP`, and all 162 sit in cells this table already satisfies with a
   `PG/BMP`-format positive of its own -- the exact 11-protein set match documented in
   the consistency check above. With the mark already accounted for, the remaining
   negatives of those cells were not listed.

Verified on the current table: every one of the 1159 `pair_id`s resolves to a row with
`Interaction == 0`, whose `LTPProtein` matches the file's own column, and whose
(protein, `fig3a_class`) pair carries a mark -- 1159 of 1159 on each check. `pair_id`
is the row position in
`Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv`,
the same `pair_id` convention the loader uses.

Two consequences worth stating:

- **The artefact is not regenerable from code.** It depends on a 600-DPI pixel reading
  of `files/Reuter.pdf` page 22 that exists only as the markdown matrix in this
  document. If the interaction table is ever rebuilt with different row order, every
  `pair_id` in the file silently points somewhere else. The steps above are enough to
  rebuild it, and they are written here for that reason.
- **Step 5 is a judgement, not a derivation.** `PG/BMP` was excluded because its mark
  was already explained; the same argument would apply to every other class, since all
  1159 rows sit in already-satisfied cells. It is not applied to them. Anyone using
  this file should know that its boundary is set by that one asymmetry.
