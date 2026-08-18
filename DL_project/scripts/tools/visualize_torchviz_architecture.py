#!/usr/bin/env python3
"""Render a TorchViz forward graph for the active interaction model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

# parents[2]: this file sits in scripts/tools/, so the project root is two levels up.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from architecture.interaction_classification import InteractionClassification
from training.read_configuration import read_named_configuration


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Build InteractionClassification on a tiny synthetic batch and "
            "render its autograd graph through torchviz."
        )
    )
    parser.add_argument(
        "--output",
        default="graphics/architecture_torchviz/model_forward",
        help="Output path without extension.",
    )
    parser.add_argument(
        "--format",
        default="pdf",
        help="Graphviz render format, for example pdf, svg, or png.",
    )
    parser.add_argument(
        "--full_dims",
        action="store_true",
        help="Keep ModelConfig default dimensions unless overridden.",
    )
    parser.add_argument(
        "--show_attrs",
        action="store_true",
        help="Pass show_attrs=True to torchviz.make_dot.",
    )
    parser.add_argument(
        "--show_saved",
        action="store_true",
        help="Pass show_saved=True to torchviz.make_dot.",
    )
    return parser.parse_known_args()


def _option_was_passed(model_args, name):
    return any(argument == name or argument.startswith(name + "=") for argument in model_args)


def build_config(model_args, full_dims):
    config = read_named_configuration(["visualize_torchviz_architecture.py"] + model_args)

    if not full_dims:
        if not _option_was_passed(model_args, "--hiddim"):
            config.hiddim = 8
        if not _option_was_passed(model_args, "--HEADS"):
            config.HEADS = 2
        if not _option_was_passed(model_args, "--m"):
            config.m = 2
        if config.final_m is None:
            config.final_m = config.m

    config.batch = 2
    config.num_workers = 0
    config.validate()
    return config


def synthetic_forward_args(config):
    torch.manual_seed(config.seed)

    prot = torch.randn(4, 3)
    plm = torch.randn(4, 1536)
    bury = torch.randn(4)
    prot_batch = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    prot_edge_index = torch.tensor(
        [[0, 1, 2, 3], [1, 0, 3, 2]],
        dtype=torch.long,
    )
    prot_edge_attr = torch.randn(4, 3)
    lip_batch = torch.tensor([0, 0, 1, 1], dtype=torch.long)

    args = {
        "config": config,
        "plm": plm,
        "bury": bury,
        "prot": prot,
        "prot_edgidx": prot_edge_index,
        "prot_e_attr": prot_edge_attr,
        "prot_batch": prot_batch,
        "lip_batch": lip_batch,
    }

    if config.lipid_isomers:
        args["lip"] = torch.randn(4, 11)
        args["lip_edgidx"] = torch.tensor(
            [[0, 1, 2, 3], [1, 0, 3, 2]],
            dtype=torch.long,
        )
        args["lip_e_attr"] = torch.randn(4, 6)
    else:
        args["lip"] = torch.randn(4, 768)

    if config.lipid_fragments_mask:
        args["lipid_batch"] = torch.tensor([0, 0, 1, 1], dtype=torch.long)

    if config.prot_attention_pos_bias or config.prot_pooling_by_pockets:
        args["pocket_mask"] = torch.tensor([True, False, True, False])

    return args


def main():
    args, model_args = parse_args()

    try:
        from torchviz import make_dot
    except ImportError as exc:
        raise SystemExit(
            "torchviz is not installed. Install Python dependencies with:\n"
            "  pip install torchviz graphviz\n"
            "Also make sure the system Graphviz executable 'dot' is available."
        ) from exc

    config = build_config(model_args, args.full_dims)
    model = InteractionClassification(config)
    model.eval()

    logits = model(**synthetic_forward_args(config))

    dot = make_dot(
        logits,
        params=dict(model.named_parameters()),
        show_attrs=args.show_attrs,
        show_saved=args.show_saved,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dot.render(args.output, format=args.format, cleanup=True)
    print(f"Rendered {args.output}.{args.format}")


if __name__ == "__main__":
    main()
