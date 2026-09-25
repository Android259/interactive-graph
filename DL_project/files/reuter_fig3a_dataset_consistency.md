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
