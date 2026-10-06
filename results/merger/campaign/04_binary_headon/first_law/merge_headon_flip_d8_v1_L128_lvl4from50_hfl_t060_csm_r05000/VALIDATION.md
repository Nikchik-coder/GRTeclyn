# HFL-ho: the head-on horizon's first law over t = 51–60 (2026-10-01)

`merge_headon_flip_d8_v1_L128_lvl4from50_hfl_t060_csm_r05000`: leg 3 of the mode-3 head-on
(`04_binary_headon/csm/merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000`) again from leg 2's
`Chk05000` (t = 50, max_level 4). Only stop_time (100 → 60) and the name changed; same binary
(`main3d_csmatch_5f988dbc`). Every plotfile was kept (t = 51–60 and 60.01). Second node, 05:25–06:50 UTC, 7.2 u/h.

## 1. It is leg 3

It reached t = 60.01 (exit 0, no NaN). Every stream is bit-identical to leg 3's at the same times (max |difference|
= 0):
- in the run: the 21 in-code Ψ4 modes, `constraint_norms`, `collapse_diagnostics`, `binary_throat_diagnostics`
  and `throat_track` (1000 rows, t = 50.01–60.00);
- in the consumer: `horizon_scan`, `areal_radius`, `boundary_flux`, `scalar_modes` and `psi4_*` (t = 51–59).

Its plotfiles are therefore leg 3's at t = 51–60.

## 2. Method (`grteclyn-wrapper/scripts/analysis/merger_feedback/headon_first_law.py`)

- **The surface.** The common MOTS r = h(θ, φ) about the centre, in real Y_lm to ℓ = 6.
  - Found by the spectral flow finder (`ah_flow_finder.py`; no star-shaped assumption).
  - Refined by Newton until every projected θ_out harmonic is below 1e-6.
  - Each plotfile starts from the previous plotfile's surface.
- **Measured.** R = √(A/4π) from the surface's area, M_MS = R/2, and dR/dt by differences between plotfiles.
- **Predicted, from each slice alone.** The spherical first law of a phantom on a marginally trapped tube
  (`c_spherical_horizon_law.py`), with averages over the found surface:
  - dR/dt = 2πR³⟨α f θ_in⟩/(1 + q), where q = 4πR²⟨f⟩ and f = (Π + s·∇φ)².
  - "pred phantom" is this rate. A phantom's influx can only shrink the horizon.
  - "pred +shear" adds the Raychaudhuri shear of the outgoing null normal, f → f − |σ|²/(8π). The shear can only
    grow the horizon.
  - The law is exact in spherical symmetry; on this surface (3–10 % out of round) the averages are an
    approximation.
- **Self-test** (`--selftest`): Kerr–Schild Schwarzschild and a flat c/a = 1.15 spheroid
  (`validation/first_law_selftest.log` in the run tree).
- **Grids.**
  - Covering grids over ±4.5 about the centre, at level 3 (Δx 0.0625) and level 2 (Δx 0.125).
  - Level 4 covers only ±2.5, which lies inside the horizon (r = 3.0–3.4), so it cannot read it. The covering grid
    would fill the rest with injected coarse cells; the script refuses such a box since 3ebfad99.

## 3. Level 3, ℓ ≤ 6

```
    t      R_mots    M_MS    h_x    h_y    h_z   rms_th_out   alpha     <f>        <sig2>     dR/dt meas   pred phantom   pred +shear
   51.00  4.77764  2.38882  3.341  3.025  3.025  1.59e-04  0.3786  2.296e-05  2.185e-04  -1.410e-03    -1.997e-03     -1.310e-03
   52.00  4.77623  2.38812  3.338  3.038  3.038  1.08e-04  0.3773  1.933e-05  2.273e-04  -1.240e-03    -1.670e-03     -9.562e-04
   53.00  4.77516  2.38758  3.331  3.052  3.052  4.37e-05  0.3762  1.569e-05  2.243e-04  -9.188e-04    -1.345e-03     -6.417e-04
   54.00  4.77439  2.38719  3.322  3.068  3.068  1.74e-05  0.3752  1.225e-05  2.106e-04  -6.444e-04    -1.040e-03     -3.796e-04
   55.00  4.77387  2.38693  3.311  3.084  3.084  5.22e-05  0.3745  9.130e-06  1.885e-04  -4.209e-04    -7.674e-04     -1.764e-04
   56.00  4.77355  2.38677  3.299  3.100  3.100  6.44e-05  0.3739  6.442e-06  1.606e-04  -2.374e-04    -5.360e-04     -3.192e-05
   57.00  4.77340  2.38670  3.287  3.117  3.117  5.09e-05  0.3734  4.239e-06  1.297e-04  -9.086e-05    -3.493e-04     +5.867e-05
   58.00  4.77337  2.38668  3.274  3.135  3.135  2.32e-05  0.3730  2.536e-06  9.853e-05  +1.195e-05    -2.071e-04     +1.036e-04
   59.00  4.77342  2.38671  3.263  3.152  3.152  9.23e-06  0.3728  1.318e-06  6.943e-05  +8.167e-05    -1.068e-04     +1.128e-04
   60.00  4.77353  2.38677  3.252  3.168  3.168  2.32e-05  0.3726  5.466e-07  4.426e-05  +1.118e-04    -4.409e-05     +9.644e-05

  over t = 51.00-60.00: R measured -0.00411; predicted by the phantom -0.00704, with the shear -0.00252  (M = R/2: halve these)
```

## 4. Level 2, ℓ ≤ 6

```
    t      R_mots    M_MS    h_x    h_y    h_z   rms_th_out   alpha     <f>        <sig2>     dR/dt meas   pred phantom   pred +shear
   51.00  4.77733  2.38867  3.342  3.025  3.025  1.95e-04  0.3786  2.297e-05  2.184e-04  -1.412e-03    -1.997e-03     -1.310e-03
   52.00  4.77592  2.38797  3.338  3.038  3.038  1.42e-04  0.3773  1.933e-05  2.273e-04  -1.244e-03    -1.670e-03     -9.562e-04
   53.00  4.77484  2.38743  3.332  3.053  3.053  7.26e-05  0.3762  1.570e-05  2.244e-04  -9.278e-04    -1.345e-03     -6.416e-04
   54.00  4.77406  2.38704  3.322  3.068  3.068  2.40e-05  0.3752  1.225e-05  2.108e-04  -6.508e-04    -1.040e-03     -3.796e-04
   55.00  4.77354  2.38678  3.311  3.084  3.084  4.32e-05  0.3745  9.137e-06  1.887e-04  -4.104e-04    -7.679e-04     -1.763e-04
   56.00  4.77324  2.38662  3.299  3.101  3.101  5.72e-05  0.3739  6.449e-06  1.607e-04  -2.200e-04    -5.365e-04     -3.202e-05
   57.00  4.77310  2.38655  3.287  3.118  3.118  4.87e-05  0.3734  4.245e-06  1.298e-04  -8.239e-05    -3.497e-04     +5.845e-05
   58.00  4.77308  2.38654  3.275  3.135  3.135  2.94e-05  0.3730  2.541e-06  9.854e-05  +2.441e-05    -2.075e-04     +1.033e-04
   59.00  4.77315  2.38657  3.263  3.152  3.152  2.07e-05  0.3728  1.321e-06  6.940e-05  +9.957e-05    -1.071e-04     +1.124e-04
   60.00  4.77328  2.38664  3.253  3.169  3.169  2.78e-05  0.3726  5.488e-07  4.419e-05  +1.266e-04    -4.426e-05     +9.604e-05

  over t = 51.00-60.00: R measured -0.00405; predicted by the phantom -0.00704, with the shear -0.00252  (M = R/2: halve these)
```

Level 2's R sits 3e-4 below level 3's throughout; the rates agree to a few %. ℓ ≤ 8 at t = 51–52 gives the same
rates as ℓ ≤ 6.

## 5. Reading

- **The horizon is steady.** R shrinks by 0.09 % over t = 51–58 (4.7776 → 4.7734) and regrows by 0.003 % to t = 60.
  Meanwhile the surface rounds: its x and y = z axes go from 3.341 / 3.025 to 3.252 / 3.168, prolate along the
  collision axis.
- **The measured change lies between the two predictions**, at both levels. Over t = 51–60:
  - measured ΔR = −0.00411 (level 2: −0.00405);
  - the phantom's influx alone predicts −0.00704;
  - influx plus shear predicts −0.00252.
- **Closing the budget takes about 65 % of the shear term.**
- **The turn to growth at t = 58 comes from the shear.** The flux-plus-shear rate turns positive at t = 57 and
  matches the measured rate at t = 59–60 (+1.13 / +0.96e-4 against +0.82 / +1.12e-4). The phantom-only rate never
  turns positive.
- **Both influxes fade over the window.** The scalar flux through the horizon falls 42× (⟨f⟩ 2.3e-5 → 5.5e-7); the
  shear falls 5× (⟨σ²⟩ 2.2e-4 → 4.4e-5).

## 6. The round scan against the MOTS

The consumer's round scan (`horizon_scan.dat`, centre C) reads the horizon growing over the same units:

```
     t      R_scan   M_MS_scan
   51.00   4.2469   2.3000
   52.00   4.2727   2.3058
   53.00   4.3031   2.3124
   54.00   4.3372   2.3196
   55.00   4.3747   2.3269
   56.00   4.4143   2.3344
   57.00   4.4553   2.3417
   58.00   4.4970   2.3489
   59.00   4.5386   2.3557
   60.00   4.5795   2.3620
```

- The scan's R rises from 4.247 to 4.580 (+7.8 %) and its M_MS from 2.300 to 2.362, while the MOTS moves by −0.09 %.
- The rise is the scan's own: the outermost fully trapped round sphere sits inside the deformed MOTS and climbs as
  the surface rounds.
- The oriented scan (`ah_oriented_scan.py`, level 3, half 4.0, as on leg 3's last slices; `ah_oriented_scan_t055.dat`, `ah_oriented_scan_t060.dat`) under-reads too: R 4.421 at t = 55 against the MOTS's 4.7739 (−7.4 %), 4.622 at t = 60 against 4.7735 (−3.2 %).
- So over t = 51–60 the head-on's horizon does not grow, as the spherical law says of the phantom; the small late
  regrowth is the shear's.

## 7. Files

- `first_law_L3.json` and `first_law_L2.json` hold one entry per plotfile: R, area, M_MS, axes, expansions,
  flux, shear, q, the three rates, and the surface's a_lm.
- The plotfiles stay on the second node's scratch, on the user's word (2026-10-01).
- To re-run:
  `OMP_NUM_THREADS=8 nice -n 19 grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/headon_first_law.py --json OUT.json --level 3 --lmax 6 PLT ...`
