# The mode-3 production head-on, validated as one chain (2026-09-30)

Three legs, one evolution (d = 8, p = 0, flipped, far-side-matched data, L = 128, N = 256):

| t | leg | max level | end |
|---|---|---|---|
| 0–35 | `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm` | 5 | NaN at t = 38.845 (merged core, inside the MOTS) |
| 35–50 | `merge_headon_flip_d8_v1_L128_lvl6from35_scalar_chk_t100_csm_r03500` | 6 | stopped by hand at t = 50.80, no NaN |
| 50–100 | `merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000` | 4 | t = 100, exit 0, no NaN |

## Seams

| seam | level-0 L2 H (new / old leg) | in-code Ψ4 on the overlap | common MOTS |
|---|---|---|---|
| t = 35 | 0.986 at t = 35.01; the level-6 leg then falls to 0.45 of the level-5 leg by t = 38.8 (the norm is core-dominated there) | identical to t = 38.84 on R = 18–36 (difference 0), 1e-11 at R = 10 | not found by the round scan at t = 26–35; at t = 36–38 both legs find it (R 4.52 and 4.49 at t = 38) |
| t = 50 | 1.000–1.001 over t = 50.01–50.8 | identical on every sphere (difference 0) | R 4.266 → 4.247, M_MS 2.296 → 2.300 (t = 50 → 51) |

Across each restart the (2,0) and (2,2) modes step by no more than one ordinary time step's change.

## Constraints (level-0 norm, the only one the run logs)

| t | 0 | 10 | 20 | 22.4 | 25 | 35 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L2 H (1e-4) | 11.9 | 13.8 | 18.9 | 27.2 (max) | 5.6 | 4.3 | 1.7 | 1.4 | 1.2 | 1.1 | 1.4 | 3.3 | 12.1 |
| L2 M (1e-4) | 0 | 0.19 | 4.6 | | 10.9 | 6.9 | 3.6 | 4.2 | 3.9 | 4.0 | 3.9 | 4.1 | 5.9 |

The rise after t = 75 (e-fold 5–6 units in the excess over the t = 65–75 floor) is not at the core and not at
the outer boundary. The Hamiltonian constraint rebuilt from the plotfile's metric on level 0 (total 1.01e-3 /
1.35e-3 at t = 98 / 100; logged 0.91e-3 / 1.21e-3) has 93–94 % of its sum of squares at r = 16–32, 0.1–0.2 %
inside r = 6 and under 0.5 % beyond r = 32. That shell is the outer part of the level-1 refinement cube
(|x|, |y|, |z| < 20). On level 1 itself the rebuilt constraint is rms 5e-3 (10–12 from the centre, Chebyshev)
to 1.2e-2 (within 2 of the cube's faces) at t = 100, ×1.33 on t = 98; on level 2 (cube ±10) it is 5–9e-4.
At t = 38 the same rebuild gives 1.0e-5 outside r = 6.

## The level-1 noise

Fine-scale structure (field minus its 1-unit Gaussian smooth) in rings of the z = 64 slice, K:

| t | 25–60 | 65 | 70 | 75 | 80 | 85 | 90 | 95 | 100 |
|---|---|---|---|---|---|---|---|---|---|
| r = 16–19.5 (1e-5) | 0.8–1.5 | 1.8 | 3.5 | 6.6 | 10 | 19 | 33 | 59 | 96 |
| r = 12–16 (1e-5) | 1.2–2.8 | 2.1 | 3.8 | 5.9 | 8.9 | 15 | 26 | 41 | 57 |
| the ring's whole K, r = 16–19.5 (1e-5) | 16–144 | 26 | 18 | 8.9 | 11 | 20 | 35 | 59 | 97 |

It doubles every ~6 units from t ≈ 65 and is the whole field in the outer ring from t ≈ 80. The
symmetry-forbidden (3,2) mode of the in-code Ψ4 has grown steadily since the merger (R = 20: 2e-6 at
t = 20–25, 1.3e-5 at 50–55, 1.7e-4 at 65–70, 4.0e-3 at 95–100), with no step at either restart.

In-code Ψ4, (3,2) over (2,0), rms per window:

| sphere | grid | t = 65–80 | 80–85 | 85–90 | 90–95 | 95–100 |
|---|---|---|---|---|---|---|
| R = 20 | inside level 1 | 3 % | 8 % | 31 % | 20 % | 59 % |
| R = 28 | cuts the level-1 cube's corners | < 1 % | 1 % | 3 % | 8 % | 7 % (and l = 4, m = 0, ±4 as large as (2,0) from t = 90) |
| R = 36 | level 0 | < 1 % | 1 % | 1 % | 1 % | 1 % |
| R = 44 | level 0 | < 1 % | < 1 % | 1 % | 3 % | 3 % |

## Waves

Signed swings of Re r Ψ4 (2,0), in-code; the paper's superposed run at R = 10: +0.023 at 28.2, −0.018 at 43.8,
+0.011 at 63.4, −0.006 at 82.2.

| sphere | A | B | C | D |
|---|---|---|---|---|
| R = 10 | +0.0240 at 28.8 | −0.0207 at 44.2 | +0.0126 at 63.0 | −0.0066 at 81.7 |
| R = 14 | +0.0212 at 33.0 | −0.0202 at 48.9 | +0.0129 at 67.9 | −0.0070 at 87.1 |
| R = 20 | +0.0189 at 39.8 | −0.0196 at 56.0 | +0.0131 at 75.1 | −0.0077 at 93.6 |
| R = 36 | +0.0163 at 57.9 | −0.0187 at 74.2 | +0.0133 at 93.0 | |
| R = 44 | +0.0158 at 66.7 | −0.0185 at 83.3 | (+0.0123 at 99.5, at the end of the record) | |

Swing B falls 10 % in r Ψ4 from R = 10 to 44 and travels at 0.86 (R = 10–20), 0.87 (20–36), 0.91 (36–44).
Im/Re of the (2,0) mode is 1e-4–1e-3. The consumer's python Ψ4 (2,0) against the in-code one: amplitude ratio
0.96 / 0.99 / 1.00 and zero phase at R = 20 / 14 / 44 (residual 17 % / 8 % / 1.3 %).

Scalar channel (consumer): the l = 1, m = ±1 mode carries it (0.62 at R = 10 and 0.14 at R = 44 at t = 0,
falling as 1/r); at R = 10 it drops to 0.047 by t = 30 and rings down (0.30, 0.16, 0.076, 0.11, 0.021, 0.040,
0.024 at t = 40 … 100).

## Horizon

Round scan about the box centre (consumer, one row per unit): first MOTS at t = 22 (r 2.53, R 5.02,
M_MS 2.69), found t = 22–25, not found t = 26–35 (the round scan loses the deformed surface), found every unit
t = 36–100.

| t | 22 | 25 | 38 | 40 | 45 | 48 | 50 | 51 | 55 | 60 | 65 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R | 5.02 | 4.57 | 4.49 | 4.55 | 4.29 | 4.25 | 4.27 | 4.25 | 4.37 | 4.58 | 4.68 | 4.61 | 4.65 | 4.58 | 4.65 |
| M_MS | 2.69 | 2.84 | 2.41 | 2.37 | 2.30 | 2.29 | 2.30 | 2.30 | 2.33 | 2.36 | 2.39 | 2.39 | 2.37 | 2.37 | 2.37 |

Oriented scan (`ah_oriented_scan.py`, level 3, half 4.0) on the last three plotfiles (`ah_oriented_scan_t098/099/100.dat`):
every shell r = 0.25–3.37 trapped, the outermost MOTS at r = 3.377, R = 4.688, M_MS = 2.373 at t = 100.
The pair's ADM mass is 2.357 (volume identity, leg 1's `constraint_solve.dat`).

## How

Scripts and logs: the run's `validation/` folder in the run tree (the constraint rebuild `ham_level_map.py`,
`ham_level1.py`; `headon_waves.py`; `slice_noise.py`). The rebuild uses the metric alone (fourth-order stencils);
the code's own constraint uses the evolved Γ̃ⁱ, which the plotfiles do not hold.
