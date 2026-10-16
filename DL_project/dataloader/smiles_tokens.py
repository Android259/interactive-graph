"""Encode canonical SMILES characters as one-hot DeepCLIP lipid tokens.

Reuse LipidGraphBuilder._canonical_smiles, also used for MoLFormer lookup.
Canonicalization gives spellings such as CCO and OCC one representation,
so a motif window need not learn equivalent spellings separately.

SMILES_VOCABULARY contains the 20 characters observed in 1287 candidate
structures in data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_
CandidatesCompleted_Deduplicated.csv. It reserves no extra characters.
The table has no aromatic lowercase forms, #, ring digits above 4, Cl/Br,
or disconnected components (.). A character encoder cannot treat Cl/Br as
single atoms. Unknown characters raise an error naming the character.
Extend the vocabulary explicitly for new inputs; changing its width
invalidates existing checkpoints.
"""

import torch

SMILES_VOCABULARY = (
    "C", "N", "O", "P", "S", "H",
    "(", ")", "[", "]",
    "=", "-", "+",
    "/", "\\", "@",
    "1", "2", "3", "4",
)

SMILES_TOKEN_INDEX = {
    character: column for column, character in enumerate(SMILES_VOCABULARY)
}


def smiles_one_hot(smiles):
    """Return canonical SMILES as (1, characters, len(SMILES_VOCABULARY)) one-hot.

    The leading 1 matches MoLFormer's (1, tokens, 768) input contract.
    _encode_lipid_fragments concatenates candidates on dim=1; lipid_encoding squeezes it.
    """
    if not smiles:
        raise ValueError(
            "cannot encode an empty SMILES string -- _lipid_fragment_keys skips "
            "unparsable candidates, so an empty key here means the caller bypassed it"
        )
    columns = []
    for position, character in enumerate(smiles):
        column = SMILES_TOKEN_INDEX.get(character)
        if column is None:
            raise KeyError(
                f"SMILES character {character!r} at position {position} of "
                f"{smiles!r} is not in SMILES_VOCABULARY (dataloader/"
                f"smiles_tokens.py). Add it there if the dataset legitimately "
                f"contains it -- but note that widening the vocabulary widens the "
                f"lipid encoder's input, so checkpoints saved before the change "
                f"stop loading."
            )
        columns.append(column)
    encoding = torch.zeros(
        (1, len(columns), len(SMILES_VOCABULARY)), dtype=torch.float32
    )
    encoding[0, torch.arange(len(columns)), torch.tensor(columns)] = 1.0
    return encoding
