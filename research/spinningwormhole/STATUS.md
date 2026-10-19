# Spinning-wormhole campaign — status

Compacted 2026-10-19 ≈ 18:30 MSK. The full earlier text (run-by-run start checks, the bug hunt step by step, the
pre-fix ledger) is `git show 57c23b77:research/spinningwormhole/STATUS.md`. Plans: [`SpinningWormhole.md`](SpinningWormhole.md)
(paper), [`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/`,
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Runs: `runs/spinning_wormhole/drainhole/00_paper_runs/`
(launch `--subdir drainhole/00_paper_runs`, pack `research/spinningwormhole/pack_run.sh drainhole/00_paper_runs <run>`).
Packs: `results/spinningwormhole/` (`runs_registry.tsv`: one outcome line per run; `trust_windows.tsv`). Branch
`feature/spinning`, pushed to `myfork`.

## RESULTS SO FAR (2026-10-19)

Spin delays the instability and the 0.9c is stable. The 0.40c (24 % of extremal) still collapses into a black hole;
the 0.46c (29 %) does not on t ≤ 100: its throat shrank to −1.1 % and turned back. That is where Azad et al.
conjecture the instability ends (≈ 30 %), but the 0.5c on N 192 (33 %, drive on) was still shrinking at t 100; the
0.5c on N 128 to t 150 (LIVE) and the 0.6c / 0.7c settle it.

- **Collapse is delayed by spin.** The throat reaches −1 % at t 43.7 (static), 46.9 (0.2c), 51.4 (0.30c) and 60.2
  (0.40c); the 0.46c peaked at −0.9 % at t 82 and turned back, the 0.5c (N 192) reached −1 % only at t 99.4, and the
  0.9c stays flat to t 150 at all three resolutions.
- **The 0.46c turned.** Its areal throat radius fell through the band at a near-constant 0.035 %/t (linear, not
  exponential), peaked at −1.12 % at t 83 and was back to −0.21 % at t 100; R_eq and the MOTS move with it, no
  trapped surface. The 0.40c's grew exponentially into the collapse.
- **Instability curve** (`figures/instability_curve.png`, `plot_instability_curve`): τ 4.4 / 5.0 / 5.9 / 8.0 from
  the static to the 0.40c; the 0.46c went through the band (15.2) and turned back, drawn open and not fitted. The
  0.5c's 13.6 is out of order: it ran at N 192 with the sponge drive on. The fit's growth rate reaches zero at 40 %
  of extremal with it, 36 % without it.
- **Against Azad et al.** (Azad, Blázquez-Salcedo, Khoo, Kunz, arXiv:2301.05243): their second-order rate matches ours
  within 3 % at the 0.30c and 0.40c (5.9 vs 6.1, 8.0 vs 8.0); their formula zeroes at 33 % and they conjecture the
  instability ends at ≈ 30 %, where their main mode meets a second unstable mode and both should merge and vanish.
  The 0.46c's turn at 29 % fits that conjecture; the 0.5c N 192 still shrinking at 33 % does not, unless it turns
  later. Kleihaus & Kunz (2014) left 4D stability open; our 0.9c is stable.
- **End state.** The low spins collapse into a black hole: the horizon settles at R 2.52 (0.2c) and 2.57 (0.30c,
  still settling at t 100); the 0.40c's MOTS leaves the throat at t 92 and reads R 3.22 at t 100, still shrinking.
  The static died just after its horizon formed.
- **Gravitational waves.** The 0.2c's collapse emits a (2,0) burst, r·Δψ4 ≈ 2e-4: one waveform from R 14 to 45, at
  the speed of light, ring-down period ≈ 24 (the L 128 far-zone run, `figures/farzone_wave_02c.png`).
- **Larger spin, stronger wave, same shape.** Aligned on each run's own collapse (u = t − R − t₁₀, t₁₀ when R_eq is
  −10 %), the 0.2c N 128 / N 192 / L 128 overlap at R 10 / 14 / 18 (at R 14: trough −1.47e-4 at u ≈ 13, peak +2.3e-4
  at u ≈ 24). The 0.30c has the same shape and timing, bigger: its first lobe ≈ 1.5×, its R 14 trough −1.9e-4 and
  still deepening when it stops at t 100. The first lobe falls with R (near field); the trough is flat from R 14
  (the radiation). The static is flat at ≤ 3e-8 (a spherical collapse emits no quadrupole wave). No burst in the
  rest: the 0.2c N 96 and the push-out died before theirs reached R 10, the 0.40c+ collapse too late for t 100.
- **Kicks.** The sign of the push decides the fate, the merger paper's rule: pushed in, the throat inflates; pushed
  out, it collapses. Both pass 1 % at t ≈ 25, 21.5 before the unkicked 0.2c, at the same rate. No more kicks.
- **Numerics.** The 0.2c triplet converges at 3rd–4th order, the 0.9c triplet is stable at every resolution, and the
  code review (10-19) found nothing that changes these results.

## MAIN RESULTS TABLE

L 64, N 128, slow recipe unless noted. −1 %: the equatorial throat radius R_eq (`throat_geometry`; the kicks against
the unperturbed throat). τ_A: the curve's fit to the areal-radius deficit over 0.2–1 %. τ_p: the proper time on the
throat's equatorial ring (∫α dt, lapse from the slice cache) over R_eq −1 → −10 %. Azad's τ at the rungs (their C = 1
row): 5.13 / 5.46 / 6.1 / 8.0 / 13.2 (static → 0.46c), zero at J 4.03 (33 %).

| rung | J/A (% ext.) | −1 % at t | τ_A | τ_p | end | trust |
|---|---|---|---|---|---|---|
| static | 0 | 43.7 | 4.4 | 2.96 | DIED 62.67, after its horizon formed | 60 |
| 0.2c (N 96 / 192: 3.57 / 3.13 τ_p) | 12.3 | 46.9 (N 192: 57.8) | 5.0 | 3.28 | horizon R 2.524, M_MS 1.262 | 100 |
| 0.2c push out (l 0, ε +1e-3) | 12.3 | 25.3 | – | 3.03 | DIED 44.08, after its horizon formed | 42 |
| 0.2c push in (l 0, ε −1e-3) | 12.3 | +1 % at 25.6 | – | 3.06 | inflates, +105 % at t 60 | 61 |
| 0.30c | 18.3 | 51.4 | 5.9 | 3.76 | horizon R 2.571, M_MS 1.286, settling | 100 |
| 0.30c to t 130 `spin_hold_L64_ml3_ve030a_spdrv0_farfix_t130` | 18.3 | – | – | – | LIVE since 10-19 18:41 (2nd node): its whole burst (peak t ≈ 108, second trough ≈ 120 at R 14), the wave against spin | – |
| 0.40c | 24.4 | 60.2 | 8.0 | 5.03 | horizon forming: MOTS off the throat from t 92, R 3.223 (M_MS 1.612) at t 100 | 100 |
| 0.40c to t 150 `spin_hold_L64_ml3_ve040a_spdrv0_farfix_t150` | 24.4 | – | – | – | LIVE since 10-19 18:41 (2nd node): a third wave point (its burst reaches R 14 at t ≈ 115–140) | – |
| 0.46c | 28.8 | never (−0.92 % at 82) | 15.2, then turned | – | no collapse: areal −1.12 % at t 83, back to −0.21 % at t 100; MOTS on the throat | 100 |
| 0.46c to t 150 `spin_hold_L64_ml3_ve045a_spdrv0_farfix_t150` | 28.8 | – | – | – | PROPOSED (no go), ≈ 7.3 h alone: whether the 0.46c's turn is a slow swing that comes back | – |
| 0.5c (N 192, drive on) | 33.3 | 99.4 | 13.6 | – | clean t 100, MOTS −1.3 %, no horizon | 100 |
| 0.5c on N 128, drive off, to t 150 `spin_hold_L64_ml3_ve050a_spdrv0_farfix_t150` | 33.3 | – | – | – | LIVE since 10-19 19:54 (1st / 1, alone): the 0.5c like the other rungs (its N 192 / drive-on τ is out of order) | – |
| 0.6c (fast) | 40.3 | – | – | – | LIVE since 10-19 18:05 | – |
| 0.7c (fast) | 51.4 | – | – | – | LIVE since 10-19 18:19 | – |
| 0.9c (L 128 triplet, fast) | 80.8 | flat to t 150 | ∞ | – | stable: areal R drift ≤ 7e-5, no MOTS | 150 |

ψ4 (2,0), r·Δψ4 at R 14 (u as above): 0.2c trough −1.47e-4 (u 13), peak +2.3e-4 (u 24), ring-down period ≈ 24 (L 128,
flat in R to 1.3 % over R 30–45); 0.30c first lobe 1.0e-4 (0.2c 6.5e-5), trough ≤ −1.9e-4 (cut at t 100); static
≤ 3e-8.

## LIVE (MSK; no checkpoints)

| run | node / card | t | stop | speed | ETA |
|---|---|---|---|---|---|
| 0.30c to t 130 `spin_hold_L64_ml3_ve030a_spdrv0_farfix_t130` | 2nd / 0, with the 0.40c t 150 | 13.4 @ 20:09 | 130 | 9.1 t/h | 10-20 ≈ 08:50 |
| 0.40c to t 150 `spin_hold_L64_ml3_ve040a_spdrv0_farfix_t150` | 2nd / 0, with the 0.30c t 130 | 13.3 @ 20:09 | 150 | 9.1 t/h (20 alone after the 0.30c) | 10-20 ≈ 09:55 |
| 0.6c `spin_hold_L64_ml3_ve060a_spdrv0_mc4_sig04_farfix_t150` | 1st / 0, with the 0.7c | 21.0 @ 20:09 | 150 | 9.1 t/h | 10-20 ≈ 10:20 |
| 0.7c `spin_hold_L64_ml3_ve070a_spdrv0_mc4_sig04_farfix_t150` | 1st / 0, with the 0.6c | 16.7 @ 20:09 | 150 | 9.1 t/h | 10-20 ≈ 10:35 |
| 0.5c to t 150 `spin_hold_L64_ml3_ve050a_spdrv0_farfix_t150` | 1st / 1, alone | 5.0 @ 20:09 | 150 | 20.5 t/h | 10-20 ≈ 03:15 |

- Start checks passed: t 0 MOTS R 5.5367 (0.6c; table 5.5419), 6.8730 (0.7c; table 6.8795) and 4.9613 (0.5c; its
  N 192 run 4.9620), ψ4 header R 10 14 18 30, frames, keep-last pruning. Decided 10-19: the 0.7c shares card 0 now
  rather than running alone on card 1 from 19:50. Watch the 0.7c: the archived one's slicing broke at t ≈ 102 (lapse
  floor, NaN 135.85), its MOTS gone by t 49.
- Done and packed 10-19: the static, the 0.30c, both 0.2c kicks, the 0.2c N 192, the L 128 far-zone run, the 0.5c
  N 192, the 0.40c and 0.46c t 100 (19:54; their movies rendering). The first node's scratch was pruned of the 0.40c /
  0.46c last plotfiles (14 GB, ≈ 20:10).
- The 0.30c t 130 and 0.40c t 150 (go 10-19 ≈ 18:40; decided: both on the second node's card now rather than the
  0.40c alone on the first node's card 1 from 19:50) are the 0.30c / 0.40c rungs' own params with only the name and
  the stop changed (diffed); t 0 constraints and R_eq identical to the t 100 runs. The second node's scratch was
  wiped of the kicks' last plotfiles (14 GB, 10-19 ≈ 18:40).
- The 0.5c N 128 drive off to t 150 (go 10-19 ≈ 19:10, no checkpoints) started at 19:54 on the first node's card 1,
  launched by a watcher the moment the 0.40c / 0.46c t 100 exited. Template: the 0.40c t 150's params with the 0.5c
  table (diffed: against the N 192 run only N, plot_interval, drive, name and stop differ). t 150 rather than 100: the
  0.46c's throat turned at t 83, so t 100 may not show whether the 0.5c collapses.
- Queue: empty; the 0.46c to t 150 PROPOSED in the main results table, no go. Cancelled 10-19: the 0.2c bar and the
  three 0.30c kicks (both rungs collapse anyway; templates stay).

## RUNS FOR THE PAPER (proposed, no go yet)

The proposed run is the PROPOSED row of the main results table (the 0.46c to t 150).
Free analyses:

| analysis | what it settles | cost |
|---|---|---|
| two-mode refit of the 0.46c / 0.5c | Azad's second mode near the mode crossing | free |
| horizon mass integral | the 0.2c's settled M_irr 1.262 against the exterior's ≈ 1.16 | free |

## THE PAPER

Claims (decided 10-18):
1. **Stability at fast spin**: the 0.9c farfix triplet holds to t 150.
2. **Stability grows with spin**: the ladder static → 0.9c; τ(J) against Azad et al.
3. **A GW signal with no nonspherical perturbation**: the rotating collapse radiates (2,0) from unperturbed data (the
   far-zone 0.2c), more with more spin; the static radiates nothing.

Paper notes:
- **τ**: quote one definition, the areal-radius fit over 0.2–1 %. The coordinate rate depends on the throat lapse at
  the collapse (0.52–0.56), so the coordinate τ of the triplet does not converge and the proper one does. Azad's τ is
  a linear mode in Killing time: the comparison is close, not like for like.
- **Azad's numbers**: J/A from each table's meta, as a fraction of extremal Kerr's 1/(8π). Their second-order zero is
  J 4.03 = 33 % on this axis; their "≈ 50 %" uses their approximate throat area. Their ≈ 30 % end is a conjecture.
- **Physicality**: J/M² bulges mid-family (0.5c 1.19, 0.7c 1.11, 0.9c 1.013); only J/M² < 1 is astrophysical,
  v_e < 0.29c on this family.
- **Exotic matter**: D/M falls 2.22 → 1.07 → 0.52 → 0.09 → 0.02 at v_e 0.06 / 0.51 / 0.70 / 0.90 / 0.96 (family (a)
  tables): rotation replaces the phantom field as what holds the throat open. The scalar charge is measured on the
  grid (t 0 to 2e-4; the static drains D by 38 % by t 64, pre-fix: requote).
- **Speed-up research** (dt × σ, 10-16, "goes fully to the article"): the dt ceiling was an AMR interface mode on
  the coarse–fine edges, where bugs 2–3 acted; retest dt 0.05 on the fixed binary before quoting it.
- **Figures**: `instability_curve.png` (not yet cited), `farzone_wave_02c.png` (claim 3), `convergence_02c.png`,
  `convergence_09c.png`. To make: the wave against spin (the aligned R 14 waveforms above).
- **`article/research.tex` fixes** (code review 10-19): it drops a 1/η₀ in ψ (line 106), double-rounds two Table I
  digits and describes solver features the code does not have. Every evolution number is requoted from the farfix
  runs; the pre-fix numbers are archived.

## SETTINGS

- Grid: L 64, N 128, max_level 3 (dx 0.5 → 0.0625), centre 32, KO sponge 24–32, dt_multiplier 0.02. The sponge drive
  is off for every run since 10-18 (`sponge_drive_strength = 0`).
- SLOW (≤ 0.5c): σ 0.1, min_chi 1e-8, stop 100. FAST (> 0.5c): σ 0.4, min_chi 1e-4, `constraint_norms_mask_radius =
  0.75`, stop 150; the 1e-4 floor is what carries > 0.5c.
- Binary `main3d_farfix_891d817d_2026-10-17.ex` (kicks: `main3d_kick_af28ad29_2026-10-18.ex`) with
  `exact_quartic_interp = 1`, `rk_stage_refill = 0`, `shift_advec_coeff = 0`, `sommerfeld_relative_to_background = 1`,
  `constraint_norms_edge_cells = 3`.
- Consumer (`--consume-args`): the 14-field frame set (zoom 64, centre 32, slice cache, `--frames-blank-edge 2`),
  `--mots-spectral --mots-spectral-center 32 32 32 --throat-spheres --radii 10 14 18 30`, keep-last 3,
  `GRTECLYN_FRAMES_BUFF_CAP=2048`. R 14 / 18 are the trusted waves (wholly on level 1), R 10 is near field, R 30 is in
  the sponge.
- Templates carry absolute `output_path` and `spinning_background_file`; packs scrub them to repo-relative, so a
  template built from a pack must restore them (the 0.6c's first launch was refused for it).
- A rerun is its old run: the packed params plus the fix keys, diffed. Checkpoints are asked per run (none so far).
- One card does ≈ 20 t/h of L 64 N 128 however it is split (two runs ≈ 9.5 each).
- Stability protocol (Evstafyeva–Siemonsen–East, arXiv:2508.11527): a growth is physical only if its τ converges to
  a nonzero value while the finest-level constraints converge, and the areal radius or MOTS moves with it.

## DEBUGGING NOTES

- **Three numerics bugs (10-17)**, found because the per-level constraints (`constraint_norms_levels.dat`) did not
  converge: the table was interpolated bilinearly (→ C2 spline); AMReX's `cell_quartic_interp` stores its weights
  rounded to 8 decimals, so every coarse–fine ghost was 6e-8 low (→ exact weights, `exact_quartic_interp = 1`); the
  example re-filled the whole RK stage from StateData (→ `rk_stage_refill = 0`). Every earlier run is archived
  (`00_archive/superseded_2026-10-17/`).
- **Far-zone junk (10-17)**: the Γ-driver advected the rotating background shift (β·∇β = −ω²r from t 0 →
  `shift_advec_coeff = 0`); the flat-space Sommerfeld faces sat at 5.5 M (→ relative to the background); Weyl4's
  stencil reads extrapolated ghosts in the outer 2 cells (→ blanked in frames).
- **The sponge drive (10-18)** pulls the shell back to the t 0 data, which is not Einstein evolution once a pulse
  arrives: 48× more face junk. Drive off.
- **CKK's eq. (12) is wrong** (Step 2): the unimposed constraints flagged it at O(J⁴); extremal Kerr closes four
  equations to 160 digits and leaves a residue in eq. (12) alone.
- **Above 0.5c**: with min_chi 1e-8 the 0.7c died at the far-side puncture (t 42.6, floored from t 2.3); σ ≥ 0.2 kills
  that puncture on the 1e-8 floor; dt 0.05 has a K instability on spin data that σ 0.4 + floor only delay. So: floor
  1e-4 on the fast runs, dt 0.02 everywhere.
- **Measuring the throat**: never quote R_pol_min (coordinate-dependent). `throat_geometry` reads the box edge once the
  throat leaves the finest box (the push-in after t 61.4): use `throat_spheres` there; it reads small deficits ≈ 20 %
  high. The MOTS stream is the most accurate (3e-6). ψ4 has no matter term (`G_newton` unset → 0): ≤ 0.4 % at
  R ≥ 30, up to 17 % at R 10.
- **Consumer cost**: the spectral MOTS search grows as N³ when it finds nothing (the 0.9c N 192: 22 min a plotfile
  against one every 12) → `restart_consumer.sh <run> --mots-spectral-steps 150` (`--busy`).
- **Collapse deaths**: a NaN in h11 on level 3 after the horizon forms is the collapse's end, not a failure (static,
  0.2c N 96, push-out); trust ends at the χ floor.

## OPEN

- Horizon mass budget: the settled 0.2c horizon (M_irr 1.262) is heavier than the exterior mass fitted from χ at
  r 26–58 (≈ 1.16 at t 150). Settle it with a mass integral before quoting a horizon mass.
- Level 0's box face (Sommerfeld on a non-flat background); dt 0.05 / σ on the fixed binary; waveform extrapolation
  in 1/R; the upstream AMReX PR for the rounded weights; the RK re-fill in the merger, RadialRecipe and
  SupportedWormholeCollapse examples (their campaigns' call).
- The 0.9c polar radius grows 1e-3 after t 110 at every N (coordinates: the areal radius is flat).
- Older numbers that did not reproduce in the code review: the 0.9c minimum orders, the troughs' flatness in R, the
  N 192 ring lapse (0.508, not 0.529), the order of the proper τ (≈ 2, not 3).

## DECISIONS

- 10-13: every quoted run is a triplet member or licensed by one; per-level masked constraint norms in every run.
- 10-15: the paper is the drainhole's alone. Campaign A (family (b) evolutions) dropped: every hold died at its
  far-side positive-mass puncture at t ≈ 23, whatever the numerics.
- 10-16: two recipes (slow ≤ 0.5c, fast above), dt 0.02.
- 10-17: the numerics and far-zone fixes; every paper run reran on them.
- 10-18: the drive off for new runs; the kick is the merger's conformal-factor shell, momentum-exact, no constraint
  solve; the 0.9c kicks dropped (far from physical spins).
- 10-19: no kicks beyond the 0.2c pair; the 0.6c / 0.7c threshold rungs added (J/M² peaks at the 0.5c, so the fast
  end is not the unphysical one); τ is the areal-radius fit over 0.2–1 %.

## DONE BEFORE THE FIXES

Step 0 (10-11): the static hold twins the merger's `single_hold`. Step 1 (10-12): the O(J²) holds' push was the
data's error (∝ J⁴). Step 2 (10-13): the full solver, both families to v_e 0.99, tables in `runs/spinning_p3/tables/`
(≤ 1e-7 to v_e 0.9). Step 3 (10-13 → 10-15): t 0 checks, the L 64 holds, the A1 ladder (the 3D ADM mass equals the
table's to 1e-12). Assets: B1's Chk10000 in its `nfs_chk/`; `fam_a_ve020.spinbg` (a J = 1 cross-check).

## RULES

CLAUDE.md's launch discipline: go first, checkpoints asked per run, full frame set, STATUS pushed at every launch,
stop or wipe. ψ4 radii 10 / 14 / 18 / 30 on every spinning launch.
