# Spinning-wormhole campaign — status

One page, current only. Plan: [`SpinningWormhole.md`](SpinningWormhole.md).
Code: `Examples/SpinningWormhole/` + `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`.
Packed results: `results/spinningwormhole/`. Branch: `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| — | | | | | |

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| — | | | |

## STEP 0 ANCHOR: PASS (2026-10-11)

`static_hold_L64_t100` (L = 64, N = 128, ml3 = the merger hold's grid on a
halved box; a = 2, M = 1 table; no checkpoints; GPU 0, 5.6 h): reached
t = 100 clean, 0 NaN.
- **Trajectory-identical to the merger `single_hold`**: t = 0 bit-identical;
  over the whole packed overlap (t ≤ 41.3) max rel diff 5e-5 in min_lapse and
  max|K|, median 0 — the table-driven pipeline IS the merger drainhole.
- **Collapse as expected (GGS mode)**: throat R 3.89 → 1.99;
  τ(δR ∈ [0.01, 0.3], t = 38–56) = **5.27** vs the paper's 5.12 (the fit is
  window-sensitive at the ±0.2 level; MOTS-R gives 5.5).
- **Horizon forms**: spectral MOTS on 101/101 plotfiles; at t = 0 it is the
  throat (R 3.886, M_MS 1.943), by t = 100 it detaches (R_MOTS 2.47 outside
  the throat's 1.99, θ_in = −0.61) and its area SHRINKS — the phantom flux
  term of the first-law columns, as in the merger paper.
- Trust window t_max = 80 (`results/spinningwormhole/trust_windows.tsv`):
  constraints clean (L2_Ham ~ 3e-3) and the horizon settled by t = 80; after
  it the collapsed puncture region grows grid-scale noise (L2_Ham 0.13 at
  t = 100, the speckled late frames).  Boundary return on the halved box is
  t ~ 64 and left no visible mark before that.

## SMOKE: PASS (2026-10-10)

Smoke runs live under `runs/spinning_wormhole/smoke/` (moved 2026-10-10 so the
campaign root holds production runs only; launch.sh now routes the smoke and
none profiles there, `--subdir` overrides).

`smoke_test3` (static massless table, L = 16, N = 64, t → 0.5, GPU 0, ~1 min):
clean exit, 0 NaN, L2_Mom(t=0) = 0 exactly, 14 frames through the throat,
consumer 3/3 plotfiles + keep-last 3, R_eq 0.97 / R_pol 0.92 / ergo_min 1 at
t = 0.  Scratch: clean — smoke_test/smoke_test2 plotfiles pruned
(manifests/MANIFEST_CLEANUP_2026-10-10.md), 79M used, 1.0T free.
Three faults found and fixed on the way (commit bfb65e8e + the coord guard):
exit-time managed-arena free, near-puncture R_pol contamination, psi4 radii
vs tiny box; plus a new shared-preflight refusal for a slice coordinate
outside the box (the featureless-frames trap).

## STATE (2026-10-10)

- Campaign scaffold landed on `feature/spinning`: clean example (background-table
  initial data, Γ̃ FD fill, throat/ergoregion diagnostics), static `.spinbg`
  generator (exact under the loader's interpolation), legacy
  `RotatingWormholeCollapse` deleted.
- Campaign scripts landed: `spinning_wormhole/` (launch → run_single →
  consumer) on the NEW shared preflight engine `campaigns/lib/preflight.py`
  (per-campaign facts in `preflight_campaign.json`; the merger keeps its
  frozen copy).  Dry-run against the built binary + static table: PASS,
  59/59 template keys read.
- Campaign pin: `main3d_smoke_bfb65e8e_2026-10-10.ex` (launch.sh
  DEFAULT_BINARY; binaries.tsv row 2 — row 1 `main3d_first_cf8cca48` had the
  exit-time crash and is superseded).

## NEXT (the plan's order)

1. **Step 0 anchor**: smoke test, then the static hold — the massless static
   table must reproduce the merger drainhole's t = 0 constraint norms and the
   binary paper's growth rate (τ ≈ 5.12) at three resolutions.
2. **Step 0 numerics**: the Δt = 0.02 Δx cause; constraint norms on the finest
   levels; constraint-solved Π seeds; 1/R waveform extrapolation.
3. **Step 1 backgrounds**: O(J²) slow-spin generator (Azad et al.) into the
   same `.spinbg` format; decide solver-vs-Oldenburg-request for fast spin.

## RULES CARRIED OVER

Same launch discipline as the merger campaign: no GPU start-up before the go,
checkpoints are asked per run, full default frame set, STATUS updated and
pushed at every launch/stop/wipe, scratch checked with every run check.
