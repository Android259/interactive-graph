# Same flags as scripts/arg_files/bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64.md
# with the exact two edits scripts/submit/structural_pretrain_solo.sh's "unfrozen" arm
# applies (--double_coldsplit stripped, --freeze_pretrained_encoders stripped,
# --pretrained_checkpoint kept -- weights load but train), plus one new one:
#   --protein_descriptors= : the 14-name protunion14 union (protbind6's 13 + protgeom8's
#     pocket_extent) via DESCRIPTOR_CATALOG, broadcast onto every protein-graph node.
#
# Points at models/structural_pretrain_protunion14/random/seed0.pt, NOT the original
# models/structural_pretrain/random/seed0.pt -- that one was trained with no
# --protein_descriptors= at all, so its protein1 encoder's first-layer projections
# (q_proj/k_proj/v_proj) are shaped for a narrower per-node input; loading it here
# fails with a PyTorch size mismatch of exactly 14 (confirmed by running it: 68->82,
# 93->107). scripts/arg_files/structural_pretrain_protunion14.md is the matching
# stage-1 config (same encoder flags, same --protein_descriptors=, different --label
# so it writes its own checkpoint) -- run scripts/submit/structural_pretrain_
# protunion14_solo.sh once and let it drain BEFORE this file, or every job here will
# hit the same size-mismatch crash this comment exists to explain.
#
# No --protein_hiddim here: tried once, also breaks checkpoint loading (a second,
# independent shape mismatch on top of the descriptor one) since stage 1 never varies
# it either. Both stage 1 and stage 2 stay at the checkpoint's native width 64
# throughout -- --pretrained-and-unfrozen is the fixed point, not a width sweep.
#
# Launchable via scripts/run_bigfoot.sh structural_pretrain_family_unfrozen_protunion14
# like any other config: bare --family_only below (added to scripts/launch/
# submit_grid.sh this session) switches the grid to the per-family-warm-split axis --
# one job per (PROTEIN_GROUPS family, seed), --family_only=<family> appended per job,
# --groups/--no_groups/--seeds/--summarize/--graphics all work the same as every other
# axis.
#
# --summarize's null-model section (full_label_report.py) reconstructs an EXCLUDED-
# family split and is the wrong script for a --family_only warm split (files/
# structural_pretrain_family_diagnosis.md's "central correction") -- expect that
# section empty/wrong for this label; SKIP_AUC=1 avoids wasting the forward-pass time
# computing it. The Overall/BA/gap sections (summarize_label.py) are unaffected.
#
# Not yet run -- waiting on structural_pretrain_protunion14_solo.sh's checkpoint.

--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--third_layers_in_mlps
--fast_attention

--hiddim=64
--plm_compression_dim=64

--dropout=0.1
--weight_decay=0.001
--pool_type="gem"

--balanced_batches
--balanced_proteins
--family_only

--protein_edge_attention

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--pretrained_checkpoint=models/structural_pretrain_protunion14/random/seed0.pt
--save_model
