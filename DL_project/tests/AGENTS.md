# Test Instructions

- Tests must be independent, deterministic where randomness matters, and fast enough for CPU execution.
- Use temporary files, small DataFrames, mocks, and synthetic tensors. Do not rewrite or depend on the full generated dataset.
- Test pair-ID versus compact-position alignment separately; ordered synthetic
  fixtures should make accidental CSV-row indexing observable.
- For attention masks, use batches with unequal node counts and verify both
  shape and allowed query-key membership.
- Reproducibility tests cover Python, NumPy, PyTorch, worker seeds, and
  DataLoader generators. They do not establish bitwise CUDA determinism.
- Never import `training/new_train.py`.
- Do not save checkpoints, metrics, TensorBoard logs, or miniature training results.
- Integration tests should validate output shapes, finite values, loss, backward, finite gradients, and optimizer step.
- `tracemalloc` checks Python allocation growth, not CUDA allocator leakage.
- `py_compile` is only syntax validation and is not equivalent to passing pytest.

Focused commands:

```bash
python3 -m pytest tests/test_read_configuration.py
python3 -m pytest tests/test_lipid_encoder.py
python3 -m pytest tests/test_new_dataloader_lipid_graphs.py
python3 -m pytest tests/test_pair_index_alignment.py
python3 -m pytest tests/test_grab_graph.py tests/test_loss.py
python3 -m pytest tests/test_reproducibility.py
python3 -m pytest tests/test_training_smoke_integration.py
```

Full verification:

```bash
python3 -m pytest tests
```

The current collection contains `304` tests. Prefer reporting the command and
actual result rather than treating that count as a permanent expected value.

When a test fails, first decide whether the test or the code drifted — both happen
here, and the answer is not always "fix the test":

- `test_active_configuration_has_no_parameters_without_gradients` failing means a module
  is built but never reached. That is a code bug (it inflates `number_of_parameters`),
  not a test to relax.
- Defaults move (`final_m`, `weight_decay`, `disable_early_stopping`, `heads` → `HEADS`),
  and column sets move (`architecture` dropped, `num_workers` added). Those are test
  drift; update the expectation and say what the new value is.
- Loss tests encode a formulation, not just numbers. `Non_Negative_Positive_Unlabeled_loss`
  uses a softplus surrogate on the margin `outl[:,1] - outl[:,0]`, averages the marginal
  term over the **whole batch**, and its nnPU correction is straight-through: the value
  is `positive_risk - beta` while the gradient is `-gamma * negative_risk`. Assert both
  separately.
- Prefer the real `ModelConfig` over a hand-listed `SimpleNamespace` stub. Stubs only get
  fixed once each newly-read config field crashes a test.
