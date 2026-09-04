# `--thematical_paths`: forced geom/chem lipid↔protein interaction

Third sufficiency-test branch `Final_Layer` can build, sibling to `--descriptors_head`
and `--two_pair_descriptors_paths` (mutually exclusive, `ModelConfig.validate`). Source
of truth: `architecture/thematic_descriptor_head.py`
(`ThematicDescriptorHead`/`ForcedInteraction`/`thematical_orthogonality_loss`), wired
into `architecture/final_layer.py` and `architecture/interaction_classification.py`,
flags in `training/read_configuration.py`. Design discussion this documents happened
in chat, not in another file — this is the only writeup.

## Motivation

`files/descriptor_catalog.md`'s 28 lipid/protein descriptors are currently either
broadcast raw onto every node (`--protein_descriptors`/`--lipid_descriptors`) or fed to
one shared self-attention token set (`--pair_descriptors`, `--good_descriptors`/
`--bad_descriptors`) that is free to read any subset of tokens alone. Neither forces
the network to actually combine a lipid-side quantity with a protein-side one before
it can use either — a classifier sitting on top of either mechanism can, in principle,
decide from lipid identity or protein identity alone. `--thematical_paths` groups the
28 names by physical hypothesis and structurally removes that shortcut within each
group: each group's output can only be a function of BOTH its lipid-side and
protein-side inputs (see "Architecture"), and the final vector can only be a function
of BOTH groups.

## Groups

Two groups, each independently comma-separated in `--geometric_descriptors=`/
`--chemical_descriptors=` (same `DESCRIPTOR_CATALOG` syntax, including `<name>_coarse=
<spec>`, as `--good_descriptors`/`--bad_descriptors`):

| group | lipid side | protein side |
|---|---|---|
| geometric (`--geometric_descriptors`) | `chain, tail_count, npr1, npr2, heavy, molar_refractivity, rotatable_bond_count, ring_count` | `pocket_extent, pocket_elongation, pocket_volume_per_sasa, pocket_flatness, buriedness_q50, depth_q10, pocket_sasa_share, pocket_residue_share, ev14_q50` |
| chemical (`--chemical_descriptors`) | `unsaturation, aromatic_ring_count, hbond, tpsa, logp` | `aromatic_share, aromatic_share_rim, apolar_sasa_share, hydropathy_core, hydropathy_rim, ev28_q10` |

All 13 `LIPID_DESCRIPTOR_NAMES` + 15 `PROTEIN_DESCRIPTOR_NAMES` (+ `extent`/
`polar_share`) are accounted for between the two groups; nothing is silently dropped.
Including `pocket_sasa_share`/`pocket_residue_share` (η² 0.85/0.71) and `ev14_q50` (η²
0.59) was a deliberate choice to use every descriptor rather than pre-excluding the
highest-family-η² ones — see "Risks" for the consequence.

`dataloader.pair_descriptors.split_names_by_side` assigns each token to a side by
membership in `LIPID_DESCRIPTOR_NAMES` vs `PROTEIN_DESCRIPTOR_NAMES + ("extent",
"polar_share")`, and raises if a caller names a `PAIR_DESCRIPTOR_NAMES` entry
(`occupancy`, `aromatic_contact`, ...) — those already combine both sides by formula
and have no single side left to assign.

## Architecture

```
geometric group:                          chemical group:
  lipid raw scalars  -> MLP -> BN -> v_lip   lipid raw scalars  -> MLP -> BN -> v_lip
  protein raw scalars -> MLP -> BN -> v_prot protein raw scalars-> MLP -> BN -> v_prot
       \___________ ForcedInteraction ___________/    \___________ ForcedInteraction ___________/
                    z_geom                                          z_chem
                          \_____________ ForcedInteraction _____________/
                                          z_final
                                             |
                                Linear -> act -> dropout -> Linear(2)
```

- **Per-side MLP** (`_ModalityMLP`): `Linear(n_side, hidden) -> act -> Linear(hidden,
  hiddim)`, then `BatchNorm1d(hiddim, affine=False)`. The classic regression trick of
  centering an interaction term's inputs on a train-only precomputed constant does not
  apply here — `v_lip`/`v_prot` are this MLP's OWN output, not a fixed input, so their
  distribution moves as the MLP trains. BatchNorm tracks train-batch running mean/var
  and freezes it for eval, `affine=False` so nothing re-adds a learned offset after
  centering — the standard tool for centering a non-stationary activation.
  **Deliberately kept over LayerNorm** despite the cold-split risk in "Risks" below:
  LayerNorm normalises one sample's own vector across channels and removes no
  population-level mean at all, so it would not do the thing centering is *for* here
  (isolating the interaction from each side's main effect) — it would fix the
  train/eval mismatch by giving up the property the design needs, not by fixing it.
- **`ForcedInteraction`**: `z = FFN(normalize(signed_sqrt((W_a . v_a) * (W_b . v_b))))`
  — a low-rank bilinear product (elementwise product of two projections, not a full
  bilinear tensor; the MLB design, Kim et al. 2017), signed-square-rooted and
  L2-normalised (Lin et al.'s bilinear-CNN pooling, 2015; reused by MFB, Yu et al.
  2017) before a small FFN. The normalisation is not a trainable regulariser — no
  parameters, nothing in the loss — it exists because a raw elementwise product's
  scale moves multiplicatively with both inputs' norms and can collapse toward a
  near-constant output if the two projections drift apart during training (MLB's own
  paper reports slow, hyperparameter-sensitive convergence without an equivalent
  step). There is **no skip connection** carrying raw `v_a`/`v_b` forward alongside
  the product — the only path to `z` is through the product, which is what makes the
  interaction structurally forced rather than optional for the downstream MLP to
  ignore. Reused identically for both levels (within-group and group-vs-group).
- **Final layer**: after the level-2 `z_final`, one `Linear -> activation -> dropout ->
  Linear(2)` block, the same shape `--descriptors_head`'s own post-attention classifier
  uses (`architecture/final_layer.py`'s `descriptors_head` branch) — a fixed, minimal
  head rather than the full `binar` MLP stack the main branch builds.

## Orthogonality penalty (`--thematical_orth_weight`)

Off by default (`0.0`, no probes built, no extra parameters). A nonzero value builds,
per `ForcedInteraction` site (3 total: geom, chem, level2), two small 2-layer MLP
probes (`_make_probe`: `Linear(dim, dim) -> act -> Linear(dim, 1)`, not a bare
`Linear(dim, 1)`) and adds `thematical_orthogonality_loss`'s `(penalty + probe_loss)`,
weighted by `--thematical_orth_weight`, into the training loop's total loss
(`training/new_train.py`, mirroring `adversarial_grl`/`dann_family`'s convention:
stashed by the head under `self.training` only, read and combined with labels by the
training loop, never inside `forward()` itself).

- `probe_loss`: each probe is trained (via its own BCE) to predict the binding label
  from ONE side alone (`v_a.detach()`/`v_b.detach()` — stop-gradient, so training the
  probe cannot reshape the side it reads).
- `penalty`: pushes the interaction's own output `z` to be **independent** (HSIC —
  `hsic()`, Gretton et al. 2005 — not a raw covariance) of the probe's **detached**
  prediction — so the penalty's gradient reaches `z` (and the `ForcedInteraction` block
  that produced it), never the probe itself. HSIC rather than covariance because
  `Cov(z, p) == 0` does not imply independence, only no LINEAR relationship — a
  covariance penalty can be driven to zero while `z` still reconstructs `p` through a
  nonlinear function, which a bare-linear probe would also have missed on the
  detection side. Both fixes (MLP probe, HSIC penalty) close the same class of gap
  from two ends: a linear probe checking a linear penalty was the weakest combination
  possible.
- Averaged over the 3 sites and the 2 probes at each (never summed), so the weight
  means the same pressure regardless of how many sites are active.
- **HSIC's own caveat**: the empirical estimator is biased and noisy at small batch
  sizes (`hsic()`'s own docstring) — trust it at the batch sizes real training runs
  use, not at the `batch=2` this module's smoke tests use (those only check the
  penalty is finite and differentiable, not that it estimates dependence well).

**Known limitation, not closed by this mechanism.** A fingerprint jointly correlated
across `a` AND `b` at once (present only in their combination, absent from either side
alone) satisfies the exact same "not predictable from one side alone" criterion real
lipid↔protein synergy does — `probe_a`/`probe_b` cannot detect it (neither side alone
predicts it), so `penalty` cannot suppress it either, HSIC or not: HSIC closed the
linear-vs-nonlinear gap a single-side probe had, it did not touch this one, because no
single-side probe (however expressive) can see a pattern that only exists in the
combination. Closing THIS gap needs a training-time signal that actually corrupts one
side and checks whether the model still performs — e.g. a SynIB-style
(arXiv:2606.09853) penalty that shuffles/masks one side within a batch and penalises
the model for staying confident, which is a differentiable, training-time version of
the pair-shuffling audit two paragraphs down. Not implemented here — a candidate
follow-up, not part of this architecture as built. This is the same shape as the
project's unresolved `LBP_BPI_CETP` leak
([[descriptors-path-fingerprint-leak]]) surviving exclusion of every individually
suspect channel — the suspected mechanism there is exactly a cross-side, not
single-side, pattern. Closing this gap needs a different, downstream test: shuffle the
lipid↔protein pairing within a held-out family (preserving each side's own marginal
distribution) and check whether `z`/the model's accuracy on that family survives — if
it does not, the signal was pair-specific identity, not real interaction. Not
implemented here; a follow-up, not part of this architecture.

## Risks

- **Every descriptor is used, including the three highest family-η² ones**
  (`pocket_sasa_share` 0.85, `pocket_residue_share` 0.71, `ev14_q50` 0.59 — all above
  the 0.235 floor, all excluded from the existing `pocket_descriptors_family_neutral`
  7). The geometric group's protein-side MLP can therefore learn a near-family
  fingerprint on its own; `ForcedInteraction`'s no-skip structure keeps that fingerprint
  from reaching `z_geom` for free, but does not prevent the fingerprint from being
  reintroduced multiplicatively (see next point).
- **The no-skip/orthogonality combination only closes the single-side shortcut**, not
  the cross-side one — see "Known limitation" above. A `LBP_BPI_CETP`-shaped leak would
  pass every check this architecture runs.
- **Higher parameter count for the same descriptor budget** than the existing
  self-attention heads at matched `hiddim`/`m` — see "Parameter count" below. On
  `--double_coldsplit` (as few as ~35 proteins per family) this is more capacity per
  training example than the family-neutral baselines were sized for; whether it overfits
  is an empirical question this writeup does not answer.
- **BatchNorm's train-only running mean/var is applied to a held-out family's own
  distribution at eval, and it is not known whether that helps or hurts.** Under
  `--double_coldsplit` the eval batch is a family never seen in train; the frozen
  centering constant is an estimate of the TRAIN mixture's mean, not this family's own.
  This could incidentally strip out a family-specific offset (helpful) or introduce a
  systematic shift the interaction layer never trained against (harmful) — kept as
  BatchNorm anyway (see "Architecture" above) because the alternative (LayerNorm)
  would remove the population-mean-centering the design needs for a different reason,
  not fix this one. Unresolved; worth an ablation before trusting a result from this
  architecture.
- **BatchNorm at batch size 2 is well-defined but noisy** — the smoke tests below use
  `batch=2`; real runs should use a larger batch so the running mean/var estimates used
  at eval are stable.

## Benefits

- **Structural, not just statistical, non-redundancy**: removing the skip connection is
  a hard architectural constraint, not a soft penalty that could be outweighed by
  another loss term — the classifier literally has no tensor path to a group's raw
  `v_lip`/`v_prot` other than through the product.
- **Per-hypothesis interpretability**: each of the 3 `ForcedInteraction` sites can be
  ablated independently (e.g. disable `chem_interaction`'s contribution) to test one
  physical hypothesis (geometry-only fit, or aromatic/polarity-only match) without
  touching the other, unlike a single shared self-attention block over all 28 tokens.
- **Reuses the project's own existing formulas as an inductive-bias hypothesis**: the
  interaction is deliberately shaped like the hand-crafted `PAIR_DESCRIPTOR_NAMES`
  products (`aromatic_contact = aromatic_share * unsaturation`, etc.) generalised from
  a fixed scalar product to a learned low-rank bilinear one — a step up in expressivity
  from those exact formulas while keeping their "both sides must be non-trivial"
  shape.
- **Orthogonality diagnostic comes for free** when `--thematical_orth_weight` is on:
  `probe_loss` alone is a readable leak gauge (a probe that gets much better than
  chance from one side alone flags that side's group as risky), independent of whether
  the penalty term is trusted to fix anything.

## Parameter count

Measured directly (`sum(p.numel() for p in model.parameters() if p.requires_grad)`),
`hiddim=8` (other fields at `ModelConfig` defaults: `m=4, HEADS=8`), both groups as
listed above — the same `--hiddim=8` this project's other small "hid8" baselines use:

| `--thematical_orth_weight` | parameters |
|---|---|
| `0.0` (no probes) | **4258** |
| `0.05` (probes built, `scripts/arg_files/thematical_paths_geom_chem.md`'s value) | **4744** (+486 = 6 MLP probes × (8×8+8 + 8×1+1) = 6 × 81) |

## References

External work this design borrows mechanisms from or should be checked against:

- Kim et al., "Hadamard Product for Low-rank Bilinear Pooling" (MLB), ICLR 2017 —
  `ForcedInteraction`'s core `(W_a . a) * (W_b . b)` shape, and the source of its
  known slow/hyperparameter-sensitive convergence without post-product normalisation.
- Yu et al., "Multi-modal Factorized Bilinear Pooling" (MFB), ICCV 2017, and Lin et
  al.'s bilinear-CNN pooling, ICCV 2015 — the signed-sqrt + L2-norm fix
  `ForcedInteraction` now applies.
- Gretton et al., "Measuring Statistical Dependence with Hilbert-Schmidt Norms", ALT
  2005 — `hsic()`.
- Bai et al., "Interpretable bilinear attention network with domain adaptation
  improves drug-target prediction" (DrugBAN), Nature Machine Intelligence 2023 — the
  closest existing model to this task; does token-level bilinear ATTENTION between
  drug substructures and protein subsequences rather than this design's
  pool-then-interact, a finer granularity this architecture does not attempt.
- arXiv:2606.09853, "SynIB: Informational Bottleneck for Maximizing Synergy in
  Multimodal Learning" — the modality-corruption training penalty named as the
  candidate fix for the "known limitation" above.

## Flags

| flag | meaning |
|---|---|
| `--thematical_paths` | activates this branch (mutually exclusive with `--descriptors_head`/`--two_pair_descriptors_paths`) |
| `--geometric_descriptors=<comma-separated>` | geometric group's token list |
| `--chemical_descriptors=<comma-separated>` | chemical group's token list |
| `--thematical_orth_weight=<float>` | 0.0 (default) = off; nonzero builds the probes and weights the penalty |

`validate()` rejects combining `--thematical_paths` with anything the usual
protein/lipid towers would need (`--bilinear_fusion`, `--adversarial_grl`,
`--dann_family`, `--chem_prior`/`--chem_adversary`, `--pocket_compat_prior`,
`--compatibility_input`/`--compatibility_split_input`, `--attention_pooling`,
`--swe_pooling`, `--lipid_only`/`--protein_only`/`--pair_descriptors_only`,
`--lipid_path_handicap`, `--double_attention`, `--pair_descriptors`,
`--protein_descriptors`, `--lipid_descriptors`) — same unsupported-combination
discipline as `--descriptors_head`/`--two_pair_descriptors_paths`, since no
protein1/lipid1/cross_attention1 tower is ever built under this flag.

## Tests

`tests/test_training_smoke_integration.py`: `test_thematical_paths_builds_no_encoder_
or_cross_attention_modules`, `test_thematical_paths_wires_columns_correctly`,
`test_thematical_paths_rejects_pair_descriptor_name`, `test_thematical_paths_requires_
both_groups`, `test_thematical_paths_conflicts_with_descriptors_head`, `test_
thematical_orth_weight_only_takes_effect_under_thematical_paths`, `test_thematical_
paths_orth_weight_trains_probes_and_resets_in_eval`. All pass, alongside the full
existing suite (127/127 in that file) and `test_lipid_encoder.py`/`test_loss.py`/
`test_dataloader_lipid_graphs.py`/`test_pair_descriptor_cache.py` per `architecture/
AGENTS.md`'s and `dataloader/AGENTS.md`'s change-rule contracts.
