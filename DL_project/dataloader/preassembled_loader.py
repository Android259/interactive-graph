"""One split's samples preassembled into device tensors, batched by indexing.

Applies only under --deepclip or dh/mlp (descriptor_catalog_only): tiny models where
PyG re-collating every sample, every batch, every epoch costs more than the model's
own arithmetic. Not usable for a real protein/lipid graph -- raises on any node-level
field (_NODE_LEVEL_KEYS) or a lipid with more than just `x`.

Nothing here is re-implemented, only replayed, so batch order and candidate draws stay
bit-identical to the DataLoader this replaces: the original batch sampler and its
base-seed draw are reused, and lipid_random_choice's draw is replayed from the same
process-wide generator in the same order -- which needs num_workers=0, since a worker's
draw can't be observed from here (a drawn split with workers is not preassembled).

Yields the same attributes a collated PyG batch would: graph-level fields concatenated,
lipid as architecture/deepclip.py's own padded `x`/`mask` (+ `lengths` on the CPU).
"""

import random

import torch


# Node-level protein fields. --deepclip's samples carry none of them (Dataloader.get);
# one showing up means the sample is not what this module was written for.
_NODE_LEVEL_KEYS = frozenset({
    "x", "edge_index", "edge_attr", "bury", "plm", "pocket", "geometric_node_attr",
    "edge_node_pairs", "edge_node_degree", "frame_rotation", "frame_translation",
    "node_confidence",
})


class PreassembledBatch:
    """Attribute bag standing in for one PyG batch (protein side or lipid side)."""

    def __init__(self, fields, host_fields=()):
        self.__dict__.update(fields)
        self._host_fields = frozenset(host_fields)

    def to(self, device, non_blocking=False):
        """Everything already lives on the loader's device; `lengths` stays on the host."""
        moved = {}
        for key, value in self.__dict__.items():
            if key == "_host_fields":
                continue
            if isinstance(value, torch.Tensor) and key not in self._host_fields:
                value = value.to(device, non_blocking=non_blocking)
            moved[key] = value
        return PreassembledBatch(moved, self._host_fields)


def preassembly_mode(dataset, num_workers=0):
    """"fixed", "drawn", or None when this split cannot be preassembled.

    Dataloader.__iter__ turns the sample cache off exactly when a sample changes from
    one access to the next. "fixed": it never does. "drawn": the only thing that
    changes is the lipid candidate (lipid_random_choice), which is replayed per access.
    Residue subsampling also switches the cache off; it draws inside the protein graph
    and is not replayed, so such a split stays None.
    "drawn" needs num_workers=0: with workers the draws happen in the worker processes.
    """
    if getattr(dataset, "_sample_cache_enabled", False):
        return "fixed"
    if (
        getattr(dataset, "_draw_lipid_candidate", False)
        and not getattr(dataset, "_augment_residues", False)
        and getattr(dataset, "_candidate_index_by_idx", None) is None
        and num_workers == 0
    ):
        return "drawn"
    return None


class PreassembledLoader:
    """Iterate `loader`'s batches from tensors built once, in the order it would have."""

    def __init__(self, loader, device):
        dataset = loader.dataset
        self._mode = preassembly_mode(dataset, loader.num_workers)
        if self._mode is None:
            raise ValueError(
                "preassembly needs samples that are fixed for the run, or differ only "
                "by the lipid candidate drawn in this process (num_workers=0)"
            )
        self._batch_sampler = loader.batch_sampler
        self._generator = loader.generator
        self._num_workers = int(loader.num_workers)
        self._persistent = bool(loader.persistent_workers) and self._num_workers > 0
        self._base_seed_drawn = False
        self._device = device

        # One variant per (row, candidate): the row's candidates are variants
        # first[idx] .. first[idx] + count[idx] - 1. A "fixed" split has one each.
        if self._mode == "drawn":
            self._candidate_counts = [
                dataset.candidate_count(idx) for idx in range(len(dataset))
            ]
            samples = [
                dataset.sample_for_candidate(idx, candidate)
                for idx, count in enumerate(self._candidate_counts)
                for candidate in range(count)
            ]
        else:
            self._candidate_counts = [1] * len(dataset)
            samples = [dataset[idx] for idx in range(len(dataset))]
        first = 0
        self._first_variant = []
        for count in self._candidate_counts:
            self._first_variant.append(first)
            first += count

        protein_rows = {}
        lipid_rows = []
        for protein_graph, lipid_graph in samples:
            for key in protein_graph.keys():
                if key in _NODE_LEVEL_KEYS:
                    raise ValueError(
                        f"preassembly handles graph-level fields only, got {key!r}"
                    )
                protein_rows.setdefault(key, []).append(protein_graph[key])
            lipid_keys = set(lipid_graph.keys())
            if lipid_keys == set():
                lipid_rows.append(None)
                continue
            if lipid_keys != {"x"}:
                raise ValueError(
                    "preassembly expects the lipid as one-hot characters alone, got "
                    f"{sorted(lipid_graph.keys())}"
                )
            lipid_rows.append(lipid_graph.x)
        count = len(lipid_rows)
        if any(row is None for row in lipid_rows) and not all(
            row is None for row in lipid_rows
        ):
            raise ValueError("some samples carry a lipid and some do not")
        for key, rows in protein_rows.items():
            if len(rows) != count:
                raise ValueError(f"{key!r} is missing from some samples")

        # One stacked tensor per field, [variants, *per-sample shape]. A batch is
        # stacked[variants] reshaped to what torch.cat over the samples gives -- the
        # first two axes merged -- or left [batch] for a 0-dim field, which PyG stacks.
        self._protein_fields = {
            key: torch.stack(rows).to(device) for key, rows in protein_rows.items()
        }

        self._has_lipid = lipid_rows[0] is not None
        if not self._has_lipid:
            return
        lengths = torch.tensor([row.shape[0] for row in lipid_rows], dtype=torch.long)
        longest = int(lengths.max())
        width = lipid_rows[0].shape[1]
        dense = torch.zeros((count, longest, width), dtype=lipid_rows[0].dtype)
        mask = torch.zeros((count, longest), dtype=torch.bool)
        for row, (length, x) in enumerate(zip(lengths.tolist(), lipid_rows)):
            dense[row, :length] = x
            mask[row, :length] = True
        self._lengths = lengths
        self._dense = dense.to(device)
        self._mask = mask.to(device)

    def __len__(self):
        return len(self._batch_sampler)

    def _variants(self, indices):
        """The variant each row of the batch is served as -- drawn exactly as get() draws."""
        if self._mode == "fixed":
            return [self._first_variant[idx] for idx in indices]
        return [
            self._first_variant[idx] + random.choice(range(self._candidate_counts[idx]))
            for idx in indices
        ]

    def _batch(self, indices):
        host_index = torch.as_tensor(self._variants(indices), dtype=torch.long)
        index = host_index.to(self._device)
        protein = {}
        for key, stacked in self._protein_fields.items():
            picked = stacked.index_select(0, index)
            if picked.dim() > 2:
                picked = picked.reshape(-1, *picked.shape[2:])
            elif picked.dim() == 2:
                picked = picked.reshape(-1)
            protein[key] = picked
        protein["num_graphs"] = len(indices)
        if not self._has_lipid:
            return PreassembledBatch(protein), PreassembledBatch({"x": None, "batch": None})
        lengths = self._lengths.index_select(0, host_index)
        longest = int(lengths.max())
        lipid = {
            "x": self._dense.index_select(0, index)[:, :longest].contiguous(),
            "mask": self._mask.index_select(0, index)[:, :longest].contiguous(),
            "lengths": lengths,
            "batch": None,
        }
        return (
            PreassembledBatch(protein),
            PreassembledBatch(lipid, host_fields=("lengths",)),
        )

    def __iter__(self):
        # _BaseDataLoaderIter.__init__'s base-seed draw, reproduced for its effect on
        # the loader's generator. Before the sampler runs, as in the DataLoader, where
        # the batch sampler's generator function only starts drawing on first next().
        if not (self._persistent and self._base_seed_drawn):
            torch.empty((), dtype=torch.int64).random_(generator=self._generator)
            self._base_seed_drawn = True
        for indices in self._batch_sampler:
            yield self._batch(indices)
