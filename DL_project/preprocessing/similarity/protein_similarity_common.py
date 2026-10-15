"""Shared storage and PDB inputs for identity, blosum62 and tmscore matrices.

Artifacts live under data/cache/protein_similarity/: a uint8 matrix over distinct
proteins, a table-row -> protein index, and a manifest with names and provenance.
Row-pair similarity is matrix[protein_index[i], protein_index[j]].
Encoding is round(clip(score, 0, 1) * 255), with diagonal 255.

All metrics use CA residues from data/esm3_input/<LTPProtein>.pdb in file order.
"""

import json
import pickle
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
SIMILARITY_SUBDIR = Path("cache") / "protein_similarity"
STRUCTURE_SUBDIR = "esm3_input"

# Artifact prefixes by metric.
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
    """Clip to [0, 1], encode as round(score * 255), and set the diagonal to 255."""
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
                # Track PDB changes independently of the interaction table.
                "structures": structures,
            },
            indent=2,
        )
        + "\n"
    )
    return matrix_path, index_path, manifest_path


def load_similarity(root_dir, metric, source_csv=None, data_dir=None):
    """Return None for absent/stale artifacts; raise with the path on read errors."""
    matrix_path, index_path, manifest_path = similarity_paths(root_dir, metric)
    if not all(path.exists() for path in (matrix_path, index_path, manifest_path)):
        return None
    try:
        manifest = json.loads(manifest_path.read_text())
        version = manifest["format_version"]
        recorded_metric = manifest["metric"]
        if version != FORMAT_VERSION or recorded_metric != metric:
            return None
        names = manifest["names"]
        normalization = manifest["parameters"].get("normalization")
        source = manifest["source"]
        structures = manifest["structures"]
        if not isinstance(names, list) or not isinstance(structures, dict):
            raise ValueError("invalid names or structures")
        source["size"], source["mtime_ns"]
        for recorded in structures.values():
            recorded["size"], recorded["mtime_ns"]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"Cannot read similarity manifest {manifest_path}: {exc}") from exc

    if source_csv is not None:
        path = Path(source_csv)
        try:
            stat = path.stat()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise OSError(f"Cannot inspect similarity source {path}: {exc}") from exc
        if stat.st_size != source["size"] or stat.st_mtime_ns != source["mtime_ns"]:
            return None
    if data_dir is not None:
        for name, recorded in structures.items():
            path = structure_path(data_dir, name)
            try:
                stat = path.stat()
            except FileNotFoundError:
                return None
            except OSError as exc:
                raise OSError(f"Cannot inspect similarity source {path}: {exc}") from exc
            if stat.st_size != recorded["size"] or stat.st_mtime_ns != recorded["mtime_ns"]:
                return None

    arrays = []
    for path in (matrix_path, index_path):
        try:
            array = torch.load(path, map_location="cpu", weights_only=True).numpy()
            if path == matrix_path:
                if array.shape != (len(names), len(names)) or array.dtype != np.uint8:
                    raise ValueError("expected a square uint8 matrix matching protein names")
            elif (
                array.ndim != 1
                or not np.issubdtype(array.dtype, np.integer)
                or np.any(array < 0)
                or np.any(array >= len(names))
            ):
                raise ValueError("expected a vector of valid protein indices")
            arrays.append(array)
        except (
            OSError, EOFError, pickle.UnpicklingError, RuntimeError,
            ValueError, TypeError, AttributeError, IndexError,
        ) as exc:
            raise ValueError(f"Cannot read similarity tensor {path}: {exc}") from exc
    matrix, protein_index = arrays
    return ProteinSimilarity(matrix, protein_index, names, recorded_metric, normalization)


def protein_order(table):
    """Proteins in first-appearance order, and each table row's matrix position."""
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
    """Read CA residues from the first PDB model in file order.

    Require one chain and at least one CA atom. Map unknown residue names to X
    and count them for reporting.
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
    if values.size == 0:
        print("off-diagonal: no protein pairs")
        return
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
