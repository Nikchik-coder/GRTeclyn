"""The common horizon itself, per plotfile, before the consumer deletes the plotfile.

Why (2026-10-01): the round scan (horizon.py) and the oriented scan (ah_oriented_scan.py)
report the outermost fully trapped ROUND sphere, which sits inside a deformed MOTS: on the
mode-3 head-on's t = 51-60 slices they read R 4-11 % and 3-7 % low.  The surface itself
was found offline, which meant keeping every plotfile (5.5 GB a unit).  Here the consumer
runs the same finder on each plotfile it has loaded anyway:

  the spectral MOTS finder of scripts/analysis/merger_feedback/headon_first_law.py --
  r = h(theta, phi) in real Y_lm to lmax, found once by the flow (ah_flow_finder.py) and
  then followed from plotfile to plotfile by Newton from the previous surface (~20 s at
  level 3) -- with the first law's scalar flux and shear on it.

One row per plotfile goes to mots_spectral.dat, and the surface's coefficients to
mots_spectral_alm.jsonl (the next plotfile's warm start; they also redraw the surface).
The finder script stays the one implementation: it is loaded from the wrapper's scripts/.
"""

from __future__ import annotations

import importlib.util
from types import SimpleNamespace

import numpy as np

from grteclyn_wrapper.core.config import WRAPPER_ROOT

MOTS_SPECTRAL_HEADER = (
    "# time  R  M_MS  area  h_x  h_y  h_z  r_mean  deform  rms_theta_out  newton_iters  newton_resid  "
    "alpha  theta_in_mean  flux  sigma2  q  dRdt_phantom  dRdt_shear  dRdt_total  level  lmax\n"
    "# the common MOTS r = h(theta, phi) about the centre (headon_first_law.py): R = sqrt(A / 4 pi), "
    "M_MS its Hawking mass, h_x/h_y/h_z its coordinate extent along each axis, <.> surface averages; "
    "dRdt_* the spherical first law's rate from the phantom flux, the shear, and both"
)
_KEYS = ("R", "M_MS", "area", "hx", "hy", "hz", "r_mean", "deform", "th_out_rms", "newton_iters",
         "newton_resid", "alpha", "th_in_mean", "flux", "sig2", "q", "dRdt_phantom", "dRdt_shear",
         "dRdt_total")

_FINDER = None


def _finder():
    """headon_first_law.py, imported once per process (it brings ah_flow_finder with it)."""
    global _FINDER
    if _FINDER is None:
        path = WRAPPER_ROOT / "scripts" / "analysis" / "merger_feedback" / "headon_first_law.py"
        spec = importlib.util.spec_from_file_location("headon_first_law", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _FINDER = module
    return _FINDER


def mots_spectral_row(ds, t: float, *, center, half: float, level: int, lmax: int, tol: float,
                      seeds, a_prev) -> tuple[str | None, list[float] | None]:
    """(row, a_lm) of the common MOTS on this plotfile, or (None, None) if there is none.

    The box is +-half about center on the finest level <= `level` that covers it: a covering
    grid fills an uncovered region with injected coarser cells, whose derivatives are
    staircases.  a_prev, the previous plotfile's a_lm, starts Newton; without it, or if
    Newton fails, the flow starts from the seed radii.
    """
    hfl = _finder()
    centre = np.asarray(center, dtype=float)
    fields, why = None, ""
    for lev in range(min(int(level), int(ds.index.max_level)), 0, -1):
        try:
            fields, dx, lev = hfl.fields_on_box(ds, centre, half, lev)
            break
        except ValueError as err:
            why = str(err)
    if fields is None:
        raise ValueError(f"no level covers the box +-{half} about {list(centre)} ({why})")
    args = SimpleNamespace(centre=list(centre), half=half, level=lev, lmax=lmax, tol=tol,
                           seeds=list(seeds), steps=400)
    row = hfl.analyse_fields(fields, dx, t, lev, args, a_prev, name=f"MOTS at t = {t:.3f}")
    if row is None:
        return None, None
    line = f"{t:.16e}  " + "  ".join(f"{float(row[k]):.10e}" for k in _KEYS) + f"  {lev}  {lmax}"
    return line, [float(x) for x in row["a_lm"]]
