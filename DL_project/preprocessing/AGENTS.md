# Preprocessing Instructions

- Preprocessing scripts produce embeddings, negative samples, FASTA/PDB derivatives, and graph-related inputs.
- Do not run them or overwrite their outputs unless explicitly requested.
- Preserve file naming and identifiers expected by `dataloader/Dataloader.py`.
- Preserve interaction-table row order: original row positions are active pair
  IDs used by Tanimoto weights and GRAB edges.
- Protein graph generation must keep node identifiers, edge endpoints,
  pocket-residue order, and PLM residue order aligned.
- Never silently replace an edge endpoint missing from the generated node
  table. Report the affected structure and residue identifier.
- Treat external binaries, network calls, and large model embedding generation as expensive side effects.
- Prefer small mocked/unit checks when changing parsing or path logic.
- Report required external tools or unavailable dependencies instead of silently changing the workflow.
