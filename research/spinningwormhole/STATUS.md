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
| smoke_test (params_test.txt, static background) | first pinned binary | — | the go |

## STATE (2026-10-10)

- Campaign scaffold landed on `feature/spinning`: clean example (background-table
  initial data, Γ̃ FD fill, throat/ergoregion diagnostics), static `.spinbg`
  generator (exact under the loader's interpolation), legacy
  `RotatingWormholeCollapse` deleted.
- Campaign scripts (`spinning_wormhole/`, launch → run_single → shared
  `campaigns/lib/preflight.py` + consumer): in progress this session.
- No pinned binary yet (`launch.sh` requires `--binary` until the first
  `build_binary.sh --tag` lands and sets the pin).

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
