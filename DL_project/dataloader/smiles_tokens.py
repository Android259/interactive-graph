"""Character-level one-hot encoding of a canonical SMILES string.

The DeepCLIP-style input for the lipid branch. Instead of MoLFormer's 768-wide
per-token embedding, a lipid IS its own canonical SMILES spelling: one node per
character, one-hot over SMILES_VOCABULARY below. This is the same substitution
DeepCLIP makes on the RNA side, where a sequence is one-hot over (A, C, G, U) and
a convolution slides over it looking for a motif -- the lipid analogue of a motif
being a head group, which canonical SMILES writes as a contiguous substring
("OP(=O)(O)OCC[N+](C)(C)C" for phosphocholine).

What this trades away. MoLFormer's 768 numbers per token carry chemistry learned
from ~1e9 PubChem molecules; a one-hot column carries none. Everything the model
knows about chemistry in this mode has to come out of this project's own ~1287
distinct candidate structures. That is DeepCLIP's own bargain (one small model,
one protein's own data, no borrowed corpus) and the reason it is worth having as
an option next to the MoLFormer path rather than instead of it.

Why the canonical string specifically. Canonicalization already happens on every
row -- LipidGraphBuilder._canonical_smiles, which is where the lookup key for the
MoLFormer table comes from -- so this encoder reuses that exact string. It matters
for more than tidiness: one molecule can be spelled many ways ("CCO", "OCC"), and
a window sliding over an arbitrary spelling would have to learn every spelling of
the same head group separately. RDKit's canonical form fixes one spelling per
molecule, so a head group looks the same every time and one learned window
suffices.
"""

import torch


# Order is load-bearing: it fixes which one-hot column each character owns, so a
# saved lipid1 is only meaningful against this exact tuple. Appending a character
# is safe for future runs but changes the encoder's input width -- which changes
# number_of_parameters, and that names the run directory and is a column of
# metrics_summary.csv -- while REORDERING silently invalidates every checkpoint
# saved before the change without changing any width. Treat this as a schema.
#
# Membership is exactly what the data uses, with nothing held in reserve: these are
# the 20 characters counted over the 1287 distinct candidate structures in
# data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_
# CandidatesCompleted_Deduplicated.csv, and no others. No lowercase aromatic forms
# (this table's lipids have no aromatic ring), no "#", no ring digits past 4, no
# "l"/"r" (a character-level encoder has no two-character atom token, so "Cl" and
# "Br" must raise rather than read as a carbon plus an unknown letter), no "."
# (disconnected components / salts).
#
# The cost of that strictness is deliberate: a molecule outside this alphabet stops
# the run in smiles_one_hot below with a message naming the character, instead of
# being quietly encoded against a column that was reserved on a guess. Widening the
# tuple is the intended fix -- it just has to be a decision someone makes, and it
# invalidates checkpoints (see the width note above).
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
    """One canonical SMILES as (1, characters, len(SMILES_VOCABULARY)) one-hot.

    The leading axis of 1 is not decoration: it matches the MoLFormer table's own
    (1, tokens, 768) contract exactly, so every caller downstream is unchanged --
    LipidGraphBuilder._encode_lipid_fragments still concatenates several candidates
    along dim=1, and lipid_encoding still squeezes the result.
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
