# Exact sibling of deepclip_gltp_warm_ep120.md, ONE mechanism added:
# --deepclip_protein_gate. Every other flag is copied verbatim -- see that file's
# header for the family, the mirror table it is built around, and why the result
# must be read per protein rather than pooled.
#
# WHAT THE GATE DOES
#
# Published DeepCLIP turns its BLSTM states into the per-position binding profile
# with Sum_last_ax -- sum_h states[:, :, h], every channel counted exactly once,
# no parameters (network.py: DenseLayer W=Constant(1.0), b=None). This flag makes
# those weights a function of the pocket instead: the named descriptors go through
# a one-hidden-layer MLP to one weight per LSTM channel, and the profile becomes
# sum_h w_h(pocket) * states[:, :, h].
#
# Multiplicative on purpose. An additive protein term -- a protein score added to
# the lipid score, which is what a concatenation into the final layer amounts to --
# shifts both proteins the same way and cannot represent a mirror at all: GLTP and
# GLTPD1 need opposite answers on identical chemistry. A gate can, because the same
# lipid channel can be amplified for one pocket and suppressed for the other.
#
# The last gate layer is zero-initialised, so at epoch 0 the weights are exactly the
# all-ones vector published DeepCLIP uses and this run STARTS as its own control. Any
# departure is something the pocket had to earn from the gradient.
#
# WHY THESE DESCRIPTORS
#
# The discrimination this family needs is "does the mouth of this pocket accommodate
# a sugar, or a zwitterionic phosphocholine". The eleven names below are the
# family-neutral seven this project already defends, plus the four pocket-chemistry
# names the Kron-RLS exhaustive search picked out (see
# geometric_edge_mlp_..._pocketchem4.md's header for that search): basic_share_core
# and basic_share_rim carry the charge complementarity a phosphocholine needs,
# hbond_donor_share_core the donors a sugar's hydroxyls need, and pocket_free_volume
# the plain size in angstrom^3.
#
# WHAT THIS RUN CAN AND CANNOT SHOW
#
# It is a CAPACITY test, not a generalisation test, and reporting it as the latter
# would be wrong. The family has two proteins, so the gate sees exactly two distinct
# input vectors and could in principle memorise them rather than read anything
# chemical off them. What it establishes is the thing published DeepCLIP provably
# cannot do at all -- give the two proteins different answers on the same lipid. If
# it fails even here, no split will rescue it; if it succeeds, whether it succeeded
# for a chemical reason is the NEXT question and needs a family with more members.
#
# The chemistry is deliberately NOT held out. Holding out the sphingolipid block
# would leave GLTPD1 with 2 of its 29 positives in training and GLTP with 9 of 33,
# and the sugar rule has exactly one instance in the whole table (GLTP is the only
# protein binding any glycosphingolipid), so the block-holdout removes the rule
# being tested rather than testing generalisation of it.
#
# Not yet run.

--ep=120
--family_only=gltp
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

--pair_descriptors
--pocket_descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
