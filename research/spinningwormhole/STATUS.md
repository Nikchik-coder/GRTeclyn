# Spinning-wormhole campaign — status

One page, current only. Plan: [`SpinningWormhole.md`](SpinningWormhole.md).
Code: `Examples/SpinningWormhole/` + `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`.
Packed results: `results/spinningwormhole/`. Branch: `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| static_hold_L64_t100 | first node / GPU 0 | 0.5 (17:40) | 100 | 18.3 u/h | ~5.5 h → ≈23:10 UTC 10 Oct |

static_hold_L64_t100 (launched 17:35 UTC 2026-10-10, no checkpoints — decided
at launch): the Step 0 anchor, ONE resolution first.  L = 64, N = 128
(dx0 = 0.5, the merger hold's), max_level 3 with the merger hold's exact
nested boxes (tagging_L = 64 → ±16/±8/±4), its dt 0.02 Δx, sigma 0.1 and gauge
numbers; background `static_eta2_m1.spinbg` (a = 2, M = 1); profile hold.
**t = 0 is bit-identical to the merger hold's collapse_diagnostics row**
(min_lapse 2.1942989020e-01, min_chi 4.1085936805e-07, min/max_phi equal to
all printed digits); L2_Mom(0) = 0; L2_Ham is √8× the merger's, the halved
box's volume norm.  Target: reproduce the growth rate (merger hold: τ ≈ 5.12).

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| — | | | |

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
