# Architecture Contract

## Active Flow

`InteractionClassification` composes:

```text
Protein_encoder + Lipid_encoder
  -> optional self-attention
  -> optional bidirectional cross-attention
  -> optional second encoder + cross-attention block
  -> configured graph pooling
  -> Final_Layer
  -> [batch, 2] logits
```

`HybridPred.py` is legacy; ignore it unless explicitly requested.

## Tensor Contracts

| Input | Shape / dtype |
|---|---|
| protein node | `[N, 3]`, float32 |
| protein PLM | `[N, 1536]`, projected to `config.plm_compression_dim` |
| protein buriedness | `[N]`, float32 |
| protein edge attr | `[E, 3]`, float32 |
| legacy lipid node | `[N, 768]`, float32 |
| graph lipid node | `[N, 11]`, float32 |
| graph lipid edge attr | `[E, 6]`, float32 |
| edge indices / CE labels | long |
| encoder output | `[N, hiddim]` |
| classifier output | `[batch, 2]` logits |

GAT output before projection is `hiddim * HEADS`. PyG `batch` is sample membership; `lipid_batch` is fragment membership.

## Attention And Pooling Contracts

- Boolean attention masks use shape `[query_nodes, key_nodes]`; `True` blocks a
  query-key pair.
- Protein and lipid self-attention may only connect nodes with equal sample
  batch IDs.
- Lipid-query cross-attention uses `[N_lipid, N_protein]`; protein-query
  cross-attention uses `[N_protein, N_lipid]`.
- Fragment masking is combined with sample masking. It must not permit
  attention across samples even when fragment IDs coincide.
- `prot_attention_pos_bias` adds a learnable bias to pocket protein keys in
  protein self-attention and, when cross-attention is active, lipid-query
  cross-attention. It does not remove non-pocket nodes.
- `prot_pooling_by_pockets` filters protein nodes only immediately before final
  pooling. Every sample must retain at least one pocket node.
- `double_attention` must execute `cross_attention1`, then the second protein
  and lipid encoders, then `cross_attention2`.
- Optional modules are created only for active modes; active trainable
  parameters should receive gradients in CPU smoke tests. This is enforced by
  `test_active_configuration_has_no_parameters_without_gradients` and is load-bearing:
  a module built but never reached inflates `number_of_parameters`, which names run
  directories and is a column of `metrics_summary.csv`. `protein_encoder.encodin2` is
  `None` under `single_gat_layer` for exactly this reason.

## Adversarial Heads (`final_layer.py`)

Two independent gradient-reversal mechanisms live in `Final_Layer`. Both are off by
default and neither changes the classifier's output.

| | `adversarial_grl` | `dann_family` |
|---|---|---|
| reads | each pooled partner **before** cross-attention | the **fused** vector, after cross-attention |
| predicts | the binding label | which of 9 protein families (`PROTEIN_FAMILY_COUNT`) |
| stashes | `_adv` = `(lip_logits, prot_logits)` | `_dann_features` (reversed features, not logits) |

- The pre/post-cross-attention split is the contract, not an implementation detail.
  `compute_adversary` must be called from the model forward **before**
  `cross_attention1`: cross-attention adds each partner into the other residually, so
  after it there is no single-partner representation left to test. The family head is
  the opposite case and must read the fused vector, which is the only place the
  per-partner adversary cannot reach.
- Both stash `None` outside `self.training`, so no stale tensor can be read in eval.
- `adv_lipid` / `adv_protein` select which sides run; a disabled side is not built at
  all and its entry in `_adv` is `None`. `dann_class_conditional` (default on) builds
  one family head per binding label.
- Penalties are **averaged** over the active sides/classes, never summed, so
  `adv_weight` / `dann_weight` mean the same pressure regardless of how many sides or
  classes a configuration or a batch happens to have. Summing would silently make
  ablations uncontrolled.
- `family_dann_loss` rejects an all-zero family one-hot rather than letting `argmax`
  relabel the sample as the first family.
- Reversal strength is read from `adv_lambda_now` / `dann_lambda_now` on the module,
  which the training loop rewrites once per epoch when a ramp is enabled. The architecture
  never reads `config.adv_lambda` directly during forward.
- `adv_deep` swaps the 2-layer probe for `ResidualAdversary`, which mirrors one side of
  the cross-attention block with the multihead replaced by an MLP of width `2 * dim`
  (the same `4 * dim^2` the Q/K/V/O projections spend). It is sized to that budget, not
  to `m`; the gap to the real block is exactly `dim` in bias count.

## Change Rules

- Preserve both lipid paths; `lipid_isomers` selects graph mode.
- `lip_edgidx` and `lip_e_attr` are mandatory only in graph mode.
- `lipid_batch` is mandatory only with `lipid_fragments_mask`.
- Keep attention masks boolean and aligned with all batched nodes.
- Keep pooling batch vectors aligned after any node filtering.
- A forward/signature/shape change must be synchronized with:
  - `training/new_train.py` train, validation, and test calls;
  - `dataloader/Dataloader.py`;
  - `tests/test_lipid_encoder.py`;
  - `tests/test_training_smoke_integration.py`.
- Preserve `GRAB_loss` normalization and commented historical loss unless explicitly changed.
- Do not refactor duplicated or suspicious existing behavior unless it is part of the request.

## Verify

```bash
python3 -m pytest tests/test_lipid_encoder.py tests/test_loss.py
python3 -m pytest tests/test_training_smoke_integration.py
```
