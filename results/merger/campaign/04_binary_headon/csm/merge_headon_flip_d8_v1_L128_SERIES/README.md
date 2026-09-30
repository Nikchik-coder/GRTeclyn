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
The (2,0) mode is the head-on's dominant channel.

## Reading it — the level-1 noise gates

Fine-scale numerical noise grows on the level-1 refinement cube from t ≈ 65
(doubling every ~6 units; leg 3's `VALIDATION.md`, "The level-1 noise"), so a
sphere inside the cube (R ≤ 20) is clean to t ≈ 80, R = 28 (which cuts the
cube's corners) to t ≈ 90, and R = 36/44 (level 0) to t = 100. Read the
symmetry-forbidden (3,2) mode as the monitor. The figures'
`plot_psi4_gallery.DRAW_GATES` carry exactly these cuts.
