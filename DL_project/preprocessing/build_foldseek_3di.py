#!/usr/bin/env python3
"""Build Foldseek 3Di sequences for protein graphs.

3Di uses 20 states to describe spatial interactions between residues. Each state
is stored as a letter. Foldseek selects residue pairs by virtual-center distance.
See van Kempen et al., Nature Biotechnology 42, 2024:
https://pmc.ncbi.nlm.nih.gov/articles/PMC10869269/

Input: data/graphs/<name>/pocketness.pdb and coarse_graph_nodes.csv.
Output: data/protein_3di.csv, one row per protein, with columns:
    LTPProtein, residues, aa, three_di, foldseek_version

The script checks that Foldseek's amino-acid sequence matches the graph's residue
sequence and that the 3Di sequence has the same length. A mismatch stops the script
before it writes the CSV. dataloader/protein_tokens.py reads the result for
--deepclip_protein_tokens.

The Foldseek binary path is set in FOLDSEEK_PATH below. Installation details are
in files/reference/deepclip_architecture.md.

    python3 preprocessing/build_foldseek_3di.py
"""

import argparse
import os
import subprocess
import sys
import tempfile

import pandas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.compute_descriptors import RESIDUE_LETTERS  # noqa: E402


FOLDSEEK_PATH = os.path.expanduser("~/tools/foldseek/bin/foldseek")


def read_fasta(path):
    """{header: sequence}; headers are Foldseek's entry names (the PDB file stem)."""
    records = {}
    name = None
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                name = line[1:].split()[0]
                if name in records:
                    raise ValueError(f"{path}: entry {name!r} appears twice")
                records[name] = []
            else:
                records[name].append(line)
    return {key: "".join(parts) for key, parts in records.items()}


def node_sequence(nodes_path):
    """The graph's residues as one-letter codes, in node order."""
    codes = pandas.read_csv(nodes_path)["residue_type"].astype(int).tolist()
    bad = [code for code in codes if not 0 <= code < len(RESIDUE_LETTERS)]
    if bad:
        raise ValueError(f"{nodes_path}: residue_type outside 0..19: {sorted(set(bad))}")
    return "".join(RESIDUE_LETTERS[code] for code in codes)


def run(foldseek, arguments, log):
    subprocess.run([foldseek, *arguments], check=True, stdout=log, stderr=log)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--graphs-dir", default=os.path.join(root, "data", "graphs"))
    parser.add_argument("--out", default=os.path.join(root, "data", "protein_3di.csv"))
    args = parser.parse_args()

    version = subprocess.run(
        [FOLDSEEK_PATH, "version"], check=True, capture_output=True, text=True
    ).stdout.strip()

    names = sorted(
        name for name in os.listdir(args.graphs_dir)
        if os.path.exists(os.path.join(args.graphs_dir, name, "coarse_graph_nodes.csv"))
    )
    with tempfile.TemporaryDirectory() as work:
        # Link each pocketness.pdb under its protein name for Foldseek entry names.
        structures = os.path.join(work, "structures")
        os.mkdir(structures)
        for name in names:
            os.symlink(
                os.path.abspath(os.path.join(args.graphs_dir, name, "pocketness.pdb")),
                os.path.join(structures, f"{name}.pdb"),
            )
        db = os.path.join(work, "db")
        with open(os.path.join(work, "foldseek.log"), "w") as log:
            # Use file-based entry names; reject missing or duplicate entries below.
            run(FOLDSEEK_PATH, [
                "createdb",
                *[os.path.join(structures, f"{name}.pdb") for name in names],
                db, "--chain-name-mode", "0", "--threads", "1",
            ], log)
            run(FOLDSEEK_PATH, ["lndb", f"{db}_h", f"{db}_ss_h"], log)
            run(FOLDSEEK_PATH, ["convert2fasta", db, f"{db}_aa.fasta"], log)
            run(FOLDSEEK_PATH, ["convert2fasta", f"{db}_ss", f"{db}_3di.fasta"], log)
        amino_acids = read_fasta(f"{db}_aa.fasta")
        three_di = read_fasta(f"{db}_3di.fasta")

    rows = []
    problems = []
    for name in names:
        if name not in amino_acids or name not in three_di:
            problems.append(f"{name}: no Foldseek entry (multi-chain or unreadable?)")
            continue
        expected = node_sequence(
            os.path.join(args.graphs_dir, name, "coarse_graph_nodes.csv")
        )
        aa, letters = amino_acids[name], three_di[name]
        if len(letters) != len(aa):
            problems.append(f"{name}: {len(aa)} amino acids but {len(letters)} 3Di letters")
        elif aa != expected:
            first = next(
                (i for i, (a, b) in enumerate(zip(aa, expected)) if a != b),
                min(len(aa), len(expected)),
            )
            problems.append(
                f"{name}: Foldseek read {len(aa)} residues, graph has {len(expected)}; "
                f"first difference at node {first}"
            )
        else:
            rows.append({
                "LTPProtein": name, "residues": len(aa), "aa": aa,
                "three_di": letters, "foldseek_version": version,
            })
    if problems:
        raise ValueError("3Di not aligned to graph nodes:\n  " + "\n  ".join(problems))

    pandas.DataFrame(rows).to_csv(args.out, index=False)
    alphabet = sorted(set("".join(row["three_di"] for row in rows)))
    print(f"{len(rows)} proteins -> {args.out} (foldseek {version}); "
          f"3Di letters used: {''.join(alphabet)}")


if __name__ == "__main__":
    main()
