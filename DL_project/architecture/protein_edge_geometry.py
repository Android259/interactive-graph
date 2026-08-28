"""RBF + rigid-frame edge features (Ingraham et al. 2019, Sec 3.3.1).

Turns the plain Voronota contact edge (distance, area, boundary) into a 25-dim,
SE(3)-invariant vector per directed edge: 16 RBF-expanded distance bins, a
frame-relative direction unit vector (3), a relative-orientation quaternion (4),
and the two original contact scalars (log-area, boundary/area).

Both directions of each edge are built natively here -- direction and quaternion
are orientation-dependent, so simply copying [i, j]'s features onto [j, i] (as
architecture/protein_encoder.py's make_bidirectional_edges does for the plain
3-dim edge_attr) would be wrong.
"""

import torch

import sys
from pathlib import Path

_RNA_BANG_DATA = Path(__file__).resolve().parents[1] / "external" / "RNA-BAnG" / "data"


def _rotation_class():
    """rigid_utils.Rotation, imported on first use rather than at module import.

    external/ is a submodule and is not everywhere the training code is: the
    cluster sync deliberately leaves it out (scripts/lib/cluster_sync_excludes.sh).
    Importing it at module scope made that absence fatal for EVERY run, because
    architecture/protein_encoder.py imports this module unconditionally while only
    --edge_attention / --edge_mlp configs ever call structured_edge_features. The
    import therefore belongs where the dependency is actually used, so a config
    that does not use structured edges never touches it, and one that does fails
    with a message naming what is missing instead of a ModuleNotFoundError three
    frames deep.
    """
    if str(_RNA_BANG_DATA) not in sys.path:
        sys.path.insert(0, str(_RNA_BANG_DATA))
    try:
        from rigid_utils import Rotation
    except ImportError as error:
        raise ImportError(
            "structured protein edges (--edge_attention / --edge_mlp) need "
            f"rigid_utils from {_RNA_BANG_DATA}, which is not present. Check out the "
            "external/RNA-BAnG submodule on this machine."
        ) from error
    return Rotation


RBF_COUNT = 16
RBF_MIN = 2.0
RBF_MAX = 22.0
STRUCTURED_EDGE_DIM = 25


def rbf(distance, count=RBF_COUNT, d_min=RBF_MIN, d_max=RBF_MAX):
    """Gaussian RBF expansion of a [*] distance tensor into [*, count]."""
    centers = torch.linspace(d_min, d_max, count, device=distance.device, dtype=distance.dtype)
    sigma = (d_max - d_min) / count
    return torch.exp(-((distance.unsqueeze(-1) - centers) / sigma) ** 2)


def structured_edge_features(edge_index, frame_rotation, frame_translation, edge_attr):
    """Build native bidirectional 25-dim structured edges.

    Args:
        edge_index: [2, E] long, one direction per column (as loaded from the
            Voronota contact graph).
        frame_rotation: [N, 3, 3] per-residue rigid-frame rotation.
        frame_translation: [N, 3] per-residue rigid-frame translation (== Cα).
        edge_attr: [E, >=2] with columns (..., area, boundary) matching the
            existing [distance, area, boundary] layout -- only area/boundary are
            reused; distance is recomputed from frame_translation so it stays
            consistent with the direction vector and quaternion.

    Returns:
        (edge_index_bidi [2, 2E], e_attr [2E, 25]) -- both directions, each with
        correctly oriented direction vectors and quaternions.
    """
    src, dst = edge_index[0], edge_index[1]
    area = edge_attr[:, -2].clamp_min(0.0)
    boundary = edge_attr[:, -1].clamp_min(0.0)

    def one_direction(i, j):
        r_i = frame_rotation[i]
        t_i = frame_translation[i]
        t_j = frame_translation[j]
        delta = t_j - t_i
        distance = delta.norm(dim=-1)
        unit = delta / distance.clamp_min(1e-8).unsqueeze(-1)
        # einsum "eij,ei->ej" sums over the row index i, i.e. computes r_i^T @ unit
        # without an explicit .transpose() -- see the module's inline derivation
        # notes in the plan; a transpose() here would silently cancel this and
        # compute r_i @ unit instead.
        local_direction = torch.einsum("eij,ei->ej", r_i, unit)
        relative_rotation = torch.einsum(
            "eij,eik->ejk", r_i, frame_rotation[j]
        )
        quaternion = _rotation_class()(rot_mats=relative_rotation).get_quats()
        return torch.cat(
            (
                rbf(distance),
                local_direction,
                quaternion,
                torch.log1p(area).unsqueeze(-1),
                (boundary / area.clamp_min(1e-8)).unsqueeze(-1),
            ),
            dim=-1,
        )

    forward = one_direction(src, dst)
    backward = one_direction(dst, src)

    edge_index_bidi = torch.cat(
        (edge_index, edge_index.flip(0)), dim=1
    )
    e_attr = torch.cat((forward, backward), dim=0)
    return edge_index_bidi, e_attr
