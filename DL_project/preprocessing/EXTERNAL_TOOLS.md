# External tools and model checkpoints used by preprocessing

Everything here is a hard dependency of a preprocessing step that produces files under
`data/`. Versions are recorded because the outputs are committed artifacts: a different
version silently produces different numbers for the same input.

## Voronota (protein graphs)

| item | value |
|---|---|
| engine | `preprocessing/voronota-js` (committed, 14 MB, `--version` prints `Voronota-JS version 1.29`) |
| release | **v1.29.4412** (upstream tag, 2025-06-15) |
| wrapper script | `preprocessing/voronota-js-receptor-data-graph` (shipped with the release, unmodified) |
| per-protein parameters | `preprocessing/voronota_parameter_per_ltp.csv` |
| driver | `data/graphs/graph_from_pdb.py` (positional pairing of structures to parameter rows -- verify before reusing) |
| outputs | `data/graphs/<stem>/{coarse_graph_nodes,coarse_graph_links,graph_nodes,graph_links}.csv`, `pocketness.pdb`, `buriedness.pdb`, `coarse_mean_buriedness.pdb` |

### How the version was established

The project never recorded it. The wrapper script is byte-identical across every commit
in this repository (md5 of the LF-normalized file: `22bcc6c201be9e188459f93566f82169`)
and matches exactly four consecutive upstream releases -- v1.29.4307, v1.29.4370,
v1.29.4408, v1.29.4412 -- while differing from every release before and after that
range. v1.29.4412 was then built from source and re-run on `GM2A_1g13.pdb1` with that
protein's stored parameters: all seven output files reproduced the committed ones
byte-for-byte (only line endings differ, the stored files are CRLF). That is the
confirmation; any release in the four-tag window is equally consistent with the data.

### Rebuilding the engine from source

```
curl -sSL -o v.tar.gz https://github.com/kliment-olechnovic/voronota/archive/refs/tags/v1.29.4412.tar.gz
tar xzf v.tar.gz            # src/, expansion_js/ and expansion_lt/ are all required
cd voronota-1.29.4412/expansion_js
g++ -std=c++14 -I"./src/dependencies" -O3 -o ./voronota-js $(find ./src/ -name '*.cpp')
```

Takes about three minutes. The wrapper needs `voronota-js` on `PATH`, and it is written
with CRLF line endings -- run it through `tr -d '\r'` before executing on Linux.

### Selenomethionine

Voronota's `voronota_restrict_atoms("-use", "[-protein]")` drops `HETATM ... MSE`
records, deleting real residues from the graph. `preprocessing/convert_mse_to_met.py`
rewrites them as ordinary methionine first; the converted structures live in
`data/structures/mse_fixed/`. Only `GM2A_1g13` and `PITPNA_1uw5` are affected in this
dataset.

## ESM3 (protein language model embeddings)

| item | value |
|---|---|
| checkpoint name | **`esm3-sm-open-v1`** (the only one this project has ever used) |
| Hugging Face repo | `EvolutionaryScale/esm3-sm-open-v1` -- **no longer gated** (`gated: false`, `private: false`), downloads anonymously |
| python package | `esm` 3.2.3 (`pip install esm`); it resolves the checkpoint name internally and downloads via `huggingface_hub.snapshot_download` |
| local cache | `data/esm3_checkpoint` (5.2 GB, 22 files, git-ignored), set through `HF_HOME` by `preprocessing/embed_protein_esm3_v2.py` before importing `esm` |
| credentials | none needed. `HF_TOKEN` / `HF_API_TOKEN` are still honoured if set, but the download works without them |
| v1 outputs | `data/embedding_ESM3/<stem>_*_ESM3.pkl` -- sequence track only, built from `data/fasta/` |
| v2 outputs | `data/embedding_ESM3_v2/<stem>_ESM3v2.pkl` -- sequence + structure + SASA + confidence, built from `data/esm3_input/<stem>.pdb` |

Both variants store one row per residue plus a BOS/EOS pair, so the loader strips the
first and last row before attaching them to graph nodes.

### Running it

```
pip install esm
python3 preprocessing/embed_protein_esm3_v2.py data/esm3_input/<stem>.pdb
```

The first run downloads the checkpoint into `data/esm3_checkpoint` (about two minutes);
later runs reuse it. CPU inference works -- roughly a minute per protein at these sizes.

### Token status

`preprocessing/EmbedProtein.py:5` contains a commented-out `HF_API_TOKEN`. It is
**expired** (the API answers `User Access Token "jesperecamarchefdp" is expired`) and it
is committed in source, so treat it as compromised regardless: rotate it, do not restore
it. Nothing here needs it -- passing it actually breaks the download that works
anonymously, because an expired bearer token turns a public 200 into a 401.

### Reproducibility

Re-embedding is deterministic in structure but not bit-exact across machines. Control
run: an untouched protein (ATCAY) re-embedded on CPU differed from the committed tensor
by at most 0.0068 in absolute value, mean 2.3e-4, against a value spread of std 276 --
a relative difference of 8e-7, with per-residue cosine similarity >= 0.9999997. That is
floating-point kernel variation (the stored tensors were produced on other hardware),
not a pipeline difference. GM2A and PITPNA were re-embedded on CPU on that basis; the
other 33 proteins keep their original tensors untouched.

## RNA-BAnG (alternative per-residue protein representation)

| item | value |
|---|---|
| checkout | `external/RNA-BAnG` (official repository) |
| checkpoint | `external/RNA-BAnG/ckpt/icml.pth` (committed, no gating) |
| environment | `external/RNA-BAnG/environment.yml`; the minimum needed on top of this project's own torch is `gemmi`, `einops`, `omegaconf` |
| inputs | `data/esm3_input/*.pdb` (already aligned to `coarse_graph_nodes.csv`) |
| outputs | `data/embedding_RNABANG/<stem>_RNABANG.pkl`, no BOS/EOS, exactly one row per graph node |

CPU inference is deterministic here: re-running an untouched protein (ATCAY) reproduced
the committed tensor exactly (`torch.equal` true), which is the check to repeat before
overwriting any stored embedding.
