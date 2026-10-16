# Preprocessing tools and checkpoints

These tools produce files under `data/`. Keep track of their versions when rebuilding
outputs. Different versions can give different results for the same input.

## Voronota

Voronota builds protein graphs. The binary is `preprocessing/voronota-js` (14 MB).
Its version output is `Voronota-JS version 1.29`.

The release used for the reproduction check was `v1.29.4412`, dated 2025-06-15.
The wrapper is `preprocessing/voronota-js-receptor-data-graph`. It comes from the
release and has no project changes.

Protein parameters are in `data/unpreprocessed_files/voronota_parameter_per_ltp.csv`.
The driver is `data/graphs/graph_from_pdb.py`. It pairs structures and parameter rows
by position, so check their order before running it.

For each protein, the output folder `data/graphs/<stem>/` contains:

- `coarse_graph_nodes.csv` and `coarse_graph_links.csv`;
- `graph_nodes.csv` and `graph_links.csv`;
- `pocketness.pdb`, `buriedness.pdb`, and `coarse_mean_buriedness.pdb`.

### Version check

The original version was not recorded. The wrapper was compared with its repository
history and upstream releases. After converting line endings to LF, its MD5 was
`22bcc6c201be9e188459f93566f82169`. It matched four releases: `v1.29.4307`,
`v1.29.4370`, `v1.29.4408`, and `v1.29.4412`.

A build of `v1.29.4412` was then run on `GM2A_1g13.pdb1` with the stored parameters.
All seven outputs matched the committed files after accounting for CRLF line endings.
This check supports the four-release range; it does not identify one unique release.

### Build from source

```bash
curl -sSL -o v.tar.gz https://github.com/kliment-olechnovic/voronota/archive/refs/tags/v1.29.4412.tar.gz
tar xzf v.tar.gz
cd voronota-1.29.4412/expansion_js
g++ -std=c++14 -I"./src/dependencies" -O3 -o ./voronota-js $(find ./src/ -name '*.cpp')
```

Keep `src/`, `expansion_js/`, and `expansion_lt/` from the archive.
The wrapper needs `voronota-js` on `PATH`. Its line endings are CRLF;
convert them with `tr -d '\r'` before running it on Linux.

### Selenomethionine

The Voronota filter `voronota_restrict_atoms("-use", "[-protein]")` drops
`HETATM ... MSE` records. This removes those residues from the graph.
`preprocessing/convert_mse_to_met.py` converts them to ordinary methionine first.
The converted structures are in `data/structures/mse_fixed/`.
The affected proteins in this dataset are `GM2A_1g13` and `PITPNA_1uw5`.

## ESM3

The project uses the `esm3-sm-open-v1` checkpoint from
`EvolutionaryScale/esm3-sm-open-v1` on Hugging Face. The recorded Python package
version is `esm` 3.2.3. The package resolves the checkpoint name and downloads it
through `huggingface_hub.snapshot_download`.

The recorded access check found the repository public and ungated. It downloaded
without credentials. The script still uses `HF_TOKEN` or `HF_API_TOKEN` when set.

`preprocessing/embeddings/embed_protein_esm3_v2.py` sets the default `HF_HOME` before
importing `esm`. An existing `HF_HOME` is kept. The default cache is
`data/esm3_checkpoint`, which is ignored by Git. The recorded cache had 22 files
and used 5.2 GB.

The two embedding formats are:

- v1: sequence input from `data/fasta/`; output in `data/embedding_ESM3/<stem>_*_ESM3.pkl`.
- v2: sequence, structure, SASA, and confidence from `data/esm3_input/<stem>.pdb`;
  output in `data/embedding_ESM3_v2/<stem>_ESM3v2.pkl`.

Both formats include BOS and EOS rows around the residue rows.
The loader removes the first and last rows before assigning embeddings to graph nodes.

### Run

```bash
pip install esm
python3 preprocessing/embeddings/embed_protein_esm3_v2.py data/esm3_input/<stem>.pdb
```

The first run downloads the checkpoint. Later runs use the cache.
Recorded CPU timings were about two minutes for the download and one minute per protein.
These timings depend on the machine and connection.

### Old token

An earlier check found an expired, commented-out `HF_API_TOKEN` in
`preprocessing/EmbedProtein.py:5`. It had been committed to source.
Do not restore or reuse it. In that check, passing the expired token caused a 401
response, while the anonymous download worked.

### Reproducibility check

An ATCAY embedding was rebuilt on CPU and compared with the stored tensor.
The maximum absolute difference was 0.0068 and the mean difference was 2.3e-4.
The stored values had a standard deviation of 276. The relative difference was
8e-7, and the cosine similarity for each residue was at least 0.9999997.
This check did not show bit-for-bit agreement across machines.

## RNA-BAnG

The source is in `external/RNA-BAnG`. The checkpoint is
`external/RNA-BAnG/ckpt/icml.pth`, included in that repository without an access gate.
The environment is described in `external/RNA-BAnG/environment.yml`.
The recorded minimum additions to this project's PyTorch environment were
`gemmi`, `einops`, and `omegaconf`.

Inputs are `data/esm3_input/*.pdb`, aligned to `coarse_graph_nodes.csv`.
Outputs are `data/embedding_RNABANG/<stem>_RNABANG.pkl`.
Each output has one row per graph node, without BOS or EOS rows.

In the recorded CPU check, rerunning ATCAY gave exactly the stored tensor
(`torch.equal` returned true). Repeat this check before replacing stored embeddings.

## Foldseek

Foldseek is a separate C++ program. It produces 3Di tokens used by
`--deepclip_protein_tokens`.

The recorded installation is `~/tools/foldseek/bin/foldseek`.
`FOLDSEEK_PATH` in `preprocessing/build_foldseek_3di.py` sets this path.

The authors provide the AVX2 build at
https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz.
For machines without AVX2, the archive is `foldseek-linux-sse2.tar.gz` at the same site.

Recorded AVX2 archive SHA256:
`f886374e29ebbf03849cd9c4c8929be00904856dd271627d8c3043607e2af95a`.
Recorded `foldseek version`: `463739e0014a1549a527de589102cde98f802f37`.

Download and unpack the binary:

```bash
mkdir -p ~/tools
curl -sSL -o ~/tools/foldseek-linux-avx2.tar.gz https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz
sha256sum ~/tools/foldseek-linux-avx2.tar.gz
tar xzf ~/tools/foldseek-linux-avx2.tar.gz -C ~/tools
```

Compare the archive hash with the recorded value above. The download URL serves
the latest build, so the version may change.

Run the script from the project root:

```bash
python3 preprocessing/build_foldseek_3di.py
```

The script calls `createdb --chain-name-mode 0 --threads 1`, then `lndb` and
`convert2fasta`. It checks each protein sequence against its graph.
If the Foldseek version changes, rebuild `data/protein_3di.csv` and compare it
with the stored file before replacing it.
