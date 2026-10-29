#!/usr/bin/env python3
r"""D21 $X = 1.829$ resolution triplet: constraints on every level, the throat, the wave zone.

The three evolutions differ only in the base grid: $N = 96 / 128 / 192$
on the $L = 64$ box, $\texttt{max_level} = 3$, so level $l$ has
$\Delta x = (2/3, 1/2, 1/3) / 2^l$.  Same layout as the spinning-wormhole
convergence figure (``plot_convergence --spin 0.2c``'s equal-$t$ rows).
Drawn to the finest member's last time, so the three sit at the same $t$.

Top two rows: each level's $L_2$ Hamiltonian (first row) and momentum
(second row) constraint, from ``constraint_norms_levels.dat``.  The
finest member is redrawn at the coarsest spacing for orders 2 and 4.

Bottom row: (i) equatorial throat radius against the background's
$R_e$; (j) areal radius against its $t = 0$ value; (k) the $(2,0)$
mode of $\Psi_4$ at $R = 14$ against its $t = 0$ value; (l) the lapse
at the $\eta \to -\infty$ puncture.

    python -m grteclyn_wrapper.visualisation.optimisation.plot_convergence

Reads the live dirs under ``runs/optimisation/evolution/convergence/``
(or a packed copy under ``results/optimisation/campaign/``).  Writes
``results/optimisation/figures/convergence_d21``.
"""

from __future__ import annotations

import argparse
import pathlib

import numpy as np

from grteclyn_wrapper.visualisation.spinning_wormhole import plot_convergence as sw
from grteclyn_wrapper.visualisation.spinning_wormhole.solutions import REPO
from grteclyn_wrapper.visualisation.wormhole_merger import style

LIVE = REPO / "runs" / "optimisation" / "evolution" / "convergence"
PACKED = REPO / "results" / "optimisation" / "campaign"
FIGURES = REPO / "results" / "optimisation" / "figures"
STEM = "convergence_d21"
BOX = 64.0
PSI4_R = 14
# background D21_X1p82879580_2049x129.spinbg, meta table_R_e
R_EXACT = 4.063830498135651
RUNS = (
    (96, "D21_X1p829_L64_N096_ml3_spdrv0_t150"),
    (128, "D21_X1p829_L64_N128_ml3_spdrv0_t150"),
    (192, "D21_X1p829_L64_N192_ml3_spdrv0_t150"),
)


def run_dir(name: str) -> pathlib.Path:
    for root in (LIVE, PACKED):
        path = root / name
        if path.is_dir():
            return path
    raise SystemExit(f"{name}: not under {LIVE} or {PACKED}")


def clip(arr: np.ndarray, t_max: float) -> np.ndarray:
    return arr[arr[:, 0] <= t_max + 1e-9]


def load(runs, psi4_r: int, t_max: float | None) -> dict[int, dict[str, np.ndarray]]:
    """Each member's streams: evolution files in ``data/``, consumer files in
    ``small_data/``; a packed dir keeps both at the root."""
    out = {}
    for n, name in runs:
        root = run_dir(name)
        data = root / "data" if (root / "data").is_dir() else root
        small = root / "small_data" if (root / "small_data").is_dir() else root
        norms = np.loadtxt(data / "constraint_norms_levels.dat")
        with open(small / "psi4_mode_l2_all.dat") as f:
            head = f.readline().split()[1:]
        psi4 = np.loadtxt(small / "psi4_mode_l2_all.dat")
        re_, im_ = head.index(f"Re_m0(R={psi4_r})"), head.index(f"Im_m0(R={psi4_r})")
        member = dict(
            norms=norms,
            geometry=np.loadtxt(data / "throat_geometry.dat"),
            spheres=np.loadtxt(small / "throat_spheres.dat"),
            psi4=np.column_stack((psi4[:, 0], np.hypot(psi4[:, re_], psi4[:, im_]))),
            psi4_re=psi4[:, [0, re_]],
            collapse=np.loadtxt(data / "collapse_diagnostics.dat"),
            mots=np.loadtxt(small / "mots_spectral.dat"),
        )
        if t_max is not None:
            member = {k: clip(v, t_max) for k, v in member.items()}
        for key, arr in member.items():
            if arr.size == 0:
                raise SystemExit(f"{name}: {key} empty at t <= {t_max}")
            if key != "mots" and not np.isfinite(arr).all():
                raise SystemExit(f"{name}: non-finite rows in {key}")
        out[n] = member
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=pathlib.Path, default=None,
                    help="output stem (default results/optimisation/figures/convergence_d21)")
    ap.add_argument("--palette", choices=sorted(sw.PALETTES), default="rgb",
                    help="colour scheme (default rgb, the spinning paper's)")
    ap.add_argument("--colors", default=None,
                    help="three comma-separated colours replacing the members' colours")
    ap.add_argument("--t-max", type=float, default=None,
                    help="clip every member to this t (default: finest member's last time)")
    args = ap.parse_args(argv)
    look = dict(sw.PALETTES[args.palette])
    if args.colors:
        look["colours"] = tuple(c.strip() for c in args.colors.split(","))
        if len(look["colours"]) != 3:
            ap.error("--colors takes exactly three colours")

    ns = tuple(n for n, _ in RUNS)
    t_max = args.t_max
    if t_max is None:
        finest = run_dir(RUNS[-1][1])
        data_dir = finest / "data" if (finest / "data").is_dir() else finest
        t_max = float(np.loadtxt(data_dir / "constraint_norms_levels.dat")[-1, 0])
    data = load(RUNS, PSI4_R, t_max)
    fig = sw.draw(data, BOX, ns, R_EXACT, look, "hold", PSI4_R)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out or FIGURES / STEM)

    print(f"D21 X=1.829 triplet N {' / '.join(map(str, ns))}, t <= {t_max:.2f}")
    sw.report(data, ns, R_EXACT, "hold", PSI4_R)
    print(f"palette {args.palette}; label audit: "
          f"{'clean' if not problems else f'{len(problems)} problem(s): {problems}'}")
    rel = png.relative_to(REPO) if png.is_relative_to(REPO) else png
    print(f"wrote {rel}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
