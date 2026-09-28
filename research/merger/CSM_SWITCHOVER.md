# Switching the paper to the mode-3 production runs

Audit of 2026-09-28 (17:00–18:00 UTC, read-only): what the paper's ledger rows and figure modules need from
the three live `_csm` runs, and what the old superposed runs gave them. Items marked (checked) were re-read by
hand; the rest come from the audit and must be confirmed when fixed.

Runs: fly-by `merge_orbit_flip_d12_p045_L128_lvl5_t100_csm`, spiral `v2_spiral_d12_p012_L128_lvl5from0_t100_csm`
(first node), head-on `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm` (second node).

Fine as is: every in-code stream and consumer file has the old column names and order and is on NFS, current;
all 14 default frame fields render; no paper figure reads frames, slice caches or movies; the psi4/scalar
readers select spheres by name or header value (one exception below).

## While the runs are live (the user's call; restarts via `restart_consumer.sh`)

1. Fly-by horizon window (checked). Its consumer runs the defaults (`--horizon-half 2.5`, common level 1); the
   old run used `--horizon-half 3.0 --horizon-common-level 3` (registry). The edge moves 2.79 → 2.29, which the
   old mouths passed at t = 30. Affects clmFlybyScanEdgeTime/ScanEdge/EdgeRadius, clmGwScalarMouthReach, the
   trust-window reason, Figs 10g, 14, 15a, 17c. Restart before t ≈ 25. The comment on `orbit-modes-scan` in
   `consumer_profiles.sh` is wrong (the default is 2.5 since 09-09).
2. Head-on common scan (checked on the old `lvl5from0_scalar` arm: 11 of 201 C rows with a MOTS, t = 21.5–37,
   r ≤ 3.29). Half 3.0 loses the remnant MOTS behind the edge, so the late track, the fits, clmDetKerrRise and
   clmShapeSystRounded have no source (they came from `lvl3down` / fill twins). Restart with `--horizon-half 4.0`
   before the MOTS forms (t ≈ 21), at the latest t ≈ 35.
3. Spiral diagnostics. Its old run had neither, but the paper's spiral numbers came from other superposed arms:
   - no `core_radial_profile` (Fig 6d, clmSpiralChiFloorTime/SpikeStart/Anatomy*, and the freeze continuation's
     fill arming): needs a restart from a checkpoint with `core_radial_profile = 1` (diagnostic only);
   - no `--horizon-scan` / `--areal-radius` (Fig 15 merger arm, 16 clmMouth* rows, fit window t = 8–25): rows
     before the restart are lost; refit a later window or keep `_lvl3_t050_mouths`;
   - plotfiles at t ≈ 54–60 and the three left at the crash: the oriented scans (clmSpiralStarScanFirst/Last),
     the flow finder (Fig 6b), an offline core profile. Keep them before the consumer deletes them.
   - the burst reaches R = 20–44 at t = 62–88, after the expected crash near t = 60: Figs 7c, 8, 9 (spiral)
     need the freeze continuation or stay on the SERIES.

## At close-out

- Head-on: run `scripts/validation/ah_oriented_scan.py --half 4.0 --level 3 --center 64 64 64` (its default
  centre is 32) on the three plotfiles left at t = 98–100, before the prune; it has no checkpoints.
- Fly-by: add its row to `trust_windows.tsv` (clmFlybyTrust*, KeyError otherwise).
- `detector_arena_peak_gib` needs the AMReX finalize line: end at stop_time or by `dump_and_stop`.
- Pack: `_read_profile` (plot_spiral_collapse.py:152) and `plot_scalar_channel._cols` take line 1 as the header;
  the pack's `# thinned` first line breaks the thinned core profile; `mergers_profile` expects a hand-made `.gz`.

## Ledger extractors (research/merger/article/claims)

- `waves_stream_radius` (extract_waves.py:285-302, checked) picks by position: clmGwScalarRadiusOuter (index 1)
  now reads 20, not 30. Use index 2 or select by value.
- `mergers_total_mass` (extract_mergers.py:215-218, checked) returns 1 + 1 = 2.0. Mode-3 M_ADM is 2.34448
  (fly-by), 2.27476 (spiral), 2.35731 (head-on), column M_ADM of `data/constraint_solve.dat` (packed). Affects
  clmHeadonADMMass, clmHeadonRemnantOverSchw, clmSpiralSeparationOverMass; M = 2.0 is also in the args of
  clmGwScalarEnergyFlyby and clmGwCensEnergy*. Decide whether M means 1 + 1 or M_ADM.
- `waves_id_sphere` (extract_waves.py:581-611) evaluates the superposed closed form at R = 30. From the new
  fly-by's t = 0 slice cache: alpha_min 0.940, chi_min 0.852, flux factor 0.958 (old 0.933/0.866/0.938).
  Write the ring values to a packed file at close-out (the slice cache is not packed).
- Head-on MOTS rows read the hand-made `horizon_offline_scan.dat` (clmHeadonMots*, IrreducibleMass, WallLead*,
  Shrink, BornArea): repoint to `mergers_mots_first` on the live C rows. clmHeadonStandardMotsRadius then loses
  its contrast. Cadence is 1.0 (was 0.5): clmGwCensMotsTime 21.5 → 22, clmPsiPipelines 0.21 → 0.32.
- `headon_fit` / `mots_compactness` have no time window (FitStart = 36 only because lvl3down restarted there):
  add t0/t1.
- Spiral, from-0 vs restart: clmSpiralScalarMax (add t0 = 36), clmSpiralMaxKStart (t = 36),
  clmSpiralTransientTime (no handover in a from-0 run), clmSpiralPitSepLate/Early (`c1` exists only in a
  header-less restart file: use `separation`), clmSpiralLevelMedian* (no level-3 mode-3 partner).
- `single_scout` / clmScoutPlateau compares R_min with the superposed probes (4.45); mode 3 sits at R⋆ = 3.8895.
- clmMouthTauFlybyPlaced / SeedFlybyPlaced use the superposed `placement_curve.dat` (R(12) = 4.2386; mode 3
  3.8763): re-measure or drop.
- Hard-coded old names in the wrapper modules feed ledger rows: plot_scalar_channel FLYBY/SPIRAL,
  plot_mouth_growth FLYBY, plot_headon_collapse GROUP/SCOUT/DOWN, plot_psi4_gallery ARMS,
  extract_detector.py:732.
- Old-run times in args: waves_trough_time 55–95 (old peak 54.46), waves_swing windows (L = 64 crests),
  t0 = 21.5 (old MOTS), fly-by trust 70 / u 50 cuts. Re-derive from the new runs.
- Cost rows: clmDetCostSpiralChain ≈ 46 h at 2.17 u/h (was 23.5), clmDetCostHeadonLevelFive ≈ 48 h (was 28.2).

## Figure modules (grteclyn-wrapper/.../visualisation/wormhole_merger)

- M = 2.0: ligo:100-106 (M_CODE), gw_search nr.py:209, headon_collapse:122.
- headon_collapse: offline diamonds (:216-217) and the late track from DOWN/FILL/SEAMED (:214-266) go;
  `gap=0.75` (:304) assumes 0.5 cadence, use 1.5.
- constraint_evolution:221-229 puts L = 64 and L = 128 norms on one axis (H(0) 2.88e-3 vs 1.19e-3).
- spiral_collapse: freeze params and HANDOVER = 36 (:109, :215-223) KeyError / cut a from-0 run; chi-floor time
  can come from collapse_diagnostics min_chi (first floored row after t > 2).
- momentum_orbits:129-134 (Fig 14): the p = 0.12 floor cut lands on row 0 (pits on the 1e-8 floor to t = 0.95).
  TRUST_END (:106) keyed by the old name; no module reads `trust_windows.tsv`.
- mouth_growth: R_FLOOR 3.8 (:91) sits just under the new t = 0 radius 3.876.
- psi4_gallery: DRAW_GATES spiral = fill light cone (:249); head-on row reads `v1c_latefreeze` (:189-191);
  with the new head-on it needs a radii filter (10, 14, 18).
- spiral_ladder:92 raises without damped rows; y-limits 51.4–57.6 (:139).
- scalar_censorship: T_WALL 59.94, T_MOTS 21.5, SPIRAL_FRZ.
- Suggested: one run table (scenario → run, trust window, M_ADM, radii) resolved with `run_tree.find_packed`.

## No mode-3 counterpart (stay on the old runs or drop)

L = 64 scout (death, max K, offline scan, Midpoint*), r02200 / fillnarrow / lvl3down (seam, fill, down-step),
spiral lvl3_t050 (level-3 norms), prof_r03600 (t = 36 restart, star scans), freeze arms (fill radius, M6 twin,
overlap, remnant radius; Fig 13), clmShapeSystFormingLevelThree.
