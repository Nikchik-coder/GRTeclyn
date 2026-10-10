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
| static hold (Step 0 anchor: τ ≈ 5.12 at three resolutions) | run plan (L, N, levels) | — | the go |

## SMOKE: PASS (2026-10-10)

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
