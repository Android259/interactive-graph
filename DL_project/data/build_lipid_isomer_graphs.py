#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import multiprocessing
import sys

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dataloader.dataset_source import INTERACTION_CSV
from dataloader.pair_descriptors import (
    CONFORMER_COUNT, CONFORMER_SEED, generate_conformer_ensemble,
)


DATA_DIR = Path(__file__).resolve().parent
# The interaction table every run reads, so the graphs cover exactly the SMILES the
# loader will ask for. It used to name a file of its own, which has since been replaced
# and left 18 of the current table's candidates without a graph.
INPUT_CSV = DATA_DIR / INTERACTION_CSV
OUTPUT_DIR = DATA_DIR / "lipid_graphs"
INDEX_CSV = OUTPUT_DIR / "lipid_graph_index.csv"


NODE_COLUMNS = [
    "atom_idx",
    "atomic_num",
    "formal_charge",
    "degree",
    "hybridization",
    "is_aromatic",
    "is_in_ring",
    "chiral_tag",
    "chirality_possible",
    "total_num_hs",
    "mass",
    "gasteiger_charge",
    "chain_rank",
]

EDGE_COLUMNS = [
    "source",
    "target",
    "bond_type",
    "is_conjugated",
    "is_in_ring",
    "stereo",
    "bond_dir",
    "is_aromatic",
    "mean_bond_length",
]

def iter_smiles(value):
    value = str(value)
    if value in ["", "0", "Empty", "NonConclusive", "nan"]:
        return
    if "//" in value or "\\\\" in value:
        value = value.replace("//", "/")
        value = value.replace("\\\\", "\\")
    for smiles in value.split(";"):
        smiles = smiles.strip()
        if smiles:
            yield smiles


def canonical_isomeric_smiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, None
    canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
    return canonical, mol


def graph_id_from_smiles(smiles):
    return hashlib.sha1(smiles.encode("utf-8")).hexdigest()[:16]


def compute_chain_ranks(mol):
    """Per-atom position along the molecule's longest topological path, 0 (head) to
    1 (tail) -- the --cross_attention_chain_bias feature: how deep into the acyl
    tail an atom sits, for pairing against a protein residue's burial depth.

    Uses the WHOLE bond graph (unlike pair_descriptors.longest_acyl_chain, which
    deliberately drops rings/aromatics to isolate just the acyl tail) so every atom
    gets a defined rank, not only ones on a qualifying chain. The two most
    topologically distant atoms (found by double-BFS, the standard tree-diameter
    trick) anchor the scale; whichever of the two is a heteroatom (O/N/P/S -- most
    lipid head groups carry one) is called the head (rank 0), the other the tail
    (rank 1). If neither or both are heteroatoms, the lower atom index is the head
    -- an arbitrary but deterministic tiebreak for symmetric molecules with no real
    head/tail distinction.
    """
    neighbours = {atom.GetIdx(): [] for atom in mol.GetAtoms()}
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        neighbours[i].append(j)
        neighbours[j].append(i)

    def bfs_distances(start):
        distances = {start: 0}
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in neighbours[node]:
                if neighbour not in distances:
                    distances[neighbour] = distances[node] + 1
                    queue.append(neighbour)
        return distances

    if not neighbours:
        return {}
    arbitrary_start = next(iter(neighbours))
    one_end = max(bfs_distances(arbitrary_start).items(), key=lambda item: item[1])[0]
    distances_from_one_end = bfs_distances(one_end)
    other_end = max(distances_from_one_end.items(), key=lambda item: item[1])[0]
    diameter = distances_from_one_end[other_end]

    def is_heteroatom(idx):
        return mol.GetAtomWithIdx(idx).GetAtomicNum() not in (1, 6)

    if is_heteroatom(one_end) and not is_heteroatom(other_end):
        head, tail = one_end, other_end
    elif is_heteroatom(other_end) and not is_heteroatom(one_end):
        head, tail = other_end, one_end
    else:
        head, tail = sorted((one_end, other_end))

    if diameter == 0:
        return {atom_idx: 0.0 for atom_idx in neighbours}
    distances_from_head = bfs_distances(head)
    return {
        atom_idx: min(distance / diameter, 1.0)
        for atom_idx, distance in distances_from_head.items()
    }


def atom_features(atom, chain_rank):
    charge = 0.0
    if atom.HasProp("_GasteigerCharge"):
        try:
            charge = float(atom.GetProp("_GasteigerCharge"))
        except ValueError:
            charge = 0.0
    if charge != charge:
        charge = 0.0

    return {
        "atom_idx": atom.GetIdx(),
        "atomic_num": atom.GetAtomicNum(),
        "formal_charge": atom.GetFormalCharge(),
        "degree": atom.GetDegree(),
        "hybridization": int(atom.GetHybridization()),
        "is_aromatic": int(atom.GetIsAromatic()),
        "is_in_ring": int(atom.IsInRing()),
        "chiral_tag": int(atom.GetChiralTag()),
        "chirality_possible": int(atom.HasProp("_ChiralityPossible")),
        "chain_rank": chain_rank,
        "total_num_hs": atom.GetTotalNumHs(),
        "mass": atom.GetMass(),
        "gasteiger_charge": charge,
    }


def bond_features(source, target, bond, mean_bond_length):
    return {
        "source": source,
        "target": target,
        "bond_type": float(bond.GetBondTypeAsDouble()),
        "is_conjugated": int(bond.GetIsConjugated()),
        "is_in_ring": int(bond.IsInRing()),
        "stereo": int(bond.GetStereo()),
        "bond_dir": int(bond.GetBondDir()),
        "is_aromatic": int(bond.GetIsAromatic()),
        "mean_bond_length": mean_bond_length,
    }


def mean_bond_lengths(mol, n_confs=CONFORMER_COUNT, seed=CONFORMER_SEED):
    """Per-bond length (Angstrom), averaged over an ETKDG+MMFF conformer ensemble.

    A single generated conformer is an arbitrary draw from a flexible molecule's
    conformational ensemble (a fatty-acid tail has many near-isoenergetic
    extended/kinked shapes) -- feeding that one draw to the model would teach it
    the generator's seed, not the molecule. Averaging over an ensemble instead
    gives a value that is stable across reruns with a different seed, while still
    coming from real 3D geometry rather than a topological proxy.

    Returns {(begin_idx, end_idx): mean_length} keyed by the ORIGINAL (no
    explicit-H) mol's atom indices -- Chem.AddHs appends new atoms after the
    existing ones, so heavy-atom indices are unchanged in the H-explicit copy
    conformers are generated on.
    """
    mol_h, conf_ids = generate_conformer_ensemble(mol, n_confs=n_confs, seed=seed)

    lengths = {}
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        distances = [
            mol_h.GetConformer(cid).GetAtomPosition(i).Distance(
                mol_h.GetConformer(cid).GetAtomPosition(j)
            )
            for cid in conf_ids
        ]
        lengths[(i, j)] = sum(distances) / len(distances)
    return lengths


def write_lipid_graph(graph_dir, mol):
    AllChem.ComputeGasteigerCharges(mol)
    bond_lengths = mean_bond_lengths(mol)
    chain_ranks = compute_chain_ranks(mol)

    nodes = pd.DataFrame(
        [atom_features(atom, chain_ranks[atom.GetIdx()]) for atom in mol.GetAtoms()]
    )
    edges = []
    for bond in mol.GetBonds():
        begin = bond.GetBeginAtomIdx()
        end = bond.GetEndAtomIdx()
        length = bond_lengths[(begin, end)]
        edges.append(bond_features(begin, end, bond, length))
        edges.append(bond_features(end, begin, bond, length))

    graph_dir.mkdir(parents=True, exist_ok=True)
    nodes.to_csv(graph_dir / "nodes.csv", columns=NODE_COLUMNS, index=False)
    pd.DataFrame(edges).to_csv(graph_dir / "edges.csv", columns=EDGE_COLUMNS, index=False)


def is_already_built(graph_dir):
    """Whether this graph dir already holds a CURRENT-schema pair of CSVs.

    Presence of the files is not enough: a dir written before mean_bond_length /
    chain_rank joined EDGE_COLUMNS/NODE_COLUMNS has both files and would be
    skipped while still missing the columns the loader now reads. Checking the
    header of each -- one short read, no parse of the body -- is what makes a
    re-run resume the schema change rather than declare it done.
    """
    nodes_csv = graph_dir / "nodes.csv"
    edges_csv = graph_dir / "edges.csv"
    if not (nodes_csv.exists() and edges_csv.exists()):
        return False
    try:
        with nodes_csv.open() as handle:
            node_header = handle.readline().strip().split(",")
        with edges_csv.open() as handle:
            edge_header = handle.readline().strip().split(",")
    except OSError:
        return False
    return node_header == NODE_COLUMNS and edge_header == EDGE_COLUMNS


def _build_one(task):
    """Worker body: rebuild one graph, or report it was already current.

    Takes/returns plain tuples of str -- an RDKit Mol does not survive the
    pickling a process pool does, so the SMILES is re-parsed inside the worker
    instead of being handed one. Parsing is microseconds against the conformer
    ensemble that dominates this job, so nothing is lost by it.
    """
    graph_id, canonical = task
    graph_dir = OUTPUT_DIR / graph_id
    if is_already_built(graph_dir):
        return graph_id, "skipped"
    mol = Chem.MolFromSmiles(canonical)
    if mol is None:
        return graph_id, "unparseable"
    try:
        write_lipid_graph(graph_dir, mol)
    except Exception as error:  # noqa: BLE001 -- one bad molecule must not sink the pool
        return graph_id, f"failed: {type(error).__name__}: {error}"
    return graph_id, "built"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jobs", type=int, default=1,
        help="worker processes (default 1). Each molecule's conformer ensemble is "
             "independent, so this scales close to linearly.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="rebuild every graph, including ones already on the current schema.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_CSV)

    # The full graph list is enumerated first, unconditionally: the index CSV must
    # describe every graph the loader can ask for, not only the ones this run
    # happened to rebuild, so a resumed run still writes a complete index.
    graph_rows = []
    tasks = []
    seen = set()
    for column in ["SmileGlobal", "SmileFragment"]:
        for value in df[column].fillna(""):
            for smiles in iter_smiles(value):
                canonical, mol = canonical_isomeric_smiles(smiles)
                if canonical is None or canonical in seen:
                    continue
                seen.add(canonical)
                graph_id = graph_id_from_smiles(canonical)
                graph_rows.append({
                    "graph_id": graph_id,
                    "canonical_smiles": canonical,
                    "source_column": column,
                })
                if args.force or not is_already_built(OUTPUT_DIR / graph_id):
                    tasks.append((graph_id, canonical))

    print(f"Graphs in table: {len(graph_rows)}; to build: {len(tasks)}", flush=True)

    counts = {"built": 0, "skipped": 0}
    problems = []
    if tasks:
        if args.jobs > 1:
            with multiprocessing.Pool(args.jobs) as pool:
                results = pool.imap_unordered(_build_one, tasks, chunksize=1)
                results = list(_report_progress(results, len(tasks)))
        else:
            results = list(_report_progress(map(_build_one, tasks), len(tasks)))
        for graph_id, status in results:
            if status in counts:
                counts[status] += 1
            else:
                problems.append((graph_id, status))

    pd.DataFrame(graph_rows).to_csv(INDEX_CSV, index=False)
    print(f"Built: {counts['built']}; already current: {counts['skipped']}")
    if problems:
        print(f"Problems: {len(problems)}")
        for graph_id, status in problems:
            print(f"  {graph_id}: {status}")
    print(f"Saved index: {INDEX_CSV}")
    # A non-zero exit on problems so a cluster job that lost molecules is not
    # mistaken for a clean one by whatever reads its status.
    return 1 if problems else 0


def _report_progress(results, total, every=25):
    """Pass results through, printing a counter line every `every` completions.

    A generator rather than a print inside the worker: workers write to the same
    stdout concurrently and their lines interleave, while this runs in the parent
    where the ordering is its own.
    """
    for done, item in enumerate(results, start=1):
        if done % every == 0 or done == total:
            print(f"  {done}/{total}", flush=True)
        yield item


if __name__ == "__main__":
    sys.exit(main())
