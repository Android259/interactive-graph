"""The protein's pocket as a DeepCLIP-style token sequence (--deepclip_protein_tokens).

The protein-side counterpart of dataloader/smiles_tokens.py: one token per pocket
residue, in chain order, each read in up to two 20-letter alphabets --

    aa    the amino acid (coarse_graph_nodes.csv's residue_type, RESIDUE_LETTERS order)
    3di   Foldseek's structural letter for the residue (data/protein_3di.csv, built by
          preprocessing/build_foldseek_3di.py)

-- plus one BREAK flag per token: 1 when the residue is not the chain neighbour of
the pocket residue before it. A pocket is mostly scattered residues (median 33
residues with 28 chain breaks between them over the 35 proteins), so a break is a
channel, not a token of its own: a separate gap character would nearly double every
sequence and leave a width-4..8 window seeing two to four residues.

Pocket membership is read the way ProteinGraphBuilder.protein_graph_tensors reads it
-- a residue is pocket when any of its side-chain atoms carries the 1 flag in
pocketness.pdb's B-factor column -- but matched to the node table by (chain, resSeq,
iCode) rather than by position. The positional parse needs a special case for RBP4,
whose pocketness.pdb ends with a lone N atom of a residue the graph does not have;
matching by identity needs none, and raises on any node the file does not describe.

Tokens are stored as integer codes, not one-hot: [residues, 3] long per protein --
aa code, 3Di code, break flag. architecture/deepclip.py expands the alphabets the run
asked for. A padded row is -1 in all three columns.
"""

import os

import pandas
import torch

from dataloader.protein_graph_builder import POCKET_BACKBONE_ATOMS, RESIDUE_LETTERS


PROTEIN_TOKEN_ALPHABETS = ("aa", "3di")

# Foldseek writes 3Di states with the 20 amino-acid letters. This order fixes which
# one-hot column each state owns -- a schema, like SMILES_VOCABULARY.
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
        # Chain neighbour = same chain, next residue number. An insertion code is a
        # residue squeezed in between two numbers, so it counts as adjacent.
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
    """{protein: [1, longest, 3] long, padded with -1}, and {protein: [1] long length}.

    Padded to the longest pocket among `proteins` -- every sample of the run then has
    the same shape, which is what lets PyG and the preassembled loader stack them.
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
    """[batch, longest, 3] codes -> [batch, longest, protein_token_width] float.

    Padded positions come out all-zero, the same "no character" a SMILES one-hot has
    past the end of a molecule.
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
