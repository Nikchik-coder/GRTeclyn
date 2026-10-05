# merge_headon_flip_d8_v1_L128_SERIES — the mode-3 production head-on as one history

The paper's head-on ran as three legs on the far-side-matched (mode-3) data
(d = 8, p = 0, flipped, L = 128, N = 256; M_ADM = 2.3573, leg 1's
`constraint_solve.dat`). This folder glues their in-code Ψ4 into one
continuous record, **t = 0 → 100**, so a figure draws the history rather than
the schedule.

| leg | run | max level | rows used |
|---|---|---|---|
| 1 | `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm` | 5 | t ≤ 35.00 — ran on to a NaN in h11 at t = 38.845 (the merged core, inside the MOTS); those rows dropped |
| 2 | `merge_headon_flip_d8_v1_L128_lvl6from35_scalar_chk_t100_csm_r03500` | 6 | 35.01 ≤ t ≤ 50.80 (stopped by hand) |
| 3 | `merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000` | 4 | t > 50.80 (to t = 100, exit 0, no NaN) |

**The seams carry nothing.** The in-code Ψ4 is identical on both overlaps
(t = 35–38.84 and t = 50–50.8: difference 0 on R = 18–36 and on every sphere at
t = 50, 1e-11 at R = 10), the level-0 constraint norms are continuous to
1.4 % / 0.1 %, and across each restart the (2,0) and (2,2) modes step by no
more than one ordinary time step's change (leg 3's `VALIDATION.md`, Seams).

## Files

`Weyl4_mode_20.dat` and `Weyl4_mode_22.dat`: in-code extraction, seven spheres
R = 10/14/18/20/28/36/44, ℓ = 2, dt = 0.01, with a five-line provenance header.
The modes are about the extraction's z axis, but the head-on falls along x, so
its quadrupole splits over the z-based (2,0) (a quarter of the power) and
(2,±2) (the rest): |h22/h20| = √(3/2) to 1.6 % on the burst at every sphere.

`Weyl4_mode_20_axis.dat` (2026-10-05): the quadrupole about the collision axis,
h'20 = 2 × the z-based (2,0) (sign kept), written by
`results/merger/analysis/headon_axis_modes.py` after it checks that split. The
figures, the search templates and every head-on number in the paper read this
file.

## Reading it — the level-1 noise gates

Fine-scale numerical noise grows on the level-1 refinement cube from t ≈ 65
(doubling every ~6 units; leg 3's `VALIDATION.md`, "The level-1 noise"), so a
sphere inside the cube (R ≤ 20) is clean to t ≈ 80, R = 28 (which cuts the
cube's corners) to t ≈ 90, and R = 36/44 (level 0) to t = 100. Read the
symmetry-forbidden (3,2) mode as the monitor. The figures'
`plot_psi4_gallery.DRAW_GATES` carry exactly these cuts.

## The scalar record (added 2026-10-05)

`scalar_modes.dat`: the chain's scalar stream (phi and Pi modes to l = 2 plus
`scalar_flux_kin`, six spheres R = 10/14/18/20/30/44, dt = 1) glued on the same
leg table as the Ψ4 files: leg 1 to t = 35, leg 2 to t = 50, leg 3 to t = 100.
Seam check: the flux is IDENTICAL (difference 0) on the three t = 36–38 rows the
level-5 and level-6 legs share; legs 2→3 share no rows (the dt = 1 grid steps
50 → 51). `horizon_scan.dat` is the same glue of the legs' live scans, kept for
the scan-based extractors; horizon NUMBERS still come from the mots replay
(`04_binary_headon/mots/`), which puts the common MOTS at t = 18.
The article's censorship figure and its clmGwCens* rows read these two files.
