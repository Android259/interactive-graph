# Training Instructions

- `read_configuration.py` uses a custom parser, not `argparse`.
- Add only requested flags; do not invent complementary `--no_*` flags. The ones that
  exist (`--no_tanimoto_weight`, `--no_class_weights`, `--no_cross_attention`,
  `--no_adv_lipid`, `--no_adv_protein`) are the exceptions, each added because the
  option defaults to on and an experiment needed it off.
- Adversary reversal strength is **not** read from the config during forward. The epoch
  loop computes it (`ramped_adv_lambda`, `adv_fit_progress`) and writes
  `model.final_layer.adv_lambda_now` / `dann_lambda_now`. Per-epoch training state
  belongs on the module, never on `conf`: the run report dumps `vars(conf)`, so a value
  stored there would be written out as if it were a hyperparameter.
- `adv_lambda_ramp_by_fit` takes precedence over `adv_lambda_ramp`, and
  `dann_lambda_ramp_by_fit` over `dann_lambda_ramp`. Both read the same ratcheted
  `fit_progress` counter in the epoch loop — it measures the model, not a head. That
  progress must stay ratcheted: lambda changes the fit it is derived from, so a freely
  falling progress would oscillate instead of converging.
- Adversary penalties are added to the backward pass *after* `update_aggregate` has
  banked the task loss, so `epoch/train loss` stays the task loss alone.
  `log_adversary_metrics` writes them separately, together with the lambdas in force.
  Reference values when reading those curves: `ln 2 = 0.693` for the 2-class per-partner
  adversaries, `ln 9 = 2.197` for the 9-class family head.
- New options must preserve defaults and update `tests/test_read_configuration.py`.
- Lipid modes: `0=concat`, `1=random_choice`, `2=fragments_mask`.
- Protein modes: `0=ordinary`, `1=pocket positional bias in protein attention
  and lipid-query cross-attention`, `2=pocket-only protein pooling`.
- `double_attention` implies `cross_attention`; validate that `hiddim` is
  divisible by `HEADS`.
- `weight_decay` is passed to Adam and defaults to `1e-5`.
- `final_m` carries its own default (`4`); `None` is still honoured as "follow `m`",
  which is the path `Final_Layer` and `new_train.py` take when a run does not set it.
- `disable_early_stopping` defaults to `True` — runs are scored on the whole curve.
- `type_opt` enables AMP only on CUDA; CPU must remain valid.
- Call `seed_everything` before model and DataLoader creation.
- Keep independent seeded generators for train, validation, and test loaders.
  `seed_worker` gives each worker a reproducible derived Python/NumPy seed.
- Seeds provide reproducible splitting and CPU-side randomness, but do not by
  themselves guarantee bitwise-identical CUDA execution.
- Do not import `new_train.py` from tests. It executes setup at import time, writes artifacts, starts TensorBoard, and may open a browser.
- Do not run full epochs, GPU training, TensorBoard, or save checkpoints/metrics unless explicitly requested.
- Do not alter `non_blocking=True`, dtype policy, AMP, or GradScaler behavior without explicit instruction.
- CPU smoke tests validate shapes, finite loss, backward, gradients, and optimizer step; they do not prove quality, CUDA speed, or CUDA memory safety.

Verify with:

```bash
python3 -m pytest tests/test_read_configuration.py
python3 -m pytest tests/test_reproducibility.py
python3 -m pytest tests/test_training_smoke_integration.py
```
