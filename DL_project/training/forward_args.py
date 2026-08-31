"""The keyword arguments InteractionClassification.forward takes for one batch.

Which tensors the model wants depends on the configuration -- geometric frames only under
``geometric_transformer``, incident-edge features only under
``rnabang_frozen_node_adapter``, and so on -- so assembling them is a dozen conditional
lines. Those lines used to be written out three times: the training loop, the validation
loop, and ``scripts/profile_training.py``, whose copy carried the comment "mirrors
new_train.py".

It stopped mirroring. The profiler's copy never grew the geometric / frozen-adapter
branches, so profiling any run that used them died in the encoder with
"rnabang_frozen_node_adapter requires precomputed node features" -- a failure that looks
like a broken config and is really a stale duplicate. Hence one function, called from all
three places: a config option added here reaches training, validation and profiling at
once, or fails in all three at once, which is the honest outcome.
"""

from dataloader.pair_descriptors import full_catalog_order


def build_forward_args(config, prot, lipid):
    """Model kwargs for one protein/lipid batch under this configuration."""
    forward_args = dict(
        config=config,
        plm=prot.plm,
        bury=prot.bury,
        prot=prot.x,
        prot_edgidx=prot.edge_index,
        prot_e_attr=prot.edge_attr,
        prot_batch=prot.batch,
        lip=lipid.x,
        lip_batch=lipid.batch,
    )
    if config.lipid_fragments_mask:
        forward_args["lipid_batch"] = lipid.lipid_batch
    if getattr(config, "lipid_graph_isomers", False):
        forward_args["lip_edgidx"] = lipid.edge_index
        forward_args["lip_e_attr"] = lipid.edge_attr
        if getattr(config, "cross_attention_chain_bias", False):
            forward_args["chain_rank"] = lipid.chain_rank
    if (
        config.prot_attention_pos_bias
        or config.prot_pooling_by_pockets
        or getattr(config, "pocket_attention_self", False)
        or getattr(config, "pocket_attention_cross", False)
    ):
        forward_args["pocket_mask"] = prot.pocket
    if getattr(config, "pocket_descriptors", False):
        forward_args["pocket_descriptor"] = prot.pocket_descriptor
    if getattr(config, "use_esm3_v2_embeddings", False):
        forward_args["node_confidence"] = getattr(prot, "node_confidence", None)
    if (
        getattr(config, "geometric_transformer", False)
        or getattr(config, "protein_edge_attention", False)
        or getattr(config, "protein_edge_mlp", False)
    ):
        forward_args["prot_frame_rotation"] = prot.frame_rotation
        forward_args["prot_frame_translation"] = prot.frame_translation
    if (
        getattr(config, "geometric_transformer", False)
        or getattr(config, "rnabang_frozen_node_adapter", False)
    ):
        forward_args["prot_geometric_node_attr"] = prot.geometric_node_attr
    if getattr(config, "rnabang_frozen_node_adapter", False):
        forward_args["prot_edge_node_pairs"] = getattr(
            prot, "edge_node_pairs", None
        )
        forward_args["prot_edge_node_degree"] = prot.edge_node_degree
    if getattr(config, "chem_prior", False) or getattr(config, "pocket_compat_prior", False):
        forward_args["frozen_prior"] = prot.frozen_prior
    if (
        getattr(config, "compatibility_input", False)
        or getattr(config, "compatibility_split_input", False)
    ):
        forward_args["compat_input"] = prot.compat_input
    if getattr(config, "pair_descriptors", False):
        forward_args["pair_descriptor_input"] = prot.pair_descriptor_input
    if full_catalog_order(config):
        # Covers --two_pair_descriptors_paths, --descriptor_names (under
        # descriptors_head or pair_descriptors), and --protein_descriptors/
        # --lipid_descriptors -- one shared predicate instead of re-deriving the same
        # boolean here a third time (dataloader/Dataloader.py's named_catalog_on is the
        # other).
        forward_args["descriptor_catalog_input"] = prot.descriptor_catalog_input
    return forward_args
