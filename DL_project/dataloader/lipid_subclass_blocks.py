"""The lipid axis cut BY THE SOURCE PAPER'S OWN SUBCLASS, for --lipid_subclass.

The third axis on the lipid side, alongside the two that already exist:

  --lipid_coldsplit   four hand-built sets of PROJECT head-group classes
                      (dataloader/sampler.py's LIPID_COLDSPLIT_SETS)
  --lipid_isolation   blocks chosen by DISTANCE, so the held-out chemistry lands at a
                      requested Tanimoto isolation (dataloader/lipid_isolation_blocks.py)
  --lipid_subclass    one subclass of Titeca et al. (files/Reuter.pdf, the y axis of
                      the LTP x lipid-subclass matrix -- Figure 3a of the bioRxiv
                      preprint), held out of training for every protein

The third one exists because it is the task as the collaborators state it: "being able
to classify binders and non-binders by lipid subclass would be quite helpful already",
against the subclass column of the shared CSV. That is not the same partition as either
of the other two -- LIPID_COLDSPLIT_SETS merges PC with LPC and PA with PI/PS/PG/PGP/
BMP/CL, and an isolation block is whatever species happen to sit at the requested
distance -- so a run on either of those answers a different question from the one
being asked, however close it looks.

Membership is NOT repeated here. It is read from data/lipid_article_classification.json
(written by preprocessing/classify_lipids_by_article.py, {FullIdentityOfLipid:
subclass}), which is already the single source of truth --
training.pair_baseline_common.resolve_excluded_lipids resolves the Kron-RLS side's
--excluded_lipids/--excluded_lipid_groups through that same file, so the network and
the Kron-RLS baseline hold out exactly the same species for the same spec, which is
the whole point of having this axis named the same way on both sides.

A block SPEC is one or more subclass abbreviations joined by "+": "PC", "LPC+LPE+LPG".
The "+" form is what makes subclasses too small to stand alone usable at all -- see
FIG3_SUBCLASS_BLOCKS below.
"""
from __future__ import annotations

import json
import os

# The nine blocks the Kron-RLS run of the same axis actually used
# (cron_test_metrics/cron_fig3_lipidgroups.txt): the five subclasses big enough to be
# their own held-out block, plus three merges of subclasses that are not.
#
# Why these merges and not others -- measured by analysis/lipid_subclass_block_report.py
# over the whole table (positives / proteins holding at least one positive in the block):
#   PC 218/16, PG 113/13, PE 80/11, FA 48/12, PA 26/4, PI 16/6      stand alone
#   Cer 14/1, CerP 10/1, HexCer 20/1, Hex2Cer 2/1, SHexCer 2/1, SM 18/2
#       -> one sphingolipid block, 66/4. Every one of the six is a single-protein block
#          on its own, which cannot produce an AUC_within_protein at all.
#   LPC 5/1, LPE 18/5, LPG 9/5 -> one lyso block, 32/6.
#   PS 5/2, PGP 2/1, DAG 2/1, TAG 8/2 -> one block, 17/6. PS+PGP alone reached
#       n_proteins=0 in the first Kron-RLS pass (files/fig3_lipid_subclass_coldsplit_
#       results.md) -- the four-way merge is what made it measurable.
# CL (14/2), BMP (1/1), VA (2/2) and FAL (1/1) are in no block: they are in the table
# but not on the paper's own Figure-3a axis at a size any split could read.
FIG3_SUBCLASS_BLOCKS = (
    "PC",
    "PG",
    "FA",
    "PE",
    "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM",
    "PI",
    "LPC+LPE+LPG",
    "PA",
    "PS+PGP+DAG+TAG",
)

# How ISOLATED each block is from whatever stays in training, measured once by
# analysis/lipid_subclass_block_report.py over the whole interaction table:
# (whole-molecule Tanimoto, head-group-only Tanimoto). Mean best similarity of a
# held-out species to the chemistry left behind -- LOW means genuinely novel, HIGH
# means a close relative stayed in training. Stored rather than recomputed for the same
# reason lipid_isolation_blocks.BLOCK_GEOMETRY is: the number is a property of the
# SPEC, identical at every seed and in every run, so paying for a Tanimoto build in
# every job's startup would buy nothing. Printed by the loader so a run's own log says
# how cold its split actually was.
#
# Read the head-group column for this axis. A subclass block is cut ON the head group,
# so its acyl tails are shared with the rest of the table by construction and the
# whole-molecule number is optimistic here. Two entries make the point: FA's head-group
# similarity is 1.0000 (a free fatty acid has no head group to be novel in -- holding
# FA out holds out no head-group chemistry at all), and the six-way sphingolipid block
# is the only one anywhere near cold (0.2624).
BLOCK_TANIMOTO = {
    "PC": (0.7956, 0.7090),
    "PG": (0.8770, 0.7804),
    "PE": (0.8267, 0.7190),
    "FA": (0.8709, 1.0000),
    "PA": (0.7922, 0.6980),
    "PI": (0.7394, 0.6353),
    "HexCer": (0.7282, 0.6675),
    "Hex2Cer": (0.8863, 0.8353),
    "SHexCer": (0.7824, 0.7020),
    "SM": (0.6758, 0.6235),
    "Cer": (0.6249, 0.4618),
    "CerP": (0.6839, 0.5569),
    "LPC": (0.7978, 0.7784),
    "LPE": (0.7600, 0.7111),
    "LPG": (0.8196, 0.7412),
    "PS": (0.7898, 0.6745),
    "PGP": (0.8157, 0.7843),
    "DAG": (0.8373, 0.7255),
    "TAG": (0.8456, 0.7255),
    "CL": (0.8991, 0.8549),
    "BMP": (0.8510, 0.8078),
    "VA": (0.1294, 0.1176),
    "FAL": (1.0000, 1.0000),
    "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM": (0.4585, 0.2624),
    "LPC+LPE+LPG": (0.7791, 0.7386),
    "PS+PGP+DAG+TAG": (0.7723, 0.6745),
}

_CLASSIFICATION_FILE = "lipid_article_classification.json"
# Callers that already carry a data directory (Dataloader's own ROOT_DIR) pass it;
# training/read_configuration.py validates a spec long before any dataset exists and
# has no such handle, so the project's own data/ is the default.
_DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def article_subclass_species(data_dir=None):
    """{subclass abbreviation: frozenset of FullIdentityOfLipid}, read off
    data/lipid_article_classification.json. Raises FileNotFoundError naming the
    generator rather than a bare missing-file error -- the file is generated, not
    tracked input, so "run this" is the useful message.
    """
    path = os.path.join(str(data_dir or _DEFAULT_DATA_DIR), _CLASSIFICATION_FILE)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{path} is missing -- build it with "
            "preprocessing/classify_lipids_by_article.py before using --lipid_subclass"
        )
    with open(path) as handle:
        assignment = json.load(handle)
    groups: dict[str, set[str]] = {}
    for species, subclass in assignment.items():
        groups.setdefault(str(subclass), set()).add(str(species))
    return {name: frozenset(members) for name, members in groups.items()}


def canonical_subclass_spec(spec, data_dir=None):
    """Normalise a "+"-joined block spec to the article's own spelling, or raise.

    Case-insensitive, and the canonical spelling is whatever the classification file
    carries ("HexCer", not "hexcer"), so a run directory named after the spec is named
    the same way however the arg file spelled it.
    """
    names = [token.strip() for token in str(spec).split("+") if token.strip()]
    if not names:
        return ""
    known = {name.lower(): name for name in article_subclass_species(data_dir)}
    unknown = [name for name in names if name.lower() not in known]
    if unknown:
        raise ValueError(
            f"Unknown lipid subclass(es) {', '.join(unknown)}; expected "
            f"'+'-joined names from {', '.join(sorted(known.values()))}"
        )
    canonical = [known[name.lower()] for name in names]
    return "+".join(dict.fromkeys(canonical))


def subclass_block_species(spec, data_dir=None):
    """The FullIdentityOfLipid species one block spec holds out of training."""
    groups = article_subclass_species(data_dir)
    species: set[str] = set()
    for name in canonical_subclass_spec(spec, data_dir).split("+"):
        species.update(groups[name])
    return species
