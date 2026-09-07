# pair_priors vs. orthogonal_init baseline (thematical_paths)

## Правило сопровождения
Numbers frozen to `graphics/thematical_paths_geom_chem_orthogonal_init_pair_priors/
thematical_paths_geom_chem_orthogonal_init_pair_priors.md` (35 rows, 7 groups x 5
seeds) and `graphics/thematical_paths_geom_chem_orthogonal_init/
thematical_paths_geom_chem_orthogonal_init.md` (33 rows: CRAL-TRIO and lipocalin have
only 4 seeds each) as of this snapshot, plus `metrics_summary.csv` rows for both
labels. Both `.md` files' "AUC vs chemistry null model" section is empty for these
two labels, so no chem-null leak check could be read off the report directly — the
LBP_BPI_CETP caveat below is inherited from `files/four_families_audit_...` /
MEMORY, not re-verified here.

## 0. Summary

| Question | Answer | Section |
|---|---|---|
| What does pair_priors change mechanically? | Adds 3 pre-computed pair-level descriptors (`elongation_shape_match`, `flatness_shape_match` to the geometric group; `hydropathy_rim_match` to the chemical group) as EXTRA input columns concatenated onto both the lipid-side and protein-side per-group MLP, before `ForcedInteraction`'s product step. No new skip path to the classifier. | 1 |
| Does it help overall (pooled)? | Pooled test BA +0.011 (0.5675→0.5787), well under 1 SEM (~0.017) — not distinguishable from noise. Pooled sens/spec gap narrows (0.535→0.465), i.e. less pooled sens/spec asymmetry, but this is a pooled artifact of opposite-direction shifts, not uniform improvement. | 2 |
| Does it help per-family? | Only 2/7 families move >1 SEM: LBP_BPI_CETP (BA +0.10, ~2.2 SEM) and scp2 (BA +0.097, ~3.1 SEM). Both wins come mostly from higher specificity, not sensitivity. IP_trans and START flip their sens/spec bias direction with roughly flat BA (trading error types, not reducing them). CRAL-TRIO, GLTP, lipocalin are flat within noise. | 2 |
| Caveats on the apparent wins? | LBP_BPI_CETP is the family flagged in `four_families_audit` as winning under nearly every descriptor/config variant regardless of mechanism — treat this "win" as consistent with a pre-existing family-fingerprint shortcut, not evidence pair_priors itself is doing real work. scp2's win is a genuine specificity gain (0.559→0.788, sens flat) not checkable against chemistry-null here (section empty in both reports). | 3 |

## 1. Mechanism (code, not name-guessing)

`--geometric_pair_priors` / `--chemical_pair_priors` (`training/read_configuration.py:649-650`,
CLI flags at `training/read_configuration.py:2964-2965`) only take effect under
`--thematical_paths` (guarded at `training/read_configuration.py:2212-2216`). They are
consumed in `architecture/thematic_descriptor_head.py:172-216`:

- The named tokens must come from `PAIR_DESCRIPTOR_NAMES`
  (`dataloader/pair_descriptors.py:57-62`) — a fixed, analytically-defined set of
  quantities that are already computed FROM both protein and lipid sides jointly
  (e.g. `elongation_shape_match`, `flatness_shape_match`, `hydropathy_rim_match` are
  in `MULTIPLICATIVE_PAIR_DESCRIPTOR_NAMES`, `dataloader/pair_descriptors.py:75-79` —
  products of two different-unit protein/lipid quantities, z-scored before
  multiplying).
- Each selected pair-prior column is concatenated onto BOTH the lipid-side input and
  the protein-side input of its group's `_ModalityMLP`
  (`architecture/thematic_descriptor_head.py:205-216`: `len(geom_lip) +
  len(geom_priors)`, `len(geom_prot) + len(geom_priors)`, etc.) — i.e. the SAME
  already-paired scalar is fed to both halves of the forced interaction, not added as
  a separate third branch or a skip path to the classifier. It still has to pass
  through a side's own MLP before reaching `ForcedInteraction`'s product
  (comment at `architecture/thematic_descriptor_head.py:172-178`).
- This run's actual selection (`metrics_summary.csv`): `geometric_pair_priors =
  elongation_shape_match,flatness_shape_match`; `chemical_pair_priors =
  hydropathy_rim_match`. All other config fields (`geometric_descriptors`,
  `chemical_descriptors`, `thematical_orthogonal_init=1`, `thematical_orth_weight=0.0`)
  are identical between the two labels — this is a clean, single-variable comparison.
- Parameter count: 4450 (pair_priors) vs. 4258 (baseline), +192 params — a small
  capacity increase from the extra input columns on 4 MLPs, not a new module.

## 2. Metrics: per-family sensitivity / specificity / BA, test split

| Group | n (base/pp) | test BA base→pp | test sens base→pp | test spec base→pp | ΔBA (SEM) |
|---|---|---|---|---|---|
| CRAL-TRIO | 4/5 | 0.537→0.515 | 0.246→0.424 | 0.828→0.607 | -0.022 (SEM 0.024) |
| GLTP | 5/5 | 0.672→0.640 | 0.600→0.592 | 0.744→0.688 | -0.032 (SEM 0.106) |
| IP_trans | 5/5 | 0.561→0.533 | 0.565→0.304 | 0.557→0.762 | -0.028 (SEM 0.037) |
| LBP_BPI_CETP | 5/5 | 0.522→0.622 | 0.226→0.426 | 0.817→0.817 | **+0.100 (SEM 0.046)** |
| START | 5/5 | 0.552→0.518 | 0.345→0.603 | 0.760→0.434 | -0.034 (SEM 0.051) |
| lipocalin | 4/5 | 0.559→0.564 | 0.569→0.633 | 0.549→0.494 | +0.005 (SEM 0.062) |
| scp2 | 5/5 | 0.562→0.659 | 0.565→0.529 | 0.559→0.788 | **+0.097 (SEM 0.031)** |
| ALL (pooled) | 33/35 | 0.568→0.579 | 0.448→0.502 | 0.688→0.656 | +0.011 (SEM ~0.017) |

SEM = sqrt((std_base/√n_base)^2 + (std_pp/√n_pp)^2) from the per-group std/n in each
`.md`'s "By group" section.

Only LBP_BPI_CETP and scp2 clear ~1 SEM; everything else is noise-level or a
sens/spec trade rather than a net error reduction (IP_trans: sensitivity drops 26pp
while specificity rises 20pp; START: the opposite trade, sensitivity rises 26pp while
specificity drops 33pp — BA nets out roughly flat in both).

## 3. Caveats

- **LBP_BPI_CETP**: per MEMORY (`four-families-audit-2026-08-31` /
  `files/four_families_audit...`), this family wins under nearly every
  descriptors/GBdescriptors/bbp config tried so far, independent of the specific
  mechanism being tested — consistent with a family-fingerprint shortcut rather than
  pair_priors adding real signal. Cannot be checked against the chemistry-null AUC
  here because the "AUC vs chemistry null model" section is empty in both `.md`
  reports for these two labels.
- **scp2**: the one family where sens/spec/BA all support a specificity-driven win
  with no compensating sensitivity loss. No chem-null section available to rule out a
  simpler chemistry-only explanation, and n=5 seeds only.
- **Pooled ALL sens/spec gap narrowing (0.535→0.465)** should not be read as "the
  model became more balanced everywhere" — it is a pooled average of two families
  moving toward higher sensitivity (CRAL-TRIO, START) and two moving toward higher
  specificity (IP_trans, scp2, LBP_BPI_CETP), i.e. opposite-direction shifts that
  happen to average out, matching the documented pooled-vs-per-family pitfall.

## Чем посчитано

- `graphics/thematical_paths_geom_chem_orthogonal_init_pair_priors/
  thematical_paths_geom_chem_orthogonal_init_pair_priors.md` (analysis/
  summarize_label.py output) — per-family test sens/spec/BA/std/n for pair_priors.
- `graphics/thematical_paths_geom_chem_orthogonal_init/
  thematical_paths_geom_chem_orthogonal_init.md` — same for baseline.
- `metrics_summary.csv` rows for both labels — `geometric_pair_priors`,
  `chemical_pair_priors`, `geometric_descriptors`, `chemical_descriptors`,
  `thematical_orthogonal_init`, `thematical_orth_weight`, `number_of_parameters`
  (confirms the two configs differ only in the pair_priors fields).
- `architecture/thematic_descriptor_head.py:147-233`, `dataloader/
  pair_descriptors.py:57-91`, `training/read_configuration.py:649-650,2212-2216,
  2964-2965` — mechanism/flag wiring.
- SEM columns computed by hand from each `.md`'s "By group" std/n (std/√n per arm,
  combined in quadrature) — no script run, arithmetic only.
