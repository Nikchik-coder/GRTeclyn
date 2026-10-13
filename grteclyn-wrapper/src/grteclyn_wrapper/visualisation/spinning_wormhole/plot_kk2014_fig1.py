#!/usr/bin/env python3
r"""Kleihaus & Kunz 2014, Fig. 1, as published, with our solutions on it.

The background is the printed figure (Kleihaus & Kunz, "Rotating Ellis
wormholes in four dimensions", PRD 90, 121503(R) (2014), arXiv:1409.1503):
(a) M/M0, J/J0 and Omega J/(Omega0 J0) of the symmetric rotating wormholes
against the throat's equatorial velocity v_e, with the Kerr curves;
(b) the polar and areal radii R_p/R and R_A/R at fixed equatorial radius R.
Our members of the same family (eta0 = 1, gamma = 0 in the packed solver
table; every quantity here is scale-free) are drawn on top as open circles,
at the places the figure's own axes give them.

Their normalisation (their eq. 12, G = c = 1) is M0 = R, Omega0 = 1/R and
J0 = R^2/2, so M/M0 = mu_+/R_e, J/J0 = 2J_+/R_e^2 and
Omega J/(Omega0 J0) = 2 omega_0 J_+/R_e, which equals M/M0 by their Smarr
relation.  Ours holds to the packed ``smarr_rel`` (<= 1e-10), so those
circles would sit on the M/M0 ones and are not drawn twice.  R_p is the
polar circumference over 2 pi and R_A = sqrt(A / 4 pi), as in
``analysis/spinning_wormhole/observables.py``.

Calibration: the two plot borders are the long dark pixel runs of the
raster, and the data ranges are the printed ones, (a) 0..1 x 0..0.5 and
(b) 0..1 x 0.6..1.  Every major tick of both panels lies within half a
pixel of where that calibration puts it (checked 2026-10-13), and
``--check`` overdraws the closed-form Kerr curves on the printed ones.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_fig1

Reads ``research/spinningwormhole/article/articles/kk2014_fig1.png`` and
``results/spinningwormhole/solver/solutions.tsv``; writes
``results/spinningwormhole/figures/solver/kk2014_fig1_overlay`` (PNG + PDF).
"""

from __future__ import annotations

import argparse
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from PIL import Image  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

IMAGE = solutions.REPO / "research" / "spinningwormhole" / "article" / "articles" / "kk2014_fig1.png"
OUT = solutions.REPO / "results" / "spinningwormhole" / "figures" / "solver" / "kk2014_fig1_overlay"
RANGES = (((0.0, 1.0), (0.0, 0.5)), ((0.0, 1.0), (0.6, 1.0)))   # (x, y) per panel, left to right
TAIL_GATE = 1e-11            # the continuation's acceptance gate on spectral tails
OURS = dict(ls="none", marker="o", ms=4.6, mfc="none", mec="black", mew=0.9, clip_on=False,
            zorder=5)


def _clusters(values) -> list[float]:
    """Means of runs of consecutive integers (a border drawn two pixels wide
    is one border)."""
    out, run = [], []
    for v in sorted(set(values)):
        if run and v - run[-1] > 1:
            out.append(sum(run) / len(run))
            run = []
        run.append(v)
    if run:
        out.append(sum(run) / len(run))
    return out


def _runs(mask: np.ndarray, min_len: int) -> list[tuple[int, int]]:
    """(start, end) of every run of True at least ``min_len`` long."""
    edges = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    starts, ends = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0] - 1
    return [(a, b) for a, b in zip(starts, ends) if b - a + 1 >= min_len]


def frames(gray: np.ndarray) -> list[tuple[float, float, float, float]]:
    """(left, right, top, bottom) pixel centres of each panel's border, left
    to right: the columns and rows holding long dark runs."""
    dark = gray < 128
    h, w = dark.shape
    rows = [y for y in range(h) if _runs(dark[y], w // 6)]
    cols = [x for x in range(w) if _runs(dark[:, x], h // 3)]
    top_bottom, sides = _clusters(rows), _clusters(cols)
    if len(top_bottom) != 2 or len(sides) % 2:
        raise RuntimeError(f"expected one row of framed panels, found border rows "
                           f"{top_bottom} and columns {sides}")
    top, bottom = top_bottom
    return [(sides[i], sides[i + 1], top, bottom) for i in range(0, len(sides), 2)]


def symmetric_family(rows: list[dict]) -> dict[str, np.ndarray]:
    """The eta0 = 1, gamma = 0 members that pass the tail gate, one per J, in
    order of v_e, in the figure's normalisation."""
    seen, keep = set(), []
    for r in rows:
        if r["eta0"] != 1.0 or r["gamma"] != 0.0 or r["tail_max"] > TAIL_GATE:
            continue
        if round(r["J"], 9) not in seen:
            seen.add(round(r["J"], 9))
            keep.append(r)
    keep.sort(key=lambda r: r["v_e"])
    c = {k: np.array([r[k] for r in keep]) for k in
         ("v_e", "J", "mu_plus", "R_e", "R_pol", "R_A", "Omega_throat", "smarr_rel")}
    return {"v": c["v_e"], "M": c["mu_plus"] / c["R_e"], "J": 2.0 * c["J"] / c["R_e"] ** 2,
            "OmJ": 2.0 * c["Omega_throat"] * c["J"] / c["R_e"],
            "Rp": c["R_pol"] / c["R_e"], "RA": c["R_A"] / c["R_e"], "smarr_rel": c["smarr_rel"]}


def thin(x: np.ndarray, ys: list[np.ndarray], spans: tuple[float, float],
         sep: float) -> np.ndarray:
    """Indices of an evenly spaced subset: a point is kept once it sits
    ``sep`` (in frame fractions) from the last kept one on any of ``ys``;
    the fastest member is always kept."""
    if sep <= 0 or len(x) < 3:
        return np.arange(len(x))

    def dist(i, j):
        return max(math.hypot((x[i] - x[j]) / spans[0], (y[i] - y[j]) / spans[1]) for y in ys)

    keep = [0]
    for i in range(1, len(x) - 1):
        if dist(i, keep[-1]) >= sep:
            keep.append(i)
    if len(keep) > 1 and dist(len(x) - 1, keep[-1]) < sep:
        keep[-1] = len(x) - 1
    else:
        keep.append(len(x) - 1)
    return np.array(keep)


def kerr(v: np.ndarray) -> dict[str, np.ndarray]:
    """Kerr at fixed equatorial horizon radius R = 2M, by v_e = a/r_H."""
    alpha = 2.0 * v / (1.0 + v**2)                     # a/M
    r_h = 2.0 / (1.0 + v**2)                           # r_H/M
    th = np.linspace(0.0, math.pi, 2001)
    rp = np.array([np.trapezoid(np.sqrt(rh**2 + (al * np.cos(th)) ** 2), th)
                   for rh, al in zip(r_h, alpha)]) / (2.0 * math.pi)
    return {"M": np.full_like(v, 0.5), "J": v / (1.0 + v**2), "OmJ": v**2 / (1.0 + v**2),
            "Rp": rp, "RA": 1.0 / np.sqrt(1.0 + v**2)}


def draw(image: pathlib.Path, fam: dict[str, np.ndarray], sep: float, check: bool):
    img = Image.open(image).convert("RGB")
    w, h = img.size
    boxes = frames(np.asarray(img.convert("L"), dtype=float))
    fig = plt.figure(figsize=(w / 100.0, h / 100.0), dpi=100)
    bg = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    bg.imshow(np.asarray(img), interpolation="lanczos", aspect="auto")
    bg.set_xlim(-0.5, w - 0.5)
    bg.set_ylim(h - 0.5, -0.5)
    bg.set_axis_off()

    panels = []
    for (left, right, top, bottom), (xr, yr) in zip(boxes, RANGES):
        ax = fig.add_axes(((left + 0.5) / w, 1.0 - (bottom + 0.5) / h,
                           (right - left) / w, (bottom - top) / h))
        ax.set(xlim=xr, ylim=yr)
        ax.set_axis_off()
        ax.patch.set_visible(False)
        panels.append(ax)
    ax_a, ax_b = panels

    spans_a = (RANGES[0][0][1] - RANGES[0][0][0], RANGES[0][1][1] - RANGES[0][1][0])
    spans_b = (RANGES[1][0][1] - RANGES[1][0][0], RANGES[1][1][1] - RANGES[1][1][0])
    ia = thin(fam["v"], [fam["M"], fam["J"]], spans_a, sep)
    ib = thin(fam["v"], [fam["Rp"], fam["RA"]], spans_b, sep)
    for key in ("M", "J"):
        ax_a.plot(fam["v"][ia], fam[key][ia], **OURS)
    for key in ("Rp", "RA"):
        ax_b.plot(fam["v"][ib], fam[key][ib], **OURS)

    if check:
        v = np.linspace(0.0, 1.0, 301)
        k = kerr(v)
        line = dict(color="black", lw=0.8, ls=(0, (2.0, 2.0)), zorder=6)
        for key in ("J", "OmJ"):
            ax_a.plot(v, k[key], **line)
        for key in ("Rp", "RA"):
            ax_b.plot(v, k[key], **line)

    fig.legend([Line2D([], [], **{**OURS, "clip_on": True})],
               ["this work, same symmetric family: M/M$_0$ and J/J$_0$ in (a), "
                "R$_p$/R and R$_A$/R in (b)"],
               loc="upper center", bbox_to_anchor=(0.5, 0.995), frameon=False,
               fontsize=9.5, handletextpad=0.4)
    return fig, len(ia), len(ib), boxes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", type=pathlib.Path, default=IMAGE)
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--sep", type=float, default=0.035,
                    help="circle spacing along each curve, in frame fractions (0: every point)")
    ap.add_argument("--check", action="store_true",
                    help="overdraw the closed-form Kerr curves to show the axis calibration")
    args = ap.parse_args(argv)

    fam = symmetric_family(solutions.load(args.table))
    fig, na, nb, boxes = draw(args.image, fam, args.sep, args.check)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out, dpi=200)
    k = -1
    print("frames (left, right, top, bottom) px: "
          + "; ".join("(" + ", ".join(f"{b:g}" for b in box) + ")" for box in boxes))
    print(f"symmetric family: {len(fam['v'])} members, v_e {fam['v'][0]:.4f}-{fam['v'][k]:.4f}; "
          f"circles drawn {na} per curve in (a), {nb} in (b)")
    print(f"fastest member v_e {fam['v'][k]:.4f}: M/M0 {fam['M'][k]:.5f}, J/J0 {fam['J'][k]:.5f}, "
          f"OmJ/(Om0 J0) {fam['OmJ'][k]:.5f}, Rp/R {fam['Rp'][k]:.5f}, RA/R {fam['RA'][k]:.5f}; "
          f"Smarr gate max {fam['smarr_rel'].max():.1e}")
    print(f"label audit: {'clean' if not problems else f'{len(problems)} problem(s)'}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
