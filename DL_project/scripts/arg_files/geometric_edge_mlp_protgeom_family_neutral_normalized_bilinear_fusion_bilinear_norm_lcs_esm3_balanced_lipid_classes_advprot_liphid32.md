# --lipid_hiddim=32 again, but over ..._advprot instead of over the plain baseline.
#
# Why re-run something already measured flat. It was measured flat
# (files/lipid_coldsplit_architecture_direction.md section 7k: +0.003 to +0.013, all
# under 0.4 combined SEM) on a configuration whose reported number was the PROTEIN
# MARGINAL -- pooled AUC 0.568 against 0.480 within protein. On that configuration an
# improvement in the pair term had nowhere to show: the metric could not see it. So
# section 7m's "seven representation changes, nothing" is sound as "representation does
# not rescue a model riding the marginal", and is NOT evidence that representation does
# not matter.
#
# --adversarial_grl --no_adv_lipid is the first configuration where the within-protein
# number is off the floor (choline 0.622 on 11 blocks, phosphorus_free 0.618 on 8 by the
# pair-pooled metric), i.e. the first one where a pair-term improvement is observable at
# all. Widening the LIPID tower -- the only branch this split actually holds out -- is
# the representation lever with the clearest mechanism, so it is the one worth asking
# again under a metric that can answer.
#
# advprot rather than rankprot as the base: it carries AUC_within_protein_pairs (rankprot
# started before that column existed) and gives the larger choline gain.
#
# If this is flat too, section 7m's conclusion is restored honestly, on a metric able to
# see an effect -- which is a stronger negative than the one it currently rests on.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
--lipid_hiddim=32
