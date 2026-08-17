"""Load legacy SMILES embeddings for the non-graph lipid path."""

import random

import torch
from rdkit import Chem


class LipidGraphBuilder:
    @staticmethod
    def _smiles_pair(smile_global, smile_fragment=None):
        if smile_fragment is None:
            return smile_global["SmileGlobal"], smile_global["SmileFragment"]
        return smile_global, smile_fragment

    def cached_lipid_encoding(self, smile_global, smile_fragment=None):
        """Return the SMILES-pair encoding from the process-local cache."""
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        if self.config.lipid_random_choice:
            return self._drawn_lipid_encoding(smile_global, smile_fragment)
        key = (str(smile_global), str(smile_fragment))
        cached = self._lipid_encoding_cache.get(key)
        if cached is None:
            cached = self.lipid_encoding(smile_global, smile_fragment)
            self._lipid_encoding_cache[key] = cached
        return cached

    def warm_lipid_encoding(self, smile_global, smile_fragment=None):
        """Fill this row's cache entry without consuming the random stream."""
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        if not self.config.lipid_random_choice:
            self.cached_lipid_encoding(smile_global, smile_fragment)
            return
        key = (str(smile_global), str(smile_fragment))
        if key not in self._lipid_candidate_key_cache:
            self._lipid_candidate_key_cache[key] = self._lipid_candidate_keys(
                smile_global, smile_fragment
            )

    def _drawn_lipid_encoding(self, smile_global, smile_fragment):
        """Draw one candidate for this row, redrawing on every access.

        Caching the drawn *encoding* would freeze the draw for the whole run: the
        DataLoader keeps its workers alive (``persistent_workers``), so a row would
        keep whichever candidate it happened to pick the first time and
        ``lipid_random_choice`` would degenerate into "an arbitrary fixed
        representative" -- the thing it exists to replace. So the cache holds the
        canonical keys instead, which is where the cost actually was (RDKit
        canonicalization); the lookup behind them is a dict hit into
        ``smiles_encoding``, which ``release_source_artifacts`` deliberately keeps
        alive in this mode, and the draw itself is O(1).

        This mirrors the isomer-graph path, where the draw already happens before a
        cache keyed by the chosen SMILES (see LipidIsomerGraphBuilder.make_graph_lipid).
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
        """Canonical embedding keys for the ";"-separated SMILES of one row.

        The field is a *bag of candidate structures* for one measured lipid species --
        sn-positional and double-bond isomers the spectrum cannot tell apart -- not the
        pieces of one molecule, and it is written with a space after each separator and
        usually a trailing one ("A; B; C; "). Hence the strip, the skip of empty/"0"
        parts (`Chem.MolFromSmiles("")` returns an empty mol whose canonical form is ""
        and is in no embedding table) and the deduplication: the same candidate is
        repeated inside a row often enough that keeping both would double its tokens
        and its weight in every mode.

        ``lipid_first_fragment_only`` keeps just the first usable candidate, which is
        what this path did unconditionally before the flag existed, so it is the
        default and leaves earlier runs reproducible.
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
        encoding = self.smiles_encoding.get(key)
        if encoding is None:
            # A cross-file mismatch, not a sample to skip: the embedding table was
            # built from these same columns (preprocessing/embed_isomeric_smiles.py
            # feeds preprocessing/embed_isomeric_smiles_molformer.py), so a missing
            # key means the two are out of sync. Report it instead of substituting
            # another fragment.
            raise KeyError(
                f"lipid SMILES missing from the embedding table: {key}. "
                "Rebuild the table for the current interaction CSV."
            )
        return encoding

    def _encode_lipid_fragments(self, fragments):
        """Encode one row's SMILES candidates under the configured fragment treatment.

        Both concat and fragments_mask lay the candidates out along the *token* axis of
        the (1, tokens, 768) MolFormer encoding, so candidates of different token
        lengths compose without padding; fragments_mask additionally records which
        candidate every token came from, and that vector is the only thing that then
        restricts lipid self-attention to within a candidate. Fragment ids are numbered
        per sample and stay so after collation, which is safe because they are only
        ever compared against the per-sample attention mask that already blocks every
        cross-sample pair (see SelfAttention: attn_mask | ~mult_mask).
        """
        encodings = [
            self._fragment_encoding(key)
            for key in self._lipid_fragment_keys(fragments)
        ]

        if self.config.lipid_concat:
            return torch.cat(encodings, dim=1), None
        if self.config.lipid_random_choice:
            return random.choice(encodings), None
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
            encoding = self.smiles_encoding[key]
            if self.config.lipid_fragments_mask:
                fragment_batch = torch.zeros(
                    (encoding.shape[1],), dtype=torch.long
                )

        if self.config.lipid_fragments_mask:
            return torch.squeeze(encoding), fragment_batch
        return torch.squeeze(encoding)

    def complete_graph_edge_index(self, num_nodes):
        """Undirected complete graph plus self loops over num_nodes, built once.

        The result depends only on num_nodes -- the lipid embedding width, constant for
        a whole run -- so this used to rebuild the same 295296-edge tensor for every
        sample: 17 ms in the Python list comprehension plus 60 ms in torch.tensor, 86%
        of the 89.5 ms spent per get(). Construction is unchanged, so the cached tensor
        is the one the old code produced.
        """
        cached = self._complete_edge_index_cache.get(num_nodes)
        if cached is None:
            a = list(range(num_nodes))
            lipedge = [(a[i], a[j+i+1]) for i in range(len(a))  for j in range(len(a[i+1:]))]
            lipedge += [(a[i],a[i]) for i in range(len(a))]
            cached = torch.tensor(lipedge).t().contiguous()
            self._complete_edge_index_cache[num_nodes] = cached
        return cached
