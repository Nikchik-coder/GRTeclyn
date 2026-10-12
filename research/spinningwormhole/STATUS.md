# Spinning-wormhole campaign — status

One page, current only. Plan: [`SpinningWormhole.md`](SpinningWormhole.md).
Code: `Examples/SpinningWormhole/` + `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`.
Packed results: `results/spinningwormhole/`. Branch: `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| `spin_hold_L64_J025_t100` (Step 1's first spinning hold: the Step 0 drainhole at J = 0.25, `slowspin_eta2_m1_J025.spinbg`; no checkpoints) | node-3220ddd4 / GPU 0 (Step 0's card) | 24.3 at 08:19 (launched 06:58) | 100 | 18.0 u/h | 4.2 h, ~12:31 |
| `spin_hold_L64_ml3_J100_t100` (the O(J²) solver's fast end: the same drainhole at J = 1.0, v_e 0.24 c, J/M² 0.79, 12 % of extremal J/A; `slowspin_eta2_m1_J100.spinbg`, chosen by a t = 0 probe at J = 0.6/0.8/1.0: L2_Ham 2.07/2.06/2.04e-3 vs static 2.10e-3, L2_Mom linear in J; no checkpoints) | node-3220ddd4 / GPU 1 | 0.0 at 08:19 (launched 08:18) | 100 | 17.4 u/h | 5.7 h, ~14:03 |

At its close-out (decided 2026-10-12): rename `spin_hold_L64_J025_t100` to
`spin_hold_L64_ml3_J025_t100` and the Step 0 run to `static_hold_L64_ml3_t100`
(registry, pack, references); every new run name carries its level.

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| — | | | |

## STEP 1 INPUT: AZAD O(J²) CLOSED FORMS CHECKED (2026-10-12)

Exact symbolic check at C = 0 against all four O(J²) l = 0 equations (tt, rr,
ang, □Φ): the printed w, h0 and b0 are exact; the printed φ20 (eq. 2.7, the
4/π reading) is missing an overall factor φ — **φ20 = φ(r) × the printed
expression**, which → 0 at r → +∞ and is regular at the throat.  b0 cannot
be the faulty one: ang (−2r h0′ + 2r b0′ + 4 b0) fixes it given h0 up to
c/r²; φ20 enters rr alone.  `derive_phi20_correction.py` (spinning_wormhole
analysis scripts; 45 s, one core, every residual cancels to 0).

Generator: `backgrounds.py slowspin` solves the same O(J²) member directly in
the table's KK gauge (Chebyshev; writes `.spinbg`).  Validated: the full
R_ab + 2∂ψ∂ψ residuals fall as J⁴ (t-φ as J³) on the Step 0 drainhole
(η0 = 2, M = 1; `check_slowspin_einstein.py`); at γ = 0 with f(−∞) matched
to Azad's C = 0 member, its l = 0 f equals their exact 2h0 to 1e-14 and its
M their ΔM.  Drainhole at J = 0.25 / 0.5 / 1: J/M² = 0.25 / 0.47 / 0.79,
3 / 6 / 12 % of the extremal J/A; Einstein residual 3e-5 / 5e-4 / 1e-2.

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
- Trust window t_max = 64 (`results/spinningwormhole/trust_windows.tsv`):
  boundary return on the halved box (r = 32 out and back; speckle in the
  local_speed frames from t ~ 60).  Constraints stay ~3e-3 to t ~ 78 and the
  settled horizon R 2.4746 is unchanged to t = 100, but nothing after 64 is
  quoted; movies cut there.

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

1. ~~**Step 0 anchor**~~ DONE 2026-10-11: smoke PASS, and the static hold is a
   numerical twin of the merger's production `single_hold_t100` (same grid)
   over the full record — packed as `01_static_hold/static_hold_L64_t100`.
   One resolution was decided to suffice: the twin check is stronger than a
   three-resolution τ fit (the merger already owns the resolution ladder on
   this grid).
2. **Step 0 numerics** (optional hardening, none blocks Step 1): the
   Δt = 0.02 Δx cause; constraint norms on the finest levels;
   constraint-solved Π seeds; 1/R waveform extrapolation.
3. **Step 1 backgrounds** ← THE FRONT: the O(J²) slow-spin generator is in
   (`backgrounds.py slowspin`, same `.spinbg` format, validated above); next
   the first spinning hold at small J on the Step 0 grid, then decide
   solver-vs-Oldenburg-request for fast spin.

## RULES CARRIED OVER

Same launch discipline as the merger campaign: no GPU start-up before the go,
checkpoints are asked per run, full default frame set, STATUS updated and
pushed at every launch/stop/wipe, scratch checked with every run check.
