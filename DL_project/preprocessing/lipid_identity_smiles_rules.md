# Lipid Identity Rules From SMILES Features

These rules classify a SMILES-derived feature set. Apply rules in order.

## Lipid Group Stereochemistry Properties

- Glycerophospholipid groups (`PC`, `PE`, `PG`, `PI`, `PS`, `LPC`, `LPE`, `LPG`, `BMP`, `Cardiolipin`) have fatty-acid unsaturation treated as cis. In SMILES this is normalized to canonical cis text form `/C=C\`.

- Sphingolipid groups (`Ceramide`, `Ceramide phosphate`, `HexCer`, `Hex2Cer`, `SHexCer`, `Sphingomyelin`) can contain two different double-bond contexts:
  - sphingoid base C4/C5 double bond
  - fatty-acid chain double bond

- For sphingolipids with `d` sphingoid base syntax, the sphingoid base C4/C5 double bond is treated as trans. In SMILES this is kept as canonical trans text form `/C=C/` when it is the first double bond after hydroxylated sphingoid carbon syntax such as `[C@]([H])(O)`, `[C@@]([H])(O)`, `[C@H](O)`, `[C@@H](O)`.

- For sphingolipids with `DH` syntax, the sphingoid base C4/C5 double bond is absent. Any remaining double bond is treated as fatty-acid unsaturation and normalized to cis `/C=C\`.

- For sphingolipids with `t` or `t*` syntax, the sphingoid base is phytosphingoid/trihydroxy and has no protected C4/C5 double bond. Any remaining double bond is treated as fatty-acid unsaturation and normalized to cis `/C=C\`.

- Additional fatty-acid unsaturation in sphingolipids is treated as cis and normalized to `/C=C\`.

- These stereochemistry properties are lipid-group properties. They are used together with identity rules: first identify the lipid group/class, then apply the group-specific cis/trans rule to SMILES double-bond syntax.

## Feature Meanings

- `amide_present`: amide bond in SMILES, detected by `NC(...)=O` or `NC(=O)`. This is the fatty-acid amide linkage of sphingolipids.

- `sphingoid_base_present`: `amide_present` plus a chiral hydroxylated sphingoid carbon. SMILES patterns: `[C@]([H])(O)`, `

[C@@]([H])(O)`, `[C@H](O)`, `[C@@H](O)`.

- `phosphate_count`: count of phosphate atoms by substring `P(`.

- `choline_present`: phosphocholine headgroup. If RDKit is installed, script uses graph SMARTS `[OX2][CX4][CX4][N+](C)(C)C`. Without RDKit, script falls back to SMILES text pattern `OCC[N+](C)(C)C`.

- `ethanolamine_present`: ethanolamine headgroup. If RDKit is installed, script uses graph SMARTS `[OX2][CX4][CX4][NX3;!$([N+])]`. It is false when `choline_present` or `serine_present` is true. Without RDKit, script falls back to SMILES text pattern `OCCN`.

- `serine_present`: serine-like headgroup. SMILES requires a carboxyl pattern (`C(O)(=O)` or `C(=O)O`),

 an amine branch `(N)`, and phospholipid linkage `COP`.

- `inositol_present`: inositol-like ring. SMILES requires `[C@H]1`, no `O1`, and at least four hydroxyl branches `(O)`.

- `glycerol_head_present`: glycerol headgroup used by PG/LPG. If RDKit is installed, script checks for a phosphate-linked acyclic glycerol unit with zero tails. Without RDKit, script falls back to SMILES text patterns `(O)(CO)COP` or `OCC(O)CO`.

- `pg_tail_layout_present`: RDKit graph check for PG layout. Around one phosphate, one glycerol unit has two acyl ester tails, and the second glycerol unit is the headgroup with zero acyl ester tails.

- `bmp_tail_layout_present`: RDKit graph check for BMP layout. Around one phosphate, two different glycerol units are present, and each glycerol unit has exactly one acyl ester tail.

- `sugar_ring_count`: if RDKit is installed, script counts 5/6-member sugar-like rings with one ring oxygen and hydroxylated ring carbons. Without RDKit, script falls back to rough ring-closure text count `O1`, `O2`, `O3`.

- `sulfate_present`: sulfate group. SMILES patterns: `S(=O)(=O)`, `S(O)(=O)=O`, `S(=O)(O)=O`.

- `glycerol_backbone_present`: glycerolipid/glycerophospholipid backbone. If RDKit is installed, script checks for an acyclic phosphate-linked glycerol unit. Without RDKit, script falls back to SMILES text patterns `COP`, `COC(`, `OC[C@]`, `[C@](CO`, `OC[C@@]`. It is false when `sphingoid_base_present` is true.

- `glycerol_backbone_count`: rough count of chiral glycerol-like centers by `[C@](` and `[C@@](`.

- `ester_count`: acyl ester count. If RDKit is installed, script counts ester carbonyls by graph bonds. Without RDKit, script searches `OC(` windows that contain carbonyl ending `)=O` or `=O)`.

- `ether_tail_count`: ether-linked tail count. SMILES patterns: `COCCCC`, `CO/C=C`, `CO\C=C`.

- `tail_count`: `ester_count + ether_tail_count + amide_tail_count`, where `amide_tail_count` is 1 when `amide_present` is true.

- `free_oh_count`: rough hydroxyl count. Counts `(O)`, plus terminal/start patterns `OC`, `CO)`, `CO;`.

- `carboxyl_present`: free fatty-acid carboxyl. If RDKit is installed, script uses SMARTS `[CX3](=O)[OX1H0-,OX2H1]` for carboxylic acid/carboxylate. Without RDKit, script falls back to SMILES text patterns: `(=O)O`, `C(=O)O`, `C(O)(=O)`, `C(O)=O`, `C(=O)[O-]`.

- `hydrocarbon_chain_present`: hydrocarbon chain. Current text check: total SMILES carbon symbol count `C` is at least 8. This keeps polyunsaturated chains valid when `/C=C\` breaks consecutive `CCCCCC`.

- `polyene_alcohol_present`: retinol-like pattern. If RDKit is installed, script counts carbon-carbon double bonds and alcohol oxygen by graph. Without RDKit, it uses text `C=C` and hydroxyl `(O)`. Requires at least three `C=C`, hydroxyl/alcohol, no carboxyl, `phosphate_count == 0`, 

`ester_count == 0`, and `amide_present == false`.

1. Sphingomyelin:
   IF amide_present
   AND sphingoid_base_present
   AND phosphate_count >= 1
   AND choline_present
   THEN class = Sphingomyelin

2. Ceramide phosphate:
   IF amide_present
   AND sphingoid_base_present
   AND phosphate_count >= 1
   AND NOT choline_present
   AND sugar_ring_count == 0
   THEN class = Ceramide phosphate

3. SHexCer:
   IF amide_present
   AND sphingoid_base_present
   AND sugar_ring_count >= 1
   AND sulfate_present
   THEN class = SHexCer

4. Hex2Cer:
   IF amide_present
   AND sphingoid_base_present
   AND sugar_ring_count >= 2
   AND NOT sulfate_present
   THEN class = Hex2Cer

5. HexCer:
   IF amide_present
   AND sphingoid_base_present
   AND sugar_ring_count == 1
   AND NOT sulfate_present
   AND phosphate_count == 0
   THEN class = HexCer

6. Ceramide:
   IF amide_present
   AND sphingoid_base_present
   AND phosphate_count == 0
   AND sugar_ring_count == 0
   THEN class = Ceramide

7. Cardiolipin:
   IF phosphate_count == 2
   AND glycerol_backbone_count >= 3
   AND tail_count == 4
   THEN class = Cardiolipin

8. BMP:
   IF phosphate_count == 1
   AND bmp_tail_layout_present
   AND free_oh_count >= 2
   AND NOT choline_present
   AND NOT ethanolamine_present
   AND NOT serine_present
   AND NOT inositol_present
   THEN class = BMP

9. PC:
   IF phosphate_count == 1
   AND glycerol_backbone_present
   AND choline_present
   AND tail_count == 2
   AND NOT amide_present
   THEN class = PC

10. PE:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND ethanolamine_present
    AND tail_count == 2
    AND NOT amide_present
    THEN class = PE

11. PG:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND glycerol_head_present
    AND pg_tail_layout_present
    AND NOT amide_present
    THEN class = PG

12. PI:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND inositol_present
    AND tail_count == 2
    AND NOT amide_present
    THEN class = PI

13. PS:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND serine_present
    AND tail_count == 2
    AND NOT amide_present
    THEN class = PS

14. LPC:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND choline_present
    AND tail_count == 1
    AND free_oh_count >= 1
    AND NOT amide_present
    THEN class = LPC

15. LPE:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND ethanolamine_present
    AND tail_count == 1
    AND free_oh_count >= 1
    AND NOT amide_present
    THEN class = LPE

16. LPG:
    IF phosphate_count == 1
    AND glycerol_backbone_present
    AND glycerol_head_present
    AND tail_count == 1
    AND free_oh_count >= 1
    AND NOT amide_present
    THEN class = LPG

17. TAG:
    IF phosphate_count == 0
    AND glycerol_backbone_present
    AND ester_count == 3
    AND free_oh_count == 0
    AND NOT amide_present
    THEN class = TAG

18. DAG:
    IF phosphate_count == 0
    AND glycerol_backbone_present
    AND ester_count == 2
    AND free_oh_count >= 1
    AND NOT amide_present
    THEN class = DAG

19. Fatty acyl / free fatty acid:
    IF phosphate_count == 0
    AND carboxyl_present
    AND hydrocarbon_chain_present
    AND NOT glycerol_backbone_present
    AND NOT amide_present
    AND sugar_ring_count == 0
    THEN class = Fatty acyl

20. Retinol:
    IF polyene_alcohol_present
    AND phosphate_count == 0
    AND ester_count == 0
    AND amide_present == false
    AND glycerol_backbone_present == false
    THEN class = Retinol

21. Unknown:
    IF no rule matched
    THEN class = Unknown
    AND leave SMILES unchanged
    AND report unknown_class
