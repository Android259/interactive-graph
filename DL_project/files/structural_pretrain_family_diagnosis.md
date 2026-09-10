# `structural_pretrain_family`: architecture diagnosis of the sens>>spec bias

Правило сопровождения: every number below is frozen to the 45-run batch behind
`graphics/structural_pretrain_family/structural_pretrain_family.md` (5 seeds x 9
families, `--label=structural_pretrain_family`, stage-2 weights loaded from
`models/structural_pretrain/random/seed0.pt`) plus the paired-skill numbers already
computed in `files/solo_family_report.md` for the same label and its two sibling arms
(`structural_pretrain_family_scratch`, `structural_pretrain_family_unfrozen`). Read-only
investigation: no training run, no checkpoint load, no script executed. Code read at the
commits present in the working tree on 2026-09-10.

**Central correction, load-bearing for everything below**: `structural_pretrain_family`
is NOT a family-held-out cold split. `--family_only` *restricts* the whole interaction
table to one family's own rows before sampling, then the ordinary code path runs a plain
random 85/15 row split inside that family (`dataloader/Dataloader.py:147-150`,
`:1461`). Train, valid and test all come from the same family's own proteins and lipids
-- this is the "one model per family/protein" regime (DeepCLIP/BERT-RBP-style), not
cross-family generalization. `analysis/solo_family_report.py`'s own docstring says so
explicitly (line 20: "the split is WARM ... 19-77% of the test block's lipids are also
in training") and its `.md` output repeats it (`files/solo_family_report.md` line 1-7).
`analysis/full_label_report.py`, which DOES reconstruct an excluded-family split, is
explicitly the wrong script for this label (`graphics/structural_pretrain_family/
structural_pretrain_family.md:214`). Everything phrased as "held-out family" in the
task framing is corrected accordingly in section 5.

## 0. Summary

| # | Question | Answer | Section |
|---|---|---|---|
| 1 | What pushes decisions toward "positive"? | Class-weighted cross-entropy (default `class_weights=True`) gives positives ~2x the per-row loss weight of negatives at this project's default 2:1 negative:positive sampling, stacked on a protein encoder frozen at a task (masked-feature reconstruction) that never saw the binding label, so protein-side signal is weak and the decision defaults toward the heavier-weighted class. No decision-threshold tuning or calibration anywhere in the pipeline: every reported sens/spec/BA is at a fixed softmax>=0.5 cut. | 1 |
| 2 | Why do groups differ? | ML/OSBP collapse because the family has 10 and 6 positive rows respectively in the whole raw dataset -- after 2:1 negative sampling and an 85/15/50/50 split the test block is 1-2 rows; train specificity is *also* 0.0, so this is a training-data-starvation failure, not a generalization gap. CRAL-TRIO/IP_trans/scp2 vs START/lipocalin is NOT resolved by any single code-groundable factor (row count, positive rate, protein count all fail to separate them cleanly); flagged as open rather than guessed. | 2 |
| 3 | Is net_AUC < null_AUC for GLTP/IP_trans real? | Artifact of pooling raw scores across different proteins with no per-protein calibration (`analysis/solo_family_report.py:234`, `binary_auc`); the same rows' within-protein-paired AUC (what the model is actually scored on) is 0.79-1.00 for GLTP, not 0.29. Not a real underperformance finding. | 3 |
| 4 | What can the model's output legitimately support? | Ranking lipids within one already-known protein (`AUC_within_protein_pairs`) has weak, mostly-not-significant positive skill over a no-training chemistry lookup (pooled +0.014 to +0.030 +/- 0.020-0.024, i.e. <=1.2 sigma across all three arms, `files/solo_family_report.md`). A fixed-threshold positive/negative call on an unseen protein is not supported by anything measured here. | 4 |
| 5 | How does the pipeline actually split/train? | Stage 1: one shared self-supervised run (`structural_pretrain`, `--structural_pretrain`, whole dataset, random split, 120 epochs) reconstructs 15% masked per-residue geometric features (3-dim, `protein_node_feature_count`) via MSE, never touching the `Interaction` label. Stage 2: 9 independent per-family runs, plain weighted cross-entropy, warm 85/15/50/50 split inside the one family, Adam, no LR schedule flags set. | 5 |

## 1. Architectural / training-pipeline causes of sens >> specificity

**1a. Fixed 0.5 decision threshold, no calibration, anywhere.** The training loop takes
`pred_class = outl.argmax(dim=1)` for every train/valid/test confusion computation
(`training/new_train.py:939,968,997,1506,1721,1850,1985`), which for 2-class logits is
exactly a softmax(class 1) >= 0.5 cut. `analysis/cross_sampler_eval.py:114-116`
(`balanced_accuracy(labels, scores, threshold=0.5)`) reproduces the same fixed cut for
every number in `graphics/*/​*.md`, including the summary table this diagnosis is built
on. There is no post-hoc threshold search or calibration step in `new_train.py` or in
`analysis/checkpoint_scores.py`; the latter's own docstring names this as a known
project-wide blind spot: "[a fixed 0.5 threshold] cannot separate 'the model ranks the
block no better than chance' from 'the model ranks it fine and the threshold sits in the
wrong place'" (`analysis/checkpoint_scores.py:4-10`). This alone means sens/spec at 0.5
conflates model quality with prior mismatch; it is not specific to `structural_pretrain`
but it is the reason the raw sens/spec numbers in the family table cannot be read as
"the model is biased" without checking what threshold-independent metrics (AUC,
within-protein-pair AUC) say -- which section 3-4 do.

**1b. Class-weighted cross-entropy actively upweights the positive class.**
`training/read_configuration.py:1283` sets `class_weights: bool = True` by default, and
neither `scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md` (the
stage-2 arg file, read in full) nor `scripts/arg_files/structural_pretrain.md` disables
it. `training/new_train.py:223-228` computes
`class_weights = class_counts.sum() / (2 * class_counts.clamp_min(1))` from the TRAIN
split's own label counts, and `training/new_train.py:1483` applies it:
`F.cross_entropy(loss_logits, interaction_labels.long(), weight=class_weights)`. Given
this project's default `negatives_per_positive = 2` (`dataloader/Dataloader.py:423-424`,
also not overridden by either arg file), a family's sampled train pool sits near 33%
positive / 67% negative, which makes `class_weights` approximately `[0.75, 1.5]` --
every positive row's loss contributes 2x a negative row's. `--balanced_batches` does
**not** additionally force a 1:1 in-batch ratio: `training/new_train.py:286-291`
documents that at `negatives_per_positive=2` a batch is drawn proportional to the pool
(~2 positive : 4 unlabeled for `--batch=8`), i.e. it only orders/covers the epoch, it
does not rebalance beyond the 2:1 the sampler already set. So the 2x per-example loss
weight from `class_weights` is the actual class-balancing force in this config, and it
biases the loss surface toward calling "positive" whenever the two classes are hard to
separate on the available signal -- which section 1c argues is often the case here.

**1c. The frozen protein encoder was pretrained on a task with zero relation to
binding.** `--structural_pretrain` (stage 1) masks 15% of a pocket's residues'
3-dimensional geometric node features (`protein_mask_share=0.15`,
`training/read_configuration.py:1442`; masking mechanics in
`dataloader/Dataloader.py:2095-2125`, `_mask_residue_features`) and trains protein1 (the
GATv2 protein encoder) plus a 2-layer MLP head (`architecture/
interaction_classification.py:70-74`, `protein_recon_head`) to reconstruct the
zeroed-out values by MSE (`training/new_train.py:1429-1437`,
`protein_recon_weight * F.mse_loss(model._recon_prediction, prot.recon_target)`). This
loss never reads `prot.inter` / the `Interaction` label at all
(`training/new_train.py:1430-1431`, explicit comment: "No Interaction label is read
here"). Stage 2 then loads protein1's weights from this checkpoint
(`training/new_train.py:108-143`) and, under `--freeze_pretrained_encoders`
(`training/new_train.py:144-146`, `for parameter in model.protein1.parameters():
parameter.requires_grad = False`), never updates them again. So the entire protein-side
representation that reaches the classifier is a generic local-geometry denoiser that was
never told which residues bind lipids -- it can encode "what a pocket residue's
neighborhood geometrically looks like" but has had no gradient pressure toward "is this
protein's pocket a binder." Whatever binding-relevant signal exists in the final
classification has to come from the lipid encoder, cross-attention and final layer
alone, learning on top of a protein representation that is informative about structure
but not, by construction, about the label. Combined with 1b's 2x loss weight on
positives, the path of least loss under a weak/uninformative protein signal is to lean
toward calling "positive" more often -- consistent with, though not a formal proof of,
the observed pattern (pooled test sens 0.90 vs spec 0.60,
`graphics/structural_pretrain_family/structural_pretrain_family.md:20`).

**Relation to other known project issues (memory cross-check).** This is a *different*
root cause from GRL collapse (no gradient-reversal head is in this config; `--dann` /
family adversary are off) and from PU/nnPU underfitting (`--pu_loss` is off in both arg
files read here -- the loss branch actually taken is the plain `elif conf.loss_type ==
"cross_entropy"` at `training/new_train.py:1472`, not `Non_Negative_Positive_Unlabeled_
loss`). It does share the general "sens/spec cold-split asymmetry... balancing/PU
amplify it" pattern from memory, but the amplifier here is concretely `class_weights`
(1b), not PU/nnPU or GRL, and the split it is measured on is warm-in-family, not a
cold split (see the central correction above and section 5).

## 2. Why some groups train worse than others

Raw family sizes, counted directly from `data/
Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_
Deduplicated.csv` (grouped by `ProteinDomain`, `Interaction==1` for positives):

| family | total rows | positive rows |
|---|---|---|
| CRAL-TRIO | 2547 | 165 |
| lipocalin | 2830 | 87 |
| IP_trans | 849 | 58 |
| START | 849 | 150 |
| scp2 | 849 | 43 |
| GLTP | 566 | 62 |
| LBP_BPI_CETP | 566 | 53 |
| OSBP | 566 | 6 |
| ML | 283 | 10 |

**ML and OSBP: a training-data-starvation collapse, grounded in both the raw counts and
the reported train metrics.** ML has 10 positive rows and OSBP has 6, in the ENTIRE raw
dataset, versus 43-165 for every other family. After `negatives_per_positive=2` sampling
and the 85/15/50/50 split, `graphics/structural_pretrain_family/
structural_pretrain_family.md` reports `test_rows` (from `analysis/
solo_family_report.py`'s own per-seed table, lines 238-247) of exactly 2 for ML and 1-2
for OSBP, with 1 positive each. A test block of 1-2 rows makes spec=0.0 a coin-flip
outcome, not evidence of a specific failure mode. But `train_spec` is ALSO reported as
`0.0000` for ML (`structural_pretrain_family.md:15`, and OSBP's train row is `n/a`,
too few rows to even report) -- the model is calling every negative training row
positive too, in-distribution, not just failing to generalize. With single-digit
positives and a handful of distinct proteins per family, and a frozen, non-
discriminative protein encoder (section 1c), there simply is not enough contrastive
signal for these two families for the classifier head to learn a boundary at all;
`analysis/solo_family_report.py:83-84` independently flags both as "carry[ing] no
readable number at all" and excludes them from every pooled figure for the same reason.

**CRAL-TRIO / IP_trans / scp2 vs START / lipocalin: not resolved by any single factor
read from code or the raw counts.** Natural positive rate does not separate them
cleanly: CRAL-TRIO 6.5%, IP_trans 6.8%, scp2 5.1% (the "bad middle" group) vs START
17.7%, lipocalin 3.1% (the "behaves well" group) -- START's rate is far higher and
lipocalin's is the lowest of ALL nine families, so "harder because rarer" does not fit
lipocalin. Row count does not separate them either: CRAL-TRIO has more rows (2547) than
START and lipocalin combined has fewer than CRAL-TRIO (lipocalin 2830 is comparable,
but CRAL-TRIO still underperforms it on specificity). `files/solo_family_report.md`'s
paired-skill table additionally shows the "START/lipocalin behave well" pattern is not
robust across the three arms: lipocalin's spec-sens gap is +0.065 (frozen,
`structural_pretrain_family`) but -0.012 (scratch) and -0.055 (unfrozen) -- i.e. it
flips sign depending on arm, well within the reported SEM (~0.03-0.06) for n=5 seeds. No
code read in this investigation (encoder architecture, sampling, splitting) treats these
seven families differently from each other beyond their raw size and composition, so a
specific mechanism (structural homogeneity, feature distinctiveness) cannot be
attributed without an additional measurement (e.g. intra-family structural/embedding
similarity) that was not run here. Stated as open rather than guessed, per instruction.

## 3. The net_AUC vs null_AUC table is a pooling artifact, not a real finding

`analysis/solo_family_report.py:234` computes the `net_AUC` column shown in
`graphics/structural_pretrain_family/structural_pretrain_family.md`'s second table as
`binary_auc(labels, scores)` -- a single AUC over ALL of a family's test rows pooled
together, comparing raw model scores across DIFFERENT proteins with no per-protein
normalization (`analysis/cross_sampler_eval.py:79-86`). `null_AUC` in the same row is
`null_within_protein_AUC`, i.e. the SAME pooling function applied to the chemistry-only
within-protein lookup's scores (`analysis/solo_family_report.py:205,219,239`) -- also
pooled, but the lookup's output is already a bounded, protein-relative similarity score,
so it is far less sensitive to between-protein scale differences than a raw network
logit/softmax score is. For GLTP seed 0 (`structural_pretrain_family.md:223`): `net_AUC
= 0.290` but `net_AUC_pairs = 1.000` on the identical 14 rows -- the paired, within-
protein-only metric (`within_protein_pair_auc`, `analysis/cross_sampler_eval.py:89-111`,
which never compares scores across a protein boundary) shows the model ranks its own
pockets' lipids perfectly; the pooled number is destroyed purely because the model's raw
score scale differs between GLTP's ~2 contributing proteins. This is exactly the
`checkpoint_scores.py:4-10` blind spot from section 1a, one level further: a fixed
threshold conflates ranking quality with calibration, and a pooled/raw AUC conflates
between-protein score-scale differences with actual discriminative signal. The paired
metric is the one both `full_label_report.py`'s methodology and `solo_family_report.py`'s
own comparison use as the actual measurement (section 4), and by that metric GLTP is
NOT underperforming the null model in any of the 5 seeds by a meaningful margin
(0.79-1.00 model vs 0.79-1.00 null, `structural_pretrain_family.md:223-227`). Conclusion:
the raw `net_AUC` column is a small-n multi-protein pooling artifact and should not be
read as "the model underperforms chemistry" -- it should not be over-interpreted.

## 4. What can the model's output legitimately be used to claim

**Unit of prediction, from the code.** The classifier consumes one (protein, lipid
candidate) row and returns `[batch, 2]` logits (`AGENTS.md`'s own invariant, confirmed
by `architecture/interaction_classification.py:396-403`'s per-row reconstruction-vs-
classification branch and by every `argmax(dim=1)` call cited in 1a). This is a
**pair-level** binary call -- "does this specific LTP bind this specific candidate
lipid" -- not a per-residue binding-site localization output; nothing in
`interaction_classification.py`'s forward path returns a score per residue for the
final classification task (the ONLY per-residue output anywhere in this pipeline is the
stage-1 reconstruction head at masked nodes, `architecture/
interaction_classification.py:403`, which is a self-supervised auxiliary target, not a
binding-site score). Consequently "binding-site classification" in the project's
framing means "which lipid(s), among candidates, does this protein bind", scored one
candidate at a time.

**What the measured numbers support.** `AUC_within_protein_pairs` -- ranking a set of
candidate lipids against each other FOR A PROTEIN ALREADY IN THE MODEL'S OWN TRAINING
DISTRIBUTION (warm split, section 5) -- is the metric with a real, though weak,
positive skill over a no-training chemistry lookup: pooled across the 7 readable
families, `files/solo_family_report.md` reports +0.030 +/- 0.024 (frozen scratch and
unfrozen arms) and +0.014 +/- 0.020 (frozen `structural_pretrain_family`), i.e. at most
~1.2 sigma above the naive Morgan-fingerprint similarity baseline computed on the
identical rows (`dataloader.chemistry_prior.null_scores_within_protein`, called from
`analysis/solo_family_report.py:205`). This supports, weakly, a claim like "within a
protein whose binding behavior the model has already trained on, the model's within-
protein lipid ranking is comparable to, and possibly marginally better than, a chemistry
similarity lookup" -- not a strong claim, and not one that generalizes to a protein the
model has not trained on (that question needs the excluded-family cold split covered by
`analysis/full_label_report.py`, an entirely different label/experiment; see the central
correction above).

**What the numbers do NOT support.** A fixed-threshold, per-row "does this protein bind
this lipid, yes or no" call: (1) section 1a/3 show the 0.5-threshold sens/spec numbers
conflate calibration with discrimination and the raw pooled AUC used to sanity-check
against a null model is itself unreliable across proteins; (2) for two families (ML,
OSBP) the model calls positive on essentially every row, including training rows
(section 2); (3) the "skill" over the naive chemistry baseline that IS measurable
(section above) is small and reaches significance in at most one or two of seven
families per arm, not project-wide. A predictor that fires on ~56% of test rows (implied
by pooled test sens 0.90 / spec 0.60 against a ~33% positive test pool, see section 1b)
while its actual candidate-ranking edge over a hand-written chemistry lookup is <=1.2
sigma is not, on this evidence, a usable "yes/no site caller" -- its legitimate, weakly-
supported use is comparative ranking of candidates for a protein the model has already
seen train.

## 5. How training actually proceeds, and what the split really is

**Stage 1 -- `structural_pretrain`** (`scripts/arg_files/structural_pretrain.md`,
`--structural_pretrain --save_model --label=structural_pretrain --ep=120 --hiddim=64
--dropout=0.1 ...`). One run, ALL nine families pooled, no `--excluded_groups` /
`--family_only` set, so `excluded_set_name` resolves to `"random"`
(`training/new_train.py:585-614`) and the split is the plain
`csvt.sample(frac=0.85, random_state=seed)` row-level 85/15 draw
(`dataloader/Dataloader.py:1461`), same code path as every other unrestricted run. Per
forward pass, `_mask_residue_features` (`dataloader/Dataloader.py:2095-2125`) zeros
`protein_mask_share=15%` of a pocket's residues' 3-dimensional geometric feature
vectors (`protein_node_feature_count`, default 3, `dataloader/
protein_graph_builder.py:311`) -- a small per-residue geometry descriptor set, separate
from the PLM/ESM3 embedding, which is passed to the encoder unmasked as its own input
(`plm` argument, `architecture/interaction_classification.py:378`). The train split's
mask is redrawn every epoch; valid/test's mask is fixed once so the reconstruction loss
used for checkpoint selection (`selection_metric_name = "loss" if conf.structural_
pretrain else "balanced_accuracy"`, `training/new_train.py:2280`) means the same thing
across epochs (`dataloader/Dataloader.py:2025-2037`). The objective is pure MSE between
`protein_recon_head`'s prediction and the true (pre-zero) values at the masked node
indices (`training/new_train.py:1429-1437`; head architecture `architecture/
interaction_classification.py:70-74`, a 2-layer MLP reading protein1's own pre-pool,
pre-cross-attention per-node output). `prot.inter` (the `Interaction` binding label) is
never read on this stage's loss path.

**Stage 2 -- 9 per-family runs**, one per `PROTEIN_GROUPS` entry
(`scripts/submit/structural_pretrain_solo.sh`), using `scripts/arg_files/
bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md`'s flags with `--double_
coldsplit` stripped (the sed at `structural_pretrain_solo.sh`, since that flag targets
an excluded-family split, the opposite of what `--family_only` does) plus `--family_
only=<family> --label=<arm_label> --seed=<0..4>`. `--pretrained_checkpoint=models/
structural_pretrain/random/seed0.pt --freeze_pretrained_encoders` loads stage 1's
protein1 weights and freezes them (`training/new_train.py:108-146`, cited in full in
section 1c) for the `structural_pretrain_family` arm specifically (the `scratch` arm
strips both flags, the `unfrozen` arm keeps the checkpoint but not the freeze,
`structural_pretrain_solo.sh`'s three `sed` derivations). **Split granularity**: the
whole table is first row-filtered to `ProteinDomain.str.lower() == family_only.lower()`
(`dataloader/Dataloader.py:147-150`), THEN split by the same plain random 85%
train / stratified-by-label 50/50 valid-test draw used everywhere without
`--excluded_groups` (`dataloader/Dataloader.py:1461`, `:1518-1533`) -- i.e. row-level,
not protein-level and not lipid-level: individual (protein, lipid) interaction rows are
assigned to train/valid/test at random within the family, so the same protein AND
often the same lipid recur across splits (`solo_family_report.py`'s own "doля липидов
теста в train" column in `files/solo_family_report.md` shows 19-77% lipid overlap
between test and train per family). Valid is drawn from the SAME family as train (there
is no held-in/held-out family distinction at all under `--family_only`); test and valid
sizes come from a 50/50 split of the 15% not sampled into train, done separately for
positive and negative labels so both carry the same positive rate by construction
(`dataloader/Dataloader.py:1518-1533`, comment: "Splitting each label in half makes
valid and test carry the same positive rate by construction"). Optimizer is plain Adam
at `conf.lr` (`training/new_train.py:453`, `torch.optim.Adam(split_lipid_branch(main_
groups), lr=conf.lr)`); neither arg file sets any LR-schedule flag, so no warmup/decay
is applied beyond whatever `conf.lr`'s single value is.

## 6. Proposed lipid cold-split design

Scope note: this section answers a design question ("how would you build the best
lipid cold split"), not a re-measurement of `structural_pretrain_family` itself. It is
read-only code analysis of `dataloader/Dataloader.py`, `dataloader/sampler.py`,
`dataloader/lipid_classes.py`, `training/read_configuration.py`, and the two existing
write-ups that already ran this experiment family, `files/
lipid_coldsplit_architecture_direction.md` (`--lipid_coldsplit` results, snapshot
2026-09-08) and `files/marginals_and_cold_split.md` (`--double_coldsplit`). No new run,
no recomputation of anything those files already answer.

**6.0 What already exists and already answers part of this.** The project already has
a working, measured lipid-only cold split: `--lipid_coldsplit=<sphingolipids|
phosphorus_free|choline|anionic>` (`training/read_configuration.py:119,1007`,
`dataloader/Dataloader.py:1351-1369`). Under it every protein stays in training and a
named set of lipid head-group classes is held out whole
(`dataloader/Dataloader.py:1454-1459`: `csvtrain = self.csvt` first, then the class
filter removes the held-out chemistry at `:1475-1477`). `files/
lipid_coldsplit_architecture_direction.md` already ran 3 full 4-set x 5-seed label
families on this split and found: the split's own `lipid prior baseline` diagnostic
(`Dataloader.py:465-501`) reads exactly 0.500/0.500/0% at test in every set it
checked (line 96-99 of that file) -- unlike the one-axis protein-only split, which
leaks 0.56-0.74 BA from a bare per-lipid lookup with no model at all (same file, lines
101-107) -- and that the pooled test metric on this split is itself mostly a
protein-identity shortcut, not a lipid-generalization signal: pooled AUC 0.568 vs
within-protein-paired AUC 0.480 on the identical rows (`lipid_coldsplit_architecture_
direction.md`, the "ПРАВИЛО" callout, lines 16-38, measured by `training/
new_train.py`'s own `within_protein_auc`). That callout is the standing rule for
reading ANY number off this split and is not re-argued here.

**6.1 Granularity: what `lipid_class_series` already holds out at, and why finer or
coarser would be worse.** `lipid_class_series` (`dataloader/lipid_classes.py:13-42`)
reads the head-group name out of `FullIdentityOfLipid`, stripping the acyl-chain
parenthesis -- e.g. "Phosphatidylcholine (34:1)" -> "Phosphatidylcholine" -- giving 34
distinct classes over 312 lipids (docstring, line 17-19: "a protein that takes PC(32:1)
takes PC(34:1) too", i.e. the claim that binding preference lives at this level is
stated as the module's own design premise, not measured here). `--lipid_coldsplit`'s
four named sets (`LIPID_COLDSPLIT_SETS`, `dataloader/sampler.py:245-286`) group
several of these 34 classes into one held-out block per set (sphingolipids: 6 classes;
anionic: 8; phosphorus_free: 16; choline: 2), chosen and justified by measured Tanimoto
isolation from what remains in train (`sampler.py:220-243` comment block, cited
verbatim in the file's own header): sphingolipids 0.458, choline 0.653, phosphorus_free
0.553, anionic 0.766 mean-best-Tanimoto-to-train. `--double_coldsplit`/`--mixed_
coldsplit` instead DERIVE the class set per held-out family via `lipid_classes_for_
holdout` (`sampler.py:292-345`), a concentration-score rule (`score = family positives
in class / (everyone else's positives there + 1)`) that grows the held-out set until it
covers `coldsplit_share` (default 0.8) of the family's own positives.

Three alternative granularities and why the code and the measured numbers argue
against each, for the "novel chemistry" question specifically:

- **Exact molecule** (finer than the current class). Rejected by the same logic
  `_report_lipid_prior_baseline`'s own docstring states as the reason a lookup can leak
  (`Dataloader.py:465-482`): a single held-out species still shares near-identical
  Tanimoto neighbours (different acyl chains, same head group) with training, so a
  per-lipid or per-structure prior would carry across almost undiminished -- worse
  leakage than the current class-level holdout, not less. Nothing in the codebase
  computes a per-molecule holdout; this is argued from the surrounding code's own
  stated premises, not measured directly.
- **Scaffold** (coarser than head-group class, e.g. "all glycerophospholipids"). Would
  merge classes the project has already found to be exactly where the interesting
  contrast sits -- `anionic`'s own set-comment says splitting it further makes
  isolation worse, not better, because "the chemistry allows" only so much separation
  once acyl chains dominate the fingerprint (`sampler.py:235-239`) -- so going the
  other way (merging distinct head groups into one scaffold-level block) would fold in
  classes with materially different biology (a phosphatidylcholine binder and a
  cardiolipin binder are different questions) under one held-out label, and would
  remove a much larger, more heterogeneous slice of train than any current set costs.
  Not measured; argued from the existing code's own stated rationale for NOT merging
  `anionic`'s components (`sampler.py:235-240`).
- **Tanimoto-similarity cluster** (data-driven, not head-group-name-driven). This is
  the one alternative the code does not implement and that is not obviously wrong:
  `LIPID_COLDSPLIT_SETS` is curated by name and only VERIFIED against Tanimoto
  isolation after the fact (via `coldsplit_share`'s own tuning story, `training/
  read_configuration.py:1008-1021`, and `analysis/coldsplit_geometry.py --sweep`,
  referenced there); nothing clusters lipids by fingerprint distance directly and holds
  out a cluster. Given `anionic`'s own comment says its poor isolation (0.766) is a
  property of the fingerprint being dominated by acyl-chain similarity across head
  groups (`sampler.py:236-239`), a Tanimoto-cluster cut might isolate better than a
  head-group-name cut precisely in cases like this one. **Open, untested**: no code
  path builds this, and nothing here measures whether it would produce chemically
  sensible clusters (a cluster driven by acyl-chain length could span several
  biologically distinct head groups, which would need its own new baseline check
  analogous to `_report_lipid_prior_baseline`).

**Conclusion on 6.1**: the current head-group-class granularity is the right level for
the stated biological premise (binding tracks head group, not exact species) and is
already tuned against Tanimoto isolation via `coldsplit_share`; a Tanimoto-cluster
alternative is plausible but unimplemented and unverified, not a clear improvement.

**6.2 "можно брать больше негативов" -- what raising `negatives_per_positive` actually
does and does not do, precisely.**

Mechanically, `negatives_per_positive` (`dataloader/Dataloader.py:423-424`, default 2)
is read by `_sample_interactions` (`Dataloader.py:1392-1447`), which runs BEFORE
`_split_interactions` (`Dataloader.py:1449`) and over the WHOLE table, not per split
(`Dataloader.py:158-169`: `_derive_lipid_class_holdout` -> `_sample_interactions` ->
concat into `self.csvt` -> `_split_interactions`). Under `--balanced_proteins` (the
`bbp` sampler family) with `--lipid_coldsplit` or `--double_coldsplit`/`--mixed_
coldsplit` active, `_sample_interactions` passes a `strata` mask -- which side of the
lipid-class cut each row is on -- into `sample_protein_balanced_negatives`
(`Dataloader.py:1403-1406`, `1420-1424`), and `_sample_group_balanced_negatives`
(`dataloader/sampler.py:50-`) then draws `min(positive_count * ratio, len(candidates))`
negatives **per (protein, stratum) cell independently** (`sampler.py:85-106`,
docstring lines 86-93: "each side of the cut is balanced per protein on its own").
Positives are never subsampled (kept whole on both sides, `sampler.py:95,100-102` and
the parallel structure in every `split_and_sample_*_interactions` wrapper). Consequence:
**raising `negatives_per_positive` scales the negative-row count of the held-out
lipid-class block (valid+test combined) proportionally, at fixed positive count**,
because that block is exactly `self.csvt.drop(csvtrain.index)` (`Dataloader.py:1479`)
taken from the same globally-sampled, ratio-scaled pool. For `--balanced_lipid_classes`
specifically the grouping key is already `(ProteinDomain, lipid_class)`
(`sampler.py:375-376`, confirmed by reading `sample_lipid_class_balanced_negatives`),
so every group already sits entirely on one side of the class cut -- no separate
`strata` argument is needed there and none is passed (`Dataloader.py:1416-1419`); this
is a consequence of the grouping key, not a gap.

What this buys, precisely:
- **More negative rows in the held-out block** -> tighter specificity estimate (larger
  n for the confusion-matrix cell), and a larger, more diverse negative pool for the
  loss to contrast against positives during training (more of "which lipids this
  protein does not bind" survives sampling, per the rationale in `read_configuration.
  py:1028-1040`'s own comment on why the project defaults to 2, not the exact-1:1 that
  `ratio=1` gives).
- **It does NOT change the held-out block's positive count** -- that is fixed by how
  many raw positive rows fall in the held-out classes, independent of `ratio`. Since
  `COLDSPLIT_MINIMUM_TEST_POSITIVES=20` (`sampler.py:289`) and `coldsplit_share`
  already gate how much of a family's own positive supply the split can draw on
  (relevant to `--double_coldsplit`, not to plain `--lipid_coldsplit`, whose 4 sets are
  fixed independent of any one family), raising `negatives_per_positive` cannot rescue
  a positive-starved held-out class the way it can pad the negative side.
- **It does NOT rebalance the loss any further, given `class_weights=True`.** This is
  the load-bearing point for section 7 below: the class-weights formula
  (`training/new_train.py:223-228`) forces the aggregate positive-class loss mass and
  aggregate negative-class loss mass to be EXACTLY equal (`class_counts.sum() / (2 *
  class_counts.clamp_min(1))`, so `count_c * weight_c = class_counts.sum() / 2` for
  every class `c` with at least one row -- exact algebraic identity, not an
  approximation), regardless of what the sampled pool's actual class ratio is. So
  changing `negatives_per_positive` from 2 to any other value changes the SIZE and
  DIVERSITY of the negative pool the model sees, but -- as long as `class_weights`
  stays on -- leaves the loss-level class balance at exactly 1:1 either way. The
  project's own comment already states this design intent directly: "The ratio is per
  group... What it does change is the class prior the loss sees, which is
  `--class_weights`' job" (`dataloader/sampler.py:65-68`). This is a documented,
  intentional two-knob separation, not an accidental double-correction: `negatives_per_
  positive` controls coverage of the negative universe; `class_weights` (when on) is
  the sole determinant of the loss-level class balance, and it fully overrides whatever
  ratio sampling produced.
- **Cost to `--double_coldsplit`'s two-axis block specifically.** The already-documented
  1.1-5.1% working-set cost (`Dataloader.py:1481-1499` comment, measured at
  `coldsplit_share=0.8`, `negatives_per_positive=2`) is a cost of DROPPED rows (rows
  whose family is held out but whose class stayed in train, or vice versa) as a share
  of the working set. Since those dropped rows come from the same per-(protein,
  stratum)-cell sampling that scales with `ratio`, the dropped row COUNT should scale
  up roughly proportionally with `negatives_per_positive` too, keeping the PERCENTAGE
  cost in a similar range -- **this proportionality is inferred from the sampling
  mechanism, not separately measured at any ratio besides 2**, and is flagged open
  rather than asserted as a verified number.

**Conclusion on 6.2**: "brать больше негативов" helps two real, distinct things for a
lipid cold split -- specificity-estimate precision on the held-out block, and negative
coverage/diversity in training -- but, contrary to the implicit worry in the question,
it does not interact with `class_weights` as a second imbalance-correction stacking on
the first: `class_weights=True` already renders the loss-level class ratio
`negatives_per_positive`-independent. It also does not touch the held-out block's
positive count.

**6.3 Fixed vs per-seed class choice, and one-axis vs two-axis.**

*Fixed vs per-seed.* Both existing mechanisms already choose classes ONCE, not per
seed: `LIPID_COLDSPLIT_SETS` (`--lipid_coldsplit`) is a hardcoded dict, independent of
`seed` entirely (`sampler.py:245-286`); `lipid_classes_for_holdout` (`--double_
coldsplit`/`--mixed_coldsplit`) is a pure function of `(csv, family, coldsplit_share)`
with no `seed` argument (`sampler.py:292-345`, signature at line 292). Only the ROW-level
draw within the fixed classes is seeded (`_sample_interactions(csv, seed)`,
`_split_interactions(seed)`, `Dataloader.py:159,169`). This is the right design to
keep, for a lipid-only axis exactly as it already is for the family axis: resampling
WHICH classes are held out per seed would confound "does the model generalize" with
"how isolated does this particular seed's held-out chemistry happen to be" -- the
Tanimoto-isolation numbers already vary 0.458-0.766 ACROSS the four fixed sets
(`sampler.py`'s own comment, cited in 6.1), so per-seed class resampling would add that
same spread as noise inside a single reported number instead of keeping it visible as
a per-set property, exactly the failure mode `files/lipid_coldsplit_architecture_
direction.md`'s own "ПРАВИЛО" callout (lines 16-38) is written to prevent for the
protein-identity axis.

*One-axis (lipid only) vs two-axis (`--double_coldsplit`, lipid + family).* These
measure two different questions by the code's own comments, not one being a
bug-fixed version of the other:
- `--lipid_coldsplit` alone: "a lipid of a chemistry never seen arrives -- which of
  the known proteins bind it" (`read_configuration.py:1002-1004`, verbatim). Every
  protein stays in train.
- `--double_coldsplit`: "neither the protein nor the lipid chemistry anywhere in
  train" (`Dataloader.py:1499`, verbatim) -- the intersection, built specifically
  because a one-axis FAMILY-only split leaves the per-lipid label prior intact (a
  held-out family's lipids have "all been seen in train paired with other proteins",
  `Dataloader.py:470-473`), which is a leak the family axis alone cannot close.

The task framing's target question -- "does the model generalize to a chemically
novel lipid **on a protein family it already knows**" -- is, by the code's own stated
intent, exactly what `--lipid_coldsplit` alone (no `--excluded_groups`, no `--double_
coldsplit`) is built to answer, and `--double_coldsplit` answers a different, strictly
harder, compound question (novel protein AND novel chemistry at once). Adding a family
holdout on top would not sharpen this question, it would change it. The lipid-only
axis is therefore sufficient on its own for the question as stated; a two-axis split is
the right tool only if the question changes to "a novel protein family AND a novel
lipid chemistry arrive together."

**6.4 Concrete recommendation.**

`--lipid_coldsplit=<sphingolipids|phosphorus_free|choline|anionic>` alone (no
`--excluded_groups`, no `--double_coldsplit`/`--mixed_coldsplit`), on top of whichever
sampler the run already uses (`--balanced_proteins --balanced_batches`, the `bbp`
family, is what the existing 3 label families in `files/lipid_coldsplit_architecture_
direction.md` used). Read results primarily off `AUC_within_protein_pairs`/`AUC_
within_protein_proteins` (`training/new_train.py`'s `within_protein_auc`,
`metrics_summary.csv` column, `analysis/compare_labels.py`'s "test AUC in-protein"
line), per that file's own standing rule (its "ПРАВИЛО" callout, lines 16-38) -- NOT
pooled BA/AUC, which that same file measured to be dominated by protein identity
(pooled 0.568 vs within-protein 0.480 on identical rows). `sphingolipids` is the most
chemically isolated of the four sets (Tanimoto 0.458 to train) and the one set where
that file found the model at or below chance in every architecture it tried before an
`--balanced_lipid_classes` sampling change (`lipid_coldsplit_architecture_direction.
md` section 0 table, row "Где модель ломается?") -- it is the hardest, most honest test
of the four, at the cost of a smaller block (66 positives, per that file's section 1
table) than `anionic`/`choline`.

Raising `--negatives_per_positive` above the default 2 (e.g. to 3) is worth trying
FOR THE PURPOSE of enlarging the held-out block's negative count and tightening the
specificity estimate's precision -- it is a real, mechanically-grounded lever for that
specific goal (section 6.2) -- but it will not, on its own, change the class-balance the
loss sees while `class_weights=True`, and it has not been run at any value other than
the project default 2 on this split (open, not measured here). Expected sample-size
cost: none on the positive side of the held-out block (fixed by the raw data); the
negative side and train pool both grow roughly proportionally with the ratio, at the
usual compute cost of a larger epoch.

## 7. Proposed class-weight fix (for the frozen-encoder `structural_pretrain` regime)

Scope note: same read-only-analysis scope as section 6, this time on `training/
new_train.py:223-228`, `training/read_configuration.py`, and `architecture/loss.py`.
Builds on, and does not contradict, section 1b/1c of this file (per-row weight ratio
~2x is one true statement about this mechanism; the exact-1:1 aggregate identity below
is a second, compatible statement about the same formula, not a revision of the first).

**7.1 The formula's exact behaviour, precisely, not approximately.**
`class_weights = class_counts.sum() / (2.0 * class_counts.clamp_min(1.0))`
(`training/new_train.py:223-227`), applied via `F.cross_entropy(loss_logits,
interaction_labels.long(), weight=class_weights)` (`new_train.py:1483`). For any class
`c` with `class_counts[c] = n_c > 0`, `weight_c = N / (2 n_c)` where `N =
class_counts.sum()`, so the class's TOTAL weighted loss mass is `n_c * weight_c = N /
2` -- **exactly the same for both classes, by algebraic construction, independent of
`n_c`'s actual value or of `negatives_per_positive`'s value** (this is the identity
cited in section 6.2). This is standard inverse-class-frequency weighting; its defining
property is exactly this exact-1:1 rebalancing, not an approximate one. So:

- **Is there double-counting between the sampler and `class_weights`?** No, not in the
  sense of two mechanisms each partially correcting the same imbalance and stacking.
  `negatives_per_positive` sets the SAMPLED pool's actual class ratio (comment,
  `sampler.py:65-68`: "raising it does not reintroduce the between-protein prior...
  What it does change is the class prior the loss sees, which is `--class_weights`'
  job"); `class_weights`, when on, THEN overrides whatever that ratio was and forces
  the loss to 1:1 regardless. The two are a documented two-knob design (coverage vs.
  loss-balance), not an accidental compounding. `negatives_per_positive` has ZERO
  effect on the loss-level class balance whenever `class_weights=True`.
- **Is a fixed 1:1 loss-balance target itself the right choice, though?** This is the
  real question, and the answer is more subtle than "on vs off". Forcing the loss to
  treat the classes as 1:1 makes the model's raw output approximate a posterior
  calibrated to a HYPOTHETICAL 50:50 world, not the actual sampled pool's ~33:67 prior
  (itself already far from the raw table's 6.9%, `read_configuration.py:1029-1033`).
  A flat 0.5 threshold on that output (section 1a of this file: every argmax call in
  `new_train.py`) does not know the output was calibrated to an artificial 50:50 prior
  rather than the pool's real one, so it reads the model's positive-class score as if
  it meant "more likely than not" under the TRUE prior when it in fact means that under
  an artificially inflated one. This is precisely the systematic bias mechanism that
  `--logit_adjustment` (Menon et al. 2020, cited in `architecture/loss.py:93`) exists
  to correct, and it is a DIFFERENT, later step than class-weighting: `logit_
  adjustment_bias` (`architecture/loss.py:92-101`) adds `tau * log(class_prior)` to the
  logits INSIDE the loss computation only (`new_train.py:1423-1427`, added to
  `loss_logits`, never to `outl`), so that the RAW logits `outl` the model is trained to
  produce are themselves already Bayes-consistent with the true (sampled-pool) prior,
  and every downstream `argmax(dim=1)` call (the same fixed 0.5 cut cited in section 1a)
  reads a properly calibrated score without needing a different threshold.
  `--logit_adjustment` is **off** in both arg files behind `structural_pretrain_family`
  (`bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md`, `structural_pretrain.md`;
  neither sets `--logit_adjustment`, confirmed by `grep` over both files), and nothing
  in `read_configuration.py`'s `validate()` forbids combining it with `class_weights`
  (no such check found by grepping `class_weights` in that file) -- but the two
  mechanisms correct the SAME miscalibration by different means (a multiplicative
  per-example loss reweighting vs. an additive per-class logit bias), and combining
  both has not been run or measured anywhere in this repository; their joint effect is
  open, not derivable from the code alone, because `class_weights=True` already forces
  the loss to be prior-agnostic (1:1 regardless of the true ratio), so adding a
  prior-restoring logit bias ON TOP of a prior-erasing reweighting does not obviously
  compose the way it would on a plain (unweighted) cross-entropy.

**7.2 Is a frozen, label-blind encoder a reason any fixed class-weight ratio is
arbitrary?** Partially, and precisely in this sense: section 1c of this file
establishes (from `training/new_train.py:108-146`, `:1429-1437`, `architecture/
interaction_classification.py:70-74`) that `protein1`'s weights are frozen after a
reconstruction objective that never reads `Interaction`, so whatever discriminative
signal the classifier learns has to come from the lipid encoder, cross-attention and
final layer alone, conditioned on a protein representation that is informative about
local geometry but not, by construction, about the label. Given that, no class-weight
RATIO can manufacture separability that is not there -- rebalancing the loss changes
WHERE the decision boundary sits on whatever score distribution the remaining trainable
parts produce, it cannot widen that distribution's separation between classes. This is
consistent with, but does not by itself prove, why an under-informative signal defaults
toward calling "positive" specifically (section 1c's "path of least loss" argument
remains the load-bearing claim for the DIRECTION of the bias, not this section).
Whether the classifier's non-frozen parts (lipid encoder, cross-attention, final layer)
carry meaningful label signal on their own is exactly the question sections 3-4 of this
file already answer with the within-protein-pair AUC (weak, <=1.2 sigma over a
chemistry-only null): so class-weight tuning here is tuning the operating point on a
weak signal, not creating one.

**7.3 Per-family class weights: already true for `--family_only`, verified from the
code, not a new recommendation.** `--family_only` filters the whole interaction table
to one `ProteinDomain` BEFORE `_derive_lipid_class_holdout`, `_sample_interactions`,
and `_split_interactions` all run (`dataloader/Dataloader.py:141-150`, comment:
"restrict the whole table to one family's rows BEFORE anything else... Must happen
before `_sample_interactions`"). `class_counts` in `new_train.py:216` is computed from
`train_dataset.csvtrain["Interaction"]` (`new_train.py:210-216`), and `train_dataset`
IS the `--family_only`-filtered dataset -- there is no code path by which a
`structural_pretrain_family` run's `class_counts` could include another family's rows.
So `class_weights` under `structural_pretrain_family` is, and already was for every one
of the 9 per-family stage-2 runs, computed purely from that one family's own train
split -- the ML-vs-CRAL-TRIO size disparity (10 vs 165 positives, section 2 of this
file) is already reflected per-run, not diluted by pooling. There is nothing to fix
here for THIS label; per-family weighting only becomes a live question for a run that
pools multiple families into one train split with `--excluded_groups`/`--double_
coldsplit` and no `--family_only` (a materially different training regime, not
`structural_pretrain_family`, and out of scope for this section).

**7.4 Threshold calibration vs. loss weighting: which lever does the real work, and
why both matter.** Restating section 1a of this file precisely in these terms: loss
weighting (class_weights, logit_adjustment, focal_loss) changes what the model is
TRAINED to output; the decision rule (`argmax(dim=1)`, i.e. a flat softmax>=0.5 cut,
`new_train.py:939,968,997,1506,1721,1850,1985`) changes how that output is READ. Fixing
`class_weights` alone (e.g. turning it off, or replacing it with `--logit_adjustment`)
changes what calibration the raw score aims for, but the project has no code anywhere
(confirmed again here: no threshold search in `new_train.py`, no calibration step in
`analysis/checkpoint_scores.py`, per section 1a) that adapts the DECISION to whatever
calibration the loss produced. So: **loss weighting is necessary to fix the CALIBRATION
of the score** (whether the raw output means "> 50% under the true prior" or "> 50%
under an artificial 1:1 prior"); **threshold calibration is necessary to fix what
OPERATING POINT is read off that score**, and these are not substitutes for each other.
A perfectly Bayes-consistent model (e.g. `class_weights=False` with `--logit_
adjustment` recovering the true sampled-pool prior) read at a flat 0.5 threshold would
report sens/spec appropriate to a "predict positive only when truly more likely than
not under the ~33:67 sampled prior" operating point -- which, given the pool's own
~33% positive rate, is a DIFFERENT, more conservative point than what any config
measured in this file's sections 0-5 currently reports, and would very likely LOWER
sensitivity and RAISE specificity relative to what `structural_pretrain_family`
reports today, simply by removing the artificial-50:50-then-flat-0.5-threshold
mismatch -- but neither the size of that shift nor whether it is the operating point a
user would actually want (vs., say, deliberately favouring sensitivity for a screening
use case) can be answered without either running it or adding an explicit
threshold-search step, neither of which exists in the codebase today. Stated as a
directional, code-grounded expectation, not a measured number.

**7.5 Concrete recommendation.** Two options, both consistent with what section 7.1-7.4
establish, and explicitly NOT a claim that either has been run:

1. **Decouple calibration from balancing: `--no_class_weights --logit_adjustment`.**
   Turns off the artificial 1:1 loss target and replaces it with the standard
   train-time Menon correction, computed from the SAME `class_counts` the sampled pool
   actually has (`architecture/loss.py:92-101`, already wired into the exact loss path
   `structural_pretrain_family` uses -- `loss_type="cross_entropy"`, confirmed in
   section 1c of this file). This is the textbook pairing (reweighting XOR logit-bias,
   not both) and is a one-flag change to the existing arg file with no new code. Still
   leaves the flat 0.5 threshold in place, but that threshold is then reading a score
   calibrated to the model's own true training-pool prior, which is the condition
   `--logit_adjustment` is designed to make safe.
2. **Leave weighting alone and add threshold calibration instead** (e.g. picking a
   decision threshold on validation, per family, rather than assuming 0.5) -- this is
   the more general fix in that it lets a chosen operating point differ from
   "Bayes-consistent with the training prior" when that is not the goal, but it
   requires new code: nothing in `new_train.py` or `analysis/checkpoint_scores.py`
   currently searches or stores a threshold (section 1a). Not proposed as a code
   change here, only named as the alternative lever, per the task's read-only scope.

Combining `class_weights=True` with `--logit_adjustment` (rather than choosing one) is
explicitly NOT recommended without a measurement first: section 7.1 shows the two
corrections target the same miscalibration by mechanisms that do not obviously compose
(a loss reweighting that already erases prior information vs. an additive bias that
tries to restore it), and no run in this repository has tried the combination.

Neither option is expected to increase the WEAK underlying signal the encoder-freezing
regime leaves available (section 7.2, and sections 3-4 of this file); both only change
where and how that signal's existing separability is read out as a sens/spec number.

## Чем посчитано / measured by

- Architecture/training claims (sections 1, 5): direct reads of `training/
  new_train.py`, `training/read_configuration.py`, `architecture/
  interaction_classification.py`, `dataloader/Dataloader.py`, `dataloader/
  protein_graph_builder.py`, `analysis/cross_sampler_eval.py`,
  `analysis/checkpoint_scores.py`, `scripts/arg_files/structural_pretrain.md`,
  `scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md`,
  `scripts/submit/structural_pretrain_solo.sh` -- all cited inline by file:line.
- Family sens/spec/BA/AUC numbers (sections 0, 2, 3): `graphics/
  structural_pretrain_family/structural_pretrain_family.md` (built by
  `analysis/summarize_label.py` and `analysis/solo_family_report.py`, not
  re-run here).
- Paired-skill / spec-sens-with-SEM numbers across all three arms (sections 2, 4):
  `files/solo_family_report.md`, itself produced by `analysis/solo_family_report.py`
  (reads only, no training -- see that script's own docstring).
- Raw per-family row/positive counts (section 2): counted directly, read-only, from
  `data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_
  CandidatesCompleted_Deduplicated.csv` grouped by `ProteinDomain` and
  `Interaction==1` -- a plain CSV scan, no project code executed.
- No model was loaded, no checkpoint scored, and no script in `analysis/` or
  `training/` was executed in the course of this diagnosis.
- Lipid cold-split design (section 6): direct reads of `dataloader/Dataloader.py`
  (`__init__`, `_configure_sampling`, `_derive_lipid_class_holdout`,
  `_sample_interactions`, `_split_interactions`, `_report_lipid_prior_baseline`),
  `dataloader/sampler.py` (`LIPID_COLDSPLIT_SETS`, `lipid_classes_for_holdout`,
  `_sample_group_balanced_negatives`, `sample_lipid_class_balanced_negatives`),
  `dataloader/lipid_classes.py` (`lipid_class_series`), and `training/
  read_configuration.py` (`lipid_coldsplit`/`double_coldsplit`/`coldsplit_share`/
  `negatives_per_positive` field comments) -- all cited inline by file:line. Prior
  measured numbers (Tanimoto isolation per set, pooled-vs-within-protein AUC, the
  `--balanced_lipid_classes` result) are taken as-is from `files/
  lipid_coldsplit_architecture_direction.md` and `files/marginals_and_cold_split.md`,
  not recomputed. No run, script, or checkpoint touched for this section.
- Class-weight fix (section 7): direct reads of `training/new_train.py:210-237,
  1423-1427,1483` (class_counts, class_weights, logit_adjustment_bias_tensor, the
  cross_entropy call, and every `argmax(dim=1)` site already cited in section 1a),
  `architecture/loss.py:92-101` (`logit_adjustment_bias`), and `training/
  read_configuration.py` (`class_weights`, `logit_adjustment`, `logit_adjustment_tau`
  fields and their `validate()` block). The exact-1:1 aggregate-mass identity in 7.1
  is an algebraic derivation from the formula at `new_train.py:223-227`, checked
  against the pre-existing design comment at `dataloader/sampler.py:65-68`; it is not
  a numeric measurement and no run was made to confirm it empirically. No run, script,
  or checkpoint touched for this section.
