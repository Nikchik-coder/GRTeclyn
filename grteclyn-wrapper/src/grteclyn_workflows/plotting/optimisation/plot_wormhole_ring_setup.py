"""Draw the November 4 weak-ring wormhole setup, without inventing field data.

Run from the repository root with the wrapper Python environment. All shaded
profiles and the two-ended embedding are explanatory artwork, not interpolation
of the solved fields. The dimensions quoted are from the recorded finest-grid
diagnostics in research/optimisation/STATUS.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import numpy as np

BG = "#fcfcfa"
INK = "#253445"
MUTED = "#617182"
BLUE = "#286fa7"
PURPLE = "#7850a5"
TEAL = "#00877e"


def curved_arrow(ax, centre, radius, start, end, color, *, squash=1, lw=2):
    angle = np.deg2rad(np.linspace(start, end, 90))
    x = centre[0] + radius * np.cos(angle)
    y = centre[1] + squash * radius * np.sin(angle)
    ax.plot(x, y, color=color, lw=lw, solid_capstyle="round", zorder=8)
    ax.add_patch(FancyArrowPatch((x[-4], y[-4]), (x[-1], y[-1]),
                                arrowstyle="-|>", mutation_scale=17,
                                color=color, lw=lw, zorder=9))


def text(ax, x, y, label, *, size=12, color=INK, weight="normal", ha="left"):
    return ax.text(x, y, label, fontsize=size, color=color, weight=weight,
                   ha=ha, va="top", linespacing=1.5, zorder=20)


def leader(ax, vertices, color):
    points = np.asarray(vertices)
    ax.plot(points[:, 0], points[:, 1], color=color, lw=1.25, zorder=10)
    ax.plot(*points[-1], "o", color=color, ms=5, mec=BG, mew=1.2, zorder=11)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(
        "results/optimisation/figures/setup/wormhole-ring-setup.png"))
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path("grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat.json").read_text())
    if config["throat_radius"] != 2.0:
        raise ValueError("This illustration describes the R_A=2 weak-ring pilot")

    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK,
                         "svg.fonttype": "none"})
    fig = plt.figure(figsize=(18, 11.5), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 18), ylim=(0, 11.5), aspect="equal")
    ax.axis("off")
    text(ax, .75, 10.94, "A rotating ring around each wormhole mouth", size=27, weight="bold")
    text(ax, .77, 10.28, "The matter rotates. Its gravity drags spacetime, including the throat, with it.",
         size=15, color=MUTED)
    text(ax, .78, 9.66, "WEAK RAILGUN RING  /  SYMMETRIC TWO-ENDED WORMHOLE", size=10, color=MUTED)

    # Main mouth view: deliberately qualitative smooth shading, with no colour
    # bar or contour that could be mistaken for a measured density threshold.
    cx, cy, radius = 7.05, 6.15, 2.37
    grid = np.linspace(-3.45, 3.45, 701)
    xx, yy = np.meshgrid(grid, grid)
    r = np.hypot(xx, yy)
    strength = .78*np.exp(-.5*((r-radius)/.40)**2) + .12*np.exp(-.5*(r/2.5)**2)
    fade = np.clip((3.44-r)/.50, 0, 1)
    strength *= fade*fade*(3-2*fade)
    rgb = np.asarray(to_rgb(BG))[None, None, :]*(1-strength[..., None])
    rgb += np.asarray(to_rgb("#337bb7"))[None, None, :]*strength[..., None]
    ax.imshow(rgb, extent=(cx-3.45, cx+3.45, cy-3.45, cy+3.45), origin="lower", zorder=1)
    # The throat outline names a surface, not a material edge or a horizon.
    throat = .70
    ax.add_patch(Circle((cx, cy), throat, fc="#eee9f5", ec=BG, lw=6, zorder=4))
    ax.add_patch(Circle((cx, cy), throat, fill=False, ec=PURPLE, lw=2.1, zorder=5))
    text(ax, cx, cy+.18, "THROAT", size=9, color=PURPLE, weight="bold", ha="center")
    ax.plot(cx, cy-.17, marker="o", ms=5, color=PURPLE, zorder=8)
    curved_arrow(ax, (cx, cy), 2.38, 80, 20, "#ffffff", lw=2.7)
    curved_arrow(ax, (cx, cy), 2.38, 260, 200, "#ffffff", lw=2.7)
    curved_arrow(ax, (cx, cy), 1.12, 165, 90, PURPLE, lw=2)
    curved_arrow(ax, (cx, cy), 1.12, -15, -90, PURPLE, lw=2)
    text(ax, cx, 9.05, "VIEW INTO ONE MOUTH", size=10, color=MUTED, weight="bold", ha="center")

    text(ax, .78, 8.54, "Rotating scalar matter", size=15, color=BLUE, weight="bold")
    text(ax, .78, 8.12, "The blue matter is the ring.\nIts angular momentum sources\nthe surrounding frame dragging.", size=12)
    leader(ax, [(3.53, 7.18), (4.10, 7.18), (5.16, 7.58)], BLUE)

    text(ax, .78, 6.47, "The throat is dragged too", size=15, color=PURPLE, weight="bold")
    text(ax, .78, 6.05, "Purple arrows show the induced\nrotation of local inertial frames.\nNo separate throat spin is imposed.", size=12)
    leader(ax, [(3.75, 5.06), (4.44, 5.06), (6.00, 6.55)], PURPLE)

    text(ax, .78, 4.22, "Diffuse matter", size=15, color=BLUE, weight="bold")
    text(ax, .78, 3.80, "The ring has smooth tails.\nThe region toward the throat\nis not an empty vacuum gap.", size=12)
    leader(ax, [(3.62, 3.02), (4.43, 3.02), (5.83, 5.13)], BLUE)

    text(ax, 7.1, 3.32, "Ring density peak: circumferential radius ≈ 6.77", size=11,
         color=BLUE, ha="center")
    text(ax, 7.1, 2.96, "Throat area radius: 2  •  fixed area: 16π", size=11,
         color=PURPLE, ha="center")
    text(ax, 7.1, 2.59, "White arrows: matter rotation; purple: frame dragging.", size=9.5,
         color=MUTED, ha="center")

    # A topological embedding sketch. Its vertical axis separates the two
    # asymptotic ends; it is not a physical distance or a second wormhole.
    text(ax, 11.25, 8.95, "One wormhole, two sides", size=16, weight="bold")
    text(ax, 11.25, 8.50, "Matching rings on opposite sides\nof the same connecting throat.", size=12, color=MUTED)
    mx, my = 14.2, 5.92
    u = np.linspace(-1.47, 1.47, 181)
    width = .47 + .68*u*u
    theta = np.linspace(0, 2*np.pi, 240)
    # Light wireframe surface; lavender is geometry, not a measured phantom map.
    for angle in np.linspace(0, 2*np.pi, 17)[:-1]:
        x = mx+width*np.cos(angle)
        y = my+u+.20*width*np.sin(angle)
        ax.plot(x, y, color="#bcb3cc", alpha=.65, lw=.7, zorder=2)
    for v in np.linspace(-1.47, 1.47, 13):
        w = .47+.68*v*v
        ax.plot(mx+w*np.cos(theta), my+v+.20*w*np.sin(theta), color="#c9c0d6", lw=.7, zorder=2)
    # Blue ellipses encode ring location only: widths and brightness have no
    # quantitative meaning, and no hard boundary is drawn for scalar matter.
    for sign in (-1, 1):
        ring_y = my+sign*1.42
        for line_width, alpha in [(22, .055), (16, .10), (10, .22), (5, .65)]:
            ax.plot(mx+1.83*np.cos(theta), ring_y+.34*np.sin(theta),
                    color=BLUE, lw=line_width, alpha=alpha, zorder=4)
    ax.plot(mx+.47*np.cos(theta), my+.094*np.sin(theta), color=PURPLE, lw=2.5, zorder=6)
    text(ax, 16.48, 7.45, "Side A", size=11, color=BLUE)
    text(ax, 16.48, 4.62, "Side B", size=11, color=BLUE)
    leader(ax, [(12.05, 5.94), (13.70, 5.94)], PURPLE)
    text(ax, 11.27, 6.06, "Throat", size=11, color=PURPLE)
    text(ax, 14.2, 3.91, "Both distant ends are nonrotating.", size=11, ha="center", color=MUTED)

    text(ax, 11.25, 3.31, "Exotic support is still present", size=14, weight="bold", color=PURPLE)
    text(ax, 11.25, 2.90, "A phantom scalar supports the throat.\nThe solve lets it adjust to the rotating ring.", size=12)

    ax.add_patch(FancyBboxPatch((.76, .92), 16.48, 1.06,
                               boxstyle="round,pad=0.02,rounding_size=0.13",
                               facecolor="#eef3f4", edgecolor="none", zorder=0))
    text(ax, 1.02, 1.76, "WHAT THIS RUN TESTS", size=10, weight="bold", color=TEAL)
    text(ax, 1.02, 1.41, "Can the rotating matter reduce the exotic support needed for the same throat area?",
         size=14, color=INK)
    text(ax, .78, .64, "Setup schematic: shading, arrow lengths and the bridge shape are illustrative, not a solved density map or an exact embedding.",
         size=9.5, color=MUTED)
    text(ax, .78, .32, "Weak-ring pilot · 4 November 2026 · Radius annotations: 210 × 36 grid; full three-grid validation remains incomplete.",
         size=9.5, color=MUTED)

    from grteclyn_workflows.plotting.wormhole_merger.style import label_audit
    audit = label_audit(fig)
    if audit:
        raise RuntimeError("Illustration label audit failed: " + "; ".join(audit))
    fig.savefig(args.out, dpi=240, facecolor=BG)
    fig.savefig(args.out.with_suffix(".svg"), facecolor=BG)
    plt.close(fig)
    provenance = {
        "kind": "setup schematic; not a numerical field reconstruction",
        "run": "railgun-throat-20261104T201026",
        "source_commit": "1bb61204b3d4bcf378c0dddf788a481d77f2834a",
        "configuration": "grteclyn-wrapper/scripts/campaigns/optimisation/configs/railgun_throat.json",
        "diagnostic_source": "research/optimisation/STATUS.md",
        "diagnostic_grid": [210, 36],
        "throat_area_radius": 2.0,
        "ring_peak_circumferential_radius_rounded": 6.77122,
        "geometry": "matching scalar ring lobes on the two sides of one throat",
        "artwork": "Qualitative blue tails, throat disk and embedding wireframe; no density data inferred",
        "arrows": "White: matter angular momentum; purple: induced frame dragging. No angular speeds encoded.",
        "validation": "Finest grid passed; campaign three-grid acceptance failed. No stability or reduction claim depicted.",
        "label_audit": audit,
        "rebuild": "grteclyn-wrapper/.venv/bin/python -m grteclyn_workflows.plotting.optimisation.plot_wormhole_ring_setup",
    }
    args.out.with_suffix(".json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(args.out)


if __name__ == "__main__":
    main()
