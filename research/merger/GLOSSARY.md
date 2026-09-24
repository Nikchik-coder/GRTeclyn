# Wormhole-merger campaign — glossary

What a run name, a stream column, a sign or a horizon word means, each with the
file it was read from. Written 2026-09-24 from a sweep of the pack
(`results/merger/campaign/`: 149 distinct runs, 148 with `evolution_params.txt`).
Paths are repo-relative; "unknown" means not determinable from what was read.
Map of the repository: [`../../MAP.md`](../../MAP.md).

## a. Run-name grammar

A name is a string of `_`-separated tokens. Most are hand-chosen (`launch.sh --name` / `WHM_NAME`). `run_single.sh` adds its own
suffixes, always in this order: `_m<mass>` `_lapse<N>` `_sg<NN>` `_fg` `_tl<N>` `_r<NNNNN>`. Numbers drop the decimal point:
`p012` = 0.12, `sg01` = 0.1, `a15` = 1.5, `d65` = 6.5. A knob with no token is at its production value: the run-tree README
says "everything not named in the suffix is identical" (`runs/wormhole_merger/README.md` §"Reading a run name").
Machine form: [`results/merger/name_grammar.tsv`](../../results/merger/name_grammar.tsv) (95 rules);
checker: `results/merger/analysis/name_check.py`, whose verdict per run is the `name_check` column of
[`results/merger/runs_index.tsv`](../../results/merger/runs_index.tsv).

| token | meaning | param = value (evolution_params.txt) | example |
|---|---|---|---|
| `d<N>`, `d65`/`d75` | throat separation d | \|wormhole_centerA − centerB\| = N (6.5, 7.5); BBH: \|bh1.offset − bh2.offset\| | `merge_headon_flip_d8_v1_t100`, `place_d65_step1` |
| `p<NNN>` | Bowen–York momentum per throat | \|wormhole_momentumA\| = d.dd, first digit = units (`p012` = 0.12, `p02` = 0.2); binaries push along y, B = −A | `merge_orbit_flip_d12_p045_t200` |
| `L<NN>` | box side | L = 64 / 128 | `single_hold_L128_t100` |
| `L<d>` (ladder only) | refinement level, **not** the box | max_level = d | `ladder_L6_r05000` |
| `ml<N>`, `lvl<N>` | finest refinement level | max_level = N | `single_hold_ml4_t100`, `..._p020_lvl5_t200` |
| `lvl<N>from0` / `lvl<N>chk` / `lvl<N>down` | level N from t = 0 / checkpointed twin / restarted from a finer checkpoint | no amr.restart / checkpoints written / amr.restart set | `v2_spiral_d12_p012_L128_lvl5from0_t100` |
| `n<N>` | base cells per side | N1 = N2 = N3 = N | `merge_orbit_flip_d12_n160` |
| `t<NNN>` | stop time | stop_time = NNN (BBH: evolution.stop_time) | `single_eps_p1e2_t250` |
| `eps_p<m>e<k>` / `eps_m<m>e<k>` (2 tokens) | declared spherical seed ε | wormhole_seed_amplitude_A = ±m·10⁻ᵏ | `single_eps_m1e3_t100` |
| `q<m>e<k>` | quadrupolar seed ε₂ | wormhole_seed_l2_amplitude_A = m·10⁻ᵏ | `single_eps_p1e2_q5e2_ml4_t100` |
| `pureq` | pure quadrupole, no spherical kick | wormhole_seed_amplitude_A = 0 | `single_pureq_q1e2_ml4_t100` |
| `hold` | lone throat held at exact static data | no seed (ε = ε₂ = 0) | `single_hold_t100` |
| `single`, `stage1`, `s15`, `s16ml3`, `s1uni<N>`, `s20` | one throat (s-labels = Stage 1 / 1.5 / 1.6 / 1.4 unigrid / 2.0) | wormhole_throat_radius_B = 0; stage1/s15 max_level 2; s1uni max_level 0, N1 = N | `s1uni256_lapse5_sg01` |
| `merge`, `ctrl`, `place` | two throats | wormhole_throat_radius_B > 0 | `ctrl_rest_d14` |
| `flip` | throat B's scalar reversed (merger channel) | wormhole_phi_sign_B = −1 | `ctrl_flip_d12` |
| `twin` | p = 0.12 one-knob twin series (flip implied) | wormhole_phi_sign_B = −1 | `merge_twin_p012_plain_t100` |
| `place` | placement probe: scout pair at rest, flipped, one step | p_A = 0, phi_sign_B = −1 (+`step1`) | `place_d8_step1` |
| `headon` / `rest` | no momentum / released from rest | p_A = 0 | `merge_headon_flip_d12` |
| `orbit` / `spiral` / `boost` | tangential push / p012 production spiral / boosted lone throat (P ∥ z) | p_A > 0 (orbit with no `p` token: 0.12) | `orbit_d12_p012`, `s20_boost_p02` |
| (no flip/twin/place) | like-charge pair | wormhole_phi_sign_B = +1 (default) | `ctrl_rest_a1` |
| `a<N>` | throat scale a | wormhole_throat_radius_A (= B) = N (a15 = 1.5) | `ctrl_rest_a15` |
| `m<NN>` | drainhole ADM mass m | wormhole_drainhole_mass_A = N.N (m05 = 0.5; B defaults to A). ≠ launcher `_m` (= bare mass, unused) | `merge_headon_flip_d6_m05_t100` |
| `mu<N>` (template only) | μ = m/a | drainhole_mass_A / throat_radius_A | `params_single_mu2_eps_p1e2_t100` |
| `eta<N>` / `lp<N>` / `lc<N>` | Γ-driver damping / Bona–Masso lapse_power / lapse_coeff | eta / lapse_power / lapse_coeff = N (production 1 / 1 / 2) | `merge_twin_p012_eta4_t060` |
| `sg<NN>` | Kreiss–Oliger σ | sigma = N.N | `merge_orbit_flip_d12_sg10_r05000` |
| `lapse<N>` | initial lapse type | wormhole_initial_lapse_type = N (5 = e^u, 6 = 5 × collar) | `stage1_lapse6` |
| `fg` / `tl<N>` | fixed nested grids / their size | tagging_type = 1 / tagging_L = N (no packed tl) | `s15_lapse5_sg01_fg` |
| `dt0<NN>` / `halfstep` | Courant factor | dt_multiplier = 0.NN / 0.01 (production 0.02) | `single_hold_dt005_t070` |
| `cf<NN>` / `lowfloor` / `chireg` | χ floor | min_chi = 10⁻ᴺᴺ / 5e-10 / (min_chi 1e-20 + chi_rhs_floor 1e-8) | `merge_twin_p012_cf10_t060_r05000` |
| `helfer` / `w<N>` / `plain` | Helfer one-body correction / its window / plain superposition | wormhole_helfer_correction 1 / wormhole_helfer_width N / 0 | `merge_twin_p012_helfer_w2_t060` |
| `nodamp` / `damped` / `rw` | core matter damping off / on / radius window | core_matter_damping 0 / 1 / core_damping_radius_start,_full > 0 | `ladder_L5_damped_r05000` |
| `nofill` / `freeze`, `freeze2`, `latefreeze` / `fillnarrow` | interior fill off / on / narrow head-on skin | core_freeze_fill 0 / 1 / 1 with radii 1.0–1.5 | `freeze_wide_t080_r05000` |
| `narrow` / `wide` / `late` | orbital fill skin 1.3–1.8 / 1.5–2.0 / armed at t = 55.5 (not 53) | core_fill_radius_full, _start / core_fill_from_time | `freeze_narrow_late_t080_r05000` |
| `v1` / `v1c` / `v2` | Phase-3 head-on scout family (fill off) / V1c late-freeze family (fill on) / V2 production spiral | core_freeze_fill 0 / 1 (both chi_rhs_floor 1e-8) / L = 128 | `merge_headon_flip_d8_v1c_eps_p1e2_t100` |
| `autopsy` / `step1` / `chk` | NaN autopsy armed / one coarse step / rolling checkpoints | nan_autopsy 1 / max_steps 1 / checkpoint_interval > 0 and amr.checkpoint_files_output ≠ 0 | `single_eps_p1e2_q1e2_chk_t100` |
| `r<NNNNN>` | continuation leg from `BinaryWormholeChk<NNNNN>` | amr.restart ends `Chk<NNNNN>`; t_restart = NNNNN × 0.01 (parent's steps) | `merge_orbit_flip_d12_r03000` |
| `prof` / `mouths` | in-code radial core profile / + per-mouth areal radius and horizon scan | core_radial_profile 1 (+ `core_radial_profile.dat`, `horizon_scan.dat` exist) | `v2_spiral_d12_p012_L128_lvl3_t050_mouths` |
| `scalar` | consumer `--scalar-modes` (not in params) | (consumer): `scalar_modes.dat` exists | `single_pureq_q1e2_ml4_scalar_t100` |
| `diag` / `crosscheck`, `wave` | Weyl diagnostic pass / in-code Weyl4 on | write_extraction 1 / activate_extraction 1 | `freeze_wave_crosscheck_diag_r09000` |
| `bbh`, `control` | vacuum BBH control (stock BinaryBH params, bh1/bh2 bare mass 0.9615) | params format bh1.* / amr.* / evolution.* | `bbh_control_d12_p045_t100` |
| `bridge`, `grtresna` | GRTresna constraint-solved initial data | recipe_initial_data_file set (initial lapse type 1) | `bridge_grtresna_L64_t025` |
| `rr`, `ladder` | rerun with checkpoints copied out / refinement ladder from Chk05000 | (none): rr params = original's | `merge_orbit_flip_d12_p015_rr_t060` |
| `HOOKFAIL`/`OOMFAIL` + `YYYY-MM-DD`, `.__keep` | hand-added close-out label of a failed launch; pack copy | (none) | `autopsy_nodamp_r05000_HOOKFAIL_2026-09-08` |

**Checker result (packed runs, 2026-09-24):** 95 rules. Every token rule that reads evolution_params.txt holds for every testable run.
The 14 failures come from two rules, the effective-seed check (4) and the max_level absence default (10):
- **4 genuine mislabels.** The name (and the params file) says `q1e2`, but the run had no quadrupole. Each ran on the campaign pin
  `main3d_boost_2026-09-08.ex`, which never reads `wormhole_seed_l2_amplitude_*`. The binary contains no such string, and
  `results/merger/binaries.tsv` says so. Each run's t = 0 L2_Ham matches its seed-free twin to all printed digits:
  `single_pureq_q1e2_ml4_scalar_t100` (= `single_hold_ml4_t100`, 2.0955094722e-03), `single_pureq_q1e2_L128_ml4_scalar_t100` and
  `single_pureq_q1e2_L128_ml4_scalar_t500` (= `single_hold_L128_t100`, 6.5838765760e-04), and `single_eps_p1e2_q1e2_ml4_scalar_t100`
  (= `single_eps_p1e2_ml4_t060`, 2.3458350524e-03). The registry's "CORRECTED 2026-09-23" lines agree. The same binary also ignored
  `core_radial_profile = 1` in these 4 runs: none has a `core_radial_profile.dat`.
- **10 omissions on restart legs.** The absence rule fails because the name hides a raised max_level (5–6), set in the template or at
  launch. `WHM_MAX_LEVEL` adds no suffix. Runs: `merge_twin_p012_cf{08,10,12}_t060_r05000` and all 7 `freeze_*`.

Traps: `L<d>` means a level but `L<NN>` means a box. Hand `m05` is drainhole mass, but the launcher's `_m05` would be bare mass. `d15`
would be ambiguous. Template names are **not** run names: templates lack launch overrides (max_level, restart). Their token meanings
also drift: `t005` = 0.5, `lapse4` = lapse_coeff 4, `boost` = scalar boost velocity, and `mu2`'s `t100` is a-scaled (stop 50). See
`name_check.py --templates`.

## b. Units and conventions

| item | value / definition | source |
|---|---|---|
| G, c | G = c = 1; G_Newton = 1 in ConstraintsWithMatter/Weyl4WithMatter | `Examples/BinaryWormholeMerger/BinaryWormholeLevel.cpp` |
| mass unit M | each throat's ADM mass m = `wormhole_drainhole_mass_A/B` = 1.0 (carried by the lapse). A pair has M_ADM = 2. The BBH bare mass 0.9615 gives ≈ 1.00 per hole | params comments; paper §VI.A; `figures/FIGURES.md` |
| time, length | code units = M (m = 1). Half-mass runs (m05) are not rescaled | paper Table II (tab:scales) |
| drainhole | X = (r − a²/4r)/a, Ω = 1 + a²/4r², u = (m/a)(arctan X − π/2); α = e^u, γ_ij = e^{−2u}Ω²δ_ij, φ = C arctan X with 4πa²C² = a² + m²; χ = e^{2u}Ω⁻², h_ij = δ_ij, K_ij = Π = 0 | paper §II.B |
| a, b0, r | a = throat scale (`wormhole_throat_radius_A/B`; `b0_A/B` in code; b in the massless formulas). r = isotropic coordinate radius about a throat centre ("rbar" in code) | `SimulationParameters.hpp`, `BinaryWormholeInitialData.hpp` |
| production throat | a = 2, m = 1: minimal surface r_t = (m + √(m²+a²))/2 = 1.618, R* = e^{−u(r_t)}√(a²+m²) = 3.8895, α_th = 0.575, C = 0.3154. r → 0 is the far side's infinity (χ ∼ r⁴) | paper §II.B, §IV.B |
| σ, Q | φ = φ_A + σφ_B, σ = `wormhole_phi_sign_B` = ±1. Like charges repel, opposite attract; \|F_φ/F_grav\| = Q = (a²+m²)/m² = 5 | paper §II.C |
| seeds | ψ → ψ[1 + ε g(r)], ψ → ψ[1 + ε₂ g(r) P₂(cos θ)] about z; g = exp(−(r−r_t)²/w²), w = a/4 (width 0 = auto). Areal radius shifts ≈ 2ε. B defaults to A | paper §II.D; `SimulationParameters.hpp` |
| box | domain [0, L]³ with `center` = L/2 (32 or 64). `wormhole_centerA/B` are offsets from `center` (d12 → x = ∓6). Sommerfeld outer boundary; sponge r = 24–32 (L64) / 48–64 (L128), strength 4, ramp power 4 | params; paper §III.B |
| level N | dx_N = (L/N1)/2^N; dt_N = dt_multiplier·dx_N (subcycled, ratio 2). L64/N128 and L128/N256 both have dx₀ = 0.5 | run_tail.log dt per level (ladder runs) |
| nested boxes | `tagging_type` 2: boxes on each tracked throat; level-N half-width ≈ tagging_L·2^−(N+1). tagging_L = 64 in every run, L128 included | `Source/Tagging/FixedGridsTagger.hpp`; paper §III.B |

| level N | 0 | 1 | 2 | 3 (production) | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| dx (dx₀ = 0.5) | 0.5 | 0.25 | 0.125 | 0.0625 | 0.03125 | 0.015625 | 0.0078125 | 0.00390625 |
| dt (dt_multiplier 0.02) | 0.01 | 0.005 | 0.0025 | 0.00125 | 0.000625 | 0.0003125 | 1.5625e-4 | 7.8125e-5 |
| box half-width (tagging_L 64) | whole box | 16 | 8 | 4 | 2 | 1 | 0.5 | 0.25 |

Other dx₀: `n160` 0.4; `s1uni256` 0.25. The registry's dx for `ladder_L4` (0.0156) and `ladder_L5` (0.0078) is one level off. Their logs give 0.03125 and 0.015625.

## c. Data streams

In-code streams go to `<run>/data/` and are written every coarse step (dt₀ = 0.01 in production, 0.125 for BBH). Consumer streams
go to `<run>/small_data/`, one row per plotfile, i.e. every plot_interval × dt₀ (0.1–1.0). Coordinates are relative to `center`
unless marked **absolute**. Writer paths: `.hpp`/`.cpp` files are in `Examples/BinaryWormholeMerger/` unless a path is given.
`extraction/…`, `driver.py`, `worker.py` and `state.py` are in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/process_wave/consume_plotfiles/`. `metrics/…` is in
`grteclyn-wrapper/src/grteclyn_wrapper/`.

| file | writer | columns (as in header) → meaning | pitfalls |
|---|---|---|---|
| `constraint_norms.dat` | `BinaryWormholeLevel.cpp` | `time L2_Ham L2_Mom`: volume RMS of H and \|M_i\| over the level-0 grid | box-dependent (L128 starts ~3× lower); restart re-seeds the outer zone (~1.5 %) |
| `collapse_diagnostics.dat` | same | `time min_lapse min_chi max_abs_K min_lapse_x/_y/_z min_phi max_phi min_Pi max_Pi`, over the **finest level only**; min_lapse_x/y/z = centroid of the min-lapse cells | a clamped cell reads as the floor (min_chi = 1e-8); values jump when a restart adds levels |
| `binary_throat_diagnostics.dat` | `BinaryThroatDiagnostics.hpp` | `time separation xA yA zA chiA_min lapseA_min xB … lapseB_min theta_A ah_r_A theta_B ah_r_B theta_common ah_r_common` | **A = half-space coord[binary_diag_axis] ≥ split**: axis x in every two-throat run, so A = the params' throat B (+x); the stage-1/1.x/2.0 lone throats split along z. The plane is fixed, so A/B scramble after a quarter orbit. θ uses +r orientation (a live monitor only; before 2026-09-01 it was conformally flat and wrong); θ = 1e30 means not measured; ah_r = 0 means none. Single throat: A/B are two halves of one throat |
| `throat_track.dat` | `ThroatTracker.hpp` | `time xA yA zA chiA_pit nA xB yB zB chiB_pit nB`: χ-pit centroids; n = cells averaged (0 = lost) | **A = params' wormhole_centerA** (x < 0), the opposite of binary_diag; B columns are 0 for a lone throat |
| `core_radial_profile.dat` | `CoreRadialProfile.hpp` | `time`, then 128 shells each of `chi_min_r<rc> absK_max_r<rc> lapse_min_r<rc> n_r<rc> dx_r<rc>` (dr 0.03125 to r 4, about `center`), composite over all levels | 1e30 = empty shell; `.dat.gz` = hand-kept unthinned copy; binary `coreprof_2026-09-15` was finest-level only |
| `Weyl4_mode_<l><m>.dat` | `Source/ParticleInterpolator/WeylExtraction.hpp` | `time`, then (Re, Im) per sphere, and a `# r = R R …` line: ∮ rΨ₄ ₋₂Ȳ_lm dΩ | `2-2` = (l = 2, m = −2); first row at t = dt; **not thinned**; spheres (extraction_radii) can differ from the consumer's |
| `Weyl4_extraction_NNNNNN.dat` | same (`write_extraction = 1`, `diag` run only) | raw `theta phi Weyl4_Re Weyl4_Im` per sphere | the pack's thinner read θ as time and kept 601 of 1776 samples; **repaired** 2026-09-24 (copied whole from the run tree; `pack_results.sh` no longer thins them) |
| `weyl_extraction_mode_<l><m>.dat`, `punctures.dat` | stock BinaryBH (bbh_* only) | as Weyl4_mode, at R 14/20/26/30; `time x_1 y_1 z_1 x_2 y_2 z_2` | puncture positions are **absolute** (26, 32, 32 at t = 0) |
| `psi4_mode_l2m0.dat` | consumer `extraction/psi4.py` via `driver.py` | `time Re(R=…) Im(R=…)`: R·Ψ₄ on ₋₂Y₂₀ | default radii 14 30 unless the profile says otherwise (headon 10 14 18) |
| `psi4_mode_l2_all.dat` | same | `Re_m<m>(R=…) Im_m<m>(R=…)` for m = −2..2 | as above |
| `psi4_directional.dat` | `worker.py` | `time P_total P_z_beam beam_ratio beaming_gain wavezone_std`: means over spheres of Σ\|RΨ₂ₘ\|², \|m\| = 2 part, their ratio, 1 + 4·ratio | wavezone_std as coded is the spread of R²\|Ψ₄\| (modes already carry R) |
| `areal_radius.dat` | `extraction/areal.py` | `time R_areal_min r_at_R_areal_min`: min of r/√χ along +x from `center`, r > 0.5 | exact only for a centred, conformally flat lone throat; for a pair it is a proxy (use horizon_scan); it loses the throat inside r = 0.5 |
| `horizon_scan.dat` | `extraction/horizon.py` | `time centre cx cy cz R_min r_at_R_min dev log10_abs_dev n_mots r_mots R_mots M_MS_mots theta_out_min_inside theta_out_max_at_R_min theta_in_max_at_R_min n_trapped n_anti_trapped n_outermost` | 3 rows per time: **A/B come from binary_diag (so A = params' B)**, C = common (midpoint) scan. cx–cz are **absolute**. dev = R_min/R_exact − 1 (R_exact = 3.8895 via `--horizon-r-exact`, else nan). The *_mots columns are nan when n_mots = 0. n_outermost is the same on all 3 rows |
| `boundary_flux.dat` | `metrics/probes/boundary.py` | `time net_outward_flux psi4_boundary_amp`: ∮[−Π∂_rφ/α + (β·n)Π²/α²]r²dΩ at r = 0.92·L/2, plus the rms \|Ψ₄\| there (not r-scaled) | header has **no `#`**; the sphere sits inside the sponge; canonical sign |
| `scalar_modes.dat` | `extraction/scalar_modes.py` | per sphere R: `R<R>_{phi,Pi}_l<l>_m<m>_{re,im}` (l ≤ 2), `R<R>_scalar_flux_kin`; A_lm = R·φ_lm (s = 0) | canonical flux sign (§d); ∂_rφ uses R ± 0.5 |
| `consume_state.json` | `consume_plotfiles/state.py` | `{"BinaryWormholePltNNNNN": true, …}`: the ledger that gates plotfile deletion | NNNNN = coarse step |
| `evolution_params.txt` · `run_tail.log` · `launch_banner.txt` · `backtrace.txt` · `LOST.md` | `research/merger/pack_results.sh` | the params.txt actually run · last 200 log lines · `[whm]` banner (binary, template, restart) · AMReX backtrace · note for a lost arm | output paths show scratch; one params file has a stray uncommented prose line (`…_lvl3_t050_mouths` l.2) |
| `*__part1_t0-30.5.dat`, `part1/` | pack | the pre-restart episode t = 0–30.5 of `merge_orbit_flip_d12_r03000` | — |

General pitfalls (`pack_results.sh`):
- Packed in-code streams are thinned to Δt ≥ 0.05, except the last time unit, which is kept whole. Rows step by 0.056 when dt₀ = 0.008 (`n160`).
- Restart legs start at t_restart + dt and carry **no header** in any in-code stream except core_radial_profile. Read the sphere radii from `extraction_radii`.
- `X.__keep` directories are byte-identical copies left by an interrupted pack; `pack_paths.py` skips them since 2026-09-24. `merge_headon_flip_d8_lp2_lvl5_t030_OOMFAIL_2026-09-22` is packed twice, filed and at top level.

Offline / hand-made files (one per run or group; headers name their producer):
- `horizon_offline_scan*.dat`: ah_oriented_scan.py output (`time r_mots R_mots M_MS_mots r_trapped_in r_trapped_out r_at_R_min R_min`).
- `05_binary_spiral/horizon/horizon_dissolution.dat`: ah_radial_scan.py, historic naive orientation. Superseded.
- `psi4_merger_stitched_0_97.dat`: p012 waveform stitched from 3 legs.
- `psi4_mode_l2m0_gated.dat` / `_t68clean.dat`: late junk gated.
- `core_radial_profile_OFFLINE_t57.dat`; `refinement_ladder.dat`; `wall_clocks.dat`; `placement_curve.dat`; `placement_scout_residual.dat`; `sign_rule_displacement.dat`; `branch_shell_scans_2026-09-08.dat`.
- `*.txt` scan logs; group notes `NOTES.md`, `INSTABILITY.md`, `BRANCHES.md`.

## d. Sign conventions

| quantity | as stored | as the paper uses it | source |
|---|---|---|---|
| `R<R>_scalar_flux_kin` | F_kin = −R²∮Π∂_rφ dΩ, canonical sign: **positive = outgoing canonical wave** (Π ≈ −∂_rφ), no lapse/shift, phantom sign not applied | physical energy flux F_φ = −F_kin, so an outgoing scalar wave carries negative energy; quoted E_φ are negative (head-on −0.056/−0.071/−0.075) | `scalar_modes.py` docstring; paper §VIII.F–G; `plot_scalar_channel.py` negates |
| `net_outward_flux` | canonical T^t_r ≈ −Π∂_rφ/α + shift term, outward > 0 | the same phantom caveat applies (the physical flux is its negative) | `metrics/probes/boundary.py` |
| Ψ₄ | Weyl4WithMatter: E/B decomposition (Alcubierre) with the gr-qc/0104063 tetrad; every stream stores rΨ₄ projected on spin −2 harmonics, Re/Im | amplitudes quoted as rΨ₄; in-code and consumer agree to 0.2 % at the head-on's burst peak, but on single throats the in-code stream is floor-dominated (only the consumer's is used) | `Source/CCZ4/Weyl4.hpp`; paper §III.C |
| φ, flip | A: +C arctan X_A (C > 0); B: σ·C arctan X_B; the π/2 tails are subtracted so φ → 0 at the boundary. Lone throat φ ∈ (−Cπ, 0) = (−0.991, 0); flipped pair min/max φ = ∓0.879 | σ = −1 is the merger channel | `BinaryWormholeInitialData.hpp`; collapse_diagnostics t = 0 |
| K, θ± | θ± = ±div s + K_ij s^i s^j − K on γ = h/χ; K > 0 = contracting | trapped: θ_out ≤ 0 and θ_in ≤ 0 | `extraction/horizon.py`; `branch_shell_scans_2026-09-08.dat` header |
| orbit sense | A at x = −6 with +p ŷ, B at +6 with −p ŷ: orbit in the x–y plane, L_z < 0 (from params) | — | params |

## e. Horizon terms

| term | definition | where defined |
|---|---|---|
| areal radius R | √(Area/4π) of a coordinate sphere, using the full induced metric h_ij/χ | `extraction/horizon.py`; paper §III.C |
| throat / mouth / pit | throat = minimum of R(r) about a mouth centre (R_min, R* = 3.8895 exact); mouth = one throat as seen from our side; pit = the χ minimum at the centre (the compactified far infinity) that the tracker follows | paper §II.B, §III.C; `ThroatTracker.hpp` |
| orientation rule | "outward" = the side where R increases (−d/dr inside a throat). The historic +r scan (ah_radial_scan.py, the in-code θ columns) labels throat interiors "trapped" (GPU_PLAN Defect 2) | `ah_oriented_scan.py`; paper §III.C |
| trapped / anti-trapped / normal shell | θ_out ≤ 0 and θ_in ≤ 0 everywhere / θ_out ≥ 0 and θ_in ≥ 0 everywhere / θ_out > 0 > θ_in | `ah_oriented_scan.py` |
| star-shaped scan, "the scan's MOTS" | coordinate spheres about a centre; MOTS = the outermost sphere where max θ_out crosses 0 with θ_in < 0 and the same orientation on neighbouring shells. It is trapped everywhere, so it bounds the true MOTS from inside | paper §III.C; `horizon.py summarise` |
| M_MS | Misner–Sharp mass, 2M_MS/R = 1 + R²⟨θ₊θ₋⟩/4 (product averaged over the sphere). On an exact MOTS it equals R/2; on scan spheres it runs up to 13 % higher (settled) or 34 % higher (forming): the shape systematic | paper eq. (misner_sharp), §III.C |
| common horizon | a MOTS enclosing both mouths: the midpoint (C) scan finds r_mots > sep/2, giving `n_outermost` = 1. Merger criterion: n_outermost goes 2 → 1 | `horizon.py`; paper §VI.A |
| live vs offline scan | live = the consumer's horizon_scan.dat per plotfile (common scan on level 1, or level 3 in the headon profiles). Offline = ah_oriented_scan.py on kept plotfiles at finer levels | `consumer_profiles.sh`; paper Fig. headon_collapse |
| flow finder | shape-free MOTS hunt `grteclyn-wrapper/scripts/validation/ah_flow_finder.py`: r = h(θ,φ) in real Y_lm to ℓ = 6 (or 8), damped fast flow, areal orientation. Self-test (`--analytic all`, log in `results/merger/campaign/05_binary_spiral/flow_finder_selftest.log`): Schwarzschild R = 2M to 0.24 %, M_MS to 0.12 %; Ellis: no surface. The head-on remnant check left no recorded number | script docstring; paper §III.C |
| "horizon", "black hole" | a MOTS on the evolved slices. The phantom violates the NEC, so it need not lie inside an event horizon | paper §III.C |

## f. Processes and places

| name | what | source |
|---|---|---|
| `test params.txt` | the evolution binary, run from the run dir with argv[0] = label (default `test`), from a copy `/tmp/ml_jobs/bin/<label>_<md5-8>` | `run_single.sh` "Process table" |
| `test_post post.py …` | plotfile consumer sidecar (`consume_plotfiles`, entered via a one-line `post.py`, `--data scratch --out small_data`) | same; `wormhole_merger/README.md` |
| `test_job run_single.sh` | the supervisor started by `launch.sh` (`exec -a "<label>_job"`) | `launch.sh` |
| `tee run.log` | log writer | `run_single.sh` |
| `test_pre pre.py …` | launch-time checks: the preflight (`preflight.py`) and the run manifest (`run_manifest.py`), since 2026-09-24 | `run_single.sh` "Preflight" |
| run dir | `runs/wormhole_merger/[NN_group/…/]<run>/` (untracked, on the shared filesystem): params.txt, run.log, data/, small_data/, frames/ | `run_single.sh`, `pack_results.sh` |
| scratch | `/tmp/grteclyn_scratch/<run>/` on **each GPU node, node-local** (`GRTECLYN_SCRATCH` overrides): plotfiles and checkpoints. The run dir holds a `scratch` symlink. The consumer deletes processed plotfiles, keeping the last N (`--keep-last`, default 3). `_keep_*/` holds items exempt from pruning | `run_single.sh`; `wormhole_merger/README.md` |
| first / second GPU node | labels for the campaign's two machines. Each has its own scratch, invisible from the other. GPUs ("cards") are numbered per node (GPU 0, 1) | `research/merger/GPU_PLAN.md` |
| campaign pin | the `launch.sh` default binary: `runs/wormhole_merger/bin/main3d_guard_7166787a_2026-09-24.ex` since 2026-09-24 (reads the l2 seed and the core profile); before that `main3d_boost_2026-09-08.ex`, which ignores both. A restart keeps its parent's binary | `launch.sh`; `results/merger/binaries.tsv` |
| other words | arm = one run of a one-knob family; leg = one restart segment; rung = one step of a ladder; wall = a family's NaN time (57 in notes = Chk05700, not a death); seam = restart/level discontinuity; skin = fill shell r_full–r_start; scout = first look; close-out = `research/merger/closeout.sh` | registry; results/merger/README.md; paper |

Not determined: the sign/orientation of the in-code Weyl4 tetrad beyond the cited references; which packed runs used
`main3d_coreprof_2026-09-15.ex` (no banner); how AMReX parsed the stray prose line in the `_mouths` params.
