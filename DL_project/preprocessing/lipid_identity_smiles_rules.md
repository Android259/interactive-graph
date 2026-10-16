# Lipid classes from SMILES

The feature checks are implemented in `training/pair_baseline_common.py`,
in `smiles_features()`. Baseline models use them to describe lipid structures.
The code does not read this Markdown file.

The classification rules below describe the former identity audit, which compared
SMILES with `FullIdentityOfLipid`. That audit has been removed. Baseline models
extract features without assigning a lipid class through these rules.
For the former classification, rules were applied in order; the first match won.

## Cis and trans conventions

These are the group-specific conventions for SMILES correction. Feature extraction
does not rewrite double-bond stereochemistry.

For `PC`, `PE`, `PG`, `PI`, `PS`, `LPC`, `LPE`, `LPG`, `BMP`, and `Cardiolipin`,
fatty-acid double bonds are treated as cis and written as `/C=C\`.

Sphingolipids can have double bonds in the sphingoid base and in the fatty-acid chain.
The groups here are `Ceramide`, `Ceramide phosphate`, `HexCer`, `Hex2Cer`, `SHexCer`,
and `Sphingomyelin`.

For a `d` sphingoid base, the C4/C5 double bond is treated as trans and written as
`/C=C/`. This is the first double bond after a hydroxylated chiral carbon written
as `[C@]([H])(O)`, `[C@@]([H])(O)`, `[C@H](O)`, or `[C@@H](O)`.
Other fatty-acid double bonds are treated as cis.

A `DH` base has no C4/C5 double bond. A `t` or `t*` base is phytosphingoid, with
three hydroxyl groups and no protected C4/C5 double bond. For these bases,
remaining fatty-acid double bonds are treated as cis and written as `/C=C\`.
Identify the lipid group before applying these conventions.

## Features

Some checks use the molecular graph through RDKit. Text checks also appear in the
script. They depend on how the SMILES is written and are approximate.

- `amide_present`: an amide pattern, `NC(...)=O` or `NC(=O)`.
- `sphingoid_base_present`: an amide and one of the hydroxylated chiral-carbon patterns listed above.
- `phosphate_count`: the number of `P(` substrings.
- `choline_present`: RDKit SMARTS `[OX2][CX4][CX4][N+](C)(C)C` or the text pattern `OCC[N+](C)(C)C`.
- `ethanolamine_present`: RDKit SMARTS `[OX2][CX4][CX4][NX3;!$([N+])]` or the text pattern `OCCN`. Choline and serine matches exclude ethanolamine.
- `serine_present`: a carboxyl pattern, `C(O)(=O)` or `C(=O)O`, together with an `(N)` branch and `COP`.
- `inositol_present`: `[C@H]1`, no `O1`, and at least four `(O)` branches.
- `glycerol_head_present`: a phosphate-linked acyclic glycerol with no tails. Text patterns include `(O)(CO)COP` and `OCC(O)CO`.
- `pg_tail_layout_present`: an RDKit check for two glycerols around one phosphate. One has two acyl ester tails; the other has none.
- `bmp_tail_layout_present`: an RDKit check for two glycerols around one phosphate, each with one acyl ester tail.
- `sugar_ring_count`: RDKit counts five- or six-member rings with one ring oxygen and hydroxylated carbons. Without RDKit, the script counts `O1`, `O2`, and `O3`.
- `sulfate_present`: `S(=O)(=O)`, `S(O)(=O)=O`, or `S(=O)(O)=O`.
- `glycerol_backbone_present`: a phosphate-linked acyclic glycerol from RDKit, or a text match for `COP`, `COC(`, `OC[C@]`, `[C@](CO`, or `OC[C@@]`. A sphingoid-base match excludes it.
- `glycerol_backbone_count`: the number of `[C@](` and `[C@@](` substrings. This is an approximate count.
- `ester_count`: acyl ester carbonyls counted through RDKit. Without RDKit, the script searches `OC(` windows for a carbonyl ending in `)=O` or `=O)`.
- `ether_tail_count`: matches for `COCCCC`, `CO/C=C`, and `CO\C=C`.
- `tail_count`: the RDKit glycerol-tail count plus an amide tail when the graph count is available and positive. Otherwise, it is `ester_count + ether_tail_count + amide_tail_count`. An amide contributes one tail.
- `free_oh_count`: an approximate count from `(O)`, a starting `OC`, and `CO)` or `CO;` patterns.
- `carboxyl_present`: RDKit SMARTS `[CX3](=O)[OX1H0-,OX2H1]` or a text match for `(=O)O`, `C(=O)O`, `C(O)(=O)`, `C(O)=O`, or `C(=O)[O-]`.
- `hydrocarbon_chain_present`: at least eight `C` symbols in the SMILES. The symbols need not be consecutive.
- `polyene_alcohol_present`: at least three carbon-carbon double bonds and an alcohol match. RDKit checks the graph; text checks use `C=C` and `(O)`. The check also excludes the carboxyl text patterns `(=O)O` and `C(O)=O`, phosphate, esters, and amides.

## Classification order

Each rule requires all the listed conditions. `NOT` means the feature must be false.

1. Sphingomyelin: `amide_present`, `sphingoid_base_present`, `phosphate_count >= 1`, `choline_present`.

2. Ceramide phosphate: `amide_present`, `sphingoid_base_present`, `phosphate_count >= 1`, `NOT choline_present`, `sugar_ring_count == 0`.

3. SHexCer: `amide_present`, `sphingoid_base_present`, `sugar_ring_count >= 1`, `sulfate_present`.

4. Hex2Cer: `amide_present`, `sphingoid_base_present`, `sugar_ring_count >= 2`, `NOT sulfate_present`.

5. HexCer: `amide_present`, `sphingoid_base_present`, `sugar_ring_count == 1`, `NOT sulfate_present`, `phosphate_count == 0`.

6. Ceramide: `amide_present`, `sphingoid_base_present`, `phosphate_count == 0`, `sugar_ring_count == 0`.

7. Cardiolipin: `phosphate_count == 2`, `glycerol_backbone_count >= 3`, `tail_count == 4`.

8. BMP: `phosphate_count == 1`, `bmp_tail_layout_present`, `free_oh_count >= 2`, `NOT choline_present`, `NOT ethanolamine_present`, `NOT serine_present`, `NOT inositol_present`.

9. PC: `phosphate_count == 1`, `glycerol_backbone_present`, `choline_present`, `tail_count == 2`, `NOT amide_present`.

10. PE: `phosphate_count == 1`, `glycerol_backbone_present`, `ethanolamine_present`, `tail_count == 2`, `NOT amide_present`.

11. PG: `phosphate_count == 1`, `glycerol_backbone_present`, `glycerol_head_present`, `pg_tail_layout_present`, `NOT amide_present`.

12. PI: `phosphate_count == 1`, `glycerol_backbone_present`, `inositol_present`, `tail_count == 2`, `NOT amide_present`.

13. PS: `phosphate_count == 1`, `glycerol_backbone_present`, `serine_present`, `tail_count == 2`, `NOT amide_present`.

14. LPC: `phosphate_count == 1`, `glycerol_backbone_present`, `choline_present`, `tail_count == 1`, `free_oh_count >= 1`, `NOT amide_present`.

15. LPE: `phosphate_count == 1`, `glycerol_backbone_present`, `ethanolamine_present`, `tail_count == 1`, `free_oh_count >= 1`, `NOT amide_present`.

16. LPG: `phosphate_count == 1`, `glycerol_backbone_present`, `glycerol_head_present`, `tail_count == 1`, `free_oh_count >= 1`, `NOT amide_present`.

17. TAG: `phosphate_count == 0`, `glycerol_backbone_present`, `ester_count == 3`, `free_oh_count == 0`, `NOT amide_present`.

18. DAG: `phosphate_count == 0`, `glycerol_backbone_present`, `ester_count == 2`, `free_oh_count >= 1`, `NOT amide_present`.

19. Fatty acyl / free fatty acid: `phosphate_count == 0`, `carboxyl_present`, `hydrocarbon_chain_present`, `NOT glycerol_backbone_present`, `NOT amide_present`, `sugar_ring_count == 0`.

20. Retinol: `polyene_alcohol_present`, `phosphate_count == 0`, `ester_count == 0`, `amide_present == false`, `glycerol_backbone_present == false`.

21. Unknown: no earlier rule matched. The former audit reported `unknown_class` and left the input SMILES unchanged.
