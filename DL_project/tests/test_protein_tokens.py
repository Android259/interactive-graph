import types

import pytest
import torch
import torch.nn.functional as F

from architecture.deepclip import DeepCLIP
from dataloader.protein_tokens import (
    PADDING_CODE,
    THREE_DI_INDEX,
    build_protein_token_table,
    parse_protein_token_alphabets,
    pocket_token_codes,
    protein_token_one_hot,
    protein_token_width,
)
from dataloader.smiles_tokens import SMILES_VOCABULARY
from training.forward_args import build_forward_args
from training.read_configuration import ModelConfig, read_named_configuration

NODE_HEADER = "ID_chainID,ID_resSeq,ID_iCode,residue_type\n"


def _pdb_line(serial, atom, residue, sequence_number, icode, pocket):
    """One ATOM record with the pocket flag at column 63, as pocketness.pdb has it."""
    return (
        f"ATOM  {serial:5d} {atom:<4} {residue} A{sequence_number:4d}{icode:1}   "
        f"{0.0:8.3f}{0.0:8.3f}{0.0:8.3f}{1.0:6.2f}{float(pocket):6.2f}           C  \n"
    )


def _write_protein(directory, residues):
    """residues: (resSeq, iCode, residue_type, side_chain_pocket, backbone_pocket)."""
    directory.mkdir(parents=True)
    nodes = NODE_HEADER
    lines = []
    serial = 1
    for sequence_number, icode, residue_type, side_chain, backbone in residues:
        nodes += f"A,{sequence_number},{icode or '.'},{residue_type}\n"
        lines.append(_pdb_line(serial, "CA", "ALA", sequence_number, icode, backbone))
        lines.append(_pdb_line(serial + 1, "CG", "ALA", sequence_number, icode, side_chain))
        serial += 2
    (directory / "coarse_graph_nodes.csv").write_text(nodes)
    (directory / "pocketness.pdb").write_text("".join(lines))


def test_pocket_residues_in_chain_order_with_break_flags(tmp_path):
    _write_protein(tmp_path / "P", [
        (10, "", 0, True, False),   # pocket, first -> break
        (11, "", 1, True, False),   # chain neighbour -> no break
        (12, "", 2, False, True),   # backbone-only flag is not pocket
        (13, "", 3, True, False),   # 11 -> 13 skips a residue -> break
        (13, "A", 4, True, False),  # insertion code: adjacent
        (20, "", 5, False, False),
    ])

    codes = pocket_token_codes(str(tmp_path / "P"), three_di="ACDEFG")

    assert codes[:, 0].tolist() == [0, 1, 3, 4]
    assert codes[:, 1].tolist() == [THREE_DI_INDEX[c] for c in "ACEF"]
    assert codes[:, 2].tolist() == [1, 0, 1, 0]


def test_codes_without_three_di_leave_that_column_padded(tmp_path):
    _write_protein(tmp_path / "P", [(1, "", 7, True, False)])

    codes = pocket_token_codes(str(tmp_path / "P"))

    assert codes.tolist() == [[7, PADDING_CODE, 1]]


def test_three_di_of_the_wrong_length_is_refused(tmp_path):
    _write_protein(tmp_path / "P", [(1, "", 7, True, False), (2, "", 8, True, False)])

    with pytest.raises(ValueError, match="3Di letters for 2 graph nodes"):
        pocket_token_codes(str(tmp_path / "P"), three_di="A")


def test_node_missing_from_pocketness_is_reported(tmp_path):
    _write_protein(tmp_path / "P", [(1, "", 7, True, False)])
    with open(tmp_path / "P" / "coarse_graph_nodes.csv", "a") as handle:
        handle.write("A,2,.,8\n")

    with pytest.raises(KeyError, match="not in pocketness.pdb"):
        pocket_token_codes(str(tmp_path / "P"))


def test_table_pads_every_protein_to_the_longest_pocket(tmp_path):
    _write_protein(tmp_path / "graphs" / "A", [(1, "", 0, True, False)])
    _write_protein(tmp_path / "graphs" / "B", [
        (1, "", 1, True, False), (2, "", 2, True, False), (5, "", 3, True, False),
    ])
    (tmp_path / "protein_3di.csv").write_text(
        "LTPProtein,residues,aa,three_di,foldseek_version\n"
        "A,1,A,W,x\nB,3,RND,YVA,x\n"
    )

    tokens, lengths = build_protein_token_table(str(tmp_path), ["A", "B"], ("aa", "3di"))

    assert tokens["A"].shape == tokens["B"].shape == (1, 3, 3)
    assert tokens["A"][0, 1:].eq(PADDING_CODE).all()
    assert lengths["A"].tolist() == [1] and lengths["B"].tolist() == [3]
    assert tokens["B"][0, :, 2].tolist() == [1, 0, 1]


def test_one_hot_width_and_padding():
    codes = torch.tensor([[[3, 5, 1], [4, 6, 0], [PADDING_CODE] * 3]])

    both = protein_token_one_hot(codes, ("aa", "3di"))
    structure = protein_token_one_hot(codes, ("3di",))

    assert both.shape == (1, 3, protein_token_width(("aa", "3di"))) == (1, 3, 41)
    assert structure.shape == (1, 3, 21)
    assert both[0, 0].nonzero().flatten().tolist() == [3, 20 + 5, 40]
    assert both[0, 1].nonzero().flatten().tolist() == [4, 20 + 6]
    assert structure[0, 0].nonzero().flatten().tolist() == [5, 20]
    assert both[0, 2].eq(0).all()


def test_alphabet_parsing():
    assert parse_protein_token_alphabets("") == ()
    assert parse_protein_token_alphabets("3di, aa") == ("3di", "aa")
    with pytest.raises(ValueError, match="unknown alphabet"):
        parse_protein_token_alphabets("dssp")
    with pytest.raises(ValueError, match="twice"):
        parse_protein_token_alphabets("aa,aa")


def _config(**overrides):
    config = ModelConfig(deepclip=True, lipid_smiles_tokens=True)
    for key, value in overrides.items():
        setattr(config, key, value)
    config.validate()
    return config


def test_flag_is_parsed_and_validated():
    config = read_named_configuration([
        "train.py", "--deepclip", "--lipid_smiles_tokens",
        "--deepclip_protein_tokens=aa,3di",
    ])
    assert config.deepclip_protein_tokens == "aa,3di"

    with pytest.raises(ValueError, match="add --deepclip"):
        ModelConfig(deepclip_protein_tokens="aa").validate()
    with pytest.raises(ValueError, match="unknown alphabet"):
        _config(deepclip_protein_tokens="dssp")
    with pytest.raises(ValueError, match="pick one"):
        _config(deepclip_protein_tokens="aa", deepclip_profile_weights=True)
    _config(deepclip_protein_tokens="3di", deepclip_gate_weight_decay=1e-3)


def _lipid(lengths, seed=0):
    torch.manual_seed(seed)
    total = sum(lengths)
    rows = torch.zeros(total, len(SMILES_VOCABULARY))
    rows[torch.arange(total), torch.randint(0, len(SMILES_VOCABULARY), (total,))] = 1.0
    batch = torch.repeat_interleave(torch.arange(len(lengths)), torch.tensor(lengths))
    return rows, batch


def _pockets(lengths, longest=9, seed=0):
    generator = torch.Generator().manual_seed(seed)
    codes = torch.full((len(lengths), longest, 3), PADDING_CODE, dtype=torch.long)
    for row, length in enumerate(lengths):
        codes[row, :length, 0] = torch.randint(0, 20, (length,), generator=generator)
        codes[row, :length, 1] = torch.randint(0, 20, (length,), generator=generator)
        codes[row, :length, 2] = torch.randint(0, 2, (length,), generator=generator)
    return codes, torch.tensor(lengths, dtype=torch.long)


def test_tower_starts_as_published_deepclip():
    """Zero-initialised gate: same logits as DeepCLIP without any protein input."""
    rows, batch = _lipid([7, 5, 9])
    codes, counts = _pockets([4, 9, 2])
    torch.manual_seed(0)
    plain = DeepCLIP(_config()).eval()
    torch.manual_seed(0)
    tokens = DeepCLIP(_config(deepclip_protein_tokens="aa,3di")).eval()

    assert torch.equal(
        tokens(rows, batch, protein_tokens=codes, protein_token_count=counts),
        plain(rows, batch),
    )


def test_padding_up_to_the_longest_pocket_changes_nothing():
    """A pocket scores the same whatever length the run pads it to."""
    torch.manual_seed(0)
    model = DeepCLIP(_config(deepclip_protein_tokens="aa,3di", deepclip_conv_init="normal"))
    codes, counts = _pockets([4, 6], longest=6)
    wider = torch.full((2, 11, 3), PADDING_CODE, dtype=torch.long)
    wider[:, :6] = codes

    assert torch.allclose(
        model.protein_summary(codes, counts), model.protein_summary(wider, counts),
        atol=1e-6,
    )


def test_tower_is_reached_once_the_gate_moves():
    """Step one trains only the gate's zero last layer; from step two the tower learns."""
    config = _config(deepclip_protein_tokens="3di")
    torch.manual_seed(0)
    model = DeepCLIP(config)
    rows, batch = _lipid([6, 4, 8, 5])
    codes, counts = _pockets([3, 7, 5, 2])
    labels = torch.tensor([0, 1, 1, 0])
    optimizer = torch.optim.SGD(model.parameters(), lr=0.5)

    for _ in range(2):
        optimizer.zero_grad()
        out = model(rows, batch, protein_tokens=codes, protein_token_count=counts)
        F.cross_entropy(out, labels).backward()
        grads = {name: p.grad for name, p in model.named_parameters()}
        optimizer.step()

    assert all(grad is not None for grad in grads.values())
    assert any(
        grad.abs().sum() > 0 for name, grad in grads.items() if name.startswith("protein_")
    )


def test_forward_args_pass_the_tokens_through():
    config = _config(deepclip_protein_tokens="aa")
    codes, counts = _pockets([2, 3])
    prot = types.SimpleNamespace(protein_tokens=codes, protein_token_count=counts)
    lipid = types.SimpleNamespace(
        x=torch.zeros(5, 3), batch=None, lengths=torch.tensor([2, 3]), mask=None
    )

    args = build_forward_args(config, prot, lipid)

    assert args["protein_tokens"] is codes
    assert args["protein_token_count"] is counts


def test_preassembled_loader_stacks_the_tokens_like_pyg():
    import torch_geometric
    from torch_geometric.data import Data

    from dataloader.preassembled_loader import PreassembledLoader
    from dataloader.graphs_builders.protein_graph_builder import ProteinGraphData

    codes, counts = _pockets([2, 5, 3, 4, 1, 5, 2], longest=5)

    class Samples:
        _sample_cache_enabled = True

        def __init__(self):
            self.samples = []
            for row in range(len(counts)):
                protein = ProteinGraphData(
                    inter=torch.tensor(row % 2), family=torch.zeros(9)
                )
                protein.protein_tokens = codes[row: row + 1]
                protein.protein_token_count = counts[row: row + 1]
                x = torch.zeros(row + 2, len(SMILES_VOCABULARY))
                x[:, 0] = 1.0
                self.samples.append((protein, Data(x=x)))

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, idx):
            return self.samples[idx]

    def loader():
        return torch_geometric.loader.DataLoader(
            Samples(), batch_size=3, shuffle=True,
            generator=torch.Generator().manual_seed(7),
        )

    reference = list(loader())
    fast = list(PreassembledLoader(loader(), torch.device("cpu")))
    assert len(fast) == len(reference)
    for (prot, _), (fast_prot, _) in zip(reference, fast):
        assert prot.protein_tokens.shape[1:] == (5, 3)
        assert torch.equal(fast_prot.protein_tokens, prot.protein_tokens)
        assert torch.equal(fast_prot.protein_token_count, prot.protein_token_count)
