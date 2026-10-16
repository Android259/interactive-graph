"""Hold out source-paper lipid subclasses with --lipid_subclass.

Use Titeca et al.'s Figure 3a LTP-by-subclass axis in
files/literature/Reuter.pdf. This matches the requested task of classifying
binders/non-binders by lipid subclass.

This differs from --lipid_coldsplit's four project sets, which merge PC/LPC
and PA/PI/PS/PG/PGP/BMP/CL, and --lipid_isolation's distance-selected species.

Read membership from data/lipid_article_classification.json:
{FullIdentityOfLipid: subclass}, written by classify_lipids_by_article.py.
Do not duplicate it here. pair_baseline_common.resolve_excluded_lipids uses
the same map for Kron-RLS --excluded_lipids/--excluded_lipid_groups, keeping
network and baseline held-out species identical for the same specification.

Join subclasses with "+", e.g. PC or LPC+LPE+LPG. Merges make small subclasses
usable; see FIG3_SUBCLASS_BLOCKS.
"""
from __future__ import annotations

import json
import os

# Nine Kron-RLS blocks (results/tables/cron_test_metrics/cron_fig3_lipidgroups.txt):
# standalone subclasses plus three merges, sized by whole-table measurements
# from analysis/probes/lipid_subclass_report.py blocks.
# Counts are positives/proteins with a positive:
#   PC 218/16, PG 113/13, PE 80/11, FA 48/12, PA 26/4, PI 16/6: standalone.
#   Cer 14/1, CerP 10/1, HexCer 20/1, Hex2Cer 2/1, SHexCer 2/1, SM 18/2:
#   merged sphingolipids 66/4; individual blocks have too little protein coverage
#   for useful AUC_within_protein evaluation.
#   LPC 5/1, LPE 18/5, LPG 9/5: merged lyso 32/6.
#   PS 5/2, PGP 2/1, DAG 2/1, TAG 8/2: merged 17/6. PS+PGP alone had
#   n_proteins=0 in the first Kron-RLS pass; the four-way merge was measurable
#   (files/results/fig3_lipid_subclass_coldsplit_results.md).
# CL 14/2, BMP 1/1, VA 2/2, FAL 1/1 are separate Figure 3a rows
# (files/literature/Reuter.pdf p.22), but too small for these blocks and
# chemically unsuitable for existing merges. CL/BMP differ from the lipid
# merges; VA/FAL are not glycerolipids.
FIG3_SUBCLASS_BLOCKS = (
    "PC",
    "PG",
    "FA",
    "PE",
    "Cer+CerP+HexCer+Hex2Cer+SHexCer+SM",
    "PI",
    "LPC+LPE+LPG",
    "PA",
)

# Recorded whole-table (whole-molecule, head-group-only) Tanimoto isolation,
# measured by analysis/probes/lipid_subclass_report.py blocks.
# Each is mean best similarity of a held-out species to training:
# low means more novel, high means retained close relatives.
# Store seed-independent block values, as in lipid_isolation_blocks.BLOCK_GEOMETRY,
# to avoid rebuilding Tanimoto at every startup; the loader logs them.
# For head-group splits, shared acyl tails make whole-molecule similarity
# optimistic. Read the head-group column: FA scores 1.0000 (no novel head group),
# while merged sphingolipids score 0.2624, the most isolated block.
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
# Dataloader passes ROOT_DIR. Default to project data/ for configuration
# validation, which runs before a dataset and has no data-directory handle.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")


def article_subclass_species(data_dir=None):
    """Read {subclass: frozenset of FullIdentityOfLipid} from the classification JSON.

    On missing generated input, raise FileNotFoundError naming its generator.
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
    """Normalize a "+"-joined spec case-insensitively to the map's spelling, or raise.

    For example, use HexCer, not hexcer, so run-directory names are consistent.
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
