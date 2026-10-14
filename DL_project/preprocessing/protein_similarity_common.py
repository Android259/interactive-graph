"""Shared format and inputs for the pairwise protein-similarity matrices.

Three metrics, one on-disk format, one directory (`data/protein_similarity/`):

    identity    sequence identity after global pairwise alignment (BLOSUM62, affine gaps)
    blosum62    the same alignment scored for conservative substitutions ("positives")
    tmscore     TM-align's structural TM-score

They are written by `preprocessing/build_protein_sequence_similarity.py` (the first two,
which share one alignment pass) and `preprocessing/build_protein_tmscore.py` (the third).

The format is the compact-Tanimoto format of
`dataloader/tensors_reading/tanimoto_compact_tensors_reader.py`, with the lipid axis
replaced by the protein one. One row per DISTINCT protein plus the index that expands it
back to one entry per interaction-table row, so a pair of rows' protein similarity is

    similarity[protein_index[i], protein_index[j]]

exactly as the lipid side reads `compact[structure_index[i], structure_index[j]]`. The
same uint8 encoding (`round(x * 255)`, diagonal forced to 255) and the same manifest
discipline (the artifacts are refused rather than served when their sources have moved).

Two differences from the lipid side, both forced by what a protein is here:

- There is no `row_ids` file. A row of the interaction table names exactly one protein,
  so the lipid side's candidate-instance axis has no analogue: the instance axis IS the
  table's rows, and a `row_ids` vector would be `arange(len(table))`.
- The manifest carries `names`, the protein per matrix row. The lipid artifacts are
  addressed positionally by the loader and need no such list; every consumer of these
  matrices instead reaches for them by `LTPProtein` (that is what a sampler steering its
  draw by protein relatedness has in hand), so the name -> row map has to survive the
  write.

Residues come from `data/esm3_input/<LTPProtein>.pdb`, not from `data/fasta/`, and all
three metrics read that one source. Those are the Voronota-normalized structures the
protein graphs and the ESM3 embeddings are built from (see
`dataloader/graphs_builders/protein_graph_builder.py` and
`preprocessing/build_consistent_esm3_pdb.py`), so a similarity computed over them is
computed over exactly the residues the model is shown -- one node per residue, same
order. The FASTA files hold the full deposited sequence instead, including residues that
are absent from the structure, which would make the sequence metrics disagree with the
structural one about what the protein is and both of them disagree with the model.
"""

import json
from pathlib import Path

import numpy as np
import torch

try:
    from Bio.Data.PDBData import protein_letters_3to1
    from Bio.PDB import PDBParser
except ModuleNotFoundError:  # pragma: no cover - reported by the builders' main()
    protein_letters_3to1 = None
    PDBParser = None


FORMAT_VERSION = 1
SIMILARITY_SUBDIR = "protein_similarity"
STRUCTURE_SUBDIR = "esm3_input"

# One prefix per metric, so the three sets sit side by side exactly as the isomeric and
# non-isomeric Tanimoto sets do, and a consumer names the metric it wants.
METRIC_PREFIX = {
    "identity": "Protein_identity",
    "blosum62": "Protein_blosum62",
    "tmscore": "Protein_tmscore",
}


class ProteinSimilarity:
    """One metric's matrix, its per-table-row index, and its protein names."""

    def __init__(self, matrix, protein_index, names, metric, normalization):
        self.matrix = matrix
        self.protein_index = protein_index
        self.names = list(names)
        self.metric = metric
        self.normalization = normalization

    @property
    def proteins(self):
        return self.matrix.shape[0]

    @property
    def index(self):
        """`{protein name: matrix row}` -- what a caller keyed by `LTPProtein` needs."""
        return {name: position for position, name in enumerate(self.names)}

    def as_float(self):
        """The matrix as similarities in [0, 1], the uint8 encoding undone."""
        return self.matrix.astype(np.float32) / 255.0

    def of(self, name_a, name_b):
        """The similarity of two proteins by name, in [0, 1]."""
        index = self.index
        return float(self.matrix[index[name_a], index[name_b]]) / 255.0


def similarity_paths(root_dir, metric):
    """The three paths of one metric under `<root_dir>/protein_similarity`."""
    if metric not in METRIC_PREFIX:
        raise ValueError(
            f"unknown metric {metric!r}; expected one of {sorted(METRIC_PREFIX)}"
        )
    directory = Path(root_dir).resolve() / SIMILARITY_SUBDIR
    prefix = METRIC_PREFIX[metric]
    return (
        directory / f"{prefix}_matrix_uint8.pt",
        directory / f"{prefix}_protein_index.pt",
        directory / f"{prefix}.manifest.json",
    )


def encode_uint8(matrix):
    """Similarities in [0, 1] as the uint8 the compact format stores.

    `round(x * 255)` and a forced 255 diagonal, both exactly as
    `preprocessing/build_tanimoto_compact.py` encodes Tanimoto, so a consumer that
    already divides a compact matrix by 255 needs no second convention. Values are
    clipped first: TM-score is bounded by construction, but a normalization that divides
    by the shorter chain can carry a rounding excess past 1.0.
    """
    encoded = np.round(np.clip(matrix, 0.0, 1.0) * 255).astype(np.uint8)
    np.fill_diagonal(encoded, 255)
    return encoded


def write_similarity(
    root_dir, metric, matrix, protein_index, names, source_csv, structures, parameters
):
    """Write one metric's matrix, index and manifest. Returns the paths written."""
    if matrix.shape != (len(names), len(names)):
        raise ValueError(
            f"matrix is {matrix.shape} for {len(names)} proteins; they must agree"
        )
    matrix_path, index_path, manifest_path = similarity_paths(root_dir, metric)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(torch.from_numpy(np.ascontiguousarray(matrix)), matrix_path)
    torch.save(
        torch.from_numpy(np.ascontiguousarray(protein_index)), index_path
    )
    source_csv = Path(source_csv)
    stat = source_csv.stat()
    manifest_path.write_text(
        json.dumps(
            {
                "format_version": FORMAT_VERSION,
                "metric": metric,
                "proteins": int(matrix.shape[0]),
                "rows": int(protein_index.shape[0]),
                "parameters": parameters,
                "names": list(names),
                "source": {
                    "path": source_csv.name,
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                },
                # The matrix is a function of the structures as much as of the table, and
                # the table's own mtime says nothing about a re-run of the PDB
                # normalization. Recorded per protein so a single replaced structure is
                # enough to make the artifact stale.
                "structures": structures,
            },
            indent=2,
        )
        + "\n"
    )
    return matrix_path, index_path, manifest_path


def load_similarity(root_dir, metric, source_csv=None, data_dir=None):
    """Load one metric's artifacts, or None when they are absent or stale.

    `source_csv` is checked against the manifest by size and nanosecond mtime, as the
    compact Tanimoto loader checks its own; `data_dir`, when given, additionally checks
    every structure the matrix was built from, so a re-normalized PDB is caught too.
    Returning None rather than raising keeps the decision with the caller: a sampler can
    fall back to an unsteered draw, while a builder can report the rebuild command.
    """
    matrix_path, index_path, manifest_path = similarity_paths(root_dir, metric)
    if not all(path.exists() for path in (matrix_path, index_path, manifest_path)):
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("format_version") != FORMAT_VERSION:
            return None
        if manifest.get("metric") != metric:
            return None
        if source_csv is not None:
            stat = Path(source_csv).stat()
            source = manifest["source"]
            if (
                stat.st_size != source["size"]
                or stat.st_mtime_ns != source["mtime_ns"]
            ):
                return None
        if data_dir is not None:
            for name, recorded in manifest["structures"].items():
                path = structure_path(data_dir, name)
                if not path.exists():
                    return None
                stat = path.stat()
                if (
                    stat.st_size != recorded["size"]
                    or stat.st_mtime_ns != recorded["mtime_ns"]
                ):
                    return None
        return ProteinSimilarity(
            torch.load(
                matrix_path, map_location="cpu", weights_only=True
            ).numpy(),
            torch.load(index_path, map_location="cpu", weights_only=True).numpy(),
            manifest["names"],
            manifest["metric"],
            manifest["parameters"].get("normalization"),
        )
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError):
        return None


def protein_order(table):
    """The table's proteins in first-appearance order, and each row's matrix position.

    First-appearance order rather than sorted, for the reason
    `build_tanimoto_compact.distinct_structures` gives: it is stable for a fixed table
    and keeps the matrix's row order traceable to the table it came from.
    """
    order = {}
    for name in table["LTPProtein"]:
        if name not in order:
            order[name] = len(order)
    protein_index = np.asarray(
        [order[name] for name in table["LTPProtein"]], dtype=np.int32
    )
    return list(order), protein_index


def structure_path(data_dir, name):
    """The normalized PDB of one protein, filed under its `LTPProtein` name."""
    return Path(data_dir) / STRUCTURE_SUBDIR / f"{name}.pdb"


class Structure:
    """One protein's residues: the sequence and the CA coordinates, in lock step."""

    def __init__(self, name, sequence, coords, unknown):
        self.name = name
        self.sequence = sequence
        self.coords = coords
        self.unknown = unknown

    def __len__(self):
        return len(self.sequence)


def read_structure(path, name):
    """The CA trace of a single-chain PDB as a `Structure`.

    One entry per residue that has a CA atom, first model only, in file order. A residue
    whose three-letter code is not a standard amino acid becomes 'X' and is counted:
    these structures have already had MSE converted to MET
    (`preprocessing/convert_mse_to_met.py`), so an 'X' here is something the
    normalization did not cover and the builders report it rather than hiding it in the
    sequence.

    Raises on more than one chain instead of silently taking the first: a second chain
    would change both the sequence the alignment sees and the point cloud TM-align
    superposes, and every structure in `data/esm3_input/` is single-chain, so a second
    one means the input, not this reader, needs attention.
    """
    parser = PDBParser(QUIET=True)
    model = next(iter(parser.get_structure(name, str(path))))
    chains = list(model)
    if len(chains) != 1:
        raise ValueError(
            f"{path}: expected a single chain, found {len(chains)} "
            f"({', '.join(chain.id for chain in chains)})"
        )

    letters, coords, unknown = [], [], 0
    for residue in chains[0]:
        if "CA" not in residue:
            continue
        letter = protein_letters_3to1.get(residue.get_resname().strip().upper(), "X")
        if letter == "X":
            unknown += 1
        letters.append(letter)
        coords.append(residue["CA"].get_coord())
    if not letters:
        raise ValueError(f"{path}: no residue carries a CA atom")
    return Structure(
        name,
        "".join(letters),
        np.asarray(coords, dtype=np.float64),
        unknown,
    )


def load_structures(data_dir, names):
    """Read every named protein's structure, reporting all missing files at once."""
    missing = [name for name in names if not structure_path(data_dir, name).exists()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} proteins have no structure under "
            f"{Path(data_dir) / STRUCTURE_SUBDIR}: {', '.join(missing)}"
        )
    return {
        name: read_structure(structure_path(data_dir, name), name) for name in names
    }


def structure_provenance(data_dir, names):
    """Per-protein size and nanosecond mtime of the structures a matrix was built from."""
    provenance = {}
    for name in names:
        stat = structure_path(data_dir, name).stat()
        provenance[name] = {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    return provenance


def report_matrix(matrix, names, top=5):
    """Print the off-diagonal spread and the most similar pairs of one metric."""
    off_diagonal = ~np.eye(len(names), dtype=bool)
    values = matrix[off_diagonal]
    print(
        f"off-diagonal: min {values.min():.3f}  mean {values.mean():.3f}  "
        f"max {values.max():.3f}"
    )
    upper = np.triu(np.ones_like(matrix, dtype=bool), k=1)
    rows, cols = np.nonzero(upper)
    order = np.argsort(matrix[rows, cols])[::-1][:top]
    print(f"most similar pairs ({top}):")
    for position in order:
        row, col = rows[position], cols[position]
        print(f"  {names[row]:<10} {names[col]:<10} {matrix[row, col]:.3f}")
