"""The objects one training run is made of, built once by new_train.main().

Passed to the epoch loop (epoch_loop.py) and the test pass (final_evaluation.py) instead
of module-level globals, so each of them states what it reads.
"""

from dataclasses import dataclass
from typing import Any, Optional

import torch

from branch_dynamics import BranchDynamics
from optimizer_setup import OptimizerSetup
from run_paths import RunPaths
from task_losses import TaskLosses


@dataclass
class RunContext:
    conf: Any
    device: torch.device
    model: torch.nn.Module
    train_dataset: Any
    train_loader: Any
    valid_loader: Any
    test_loader: Any
    # The per-epoch cap on training batches (1740 rows' worth, see new_train.main).
    train_batches_to_run: int
    losses: TaskLosses
    optim: OptimizerSetup
    use_amp: bool
    scaler: Any
    # Endless validation batches for the bilevel gate step; None unless --bilevel.
    hyper_val_iter: Optional[Any]
    writer: Any
    dynamics: BranchDynamics
    paths: RunPaths
    number_of_parameters: int
    # Rewritten at the top of every epoch from conf.ramped_lipid_path_weight; starts at
    # conf.lipid_path_weight so the TensorBoard logger has it whatever order the first
    # epoch runs in.
    lipid_path_weight_now: float
