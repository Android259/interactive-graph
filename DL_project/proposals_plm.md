# ESM3 usage in this project: findings and proposals

Audit of how the protein-language-model (PLM) branch is built and consumed, and
what was changed in response. Nothing existing was deleted or modified in place;
everything below is either a finding or an additive file/flag.

## 1. Findings

### 1.1 ESM3 is used sequence-only -- effectively ESM2-grade

`preprocessing/EmbedProtein.py` calls `ESMProtein(sequence=seq)` with only a FASTA
sequence. ESM3 is a multi-track model (sequence, structure/coordinates, SASA,
secondary structure, function); with every other track empty/masked, it runs in
exactly the information regime of a sequence-only model. The multimodal value of
ESM3 over ESM2 (structure- and function-conditioned representations) is unused,
despite the extra architecture/compute cost.

### 1.2 Per-residue embeddings are pooled to one flat mean vector

`Final_Layer` (`architecture/final_layer.py`) pools protein residues with
mean/GeM pooling before classification. Whatever per-residue specificity ESM3
embeddings carry is averaged away before the decision is made, and (pre-fix)
uniformly across the whole protein rather than focused on the binding site.
-> Addressed by `attention_pooling` (see 2.4).

### 1.3 ESM3-row <-> graph-node alignment was checked by count only, silently

The loader (`dataloader/New_dataloader.py`) attached ESM3 embedding row `i` to graph
node `i` positionally, checking only that the row COUNT matched (and only printing a
warning on mismatch, never failing). No check that residue `i` in the embedding is
actually residue `i` in the graph (order, not just count).
-> Addressed by `dataloader/plm_alignment.py` + `tests/test_esm3_alignment.py` +
hard-fail in the loader (see 2.1).

### 1.4 FASTA and `pocketness.pdb` are NOT independent sources in this project

Contrary to general practice (FASTA from UniProt, structure from PDB), in this repo
BOTH are derived from the same raw file `data/structures/raw/<stem>*.pdb1`:
FASTA via `preprocessing/pdb2fasta.py` (a CA-atom regex extractor,
`data/structures/fasta.sh`), the graph/`pocketness.pdb` via Voronota. Divergence
risk is between two parsers of one file, not between two databases.

Verified concrete divergence mechanisms on the actual data:
  - **Unresolved residues (real gaps in electron density)**: confirmed in
    `CERT_6j81` (gaps at resSeq 492-496, 534-541), `GLTP_2evl` (167-169),
    `HSDL2_3kvo` (210-213), `LCN15_2xst` (78-84). Physically unavoidable for
    experimental structures; AlphaFold models have none by construction.
  - **Alternate conformations (altLoc)**: raw `BPI_1ewf` has 474 CA records for 456
    residues (18 duplicated); `pocketness.pdb` already has exactly 456 (1:1) --
    Voronota already collapsed these. NOT a live risk for `pocketness.pdb`-based
    work.
  - **Selenomethionine (MSE)**: present (as HETATM) in raw `GM2A_1g13.pdb1` and
    `PITPNA_1uw5.pdb1` -- the only two proteins in the dataset with hard-coded
    extra-trim compensation in `New_dataloader.get()` (`GM2A: [1:-1]` extra,
    `PITPNA: [4:-4]`), almost certainly patching an MSE-handling mismatch upstream
    of `pocketness.pdb`. Verified: `pocketness.pdb` for both already shows 0 MSE
    records, residue count matching the graph node count exactly -- MSE is NOT a
    live risk for `pocketness.pdb`-based work either, only for naive parsers of the
    raw file.
  - **Insertion codes / multi-model (NMR) files**: none present in this dataset
    (checked across all 35 raw structures).

### 1.5 `pocketness.pdb`'s B-factor column is not a confidence value

Verified directly: `pocketness.pdb`'s B-factor column has only 2 distinct values
(`{0.00, 1.00}`) across a whole protein, vs 142 distinct real pLDDT values in the
matching raw AlphaFold file. The Voronota pocket-detection step overwrote this
column with a binary pocket-membership flag (hence the filename). The real
experimental B-factor / AlphaFold pLDDT is **lost** in `pocketness.pdb` and cannot
be recovered from it.

It **is** recoverable from `data/structures/raw/<stem>*.pdb1` by matching residues
on `(chain, resSeq)` -- verified 100% recoverable (0 misses) across all 35 proteins
in the dataset, both AlphaFold-derived and experimental.

### 1.6 Voronota SASA and Shrake-Rupley SASA agree almost perfectly

`residue_sas_area` (Voronota, tangent-sphere method, already feeding the GNN branch)
vs `freesasa`-recomputed SASA (Shrake-Rupley, the convention ESM3's SASA tokenizer
is presumably calibrated on) were compared directly
(`analysis/check_sasa_correspondence.py`): Pearson r = 0.9997 across 7794 residues
from all 35 proteins, linear fit `voronota = 1.006 * freesasa - 0.73`, 100% residues
matched by `(chain, resSeq)`. Either source is usable for an ESM3 `sasa` track after
this (near-identity) rescaling; using Voronota's own value keeps the PLM and GNN
branches looking at the same solvent-accessibility signal.

### 1.7 AlphaFold vs experimental structures need different B-factor semantics

`data/structures/raw/` mixes AlphaFold models (filenames containing `AF-`, e.g.
`ATCAY_AF-Q86WG3-F1-model_v4.pdb1`) and real experimental structures (4-character PDB
codes, e.g. `BPI_1ewf.pdb1`). The same file column holds pLDDT (0-100 confidence) for
the former and a real crystallographic B-factor (arbitrary per-structure Å² scale,
**opposite direction**: higher = more disordered, vs pLDDT where higher = more
confident) for the latter. Any code reading this column must know which convention
applies per protein (`ESMProtein.from_pdb(..., is_predicted=...)` in the SDK).

### 1.8 Missing tracks that cannot be filled from data in this repo

  - `secondary_structure`: would need an `mkdssp` run against the raw structure;
    not present as data, and not attempted (would need to vendor/install DSSP).
  - `function_annotations`: needs real InterPro/GO annotations; the protein-family
    label used elsewhere in this project (e.g. `CRAL-TRIO`) is a different
    vocabulary and would misrepresent the track if forced in.

### 1.9 ESM3 SDK confirms a `CHAINBREAK` structure token exists

Checked the actual `evolutionaryscale/esm` source: `StructureTokenizer` reserves a
`CHAINBREAK` token id (`codebook_size + 4`). Documented usage
(`ProteinChain.concat(..., use_chainbreak=True)`) is for joining **separate chains**
of a complex, not confirmed to be automatically inserted for an unresolved loop
**within** one chain (residue_index/atom37_mask NaN-based gap representation is
documented for that case instead). Not verified live (no `esm` package installed in
this environment) -- flag before relying on it.

## 2. What was implemented

### 2.1 ESM3<->graph alignment: hard check + training-free test

- `dataloader/plm_alignment.py` -- reusable count-invariant check (embedding rows vs
  graph nodes after special-token trimming).
- `tests/test_esm3_alignment.py` -- training-free pytest over all 35 proteins;
  currently all pass.
- `dataloader/New_dataloader.py` -- the loader now raises `ValueError` on mismatch
  instead of printing a warning.
- Scope note (unchanged limitation): this checks **count**, not residue **order**;
  order verification needs a real sequence alignment, not attempted.

### 2.2 GRL adversary moved to pre-cross-attention representations

(Separate finding from an earlier part of this audit, included here for
completeness.) The adversarial anti-shortcut heads (`adversarial_grl`) were reading
POST-cross-attention pooled features, where cross-attention has already injected the
counterpart partner residually -- penalizing the interaction summary, not the
single-partner identity shortcut they're meant to suppress. Moved to pre-cross-
attention (`architecture/final_layer.py`'s `compute_adversary`, called from
`architecture/interaction_classification.py` before `cross_attention1`).

### 2.3 Empirical effect of GRL / lipid_only / protein_only on cold-split dynamics

`analysis/run_dynamics.py` -- general per-epoch dynamics extractor (any run label,
binned trajectories, per-run early->late deltas, paired comparison against a
baseline label). Findings from the 18-run (9 leave-one-family-out groups x 2 seeds)
sweep: GRL gives a small but real positive shift in validation sensitivity
(+0.095 mean, 15/18 runs) without changing the underlying collapse dynamic;
`protein_only` never exceeds chance (valid BA pinned at 0.500 every epoch) --
the protein branch carries no cold-transferable signal on this split, `lipid_only`
matches or beats the full model on late-epoch metrics. Anti-shortcut mechanisms
(GRL, bilinear fusion) push against the one signal (lipid identity) that actually
generalizes across held-out families.

### 2.4 Attention pooling (learned query) + pocket bias

`architecture/final_layer.py`: `AttentionPool` replaces the fixed mean/GeM/add_max
reduction with a learned per-node gate + per-graph softmax readout
(`out = sum_i softmax_i(w.x_i [+ pocket_bias * pocket_i]) * x_i`), so pooling can
weight residues instead of averaging them uniformly (addresses 1.2).
Flags: `attention_pooling`, `attention_pooling_pocket_bias` (requires the former).

### 2.5 Consistent-structure PDB + real confidence recovery (this session's main ask)

**New files only; `data/graphs/*/pocketness.pdb`, `data/embedding_ESM3/`, and every
other pre-existing file are untouched (verified: original B-factor values
`{0.00, 1.00}` unchanged after running the builder).**

- `preprocessing/build_consistent_esm3_pdb.py` -- for each of the 35 proteins,
  recovers the real per-residue B-factor/pLDDT from `data/structures/raw/<stem>*.pdb1`
  by `(chain, resSeq)` matching (see 1.5) and writes:
    - `data/esm3_input/<stem>.pdb` -- pocketness.pdb's coordinates/residue set
      (already MSE/altLoc-normalized, see 1.4) with the B-factor column replaced by
      the recovered real value (CA atom's value applied per-residue, matching
      AlphaFold's own per-residue pLDDT convention).
    - `data/esm3_input/<stem>_node_confidence.csv` -- one row per graph node, same
      order as `coarse_graph_nodes.csv`, with a direction-normalized `confidence` in
      `[0, 1]` where **higher always means more reliable**, regardless of source:
      `pLDDT / 100` for AlphaFold stems, `1 - minmax(B-factor)` for experimental ones
      (B-factor's "higher = more disordered" is the opposite direction of pLDDT, so
      this flips it to a consistent semantics -- see 1.7).
    - `data/esm3_input/is_predicted_manifest.csv` -- `stem,is_predicted` for the SDK's
      `from_pdb(is_predicted=...)`.
  Run and verified against all 35 proteins: 0 unmatched residues in either the PDB
  rewrite or the node-confidence CSVs; spot-checked ATCAY (142 distinct real pLDDT
  values recovered, vs 2 before) and BPI (continuous `1-minmax(B-factor)` values).

- `preprocessing/embed_protein_esm3_v2.py` -- new ESM3 embedding generator, takes a
  single `.pdb` path as a CLI argument (`data/esm3_input/<stem>.pdb`), loads it via
  `ProteinChain.from_pdb`/`ESMProtein.from_protein_chain` (real coordinates + real
  confidence via `is_predicted`, read from `is_predicted_manifest.csv`), sets `sasa`
  from Voronota's `residue_sas_area` (see 1.6), writes to
  `data/embedding_ESM3_v2/<stem>_ESM3v2.pkl` (does not touch `data/embedding_ESM3/`).
  Auto-downloads the checkpoint into a project-local `data/esm3_checkpoint/` folder
  (checks first, downloads only if missing -- `HF_HOME` is pointed there before `esm`
  is imported, so both this script's explicit check and ESM3's internal
  `data_root()` resolve to the same place; re-running never re-downloads).

  **`esm` package installed and executed for real in this session** (with explicit
  user go-ahead, after flagging a HF-token-shaped string found commented out in
  `EmbedProtein.py:5` -- that token was deliberately NOT reused; the checkpoint
  turned out to download without any token at all). The exact checkpoint identity,
  confirmed by reading the installed package's own source
  (`esm.utils.constants.esm3.data_root`): model name `esm3-sm-open-v1` resolves to
  the Hugging Face repo `EvolutionaryScale/esm3-sm-open-v1`
  (`huggingface_hub.snapshot_download`, ~11 GB, cached under
  `data/esm3_checkpoint/`). Note: installing `esm` downgraded this conda
  environment's `huggingface-hub` (1.21.0 -> 0.36.2) and `transformers`
  (5.12.1 -> 4.48.1) to satisfy its dependency pins.

  Generated real v2 embeddings for **all 35 proteins**
  (`data/embedding_ESM3_v2/*_ESM3v2.pkl`, ~47 MB total). Verified: every protein's
  embedding row count minus the standard BOS/EOS trim (`[1:-1]`, no special-case
  hacks needed -- unlike v1's GM2A/PITPNA patches) equals its graph node count
  exactly, 35/35. Also ran a real end-to-end dataloader check
  (`PLIDataset.get()` with `use_esm3_v2_embeddings=True` on 20 real training
  samples): `plm` and `node_confidence` both load with the correct per-node shape,
  all confidence values finite and in `[0, 1]`.

- `training/read_configuration.py`: new flag `use_esm3_v2_embeddings` (+ CLI
  `--use_esm3_v2_embeddings`). When on:
    - `dataloader/New_dataloader.py` reads embeddings from `data/embedding_ESM3_v2/`
      instead of `data/embedding_ESM3/`, and applies only the standard BOS/EOS
      `[1:-1]` trim (the `GM2A`/`PITPNA` hard-coded extra trims are v1-pipeline-
      specific patches that should not apply to a freshly-generated v2 embedding --
      see 1.4's MSE finding).
    - `dataloader/New_dataloader.py` also loads
      `data/esm3_input/<stem>_node_confidence.csv` into a new
      `ProteinGraphData.node_confidence` field (only attached to the graph object
      when the flag is on, so PyG batch collation never sees a mix of tensor/None
      for this key within one run).
    - `architecture/interaction_classification.py`: when
      `attention_pooling_pocket_bias` is also on, the pocket-bias term in
      `AttentionPool` uses this real, continuous per-node confidence instead of the
      binary pocket flag from `pocketness.pdb` (`_pocket_pool_signal`, replacing the
      binary-only `_pool_pocket_mask` at all 3 call sites: the GRL adversary and both
      the single- and double-attention final-layer calls). Falls back to the
      original binary behaviour when the flag is off or confidence is unavailable.

  Verified (smoke tests, `/tmp/.../smoke_esm3v2.py`, not checked into the repo):
  default path unaffected by the new flag; forward+backward run with continuous
  confidence and `pocket_bias` receives gradient; changing the confidence values
  measurably changes the model's output (proves the values are consumed, not just
  accepted); graceful fallback to the binary mask when confidence is absent;
  combination with `prot_pooling_by_pockets` (confidence correctly restricted to the
  pocket-selected subset) all pass. Full existing test suite re-run: no new
  failures (same 27 pre-existing, unrelated failures as before this change, from
  stale test defaults -- `cross_attention`/`weight_decay` defaults drifted since
  those tests were written).

## 3. What remains open

- **Chain-break handling for internal gaps** (1.9): the `CHAINBREAK` token's
  applicability to unresolved intra-chain loops (as opposed to joining separate
  chains) was not confirmed against a live SDK run on a gapped protein (e.g. CERT).
- **Residue-order verification** (2.1): only embedding-row **count** is checked
  against graph-node count; true order-correctness needs a sequence alignment this
  audit did not implement.
- **v2 embeddings now exist for all 35 proteins** (generated and verified this
  session, see 2.5) -- `use_esm3_v2_embeddings=True` is ready to use for real
  training, not just architecturally wired.
- **Model comparison not yet run**: v2 embeddings exist but no training run has
  compared v1 vs v2 (or `attention_pooling_pocket_bias` binary vs continuous
  confidence) on the cold-split sweep yet -- the empirical payoff of the real
  structure/SASA/confidence tracks over sequence-only v1 is still unmeasured.
- **The leaked-looking HF token in `EmbedProtein.py:5` was not removed or rotated**
  -- flagged to the user, not acted on; worth deleting/rotating regardless of
  whether it turned out to be needed (it wasn't, for this checkpoint).
- **Secondary structure / function annotation tracks**: not attempted (1.8);
  would need `mkdssp` and real InterPro/GO annotations respectively.
