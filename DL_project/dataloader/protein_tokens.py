"""Encode pocket residues for --deepclip_protein_tokens.

One token per pocket residue in chain order, with up to two 20-letter alphabets:
aa: residue_type from coarse_graph_nodes.csv, in RESIDUE_LETTERS order;
3di: data/protein_3di.csv, built by preprocessing/build_foldseek_3di.py.
This is the protein counterpart of smiles_tokens.py.

A break flag is 1 when the preceding pocket residue is not a chain neighbor.
Across 35 proteins, pockets have a median 33 residues and 28 breaks.
A channel avoids nearly doubling sequence length with gap tokens, which would
leave width-4..8 windows seeing only 2-4 residues.

As in ProteinGraphBuilder.protein_graph_tensors, a residue is in the pocket
when any side-chain atom has B-factor 1 in pocketness.pdb.
Match (chain, resSeq, iCode), not positions. This handles RBP4's trailing lone
N atom, absent from its graph, without a special case. Missing node IDs raise.

Store integer [residues, 3] long tensors: aa code, 3Di code, break flag.
deepclip.py expands the requested alphabets. Padding is -1 in all columns.
"""

import os

import pandas
import torch

from preprocessing.compute_descriptors import POCKET_BACKBONE_ATOMS, RESIDUE_LETTERS


PROTEIN_TOKEN_ALPHABETS = ("aa", "3di")

# Foldseek uses 20 amino-acid letters for 3Di states. This order defines
# one-hot columns, as SMILES_VOCABULARY does.
THREE_DI_VOCABULARY = RESIDUE_LETTERS
THREE_DI_INDEX = {letter: code for code, letter in enumerate(THREE_DI_VOCABULARY)}

THREE_DI_FILE = "protein_3di.csv"
PROTEIN_TOKEN_COLUMNS = 3
PADDING_CODE = -1


def parse_protein_token_alphabets(value):
    """--deepclip_protein_tokens as a tuple of alphabet names, in the order given."""
    if not value:
        return ()
    names = tuple(part.strip() for part in str(value).split(",") if part.strip())
    unknown = [name for name in names if name not in PROTEIN_TOKEN_ALPHABETS]
    if unknown:
        raise ValueError(
            f"deepclip_protein_tokens: unknown alphabet(s) {unknown}; choose from "
            f"{PROTEIN_TOKEN_ALPHABETS}"
        )
    if len(set(names)) != len(names):
        raise ValueError(f"deepclip_protein_tokens names an alphabet twice: {names}")
    return names


def protein_token_width(alphabets):
    """One-hot width the model builds: 20 per alphabet, plus the break channel."""
    return len(RESIDUE_LETTERS) * len(alphabets) + 1


def pocket_flags(pocketness_path):
    """{(chain, resSeq, iCode): is_pocket} over the residues pocketness.pdb lists."""
    flags = {}
    with open(pocketness_path) as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            key = (line[21].strip(), line[22:26].strip(), line[26].strip())
            flags.setdefault(key, False)
            if line[12:16].strip() in POCKET_BACKBONE_ATOMS:
                continue
            if line[62] == "1":
                flags[key] = True
    return flags


def pocket_token_codes(graph_dir, three_di=None):
    """[pocket residues, 3] long: aa code, 3Di code (-1 without `three_di`), break.

    `three_di` is the protein's whole 3Di string, one letter per node of
    coarse_graph_nodes.csv in node order.
    """
    nodes = pandas.read_csv(os.path.join(graph_dir, "coarse_graph_nodes.csv"))
    flags = pocket_flags(os.path.join(graph_dir, "pocketness.pdb"))
    if three_di is not None and len(three_di) != len(nodes):
        raise ValueError(
            f"{graph_dir}: {len(three_di)} 3Di letters for {len(nodes)} graph nodes -- "
            "rebuild data/protein_3di.csv (preprocessing/build_foldseek_3di.py)"
        )
    rows = []
    previous = None
    for position, node in enumerate(nodes.itertuples(index=False)):
        icode = "" if str(node.ID_iCode) == "." else str(node.ID_iCode)
        key = (str(node.ID_chainID), str(node.ID_resSeq), icode)
        if key not in flags:
            raise KeyError(f"{graph_dir}: node {key} is not in pocketness.pdb")
        if not flags[key]:
            continue
        chain, sequence_number = key[0], int(node.ID_resSeq)
        # Neighbors share a chain and consecutive residue numbers; insertion codes
        # also count as adjacent residues.
        adjacent = previous is not None and previous[0] == chain and (
            sequence_number - previous[1] in (0, 1)
        )
        three_di_code = PADDING_CODE
        if three_di is not None:
            letter = three_di[position]
            if letter not in THREE_DI_INDEX:
                raise ValueError(f"{graph_dir}: 3Di letter {letter!r} at node {position}")
            three_di_code = THREE_DI_INDEX[letter]
        rows.append((int(node.residue_type), three_di_code, 0 if adjacent else 1))
        previous = (chain, sequence_number)
    if not rows:
        raise ValueError(f"{graph_dir}: pocketness.pdb marks no residue as pocket")
    return torch.tensor(rows, dtype=torch.long)


def load_three_di(root_dir):
    """{LTPProtein: 3Di string} from data/protein_3di.csv."""
    path = os.path.join(root_dir, THREE_DI_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} is required by --deepclip_protein_tokens=...3di; build it with "
            "preprocessing/build_foldseek_3di.py"
        )
    table = pandas.read_csv(path)
    return dict(zip(table["LTPProtein"].astype(str), table["three_di"].astype(str)))


def build_protein_token_table(root_dir, proteins, alphabets):
    """Return protein-to-codes [1, longest, 3] and protein-to-length [1] maps.

    Use long tensors and -1 padding to the longest requested pocket.
    Equal shapes allow PyG and the preassembled loader to stack samples.
    """
    three_di = load_three_di(root_dir) if "3di" in alphabets else {}
    codes = {}
    for protein in proteins:
        if "3di" in alphabets and protein not in three_di:
            raise KeyError(f"{protein} has no row in {THREE_DI_FILE}")
        codes[protein] = pocket_token_codes(
            os.path.join(root_dir, "graphs", protein), three_di.get(protein)
        )
    longest = max(len(value) for value in codes.values())
    tokens, lengths = {}, {}
    for protein, value in codes.items():
        padded = torch.full((1, longest, PROTEIN_TOKEN_COLUMNS), PADDING_CODE, dtype=torch.long)
        padded[0, : len(value)] = value
        tokens[protein] = padded
        lengths[protein] = torch.tensor([len(value)], dtype=torch.long)
    return tokens, lengths


def protein_token_one_hot(codes, alphabets):
    """Convert [batch, longest, 3] codes to [batch, longest, protein_token_width].

    Return float values, with zero padding as in SMILES one-hot encoding.
    """
    valid = codes[..., 0] >= 0
    channels = []
    for alphabet in alphabets:
        column = 0 if alphabet == "aa" else 1
        channels.append(torch.nn.functional.one_hot(
            codes[..., column].clamp(min=0), len(RESIDUE_LETTERS)
        ))
    channels.append(codes[..., 2:3].clamp(min=0))
    return torch.cat(channels, dim=-1).float() * valid.unsqueeze(-1)
