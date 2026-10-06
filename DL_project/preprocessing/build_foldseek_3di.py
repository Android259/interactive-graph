#!/usr/bin/env python3
"""Per-residue Foldseek 3Di letters for every protein graph, aligned to its nodes.

3Di (van Kempen et al., "Fast and accurate protein structure search with Foldseek",
Nature Biotechnology 42, 2024) is a 20-letter structural alphabet: each residue gets
one letter describing the local backbone geometry it forms with its spatially nearest
residue. It is read here as a second per-residue alphabet next to the amino acid,
for --deepclip_protein_tokens (dataloader/protein_tokens.py).

Input: data/graphs/<name>/pocketness.pdb -- the structure Voronota built the graph
from, so its residues ARE the nodes of coarse_graph_nodes.csv, in the same order. Not
data/esm3_input/<name>.pdb: that copy predates the 2026-09-17 graph rebuild and has
fewer residues than the graph for GLTP (205/206), GM2A (162/193), HSDL2 (273/275) and
LCN15 (149/154). Foldseek reads only coordinates, so the pocket flag pocketness.pdb
keeps in its B-factor column does not matter here.

Output: data/protein_3di.csv, one row per protein:
    LTPProtein, residues, aa, three_di, foldseek_version
`aa` and `three_di` have one letter per graph node, in node order.

Alignment is CHECKED, not assumed: Foldseek writes its own amino-acid string next to
the 3Di one, and that string must equal the node table's residue_type codes read as
letters (RESIDUE_LETTERS). Any protein where it does not -- a dropped residue, an
unknown residue written as X -- stops the script with the protein named, instead of
producing letters shifted against the nodes (preprocessing/AGENTS.md).

Needs the Foldseek binary (not a Python package); see
files/reference/deepclip_architecture.md for the exact download and version used.

    python3 preprocessing/build_foldseek_3di.py --foldseek ~/tools/foldseek/bin/foldseek
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import pandas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataloader.protein_graph_builder import RESIDUE_LETTERS  # noqa: E402


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
    parser.add_argument("--foldseek", default=shutil.which("foldseek") or "foldseek")
    parser.add_argument("--graphs-dir", default=os.path.join(root, "data", "graphs"))
    parser.add_argument("--out", default=os.path.join(root, "data", "protein_3di.csv"))
    args = parser.parse_args()

    version = subprocess.run(
        [args.foldseek, "version"], check=True, capture_output=True, text=True
    ).stdout.strip()

    names = sorted(
        name for name in os.listdir(args.graphs_dir)
        if os.path.exists(os.path.join(args.graphs_dir, name, "coarse_graph_nodes.csv"))
    )
    with tempfile.TemporaryDirectory() as work:
        # Every structure is called pocketness.pdb, and Foldseek names an entry after
        # its file -- so each is linked under its protein's name first.
        structures = os.path.join(work, "structures")
        os.mkdir(structures)
        for name in names:
            os.symlink(
                os.path.abspath(os.path.join(args.graphs_dir, name, "pocketness.pdb")),
                os.path.join(structures, f"{name}.pdb"),
            )
        db = os.path.join(work, "db")
        with open(os.path.join(work, "foldseek.log"), "w") as log:
            # --chain-name-mode 0: entries are named after the file alone when it
            # holds one chain, which every structure here does (checked below by
            # requiring exactly one entry per name).
            run(args.foldseek, [
                "createdb",
                *[os.path.join(structures, f"{name}.pdb") for name in names],
                db, "--chain-name-mode", "0", "--threads", "1",
            ], log)
            run(args.foldseek, ["lndb", f"{db}_h", f"{db}_ss_h"], log)
            run(args.foldseek, ["convert2fasta", db, f"{db}_aa.fasta"], log)
            run(args.foldseek, ["convert2fasta", f"{db}_ss", f"{db}_3di.fasta"], log)
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
