# NOISE-1: the head-on's leg 3 with three times the dissipation (2026-09-30)

One knob against leg 3 of the mode-3 head-on (`merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000`):
Kreiss–Oliger `sigma` 0.1 → 0.3, from the same checkpoint (leg 2's `Chk05000`, t = 50, max_level 4), to t = 80
(leg 3 ran to 100). `main3d_csmatch_5f988dbc`, the second GPU node, 13:27–17:40 UTC, 7.15 u/h, exit 0, no NaN, no
checkpoints. Question: what feeds the fine-scale noise that grows on leg 3's level-1 cube from t ≈ 65 (leg 3's
`VALIDATION.md`, "The level-1 noise")?

## The noise monitors, at the same times

In-code Ψ4, the symmetry-forbidden (3,2) mode at R = 20 (inside level 1), rms per window:

| t | 50–55 | 55–60 | 60–65 | 65–70 | 70–75 | 75–80 |
|---|---|---|---|---|---|---|
| leg 3 (σ = 0.1) | 1.3e-5 | 2.9e-5 | 3.3e-5 | 1.7e-4 | 3.1e-4 | 2.9e-4 |
| NOISE-1 (σ = 0.3) | 6.6e-6 | 7.6e-6 | 7.4e-6 | 1.4e-5 | 6.9e-6 | 1.0e-5 |
| (3,2)/(2,0), leg 3 | 0.08 % | 0.16 % | 0.33 % | 3.4 % | 2.6 % | 2.5 % |
| (3,2)/(2,0), NOISE-1 | 0.04 % | 0.04 % | 0.07 % | 0.29 % | 0.06 % | 0.09 % |

The other forbidden mode, (2,1) at R = 20, over t = 75–80: 1.2e-5 against 1.3e-7.

Fine-scale part of K (field minus its 1-unit Gaussian smooth) in the ring r = 16–19.5 of the z-slice, and the
level-0 L2 H the run logs:

| t | 60 | 65 | 70 | 75 | 80 |
|---|---|---|---|---|---|
| K ring, leg 3 (1e-5) | 1.0 | 1.8 | 3.5 | 6.7 | 10.4 |
| K ring, NOISE-1 (1e-5) | 0.59 | 0.42 | 0.43 | 0.98 | 0.75 |
| L2 H, leg 3 (1e-4) | 1.16 | 1.11 | 1.10 | 1.16 | 1.37 |
| L2 H, NOISE-1 (1e-4) | 1.16 | 1.10 | 1.06 | 1.03 | 1.01 |

NOISE-1's ring stays at leg 3's pre-noise floor (0.8–1.5e-5 over t = 25–60); what it has is the smooth field's
leak through the filter (half of it survives a 0.5-unit filter, against 97–99 % of leg 3's), and its finest-scale
part (0.25-unit filter) holds at 1.5–2.6e-6 over t = 60–72. Weyl4_Re in the same ring at t = 80: 6.9e-6 against
9.2e-5. L2 M agrees to 0.6 % throughout.

## The constraint rebuilt from the plotfiles

The metric-only Hamiltonian constraint (fourth-order stencils, leg 3's `ham_level_map.py`), on NOISE-1's last
plotfiles. On level 1 (the cube ±20), rms by distance from the cube's centre (Chebyshev radius):

| Chebyshev radius | 10–12 | 12–14 | 14–16 | 16–18 | 18–19 |
|---|---|---|---|---|---|
| NOISE-1, t = 74 | 6.2e-5 | 6.3e-5 | 4.3e-5 | 2.1e-5 | 3.0e-5 |
| NOISE-1, t = 80 | 6.3e-5 | 6.9e-5 | 4.3e-5 | 2.2e-5 | 3.3e-5 |
| leg 3, t = 100 | 5.0e-3 | 7.7e-3 | 1.0e-2 | 1.2e-2 | 1.2e-2 |

Flat over t = 74–80, and falling toward the cube's faces where leg 3's noise peaks. Level 2 (±10) at t = 80:
0.9–1.6e-4 (leg 3 at t = 100: 0.9–1.2e-3). On level 0 at t = 80 the rebuilt L2 is 7.5e-5 (logged 1.01e-4); 1.0 % of
its sum of squares lies at r = 16–32 (leg 3 at t = 100: 94 %), 34 % in the eight cells next to the puncture and 59 %
in the box corners beyond r = 64. No plotfile of leg 3 at t ≤ 80 is left, so the rebuilds compare against leg 3's
end.

## The physics does not move

- The allowed modes on level 0: (2,0) and (2,2) at R = 36 and 44 agree with leg 3's to within 1 % of their maximum
  over t = 50–80. Inside R ≤ 28 they differ by up to 7 % ((2,0) at R = 18–20), the size of leg 3's own contamination
  there; the cube's harmonics (4,0), (4,±4) at R = 14–28 differ by 11–40 %.
- The remnant: the round scan's MOTS at t = 80 has R 4.646 and M_MS 2.3745 in both runs (4.701 / 2.3860 at t = 75
  in both); K's fine-scale part at r = 4–8 agrees to 0.3 %.

## What it means

The level-1 noise is under-dissipation. At σ = 0.1 grid-scale structure on the level-1 cube grows (e-fold ~8 units
in the K ring from t ≈ 62) until it is the whole field; at σ = 0.3 it stays at the floor, with the waves on the clean
spheres and the remnant unchanged. The live spiral and fly-by run σ = 0.1 on the same level-1 cubes.

## How

Scripts and logs are in the run's `validation/` folder in the run tree (`08_convergence/<run>/validation/`):
`noise1_vs_leg3.py` (modes, norms, slice rings, remnant; `noise1_vs_leg3_final.log`), `noise1_scales.py` (the
two-filter test), `ham_level_map.py` and `ham_level1.py` (leg 3's rebuild; `ham_level1_t075.log`,
`ham_level1_t078_t080.log`, `ham_level0_map_t080.log`). The plotfiles were wiped after the rebuild (17:48 UTC).
