"""Load legacy SMILES embeddings for the non-graph lipid path."""

import random

import torch
from rdkit import Chem

from dataloader.smiles_tokens import smiles_one_hot


class LipidGraphBuilder:
    @staticmethod
    def _smiles_pair(smile_global, smile_fragment=None):
        if smile_fragment is None:
            return smile_global["SmileGlobal"], smile_global["SmileFragment"]
        return smile_global, smile_fragment

    def cached_lipid_encoding(
        self, smile_global, smile_fragment=None, candidate_index=None
    ):
        """Return the process-cached encoding for this SMILES pair.

        _draw_lipid_candidate, set per split by Dataloader.__iter__, enables training
        augmentation. Validation/test use fixed cached candidates each epoch.
        candidate_index selects a specific candidate for expanded averaged evaluation;
        cache each separately so predictions can be combined per pair without collisions.
        """
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        if candidate_index is not None:
            return self._indexed_lipid_encoding(
                smile_global, smile_fragment, int(candidate_index)
            )
        if self._draw_lipid_candidate:
            return self._drawn_lipid_encoding(smile_global, smile_fragment)
        key = (str(smile_global), str(smile_fragment))
        cached = self._lipid_encoding_cache.get(key)
        if cached is None:
            cached = self.lipid_encoding(smile_global, smile_fragment)
            self._lipid_encoding_cache[key] = cached
        return cached

    def warm_lipid_encoding(self, smile_global, smile_fragment=None):
        """Warm candidate keys and fixed encodings without consuming RNG draws.

        The training clone shares caches with validation/test through shallow copies.
        Warm both drawn keys and their fixed encoding; the latter is a view into the
        same mapped embedding table, without extra tensor storage.
        """
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        key = (str(smile_global), str(smile_fragment))
        if (
            self._draw_lipid_candidate
            and key not in self._lipid_candidate_key_cache
        ):
            self._lipid_candidate_key_cache[key] = self._lipid_candidate_keys(
                smile_global, smile_fragment
            )
        if key not in self._lipid_encoding_cache:
            self._lipid_encoding_cache[key] = self.lipid_encoding(
                smile_global, smile_fragment
            )

    def candidate_keys_for_row(self, smile_global, smile_fragment=None):
        """This row's candidate keys, memoized -- how many samples it expands into."""
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        key = (str(smile_global), str(smile_fragment))
        keys = self._lipid_candidate_key_cache.get(key)
        if keys is None:
            keys = self._lipid_candidate_keys(smile_global, smile_fragment)
            self._lipid_candidate_key_cache[key] = keys
        return keys

    def draw_candidate_index(self, smile_global, smile_fragment):
        """Draw the candidate index for this row.

        Use an index, not a key, so frozen priors and compatibility values select
        the same encoded structure instead of the first candidate.
        """
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        candidate_keys = self.candidate_keys_for_row(smile_global, smile_fragment)
        return random.choice(range(len(candidate_keys)))

    def _indexed_lipid_encoding(self, smile_global, smile_fragment, index):
        """The index-th candidate of this row, clamped to the ones it actually has."""
        candidate_keys = self.candidate_keys_for_row(smile_global, smile_fragment)
        position = min(index, len(candidate_keys) - 1)
        cache_key = (str(smile_global), str(smile_fragment), position)
        cached = self._lipid_encoding_cache.get(cache_key)
        if cached is None:
            cached = torch.squeeze(
                self._fragment_encoding(candidate_keys[position])
            )
            self._lipid_encoding_cache[cache_key] = cached
        return cached

    def _drawn_lipid_encoding(self, smile_global, smile_fragment):
        """Draw a fresh candidate on each access, caching only canonical keys.

        Caching encodings would freeze the first draw for persistent_workers and
        turn lipid_random_choice into a fixed representative. Canonicalization is
        the expensive step; drawing and smiles_encoding lookup are O(1).
        release_source_artifacts keeps smiles_encoding in this mode.
        This matches make_graph_lipid, which draws before its chosen-SMILES cache.
        """
        key = (str(smile_global), str(smile_fragment))
        candidate_keys = self._lipid_candidate_key_cache.get(key)
        if candidate_keys is None:
            candidate_keys = self._lipid_candidate_keys(
                smile_global, smile_fragment
            )
            self._lipid_candidate_key_cache[key] = candidate_keys
        return torch.squeeze(
            self._fragment_encoding(random.choice(candidate_keys))
        )

    def _select_lipid_embedding_text(self, smile_global, smile_fragment):
        return str(smile_fragment) if str(smile_global) == "0" else str(smile_global)

    def _canonical_smiles(self, mol):
        return Chem.MolToSmiles(
            mol,
            canonical=True,
            isomericSmiles=self.config.lipid_isomers,
        )

    def _canonical_embedding_key(self, smiles):
        return self._canonical_smiles(Chem.MolFromSmiles(smiles))

    def _lipid_fragment_keys(self, fragments):
        """Return canonical keys for a row's semicolon-separated candidate SMILES.

        Fields such as "A; B; C; " list unresolved sn-positional/double-bond isomers,
        not molecular fragments. Strip parts, skip empty/"0", and deduplicate.
        RDKit parses "" as an empty molecule, absent from the embedding table;
        repeated candidates would double tokens and weights.
        lipid_first_fragment_only keeps the first usable candidate. This default
        preserves behavior from before the flag existed.
        """
        keys = []
        seen = set()
        for fragment in fragments:
            fragment = fragment.strip()
            if not fragment or fragment == "0":
                continue
            mol = Chem.MolFromSmiles(fragment)
            if mol is None or mol.GetNumAtoms() == 0:
                continue
            key = self._canonical_smiles(mol)
            if key in seen:
                continue
            seen.add(key)
            keys.append(key)
            if self.config.lipid_first_fragment_only:
                break

        if not keys:
            raise ValueError(
                "no parsable lipid SMILES among the fragments: "
                + ";".join(fragments)
            )
        return keys

    def _fragment_encoding(self, key):
        if getattr(self.config, "lipid_smiles_tokens", False):
            # --lipid_smiles_tokens encodes the canonical lookup key directly, not raw CSV
            # spelling. Dataloader skips the embedding table in this mode; return before
            # accessing smiles_encoding.
            return smiles_one_hot(key)
        encoding = self.smiles_encoding.get(key)
        if encoding is None:
            # A missing key is a cross-file mismatch, not a candidate to skip.
            # The table uses these same columns: embed_smiles_isomeric_and_nonisomeric.py
            # feeds embed_isomeric_smiles_molformer.py (preprocessing/embeddings/).
            # Report the out-of-sync table instead of substituting another candidate.
            raise KeyError(
                f"lipid SMILES missing from the embedding table: {key}. "
                "Rebuild the table for the current interaction CSV."
            )
        return encoding

    def _encode_lipid_fragments(self, fragments):
        """Encode candidates using the selected fragment treatment.

        concat/fragments_mask concatenate (1, tokens, 768) encodings along tokens,
        without padding differing lengths. fragments_mask also records a candidate
        ID per token to restrict lipid self-attention within candidates.
        IDs remain sample-local after collation: SelfAttention's
        attn_mask | ~mult_mask already blocks cross-sample comparisons.
        """
        encodings = [
            self._fragment_encoding(key)
            for key in self._lipid_fragment_keys(fragments)
        ]

        if self.config.lipid_concat:
            return torch.cat(encodings, dim=1), None
        if self.config.lipid_random_choice:
            # _drawn_lipid_encoding handles augmented splits. random_choice reaches here
            # only for fixed splits or warm-up: use the first candidate, not a cached draw.
            return encodings[0], None
        if self.config.lipid_fragments_mask:
            fragment_batches = [
                torch.full((encoding.shape[1],), fragment_id, dtype=torch.long)
                for fragment_id, encoding in enumerate(encodings)
            ]
            return (
                torch.cat(encodings, dim=1),
                torch.cat(fragment_batches, dim=0),
            )

    def _lipid_candidate_keys(self, smile_global, smile_fragment):
        """Every embedding key this row can be encoded as, in field order."""
        lipid_text = self._select_lipid_embedding_text(
            smile_global, smile_fragment
        )
        if ";" in lipid_text:
            return tuple(self._lipid_fragment_keys(lipid_text.split(";")))
        return (self._canonical_embedding_key(lipid_text),)

    def lipid_encoding(self, smile_global, smile_fragment=None):
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        lipid_text = self._select_lipid_embedding_text(
            smile_global, smile_fragment
        )

        fragment_batch = None
        if ";" in lipid_text:
            encoding, fragment_batch = self._encode_lipid_fragments(
                lipid_text.split(";")
            )
        else:
            key = self._canonical_embedding_key(lipid_text)
            # Use _fragment_encoding for both SMILES tokens (no table) and MoLFormer lookup.
            # It also reports missing embedding keys with the out-of-sync table name.
            encoding = self._fragment_encoding(key)
            if self.config.lipid_fragments_mask:
                fragment_batch = torch.zeros(
                    (encoding.shape[1],), dtype=torch.long
                )

        if self.config.lipid_fragments_mask:
            return torch.squeeze(encoding), fragment_batch
        return torch.squeeze(encoding)

    def complete_graph_edge_index(self, num_nodes):
        """Cache the undirected complete graph with self-loops for num_nodes.

        Only embedding width determines it and is fixed per run. Previously, each
        sample rebuilt 295296 edges: 17 ms for the list and 60 ms for torch.tensor,
        86% of the 89.5 ms get() cost. Construction and tensor values are unchanged.
        """
        cached = self._complete_edge_index_cache.get(num_nodes)
        if cached is None:
            a = list(range(num_nodes))
            lipedge = [(a[i], a[j+i+1]) for i in range(len(a))  for j in range(len(a[i+1:]))]
            lipedge += [(a[i],a[i]) for i in range(len(a))]
            cached = torch.tensor(lipedge).t().contiguous()
            self._complete_edge_index_cache[num_nodes] = cached
        return cached
