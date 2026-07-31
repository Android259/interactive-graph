"""Single source of protein names and artifact metadata."""

import csv
from functools import lru_cache
from pathlib import Path


DEFAULT_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
REGISTRY_FILE = "protein_registry.csv"


@lru_cache(maxsize=None)
def load_protein_registry(root_dir=DEFAULT_DATA_ROOT):
    path = Path(root_dir).resolve() / REGISTRY_FILE
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    registry = {}
    for row in rows:
        protein_id = row["protein_id"]
        if protein_id in registry:
            raise ValueError(f"Duplicate protein_id in {path}: {protein_id}")
        registry[protein_id] = {
            "protein_id": protein_id,
            "artifact_stem": row["artifact_stem"],
            "family": row["family"],
            "uniprot_id": row["uniprot_id"],
            "esm3_v1_extra_trim_pairs": int(row["esm3_v1_extra_trim_pairs"]),
        }
    return registry


def protein_record(protein_id, root_dir=DEFAULT_DATA_ROOT):
    registry = load_protein_registry(root_dir)
    try:
        return registry[protein_id]
    except KeyError as error:
        raise KeyError(
            f"Protein {protein_id!r} is absent from "
            f"{Path(root_dir) / REGISTRY_FILE}"
        ) from error


def protein_record_by_artifact_stem(artifact_stem, root_dir=DEFAULT_DATA_ROOT):
    matches = [
        record
        for record in load_protein_registry(root_dir).values()
        if record["artifact_stem"] == artifact_stem
    ]
    if len(matches) != 1:
        raise KeyError(
            f"Expected one protein for artifact stem {artifact_stem!r}, "
            f"found {len(matches)}"
        )
    return matches[0]
