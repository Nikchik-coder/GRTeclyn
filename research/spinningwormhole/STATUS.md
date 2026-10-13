# Spinning-wormhole campaign — status

One page, current only. Plans: [`SpinningWormhole.md`](SpinningWormhole.md) (paper),
[`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/` +
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Packed: `results/spinningwormhole/`.
Branch `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| `t0conv_ve050a_L64_N096/N128/N192_ml3`, one after another | first GPU node / 0 | 0 | 1 | — | ~0.5 h, ~07:35 |
| `t0_ladder_ve050b/070b/090b/095b/099b_L64_ml3`, one after another | first GPU node / 1 | 0 | 1 | — | ~0.4 h, ~07:30 |

Started 07:03 UTC 2026-10-13, no checkpoints, under `runs/spinning_wormhole/validation/`.

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| `spin_hold_L64_ml3_ve050a_t100` | a GPU, ~5.5 h, no checkpoints | — | the v_e 0.5 check passing (go given) |
| `spin_hold_L64_ml3_J100_full_t100` | a GPU, ~5.5 h | — | its go |

## NOW: STEP 3, TEST THE FAST-SPIN TABLES

The question the solver was built for: **does fast spin fix the instability?**
The O(J²) holds could not tell (their push was the data's own J⁴ error); the
full tables are exact to ~1e-10.
1. **t = 0 checks** (live): at v_e 0.5 the constraints must fall with the grid
   (3 grids); up to v_e 0.99 the constraints and throat radii must match each
   table (family (b), rescaled to η0 = 2 to fit the box).
2. **The test**: a hold at v_e 0.5 (family (a), the earlier holds' grid) to
   t = 100: collapse, inflation, or does it hold?
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
