#!/usr/bin/env python3
r"""Kleihaus & Kunz 2014, Fig. 1: its quantities, its Kerr curves, its numbers.

KK 2014 (Kleihaus & Kunz, "Rotating Ellis wormholes in four dimensions",
PRD 90, 121503(R), arXiv:1409.1503) plot the symmetric rotating wormholes
against the throat's equatorial velocity v_e: (a) M/M0 and J/J0, (b) the
polar and areal radii R_p/R and R_A/R at fixed equatorial radius R, each
beside its Kerr curve.  Their normalisation (their eq. 12, G = c = 1) is
M0 = R, Omega0 = 1/R, J0 = R^2/2, so in our conventions M/M0 = mu_+/R_e and
J/J0 = 2J_+/R_e^2; R_p is the polar circumference over 2 pi and
R_A = sqrt(A / 4 pi).

Their wormhole curves exist only as drawn lines.  ``digitize`` reads them
off the published raster (kept beside the papers) into numbers:

- calibration: the two plot borders are the long dark pixel runs, and the
  data ranges are the printed ones, (a) 0..1 x 0..0.5 and (b) 0..1 x
  0.6..1; every major tick lies within half a pixel of the calibration;
- each curve is a colour core (red M/M0 and R_p/R, green J/J0 and R_A/R,
  blue Omega J/(Omega0 J0), their Smarr dots, which cover the red M/M0
  line below v_e ~ 0.2 and above ~ 0.9), read column by column as the
  intensity-weighted centre of its single run of pixels, with the
  same-coloured Kerr curve masked out by its closed form and the key
  masked out by its box; columns averaged in bins of 0.01 in v_e;
- accuracy: the same reader run on the printed Kerr curves (masking the
  wormhole curve instead) against their closed forms.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.kk2014

writes ``results/spinningwormhole/solver/kk2014_fig1_digitized.tsv`` (and
prints the accuracy), which the comparison figure reads; the raster is not
needed again.
"""

from __future__ import annotations

import argparse
import datetime
import math
import pathlib

import numpy as np

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions

IMAGE = solutions.REPO / "research" / "spinningwormhole" / "article" / "articles" / "kk2014_fig1.png"
DIGITIZED = solutions.REPO / "results" / "spinningwormhole" / "solver" / "kk2014_fig1_digitized.tsv"
RANGES = (((0.0, 1.0), (0.0, 0.5)), ((0.0, 1.0), (0.6, 1.0)))   # (x, y) per panel, left to right
TAIL_GATE = 1e-11            # the continuation's acceptance gate on spectral tails
CORE = 80                    # colour excess (0-255) of a curve's core pixels
BAND_PX = 5.0                # half-width of the mask laid over the other curve
BIN = 0.01                   # v_e width of one digitized point
# The printed keys' coloured samples, in data coordinates (v_e, value) per panel.
KEYS = (((0.20, 0.40), (0.33, 0.49)), ((0.10, 0.32), (0.62, 0.70)))
# curve: (panel, colour, the quantity whose other curve is masked).  Their
# Omega J dots are drawn ON the M/M0 line and hide it below v_e ~ 0.2 and
# above ~ 0.9, so they are read as a curve of their own.
CURVES = {"M_over_M0": (0, "red", "M"), "OmJ_over_OmJ0": (0, "blue", "OmJ"),
          "J_over_J0": (0, "green", "J"),
          "Rp_over_R": (1, "red", "Rp"), "RA_over_R": (1, "green", "RA")}


def kerr(v: np.ndarray) -> dict[str, np.ndarray]:
    """Kerr at fixed equatorial horizon radius R = 2M, by v_e = a/r_H."""
    v = np.asarray(v, dtype=float)
    alpha = 2.0 * v / (1.0 + v**2)                     # a/M
    r_h = 2.0 / (1.0 + v**2)                           # r_H/M
    th = np.linspace(0.0, math.pi, 2001)
    rp = np.array([np.trapezoid(np.sqrt(rh**2 + (al * np.cos(th)) ** 2), th)
                   for rh, al in zip(np.atleast_1d(r_h), np.atleast_1d(alpha))]) / (2.0 * math.pi)
    return {"M": np.full_like(v, 0.5), "J": v / (1.0 + v**2), "OmJ": v**2 / (1.0 + v**2),
            "Rp": rp.reshape(v.shape), "RA": 1.0 / np.sqrt(1.0 + v**2)}


def symmetric_family(rows: list[dict], static_end: bool = False) -> dict[str, np.ndarray]:
    """Our eta0 = 1, gamma = 0 members that pass the tail gate, one per J, in
    order of v_e, in KK's normalisation.  ``static_end`` prepends the exact
    static Ellis member (v_e = 0: M = J = 0, R_p = R_A = R)."""
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
    out = {"v": c["v_e"], "M": c["mu_plus"] / c["R_e"], "J": 2.0 * c["J"] / c["R_e"] ** 2,
           "OmJ": 2.0 * c["Omega_throat"] * c["J"] / c["R_e"],
           "Rp": c["R_pol"] / c["R_e"], "RA": c["R_A"] / c["R_e"]}
    if static_end:
        out = {k: np.concatenate(([s], a)) for (k, a), s in
               zip(out.items(), (0.0, 0.0, 0.0, 0.0, 1.0, 1.0))}
    out["smarr_rel"] = c["smarr_rel"]
    return out


def thin(x: np.ndarray, ys: list[np.ndarray], spans: tuple[float, float],
         sep: float) -> np.ndarray:
    """Indices of an evenly spaced subset: a point is kept once it sits
    ``sep`` (in frame fractions) from the last kept one on any of ``ys``;
    the last point is always kept."""
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


# ---------------------------------------------------------------------------
# The raster.
# ---------------------------------------------------------------------------

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


def _runs(mask: np.ndarray, min_len: int = 1, gap: int = 0) -> list[tuple[int, int]]:
    """(start, end) of every run of True at least ``min_len`` long; runs
    separated by at most ``gap`` False entries are joined."""
    idx = np.nonzero(mask)[0]
    if not len(idx):
        return []
    cuts = np.nonzero(np.diff(idx) > gap + 1)[0]
    starts = np.concatenate(([idx[0]], idx[cuts + 1]))
    ends = np.concatenate((idx[cuts], [idx[-1]]))
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


class Axes:
    """Pixel <-> data for one calibrated panel."""

    def __init__(self, box, ranges):
        (self.left, self.right, self.top, self.bottom), ((self.x0, self.x1), (self.y0, self.y1)) = box, ranges

    def x_data(self, px):
        return self.x0 + (np.asarray(px) - self.left) / (self.right - self.left) * (self.x1 - self.x0)

    def y_data(self, py):
        return self.y0 + (self.bottom - np.asarray(py)) / (self.bottom - self.top) * (self.y1 - self.y0)

    def x_px(self, x):
        return self.left + (np.asarray(x) - self.x0) / (self.x1 - self.x0) * (self.right - self.left)

    def y_px(self, y):
        return self.bottom - (np.asarray(y) - self.y0) / (self.y1 - self.y0) * (self.bottom - self.top)


def _excess(rgb: np.ndarray) -> dict[str, np.ndarray]:
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    return {"red": r - np.maximum(g, b), "green": g - np.maximum(r, b),
            "blue": b - np.maximum(r, g)}


def read_curve(excess: np.ndarray, ax: Axes, masked: list, key_box) -> np.ndarray:
    """(v_e, value, columns) per BIN-wide bin along one coloured curve.

    ``masked`` lists functions v_e -> value of the curves to blank out (the
    other curve of the same colour); ``key_box`` is the printed key's
    ((v0, v1), (y0, y1))."""
    h = excess.shape[0]
    rows = np.arange(h)
    (kv0, kv1), (ky0, ky1) = key_box
    samples = []
    for x in range(int(math.ceil(ax.left)) + 3, int(ax.right) - 2):
        col = excess[:, x].astype(float)
        inside = (rows > ax.top + 2) & (rows < ax.bottom - 2)
        v = float(ax.x_data(x))
        if kv0 <= v <= kv1:
            inside &= ~((rows >= ax.y_px(ky1)) & (rows <= ax.y_px(ky0)))
        for f in masked:
            ends = ax.y_px(f(np.array([ax.x_data(x - 0.5), ax.x_data(x + 0.5)])))
            inside &= ~((rows >= ends.min() - BAND_PX) & (rows <= ends.max() + BAND_PX))
        runs = _runs(inside & (col >= CORE), gap=1)
        if len(runs) != 1:
            continue
        a, b = runs[0]
        w = col[a:b + 1]
        samples.append((v, float(ax.y_data((rows[a:b + 1] * w).sum() / w.sum()))))
    if not samples:
        return np.zeros((0, 3))
    s = np.array(samples)
    bins = np.floor(s[:, 0] / BIN).astype(int)
    out = [(s[bins == k, 0].mean(), s[bins == k, 1].mean(), (bins == k).sum())
           for k in np.unique(bins) if (bins == k).sum() >= 2]
    return np.array(out)


def digitize(image: pathlib.Path = IMAGE, table: pathlib.Path = solutions.TABLE) -> dict:
    """The five wormhole curves of ``CURVES`` and, as the accuracy check, the
    printed Kerr curves the reader can reach, each an (n, 3) array."""
    from PIL import Image

    from scipy.interpolate import PchipInterpolator

    img = Image.open(image).convert("RGB")
    rgb = np.asarray(img)
    gray = np.asarray(img.convert("L"), dtype=float)
    axes = [Axes(b, r) for b, r in zip(frames(gray), RANGES)]
    exc = _excess(rgb)
    fam = symmetric_family(solutions.load(table), static_end=True)
    ours = {k: PchipInterpolator(fam["v"], fam[k], extrapolate=False)
            for k in ("M", "OmJ", "J", "Rp", "RA")}

    def kerr_of(q):
        return lambda v: kerr(v)[q]

    def ours_of(q):
        return lambda v: np.nan_to_num(ours[q](np.clip(v, 0.0, fam["v"][-1])))

    out = {}
    for name, (panel, colour, q) in CURVES.items():
        masked = [kerr_of(q)] if q != "M" else [lambda v: np.full_like(np.asarray(v, float), 0.5)]
        out[name] = read_curve(exc[colour], axes[panel], masked, KEYS[panel])
        if q != "M":                       # Kerr M/M0 = 1/2 is the top border itself
            out["kerr_" + name] = read_curve(exc[colour], axes[panel], [ours_of(q)], KEYS[panel])
    return out


def accuracy(curves: dict) -> dict[str, tuple[float, float, int]]:
    """rms and max |digitized - closed form| on each printed Kerr curve."""
    q_of = {name: q for name, (_, _, q) in CURVES.items()}
    out = {}
    for name, arr in curves.items():
        if name.startswith("kerr_") and len(arr):
            d = arr[:, 1] - kerr(arr[:, 0])[q_of[name[5:]]]
            out[name] = (float(np.sqrt(np.mean(d**2))), float(np.abs(d).max()), len(arr))
    return out


def write(curves: dict, acc: dict, out: pathlib.Path = DIGITIZED) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Kleihaus & Kunz, PRD 90, 121503(R) (2014), arXiv:1409.1503, Fig. 1: the symmetric",
        "# rotating wormholes' curves, digitized from the published raster by",
        "# grteclyn_wrapper.visualisation.spinning_wormhole.kk2014 "
        f"({datetime.date.today().isoformat()}).",
        "# M_over_M0 = mu_+/R, OmJ_over_OmJ0 = 2 Omega J/R (their blue dots, = M/M0 by their",
        "# Smarr relation), J_over_J0 = 2J/R^2 (their J0 = R^2/2), Rp_over_R, RA_over_R;",
        "# kerr_* are the printed Kerr curves read the same way, the accuracy check:",
    ] + [f"#   {k}: rms {r:.1e}, max {m:.1e} over {n} points" for k, (r, m, n) in acc.items()] + [
        "# columns: curve, v_e, value, raster columns averaged",
        "curve\tv_e\tvalue\tn_cols",
    ]
    for name, arr in curves.items():
        lines += [f"{name}\t{v:.5f}\t{y:.5f}\t{int(n)}" for v, y, n in arr]
    out.write_text("\n".join(lines) + "\n")


def load(path: pathlib.Path = DIGITIZED) -> dict[str, np.ndarray]:
    """curve -> (n, 2) array of (v_e, value)."""
    out: dict[str, list] = {}
    for line in pathlib.Path(path).read_text().splitlines():
        if not line or line.startswith("#") or line.startswith("curve\t"):
            continue
        name, v, y, _ = line.split("\t")
        out.setdefault(name, []).append((float(v), float(y)))
    return {k: np.array(v) for k, v in out.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", type=pathlib.Path, default=IMAGE)
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--out", type=pathlib.Path, default=DIGITIZED)
    args = ap.parse_args(argv)
    curves = digitize(args.image, args.table)
    acc = accuracy(curves)
    write(curves, acc, args.out)
    for name, arr in curves.items():
        if len(arr):
            print(f"  {name:16s} {len(arr):3d} points, v_e {arr[0, 0]:.3f}-{arr[-1, 0]:.3f}")
    for name, (rms, mx, n) in acc.items():
        print(f"  accuracy {name:16s} rms {rms:.1e}  max {mx:.1e}  ({n} points)")
    print(f"wrote {args.out.relative_to(solutions.REPO) if args.out.is_relative_to(solutions.REPO) else args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
