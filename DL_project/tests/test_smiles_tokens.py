import pytest
import torch

from dataloader.smiles_tokens import (
    SMILES_TOKEN_INDEX, SMILES_VOCABULARY, smiles_one_hot,
)


def test_one_hot_shape_matches_the_molformer_table_contract():
    """(1, characters, vocabulary) -- the leading 1 is what keeps every caller
    downstream (the dim=1 concat of candidates, the squeeze) unchanged."""
    encoding = smiles_one_hot("CCO")

    assert encoding.shape == (1, 3, len(SMILES_VOCABULARY))


def test_every_character_sets_exactly_its_own_column():
    smiles = "OP(=O)(O)O"
    encoding = smiles_one_hot(smiles)[0]

    assert torch.equal(encoding.sum(dim=1), torch.ones(len(smiles)))
    for position, character in enumerate(smiles):
        assert encoding[position, SMILES_TOKEN_INDEX[character]] == 1.0


def test_vocabulary_covers_the_characters_this_dataset_uses():
    """The 20 characters counted over the interaction table's own SMILES."""
    for character in "()+-/=@[\\]1234CHNOPS":
        assert character in SMILES_TOKEN_INDEX


def test_two_character_atoms_raise_rather_than_being_silently_split():
    """"Cl" must not read as carbon followed by an unknown letter."""
    with pytest.raises(KeyError, match="'l'"):
        smiles_one_hot("CCl")


def test_empty_smiles_raises():
    with pytest.raises(ValueError, match="empty SMILES"):
        smiles_one_hot("")
