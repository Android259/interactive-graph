"""The lipid axis cut at the CONCRETE STRUCTURE, for --lipid_species_coldsplit.

The fourth cut on the lipid side, and the only one whose unit is an individual lipid
rather than a named chemical set:

  --lipid_coldsplit   four hand-built sets of project head-group classes
  --lipid_isolation   a block chosen by Tanimoto distance to a target isolation
  --lipid_subclass    one subclass of Titeca et al. (a head-group row of Figure 3a)
  --lipid_species_coldsplit   a seeded draw of individual lipids, sized by how many
                      positives it has to carry

What it guarantees is narrower and stricter than the three above: no concrete lipid
structure appears both in training and in the evaluated block. That is NOT the same as
holding out a set of `FullIdentityOfLipid` names, and the difference is measurable in
this table rather than hypothetical. A name is a measured species (a sum composition
like "Phosphatidylcholine (34:1)") and it carries a BAG of candidate structures -- the
sn-positional and double-bond isomers the spectrum cannot separate. Those bags overlap:
149 of the 1226 distinct structures are offered by more than one name. Drawing 15% of
NAMES therefore leaves 12-22% of the drawn structures still present in training under a
different name, which is precisely the leak this flag exists to close.

The unit is therefore the connected component of the bipartite name-structure graph:
a name, every structure it offers, every other name offering one of those structures,
transitively. Cutting between components is the finest cut that is structure-disjoint,
and any cut inside one is not disjoint at all. In this table that costs almost nothing
-- the graph is nearly atomized, 243 components over 283 names, 207 of them a single
name, the largest holding 6 -- so "structure-disjoint" and "fine-grained" are not in
tension here the way they would be in a set of congeneric drug-like series.

Nothing about the rest of the split changes: every protein stays in training, and the
block is halved label-by-label into validation and test by the same code every other
lipid-axis flag goes through (Dataloader._split_interactions).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from rdkit import Chem


def row_candidate_structures(smile_global, smile_fragment, isomeric=False):
    """The canonical candidate structures of one table row, in field order.

    Exactly LipidGraphBuilder's own rule (_select_lipid_embedding_text plus
    _lipid_fragment_keys): the untrimmed "0" test picks which column is read, then the
    ";"-separated field is split, stripped, emptied of ""/"0" parts and deduplicated by
    canonical SMILES. `isomeric` mirrors --lipid_isomers, which decides whether
    stereoisomers are separate structures or one, so a run cuts on the same notion of
    "a structure" that its own encoder uses.
    """
    text = str(smile_global)
    if text == "0":
        text = str(smile_fragment)
    structures = []
    for part in text.split(";"):
        part = part.strip()
        if not part or part == "0":
            continue
        mol = Chem.MolFromSmiles(part)
        if mol is None or mol.GetNumAtoms() == 0:
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=isomeric)
        if canonical not in structures:
            structures.append(canonical)
    return structures


def structures_by_species(csv, isomeric=False):
    """{FullIdentityOfLipid: frozenset of its candidate structures}.

    Canonicalization is memoized on the (SmileGlobal, SmileFragment) pair rather than
    run per row: the table's 9905 rows carry 419 distinct pairs, so this is 419 RDKit
    passes (~0.5 s) instead of 9905.
    """
    by_pair = {}
    mapping = {}
    for name, part in csv.groupby("FullIdentityOfLipid", sort=True):
        found = set()
        for pair in set(zip(part["SmileGlobal"], part["SmileFragment"])):
            if pair not in by_pair:
                by_pair[pair] = tuple(
                    row_candidate_structures(pair[0], pair[1], isomeric=isomeric)
                )
            found.update(by_pair[pair])
        mapping[name] = frozenset(found)
    return mapping


def structure_components(csv, isomeric=False):
    """The name-structure graph's connected components, as tuples of names.

    Sorted, and each component's names sorted inside it, so the order a seeded draw
    permutes is a property of the table alone -- not of dict iteration order, and not
    of how many workers happened to build it.
    """
    by_species = structures_by_species(csv, isomeric=isomeric)
    owners = {}
    for name, structures in by_species.items():
        for structure in structures:
            owners.setdefault(structure, set()).add(name)

    seen = set()
    components = []
    for start in sorted(by_species):
        if start in seen:
            continue
        stack, names = [start], set()
        seen.add(start)
        while stack:
            name = stack.pop()
            names.add(name)
            for structure in by_species[name]:
                for other in owners[structure]:
                    if other not in seen:
                        seen.add(other)
                        stack.append(other)
        components.append(tuple(sorted(names)))
    return sorted(components)


def species_coldsplit_block(csv, share, seed, isomeric=False):
    """A structure-disjoint block carrying about `share` of the table's positives.

    Whole components are drawn in a seeded random order and accumulated until the
    positive target is met, so the block is structure-disjoint by construction and its
    SIZE is what the share controls. Sizing by positives rather than by a count of
    names is what makes the share mean the same thing from run to run: positives are
    spread thinly and unevenly over the names (634 of them over 283 names, median 1 per
    name, 154 names carrying exactly one), so a fixed count of names would hand one
    seed twice the evaluated positives of another.

    The seed is the run's own seed, so the five seeds of a grid measure five different
    draws rather than five repetitions of one arbitrary block. That is deliberate: a
    single fixed block of individual lipids would be one draw of many with nothing to
    recommend it, unlike a subclass, which names itself.

    Returns (species tuple, stats dict).
    """
    components = structure_components(csv, isomeric=isomeric)
    positives = csv.groupby("FullIdentityOfLipid")["Interaction"].sum()
    total_positives = int(csv["Interaction"].sum())
    target = share * total_positives

    order = np.random.default_rng(seed).permutation(len(components))
    held, held_positives, used = set(), 0, 0
    for index in order:
        if held_positives >= target:
            break
        component = components[index]
        held.update(component)
        held_positives += int(sum(int(positives.get(name, 0)) for name in component))
        used += 1

    species = tuple(sorted(held))
    in_block = csv["FullIdentityOfLipid"].isin(held)
    block, train = csv[in_block], csv[~in_block]
    train_positive_proteins = set(train.loc[train["Interaction"] == 1, "LTPProtein"])
    stats = {
        "components": len(components),
        "components_used": used,
        "species": len(species),
        "block_rows": int(len(block)),
        "block_positives": int(block["Interaction"].sum()),
        "block_proteins": int(
            block.loc[block["Interaction"] == 1, "LTPProtein"].nunique()
        ),
        "train_positives": int(train["Interaction"].sum()),
        # Proteins left with no positive anywhere in training: they can still appear as
        # negatives, but nothing in train says what they DO bind. Reported rather than
        # prevented -- the fix is a smaller share, which is the caller's call.
        "proteins_without_train_positive": int(
            csv["LTPProtein"].nunique() - len(train_positive_proteins)
        ),
    }
    return species, stats
