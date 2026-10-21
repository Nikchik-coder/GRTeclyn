# Spinning-wormhole campaign — packed results

Nonlinear evolutions of rotating Ellis–Bronnikov wormholes, slow spin to the
extremal Kerr limit, behind N. M. Shirokov and I. Nachevsky, *Rotation slows the
instability of Ellis–Bronnikov wormholes* (2026). Code:
`Examples/SpinningWormhole/` (launcher:
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`).

## The paper

The paper's 19 evolutions (its Table IV) are `campaign/drainhole/00_paper_runs/`.
Every figure rebuilds from this directory without a GPU, with
`grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.spinning_wormhole.<script>`:

| In the paper | Data | Script |
|---|---|---|
| Fig. 2, Table II | `solver/solutions.tsv`, `solver/kk2014_fig1_digitized.tsv` | `plot_kk2014_comparison` |
| Fig. 3, Table III | `solver/solutions.tsv`, `solutions/`, `backgrounds/`, `scalar_charge_runs.tsv` | `plot_spin_trends` |
| Tables IV–V, Fig. 4 | `campaign/drainhole/00_paper_runs/`, `backgrounds/`, `runs_registry.tsv`, `trust_windows.tsv` | `plot_instability_curve` |
| Fig. 5 | `campaign/drainhole/00_paper_runs/`, `backgrounds/` | `plot_farzone_wave` |
| Fig. 6 / Fig. 7 | the D21 / D90 triplets in `campaign/drainhole/00_paper_runs/` | `plot_convergence --spin 0.2c` / `plot_convergence` |
| Sec. IV B, the t = 0 checks | `campaign/drainhole/03_t0_checks/`, `campaign/symmetric_massless/01_t0_checks/` | — |

The other groups below are the campaign's development record; the paper quotes
none of their numbers.

- `binaries.tsv` — the record of every frozen campaign binary (the bin/
  directory itself is untracked).
- `runs_registry.tsv` — one line per run: what it is for, outcome.
- `trust_windows.tsv` — the last trustworthy time per run; movies, figures
  and quoted numbers stop there.
- `backgrounds/` (2026-10-20) — the header (grid + `meta` numbers: J, M_ADM,
  v_e, J/A, the solver gates) of each background table the article's 3D runs
  start from, copied verbatim from the untracked 12.7 MB `.spinbg` tables by
  `python -m grteclyn_wrapper.visualisation.spinning_wormhole.headers`; the
  figures read these.  The far-zone 0.2c pack also holds
  `light_speed_equator.dat`, the light speed of its wave figure's panel (d),
  taken from the run's slice cache (`plot_farzone_wave --light-from-cache`).
- `campaign/` — packed runs (full `.dat` streams, `evolution_params.txt`,
  `run_manifest.json`, `mots_spectral.dat`; paths scrubbed by
  `grteclyn_wrapper.packaging.scrub_paths`; packed by
  `research/spinningwormhole/pack_run.sh`), laid out as the run tree
  (decided 2026-10-13): `campaign/<family>/<NN_study>/` here is
  `runs/spinning_wormhole/<family>/<NN_study>/` there, a triplet in a
  per-spin folder (the merger's convention: `results/merger/campaign/<group>`
  ↔ `runs/wormhole_merger/<group>`).  The families:
  - `drainhole/` — family (a): η0 = 2, γ = −π, the static drainhole
    a = 2, M = 1 (the merger's single wormhole) spun up;
  - `symmetric_massless/` — family (b): CKK's symmetric family (γ = 0,
    equal masses on both sides), whose static member is the massless
    Ellis wormhole; rescaled η0 1 → 2 so its throat sits on the
    drainhole's cells.

## Claims: drainhole (`campaign/drainhole/`)

Every evolution below ran before the three numerics fixes of 2026-10-17 (spline table, exact
coarse–fine weights, no RK stage re-fill; `research/spinningwormhole/STATUS.md`): none is quoted until
its rerun on binary rkfix 0661dac4. The pre-fix paper runs and their packs were moved to
`runs/spinning_wormhole/drainhole/00_archive/superseded_2026-10-17/` (untracked).

- `01_static_hold/static_hold_L64_ml3_t100` (2026-10-11; launched as
  `static_hold_L64_t100`, renamed 2026-10-12): the Step 0 anchor.
  The merger's production `single_hold_t100` ran on this exact grid (L = 64,
  N = 128, ml3), and the new table-driven pipeline reproduces it as a
  numerical twin over the FULL record: t = 0 bit-identical, L2_Ham within
  5e-7 (median 0) for all t ≤ 100, collapse milestones within one time unit;
  τ(δR) = 5.27 vs the merger's 5.12 fit; MOTS on every plotfile, horizon
  detaches at t ≈ 61 and shrinks under the phantom flux.  The t > 80
  constraint growth is the same in both runs — a property of this grid, not
  of the new code.  Trust window t ≤ 64.  Constraint overlay:
  the run's `figures/constraint_norms.png` (both curves within linewidth).
- `02_spin_hold/spin_hold_L64_ml3_J025_t100` and `…_J100_t100` (2026-10-12):
  Step 1's first spinning holds, the Step 0 drainhole at J = 0.25 and 1.0 on
  the same grid.  Both throats INFLATE where the static one collapses: the
  same unstable mode with the opposite sign (τ = 5.8 and 5.6 vs 5.26), no
  horizon about the throat (anti-trapped), R_eq 3.90 → 5.34 at t = 64
  (J025) and 4.09 → 7.36 at t = 40 (J100).  In the merger seed arms' terms
  they act as radial kicks ε ≈ −3e-5 and −7e-3, the inflating sign; that
  equivalent kick grows ~J⁴ (×230 for ×4 in J), the size of the O(J²)
  data's own error, so the branch is set by the data, not yet by the spin.
  The spin's own signature is the throat's flattening, at a rate ∝ J².
  Constraints at the static hold's level.  Trust windows t ≤ 64 and t ≤ 57.
  (2026-10-13: that "flattening" is most likely the coordinates, not the
  geometry: in the full-data holds the in-code R_pol ray falls 14–16 % by
  t ≈ 11 while the MOTS area about the same throat stays constant to 1e-4.)
- `03_t0_checks/` (2026-10-13): Step 3's t = 0 check of the fast-spin
  tables in 3D, run to t = 1 on the Step 1 grid (`t0_checks.py`:
  per-level constraint shells away from the puncture, throat-ray minima
  against the table's own), at v_e 0.51 on three grids
  (N = 96 / 128 / 192): Ham and Mom converge at 4th order inside the
  throat; outside they grow as 1/dx² and 1/dx, the tables' fixed ~2e-7
  bilinear error, 10⁴× below the O(J²) holds' push; throat rays converge
  to the table (−5e-5 at N = 192).
- `04_fast_spin_hold/spin_hold_L64_ml3_ve070a_t100` (2026-10-13): the
  drainhole family at v_e 0.70 on the J holds' grid and gauge, only the
  table changed.  DIED at t = 42.36 at the far-side puncture, not the
  throat: the puncture's χ fell to the min_chi floor by t ≈ 4 (in every
  other hold it rises) and its shift ran away; the throat never moved
  (R_eq 7.7710 → 7.7713, MOTS area constant to 1e-4 while found).
  Trust window t ≤ 40.
- `04_fast_spin_hold/spin_hold_L64_ml3_ve070a_minchi4_t100` (2026-10-15):
  the run above rerun exactly, one knob — min_chi 1e-8 → 1e-4.  RESCUE
  PASS: reaches t = 100 with 0 NaN.  The floor is pinned only t = 0–3.17,
  then χ_min lifts off and rises to 1.0e-3 by t = 100 — the far side
  heals rather than clamps.  L2_Ham flat at 3.4e-3 the whole run; the
  throat is frozen, R_eq −0.016 % over t = 0–100 (the 0.5c hold shrinks
  −2.9 % on this grid; the spin-slowdown trend continues to 0.7c, where
  it is below detection).  Trust window t ≤ 64 (the L64 boundary
  return).  Verdict: the 0.7c far-side death is cured at the data level;
  B2 (v_e 0.7 on L = 128, ×3) unblocked with min_chi 1e-4 in its
  templates.
- `04_fast_spin_hold/spin_hold_L64_ml3_ve050a_t100` (2026-10-13): the
  drainhole family at v_e 0.51 on the J holds' grid and gauge, only the
  table changed; reached t = 100 clean.  The throat SHRINKS, the static
  hold's sign, but far more slowly: MOTS R −0.61 % at t = 64, where the
  static hold's had shrunk 2.5 % by t = 49 and detached a horizon at
  t ≈ 61.  The shrink's e-fold time is ~5 at t = 40–50, then its rate
  stops growing; no horizon forms.  Constraints at the static hold's
  level until the boundary return (t ≈ 62).  Trust window t ≤ 64; 14
  movies to t = 64 in the run directory.
- `04_fast_spin_hold/spin_hold_L64_ml3_J100_full_t100` (2026-10-13): the
  J = 1 acceptance hold — the point the O(J²) `…_J100_t100` ran, now on
  the exact table (v_e 0.21), same grid and gauge.  The throat COLLAPSES
  on the static hold's mode: R_eq −1 % at t = 46.9 and −10 % at 61.8
  (static: 44.1 / 57.0), τ 6.8 against the static hold's 5.8 by the same
  measure; the run dies inside the collapsing throat at t = 70.64.  So
  the O(J²) hold's inflation was its data's error, and with the 0.5c
  hold the rate falls with spin: τ 5.8 (J = 0), 6.8 (v_e 0.21), and at
  v_e 0.51 only −0.5 % by t = 64.  Trust window t ≤ 64.
- `05_hold_L128/J100_full/spin_hold_L128_ml3_J100_full_t100` (2026-10-15),
  the verification rung's N = 256 member: the J = 1 exact point (v_e 0.21)
  on the production L = 128 box, levnorm binary (per-level masked norms).
  REACHED t = 100 clean, 0 NaN.  THE MODEL CHECK PASSES:
  τ(ΔR ∈ [0.01, 0.3]) = 6.78 vs the L64 acceptance run's 6.8 (static 5.8);
  R_eq −1 % / −10 % at t = 46.85 / 61.82 vs L64's 46.9 / 61.8 — the
  nonlinear collapse rate at the published-domain point is box- and
  resolution-independent to 0.05 time units.  Full collapse with a
  detached horizon at t ≈ 64 (static ≈ 61), throat −44 % by t = 96,
  ridden cleanly to t = 100 (χ_min ~1e-3, puncture-style).  Trust window
  t ≤ 67.  The formal triplet awaits the N 192 rerun and N 384.
- `06_dt_ladder/spin_hold_L128_ml3_ve050a_sig04_dt005_t100` (2026-10-16),
  speed-recipe test: B1's production run with σ 0.4 + dt 0.05 as a
  package.  DIED at t = 47.85 (NaN in K): χ_min crashed to the floor by
  t ≈ 30 and max|K| ran away, where B1 held 1.5e-6 to t = 100.  dt 0.05
  is unstable on L128 spin data even with σ 0.4; dt stays 0.02 and the
  speed-up candidate is σ 0.4 alone.  Nothing from this run is quoted.
- `static_hold_L64_ml3_spdrv1_t100` (2026-10-16; ARCHIVED 2026-10-17 in
  `drainhole/00_archive/superseded_2026-10-17/`, pre-fix), damping
  sponge test: the static hold with `sponge_drive_strength = 1` (drive
  the 24–32 shell back to the stationary background).  Reached t = 100
  clean; throat and all interior diagnostics identical to the packed
  static hold to 4 digits while |K| falls two decades across the shell.
  The unchanged interior ring shows the t ≈ 60+ growth is
  collapse-sourced, not a boundary echo — the drive is adopted for runs
  intended past the box-crossing time (t ≳ L).  (2026-10-18: the drive is
  off for new runs; it pulls the shell back to the t 0 data, 48× more face
  junk; STATUS.md.)
- `05_hold_L128/ve050a/spin_hold_L128_ml3_ve050a_t100` (2026-10-15), Phase
  B1's N = 256 member: the drainhole at v_e 0.513 on the production L = 128
  box (the merger hold's layout, return t ≈ 120), to t = 100.  REACHED
  t = 100 clean, 0 NaN; matches its killed first launch exactly through
  t = 46 (MOTS R byte-level).  The throat shrinks slowly throughout:
  MOTS R −1 % at t = 71 where the static twin took t = 44, −3.14 % at
  t = 100, no horizon detaches.  L2_Ham doubles off its 5.4e-4 plateau at
  t = 78.8 (the slow level-2 interface mode the dt ladder identified;
  L2_Mom ×2 off 3.8e-5 at 66.8); the far-side χ reaches the 1e-8 floor at
  t = 91.9.  Trust window t ≤ 78; movies to t = 78 in the run directory.

## Claims: symmetric, massless (`campaign/symmetric_massless/`)

- `01_t0_checks/L64_ladder/` (2026-10-13): the same t = 0 check (Step 1
  grid, N = 128, to t = 1) on family (b) rescaled to η0 = 2, at
  v_e 0.50 / 0.70 / 0.90 / 0.95 / 0.99: throat rays within 0.1 % of the
  table, constraints at the static hold's level.
- `01_t0_checks/L128_A1/<spin>/` (2026-10-13), Phase A1: the t = 0 check on
  the L = 128 box (the merger's `single_hold_L128_t100` layout) at
  v_e 0.24 / 0.43 / 0.67 / 0.85 / 0.90 / 0.95 / 0.99, each as a triplet
  N = 128 / 192 / 256 run to t = 1; per spin `t0conv_<spin>_L128_checks.txt`
  (`t0_checks.py` with `adm.py`).  PASS at every spin: the throat's ray
  radii converge to the table's (R_eq −7e-5 at v_e 0.24 to −9e-4 at 0.99
  on N = 256); Ham and Mom converge at ~4th order inside the throat and
  grow as 1/dx² and 1/dx outside, the tables' interpolation error (at
  0.95–0.99 the innermost shell, at the far-side puncture, stops
  converging); the 3D ADM mass integral equals the table metric's on the
  same grid to ≤ 1e-12, and its extrapolation meets the table's meta M to
  2e-5–7e-4 (0.7 % at 0.99, the extrapolation at R ≤ 46); J meets the
  table's to 2e-3 at 0.24 falling to 2e-5 at 0.99 (an R- and
  N-independent offset of 1e-4–9e-4).
- `03_spin_hold/` (2026-10-13): the first puncture probes (v_e 0.43 / 0.67 /
  0.85, N = 128 on L = 128) all DIED at t = 3.4–4.0 at the far-side
  puncture, but were SUPERSEDED the same day and their packs removed:
  they ran at dx0 = 1, below the resolution floor (triplets are
  N 192 / 256 / 384), so the deaths are confounded between the coarse grid
  and the puncture itself.  The far-side evidence that stands is the
  drainhole's v_e 0.7 hold (dx0 0.5).  Retests run at N ≥ 192 (the first:
  the √χ-lapse probe, 2026-10-13).

## Fast-spin solver

- `solver/solutions.tsv` — every converged solution of the fast-spin
  solver (462 rows, 20 continuation legs: families (a) and (b), the four CKK
  anchor families, the low-spin end of the symmetric family), one row each:
  family, grid and map, the global charges and throat radii in CKK
  conventions, and the identity gates.  Packed from the untracked
  `runs/spinning_p3/` by `python -m
  grteclyn_wrapper.visualisation.spinning_wormhole.solutions`.
- `solver/kk2014_fig1_digitized.tsv` (2026-10-13): the wormhole curves of
  Kleihaus & Kunz 2014 Fig. 1 (M/M0, their Smarr dots Omega J/(Omega0 J0),
  J/J0, R_p/R, R_A/R) read off the published raster by
  `grteclyn_wrapper.visualisation.spinning_wormhole.kk2014`.  Reading error,
  measured by reading their printed Kerr curves the same way: rms 1-6e-4,
  max 1.1e-3.
- `figures/solver/kk2014_comparison` (2026-10-13), THE PAPER FIGURE: our
  symmetric family (eta0 = 1, gamma = 0; 81 solutions, v_e 0.02-0.991, plus
  the exact static member) as curves in KK's normalisation (M0 = R,
  J0 = R^2/2, Omega0 = 1/R), their digitized points as open symbols, Kerr
  from closed forms (dashed).  Coloured by quantity as KK do (red M/M0 and
  R_p/R, green J/J0 and R_A/R, blue Omega J), the spinning paper's scheme;
  `--palette house` or `--colors C1,C2,C3` redraws it in another.
  Digitized minus ours: rms 2.5-8e-4, max 2.5e-3 over all five curves, the
  size of the reading error, so the two solvers agree to the precision a
  printed figure carries.
- `figures/solver/kk2014_fig1_overlay` (2026-10-13), INTERNAL CHECK ONLY
  (it shows the published raster itself, which a paper cannot reuse): our
  solutions as circles on KK's Fig. 1.  The closed-form Kerr curves drawn on
  the calibrated axes (`--check`) land on the printed Kerr curves, fixing
  both the pixel calibration and their J0 = R^2/2.
