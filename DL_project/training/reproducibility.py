import random

import numpy as np
import torch


def seed_everything(seed):
    """Seed Python, NumPy, and PyTorch random number generators."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def seed_worker(_worker_id):
    """Seed a DataLoader worker from its PyTorch-derived initial seed."""
    worker_seed = torch.initial_seed() % (2 ** 32)
    random.seed(worker_seed)
    np.random.seed(worker_seed)


def seeded_generator(seed):
    """Create a PyTorch generator initialized with the requested seed."""
    return torch.Generator().manual_seed(seed)
