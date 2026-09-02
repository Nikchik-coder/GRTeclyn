"""Scalar-field mode extraction on the Psi4 extraction spheres.

Why this is a separate module (same rule as ``psi4_higher_l.py``)
-----------------------------------------------------------------
The Psi4 streams are published column contracts and must not widen.  This
module owns its own stream (``scalar_modes.dat``) and is **off by default**,
enabled per campaign with ``--scalar-modes`` in the consumer arguments.

Physics motivation (GPU_PLAN.md section 7)
------------------------------------------
The post-merger tail is a coupled scalar-metric mode: the equatorial ring
harmonic showed the phi dipole amplitude phase-locked to Psi4 (|r| = 0.95,
lag ~0) at the same ~17-unit period.  The ring trick only sees the equator
and cannot separate true (l, m) modes.  This stream projects phi and Pi onto
proper s = 0 spherical harmonics on the same spheres as Psi4, at every
extraction radius, and adds a kinematic scalar energy flux so the scalar/GW
energy budget can be quoted per radius.

Conventions (deliberate, read before consuming the stream)
----------------------------------------------------------
- Harmonics come from the same Wigner-d routine as the higher-l Psi4 stream
  (``sphere.spin_weighted_sph_harm`` with s = 0), so phases are consistent
  across channels and across l.  Note phi is spin weight 0, so l = 0 and
  l = 1 exist here even though they do not for Psi4.
- ``A_lm(field, R) = R * sum(field * conj(Ylm) * W_renorm)`` -- the same
  overall R scaling as the Psi4 streams, so wave-zone amplitudes are
  directly comparable across radii.
- ``flux_kin(R) = -R^2 * sum(Pi * d_r phi * W_renorm)``: a *coordinate*
  ("kinematic") proxy for the outgoing scalar energy flux.  No lapse or
  shift factors are applied, Pi is used exactly as stored in the plotfile,
  and the **phantom kinetic sign is NOT applied** -- for phantom matter the
  physical energy flux is the negative of the canonical-scalar expression.
  The sign convention is chosen so a canonical outgoing wave (Pi ~ -d_r phi)
  gives a positive number.  d_r phi is a central difference over spheres at
  R -+ flux_delta.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

from ..sphere import spin_weighted_sph_harm

SUPPORTED_ELLS = (0, 1, 2, 3, 4)
DEFAULT_ELLS = (0, 1, 2)

_PHI_FIELD = ("boxlib", "phi")
_PI_FIELD = ("boxlib", "Pi")


def _coerce_scalar_samples(values) -> np.ndarray:
    arr = np.asarray(values)
    if arr.dtype != object and arr.ndim == 1:
        return arr.astype(float, copy=False)
    out = np.empty(len(values), dtype=float)
    for jj, v in enumerate(values):
        vv = np.asarray(v, dtype=float).reshape(-1)
        out[jj] = vv[0] if vv.size else np.nan
    return out


def parse_scalar_ells(raw: Sequence[int] | str | None) -> tuple[int, ...]:
    """Normalise an ell specification into a validated, ordered tuple."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return DEFAULT_ELLS
    if isinstance(raw, str):
        items = [tok for tok in raw.replace(",", " ").split() if tok]
    else:
        items = list(raw)
    ells: List[int] = []
    for tok in items:
        val = int(tok)
        if val not in SUPPORTED_ELLS:
            raise ValueError(
                f"unsupported l={val} for s=0 harmonics; supported: {SUPPORTED_ELLS}"
            )
        if val not in ells:
            ells.append(val)
    return tuple(sorted(ells))


def extract_scalar_modes(
    ds,
    radii: Sequence[float],
    n_points: int,
    center: Sequence[float],
    ells: Sequence[int] = DEFAULT_ELLS,
    flux_delta: float = 0.5,
) -> Tuple[Dict[int, List[Dict[int, complex]]], Dict[int, List[Dict[int, complex]]], List[float]]:
    """Project phi and Pi onto s = 0 harmonics and integrate the kinematic flux.

    Returns ``(phi_modes, pi_modes, fluxes)`` where each modes dict is
    ``{l: [ {m: amplitude} per radius ]}`` and ``fluxes`` is one float per
    radius.  Three spheres (R - delta, R, R + delta) are sampled per radius,
    all radii batched into one field query, matching the Psi4 modules.
    """
    ells = tuple(ells)
    if not radii:
        return ({l: [] for l in ells}, {l: [] for l in ells}, [])

    if _PHI_FIELD not in ds.field_list or _PI_FIELD not in ds.field_list:
        raise RuntimeError("Plotfile missing phi/Pi fields; scalar modes need both.")

    left = np.asarray(ds.domain_left_edge, dtype=float)
    right = np.asarray(ds.domain_right_edge, dtype=float)
    center = np.asarray(center, dtype=float)

    theta = np.linspace(0.0, np.pi, n_points)
    phi_az = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
    THETA, PHI = np.meshgrid(theta, phi_az, indexing="ij")
    sinT = np.sin(THETA)
    X1 = sinT * np.cos(PHI)
    Y1 = sinT * np.sin(PHI)
    Z1 = np.cos(THETA)
    dtheta = np.pi / (n_points - 1)
    dphi = 2.0 * np.pi / n_points
    Wf = (sinT * dtheta * dphi).ravel()
    shape = X1.shape
    npts = shape[0] * shape[1]

    harmonics: Dict[int, Dict[int, np.ndarray]] = {
        l: {m: spin_weighted_sph_harm(0, l, m, THETA, PHI) for m in range(-l, l + 1)}
        for l in ells
    }

    # Per radius, three concentric spheres: [R - delta, R, R + delta].
    shell_radii: List[float] = []
    for r in radii:
        shell_radii.extend([float(r) - flux_delta, float(r), float(r) + flux_delta])

    sx = np.concatenate([(rs * X1).ravel() + center[0] for rs in shell_radii])
    sy = np.concatenate([(rs * Y1).ravel() + center[1] for rs in shell_radii])
    sz = np.concatenate([(rs * Z1).ravel() + center[2] for rs in shell_radii])

    in_domain = (
        (sx >= left[0]) & (sx <= right[0])
        & (sy >= left[1]) & (sy <= right[1])
        & (sz >= left[2]) & (sz <= right[2])
    )
    idxs = np.where(in_domain)[0]
    if idxs.size < 4:
        raise RuntimeError("Too few sphere points inside domain (all radii).")

    phi_v = np.full(sx.shape, np.nan)
    pi_v = np.full(sx.shape, np.nan)
    pts = np.column_stack((sx[idxs], sy[idxs], sz[idxs]))

    try:
        vals = ds.find_field_values_at_points([_PHI_FIELD, _PI_FIELD], pts)
        phi_v[idxs] = _coerce_scalar_samples(vals[0])
        pi_v[idxs] = _coerce_scalar_samples(vals[1])
    except Exception:
        for ii, i in enumerate(idxs):
            pt = ds.point([pts[ii, 0], pts[ii, 1], pts[ii, 2]])
            pv = np.asarray(pt[_PHI_FIELD])
            qv = np.asarray(pt[_PI_FIELD])
            if pv.size and qv.size:
                phi_v[i] = float(pv.flat[0])
                pi_v[i] = float(qv.flat[0])

    phi_modes: Dict[int, List[Dict[int, complex]]] = {l: [] for l in ells}
    pi_modes: Dict[int, List[Dict[int, complex]]] = {l: [] for l in ells}
    fluxes: List[float] = []

    for ir, r in enumerate(radii):
        base = 3 * ir * npts
        phi_m = phi_v[base : base + npts]
        phi_c = phi_v[base + npts : base + 2 * npts]
        phi_p = phi_v[base + 2 * npts : base + 3 * npts]
        pi_c = pi_v[base + npts : base + 2 * npts]

        mask_c = np.isfinite(phi_c) & np.isfinite(pi_c)
        if np.sum(mask_c) < 4:
            raise RuntimeError(f"Too few valid phi/Pi samples at R={r}.")
        omega_tot = np.sum(Wf[mask_c])
        if omega_tot <= 0.0:
            raise RuntimeError(f"Invalid integration weights at R={r} (omega_tot <= 0).")
        W_renorm = (Wf / omega_tot * 4.0 * np.pi).reshape(shape)

        phi_grid = np.where(mask_c, phi_c, 0.0).reshape(shape)
        pi_grid = np.where(mask_c, pi_c, 0.0).reshape(shape)

        for l in ells:
            pm: Dict[int, complex] = {}
            qm: Dict[int, complex] = {}
            for m, ylm in harmonics[l].items():
                pm[m] = complex(np.sum(phi_grid * np.conj(ylm) * W_renorm) * float(r))
                qm[m] = complex(np.sum(pi_grid * np.conj(ylm) * W_renorm) * float(r))
            phi_modes[l].append(pm)
            pi_modes[l].append(qm)

        # Kinematic flux: central-difference d_r phi where both shells are
        # valid, the center-sphere quadrature elsewhere is dropped alongside.
        mask_f = mask_c & np.isfinite(phi_m) & np.isfinite(phi_p)
        omega_f = np.sum(Wf[mask_f])
        if omega_f > 0.0 and np.sum(mask_f) >= 4:
            Wr_f = (Wf / omega_f * 4.0 * np.pi).reshape(shape)
            dphi_dr = np.where(mask_f, (phi_p - phi_m) / (2.0 * flux_delta), 0.0).reshape(shape)
            pi_f = np.where(mask_f, pi_c, 0.0).reshape(shape)
            fluxes.append(float(-(float(r) ** 2) * np.sum(pi_f * dphi_dr * Wr_f)))
        else:
            fluxes.append(float("nan"))

    return phi_modes, pi_modes, fluxes


def scalar_modes_header(ells: Sequence[int], radii: Sequence[float]) -> str:
    """Column header for ``scalar_modes.dat``.

    Layout: time, then for each radius: phi modes (each l, m as Re/Im), Pi
    modes likewise, then the kinematic flux.  Names carry the radius so the
    file is self-describing.
    """
    cols = ["time"]
    for r in radii:
        for field in ("phi", "Pi"):
            for l in ells:
                for m in range(-l, l + 1):
                    cols.append(f"R{float(r):g}_{field}_l{l}_m{m}_re")
                    cols.append(f"R{float(r):g}_{field}_l{l}_m{m}_im")
        cols.append(f"R{float(r):g}_scalar_flux_kin")
    return "# " + "  ".join(cols)


def scalar_modes_line(
    t: float,
    phi_modes: Dict[int, List[Dict[int, complex]]],
    pi_modes: Dict[int, List[Dict[int, complex]]],
    fluxes: List[float],
    ells: Sequence[int],
    n_radii: int,
) -> str:
    """Format one time row matching :func:`scalar_modes_header`."""
    parts = [f"{t:.16e}"]
    for ir in range(n_radii):
        for modes_by_l in (phi_modes, pi_modes):
            for l in ells:
                per_radius = modes_by_l.get(l) or []
                modes = per_radius[ir] if ir < len(per_radius) else {}
                for m in range(-l, l + 1):
                    c = modes.get(m, 0j)
                    parts.append(f"{c.real:.16e}")
                    parts.append(f"{c.imag:.16e}")
        parts.append(f"{fluxes[ir]:.16e}" if ir < len(fluxes) else "nan")
    return "  ".join(parts)


def selftest(n_points: int = 96) -> None:
    """Verify s = 0 harmonic orthonormality and projection round-trip.

    Builds synthetic fields from known Y_lm combinations on the quadrature
    grid and checks the projection recovers the coefficients.  Raises on
    failure; silent on success.
    """
    theta = np.linspace(0.0, np.pi, n_points)
    phi_az = np.linspace(0.0, 2.0 * np.pi, n_points, endpoint=False)
    THETA, PHI = np.meshgrid(theta, phi_az, indexing="ij")
    dtheta = np.pi / (n_points - 1)
    dphi = 2.0 * np.pi / n_points
    W = np.sin(THETA) * dtheta * dphi
    W_renorm = W / np.sum(W) * 4.0 * np.pi

    ys = {
        (l, m): spin_weighted_sph_harm(0, l, m, THETA, PHI)
        for l in (0, 1, 2)
        for m in range(-l, l + 1)
    }
    for (l1, m1), y1 in ys.items():
        for (l2, m2), y2 in ys.items():
            want = 1.0 if (l1, m1) == (l2, m2) else 0.0
            got = np.sum(y1 * np.conj(y2) * W_renorm).real
            if abs(got - want) > 5e-3:
                raise AssertionError(
                    f"<Y{l1}{m1}|Y{l2}{m2}> = {got:.4f}, expected {want}"
                )

    f = 0.7 * ys[(1, 1)] + 0.3 * ys[(2, -2)] + 0.2 * ys[(0, 0)]
    for (l, m), want in [((1, 1), 0.7), ((2, -2), 0.3), ((0, 0), 0.2), ((2, 0), 0.0)]:
        got = np.sum(f * np.conj(ys[(l, m)]) * W_renorm)
        if abs(got - want) > 5e-3:
            raise AssertionError(f"projection ({l},{m}) = {got:.4f}, expected {want}")
