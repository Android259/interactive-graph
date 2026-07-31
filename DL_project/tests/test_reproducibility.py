import random

import numpy as np
import torch

from training.reproducibility import (
    seed_everything,
    seed_worker,
    seeded_generator,
)


def sample_random_values():
    return (
        random.random(),
        float(np.random.random()),
        float(torch.rand(1)),
    )


def test_seed_everything_reproduces_python_numpy_and_torch():
    seed_everything(17)
    first = sample_random_values()
    seed_everything(17)
    second = sample_random_values()

    assert first == second


def test_seed_worker_reproduces_python_and_numpy(monkeypatch):
    monkeypatch.setattr(torch, "initial_seed", lambda: 123456)

    seed_worker(0)
    first = (random.random(), float(np.random.random()))
    seed_worker(1)
    second = (random.random(), float(np.random.random()))

    assert first == second


def test_seeded_generator_uses_requested_seed():
    assert seeded_generator(23).initial_seed() == 23
