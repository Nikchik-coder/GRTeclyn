# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| `spin_hold_L64_ml3_ve050a_t100` | first GPU node / 0 | 68 | 100 | ~18 t/h | ~1.8 h, ~13:15 |
| `spin_hold_L64_ml3_J100_full_t100` | first GPU node / 1 | 21 | 100 | ~18 t/h | ~4.3 h, ~15:45 |

No checkpoints. `spin_hold_L64_ml3_ve070a_t100` (GPU 1, 07:49) DIED at
t = 42.36 at its far-side puncture (χ at the 1e-8 floor from t ≈ 4, then the
shift ran away); its throat never moved.  Closed out 11:30: packed as
`04_fast_spin_hold/` (trust window 40, no movies), scratch pruned (7 GB).
The t = 0 checks are packed as `03_t0_checks/`; their scratch was wiped
08:00 (54 GB).

## QUEUED

**Order (decided 2026-10-13): the symmetric family first, then the drainhole.**
The symmetric family is the one Kleihaus–Kunz and CKK published and Azad et al.
analysed in full, so it validates the 3D pipeline against published values before
the drainhole, which has no published fast-spin data, is taken to high spin. The
two live drainhole holds finish as they are.

*Phase A: symmetric, family (b) at η0 2*

| run | needs | restart from | waiting on |
|---|---|---|---|
| A1 t = 0 validation at v_e 0.24 / 0.43 / 0.67 / 0.85 / 0.9 / 0.95 / 0.99, N 64/96/128 | GPU minutes each; ADM M, J extraction (to add; `t0_checks.py` has the throat radii) | — | its go |
| A2 `static_hold_L64_ml3_sym_t100` ×3 (N 64/96/128) | ~7.6 GPU-h; static table η0 2, M 0 (`backgrounds.py static`) | — | A1, its go |
| A3 `spin_hold_L64_ml3_ve024b_t100` ×3 | ~7.6 GPU-h; family (b) table at v_e 0.24, η0 2 (CPU, saved solution) | — | A2, its go |
| A3 `spin_hold_L64_ml3_ve043b_t100` ×3 | as above, v_e 0.43 | — | A2, its go |
| A3 `spin_hold_L64_ml3_ve067b_t100` ×3 | as above, v_e 0.67 | — | A2, its go; the ve070a puncture death |
| A3 `spin_hold_L64_ml3_ve085b_t100` ×3 | as above, v_e 0.85 | — | A2, its go; the ve070a puncture death |
| A4 `spin_hold_L64_ml3_ve090b/095b/099b_t100` ×3 | tables exist (`tables_eta2/`); a bigger box near 0.99 | — | A3, its go |

- **A1, what it validates:** the Kleihaus–Kunz 2014 Fig. 1 quantities (M/M0,
  J/J0, R_p/R, R_A/R, ΩJ), read off the 3D grid at t = 0 and compared with the
  table and the digitized KK curves, converging across N.
- **A2:** the static Ellis growth against Azad et al.'s C = 0 rate (τ ≈ 1.7 at
  η0 = 2).
- **A3:** their two modes and the crossing.
- **A4:** beyond any published stability result.

*Phase B: drainhole, family (a), after Phase A*

| run | needs | restart from | waiting on |
|---|---|---|---|
| B1 N 64 / 96 partners of `static_hold_L64_ml3_t100`, `spin_hold_L64_ml3_ve050a_t100`, `spin_hold_L64_ml3_J100_full_t100` | ~2.1 GPU-h each pair | — | Phase A, its go |
| B2 `spin_hold_L64_ml3_ve070a_t100` again ×3 | the far-side puncture fix | — | Phase A, the fix, its go |
| B3 higher spin ×3 (v_e 0.9 / 0.95 / 0.99) | tables exist; a bigger box near 0.99 | — | B2, its go |

**Every quoted run is a triplet** (decided 2026-10-13; the stability protocol in
`SpinningWormhole.md`, after Evstafyeva, Siemonsen & East, arXiv:2508.11527):
L64 ml3 at N = 64 / 96 / 128 (finest Δx 0.125 / 0.083 / 0.0625). A growth is
physical only if its τ converges to a nonzero value, the finest-level constraints
converge while it grows, and the throat's areal radii or MOTS grow with it.
N 64 / 96 costs are N⁴ estimates from the measured ~5.5 h at N = 128.

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
   0.7: died at the far side (above), throat frozen.  0.5 (t = 67): the
   throat shrinks (R_eq −0.6 %, MOTS R −0.8 %), the static hold's sign, but
   slower than exponential since t ≈ 50 (e-fold time 5 → 14; the static's
   stays ≈ 5); constraints flat, Mom +30 % since t = 60.
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
