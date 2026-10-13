# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| `spin_hold_L64_ml3_ve050a_t100` | first GPU node / 0 | 47 | 100 | ~18 t/h | ~2.9 h, ~13:15 |
| `spin_hold_L64_ml3_J100_full_t100` | first GPU node / 1 | 1 | 100 | ~18 t/h | ~5.4 h, ~15:45 |

No checkpoints. `spin_hold_L64_ml3_ve070a_t100` (GPU 1, 07:49) DIED at
t = 42.36 at its far-side puncture (χ at the 1e-8 floor from t ≈ 4, then the
shift ran away); its throat never moved.  Closed out as
`04_fast_spin_hold/` (trust window 40) once its consumer drains.  The t = 0
checks are packed as `03_t0_checks/`; their scratch was wiped 08:00 (54 GB).

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| `static_hold_L64_ml3_sym_t100` | a GPU ~5.5 h; static table η0 2, M 0 (`backgrounds.py static`) | — | its go |
| `spin_hold_L64_ml3_ve024b_t100` | a GPU ~5.5 h; family (b) table at v_e 0.24, η0 2 (CPU, saved solution) | — | its go |
| `spin_hold_L64_ml3_ve043b_t100` | as above, v_e 0.43 | — | its go |
| `spin_hold_L64_ml3_ve067b_t100` | as above, v_e 0.67 | — | its go; the ve070a puncture death |
| `spin_hold_L64_ml3_ve085b_t100` | as above, v_e 0.85 | — | its go; the ve070a puncture death |

**Why a symmetric ladder** (decided 2026-10-13: the paper carries both
families). Azad et al. computed the second unstable mode, and its crossing
with the main one, only for C ≤ 0.2 (near-symmetric). For our drainhole
(C = 1) they give the main mode alone (τ ≈ 5.1 at η0 = 2). So the paper's
mode-merger test runs on family (b): spins at 10 / 20 / 33 / 50 % of the
limiting J/A, where 33 % is their predicted crossing (J/A ≈ 0.013) and 50 %
is where their O(J²) main mode reaches zero. The static Ellis anchor comes
first (their C = 0 rate gives τ ≈ 1.7 at η0 = 2). Same grid, gauge and
η0 1 → 2 rescale as the family (b) t = 0 ladder; no checkpoints unless asked.

## NOW: STEP 3, TEST THE FAST-SPIN TABLES

The question the solver was built for: **does fast spin fix the instability?**
The O(J²) holds could not tell (their push was the data's own J⁴ error); the
full tables are exact to ~1e-10.
1. **t = 0 checks: PASS** (07:03–07:50; `runs/spinning_wormhole/validation/`,
   `t0_checks.py`). v_e 0.5, 3 grids: constraints converge at 4th order
   inside the throat; outside they grow as 1/dx² (Ham) and 1/dx (Mom), the
   fingerprint of the tables' fixed ~2e-7 bilinear error, 10⁴× below the
   O(J²) holds' push; throat radii converge to the table (R_eq −5e-5 at
   N = 192). Family (b) to v_e 0.99: throat radii within 0.1 %, constraints
   at the static hold's level.
2. **The test** (live): holds at v_e 0.5 and 0.7 (family (a), the earlier
   holds' grid) to t = 100: collapse, inflation, or do they hold?
3. Then higher spin (a bigger box near 0.99), and the J = 1 hold on full data
   (does the push vanish?).

## DONE

- **Step 0** (2026-10-11): the static hold twins the merger's `single_hold`:
  collapse, τ 5.27, trust window t ≤ 64.
- **Step 1** (2026-10-12): the O(J²) holds at J = 0.25 / 1 inflate (τ 5.8 / 5.6);
  their push grew as J⁴, the data's error, not the spin.
- **Step 2** (2026-10-13): full solver, both families to v_e 0.99, every gate
  green; CKK's eq. (12) is wrong; tables in `runs/spinning_p3/tables/`
  (error ≤ 1e-7 to v_e 0.9).

## RULES

Merger launch discipline: go first, checkpoints asked per run, full frame set,
STATUS pushed at every launch/stop. Ψ4 radii in the box's wave zone (L = 64:
12 / 16 / 20, decided 2026-10-12).
