# Preprocessing instructions

These scripts prepare embeddings, negative samples, FASTA and PDB files, and graph inputs.

- Run scripts or overwrite their outputs only when explicitly requested.
- Keep the file names and identifiers expected by `dataloader/Dataloader.py`.
- Keep interaction-table rows in their original order. Row positions are pair IDs used by Tanimoto weights.
- Keep graph node IDs, edge endpoints, pocket residues, and PLM residues aligned.
- If an edge endpoint is missing from the node table, report the structure and residue ID. Never replace it silently.
- Treat external programs, network calls, and large embedding jobs as expensive operations.
- Use small mocked or unit checks when changing parsing or path handling.
- Report missing tools and dependencies. Do not silently change the workflow.
