"""Hold out structure-disjoint lipids with --lipid_species_coldsplit.

Other lipid-axis cuts use fixed classes (--lipid_coldsplit), target Tanimoto
isolation (--lipid_isolation), or Titeca et al. Figure 3a subclasses
(--lipid_subclass). This cut draws individual lipids, sized by positive count.

FullIdentityOfLipid names, e.g. PC(34:1), each list candidate sn-positional
and double-bond isomers unresolved by the spectrum. Names share structures:
149/1226 structures occur under multiple names. Holding out 15% of names
alone left 12-22% of held structures in training under another name.

Draw connected components of the name-structure bipartite graph: names,
their candidates, and all transitively linked names. Only cuts between
components are structure-disjoint. The table has 243 components over 283
names, 207 singleton names, and a largest component of 6, retaining fine cuts.

All proteins remain in training. Dataloader._split_interactions halves the
held block label-by-label into validation/test, as for other lipid-axis cuts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from rdkit import Chem


def row_candidate_structures(smile_global, smile_fragment, isomeric=False):
    """Return canonical candidates in field order using LipidGraphBuilder rules.

    Match _select_lipid_embedding_text and _lipid_fragment_keys: choose the field
    with the untrimmed "0" test, split on semicolons, strip, skip empty/"0" parts,
    and deduplicate canonical SMILES. isomeric follows --lipid_isomers, so the
    split and encoder use the same definition of a structure.
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
    """Return {FullIdentityOfLipid: frozenset of candidate structures}.

    Memoize by (SmileGlobal, SmileFragment): 9905 rows had 419 distinct pairs,
    requiring 419 RDKit passes (~0.5 s) instead of 9905.
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
    """Return sorted connected components, each a sorted tuple of names.

    Seeded draws then depend on table content, not dict order or worker count.
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
    """Draw a structure-disjoint block covering about share of table positives.

    Accumulate whole components in seeded random order until the positive
    target is reached. Positive counts size evaluation more reliably than names:
    634 positives span 283 names, median 1, with 154 names having exactly one.
    Fixed name counts could give twice as many evaluated positives for one seed.

    Use the run seed: a five-seed grid tests five draws, not one arbitrary fixed
    block repeatedly. Unlike subclasses, individual-name blocks have no fixed
    chemical definition. Return (species tuple, stats dict).
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
        # Report proteins with no training positive; they may still supply negatives.
        # Do not redraw silently. The caller can choose a smaller share.
        "proteins_without_train_positive": int(
            csv["LTPProtein"].nunique() - len(train_positive_proteins)
        ),
    }
    return species, stats
