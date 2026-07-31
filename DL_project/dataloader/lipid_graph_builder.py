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
        key = (str(smile_global), str(smile_fragment))
        cached = self._lipid_encoding_cache.get(key)
        if cached is None:
            cached = self.lipid_encoding(smile_global, smile_fragment)
            self._lipid_encoding_cache[key] = cached
        return cached

    def _select_lipid_embedding_text(self, smile_global, smile_fragment):
        return str(smile_fragment) if str(smile_global) == "0" else str(smile_global)

    def _canonical_embedding_key(self, smiles):
        return Chem.MolToSmiles(
            Chem.MolFromSmiles(smiles),
            canonical=True,
            isomericSmiles=self.config.lipid_isomers,
        )

    def _encode_lipid_fragments(self, fragments):
        encodings = []
        fragment_batches = []
        fragment_id = 0
        for fragment in fragments:
            key = self._canonical_embedding_key(fragment)
            encoding = self.smiles_encoding[key]
            if self.config.lipid_fragments_mask:
                fragment_batches.append(
                    torch.full(
                        (encoding.shape[1],),
                        fragment_id,
                        dtype=torch.long,
                    )
                )
                fragment_id += 1
            encodings.append(encoding)
            # Process every available fragment instead of stopping after the
            # first one. Before removing this break, define how missing embedding
            # keys and variable token lengths compose in concat, random-choice, and
            # fragments-mask modes; changing it will alter existing run results.
            break

        if self.config.lipid_concat:
            return torch.cat(encodings, dim=1), None
        if self.config.lipid_random_choice:
            return random.choice(encodings), None
        if self.config.lipid_fragments_mask:
            return (
                torch.cat(encodings, dim=0),
                torch.cat(fragment_batches, dim=0),
            )

    def lipid_encoding(self, smile_global, smile_fragment=None):
        smile_global, smile_fragment = self._smiles_pair(
            smile_global, smile_fragment
        )
        lipid_text = self._select_lipid_embedding_text(
            smile_global, smile_fragment
        )

        if not self.config.lipid_isomers and (
            "//" in lipid_text or "\\\\" in lipid_text
        ):
            lipid_text = lipid_text.replace("//", "/").replace("\\\\", "\\")

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
