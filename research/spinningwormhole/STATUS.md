# Spinning-wormhole campaign — status

One page, current only. Plan: [`SpinningWormhole.md`](SpinningWormhole.md).
Code: `Examples/SpinningWormhole/` + `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`.
Packed results: `results/spinningwormhole/`. Branch: `feature/spinning` (pushes to `myfork`).

## LIVE

| run | node/card | t | stop | speed | ETA (h, UTC) |
|---|---|---|---|---|---|
| — | | | | | |

Both GPUs of node-3220ddd4 are free since 13:49 (the two J holds finished).
Every run name carries its level (decided 2026-10-12): `spin_hold_L64_J025_t100`
and `static_hold_L64_t100` were renamed at close-out to
`spin_hold_L64_ml3_J025_t100` and `static_hold_L64_ml3_t100` (registry, pack,
references; their run dirs keep the old name as a symlink).

## QUEUED

| run | needs | restart from | waiting on |
|---|---|---|---|
| — | | | |

## STEP 2 STARTED: THE FULL SOLVER, M1 PASSED (2026-10-12)

`SpinningSolver.md` P0-P2 are done on `feature/spinning` (pure CPU, the
wrapper venv + jax; no GPU use):
- **The published CKK eq. (12) is wrong**: extremal Kerr (a = M, eta0 = 0,
  closed form, fits their ansatz exactly) satisfies eqs. (10), (11), (13),
  (19) exactly and leaves ~1e-2 in the printed (12).  Solutions of the
  printed elliptic system violate the constraints at J^4 at EVERY
  resolution; the solver instead takes N and D^2 jointly from the
  constraints (13)+(19) (linear least squares), and
  `derive_xy_equations.py --stage kerr` pins the finding as a regression
  check.  The Oldenburg email (plan section 11) now asks about an erratum.
- **First full (non-perturbative) rotating backgrounds**: the a = 2, M = 1
  drainhole at J = 0.25 and J = 1 (v_e 0.057 / 0.21), ~2 s each at
  64 x 16.  Independent full-Einstein residual (sympy Ricci, C >= 0.05)
  1.0e-10 / 4.2e-10 vs the static member's 2e-11 floor -- against 3e-5 /
  1e-2 for the O(J^2) tables that ran the Step 1 holds.  D^2 spread
  1.4e-12, Smarr 9e-11, J-flux spread <= 1.3e-9, tails <= 5e-12.
- Agreement with the O(J^2) generator at equal J: f, N differ by J^4 and
  omega by J^3 with ratios constant to 1 % (J = 0.05-0.2); at J = 1 the
  full M_ADM is 1.4 % below O(J^2), D +0.3 %, the omega sector -13 %
  (its own J^2-relative correction).
- First `.spinbg` from the full solver written (`backgrounds.py full`,
  1025 x 65; bilinear midpoint error in f 1.8e-7 -- P5 sizes the final
  grids).  22 wrapper tests in `tests/spinning_wormhole/`.
- NEXT in the plan: P3 (continuation to v_e ~ 0.9 on both families, CKK
  anchors), then P4 near-extremal, P5 tables + the 3D acceptance hold
  (GPU; will be proposed before any launch).

## STEP 1: THE SPINNING HOLDS INFLATE (2026-10-12)

`spin_hold_L64_ml3_J025_t100` and `spin_hold_L64_ml3_J100_t100` (the Step 0
drainhole at J = 0.25 and 1.0, same grid, gauge and table pipeline; no
checkpoints) reached t = 100 clean, 0 NaN.  Packed as `02_spin_hold/`.
- **Inflation, not collapse**: the throat grows on the static hold's unstable
  mode with the opposite sign: τ = 5.8 (J025) and 5.6 (J100) vs 5.26.
  R_eq 3.90 → 5.34 at t = 64 (J025); 4.09 → 7.36 at t = 40 and ~9.3 by
  t = 56 from the χ slice (J100; the in-code rays cover the finest level
  only, r < 4, and lose the throat at t ≈ 41).  No MOTS about the throat
  once it opens (from t = 42 / 11): it is anti-trapped, as in the merger's
  ε < 0 arms; a MOTS on its far side (coordinate r ≈ 1.5, R 36 / 30.5)
  appears from t = 55 (J100) / 84 (J025).
- **The branch is set by the data, not yet by the spin**: in the merger seed
  arms' terms the holds act as radial kicks ε ≈ −3e-5 and −7e-3; ×230 for
  ×4 in J is ~J⁴, the size of the O(J²) data's own error (J² would give ×16).
  The spin's own signature is the throat's flattening, at a rate ∝ J²
  (R_eq − R_pol 0.04 → 0.35 by t = 25 at J = 1).
- **Constraints at the static hold's level** to the trust windows: L2_Ham
  ≤ 2.5e-3; L2_Mom rises with the grid's K speckle exactly as in the static
  hold.  Trust windows t ≤ 64 (J025, the box's boundary return) and t ≤ 57
  (J100: throat leaves level 2 at r = 8, Ham doubles off its floor at 59).

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

`static_hold_L64_ml3_t100` (L = 64, N = 128, ml3 = the merger hold's grid on a
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
   over the full record — packed as `01_static_hold/static_hold_L64_ml3_t100`.
   One resolution was decided to suffice: the twin check is stronger than a
   three-resolution τ fit (the merger already owns the resolution ladder on
   this grid).
2. **Step 0 numerics** (optional hardening, none blocks Step 1): the
   Δt = 0.02 Δx cause; constraint norms on the finest levels;
   constraint-solved Π seeds; 1/R waveform extrapolation.
3. ~~**Step 1 slow spin**~~ DONE 2026-10-12: the O(J²) slow-spin generator
   is in (`backgrounds.py slowspin`, same `.spinbg` format, validated above)
   and the first spinning holds are done (J = 0.25, 1.0: they inflate, the
   branch set by the data's J⁴ error, above).
4. **The full solver** ← IN PROGRESS (started 2026-10-12): the rotating
   Ellis–Bronnikov backgrounds solved in full, not as the O(J²) expansion —
   fast spin, and data accurate enough that the spin, not the data's error,
   picks the throat's branch.  Plan `SpinningSolver.md`; P0–P2 (M1) done
   (above), P3 continuation next.

## RULES CARRIED OVER

Same launch discipline as the merger campaign: no GPU start-up before the go,
checkpoints are asked per run, full default frame set, STATUS updated and
pushed at every launch/stop/wipe, scratch checked with every run check.

**Wave extraction placed for the box (decided 2026-10-12).** Production runs
must put their Ψ4 extraction radii in the wave zone of *their* box: outside
the near zone (≳ one ringdown wavelength from the throat) and inside the
sponge's inner radius.  The consumer's default `--radii 14 30` is the merger's
L = 128 choice; on L = 64 (sponge 24–32) R = 30 is damped and R = 14 is
near-zone — e.g. 12 / 16 / 20 there, and the in-code extraction
(`activate_extraction = 1`) on for a per-step waveform.  A spinning collapse
radiates l = 2, m = 0 with no seed (the oblate throat), so it needs this.
The two J holds ran with 14 / 30.
