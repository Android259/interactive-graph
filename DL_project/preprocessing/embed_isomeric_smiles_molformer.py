#!/usr/bin/env python3

import argparse
import importlib.machinery
import os
import pickle as pkl
import sys
import types
from argparse import Namespace
from pathlib import Path

from rdkit import Chem


DEFAULT_INPUT = Path("preprocessing/isomeric_smiles_before_encoding.pkl")
DEFAULT_OUTPUT = Path("data/lipid_SMILES_isomeric_embedding.pkl")
DEFAULT_HPARAMS = Path("../../data/Pretrained MoLFormer/hparams.yaml")
DEFAULT_CHECKPOINT = Path(
    "../../data/Pretrained MoLFormer/checkpoints/N-Step-Checkpoint_3_30000.ckpt"
)
DEFAULT_VOCAB = Path("bert_vocab.txt")
EMPTY_VALUES = {"", "0", "Empty", "NonConclusive", "nan", "NaN", "None"}


def resolve_path(path, base_dir):
    path = Path(path)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def canonicalize_isomeric(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def normalize_smiles(smiles_list):
    normalized = []
    seen = set()
    invalid = []
    for raw in smiles_list:
        text = "" if raw is None else str(raw).strip()
        if text in EMPTY_VALUES:
            continue
        canonical = canonicalize_isomeric(text)
        if canonical is None:
            invalid.append(text)
            continue
        if canonical not in seen:
            normalized.append(canonical)
            seen.add(canonical)
    return normalized, invalid


def batch_split(items, batch_size):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def load_molformer(molformer_dir, hparams_path, checkpoint_path, vocab_path, device):
    import rdkit  # Load RDKit before torch to keep conda libstdc++ resolution stable.
    import torch
    import yaml

    sys.path.insert(0, str(molformer_dir))
    if "apex" not in sys.modules:
        apex = types.ModuleType("apex")
        apex.__path__ = []
        apex.__spec__ = importlib.machinery.ModuleSpec("apex", loader=None, is_package=True)
        apex.optimizers = types.ModuleType("apex.optimizers")
        apex.optimizers.__spec__ = importlib.machinery.ModuleSpec(
            "apex.optimizers", loader=None
        )
        apex.amp = types.ModuleType("apex.amp")
        apex.amp.__spec__ = importlib.machinery.ModuleSpec("apex.amp", loader=None)
        sys.modules["apex"] = apex
        sys.modules["apex.optimizers"] = apex.optimizers
        sys.modules["apex.amp"] = apex.amp

    from tokenizer.tokenizer import MolTranBertTokenizer
    from train_pubchem_light import LightningModule

    with open(hparams_path, "r") as handle:
        config = Namespace(**yaml.safe_load(handle))

    tokenizer = MolTranBertTokenizer(str(vocab_path))
    old_cwd = os.getcwd()
    original_torch_load = torch.load

    def torch_load_legacy(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return original_torch_load(*args, **kwargs)

    try:
        torch.load = torch_load_legacy
        os.chdir(molformer_dir)
        model = LightningModule(config, tokenizer.vocab).load_from_checkpoint(
            str(checkpoint_path),
            config=config,
            vocab=tokenizer.vocab,
        )
    finally:
        torch.load = original_torch_load
        os.chdir(old_cwd)
    model.eval()
    model.to(device)
    return model, tokenizer


def embed_smiles(model, tokenizer, smiles_list, batch_size, device):
    import torch
    from fast_transformers.masking import LengthMask

    embeddings = {}
    with torch.no_grad():
        for batch in batch_split(smiles_list, batch_size):
            encoded = tokenizer(
                batch,
                padding=True,
                add_special_tokens=True,
            )
            idx = torch.tensor(encoded["input_ids"], device=device)
            mask = torch.tensor(encoded["attention_mask"], device=device)
            token_embeddings = model.blocks(
                model.tok_emb(idx),
                length_mask=LengthMask(mask.sum(-1)),
            ).detach().cpu()

            for smiles, embedding, seq_len in zip(
                batch,
                token_embeddings,
                mask.sum(-1).detach().cpu().tolist(),
            ):
                embeddings[smiles] = embedding[:seq_len].unsqueeze(0).contiguous()
    return embeddings


def main():
    parser = argparse.ArgumentParser(
        description="Create MolFormer token embeddings for canonical isomeric lipid SMILES."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--molformer-dir",
        type=Path,
        required=True,
        help="Directory containing tokenizer/ and train_pubchem_light.py.",
    )
    parser.add_argument("--hparams", type=Path, default=DEFAULT_HPARAMS)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--vocab", type=Path, default=DEFAULT_VOCAB)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
    )
    parser.add_argument(
        "--skip-canonicalization",
        action="store_true",
        help="Trust input SMILES are already canonical isomeric strings.",
    )
    args = parser.parse_args()

    import torch

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    molformer_dir = args.molformer_dir.resolve()
    hparams_path = resolve_path(args.hparams, molformer_dir)
    checkpoint_path = resolve_path(args.checkpoint, molformer_dir)
    vocab_path = resolve_path(args.vocab, molformer_dir)

    for path, label in [
        (args.input, "input"),
        (molformer_dir, "molformer-dir"),
        (hparams_path, "hparams"),
        (checkpoint_path, "checkpoint"),
        (vocab_path, "vocab"),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Missing {label}: {path}")

    with open(args.input, "rb") as handle:
        loaded_smiles = pkl.load(handle)

    if args.skip_canonicalization:
        smiles = list(dict.fromkeys(str(item).strip() for item in loaded_smiles))
        invalid = []
    else:
        smiles, invalid = normalize_smiles(loaded_smiles)

    model, tokenizer = load_molformer(
        molformer_dir,
        hparams_path,
        checkpoint_path,
        vocab_path,
        device,
    )
    embeddings = embed_smiles(
        model,
        tokenizer,
        smiles,
        batch_size=args.batch_size,
        device=device,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "wb") as handle:
        pkl.dump(embeddings, handle)

    print(f"input SMILES: {len(loaded_smiles)}")
    print(f"embedded SMILES: {len(embeddings)}")
    print(f"invalid skipped: {len(invalid)}")
    print(f"output: {args.output}")
    if embeddings:
        first_key = next(iter(embeddings))
        print(f"first shape: {tuple(embeddings[first_key].shape)}")


if __name__ == "__main__":
    main()
