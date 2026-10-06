#!/usr/bin/env python3
"""The merger campaign's collapse diagnostics, as ONE grid, with no empty panels.

The general plotter (``visualisation/diagnostic/diagnostic.py``) lays out a
fixed twelve-panel grid built for ``WormholeCollapse``, which writes horizon and
areal-radius columns.  ``BinaryWormholeMerger`` does not write them, so on this
campaign's runs six of those twelve panels came out blank or flat-zero -- max
trapped-surface radius, the null-expansion proxy and its radius, throat areal
radius, expansion velocity, instability growth.  A blank panel is not a null
result, it is a missing column, and printing it next to real data invites the
reader to read one as the other.

So this module keeps that figure's LOOK exactly -- Computer Modern, a lettered
grid, black curves on a dashed grid -- and builds the panel list from what the
run actually wrote.  It also brings in the two constraint norms and one panel
those diagnostics cannot give on their own: the core indicators and the
constraints rescaled onto a common range, which is what answers "do they grow
together?".  They do not, and that panel is the evidence.

  python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_collapse_diagnostics \\
      --run v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600 --t-min 36 \\
      --out /tmp/p012_collapse_dashboard.png

NB the article's spiral collapse page at
``figures/05_binary_spiral/p012_collapse_diagnostics`` is drawn by
``plot_spiral_collapse.py`` (PRD grammar, horizon scans included) since
2026-09-18 -- do not point ``--out`` there, this module would overwrite it.
"""
from __future__ import annotations

import argparse
import pathlib
import string

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    find_packed, find_run,
)

# BinaryWormholeLevel's writer, in order.  The file carries NO header on a
# restart, so the order is recorded here rather than parsed.
COLS = ("min_lapse", "min_chi", "max_abs_K", "min_lapse_x", "min_lapse_y",
        "min_lapse_z", "min_phi", "max_phi", "min_Pi", "max_Pi")


def _resolve(spec: str) -> pathlib.Path:
    p = pathlib.Path(spec).expanduser()
    if p.is_dir():
        return p
    repo = pathlib.Path(__file__).resolve().parents[5]
    try:
        base = find_packed(spec)
        if (base / "collapse_diagnostics.dat").exists() or \
           (base / "data" / "collapse_diagnostics.dat").exists():
            return base
    except Exception:
        pass
    return find_run(repo / "runs" / "wormhole_merger", spec)


def _read(base: pathlib.Path, name: str) -> np.ndarray | None:
    for cand in (base / name, base / "data" / name):
        if cand.exists():
            d = np.loadtxt(cand)
            return d[np.argsort(d[:, 0])]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="run NAME or directory")
    ap.add_argument("--t-min", type=float, default=None)
    ap.add_argument("--t-max", type=float, default=None)
    ap.add_argument("--skip-settle", type=float, default=0.06,
                    help="drop this much time at the start.  A restart reduces over an "
                         "INCOMPLETE level hierarchy for its first few steps, and those "
                         "rows report the coarse grid's extrema -- left in, one row sets "
                         "three of the axes and every panel becomes mostly empty.")
    ap.add_argument("--chi-floor", type=float, default=1e-8)
    ap.add_argument("--ncol", type=int, default=3)
    ap.add_argument("--dr", type=float, default=0.03125,
                    help="shell width the run's core_radial_profile was given")
    ap.add_argument("--edge", type=float, default=0.2,
                    help="|K| defining the outer edge of the disturbance")
    ap.add_argument("--r-max", type=float, default=2.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base = _resolve(args.run)
    d = _read(base, "collapse_diagnostics.dat")
    if d is None:
        raise SystemExit(f"no collapse_diagnostics.dat under {base}")
    c = _read(base, "constraint_norms.dat")
    prof = None
    for nm in ("core_radial_profile.dat", "core_radial_profile.dat.gz"):
        for cand in (base / nm, base / "data" / nm):
            if cand.exists():
                import gzip
                op = gzip.open if cand.suffix == ".gz" else open
                with op(cand, "rt") as fh:
                    prof = np.loadtxt(fh)
                break
        if prof is not None:
            break

    lo = (args.t_min if args.t_min is not None else d[0, 0]) + args.skip_settle
    hi = args.t_max if args.t_max is not None else d[-1, 0]
    d = d[(d[:, 0] >= lo) & (d[:, 0] <= hi)]
    t = d[:, 0]
    col = {n: d[:, i + 1] for i, n in enumerate(COLS) if i + 1 < d.shape[1]}
    if c is not None:
        c = c[(c[:, 0] >= lo) & (c[:, 0] <= hi)]

    def live(y) -> bool:
        """A column with no information is not a result -- leave it out."""
        y = np.asarray(y, dtype=float)
        y = y[np.isfinite(y)]
        return len(y) > 0 and float(np.ptp(y)) > 0.0

    # ---- build the panel list from what the run actually wrote ---------------
    panels = []
    if live(col.get("min_lapse", [])):
        panels.append(("line", t, col["min_lapse"], r"$\min(\alpha)$",
                       r"Minimum lapse: $\alpha$", True))
    if live(col.get("min_chi", [])):
        panels.append(("line", t, col["min_chi"], r"$\min(\chi)$",
                       r"Minimum conformal factor: $\chi$", True))
    # No standalone max|K| panel either: it is the solid curve of the
    # comparison panel, with its absolute peak in that panel's key.
    # No standalone Hamiltonian or momentum panel: both are in the comparison
    # panel below, with their absolute peaks in its key, and drawing a curve
    # twice says nothing the first drawing did not.
    if live(col.get("max_phi", [])):
        panels.append(("pair", t, (col["max_phi"], col["min_phi"]), r"$\phi$",
                       r"Scalar field profile $\phi$", False))
    if live(col.get("max_Pi", [])):
        panels.append(("pair", t, (col["max_Pi"], col["min_Pi"]), r"$\Pi$",
                       r"Scalar field momentum $\Pi$", False))
    if c is not None and live(col.get("max_abs_K", [])):
        panels.append(("compare", t, None, r"normalised $\log_{10}$",
                       r"Growth compared: core against constraints", False))
    if prof is not None:
        panels.append(("radial:K", None, None, r"$\max|K|$",
                       r"Curvature against radius", True))
        panels.append(("radial:chi", None, None, r"$\min(\chi)$",
                       r"Conformal factor against radius", True))
        panels.append(("radial:lapse", None, None, r"$\min(\alpha)$",
                       r"Lapse against radius", True))
        panels.append(("extent", None, None, r"$r$",
                       r"Where the disturbance is, and how wide", False))

    n = len(panels)
    ncol = min(args.ncol, n)
    nrow = int(np.ceil(n / ncol))
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Computer Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
    })
    # sharex is off: one panel is against RADIUS, not time, and sharing the
    # axis with it silently rescales every other panel.
    fig, axes = plt.subplots(nrow, ncol, figsize=(5.0 * ncol, 4.0 * nrow),
                             squeeze=False)
    flat = axes.flatten()

    floored = col.get("min_chi")
    t_floor = None
    if floored is not None and (floored <= args.chi_floor * 1.01).any():
        t_floor = t[np.argmax(floored <= args.chi_floor * 1.01)]
    t_peak = c[np.argmax(c[:, 2]), 0] if c is not None else None

    for ax, (kind, x, y, ylab, title, logy) in zip(flat, panels):
        if kind == "line":
            (ax.semilogy if logy else ax.plot)(x, y, color="black", linewidth=1.5)
        elif kind == "pair":
            ax.plot(x, y[0], color="black", linewidth=1.5, label=r"max")
            ax.plot(x, y[1], color="black", linewidth=1.5, linestyle="--", label=r"min")
            ax.legend(loc="best", frameon=True, framealpha=0.9, fontsize=9)
        elif kind.startswith("radial:"):
            which = kind.split(":", 1)[1]
            pt, pa = prof[:, 0], prof[:, 1:]
            nsh = pa.shape[1] // 5
            rr = (np.arange(nsh) + 0.5) * args.dr
            block = {"chi": 0, "K": 1, "lapse": 2}[which]
            y = pa[:, block * nsh:(block + 1) * nsh].copy()
            # the module's sentinels: BIG for the mins, -BIG for the max
            y = np.where(np.abs(y) > 1e29, np.nan, y)
            times = np.linspace(max(pt[0], lo), pt[-1], 6)
            cmap = plt.cm.Greys
            for i, tt in enumerate(times):
                k = int(np.argmin(abs(pt - tt)))
                ax.semilogy(rr, y[k], lw=1.3,
                            color=cmap(0.35 + 0.6 * i / (len(times) - 1)),
                            label=rf"$t={pt[k]:.1f}$")
            if which == "K":
                ax.axhline(args.edge, color="red", lw=0.8, ls=":")
            if which == "chi":
                ax.axhline(args.chi_floor, color="red", lw=0.8, ls=":")
            ax.set_xlim(0, args.r_max)
            ax.set_xlabel(r"$r$")
            ax.legend(loc="best", frameon=True, framealpha=0.9, fontsize=7.5, ncol=2)
        elif kind == "extent":
            pt, pa = prof[:, 0], prof[:, 1:]
            nsh = pa.shape[1] // 5
            dr = args.dr
            rr = (np.arange(nsh) + 0.5) * dr
            aK = pa[:, nsh:2 * nsh]
            aK = np.where(aK < -1e29, np.nan, aK)
            bg = aK[:, int(0.4 / dr)]
            pk = np.nanargmax(np.where(np.isnan(aK), -np.inf, aK), axis=1)
            vpk = aK[np.arange(len(pt)), pk]
            real = vpk > 2.0 * bg
            edge = np.array([rr[np.where(aK[k] > args.edge)[0].max()]
                             if (aK[k] > args.edge).any() else np.nan
                             for k in range(len(pt))])
            ax.plot(pt, np.where(real, rr[pk], np.nan), color="black", lw=1.5,
                    label=r"$r_{\mathrm{peak}}$")
            ax.plot(pt, edge, color="black", lw=1.2, ls="--", label=r"$r_{\mathrm{edge}}$")
            ax.set_xlim(lo, hi)
            ax.set_xlabel(r"$t$")
            ax.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=8.5)
            ax.text(0.5, 0.95, rf"widest {np.nanmax(edge):.3f}", transform=ax.transAxes,
                    ha="center", va="top", fontsize=8)
        else:
            def unit(v):
                v = np.log10(np.maximum(np.asarray(v, float), 1e-300))
                return (v - v.min()) / max(float(np.ptp(v)), 1e-30)
            hh = np.interp(t, c[:, 0], c[:, 1])
            mm = np.interp(t, c[:, 0], c[:, 2])
            K = col["max_abs_K"]
            ax.plot(t, unit(K), color="black", lw=1.6,
                    label=rf"$\max(|K|)$, peak {K.max():.2f}")
            ax.plot(t, unit(hh), color="black", lw=1.2, ls="--",
                    label=rf"$\|\mathcal{{H}}\|_{{L^2}}$, peak {c[:,1].max():.1e}")
            ax.plot(t, unit(mm), color="red", lw=1.2, ls="-.",
                    label=rf"$\|\mathcal{{M}}\|_{{L^2}}$, peak {c[:,2].max():.1e}")
            ax.set_ylim(-0.04, 1.45)     # headroom so the key clears the peaks
            ax.legend(loc="upper left", frameon=True, framealpha=0.9, fontsize=8.5)
        ax.set_ylabel(ylab)
        ax.set_title(title)
        ax.grid(True, which="both", ls="--", alpha=0.6)
        if kind.startswith("radial:"):
            continue
        if kind != "extent":
            ax.set_xlim(lo, hi)
            ax.set_xlabel(r"$t$")
        if t_peak is not None:
            ax.axvline(t_peak, color="gray", lw=0.8, ls="--", alpha=0.8)
        if t_floor is not None:
            ax.axvline(t_floor, color="red", lw=0.8, ls=":", alpha=0.8)

    for ax in flat[n:]:
        ax.set_visible(False)
    for ax, letter in zip(flat[:n], string.ascii_lowercase):
        ax.set_title(f"({letter}) {ax.get_title()}")
    fig.tight_layout()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight")
    print(f"saved {out.with_suffix('.png')} (+pdf) -- {n} panels, none empty")
    if c is not None:
        def corr(a, b):
            a, b = np.log10(np.maximum(a, 1e-300)), np.log10(np.maximum(b, 1e-300))
            return float(np.corrcoef(a, b)[0, 1])
        m = t >= 40.0
        print(f"  after t = 40: corr(log max|K|, log H) = "
              f"{corr(col['max_abs_K'][m], np.interp(t[m], c[:,0], c[:,1])):+.3f}, "
              f"corr(log max|K|, log M) = "
              f"{corr(col['max_abs_K'][m], np.interp(t[m], c[:,0], c[:,2])):+.3f}")


if __name__ == "__main__":
    main()
