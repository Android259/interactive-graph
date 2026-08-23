Isolates the lipid candidate treatment.

Identical to bbp_dcs_rnd_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 except for the two
flags at the bottom: this one encodes a row with the FIRST member of its candidate set,
fixed for the whole run, where the rnd variant draws one candidate afresh at every
presentation.

Why it exists. The rnd runs were compared against runs from 2026-08-19, and three things
had changed between them at once: the candidate treatment, coldsplit_share (0.70 ->
0.80), and the interaction table itself (the deduplicated file removed 98 duplicate
positive rows over 92 repeatedly measured cells). Nothing in that comparison isolates the
candidate treatment. This variant runs the OLD treatment under the CURRENT share and the
CURRENT table, so the difference against the rnd runs is the treatment alone.

Read it against bbp_dcs_rnd_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120 on the same seven
families and seeds 0 and 1, with analysis/rnd_candidates_vs_first_candidate.py.

--ep=120
--protein_disable_post_sa_mlp
--lipid_disable_post_sa_mlp
--fast_attention

--hiddim=8
--plm_compression_dim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="gem"

--balanced_batches
--balanced_proteins
--double_coldsplit

--save_model_in_dynamics

--lipid_fragments_treatment=concat
--lipid_first_fragment_only
