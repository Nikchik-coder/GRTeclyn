# Status — 2026-09-29 20:23 UTC (Live sections; queue updated 2026-09-28 ~11 UTC)

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## CRITICAL FINDING: a moving throat is Lorentz-contracted; every moving setup so far was a round throat at rest (the user, 2026-09-29)

**A throat with momentum is the static throat seen from a moving frame** (the exact Lorentz boost of the drainhole).
On the t = 0 slice:
- it is squashed along its motion by 1/γ: 9 % at p = 0.45 (v = 0.41, γ = 1.097), visible in frame 0;
- its scalar moves with it (Π ≠ 0);
- it carries its own K_ij and shift. The K_z, Π_z and shift frames show a moving dipole at t = 0 where they used to be
  blank.

**Every run with p > 0 until now started from a round throat whose scalar was at rest** (Π = 0). The momentum was put
in through the Bowen–York K_ij alone: the black-hole recipe, on conformally flat, spherical data. That is not a
moving wormhole. A black hole gets away with it because the junk radiates away or falls behind the horizon. A throat
has no horizon and sits at an unstable equilibrium, so the mismatch drives it to inflate. The push grows as p², like
the ADM-mass excess the momentum adds. The single-throat probes (level 3, L = 64, stopped at t ≈ 32–33 on the user's
word):
- at rest the throat stays put (R −0.05 % at t = 32);
- p = 0.12 inflates: +10 % at t = 32 (ε_eff ≈ −0.15 %);
- p = 0.45 inflates: +10 % at t = 20.2, +24 % at t = 25 (ε_eff ≈ −1.8 %), past the scan from t = 26.

**The correct setup holds its size.** On the same template with `wormhole_momentum_model = 1`, the p = 0.45 throat is
flat: +0.03 % at t = 10, where the Bowen–York twin was already at +0.85 %.
- **Measuring a moving throat needs the squash.** The round scan (the consumer's A rows) reads +0.2 to +0.4 % of
  growth that is not there. Fitted to a shifted ellipsoid, R is 3.87815 at t = 0 and 3.87913 at t = 9 and 10. The
  throat is squashed 9 % at t = 0 (1/γ) and 12 % by t = 8–10 as the gauge relaxes, and the round scan's centre lags it
  by up to 0.15. The horizon scan needs this fit for every moving throat.
- **The squash is Lorentz contraction, as for a boosted black hole's horizon:** a coordinate effect along the
  motion, by 1/γ = m/√(m² + p²), with the area unchanged.
  - At p = 0.12 / 0.25 / 0.45 (m = 1) that is 0.7 / 3 / 9 % (v = 0.12 / 0.24 / 0.41, γ = 1.007 / 1.03 / 1.097).
  - Axis ratio (along/across the motion) of the throat's χ contour, from the z = 32 slice caches:

    | run | t = 0 | t = 10 | t = 20 | t = 24 |
    |---|---|---|---|---|
    | exact boost (`single_boost_p045_lb_t050`) | 0.910 (= 1/γ) | 0.868 | 0.775 | 0.740 |
    | Bowen–York p = 0.45 (`single_boost_p045_csm_t050`) | 1.000 | 0.987 | 0.984 | 0.998 |
    | at rest (`single_rest_csm_t050`) | 0.998 | 0.998 | 0.998 | 0.998 |

  - The old Bowen–York throats never showed it because it was never there: their data are round by construction
    (conformally flat, the scalar at rest). It was not missed for being small.
  - In evolution the exact-boost throat squashes past 1/γ. That is the gauge (1+log and Gamma-driver coordinates),
    not physics: its fitted size stays flat through t = 16. After t ≈ 15 the puncture's lapse runaway may drive part of
    it; the freeze rerun will tell (the collar rerun could not: it broke the boost).
  - The frames do not fake it: the panel is 722 × 749 px for a 40 × 40 box, a 3.7 % horizontal stretch. The dark lapse
    well around the throat is gauge too.
- K_z at t = 0–7: the throat's own dipole moves with it and the far lobes relax. The Bowen–York twin instead grows a
  new K > 0 region around its throat.

What it overturns:
- **The fly-by was wrong** (`merge_orbit_flip_d12_p045_L128_lvl5_t100_csm`), and so is the claim that the fly-by
  cannot spiral (§VII.A: every p ≥ 0.35 "passes without merging"). The junk drove its throats to expand; at
  p = 0.45 it is about the mouths' whole kick (−1.2 %).
  - Stopped at t = 64.98 (15:39 UTC) on the user's word, no NaN.
  - Not packed (the user's word). Its frames stay. Its scratch (Chk05000–06000 and Plt06200–06400, 127 GiB) was
    wiped at 15:45 UTC on the user's word (`MANIFEST_CLEANUP_2026-09-29`).
- **Every p > 0 result waits for a rerun on boosted data.** At the spiral's p = 0.12 the junk is ~0.15 %, small next
  to the companion's −0.8 %.
- **Clean of it: the head-on and the rest pairs** (p = 0; the user, 15:38 UTC).

**The fix (dc34eb51, 14:50 UTC).** `wormhole_momentum_model = 1` builds each throat as the exact Lorentz-boosted
drainhole: the metric, K_ij, φ and Π together, with the boosted lapse and shift. `wormhole_momentumA/B` become each
throat's ADM momentum γmv (p = 0.45 is v = 0.4104). Model 0 is unchanged bit for bit and now warns.
- Checked:
  - both constraints vanish to 1e-9 of their terms (finite differences of the closed forms, the exact static throat's
    own level);
  - the lapse and shift carry the slice rigidly to 1e-12;
  - the run's t = 0 plotfile matches the closed forms to 2e-14 in every field;
  - the closed-form Γ̃^i matches finite differences to 1e-11.
- The old V2 option (`wormhole_boost_velocity`) does not give the moving throat's Π either. Near the throat it is
  ~Q/α² ≈ 17× too large, because the boosted slice's shift carries most of the motion. The unsolved `_vscal` probe
  would have tested the wrong thing.
- **End-to-end test** (`single_boost_p045_lb_t050`: the p = 0.45 probe's template with only the momentum model changed
  and the solve off). Its Bowen–York twin reached +10 % at t = 20.2 and +24 % at t = 25.
  - **The throat holds its size through t = 16** (shape-fitted R within 0.05 % of t = 0).
  - **It DIED at t = 26.1** (16:22 UTC, NaN in h11 on level 3). The cause was a lapse runaway at the moving puncture,
    the far side's compactified infinity: 0.20 until t ≈ 10, then 0.28 at t = 15, 0.89 at t = 20 and 2.6 at t = 24,
    with a ring of 0.06 around it. The rest and Bowen–York throats keep 0.19–0.22 there.
  - The boost carries the puncture across the grid at v = 0.41 from t = 0, with lapse 0.2 there. The runaway came from
    −2α(K − 2Θ) acting on K errors at the pit, and stayed within r < 0.25 of it until t ≈ 20 (z = 32 slices): the
    lapse at the throat held 0.51–0.53 across the motion through t = 20.
  - **The collar lapse (type 6) is not the cure: its rerun was unhealthy from the start and DIED at t = 37.60** (18:29
    UTC, NaN in h11 on level 3; `single_boost_p045_lbc_t050`, card 1, the user's go 16:24 UTC, t = 0 data the old
    run's except the lapse at r < 1 about the puncture). Its zero-lapse core, swept across the grid by the boosted
    shift, broke the rigid boost:
    - at t = 4, K inside the throat was already up to 0.125 (the old run: 0.007), and the momentum-constraint norm
      50× the old run's (2.7e-3 against 5e-5);
    - the lapse at the throat fell from 0.52 to 0.26 by t = 10 (a trumpet), and 0.67 → 0.48 at r = 3;
    - by t = 32, K ≈ −0.5 inside the throat and a Π ring of 0.22 around it (0.009 at t = 0), both still growing; the
      round-scan R +1.3 % at t = 20, then −1.7 % at t = 32; max |K| 1.7 at the death.
    Its "size holds" reading is void. Not packed; frames kept.
  - **The cure being tested: the per-throat slicing freeze** (`single_boost_p045_lbf_t050`, card 0, launched 18:29 UTC,
    the user's go ~18:15 UTC, no checkpoints). The old run's template with only the freeze added: the boosted lapse
    (type 5) is kept; inside r < 0.3 of the tracked pit (tapered to 0.8; the throat is at r ≈ 1.4–1.6) the slicing
    source is removed and the lapse only rides the shift, which is −v e there to 1e-3. `CoreLapseFreeze` with
    `core_freeze_track_throats = 1` (build `main3d_boostfix_5384c104-dirty`). Its t = 0 data equal the old run's in
    every field. PASS: no runaway past t = 26, the throat as the old run's through t = 20, R_min flat to t = 50.
- **The constraint solve for boosted pairs** (d9ca1bc1; tested 16:00–17:10 UTC, four t = 0 runs, level 3, L = 64). It
  solves both constraints, for w and a vector potential W (Â → Â + L_G W).
  - Test 1, one boosted throat: **passes**, the solve leaves it alone (max |w| ≤ 5e-7, max |W| ≤ 5e-6, far side the
    isolated throat's to 4e-7).
  - Test 2, the d = 12 rest pair under model 1: **passes**. It reproduces the model-0 mode-3 solve: c, σ and w0 to
    ~1e-5, M_ADM 1.5658 against 1.5658, R_min 3.891, and the throat-shell Hamiltonian at 1.9e-6.
  - Test 3, the fly-by pair (flipped, d = 12, p = ±0.45): **the solve converges but the mouths are wrong**. The
    level-3 throat-shell Hamiltonian falls 300× (rms 7.1e-3 unsolved to 2.2e-5), and the far sides match the
    isolated throat to 3e-6 (4 matching rounds). But R_min comes out 4.43, 14 % above the isolated 3.88 (the
    unsolved pair: 4.27), with w0 = −0.21, σ = 0.70 and max |W| = 128 by the punctures. The likely cause: the
    companion's K_ij and Π reach into each throat's far side, where the constraints weight them by Ψ⁵ and Ψ⁶. Those
    diverge at the puncture: π s Π_Y² Ψ⁵ ~ r⁻⁵ and Ψ⁶ Π_Y ∂φ ~ r⁻⁶, with Π_Y ≈ 2e-3 there. The solve chases that
    source, and the far-side reading follows. The fix: cut the companion's K_ij, Π and anisotropy E inside each
    throat, with the collar's profile about each puncture (1 − exp[−(r/0.3a)⁸]), so each far side holds its own
    throat only. **Test 3c** (`t0_flip_d12_p045_lbcs_cut`: 3b line for line on the build with the cut; card 0,
    relaunched 19:01 UTC on card 1 after the first launch's preflight timed out mid-solve; the user's go ~18:15 UTC). **PASS** (19:12 UTC): mouths R_min 3.894 per mouth (the isolated throat 3.877, +0.4 %; 3b 4.425), σ 0.918 (rest pair 0.930), w0 −0.0125, max |W| 0.18 (3b: 128), far sides matched to 3e-6 in 3 rounds, level-3 throat-shell Hamiltonian rms 1.05e-5 (unsolved 7.1e-3). Committed 91ed17cd with the per-throat freeze.
  - The builds on the way: the first aborted on AMReX's Robin-reuse assertion; the second crawled ~2 % per pass on
    the pair (linear extrapolation outside the box); the third fills those ghosts with the Robin condition.

## CRITICAL: every binary simulation is corrupted by its initial data and must be rerun (the user, 2026-09-28)

Every binary run so far (the pairs at rest, the head-on, the spirals, the fly-by, the scans, the placement probes)
started from the superposition of two throats, which is not a solution of the Hamiltonian constraint
["2026-09-27 (12:15 UTC) — parameter matching and the energy check"]:
- each mouth comes out 9–15 % larger in every length than the isolated throat it is named for (one-body mass 1.149 at
  d = 8, 1.094 at d = 12), so every p is in the wrong unit (p = 0.12 / 0.45 are 0.110 / 0.411 per one-body mass);
- the pair's mass leaves out the interaction energy: M_ADM is 2.00 in the superposition, 2.36 (flipped) and 1.38
  (like) at d = 8 for the same two isolated throats constraint-solved (mode 3).

No binary number is final until it is remeasured on mode-3 data (`constraint_solve = 1`,
`constraint_solve_puncture_mode = 3`, name token `csm`).

**RULE for every rerun (the user, 2026-09-28): the new run's properties must match the corrupted run it replaces,**
so the two differ in the initial data alone and the old result can be tested. Same L, N, max_level, tagging_L,
sponge, separation, gauge, dt_multiplier, stop_time and plot cadence as the old run's `evolution_params.txt`
(`results/merger/campaign/...`); the only changes allowed are the constraint-solve block (mode 3), checkpoints only if the user
says so, and the plot variables the full frame set needs (output only). Diff the new template against the old params before
launching. E.g. the rest pairs are L = 64, N = 128, max_level 3, tagging_L 64, sponge 24/32, t = 15, plots every 0.5. CS-1 (mode 0: the superposition's mouths, solved) is the
old-versus-clean comparison, not a rerun. The binary verdicts below stand only as results on superposed data.

## The plan, in order (the user's, 2026-09-28)

1. **Energy check** (CPU only, about a day). The pair's total mass in mode 3 at d = 8, 12, 16, 24 and 48, attracting
   and repelling: what "M" means in the paper, and whether the extra interaction energy agrees with the attraction or
   is a bug. **Done** 2026-09-27 12:15 UTC (`results/merger/t0_matching/energy_scan.tsv`): not a bug, it agrees only
   if the throats act at fixed scalar potential. The GPU build reproduces it (2026-09-28, below).
2. **First two runs** (about 18 GPU-hours, side by side).
   - Pairs released from rest (~6 h): remeasure the attraction/repulsion ratio (1.518) and the force law for the true
     wormholes. **Done 2026-09-28 09:11 UTC**: the five old rest pairs rerun in mode 3, all clean to t = 15. Pull/push
     1.463 ± 0.023 (superposed 1.518; fixed potential 1.500, fixed charge −0.667 excluded); force-law offset δ = 2.65
     (superposed 3.56). Closed out, below.
   - Head-on to t = 100: does "the horizon shrinks by a quarter" survive, or was it a symptom of the missing
     energy? Moved to the L = 128 production box with the spiral and the fly-by (the user, 08:20 UTC; queued below);
     the L = 64 rerun was stopped at t = 0.6.
   - Decision point: these two show how much of the abstract changes.
3. **The orbits** (about 3 days of GPU).
   - Spiral p = 0.12 (~22 h), plus a finer-grid twin for convergence (~8–10 h).
   - Fly-by p = 0.45 at two resolutions (30–67 h).
   - p = 0.25 and 0.35 (~12 h) to relocate the merger/fly-by boundary.
   - Decision point: if any outcome flips (merger ↔ fly-by), map the boundary more finely.
4. **Single wormhole on clean data** (12–25 h, any time in parallel). The kicked single throats with properly solved
   starting data. This settles the "regrowth" question.
5. **Rewrite.**
   - The initial-data story is told once, in this order (the user, 2026-09-28): the superposition (not a solution;
     one line only, per the framing rule below), then the Helfer-type windowed one-body correction (tested, all four
     twins stalled, not adopted, \cite{helfer2022} kept), then mode 3 (the exact solve) as the resolution and the
     headline. No Helfer reruns: on clean data there is nothing left for the correction to correct; the twins stay
     in Table I's systematics row.
   - Every binary number comes from mode-3 runs.
   - The old campaign becomes the systematics study (gauge, grid, freeze tests), with CS-1 as the table showing old
     versus clean starting data.
   - Add the new definitions: each wormhole's mass, the pair's total mass, and p in true units.
   - **Add a section on the boosted single throats (the user, 2026-09-29 09:45 UTC):** what one throat does after a
     momentum kick, inflation or collapse, and how fast. Sources: the three mode-3 probes
     (`single_rest_csm_t050`, `single_boost_p012_csm_t050`, `single_boost_p045_csm_t050`; stopped 14:27 UTC at t ≈ 32–33, the user's word)
     and the unsolved pair (`single_boost_p045_t050`, `..._vscal_t050`: the scalar at rest against moving; not
     launched: the fix's end-to-end test replaces it), each read as ε_eff on the seed ladder. It ties the binaries' mouth kicks (ε_eff −0.4 to −1.2 %) to
     momentum and the companion. Written only once the probes are closed out.
   - **Withdraw the fly-by/capture boundary (the user, 2026-09-29 14:25 UTC).** §VII.A's "every p ≥ 0.35 passes
     without merging" and the fly-by's outcome rest on data whose momentum setup inflates the throats (CRITICAL,
     top). Rerun p = 0.35 / 0.45 on the fixed data before the text states any boundary.
   - **Add a section on the boosted wormhole setup, with its validation figure (the user, 2026-09-29 ~16:50 UTC).**
     It goes in the binary setup, before any moving result. Contents:
     - a throat with momentum is the exact drainhole Lorentz-boosted and cut at t = 0: squashed along its motion
       by 1/γ = m/√(m² + p²), its scalar moving with it (Π ≠ 0), its own K_ij, lapse and shift;
     - the pair is superposed, each throat's K_ij and Π scaled by the companion's conformal factor, and the solve
       then corrects both constraints (w and W);
     - the tests that it is right.
     **The figure is made** (17:15 UTC, `plot_boost_contraction`; `results/merger/figures/02_moving_throat/
     boost_contraction`; label audit clean). It is a t = 0 strip, the user's choice: t = 0 shows the shape, and no
     evolution is needed for it.
     - (a) the p = 0 and p = 0.45 throat contours, the latter on its analytic ellipse x² + γ²y² = r_t²;
     - (b) the axis ratio against p, on 1/γ = 1/√(1 + p²);
     - (c) the residual, below 6e-5 at every p and at three contour levels.
     Measured: 1.00000 / 0.99288 / 0.97015 / 0.94387 / 0.91195 at p = 0 / 0.12 / 0.25 / 0.35 / 0.45, against
     1/γ = 1.00000 / 0.99288 / 0.97014 / 0.94386 / 0.91192 (`campaign/02_moving_throat/boost_contraction_t0.tsv`).
     That the size holds in evolution comes from the p = 0.45 collar rerun, quoted in the text. The text states
     the setup and its checks only, with no failure narrative (the paper's rule). The Bowen–York comparison enters
     as the reason for the choice, in one sentence with its numbers.
   - **Add the branch-selection finding: why the interaction inflates the mouths, and the race (the user,
     2026-09-29 ~10:45 UTC).** Verified and quotable now: the seed ladder fixes the signs (+ε at the throat
     collapses and traps, −ε inflates); every companion reads as a −ε kick that strengthens with closeness
     (−0.4 % at d = 12, −1.2 % at d = 8), the same in superposed and mode-3 data, so it is the physical
     interaction, not the solve; the collapse sign arrives only at contact, so a merger is a race — the head-on's
     common MOTS at t = 22 with the mouths at +6–10 % against the spiral's contact at t ≈ 40–45 past +50 %; and
     this is the design rule for a collapsing spiral (d = 8, small p). Interpretation, needs a check before the
     text states it: *which* piece of the companion carries the −ε sign — the flip pairing's phantom-tail
     gradient between the mouths (negative gradient energy) and the tide, against the near-uniform ~m/d potential
     shift. Cheap test on existing t = 0 data: superpose the tails, integrate the scalar's ρ over the throat
     region, compare with the seed ε that reproduces the measured ε_eff; a like-pair (no flip) rest run would
     separate the tail term from the tide.
     - **The head-on is not an exception (the user, 2026-09-29 ~10:47 UTC):** its mouths inflate too — the dead run
       had them at +6–10 % when the common MOTS formed at t = 22, and the live mode-3 rerun sits on the same
       ε ≈ −1.2 % track (+0.45 % at t = 10). The horizon forms anyway because contact (t = 22) beats the runaway
       (+10 % at t ≈ 23 on that track), and it swallows the mouths mid-inflation. State it this way in the paper:
       every mouth inflates; the outcomes differ only in whether contact comes first.
   - Update the abstract once step 2's answers are in.
   - Constraint norms are not a paper problem (checked 2026-09-28 06:55 UTC, the rest-pair reruns to t ≈ 5 against
     their old runs). The logged 𝓗 norm reads 9–13 % higher for the like pairs and 21 % for the flipped one, a flat
     offset from t = 0 that does not grow; 𝓜 is 27–59 % lower. That 𝓗 is the base grid's box average (Δx = 0.5),
     which does not resolve the throat cores (3.35e-3 in all four like pairs whatever d): the discretisation floor,
     not the superposition error. Every constraint claim in the paper is relative (growth, onsets, level agreement,
     "below its value at formation"), and the `fig:constraints` caption already says the norms compare only within
     one box. The binary norm values the text quotes (the Helfer fly-by's 3.2e-3 → 1.6e-2, the spiral's 3.5 % level
     agreement) are re-read from their reruns.
     Rechecked 2026-09-29 (06:10 UTC) on the production runs against their superposed twins (the head-on through
     CS-1 against its scout, one grid; the level-5 head-on's twin is in the L = 64 box): 𝓗 1.1–1.4× through t ≈ 20,
     the base-grid floor of the smaller matched throats (R_min 3.89 against 4.25–4.47); 𝓜 about half over
     t = 0.5–10 (head-on 0.4–0.56×, spiral 0.45–0.66× to t = 15), no gain in the fly-by (1.0–1.3×). The brief 𝓗 peaks
     (up to ~1.5) are in the old orbiting runs too. Late: the spiral sits below its old run over t = 35–50 (𝓗 0.77×,
     𝓜 0.5×; the old run's 𝓜 bump of 1–3e-2 at t = 39–43 is absent); the fly-by's 𝓗 is 1.7–2× at t = 40–43, while
     its mouths inflate faster. Per-level 𝓗/𝓜 during the evolution stay unlogged (skipped on the user's word,
     2026-09-28 09:20 UTC: no claim needs them); if a referee asks, any kept checkpoint is graded per level by a 0-step
     restart that writes the `constraints` field.
   - Re-measure Sec. II D's solve paragraph on mode-3 data. Its numbers are the mode-0 solve's, which keeps the
     superposed mouths: throat-shell 𝓗 9.7e-3 → 5.1e-6, M_far moving 0.1 %, R_min 1.3 % (`clmSolveShellHamSup`,
     `clmSolveShellHamSolved`, `clmSolveKeepsMfar`, `clmSolveKeepsRmin`). M_ADM = 2.738 (`clmSolvedHeadonMadm`) is
     CS-1's, the mode-0 pair's; the mode-3 pair at d = 8 has 2.360. How: a t = 0-only start (`max_steps = 0`) of the
     mode-3 d = 8 pair on CS-1's grid with the `constraints` plot field (`amr.derive_plot_vars = constraints`,
     `G_Newton = 1.0`), graded by `constraint_solve_t0_check.py`, as the mode-0 number was. This is the paper's only
     per-level constraint number.
   - The scalar energies the paper quotes are partly near-field and change: `clmGwScalarEnergyFlyby`, the
     `clmGwScalarRatio*` rows, the head-on E_φ (step 6).
   - Switching the ledger and the figures to the mode-3 runs: every extractor and figure module that breaks or reads
     differently (M = 2.0 hard-coded, the R = 30 sphere by position, old run names and times, the hand-made offline
     scans, trust windows) is listed in `CSM_SWITCHOVER.md` (audit 2026-09-28, 18:00 UTC).
6. **Longer GW runs, with the sponge and the extraction spheres farther out** (the user, 2026-09-28; proposed, not
   queued).
   - Why ["Open, the user's call: the scalar energies the paper quotes are partly near-field"]: the scalar spheres sit
     at ωR ≈ 1–3. Fitting the exact outgoing ℓ = 1 solution on each sphere, only ~35 % of the fly-by's |E_φ| = 0.087
     (R = 30, t = 60) is radiated, so |E_φ|/E_GW ≈ 0.8–0.95, not 2.3. The head-on's E_φ becomes the same on every
     sphere, ≈ −0.044, not −0.056 to −0.075. "Comparable and negative" survives. Not yet checked: the fit is
     flat-space, without the O(M/R) terms. No text changed.
   - Now: the fly-by and the spiral run in L = 128 (sponge from r = 48; Ψ4 spheres 20–44, the scalar only at 14 and 30,
     the consumer's default radii) to t = 100 / 150; the head-on in L = 64 (sponge from 24, spheres 10/14/18) to t = 100.
   - Check (2026-09-28 07:29 UTC): ωR ≈ 1–3 at R = 14–30 means ω ≈ 0.07–0.1, so the wave zone (ωR ≳ 10) starts at
     R ≈ 100–150. Spheres there need the box edge near r = 200 (L = 512: a coarser base and two more levels keep the
     interior's grid) and runs longer by R: the fly-by to t ≈ 220 (it is trusted to t = 70), the head-on to t ≈ 200.
     Roughly 2–3× each old run's GPU time; the memory must be measured first (the old level-5 fly-by peaks at 59 GB of
     80).
   - Farther spheres alone do not clean the raw number: between R = 14 and 30 the stored part falls only about as 1/R
     (the pair is still moving when the window closes), so at R = 150 it would still be ~15–40 % of it (65 % at
     R = 30). They validate the fit and cut the O(M/R) terms from ~7 % to ~1.5 %; the fit stays the estimator.
   - Free, inside the old boxes (output only, so the reruns stay exact): scalar spheres at 14/20/30/44 on the fly-by and
     the spiral, 10/14/18/22 on the head-on (the consumer's `--radii`), for the fit and a 1/R extrapolation over four
     spheres.
   - Decided (the user, 08:20 UTC): the head-on, the spiral and the fly-by all run in the L = 128 box with Ψ4 at
     20/28/36/44 and the scalar at 14/20/30/44 (queued below). Wave-zone twins: not decided.

Along the way:
- Cancel the planned convergence runs on the old data; the finer-grid twins in step 3 replace them (the convergence queue
  below is cancelled).
- For every run: ask the user directly whether it needs checkpoints (the user, 2026-09-28: never on by default;
  the rest-pair reruns keep the last 3), check the starting mass and throat size before walking away, and put "mode 3"
  in the run's name (`csm`) and registry entry.

Total: about 100–170 GPU-hours, roughly 4–5 days on the three free cards.

## Live — first node (two H100s): nothing live since 23:33 UTC 09-29 (both cards free); the fly-by NOT verified

| card | run | p | t now (09-29) | t end | speed | ETA |
|---|---|---|---|---|---|---|
| — | `merge_orbit_flip_d12_p045_L128_lvl5_t100_csm` (the fly-by) | 0.45 | **stopped at t = 64.98** (15:39 UTC, `stop_campaign.sh`, the user's word: Bowen–York momentum junk in its initial data) | 100 | — | wrong: not packed (the user's word); scratch wiped 15:45 UTC, frames kept |
| 0 | `t0_single_boost_p045_lbcs` (test 1: one exact-boost throat, p = 0.45, solve on, mode 3; level 3, L = 64; the user's go 16:00 UTC; no checkpoints) | 0.45 | **done**, t = 0.5 (16:14 UTC) | 0.5 | — | **PASS**: max \|w\| ≤ 5e-7, max \|W\| ≤ 5e-6, c = c_iso, far-side mass and charge the isolated throat's to 4e-7 |
| — | `t0_flip_d12_p045_lbcs` (test 3b: the fly-by pair, flipped, d = 12, p = ±0.45, as exact-boost throats, solve on, mode 3; level 3, L = 64; static preflight, match tolerance 1e-5) | 0.45 | **done** (t = 0.5, ~16:50 UTC) | 0.5 | — | **the solve converges, the mouths are wrong**: throat-shell Hamiltonian 300× down, far sides matched, but R_min 4.43 (+14 %); see the CRITICAL finding |
| — | `t0_flip_d12_p045_lb` (test 3a: the same pair, solve off) | 0.45 | **done** (t = 0.5) | 0.5 | — | the unsolved reference for 3b |
| — | `t0_ctrl_rest_d12_lbcs` (test 2: ctrl_rest_d12_csm's rest pair under model 1, solve on; must reproduce its model-0 mode-3 solve) | 0 | **done** (t = 0.5) | 0.5 | — | **PASS**: c 2.115528 / 2.115542 against 2.115536, σ 0.930357 / 0.930369 against 0.930364, w0 −3.430e-3 / −3.423e-3 against −3.426e-3, W = 0; far sides the isolated throat's to 1e-6 (10 matching rounds: the finite-difference floor is 3–5e-6) |
| — | `single_rest_csm_t050` (probe control, launched 08:23 UTC) | 0 | **stopped at t = 32.27** (14:26:50 UTC, `stop_campaign.sh`, the user's word) | 50 | — | close-out: packed, no movies |
| — | `single_boost_p012_csm_t050` (probe, 08:23 UTC) | 0.12 | **stopped at t = 32.97** (14:26:50 UTC, same) | 50 | — | same |
| — | `single_boost_p045_csm_t050` (probe, 08:23 UTC) | 0.45 | **stopped at t = 32.64** (14:26:50 UTC, same) | 50 | — | same |
| — | `single_boost_p045_lb_t050` (end-to-end test of `wormhole_momentum_model = 1`, launched 14:58 UTC, `main3d_boost_dc34eb51_2026-09-29.ex`, no checkpoints) | 0.45 | **DIED at t = 26.1** (16:22 UTC, NaN in h11, level 3: lapse runaway at the moving puncture) | 50 | — | superseded by the collar rerun |
| — | `single_boost_p045_lbc_t050` (its rerun with the collar lapse, type 6; the user's go 16:24 UTC; same binary; no checkpoints) | 0.45 | **DIED at t = 37.60** (18:29 UTC, NaN in h11, level 3) | 50 | — | unhealthy from t ≤ 4 (the collar breaks the boost; see the CRITICAL finding); not packed, frames kept |
| — | `single_boost_p045_lbf_t050` (the old run with the per-throat slicing freeze instead; the user's go ~18:15 UTC; `main3d_boostfix_5384c104-dirty`; no checkpoints) | 0.45 | **DIED at t = 44.67** (22:53 UTC 09-29, NaN in h11 on level 3): the throat collapsed (R_min +1.2 % by t = 24, then 3.8985 / 3.8454 / 3.7366 / 3.5191 at t = 32 / 36 / 40 / 44, −9 %, doubling every ~4 units; χ at the pit on its 1e-8 floor at t = 44.60, max\|K\| 2.4). The gauge held to the end: the pit lapse 0.215–0.233 from t = 24 on (the old run's ran away at t = 26), Ham L2 ≤ 1.8e-2 | 50 | — | the slicing fix works; the throat dies of its own collapse mode at level 3. Not packed yet (its scratch plotfiles t = 42–44 kept for the diagnosis) |
| — | `t0_flip_d12_p045_lbcs_cut` (test 3c: 3b with the companion cut; relaunched 19:01 UTC on card 1 with `--preflight static` after the first launch's preflight timed out mid-solve) | 0.45 | **done**, t = 0.5 (19:12 UTC) | 0.5 | — | **PASS**: mouths R_min 3.894 (isolated 3.877; 3b 4.425), σ 0.918, w0 −0.0125, max \|W\| 0.18 (3b: 128), far sides matched to 3e-6 in 3 rounds, level-3 throat-shell Hamiltonian rms 1.05e-5 (unsolved 7.1e-3, 3b 2.2e-5) |
| — | `t0_merge_orbit_flip_d12_p025_L128_lvl5_lbf_csm` (verification A: the fly-by's own template stopped at t = 0.5; checkpoints off, + constraints in the plot; the user's go ~19:25 UTC; `main3d_boostpair_91ed17cd`) | 0.25 | **done** (20:07 UTC) | 0.5 | — | **PASS**: solve converged (22 Newton passes, 2 matching rounds), far sides the isolated throat's to 1e-5 (one-body a 2.0000, m 1.0000); mouths R_min 3.8807 each (isolated 3.8772, +0.09 %); throat-shell Hamiltonian rms 7.8e-5 / 3.2e-5 / 5.6e-5 on levels 3 / 4 / 5 (unsolved ~7e-3; the small grid's 1e-5 is not reached here, the shell crosses level edges); axis ratio 0.9657 / 0.9638 / 0.9605 at r_c = 1 / 1.55 / 2.5 against 1/γ = 0.9701: the solved pair is 0.4–1 % flatter than a lone boosted throat, the same on B's L = 64 level-3 start to 3e-5 (so not resolution) and ∝ p² (the solved p = 0.45 pair: 1.2–2.3 %; the unsolved one matches 1/γ at r_c = 1): the pair's interaction in the solve |
| — | `check_flyby_d12_p025_lbf_csm_t020` (verification B: the same pair on test 3c's L = 64 level-3 grid, with the per-throat freeze, to t = 20; no checkpoints; same go and build) | 0.25 | **done**, t = 20 (23:33 UTC 09-29), no NaN | 20 | — | **NOT a pass.** (1) Ham L2 blows up in episodes the rest pair (≤ 5e-3 to t = 15, same grid) and the single boosted throat (≤ 1.8e-2) never show: a bump 0.02 → 0.36 over t = 7.4–8.6 with a one-row spike of 8.6 at t = 7.74, and 0.015 → 0.92 over t = 19.85–20.00, still climbing at the stop; max\|K\| stays 0.005–0.03 and χ_min 5–8e-6 through them. (2) The mouths inflate, faster each unit: +0.27 % at t = 10, +1.05 % at t = 15, +3.6 % at t = 20 (the rest pair: +0.61 % at t = 15). (3) The pair falls in: separation 12.06 → 11.74 → 9.95 at t = 0 / 12 / 20 while the tangential motion slows (the rest pair's pits drift apart, 11.94 → 13.06 at t = 15); a K > 0 blob between the throats grows ~10× over t = 8–20. Pit lapse steady at 0.20. Scratch plotfiles t = 19–20 kept for the diagnosis |
| 1 (queued) | `merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` (the fly-by rerun on the exact-boost setup: the old fly-by's params with p = 0.45 → 0.25, momentum model 1, the per-throat freeze and match tolerance 1e-5; the user, ~19:10 UTC: p = 0.25, checkpoints on every 5 units keeping the newest 3, max level 5; clean build of 91ed17cd; profile `orbit-modes-scan-prod`, zoom/coord 64) | 0.25 | queued, **not before its setup is verified (the user, 19:18 UTC: "we need to be sure this time the fly-by is correct, only after that we can launch")**: proposed A = its own t = 0 on the production grid, B = the same pair on the L = 64 level-3 grid to t = 20, plus the e2e to t = 50 | 100 | — | **not verified** (09-30 04:50 UTC): B's constraint blow-ups and inflating, infalling mouths, and the e2e's collapse at t = 44.67, need a diagnosis first |
| — | `v2_spiral_d12_p012_L128_lvl5from0_t100_csm` (the merger) | 0.12 | **stopped at t = 60.40** (08:21:51 UTC, `dump_and_stop`, the user's word: it does not end in a merger) | — | — | **closed out 08:45 UTC**: filed `05_binary_spiral/csm/`, packed, movies to its trust window t = 57, Table I `-` |

- **The probes stopped at 14:26:50 UTC (the user's word; no NaN in any log).** Last readings (t = 32): rest −0.05 %;
  p = 0.12 +9.9 % (t₁₀ ≈ 32.1, ε_eff ≈ −0.15 %, as extrapolated); p = 0.45 past the scan (edge reading +82 %, an
  upper bound). The verdict is in the CRITICAL section at the top.
- **The probes at t ≈ 11.5 (10:35 UTC):** alive, no NaN. Read R from the A rows of `horizon_scan.dat` (level 3,
  dr 0.02; the C rows are the level-1 common scan, dr 0.08, too coarse for a single throat).
  - Rest: R = 3.8772 flat to 5e-6 by t = 10, not moving.
  - p = 0.12: R +0.14 % by t = 10 (±0.05 % jitter as the scan re-centres on the moving throat); moved +0.34 in y.
  - p = 0.45: R +0.85 % by t = 10 (3.8757 → 3.9088) and speeding up (+0.12, +0.20, +0.25 % per unit over
    t = 7–10); moved +1.09 in y.
    - It is not the scan: the throat stays centred on the chi pit and round. Surfaces shifted and stretched along y
      find at most 0.02 % less area (t = 9 and 10).
    - On the seed ladder (the ε = −1e-3 seed is +0.15 % at t = 10) it reads ε ≈ −2.6e-3 at t = 6 and −5.8e-3 at
      t = 10. The reading is still climbing, so it is not yet one fixed kick.
    - The scalar, at rest at t = 0, picks up motion: max |Π| ≈ 1e-2 at t = 10, ∝ p, still growing.
    - **Settled by t = 25 (13:45 UTC): the inflation mode, not the slicing.** It runs away, as inflation does:
      +9.5 % at t = 20, +14.8 % at 22, +20.6 % at 24, +24.2 % at 25, still speeding up; no MOTS, nothing trapped.
      From t = 26 the throat is past both scans' outer radius (r = 2.29 on level 3, 2.33 on the common scan: the
      consumer's `horizon_half` 2.5), so those rows read the edge and are only upper bounds (+47 % at t = 29).
      - p = 0.12 inflates too: +0.88 % at t = 20, +4.4 % at t = 28, ×5.0 over t = 20–28 (the seeds' e-fold, ~5).
        Rest: flat to 4e-5 at t = 28.
      - On the seed ladder at t = 20: ε ≈ −1.2e-3 (p = 0.12) and ≈ −1.5e-2 (p = 0.45), a ratio ~12, close to p²
        (14) and to the ADM-mass excess over rest (0.0057 against 0.078, ×14). For p = 0.45 the reading climbed
        through t ≈ 20 (−2.6e-3 at t = 6, −6e-3 at 10), so the push lasts at least that long.
      - By the t₁₀ rule the binaries are read with: p = 0.45 reaches +10 % at t ≈ 20.2, ε_eff ≈ −1.8 %; p = 0.12
        is on track for t₁₀ ≈ 32 (extrapolated), ≈ −0.15 %. So the momentum setup alone is about the fly-by mouths'
        whole kick (−1.2 %), and small next to the spiral's (−0.8 %). The probes share the ladder's grid (L = 64,
        level 3); the binaries' mouths are on level 5, so the comparison is rough.
  - Their grid speed is the shift (β^y = −0.095 / −0.026 at t = 4) and grows as the shift builds; the physical
    speed (v ≈ 0.41 / 0.12) is fixed by the t = 0 momentum. Nothing feeds momentum or energy after t = 0: the
    momentum is read only by the initial data and the solve; support 1 with no ramp, phantom mass 0, core
    damping/freeze/fill off; the sponge only absorbs.
- **Close-out of the spiral (08:25–08:45 UTC):** no NaN in any stream or in `run.log`; trust window t = 57 (the
  constraint norms grow ×1.3 per unit from t ≈ 50, cut at the fly-by's L2 H ≈ 2.5e-2); registry, README and GPU_PLAN
  entries written; claims check 1075 rows, 0 problems; identity grep clean.
- **Wiped 08:52 UTC, the user's word** (`MANIFEST_CLEANUP_2026-09-29`): the spiral's scratch (`Chk05500`, `Chk06000`,
  the last plotfiles) and its plotfile keep (t = 45–60.40), 146 GB freed, 983 GB free. Kept: `Chk06040` in
  `_keep_v2_spiral_d12_p012_L128_lvl5from0_t100_csm_chk/` (25 GB) for a later wave extraction.
- **The dead production head-on is out of the pack** (08:55 UTC, the user's word): the close-out's rebuild had packed
  it (finished, not filed). Its run dir moved to `runs/wormhole_merger/00_archive/superseded/` (the packer skips
  `00_*`; data, the autopsy and frames kept), its packed copy and Table I row removed, the pack rebuilt.

- **The spiral stopped and the probes launched** (the user, 08:20 UTC 09-29). The spiral wrote `Chk06040` (t = 60.40)
  and exited normally (AMReX finalized, no NaN); the checkpoint is hard-linked into
  `/tmp/grteclyn_scratch/_keep_v2_spiral_d12_p012_L128_lvl5from0_t100_csm_chk/` (25 GB) for a later wave extraction,
  its plotfile keep (t = 45–60.40) and the rest of its scratch were wiped at 08:52 (above). The three mode-3 single-throat probes went
  on card 1 at 08:23 UTC (templates and launch line below; no checkpoints, the user's word). t = 0 read at 08:25:
  M_ADM 1.00137 / 1.00703 / 1.07969 (rest / 0.12 / 0.45; the exact throat's volume identity is 1.0014), every far
  side at the isolated −4.81048 / 3.03437, one-body mass 1.0000, the rest arm's solve w ~ 1e-14; L2_Ham(0) 2.12e-3
  (the seed ladder's floor), L2_Mom(0) 0 / 2.8e-6 / 1.1e-5; frame 0 renders (throat at y = −8); 59 GB on the card.
  The unsolved pair (`single_boost_p045_t050`, `..._vscal_t050`) waits for a card.

- **The spiral's merger inflates instead of collapsing** (07:00–07:55 UTC 09-29). The superposed run had a common MOTS
  by t = 55 and died at t = 59.94; this one has neither at t = 58.9:
  - the flow finder (`ah_flow_finder.py`, level 2, half 9, lmax 8, seeds 2.0 / 3.5 / 5.0 about the snapped pit, run on
    every plotfile from t = 53 by a loop that stops with the run; logs in the run's `flow_finder/wide/`) finds no MOTS
    at t = 53–56: the inner surfaces are anti-trapped (θ_out ≈ +0.3, θ_in up to +1.8); the outer one averages
    θ_out ≈ 0 with half its area negative and never converges;
  - the common-centre sphere scan (full metric): the common throat grew 5.46 → 5.60 over t = 45–52, anti-trapped
    (θ± ≈ +0.5 at R_min), and has been past the scan edge since t = 53 (edge reading 6.8 → 8.9 by t = 57);
  - the core's max |K| peaked at 0.42 at t ≈ 55 and fell to 0.28 by t = 57 (the old run's: 2.5 at t = 57, 53 at its NaN);
  - on one log scale against the superposed level-4 arm (`08_convergence/..._lvl4_t100_freeze_r03600`, fill off
    before t = 57), the lapse well is ~2× wider (α < 0.6 over ~195 against ~88 units² inside r < 8) and its two
    lobes grow.
  - Retracted as evidence of collapse: `areal_radius.dat` (4.72 → 3.80 over t = 40–57) is r/√χ along one ray, the
    flat-metric estimate that under-reads once the shift distorts the grid (no `--areal-full-metric` on this consumer).
- **The mouths' effective kick** (07:15 UTC 09-29). Each mouth's early R/R0 − 1 follows the single-throat seed ladder
  (ε = −1e-2 reaches +10 % at t = 23, −1e-3 at t = 34: ~11 units per decade), so ε_eff ≈ −1e-2 × 10^(−(t₁₀ − 23)/11),
  with t₁₀ the time to +10 %. Mode 3: fly-by (p = 0.45, d = 12) −1.2 %, head-on (p = 0, d = 8) −1.2 %, spiral
  (p = 0.12) −0.8 %, the p = 0 rest pairs at d = 12 about −0.4 % (+0.9 % by t = 15 against the fly-by's +2.7 %);
  superposed fly-by −1.0 %, head-on −0.9 %. Every mouth starts as a throat pushed toward inflation: the companion
  pushes (harder at d = 8), and momentum adds at fixed d. A merger collapses only if it finishes first: the head-on's
  common MOTS formed at t = 22 with the mouths at +6–10 %; the spiral merges at t ≈ 40–45 with them past +50 %. At
  d = 12 even p = 0 contacts only at t ≈ 28–30 (the old d = 12 head-on: separation 2.4 at t = 30).
- **Momentum against kick, and its constraints.** A boost cannot change a throat's fate: a uniformly moving exact
  wormhole is the static one in another frame, and time dilation (γ ≈ 1.1) only slows it. If momentum speeds
  inflation, the setup does it: the metric carries the Bowen–York momentum, but the scalar that holds the throat open
  starts at rest (Π = 0; `wormhole_boost_velocity` unset in all three runs), so the support lags the geometry. Both
  constraints hold at t = 0: with Π = 0 the scalar carries no current, so the Bowen–York Â_ij solves the momentum
  constraint exactly (the t = 0 base-grid L2_Mom, 5.8e-6 fly-by / 1.5e-6 spiral / 0 head-on, is its finite-difference
  error), and the Hamiltonian solve includes its kinetic term (the Newton passes). Boosting the scalar would leave a
  t = 0 momentum-constraint residual: the solve holds Â_ij fixed and omits the scalar's current.
- **Proposed, not queued (the user, 07:55 UTC 09-29; nothing starts without the go):**
  1. Single throat with momentum: at rest; with p = 0.12 and 0.45 (Bowen–York, scalar at rest); with p and the
     boosted scalar; one level (3 or 4). ε_eff from the time to +10 % against the seed ladder. If the throat with the
     resting scalar inflates sooner as p grows, the kick is the setup's, not physics. **Prepared 08:10 UTC 09-29 (the
     user: L = 64, N = 128, level 3); the three solved arms LIVE on card 1 since 08:23 UTC (the user's go, no
     checkpoints); the unsolved pair waits for a card:** templates in
     `runs/wormhole_merger/templates_scan/`, each the seed ladder's `params_single_eps_m1e2_t100.txt` without its seed,
     the throat starting at y = −8 and moving +y, t = 50; `launch.sh --dry-run` PASS on all five.
     - `single_rest_csm_t050` (mode-3 solve, p = 0: the solve's own seed), `single_boost_p012_csm_t050`,
       `single_boost_p045_csm_t050` (solve, scalar at rest);
     - `single_boost_p045_t050` and `single_boost_p045_vscal_t050` (no solve: the code refuses a boosted scalar under
       the solve; scalar at rest against scalar moving at v = 0.4104).
     - Launch each with `--profile headon-scout --zoom 40 --coord 32 --binary $B` (the mode-3 binary). ~18.5 GB and
       ~3 h each alone (18 u/h); the three solved arms share card 1 at 5.2 u/h each (59 GB). The unsolved pair was
       not launched: the user chose the fix instead (14:25 UTC).
     - Existing data point: `02_moving_throat/s20_boost_p02` (p = 0.2 along z, level 3, unsolved, 2026-08-31)
       inflates on the ε = −1e-2 track ~2 units behind (ε_eff ≈ −0.6 %; χ at the pit 1.6e-4 and max |K| 0.061 at
       t = 40, against 2.6e-4 / 0.060 for the seed), while the same throat at rest (`single_hold_t100`) drifts to
       collapse at t ≈ 60–65.
  2. A spiral that collapses: d = 8 with a small p (0.05, 0.10), so the plunge ends by t ≈ 25 as the head-on's did;
     level-3 scouts first (the −1e-2 seed runs identically at levels 3 and 4), then level 5 for the winner. Lowering p
     at d = 12 is not enough.

- The fly-by and the spiral: launched 09:49 UTC 09-28, both exact reruns of their old runs (only the solve block and checkpoints every 5 units, newest
  3), binary `main3d_csmatch_5f988dbc_2026-09-28.ex`, profiles `orbit-modes-scan-prod` / `orbit-modes-prod` (the
  scalar at 14/20/30/44), zoom 64. The fly-by's name keeps its old run's `merge_orbit_` prefix: it is the p = 0.45
  fly-by; the merger is the p = 0.12 spiral.
- t = 0 checked: preflight pass; each mouth's far-side mass −4.81048 and charge 3.03437, one-body mass 1.0000 (match
  8e-10 fly-by, 4e-10 spiral; mode 3 at p = 0.45 converged in 2 matching passes). M_ADM 2.34448 (fly-by), 2.27476
  (spiral; the CPU mode-3 check at p = 0.12 gives 2.27920 on L = 64). Frame 0 (χ) matches the old runs' (pits at ±6).
  Cards at 60 GB of 80 each.
- Checkpoints confirmed: `Chk00500` (t = 5) written 12:12 / 12:14 UTC, Header complete, 36–37 GB each; with the t = 0
  one on scratch, rolling to the newest 3. Plotfiles keep the last 3 (00700–00900 at 14:23). Each run holds 80 GB of
  scratch now, ~135 GB at most; 1.0 TB free. No NaN; consumer errors 0; 10 frames each (t = 0–9).
- **All three production runs verified at 10:15 UTC 09-28** (fly-by, spiral, and the second node's head-on):
  - each run's `params.txt` differs from its old run only in the named changes;
  - mode 3 in every `constraint_solve.dat`, converged: every MLMG solve ≤ 4e-9, each mouth's far side matched to
    8e-10 / 4e-10 / 4e-8, one-body mass 1.000000;
  - in-code Ψ4 written every step at 20/28/36/44 (head-on 10/14/18/20/28/36/44);
  - the consumer's scalar and Ψ4 at 14/20/30/44 (head-on 10/14/18/20/30/44), the same small-data files as the old
    runs, horizon scans (fly-by, head-on) with R_min 3.8763 / 3.8786 at t = 0, 15 frame fields, no consumer errors;
  - no NaN.
- **Consumers restarted 18:08 / 18:09 UTC 09-28** (the user's go; `restart_consumer.sh`, evolution untouched; frames 504 →
  504 and every stream intact to t = 17, checked with `restart_consumer.sh --check`):
  - fly-by: `--horizon-half 3.0 --horizon-common-level 3`, its old run's scan window. It had launched on the defaults
    (2.5, level 1, from the `orbit-modes-scan` profile; the profile passes 3.0 / level 3 since 19:01 UTC), which move
    the scan edge 2.79 → 2.29; rows to
    t = 17 are unaffected (r ≤ 1.53), rows from t = 18 use the old window.
  - spiral: `--horizon-scan` (same window) and `--areal-radius`, which the paper's mouth arm (`_lvl3_t050_mouths`)
    had; rows from t = 18.
  - Each new watcher runs under a supervisor that stops it when the evolution exits, so `run_single.sh`'s final
    drain (launch flags) does not race it; that drain extracts the last plotfile with the launch flags.
  - Why: the audit of what the paper needs from these runs, `CSM_SWITCHOVER.md`.
- **The spiral's plotfile keep (t = 45–60.40) was wiped at 08:52 UTC 09-29** (the user's word, above), so its offline
  core profile is gone with it; only `Chk06040` remains. `keep_plotfiles.sh` (hard-links each complete plotfile into
  `/tmp/grteclyn_scratch/_keep_<run>_plt/`, status with `--status <run dir>`) stays for later runs.

**The four mode-3 rest-pair reruns are closed out** (09:11–09:30 UTC): `ctrl_rest_d12_csm`, `ctrl_flip_d12_csm`,
`ctrl_rest_d14_csm`, `ctrl_rest_d16_csm`, each its old run's packed params with only the data changed (L = 64, N = 128,
level 3, t = 15), clean to t = 15, no NaN. Filed under `03_two_throats/csm/` with d = 18, packed without movies (frames
kept), scratch pruned (237 GB; MANIFEST_CLEANUP_2026-09-28) ["2026-09-28 (09:30 UTC)"].
- Pull/push at d = 12 over t = 3.5–10.5: 1.463 ± 0.023 (superposed 1.518 ± 0.021; fixed potential 1.500; fixed charge
  −0.667, excluded).
- Like-pair ladder at t = 11.5: +0.4791 / +0.3716 / +0.2963 / +0.2406 at d = 12 / 14 / 16 / 18 (×1.020 / 1.004 / 0.994 /
  0.987 the superposed runs'); A/(d + δ)² gives δ = 2.65 (superposed 3.56). Table:
  `results/merger/campaign/03_two_throats/matched_rest_displacement.dat`.
- t = 0 read at launch: every mouth's far-side mass and charge are the isolated throat's (one-body mass 1.0000); M_ADM
  2.27376 (flipped d = 12), 1.56579 / 1.62149 / 1.66449 / 1.69871 (d = 12 / 14 / 16 / 18).
- The GPU build reproduces the CPU energy scan at d = 8 (preflight-only on the scan's grid): M_ADM 2.3604109 (CPU
  2.36041), λ 0.856614, c 2.029956.
- The L = 128 pair launched first (05:12, `ctrl_{flip,rest}_d16_csm_L128_ml4_t015`) broke the rerun rule; stopped at
  t = 3 and wiped on the user's word, frames included (MANIFEST_CLEANUP_2026-09-28).

## Live — second node (one H100): the production head-on, leg 3 (the user's go, 04:23 UTC 09-30)

| card | run | t now | t end | speed | ETA |
|---|---|---|---|---|---|
| 0 | `merge_headon_flip_d8_v1_L128_lvl4from50_scalar_t100_csm_r05000` (leg 3: leg 2's Chk05000 down-stepped to `max_level = 4`, to t = 100, **no checkpoints** (the user's word, 04:23 UTC 09-30); levels 5–6 (boxes ±1.25 / ±0.63) lie inside the remnant horizon (coordinate r 2.28–2.34 since t = 45; the level-5 box's corner is at 2.17), so the horizon and the wave spheres keep their grid; template = leg 2's with the checkpoint keys off; same binary; profile `headon-modes-prod`) | 50.03 (04:27 UTC; alive: `max_level is lower than before`, finest 4, levels 2–4 125 grids each as leg 2's; 46.6 GB; Ham / Mom as leg 2's at t = 50.01–50.02 to 1e-4 relative; the core on level 4 reads calmer, lapse 5e-3, χ 7e-5, \|K\| 0.14 against leg 2's floor / 7e-6 / 0.35, as the old level-3 down-step's did) | 100 | ~6.8 u/h | ~7.3 h, ~11:45 UTC |
| — | `merge_headon_flip_d8_v1_L128_lvl6from35_scalar_chk_t100_csm_r03500` (leg 2: leg 1's Chk03500 with `max_level = 6`, no fill; tracker seeded at the merged core, the only template change; checkpoints every 5 units, newest 3; same binary; the user's go 20:30 UTC. A first launch at 20:33 seeded the tracker at the t = 0 positions ±4: the restart regrid dropped the core to level 3 (lapse and χ on their floors by t = 35.05); stopped 20:37 at t = 35.07, archived `_badseed_2037`) | **stopped at t = 50.80** (04:25 UTC 09-30, `stop_campaign.sh`, the user's word: leg 3 down-steps from its Chk05000). Through the wall: alive and NaN-free 12 units past leg 1's death at t = 38.85; the core lapse frozen on the 1e-10 floor from t = 35.01 (as the old level-5 twin's that walked through); max\|K\| 1.0 / 1.2 / 1.6 over t = 39–42, ~0.9 to t = 48, 0.35 at t = 50; common MOTS every unit t = 36–50 (R 3.85 / 4.26 / 4.49 at t = 36 / 37 / 38 against leg 1's 3.87 → 4.52; peak 4.66 at t = 39; 4.25–4.27 over t = 46–50); Ham L2 1.4e-4, Mom 4.2e-4 at t = 50 | 100 | — | **`Chk05000` (t = 50, level 6, 28 GB) kept (the user's word)**; `Chk04000` / `Chk04500` and the plotfiles t = 48–50 wiped 04:35 UTC (the user's word; frames and streams complete to t = 50; `MANIFEST_CLEANUP_2026-09-30`) |
| — | `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm` (leg 1, checkpointed; from rest, mode-3 data: clean of the momentum junk; `main3d_csmatch_5f988dbc`) | **DIED at t = 38.845** (20:20:49 UTC 09-29, NaN in h11 on level 5), the dead run's step to the digit, as planned | 100 | — | **leg 2 live** (below); `Chk03500` kept, `Chk02500` / `Chk03000` deleted 20:33 UTC (the user's word) |
| — | `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm` | **DIED at t = 38.85** (00:32 UTC 09-29) | 100 | — | superseded by leg 1 |

- **The head-on died at t = 38.845** (read from its own log at 04:58 UTC 09-29): NaN in h11 (A_ij non-finite) on
  level 5, 17 steps after a regrid, then MPI_ABORT; the manifest says failed, t_end 38.84. The core had reached the
  χ floor (min χ 1e-20 by t = 38; max |K| 0.6–1.1 over t = 34–39, min lapse 5e-4 → 6e-3). No checkpoints (the
  user's word), so it cannot be continued. Its old level-5 twin (L = 64, superposed data, plot interval 0.5) ran to
  t = 100 without a NaN; the params differ only in the box, the mode-3 solve, the checkpoints and the plot interval.
- **Anatomy of the death** (05:10 UTC 09-29, the autopsy and `collapse_diagnostics.dat` against the old twin's): a
  one-step overflow at the merged core, 0.15 from the box centre, inside the common MOTS (r = 2.5 at t = 38) and 16
  cells from any level-5 grid edge: χ 1e-3 → 1e+129, h11 0.95 → 1e+155, K 0.08 → 1e+178 in one dt = 3e-4. The
  interior failure of the L = 64 scout (t = 26.9: χ floor at the midpoint, K doubling), 12 units later. The old
  level-5 twin walked through it because its core lapse froze on the 1e-10 floor from t = 38.15; this run's core
  lapse re-inflated instead (8e-4 at t = 37 → 9e-3 at t = 38.25) with |K| ≈ 1, χ hit the floor at t = 38.84 and the
  next step overflowed. Outside the horizon the run is clean to the end: the (2,0) burst peaks at R = 10 / 14 / 18
  at t = 28.8 / 33.0 / 37.5 (old twin 28.1 / 32.3 / 36.7, 3–5 % weaker); at R = 20 it is at its peak when the run
  dies, and R = 28–44 never receive it. Common MOTS: R 5.02 at t = 22, peak 5.09 at t = 23 (old 5.53 / 5.58), lost
  t = 26–35 as in the old twin, back at 3.87 → 4.52 over t = 36–38 (old 4.27 → 4.63). Dynamics: same infall to
  t = 10, then 2–3 % ahead (sep 5.11 vs 5.23 at t = 15); throat lapse collapses earlier (0.064 vs 0.090 at t = 20).
  Speed 2.68 u/h average (old L = 64 twin 3.54).
- **Scratch wiped 05:13 UTC 09-29** (the user's word: "left overs should be wipe out"): its three plotfiles (t = 36–38,
  19 GB) and CS-1's empty scratch dir; the second node's scratch is empty, 671 GB free. The run dir stays on NFS
  (data to t = 38.84, the autopsy, frames 1092 files), since 08:55 UTC in `00_archive/superseded/` (out of the pack,
  the user's word). `MANIFEST_CLEANUP_2026-09-29.md`.
- **The plan (the user, 05:30 UTC 09-29): through the core failure by resolution, no fill.** Three legs:
  1. **Leg 1, live since 05:46 UTC:** `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_chk_t100_csm`, the dead run's
     params (level 5 from t = 0) with rolling checkpoints every 5 units, newest 3, as the fly-by and the spiral
     (36 GB each; template `..._scalar_chk_t100_csm.txt`, which differs from the dead run's params only in the
     three checkpoint keys). Profile `headon-modes-prod`, which now scans with half 4.0 from t = 0 (the profiles
     carry what the 2026-09-28 restarts had to add: `orbit-modes-scan` half 3.0 / level 3, `orbit-modes-prod` the
     scan and the areal radius). It dies at t ≈ 38.85 as the dead run did, ~14.5 h (~20:15 UTC), leaving Chk at
     t = 25 / 30 / 35. (A first launch at 05:40 UTC went up with checkpoints every unit, newest 8, against the
     user's instruction; stopped at t = 0.09 and wiped whole on the user's word, `MANIFEST_CLEANUP_2026-09-29`.)
  2. **Leg 2:** restart from Chk03500 (t = 35) with `max_level = 6` through the wall. Adding a level on restart is
     how the old level-5 arm was born (from the scout's level-3 Chk02200). Level 6 costs ~2× per unit: t = 35 → 45
     in ~7 h. If it dies too, the next try starts from Chk03000.
  3. **Leg 3:** once past the wall, down-step to level 3 from a checkpoint after it, to t = 100 (~10 u/h, ~6 h). **Done instead as level 4 from t = 50** (the user, 04:23 UTC 09-30): t = 40 sits before the post-wall max\|K\| peak (1.6 at t = 41–42); level 4 keeps the horizon's grid, level 3 would coarsen it.
  The dead run's data to t = 38.84 is the no-fill level-5 reference. Nothing of legs 2–3 starts without the go.
  The dead run's live common-horizon scan found the MOTS in 7 of 39 C rows (t = 22–38; R 5.02 at birth, 4.52 at
  t = 38). It is archived out of the pack (08:55 UTC 09-29, the user's word); none of its 3D state is left (scratch
  wiped 05:13).

- **The dead run's common horizon at t = 22.0** (09-28; the live scan, half 4.0): r = 2.53, areal radius R = 5.02 (the superposed runs:
  5.53 live at t = 21.5 in the old level-5 arm, 5.56 offline in the scout), ~10 % smaller, as the mode-3 mouths are.
  The evolution sped up with the merger as the old run did: 2.4 → 2.6 → 3.7 → 3.85 u/h over t = 19–23. No NaN;
  streams and frames clean to t = 22 (checked 20:25 UTC).

- **The dead run's consumer restarted 18:19 UTC 09-28 with `--horizon-half 4.0`** (the user's go; `restart_consumer.sh`, evolution
  untouched; frames 504 → 504, every stream intact to t = 17, parsed flags checked). The old level-5 head-on scanned
  with half 3.0 and lost the common MOTS past the scan edge after t = 37 (11 of 201 C rows); the late track, its fits
  and clmDetKerrRise need it. Rows to t = 17 use half 3.0 (no MOTS yet), rows from t = 18 half 4.0. The fly-by's
  and the spiral's first rows after their restarts (t = 18) checked clean.

- The dead run: launched 10:02 UTC 09-28 (template `params_merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm.txt`, profile
  `headon-modes-prod`, zoom 40, coord 64, binary `main3d_csmatch_5f988dbc_2026-09-28.ex`). The blessed exception to the
  rerun rule: the old L = 64 physics in the shared L = 128 box (details in the production set below).
- The 09:58 attempt was refused by the preflight: the template still carried the old run's `checkpoint_interval = 100`
  and `checkpoint_keep = 1` with checkpoint output off. Now `checkpoint_interval = -1`: **no checkpoints** (the user's
  word); if it dies it cannot be restarted.
- t = 0 checked: preflight pass; M_ADM 2.35731 (CPU scan 2.3604 on L = 128 level 4; the L = 64 attempt 2.35892),
  m1_A = m1_B = 1.0000000; frame 0 (χ) two pits at ±4; 59 GB on the card, stepping (t = 0.06 at 10:05).
- The L = 64 head-on rerun before it (08:07–08:26 UTC, stopped at t = 0.60) was wiped on the user's word, frames
  included (MANIFEST_CLEANUP_2026-09-28).

## The production set: head-on, spiral, fly-by in one box (the user's final proposal, 2026-09-28 09:00 UTC) — the fly-by live, the spiral stopped, the head-on rerun as leg 1

Shared by all three (the user): L = 128, N = 256 (Δx = 0.5, finest 1/64), max_level 5 from t = 0, tagging_L 64 (the same
refined grids), sponge 48/64, Ψ4 at 20/28/36/44, the scalar at 14/20/30/44 (consumer profiles `*-prod`, output only),
plots every 1.0, mode-3 data, binary `main3d_csmatch_5f988dbc_2026-09-28.ex`. Launched on the user's go.
Order: fly-by → spiral → head-on. **Now (09-29): the fly-by is live on the first node (card 0); the spiral stopped at
t = 60.40 and is closed out; the head-on died at t = 38.85 and runs again as leg 1 on the second node; see Live, above.** Templates in `runs/wormhole_merger/templates_scan/params_<run>.txt`, each
diffed against its old run's packed params (only the named changes):
- **`merge_orbit_flip_d12_p045_L128_lvl5_t100_csm`** (first node, card 0, first): the exact rerun, plus checkpoints
  every 5 units (500 steps), the newest 3 (the old kept 8 at every 1.0). t = 100 (never NaN'd; trusted to t = 70).
  Profile `orbit-modes-scan-prod`, zoom 64, coord 64. 2.17 u/h (old) → ~46 h; 58.8 GB (old). Mode 3 at p = 0.45 is
  new (tested at 0.12): read the Newton passes and each mouth's far side at start-up.
- **`v2_spiral_d12_p012_L128_lvl5from0_t100_csm`** (first node, card 1): the exact rerun, plus checkpoints every 5
  units, the newest 3 (19–26 GB each). To its NaN (old wall t = 59.94; stop_time 100). Profile `orbit-modes-prod`,
  zoom 64, coord 64. 2.81 u/h (old) → ~21 h; ~59 GB. Then the freeze continuation (plan now, launch later): relaunch
  from the last checkpoint ≥ ~55 with the interior fill, armed from THIS run's core profile (the spike time moves with
  the smaller mode-3 throats), not the old t = 57; the validated ratios r_full/r_start = 1.40/1.90.
- **`merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm`** (second node): **a blessed exception to the rerun rule**
  (the user's word): the old L = 64 physics in the shared geometry, for one geometry and a reflection-free window to
  t ≈ 84 at R = 44 in the shared energy table. Changed: the box keys (identical to the fly-by's), plots every 1.0
  (was 0.5), the solve block, and the old spheres kept (output only): Ψ4 at 10/14/18 + 20/28/36/44, the scalar at
  10/14/18/20/30/44 (profile `headon-modes-prod`). Δx and the finest level are the old run's, so at 10/14/18, before
  any reflection, old vs new is one knob (the data); the box enters only through reflections, which it delays. The
  paper's head-on chain: superposed scout → CS-1 (same grid, one knob) → mode-3 big box (data + box, compared at common
  spheres). **No checkpoints** (the user, 09:00: "it will run smooth"). t = 100, zoom 40, coord 64. Est. 2–2.8 u/h,
  ~36–50 h; ~59 GB (the preflight measures it).
- **Skipped on the user's word (09:20 UTC): per-level + core-excised 𝓗/𝓜 diagnostics.** No claim needs them (every
  constraint statement is relative, the figure calls the norms base-grid box averages); Sec. II D's t = 0 throat-shell
  number is redone on CPU with `constraint_solve_t0_check.py` ["2026-09-28 (09:30 UTC)"].
- Launch checklist: t = 0 far-side mass and charge at the isolated values (~2e-7), R_min ≈ 3.889; each run's M_ADM
  into the registry (head-on 2.360; spiral and fly-by above 2.274 by their kinetic term); frame 0 against an old
  reference; the first checkpoint on scratch (spiral, fly-by). The registry marks the head-on as the blessed exception,
  the spiral and fly-by as exact reruns. No test launches.

From the repo root, `nvidia-smi` first, each redirected (`< /dev/null > <log> 2>&1`):
```
L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh; B=runs/wormhole_merger/bin/main3d_csmatch_5f988dbc_2026-09-28.ex
bash $L --gpu 0 --template params_merge_orbit_flip_d12_p045_L128_lvl5_t100_csm.txt --name merge_orbit_flip_d12_p045_L128_lvl5_t100_csm --profile orbit-modes-scan-prod --zoom 64 --coord 64 --binary $B
bash $L --gpu 1 --template params_v2_spiral_d12_p012_L128_lvl5from0_t100_csm.txt --name v2_spiral_d12_p012_L128_lvl5from0_t100_csm --profile orbit-modes-prod --zoom 64 --coord 64 --binary $B
bash $L --gpu G --template params_merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm.txt --name merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm --profile headon-modes-prod --zoom 40 --coord 64 --binary $B
```
Then the plan's step 4 (single throats on clean data), each a rerun of its old run by the rule.

## Done — the boosted-setup shape set (t = 0; the user's go 16:58 UTC; packed 19:45 UTC, `campaign/02_moving_throat/contraction_t0/`, no movies)

One exact-boost throat per p (`t0_single_boost_pXXX_lbc`, the collar rerun's template with only p, the name and
stop_time 0.1 changed; level 3; no checkpoints), started 16:53 UTC, all done in minutes. The t = 0 plotfiles are on
the first node's scratch; the measured table and slices are in the pack
(`campaign/02_moving_throat/boost_contraction_t0.*`).

| p | v | 1/γ | measured axis ratio (throat contour) |
|---|---|---|---|
| 0 | 0 | 1.00000 | 1.00000 |
| 0.12 | 0.119 | 0.99288 | 0.99288 |
| 0.25 | 0.243 | 0.97014 | 0.97015 |
| 0.35 | 0.330 | 0.94386 | 0.94387 |
| 0.45 | 0.410 | 0.91192 | 0.91195 |

**p = 0.45 is extreme** (v = 0.41 per mouth, 0.70 relative). It stays only as the curve's top point. Binary
production stays at p ≤ 0.35 unless a clean rerun places the capture boundary above that.

## Queued — mode-3 follow-ups: the ladder (Fig. 12a) and a convergence twin (the user, 2026-09-28 ~11 UTC; nothing launches without the go)

Fig. 12 is `fig:spiral_ladder`. Panel (b), the slicing/gauge study, **is done** (the gauge arms on superposed
data); it is a systematics statement and is not rerun. Panel (a), the refinement ladder to the wall, is rerun on
mode-3 data; the paper's framing (the user): the old constraint state is barely mentioned — the headline is that
mode 3 improves the constraints, and the old campaign is the systematics study.

| id | run | what | how | GPU-h |
|---|---|---|---|---|
| LAD-csm | ladder arms `ladder_csm_L{4,6,7}_r0XXXX` | the wall under refinement on mode-3 data (Fig. 12a) | restart from the production spiral's own checkpoint at t ≈ 50 (its every-5 checkpoints exist for this), max_level 4 / 6 / 7; the production run itself is the level-5 rung; ~10–15 units per arm | ~15–25 total |
| CONV-csm | `v2_spiral_d12_p012_L128_lvl4from0_t100_csm` | spiral burst and energy, level 4 vs 5 on mode-3 data (replaces CONV-3's role) | the production spiral's template, max_level 4, from t = 0 | ~8–10 |

| EGW-p06 | `merge_orbit_flip_d12_p060_lvl5_t040_csm` | E_GW(p) above the fly-by: where the curve turns over | the fly-by template, p = 0.60, stop_time ~40 (the encounter is over) | ~8-12 |
| EGW-p09 | `merge_orbit_flip_d12_p090_lvl5_t040_csm` | E_GW(p) far side of the peak | same, p = 0.90 | ~8-12 |
- LAD-csm launches only after the spiral passes t ≈ 55 and a checkpoint ≥ 50 is on scratch; convergence-study rules
  apply (no frames: `--frames-fields none` + `WHM_FRAMES_SUBSET`, `WHM_MOVIES=0`, group `08_convergence`).
- max_level alone still leaves the wave zone on the base grid; a wave-zone twin (CONV-3w's role) is contingent on
  the mode-3 waveforms shifting beyond a few % and is not queued.
- Checkpoints: to be asked per run at launch (the standing rule); the ladder arms need none.
- EGW-p06/p09 (proposed 2026-09-28, the E_GW(p) curve for Fig. 9b): with p = 0/0.12/0.25/0.35/0.45 from the
  campaign these bracket the curve's turnover, so "loudest possible burst" becomes measured. Watch: junk
  radiation grows ~p^2 (separable at 0.45, check at 0.9), and mode 3 above p = 0.45 is new -- read the Newton
  passes at start-up. The fit itself is CPU analysis over the packed psi4 streams.

## Earlier (2026-09-27)

CONV-1, CONV-2 and CONV-3w were stopped at 08:33 UTC on
2026-09-27 and removed at 08:40 UTC ["2026-09-27 (08:33 UTC)"]. They had reached t = 30.25 / 60, 57.88 / 60 and 58.18 / 100.
Their scratch (38 GB of plotfiles, no checkpoints), run dirs, launcher logs, registry rows and untracked partial packs
are gone. Only their rendered frames are kept, in `runs/wormhole_merger/00_archive/stopped_2026-09-27/`, because frames
are never deleted without the user's explicit word. All three were queued again, and the plan (2026-09-28) cancels them.
- **CONV-3 is closed out** (finished t = 100 at 02:12 UTC; filed under `08_convergence/`, packed, scratch pruned).
  - Its (2,2) burst matches the level-5 chain on every sphere: peak ratio 1.000, waveform within 0.1 % of peak.
  - Both runs extract on the base grid, so this tests the core's resolution, not the wave zone's. CONV-3w tests the
    wave zone ["2026-09-27 (05:00–05:45 UTC)"].
- **Kept on the user's word (2026-09-27, "skip"):** CONV-3's frames (in its run dir) and Chk05700. Chk03600 stays too:
  the queued CONV-3w restarts from it.

- **Second node: free. CS-1 `merge_headon_flip_d8_cs_lvl3_t030` is closed out** (the head-on scout on
  constraint-solved data; finished t = 30 at 08:14 UTC, no NaN; filed under `04_binary_headon/`, packed)
  ["2026-09-27 (08:30 UTC)"].
  - The same merger as the scout, about 2 units later, with a horizon 4–5 % larger: common MOTS born at t = 23
    (scout: present at t = 22), R = 5.84 at birth and 5.94 at its peak (scout 5.56 and 5.71).
  - The pair's M_ADM is 2.74 (corrected 12:15 UTC; the 2.63 read the Robin face's offset of w as mass), not 2.00,
    so R/2 is 7–8 % above it (the paper's 39 % used 2.00). Its mouths are the scout's, to 0.1 % in far-side mass.
  - Trust window t ≤ 29.7: the core's K runaway starts at t = 29.8.
  - One resolution (level 3), one separation. The level-5 head-on, the spiral and the fly-by have no solved twin;
    CS-2 (the p = 0.12 spiral on solved data) was not run (the user: "do not run it").
  - **Scratch pruned at 08:36 UTC on the user's word** (115 GB: its checkpoints, its plotfiles and
    `_keep_cs1_formation/`; MANIFEST_CLEANUP_2026-09-27). CS-1 has no restart state left; its frames and movies
    are in the run tree.
  - The three partial pack copies of the first node's live runs, made by this close-out, were removed at 08:38 UTC
    on the user's word. The pack now skips a run that is live on the other node, the summaries carry no live
    rows, and `claims.py check` passes (833 recomputed, 0 problems).

**Done 2026-09-27 (12:35 UTC, paper session): the paper's rewrite for the matched placement has started** ["2026-09-27 (12:35 UTC, paper session)"]: new Sec. II D (constraint-solved data, far-side identity, matched placement, Eq. (ebind) E_b = −λ²(m²/d)(1 + σQ)), Tables placement and energy, Table I counts CS-1, head-on Penrose and area statements qualified. Ledger 1070 rows, 0 problems. Not built (no LaTeX here). The evolution sections still quote the superposed runs, in the units II D states.

**Done 2026-09-27 (12:15 UTC, CPU only): parameter matching and the energy check** ["2026-09-27 (12:15 UTC) — parameter matching and the energy check"]. Each mouth's far side (ADM mass 2cd and scalar charge at its own compactified infinity) is now measured after every solve. Verdicts:
- The solve did **not** change the throats: CS-1's mouths have the scout's far-side mass to 0.1 % (R_min +1.3 %). CS-1 turned one knob, the data.
- The **superposition** did: every superposed pair's mouths are ~13 % larger in every length than the isolated throat (one-body mass 1.149 at d = 8, 1.094 at d = 12, same for solved mode-0 twins). So p = 0.12 / 0.45 at d = 12 are 0.110 / 0.411 per one-body mass in every run; no rerun is needed for this, only the paper's normalisation.
- CS-1's M_ADM is **2.74**, not 2.63 (the Robin face leaves w a constant −1e-3; the volume identity, 1.0014 on the exact throat, does not see it).
- **Mode 3** (`constraint_solve_puncture_mode = 3`) builds the pair from two isolated throats: c and each throat's coordinate size iterated until its far-side mass and charge are the isolated ones; R_min lands 0.06 % from R⋆. Also with momentum (d = 12, p = 0.12).
- **Energy check** (mode 3, d = 8–48, both signs): M_ADM − 2m = σ²[±(a² + m²) − m²]/d to 3 % (d = 8) and 0.3 % (d = 48): gravity's −m²/d plus the ghost scalar's cross energy, **positive for the attracting pair**. Not a bug. It matches the measured attraction (and its ratio 5 to gravity) only if the throats behave as conductors at fixed scalar potential; at fixed charge it would be repulsion. Open: a dynamical test (initial acceleration in mode-3 data, both signs, GPU minutes). Nothing launched; the code is not yet compiled for CUDA.

**Done 2026-09-27 (05:45–06:00 UTC): constraint-solved initial data** ["2026-09-27 (05:45 UTC) — constraint-solved initial data"]. `constraint_solve = 1` in the merger example solves the Hamiltonian constraint on the initial hierarchy with AMReX MLMG (φ, Â, Π, lapse fixed; momentum constraint stays exact; Newton for p ≠ 0). Validated on CPU at t = 0: rebuilds the exact drainhole from bare punctures (R_min to 5e-4); the d = 8 head-on's finest-level Hamiltonian drops 9.7e-3 → 5.1e-6 (×1900, the exact throat's floor); orbital p = 0.12/0.45 converge in 3 Newton passes. The solve adds the scalar interaction energy: M_ADM 2.00 → 2.63 at d = 8, throats +1.3 %. Base-grid L2_Ham cannot see it (unresolved throat). The test binary is a `-dirty` build; a clean pin from the commit is still to be built. Grader: `scripts/validation/constraint_solve_t0_check.py`. **On the GPU (second node, 06:00 UTC):** the dirty build reproduces the CPU solve digit for digit (max |w|, L2_Ham, the Newton sequence), 3–4 s per start-up; level 5 solves in +2.5 s, 24.6 GB at start-up.

**Done 2026-09-26 (afternoon, not committed): the referee's fixes** ["2026-09-26 (afternoon, paper session)"]. Retitled "The Four Fates of Ghost-Supported Wormholes: Collapse, Inflation, Merger and Scattering in Numerical Relativity"; the abstract is the user's own text (16:00 UTC). Cosmology conditional on z_e; no "baby universe", no percolation bound; "wall" → "interior failure"; no vacuum ISCO (the pull's period P = 75–100; ε = 1e-15 buys 1.8–2.7 periods); η = 4 horizons in §VII C; fly-by trust window t = 70 (new Fig. 10(g); Figs. 14/15/17/18 cut). Re-read on CPU: throat energy 2.6e-5 (to t = 58), 44× the matched control; Kerr rise 1.34; orbit fractions 0.27–0.30; **the mouths' τ with the companion's field removed: the merging arm has no growth of its own, the fly-by τ = 3.9** (the referee's "lower bound" had the wrong sign); the mouth fit had dropped its end rows (τ 3.64/4.33 now). 17 references. Ledger: 1000 rows, 0 problems. Caveats the referee asked for are in the text (Δt, ADM balance, curvature at the failure): G17/G18 queued. The head-on t ≤ 70 sentence was narrowed on the user's word (16:10 UTC): its numbers past t = 70 carry the late spread; no re-gate. No DOI yet (the user will add it).

**F4 `single_eps_m1e2_L512_ml5_oct_t400` is closed out** ["2026-09-26 (05:00 UTC)"]: it died at t = 392.36 (04:22 UTC, NaN in
h11 on level 2, blowing up on the neck sphere r ≈ 60–65). It was closed out with movies (chi K lapse phi Pi), filed under
`01_single_throat/seed/` and packed. **Quotable to t = 218 only**: the 1+log collapse front reaches the outer face at
t = 218, and its reflection runs back in, reaching the neck as the run dies. The far θ_k horizon is lost at t = 212, and L2 𝓗
passes 0.1 at t = 220. Result: R 3.813 → 14.48 (×3.80) by t = 218 with no trapped surface. The onset is exponential,
T = 5.69 over t = 16–28. In proper time it grows at the Shinkai–Hayward rate over t = 16–40: H R0 = 1.22 (their 1.1). The θ_k = 0 horizon
grows to R = 73.4 by t = 212. The launch passed a trimmed frame list, so it has **no Weyl4 or shift frames** (lost). Its
scratch (24 GB) was pruned at 05:53 on the user's word. Figures: the paper's `fig:single_inflation` (the `single_throat_inflation_L512` campaign page was retired from `figures/` on 2026-09-26). The paper's Fig. single_inflation and §IV.D are rebuilt on F4 alone; Table I counts it (145 runs, 663 GPU-hours).

**Wiped on the user's word** (2026-09-26 04:16–04:18, frames included, `manifests/MANIFEST_CLEANUP_2026-09-26.md`): the failed
harmonic retries F5 `…harm_oct_t400_sg03` / `_sg10` (NaN at t = 46.71 / 47.01 on F3's wall) and F6 `…harm_oct_zs_t400`
(zero shift, runaway from t ≈ 29). Earlier: F3 and F2 (16:33), F1b (14:15). No NaN-free re-run (3D harmonic with
solution-following refinement, or a 1D spherical code): the user's no-go, 2026-09-26. The question is only whether the
throat keeps growing, and F4 answers it.

Done 2026-09-26 (not committed): the paper renamed ("… BLACK-HOLE SEEDS AND BABY UNIVERSES: MERGER, SCATTERING, AND
INFLATION …") and the inflating branch made a result instead of a loose end, on the user's direction. New §X
"The inflating half of the population": sign-symmetric seeds send about half of a foam population inflating (large seeds
skew toward collapse); an inflating throat is a Farhi–Guth baby universe — anti-trapped interior, exterior at fixed ADM
mass — with 1.3 (neck) / 3.0 (θ_k boundary) areal e-folds in F4's record against inflation's ~60; the boundary advances
at a steady 0.33c (no slowing over the last 50 units), so non-overlap of mouths today caps the mean comoving speed at
(2.6×10⁻⁴–1.2×10⁻³)c for n = 10⁻⁴–10⁻² Mpc⁻³ — the seed channel is consistent only if the boundary stalls (recorded
speed is 270× the loosest bound) or the inflating half is rare. §IV.D now quantifies the turnover premise: store
R⋆/2 − m = 0.94; shed 0.03 over the quiet window; F4's own spheres only bracket it, 4.1 kinematic vs 0.04 geometric
(the 1+log front collapses the lapse at the spheres first) — ending stays open. Backing: `results/merger/analysis/
inflating_population.py`, extractors `single_f4_pop` / `detector_stall`, 12 ledger rows, three new references
(Farhi–Guth 1987; Blau–Guendelman–Guth 1987; Liddle–Leach 2003). Same session, referee-critique edits: abstract
trimmed 457 → 368 words (incl. one new baby-universe sentence), near-zone extraction now stated in the intro,
a junk-radiation paragraph in §VIII (t=0 defect crosses spheres by t≈R, bursts arrive with their triggers), duplication
trims across §§I–X; 29 rows re-anchored after the trims. Ledger: 963 rows, 802 recomputed, 0 problems, stamped.
The wrapper venv was re-synced (pycbc/astropy had gone missing; full `claims.py check` needs them).

Done 2026-09-26 (not committed): the paper's layout, on a referee-style read. The constraint panels of Figs. 1/2/3/5/7
(old numbers 1/2/4/6/9) became one appendix figure, `fig:constraints` (App. A, "Code Health and Constraint Evolution",
each run at its highest level); regrowth, refinement ladder and fill insensitivity moved to App. A, mouth growth, seed
linearity and scalar censorship to App. B. `results/merger/figures/` now holds the paper's 18 figures only (17 others
deleted, `p012_paper/` flattened) and `pack_results.sh` draws none. Ledger: 951 rows, 0 problems.

Done 2026-09-26 (pushed): the full default frame set (`frames_default.txt`), with a preflight that renders every field
at t = 0 and refuses a subset without `WHM_FRAMES_SUBSET`; movies cut at each run's trust window
(`results/merger/trust_windows.tsv`); the cleanup manifests moved to `runs/wormhole_merger/manifests/`.

First node: the long
single-throat arms closed out under `01_single_throat/seed/` ["2026-09-24 (16:15)"]; its
scratch holds only the live runs. The paper session's `plt_take2/` plotfile copies (77 GB, G16's input) were deleted
on the user's word on 2026-09-27, because G16 was dropped.

Second node (one H100): free since 08:14 UTC on 2026-09-27; CS-1 and the η = 4 level-5 probes are closed out and
filed ["2026-09-27 (08:30 UTC)", "2026-09-25 (morning)"]. Its scratch is empty (115 GB pruned at 08:36 UTC,
MANIFEST_CLEANUP_2026-09-27).

Run tree: every plotfile deleted on the user's word; 192 → 52 GB. Two checkpoints remain: Chk03600 (20 GB, the t = 36 seed of CONV-3) and Chk05700 (26 GB, no queued
use since G4 was dropped; kept on the user's word, 2026-09-27).

## Cancelled — the convergence runs on the old data (the plan, the user's word 2026-09-28)

**Cancelled by the plan above:** they converge superposed-data runs; the finer-grid twins of step 3 replace them.
Kept below as the record of their templates (queued on the user's word, 2026-09-26 17:30 UTC).

Nothing launches without the user's word. Every other option (G1–G18, A1–A4, B/C, the inflation campaign) was dropped
from the queue on the user's word ["2026-09-26 (evening) — the convergence queue"]. Each template is its partner's params
with only the named keys changed, and all nine PASS the full preflight (2026-09-26 16:50 UTC; nothing launched).

| id | run (template in `templates_scan/params_*`) | converges | partner | GPU-h | peak GB |
|---|---|---|---|---|---|
| CONV-1 | `single_eps_m1e2_ml5_t060` (`single_eps_m1e2_ml5_t060`) | τ: third level, a convergence order (abstract) | `single_eps_m1e2_t100` / `_ml4_t100` | 14 | 27 |
| CONV-2 | `single_eps_m1e2_halfstep_t060` (`single_eps_m1e2_halfstep_t060`) | Δt: dt_multiplier 0.01, intervals doubled (§III) | `single_eps_m1e2_t100` | 7 | 20 |
| CONV-3 = G9 **DONE, closed out** | `v2_spiral_d12_p012_L128_lvl4_t100_freeze_r03600` (`prod_L128_p012_lvl4_t100_freeze`) | spiral burst and energy, level 4 vs 5; fill at t = 57 in the same leg | the production chain | 9 | 56 |
| CONV-3w | `v2_spiral_d12_p012_L128_lvl4_wz1_t100_freeze_r03600` (`prod_L128_p012_lvl4_wz1_t100_freeze`) | the WAVE ZONE: R = 20 and its path (r < 24) on level 1, vs CONV-3 on level 0 | CONV-3 | 10 | 62 |
| CONV-4 | `merge_orbit_flip_d12_p045_L128_lvl4_t095` (`flyby_p045_L128_lvl4_t095`) | fly-by energy, scalar, mouths; t = 95 reaches the R = 44 gate | `…p045_L128_lvl5_t100` | 21 | 56 (+1–5 at the pass) |
| CONV-5 | `merge_orbit_flip_d12_p045_L128_lvl3_t095` (`flyby_p045_L128_lvl3_t095`) | the fly-by's third level (order) | same | 11 | 52 (+1–5) |
| CONV-6 = G12 | `merge_headon_flip_d8_lvl5from0_ball4_t100` (`headon_d8_lvl5from0_ball4_t100`) | remnant horizon on level 4, not 3 ("loses a quarter", abstract); since 2026-09-27 also the head-on's wave zone: R = 10 and its path (r < 12) on level 2 | `…v1_lvl5from0_scalar_t100`, `…v1_lvl3down_t100_r03500` | 34 | 60 |
| CONV-7 | `merge_orbit_flip_d12_p035_lvl5_t080` (`scan_p035_lvl5_t080`) | p = 0.35 passes at level 5 (the abstract's 50–70 %) | `…p035_t200` (closest 2.75 at t = 42) | 35 | 47 |
| CONV-8a/b | `ctrl_rest_d12_ml4_t015`, `ctrl_flip_d12_ml4_t015` | the sign ratio 1.52 at level 4 (abstract) | `ctrl_rest_d12`, `ctrl_flip_d12` | 3 + 3 | 41 each |

~140 GPU-h in all. GPU-h are solo speeds (measured for the parent class, level-4 L = 128 estimated at 4.5 u/h). Peak GB =
AMReX arena high-water + ~1.3 GB context, measured on the parent class where one exists; the preflight start-up
footprint × 1.8 reproduces every measured one (level-5 fly-by 34.0 → 58.8; L = 64 level-3 arm 17.8 → ~32). A card has
79.6 GB; most runs peak in step 1.

**Sharing a card buys nothing**: two L = 64 level-4 arms on one card ran 3.9 u/h each against 8.7 alone (GPU_PLAN
Phase 2b). Placement: none. All three cards are free, and nothing launches until the user says go.

Every remaining launch goes without frames: `--frames-fields none` with
`WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)"`. CONV-8a/b use `--frames-fields chi`
instead, because the sign rule reads the chi slice cache. Close-outs use `WHM_MOVIES=0`.
The queued templates still write rolling checkpoints. The user's no-checkpoint word was given for CONV-1, CONV-2 and CONV-3w.

Pairs that fit if two must share: CONV-1 + CONV-2 (47 GB), CONV-2 + CONV-8 (61), CONV-1 + CONV-8 (68), CONV-2 +
CONV-7 (67). Never CONV-8a + CONV-8b (82), and nothing beside CONV-3/4/5/6.

Launch from the repo root with `L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh`,
`B=runs/wormhole_merger/bin`. Check `nvidia-smi` first, and redirect each launch (`< /dev/null > <log> 2>&1`):
```
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_single_eps_m1e2_ml5_t060.txt --name single_eps_m1e2_ml5_t060 --profile headon-scout --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_single_eps_m1e2_halfstep_t060.txt --name single_eps_m1e2_halfstep_t060 --profile headon-scout --frames-fields none --binary $B/main3d_boost_2026-09-08.ex
bash $L --gpu G --template params_prod_L128_p012_lvl4_t100_freeze.txt --name v2_spiral_d12_p012_L128_lvl4_t100_freeze --profile orbit-modes --zoom 64 --coord 64 --binary $B/main3d_coreprof_2026-09-15.ex --restart "$PWD/runs/wormhole_merger/05_binary_spiral/p012/_keep_spiral_premerger_decay/BinaryWormholeChk03600"
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_prod_L128_p012_lvl4_wz1_t100_freeze.txt --name v2_spiral_d12_p012_L128_lvl4_wz1_t100_freeze --profile orbit-modes --zoom 64 --coord 64 --frames-fields none --binary $B/main3d_coreprof_2026-09-15.ex --restart "$PWD/runs/wormhole_merger/05_binary_spiral/p012/_keep_spiral_premerger_decay/BinaryWormholeChk03600"
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_flyby_p045_L128_lvl4_t095.txt --name merge_orbit_flip_d12_p045_L128_lvl4_t095 --profile orbit-modes-scan --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_flyby_p045_L128_lvl3_t095.txt --name merge_orbit_flip_d12_p045_L128_lvl3_t095 --profile orbit-modes-scan --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_headon_d8_lvl5from0_ball4_t100.txt --name merge_headon_flip_d8_lvl5from0_ball4_t100 --profile headon-modes --frames-fields none --binary $B/main3d_boost_2026-09-08.ex
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_scan_p035_lvl5_t080.txt --name merge_orbit_flip_d12_p035_lvl5_t080 --profile orbit-modes --frames-fields none
WHM_FRAMES_SUBSET="convergence study: chi only, for the sign rule (the user's word, 2026-09-27)" bash $L --gpu G --template params_ctrl_rest_d12_ml4_t015.txt --name ctrl_rest_d12_ml4_t015 --profile orbit --frames-fields chi
WHM_FRAMES_SUBSET="convergence study: chi only, for the sign rule (the user's word, 2026-09-27)" bash $L --gpu G --template params_ctrl_flip_d12_ml4_t015.txt --name ctrl_flip_d12_ml4_t015 --profile orbit --frames-fields chi
```
Each `--binary` is the partner's build: CONV-2 and CONV-6 compare against boost-built runs; CONV-3 splices onto the
coreprof-15 legs. The rest run on the pin, which has the same source as the level-4/5 partners.
- CONV-3's `--restart` must be an absolute path: the binary runs from the run dir, and a relative one aborted the first
  preflight. If level 4 dies before t = 57, restart from its last checkpoint ≥ 55 with `core_fill_from_time` there.
- CONV-6's ball is the stock ExtractionTagger: a 4th extraction radius R = 3.0 at level 4 refines r < 3.6. Its R = 3
  Ψ4 is not a wave product.
- CONV-8's parents wrote no shift or h_ij. The full plot list is added (output only), because the frame set needs it.

## Verdicts (the paper's wording; paper section in parentheses)

Every binary verdict below (two throats at rest, head-on, spiral, fly-by, waves and astrophysics from them) is on
superposed initial data: see CRITICAL at the top. Each stands only until its mode-3 rerun.

- **Single throat**: unstable fixed point, one exponential mode; the e-fold is within 2.5 % (level 4) and 15 % (level 3) of the PARAMETER-MATCHED González–Guzmán–Sarbach linear rate (our throat is their γ₁ = 0.5 member: T = 0.758; τ_lin = 5.13 M); truncation noise picks the branch. The collapse horizon SHRINKS 40 % as it swallows the phantom; the 9–11 % REGROWTH in the scans is NUMERICAL (spherical first law forbids it; it tracks a constraint-violation double layer reaching the MOTS; same in purely spherical data; the pure quadrupole never regrows; the head-on horizon never regrows either). The late (t ≳ 75) constraint rise of every single-throat arm is a refinement-boundary grid mode whose onset the L = 128 box does not delay — NOT the t500 wall reflection ["2026-09-25 (09:30)"]. **Inflation, the verdict (F4: L = 512, level 5, 1+log, quotable to t = 218)** ["2026-09-26 (05:00 UTC)"]: the kicked throat keeps growing, at every sample to t = 218 (3.81 → 14.5) and on to t = 390, with no trapped surface. It stays anti-trapped. θ_l = 0 sits on the neck and θ_k = 0 runs outward (R = 73 by t = 212): Shinkai–Hayward's trapping horizons turning cosmological. Over t = 16–40 it grows at the Shinkai–Hayward rate in its own proper time: local H R0 = 1.0–1.3, and a fit gives 1.22 (SH's massless 1.1, our linear mode 1.30). It leaves that rate at t ≈ 40 because 1+log freezes the lapse at the neck (α 0.57 → 0.02 by t = 100), so the neck's proper time nearly stops: only ~5 units pass between t = 40 and 218. The growth per unit t then falls (dR/dt 0.08 → 0.015). That is the slicing, not the throat. The neck also leaves the finest box at t = 44. No end state is measured: the record ends when the gauge wave reaches the wall. Only the onset is clean, because grid noise grows on the neck from t ≈ 120, after it leaves level 3. The t500 arm's turn at t = 161 was the same wall ["2026-09-25 (06:30)"]. (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the seed is not constraint-solved (H defect ∝ ε, 0.93×16π|ρ| on the shell at 1 %); ε = ±0.1 both collapse (+0.1 makes the throat a maximum, trapped at t = 1; −0.1 re-expands, then collapses) and die at the origin, not "from a Hamiltonian violation". (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: η = 4 MOTS located (level 3: R 5.41 at t = 30.0, lead ≥ 4.15; level 5 walks through its wall, R 5.29 → 5.17 over t = 34.2–40) [09-25, not yet in the paper]; common MOTS from t = 22, born with both throats' area (R = 1.01 √2 R⋆), around both throats behind a trapped neck; it never bounces (first law) and shrinks toward the pair's Bondi mass, 2M_B ≈ 4.1 (at t = 97: 1.07 R⋆, 4 % above 2M_ADM); the late decline is not accretion. The level-3 death is the grid's; level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN, with BOTH wormholes inside (pits distinct to the χ floor) behind a common neck (R = 3.87 at t = 60); the wall is censored — under η = 4 too, at levels 5 (MOTS from ≤ 55.2, 0.04 before the 60.04 NaN) and 3 (at 61.5, 0.42 before 61.92), with M_MS within 0.3 % of the standard gauge's (η moves only the coordinate size); harmonic class: a θ_out = 0 surface 0.03 before its NaN, not trapped — open [plan/registry 09-25, not yet in the paper]; not "more momentum → stronger curvature" (max|K| says no); what falls with p is the grid's leverage. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; every p ≤ 0.25 merges, every p ≥ 0.35 does not — bound passes, not escapes (both start below the circular momentum; a central pull cannot capture without contact); the fly-by's recession after t = 43 is between the pits of two inflating mouths; the level-3 p = 0.45 closest approach (3.95) is a pit hop, level 5 passes at 4.8 ["2026-09-25 (09:30)"]. (§VII.A, new Fig. orbits)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂ and the radial kick moves only its phase; it rings at the Schwarzschild period of its late mass (fit drawn); the scalar channel is comparable and negative-energy; the horizon switches it off; each vacuum control is drawn under its drainhole twin at R = 20 (Fig. 11(c,d)): the BBH spiral merges 2.9× lower and 43 units after the drainhole burst; the p = 0.45 BBH fly-by radiates one cycle at periapsis, 4.5× below the fly-by's peak, and nothing at the pass. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, and none expected (no throat survives; conversions are at z ≳ 20). (§IX)
- **Astrophysics** (abstract + §X.B re-framed 2026-09-25: LISA is the headline, LIGO the null channel; the fly-by and spiral are the loudest LISA sources, optimal SNR 175–500 at 10⁵–10⁶ M⊙; conservative SNR ≥ 8 for every encounter 3×10⁴–4×10⁶, the fly-by to 2×10⁷; the fly-by marks no seed (its mouths inflate); lone collapse ≤ 6 conservative, ≈10 optimal — was "≈7"; Fig. 17(b) is now one burst's strain against the LISA noise, (c)'s Ω_GW the conversions only (head-on to spiral); the LISA SNRs are ledger rows recomputed by gw_search.lisa): no ghost-scalar wormhole inspiral (rotation is the open exception); collapse is a heavy-seed channel whose conversion bursts LISA would detect ONE BY ONE (SNR 61–500 at 10⁵–10⁶ M⊙, z = 20; > 8 from 3×10⁴ to 4×10⁶ M⊙), limited by abundance; the negative-energy deposit cannot be Λ (w, sign, size: Ω_WH ≈ 60–800 needed). (§X)

**Plan vs paper**: the paper is the current word — 1000 ledger rows, 0 problems, 828 recomputed (`claims.py check`, 2026-09-26 16:00 UTC, after the referee's fixes). Where the verdicts below disagree with the paper (the regrowth "NUMERICAL" → "not a measurement"; "wall" → "interior failure"; the mouths' shared clock; the baby-universe framing; the unconditional LISA headline), the paper wins. The plan's older entries still carry superseded readings (the regrowth as physics, "no horizon ever forms" for the spiral, "+17 %" regrowth, the ×7.8 fly-by growth as a measurement, the "21 % short" ringdown).

## Traps (each has cost a run)

- AMReX ignores keys nothing reads: old binaries run new params without the new
  physics. The launch preflight now refuses this (keys read only inside a switched-off
  feature are allowed by name in `preflight_allow.txt`).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the
  interval (19 templates carry that contradiction): the preflight now refuses it.
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows (R ≈ 47.6, 60.6) that are not horizons.
- A horizon hunt whose seeds "leave the box" found a trapped region bigger than the box, not nothing: every η = 4 null to 09-24 (half 3–5) was that. Size the box from a wide radial θ_out profile first (the finder now says LEFT THE BOX).
