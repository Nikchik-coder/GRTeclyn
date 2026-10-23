# Bondi dipole paper — status

One page, current only. Paper: [`bondi_dipole.tex`](bondi_dipole.tex), arXiv:2608.24577 (v1). Data:
[`results/bondi-dipole-runaway/`](../../results/bondi-dipole-runaway/README.md), tag `v1.0-bondi-dipole`. Code:
`Examples/RadialRecipe/`, launcher `grteclyn-wrapper/scripts/campaigns/bondi_dipole/run_pair_selfgrav.sh`. Runs:
`runs/bondi/` (untracked). Writing rules: [`../WRITING_STANDARDS.md`](../WRITING_STANDARDS.md). Branch
`feature/fix_bondi`, cut from `feature/spinning` on 2026-10-22 (develop carries no `research/`; its code is the same).

## Journal trail

- PRD, then CQG: rejected (dates not recorded).
- GRG: sent to review, rejected 2026-10-20 on presentation (undefined symbols and lab vocabulary, too many numbers,
  no convergence test), no invitation to resubmit. The reports are kept locally only, in `referee/` (git-excluded).
- Next: EPJC (open access through SCOAP3; confirm it charges no APC), fallback IJMPD.

## REVISION (from 2026-10-22)

Two tracks in parallel: the text on the workstation, the convergence runs on the cluster. Tick each item as it lands.

### What the packed data say

The runs are uniform-grid (one level), so the pack's boundary-masked norms (`L2_Ham_amr`, `L2_Mom_amr` in each run's
`constraint_norms.dat`) already cover the whole grid. Order between the d₀ = 10 runs, N 128→192 / 192→256, where
the code's order is 4:

| | t 0 | t 10 | t 50 | t 100 | t 200 |
|---|---|---|---|---|---|
| Ham L0 | 1.7 / 0.3 | 0.8 / 0.4 | 1.5 / 1.1 | 1.5 / 1.2 | 1.6 / 1.3 |
| Mom L0 | −1.4 / −1.3 | 1.5 / 0.2 | 1.4 / −0.6 | 1.6 / −0.3 | 1.7 / 0.4 |
| ΔX: Q_meas (Q₂ 2.86, Q₄ 5.94) | – | −0.1 | −3.8 | −6.7 | −10.8 |

- Neither convergence test passes. The constraints converge at order 1.5 at best, and the momentum constraint stops
  converging between N 192 and 256. ΔX is non-monotone from t 50 on, so N 128 is outside the convergent regime.
- Cause found 10-22: the star tables' lapse steps by 4–5 × 10⁻⁵ where each star's integrated interior meets its
  analytic exterior (section 2, "The lapse step"). The paper's runs and the 2a cells used those tables.
- The rise of the domain-wide Hamiltonian norm at t = 0 (2.0 → 3.7 → 5.6 × 10⁻⁴), which App. A and Fig. 4(b)
  attribute to the solve-to-evolution transfer, sits in the box's outer boundary layer: the boundary-masked norm
  falls (2.1 → 1.1 → 1.0 × 10⁻⁶). That explanation goes.
- No plotfiles of these runs survive, so any new norm needs new runs.

### 1. Text (workstation)

Every presentation point of the GRG reports maps to WRITING_STANDARDS §1–7 and its Bondi open items. Done
2026-10-22 (pdflatex and lualatex both build: 13 pages, no overfull boxes, no undefined references):

- [x] Title in normal case; Nachevsky co-author; acknowledgments as in the spinning paper. Abstract rebuilt from
      WRITING_STANDARDS' draft: no undefined symbol, two result numbers, the scope at the end.
- [x] Defined at first use: ADM, NEC, rms, CCZ4, m, λ, μ, ψ, α, K, χ, ρ / Sᵢ / Sᵢⱼ (as projections), a, d, M̄, X,
      ΔX, P, Q. Diagnostics are numbered equations (barycentre, midpoint, fit, Bondi's law, momentum).
- [x] Private vocabulary out of the text and the figure labels (`article_figures.py`): campaign, cell, run matrix,
      rung, ladder, mass-matched, repainted, bicomplex, gap, birth kick, twin, verdict, certifies, nulls, deeper
      solve, box doubling, hill / well, dressed. "Phantom" survives only in its usual meaning (cosmology, ghost
      fields); our sectors are the positive- and negative-mass fields Φ₊, Φ₋.
- [x] Sec. II: the consistency argument has its own paragraph right after the action, tied to the NEC.
- [x] The five tests (Sec. IV C) come before the results; each results subsection opens with its question.
- [x] Table I is the setup (34 simulations, labels PM10, R0.60, E1.34, …); Table II holds the results.
- [x] Results: one number per claim, the rest in Table II; no chronology, no bold sentences. Convergence moved to
      Sec. VII.
- [x] Conclusions as a passage with a scope paragraph; "What is not established" is gone.
- [x] Captions rewritten: what is plotted first, one outcome sentence last.
- [x] App. A: the transfer-residual explanation is gone (the t = 0 rise is the outer boundary layer); App. B (cost)
      folded into Sec. IV A. Fixed on the way: the L = 128 run has Δx 0.50, not 0.25.
- [x] Data availability statement (concept DOI for now).
- [ ] Notation table: about 20 symbols, so WRITING_STANDARDS §2 asks for one. Decide whether it is worth the space.
- [x] Outside-reader test (2026-10-22): a fresh agent reviewed the paper against WRITING_STANDARDS as a PRD referee;
      its ~60 findings are applied (signed mass dipole used consistently, CCZ4 / CTTK / AMR / shift defined at first
      use, a parameter table, E / R / S labels explained, one word per position diagnostic, long sentences split,
      precision matched to the error bars). Kept on purpose: British spelling (EPJC takes either, consistently) and
      the question that opens each results subsection (§6).
- [x] Redundancy pass (2026-10-22): a fresh agent listed what the paper says twice; 24 of its 25 cuts applied (the
      introduction keeps its scope sentence, §5). Abstract 234 → 182 words, text 6608 → 6191 words; still 13 pages,
      which the full-width floats set.
- [ ] After 2b: the convergence paragraph of Sec. VII A, App. A and Fig. 6(b) / Fig. 10 from the new runs (TODO
      comments in the tex; strip all comments before the arXiv upload).
- [ ] Initial data, Sec. III A "Isolated stars" (the lapse step, section 2). Say how each star's profile continues
      past the matching radius, where the field has fallen to 5 % of its central value: the field's exponential tail
      and the exterior Schwarzschild metric in isotropic coordinates, with the lapse matched to the interior in value
      and slope, which fixes α_∞ and the lapse's exterior mass. Also say that the evolution starts from the
      superposed lapse α = 1 + Σ_k (α_k − 1) of the two stars and that Π = −(ω/α) φ₀ uses it: the current "the lapse
      of its own solution" holds only for an isolated star. Describe the construction as it is, not the step
      (CLAUDE.md, the paper). How the other runs enter waits for step 4: if the joined-lapse N 256 reproduces ΔX,
      Sec. VII "Other numerical choices" lists the join with its effect on ΔX(200); if not, those runs need the
      joined lapse too.

### 2. Convergence (cluster)

**Live** (10-23, launched 08:44 MSK, first GPU node; no checkpoints, frames off, binary
`main3d_sgnshells_d2511dca`): the core-drift resolution test, the lone star painted from its profile on a 16-unit box
(centre 8) to t 3, Δx 0.25 / 0.125 / 0.083 / 0.0625. Each `launch.sh` differs from the 64-unit N 256 one only in box,
N, card, stop time, data path and the consumer's spheres (r 4 / 6, inside the box). Box check passed: the N 64 run's
first constraint row equals the 64-unit N 256 run's to all ten printed digits.

| run | card | t (09:16) | stop | speed | ETA |
|---|---|---|---|---|---|
| `diag_direct_lone_p_L16_N64_lev0_t3` | 0 | 3 | 3 | 80 u/h | done 08:46 MSK, no NaN |
| `diag_direct_lone_p_L16_N128_lev0_t3` | 0 | 3 | 3 | 16 u/h | done 08:55 MSK, no NaN |
| `diag_direct_lone_p_L16_N192_lev0_t3` | 0 | 3 | 3 | 7 u/h | done 09:04 MSK, no NaN |
| `diag_direct_lone_p_L16_N256_lev0_t3` | 1 | 2.1 | 3 | 4 u/h | 0.2 h, 09:29 MSK |

Process names (10-23): every Bondi run launched from now on shows as `test params.txt` (run from the shared
checksum-named copy in `/tmp/ml_jobs/bin`) and `test_post post.py`, as the merger runs do (`core/runner.py` with
`GRTECLYN_PROC_LABEL`, set by both Bondi launchers). The four runs above predate it.

**10-23: the cause found, a first-order time integrator.** At the star's centre the lapse drift converges at order
1.0 on the fine grids (Δx 0.125 → 0.083 → 0.0625: 1.09 / 0.99 at t 0.3, 0.98 / 0.98 at t 0.5), and χ there too.
`RadialRecipeLevel::specificEvalRHS` called `FillPatch(*this, a_soln, ...)` on every RK stage; AMReX's FillPatch
overwrites the stage's VALID cells with the old and new state interpolated to the stage time, so RK4's two mid
stages see Uold + k dt/4 instead of Uold + k dt/2. The update becomes 1 + z + z²/3 + …: first order (a replica of
AMReX's RK4 converges at 4.00 clean, 1.00 with the overwrite). For the star's field, whose phase turns at ω = 0.75,
it anti-damps |Φ| at ~ω² dt/6 per unit t, so ρ grows against the geometry: predicted core drift
16π ρ_c ω² dt / 3 = 6.3 × 10⁻⁶ per unit t at dt 0.005, measured 4.4 × 10⁻⁶, same sign. Upstream `BinaryBH` has
no such call (AmrLevel::RK fills the stage ghosts itself, FillRKPatch). Fixed in RadialRecipe only (binary
`main3d_rkfix_aa0dc4a1-dirty`); the same call sits in BinaryWormholeMerger, SpinningWormhole and
SupportedWormholeCollapse, left to their campaigns. The spinning runs' order 3–4 stands: a static phantom field and
a slow collapse make the error ∝ (rate of change)² dt negligible there. Next: the A/B, the four L 16 runs on the
fixed binary (`diag_rkfix_lone_p_L16_N*_lev0_t3`, scripts ready), on the go.

**10-23: the drift starts inside the star** (supersedes "this set cannot split those two" below). The painted
star's interior (r < 5.19) is exact, and nothing from r 5.19 reaches the core (r < 1) before t ≈ 3, even at the
gauge speed √2. Yet the core's signed Hamiltonian grows from t ≈ 1 at −7.9 / −6.1 / −4.4 × 10⁻⁶ per unit t
(N 128 / 192 / 256, t 1–2), order 0.6 / 1.1, and the solved star's core grows the same way. So the drift is made
in the star's interior by the evolution, not by the tail join. Checked and clean: the potential and its derivative
agree, the Klein-Gordon terms and the CCZ4 matter coupling are the standard GRChombo ones, the pump and treadmill
are off. The live test tells whether the core's order climbs toward 4 at finer Δx (the grids are too coarse for the
star) or stays near 1 (an order-1 error in the evolution). Also found: the field's tail is joined at r 5.19 in
value only (a 0.4 % slope kink, ~10⁻⁷ in Ham: too small to drive the drift; the profile should join it C¹).

**The third defect, localized 10-22 evening** (diag runs on the shell-norm binaries 65cc1a98 / d2511dca, which
write `constraint_shells.dat`, the norms in unit shells, L2 and signed mean, every 0.1):
- With both data fixes in, a Hamiltonian violation remains that grows linearly in time at a rate that does not
  shrink with the grid (pair, shells r ≤ 8: ~1.1 × 10⁻⁶/t at both N 192 and N 256), capping the interior order
  at ~1.2 from t ≈ 4. The face repair left the interior orders unchanged (Mom 2.5–3.6 ✓, Ham 1.7/1.2 ✗).
- Not the superposition: the lone canonical star (`diag_lone_p_L64_N128_lev0_t10`, the control_lone recipe on the
  fixed pipeline) grows the same way at half the pair's rate — one star, half the sources. The pair's midpoint
  bump is the two stars' contributions adding.
- Not GRTresna and not the star ODE: `paint_lone_star_direct.py` paints the lone star's data straight from the
  ODE profile (exact to ~1e-10; vs the solved data: phi/Pi/lapse/K equal to 1e-11, only chi differs, by the
  solve's 3.8 × 10⁻⁴). The run from it (`diag_direct_lone_p_L64_N128_lev0_t10`) grows at the same rate
  (0.54 vs 0.66 × 10⁻⁶/t). Exact initial data cannot source a steady constraint drift under a consistent
  evolution, so the defect is in the GRTeclyn evolution (or its diagnostic), not in the initial data chain.
- The fingerprint: the signed mean per shell shows the growth at the star CORE (r < 1), negative, monotonic
  (−9.5 × 10⁻⁶ at t 0 → −2.1 × 10⁻⁴ at t 10 at N 128): the matter's ρ drifts up against the geometry. The field's
  oscillation itself is clean (max φ follows f cos ωt to 4 digits). At the core the quartic and sextic potential
  terms nearly cancel (V ≈ 2 × 10⁻⁵ from ±4 × 10⁻⁴ pieces), so a small inconsistency there is amplified.
- Stopped 21:20 MSK ("lets terminate the runs no point burning gpus"): the PP-pair and lone N 192 solves, the
  unrepaired N 256 control and the two signed pair reruns (log `runs/bondi/staging/stop_diag_2026-10-22.log`);
  superseded by the lone-star verdict. The finished diag runs' episodes are kept under `runs/bondi/staging/diag_*`.
- **Conclusion of the lone-star splitter set (10-22, 22:40 MSK; supersedes the "Not GRTresna and not the star ODE"
  bullet above and the 21:50 reading that put the floor in the solved data):**
  - The direct paint is not exact data. The star profile (`boson_star_ode._build_profile`) puts a vacuum exterior
    (ψ = 1 + M/2r, Schwarzschild-like lapse) beyond the match radius r_m = 5.19 over the field's Yukawa tail,
    which holds 2.75 × 10⁻⁴ of energy (1.9 % of the ADM mass). Hence Ham = −16πρ_tail there: predicted from the
    profile 2.8 × 10⁻⁵ / 7.1 × 10⁻⁶ / 1.4 × 10⁻⁶ / 2.9 × 10⁻⁷ / 6.0 × 10⁻⁸ in shells r 5–10, measured the same
    to 1–2 % (r ≥ 6) at N 128, 192 and 256 alike (order 0). The "defect in the evolution" verdict drawn from
    the N 128 direct run rested on this false premise and is withdrawn.
  - GRTresna repairs ψ there: the solved data's t 0 violation converges at order 2 in every shell (r 5–6:
    3.7 → 1.7 × 10⁻⁶). The lapse and Π₂ = −ωφ/α beyond r_m stay the profile's vacuum-exterior ones.
  - Not the superposition: the SOLVED LONE star reproduces the pair's order deficit in the star body. Ham L2
    per shell at t 10, N 128 → 192: r 0–1 2.75, r 1–2 1.28, r 2–3 1.73, r 3–4 1.17, r 4–5 0.91, r ≥ 5 1.6–2.5
    (pair interior: 1.7 / 1.2). The pair's growth is two stars' worth of the same single-star effect.
  - What remains: a signed drift in r 1–5 (ρ ahead of the geometry), converging at order ≤ 1 on both the direct
    and the solved data. Common to both: the profile's lapse and field tail beyond r_m, and the evolution. This
    set cannot split those two; the splitter would be a profile whose exterior carries its own matter (the ODE
    integrated through the tail, or the lapse solved with the tail), on solved data. Not queued.

**The face-layer step** (found 10-22, the second defect): with a target origin, the Chombo converter's nearest-cell
fallback (`grtresna/io/chombo.py`, `_target_span_slice`) painted each face's outermost cell layer from a solve cell
beyond the evolution box, so chi and the lapse step there by up to 3 × 10⁻⁴ (five of six faces; the matter is
repainted analytically and clean). At t 0 the violation sits in shells r ≥ 29 at 3–8 × 10⁻⁷ and GROWS with N; the
evolution then carries it inward, which is what capped the interior Hamiltonian order at ~1.2–1.5 from t ≈ 4 on
(the paper's runs and 2a/2b/2c all carry it). Fixed in the converter (a source cell whose centre lies outside the
target paints nothing, e3992acf) and, for the already-solved pairs, repaired in copies
`facefix_pair_d10_L64_N*_lev0` by `repair_face_layer.py`: the outermost layer of chi and the lapse set by cubic
extrapolation along each face normal (the solve's HDF5 is deleted after conversion, so the exact values are gone);
`face_repair.json` records the change, everything else byte-identical. After the repair the r ≥ 29 shells sit at
~10⁻⁸ and fall with N.

The t 20 check of the lapse fix (conv2c, launched 19:10 MSK) found this: its interior momentum order is 2.4–3.6
everywhere, but the Hamiltonian falls to ~1.2 (N 192→256) from t ≈ 4, the same as the stepped-lapse runs.
- `conv2c_pair_d10_L64_N256_lev0_t20`: died at t 16.9 with the session restart (20:17 MSK, process killed with the
  shell; no NaN). Data to t 16.9 intact; the facefix N 256 run supersedes it.
- Done: `conv2c_pair_d10_L64_N128_lev0_t20` (19:31 MSK) and `conv2c_pair_d10_L64_N192_lev0_t20` (19:47 MSK), both
  t 20, no NaN, scratch purged. Card 0 idle.
- Same N against the stepped lapse (2a), t ≤ 20: the separation agrees to 1.2 × 10⁻⁴ (N 128 and 192), ΔX is
  1.4 % larger at t 5 at both N (the lapse change itself, not resolution) and 0.01–0.02 % at t 20, and the
  acceleration fitted over 5 ≤ t ≤ 20 changes by −0.3 %. N 128→192 at t 5 / 10 / 15 / 20: Ham 2.4 / 1.7 / 1.6 /
  1.5 (stepped: the same to 0.1), Mom 3.1 / 2.8 / 2.6 / 2.4 (stepped 1.7 / 2.2 / 2.4 / 2.4). The step held down the
  early orders only; the later Hamiltonian cap traced to the face-layer step (above).
- Each starts from `runs/bondi/staging/lapsefix_pair_d10_L64_N*_lev0`: the fixid data with only the lapse replaced
  (`grteclyn-wrapper/scripts/campaigns/bondi_dipole/patch_lapse_join.py`, record in `lapse_patch.json`).
- Start checked: the first step's momentum violation (L2, r ≤ 24) is 5.1 / 1.5 / 0.63 × 10⁻⁸ at N 128 / 192 / 256,
  order 3.0 / 3.05; with the stepped lapse it was 63 / 121 / 180 × 10⁻⁸, order −1.6 / −1.4.

**The lapse step** (found 10-22): the star tables (`profiles/boson_star_ode.py`, `_build_profile`) join the
integrated star to an analytic exterior at r ≈ 5.2, where the field is 5 % of its centre value. The interior lapse
was scaled by α_∞ read as A + B/r, the exterior lapse took the conformal factor's mass, and the two did not meet: the
lapse stepped by +4.3 × 10⁻⁵ (canonical star) and −5.1 × 10⁻⁵ (phantom). The field is smooth there and the lapse
does not enter the t = 0 constraints, so every t = 0 check passed. The evolution's first step turns the step into a
momentum violation growing like N^1.5; the step alone predicts 0.66 / 1.26 / 1.87 × 10⁻⁶ against the measured
0.63 / 1.21 / 1.80 × 10⁻⁶. The 2a cells and the paper's runs have the same tables (byte-identical), so the step is
what capped their order. Fixed at the source: the lapse is joined in value and slope (`_lapse_join`; the exterior
lapse takes the lapse's own mass, 1.7 % above the conformal factor's; α_∞ moves by 4 × 10⁻⁶). The patch writes the
same join into the existing tables and adds the change to the gridinit's lapse (≤ 5.5 × 10⁻⁵); all other fields stay
byte-identical, and the star frequency and interior lapse scale together, so Im Π = −ωφ/α still holds.

Orders so far (19:26 MSK; N 256 at t 3.4), r ≤ 24, N 128→192 / 192→256, joined lapse against the stepped one (2a):

| | t 0 | t 1 | t 2 | t 3 | t 5 |
|---|---|---|---|---|---|
| Ham, joined | 2.1 / 2.0 | 2.7 / 2.6 | 3.0 / 2.8 | 3.1 / 2.1 | 2.4 / – |
| Ham, stepped | 1.9 / 1.6 | 1.1 / −0.7 | 1.6 / −0.3 | 2.5 / 0.3 | 2.3 / – |
| Mom, joined | 3.0 / 3.1 | 2.5 / 2.8 | 3.0 / 3.4 | 2.8 / 3.6 | 3.1 / – |
| Mom, stepped | −1.5 / −1.4 | −0.6 / −1.1 | −0.2 / −0.6 | 0.9 / 0.0 | 1.7 / – |

From t 1 on, the boundary-masked norm, which adds the absorbing layer and the outer cells, matches the stepped runs'
to ±0.1 (orders −2.2 to 0.6 at t ≤ 3): the outer region sets it, not the stars. The full t 20 table follows when
N 256 ends.

- Stopped and wiped 18:59 MSK on the word ("all current runs should be stoped and wiped"): the three 2b t 200 runs
  (N 128 at t 29.9, N 192 at t 55.8, N 256 at t 12.4), which started from the stepped lapse. Run dirs and 9 GB of
  scratch deleted, logged in `runs/wormhole_merger/manifests/MANIFEST_CLEANUP_2026-10-22.md`. Up to then their
  orders matched 2a's to ±0.1 (the 2a fix removed 6–15 % of the t = 0 violation, not the cap).
- Decided 10-22: the study is N 128 / 192 / 256 on the fixed data; no N 320 ("i see no reason for 320"). N 384 would
  not fit this node anyway (~195 GB of GPU memory, ~750 GB for its solve). Frames stay off on these runs: the star
  tracks, separation and acceleration come from `small_data/sector_dynamics.dat` and `sector_barycenters.dat`.
- Paper check 10-22 (t ≤ 38): the 2b N 192 reproduced the paper's N 192 run, ΔX to 0.27 %, d to 4 digits, the
  acceleration fitted over 5 ≤ t ≤ 38 to 0.5 %. In the paper's own runs the barycentre separation dips to 9.71
  (−2.9 %) at t ≈ 51 before returning to 9.91; the text's "constant to 1 %" holds only for the net change (Table
  results: −0.9 %) and the proper core distance (+0.24 %). Reword in the revision.
- Done: plan step 2's three solves (CPU, N 128 / 192 / 256 done 17:20 / 17:37 / 18:11 MSK).
- Done: `conv2b_pair_d10_L64_N128_lev0_t20`, card 1, 17:28–17:38 MSK: the 2a N 128 cell on the fixed data (only the
  gridinit changes), t 20, no NaN, scratch cleared. At N 128 its norms match 2a's to 0.1 % (the fix hides under the
  solve's own error there); it is the gate's third rung.
- Near-miss 17:22 MSK: the first N 128 launch from a gridinit re-solved a star for the unused pump width and reached
  96 GB in Python beside the two solves (container 475 of 524 GB); killed in time, nothing else lost. The launches now
  pass the old cells' width (`RL_PUMP_TARGET_WIDTH`, a new wrapper knob), which skips that solve.

The three 2a cells ran on the first GPU node on
10-22 (done N 128 13:13, N 192 13:41, N 256 15:08 MSK; 207 / 49 / 16 units/h), all to t 20 with no NaN and their
scratch cleared. Each reproduces its archived run over
t ≤ 20 to 1 % (L2 norms) and 1.5e-6 (Linf_Ham_amr). Run dirs `runs/bondi/staging/conv2a_*`, each with its `launch.sh`
(diffed against the old cell: only the stop time, frames off, the binary, solve ranks and timeout change) and its t = 0
split in `t0_constraints.log`. The solve stops at 0.002 % × (128/N)⁴ relative error (16 Newton iterations at N 256).
No checkpoints. Scratch on the node: empty (the 29 GB of two dead spinning runs' plotfiles wiped 10-22 on the word).

- [x] An interior norm in `Examples/RadialRecipe` beside the boundary-masked one: drop the outer boundary layer and
      the sponge (r > 24), as `SpinningWormhole`'s `constraint_norms_levels` does. Rebuild and record the binary.
      Code reaches the nodes only by push and pull.
      Done 10-22 (8d0771d4): `constraint_norms.dat` cols 18-19, `L2_Ham_int` and `L2_Mom_int`, are the
      boundary-masked norms (cols 12-13) restricted to r ≤ `constraint_norms_interior_radius` (default: the sponge's
      inner radius, 24). Binary `runs/bondi/bin/main3d_intnorm_37ae5be1_2026-10-22.ex` (sha256 f5ca01e5fb417458,
      AMReX 26.02-12-gd7da5045, nvcc 12.1, sm_90). It is stamped 37ae5be1, the same commit before the rebase onto
      the paper commits: Source/, the example and Tools/GNUMake are identical in 8d0771d4. `run_pair_selfgrav.sh`
      takes it as `BONDI_BINARY` (unset: the example's own build, as every archived cell ran). Source/ has changed since the archived runs' a6d9dccb, so the
      2a runs' existing columns are checked against the archived rows over t ≤ 20.
- [x] 2a. Diagnosis: short runs (t ≤ 20) of the d₀ = 10 pair at N 128/192/256 with the interior norm, plus a CPU
      check of each initial-data set's t = 0 constraints. It finds what caps the order: the second-order GRTresna
      solve, a mismatch between the matter the solver used and the matter painted on the evolution grid, or
      under-resolved stars. Without it, N 320 may only reproduce order 1.5.
      Suspects found in the code (10-22), for the CPU check to size: the solve's Im Π divides by each star's own
      lapse, the painted Im Π by the summed lapse (the companion's α − 1 enters, independent of N); the solve
      interpolates the star tables linearly and differentiates the interpolant, the evolution paints a cubic spline
      and differentiates on the grid. The gridinit and the star tables are kept for it.
      Done 10-22. Orders N 128→192 / 192→256 from
      `grteclyn-wrapper/scripts/analysis/bondi_dipole/constraint_orders.py` (r ≤ 24 is the interior norm, "box" the
      boundary-masked one):

      | | t 0 | t 5 | t 10 | t 15 | t 20 |
      |---|---|---|---|---|---|
      | Ham r ≤ 24 | 1.9 / 1.6 | 2.3 / 0.6 | 1.7 / 1.1 | 1.6 / 1.1 | 1.5 / 1.2 |
      | Mom r ≤ 24 | −1.5 / −1.4 | 1.7 / −0.8 | 2.2 / 0.2 | 2.4 / 0.9 | 2.4 / 1.4 |
      | Ham box | 1.7 / 0.3 | 0.9 / 0.3 | 0.8 / 0.4 | 1.1 / 0.6 | 1.3 / 0.7 |
      | Mom box | −1.4 / −1.3 | 0.9 / 0.3 | 1.5 / 0.2 | 1.9 / 0.4 | 1.6 / −0.3 |

      The t = 0 split (`t0_constraints.py`, L2 over r ≤ 24, N 128 / 192 / 256): total 4.1 / 1.9 / 1.2 × 10⁻⁶; the
      solve's second-order truncation error 3.5 / 1.6 / 0.94 × 10⁻⁶ (order 1.9); the Im Π lapse 4.55 × 10⁻⁷ and the
      table derivative 3.5 × 10⁻⁷ at every N (order 0); the grid gradient of the painted stars 7.4 / 1.7 / 0.57 × 10⁻⁷
      (order 3.6–3.8: the stars are resolved). The solve's own residual comes out at 10⁻⁹–10⁻¹⁰, so the split
      reproduces the solve's matter.
      Verdict: the solve caps the order at 2. The two fixed mismatches are half the t = 0 total by N 256, which fits
      the interior order falling to about 1 between N 192 and 256. The momentum constraint's first-step jump grows
      with N (r ≤ 24 at t = dt: 0.6 / 1.1 / 1.7 × 10⁻⁶, from 10⁻⁸ at t = 0), so something injects grid-scale error;
      the likeliest source is the table derivative, whose error is a sawtooth at the table's spacing sampled at the
      grid points. The box norms are held down by the region outside r 24, where the sponge acts; the order is read
      inside r ≤ 24.
**The error found (2a, 10-22).** The initial-data solver (GRTresna) and the evolution describe the stars differently
in two places, so every run starts with a constraint violation of about 8 × 10⁻⁷ (L2 over r ≤ 24) that is the same
at every resolution:

1. The U(1) momentum Im Π: the solve divides by each star's own tabulated lapse, the painted data by the summed lapse
   of the grid, 1 + Σ(α_k − 1), so the companion's α − 1 ≈ ±1.4 × 10⁻³ enters (4.55 × 10⁻⁷).
2. The gradient term |∇φ|²: the solve differences its linear interpolant of the star table, the evolution
   differentiates the painted cubic spline on the grid (3.5 × 10⁻⁷). Its error is a sawtooth at the table's spacing
   sampled at the grid points, the likeliest source of the momentum constraint's first-step jump.

At N 128 it hides under the solve's second-order error; by N 256 it is half the total, and the interior order falls
from about 2 to about 1. The stars are resolved and the evolution is not at fault. The solve itself stays second
order, so a fixed solve converges at 2 (the spinning paper's bar), not at the evolution's 4.

**Plan to a convergence pass** (decided 10-22; about 2.5–3 days from the go):

- [x] 1. Fix the solve's matter in GRTresna: Im Π with the summed lapse, as painted, and |∇φ|² from the profile's
      exact (spline) derivative. A few hours; record the GRTresna build as the evolution binary is recorded.
      Done 10-22: GRTresna branch `fix/bondi-solve-matches-painter` at 9a85e6a, built in its own worktree
      `GRTresna_bondi_fix` beside `GRTresna`, so the main checkout and its 08-06 binary stay as they were (the 2a
      cells ran on that binary). The star tables are now the painter's natural cubic spline (the C++ spline equals
      scipy's on the tables to 5 × 10⁻¹⁶), ∇φ its exact derivative, and Im Π divides by the summed lapse. The lapse
      column is splined too, so the initial lapse loses the same sawtooth (it does not enter the t = 0 constraints).
      Binary sha256 94a12c672f972e62, frozen as `runs/bondi/bin/grtresna_BosonStarBH_9a85e6a_2026-10-22.MPI.ex`. The
      unfixed HEAD rebuilt the same way reproduces the old binary's first Newton iteration to all printed digits
      (25.00075 / 24.29425 % at N 128). This container has no `/bin/csh`: build with
      `CSHELLCMD="$GRTRESNA_ENV/bin/csh -f -c"`. `run_pair_selfgrav.sh` gains `BONDI_SOLVE_ONLY=1` (solve and
      gridinit, no GPU); `t0_constraints.py` gains `--solve matched|legacy` (the 2a data are `legacy`).
- [x] 2. Check at t = 0 (~1.5 h, CPU only): re-solve N 128/192/256 together (N 256's took 68 min and 221 GB on
      12 ranks) and rerun `t0_constraints.py`. The two terms must vanish and the total keep order 1.9 at both steps.
      The N 192 and N 256 data carry over to step 3.
      Live (see above): `GRTRESNA_ROOT` points the launch at the worktree; all 24 ranks run its binary. The new
      solves converge as the old ones did (12 / ~13 / ~16 Newton steps, each cutting the error ~2.5×).
      N 128 (`t0_constraints.py --solve matched`, L2 over r ≤ 24): the Im Π term 4.55 × 10⁻⁷ → 8 × 10⁻²⁰, the
      gradient term 3.5 × 10⁻⁷ → 0, interp 3 × 10⁻⁹ → 10⁻¹³; the solve's residual with the rebuilt matter
      5.0 × 10⁻⁹ (the solve's tolerance), so the solve really used the new matter. The total stays 4.1 × 10⁻⁶, as
      expected at N 128 (the solve's own 3.5 × 10⁻⁶ plus the evolution's stencil 7.4 × 10⁻⁷). Also gone: a spurious
      A_ij ~ 10⁻⁷ (now 4 × 10⁻²⁰) and Mom 7 × 10⁻⁹ (now 2 × 10⁻²¹). The wrapper writes each star's frequency
      into `lump{k}_omega`, which GRTresna reads as a rigid rotation rate; with the finite-difference gradient the
      rotation term ω(x ∂_y φ − y ∂_x φ) most likely did not cancel and sourced a small Re Π and S_i the painter
      never had.
      N 192: the same (Im Π 7 × 10⁻²⁰, gradient 0, residual 2.0 × 10⁻⁹); the total 1.89 → 1.77 × 10⁻⁶; order of
      the total N 128→192 2.07 (was 1.9). The momentum constraint's first step is unchanged at N 128 and N 192
      (6.3 × 10⁻⁷ and 1.21 × 10⁻⁶ at t = dt, 2a 6.1 × 10⁻⁷ and 1.14 × 10⁻⁶), so that jump is not from the two
      mismatches.
      Done 10-22 18:12 MSK, passed. L2 over r ≤ 24 at N 128 / 192 / 256: total 4.10 / 1.77 / 0.985 × 10⁻⁶ (old data
      4.09 / 1.89 / 1.20), order 2.07 / 2.05 (old 1.91 / 1.65); the Im Π and gradient terms ≤ 10⁻¹⁹ at every N; the
      solve's own error order 1.87 / 1.93; the evolution's stencil on the painted stars order 3.6 / 3.8. Logs:
      `fixid_pair_d10_L64_N*_lev0/t0_constraints.log` (the N 256 one holds all three and the orders).
      First look at the evolution, N 128→192 (the N 128 t 20 rung and 2b's N 192), r ≤ 24 Ham / Mom at t 0 5 10 15 20:
      2.0 / −1.6, 2.3 / 1.7, 1.7 / 2.2, 1.5 / 2.4, 1.5 / 2.4, the same as 2a's to ±0.1. N 192→256 decides the gate.
- [ ] 3. 2b, the resolution study N 192/256/320 (Δx 0.33/0.25/0.20) at L 64 to t 200 (~2 days, ~50 GPU-h; expected
      Q₂ 2.16, Q₃ 2.81, Q₄ 3.66). A rerun is its old run: start from `campaign/runaway_pair_d10_L64_N256_lev0`
      (`evolution_params.txt`, `launch_config.sh`) and change only N, the Δx-scaled solve tolerance and the
      diagnostics. N 192 and N 256 go first, one per card (4 h and 13 h at today's speeds). Gate at t 20, about 1.5 h
      in: the r ≤ 24 order N 192→256 must be about 2, or stop and look again. N 320 then runs on both cards (about
      94 GB). Its 640³ solve needs about 430 GB and 2.5 h on 12 ranks, scaled from N 256, close to the container's
      524 GB: start it only with that much free, under a per-rank cap (CLAUDE.md, the OOM rule), never beside another
      solve.
      10-22: N 320 dropped, the study is N 128 / 192 / 256. The t 200 runs were stopped for the lapse step (above);
      they restart from the `lapsefix_*` data once the t 20 check gives an order near 2 for N 192→256.
- [ ] 4. Compare 2b's N 256 with `campaign/runaway_pair_d10_L64_N256_lev0`, the same run on the old data. If the
      drift ΔX agrees, the paper's other runs stand, and the paper says the convergence runs use the corrected
      data. If it does not, those runs need the corrected data too.
- [ ] 5. The pass: the r ≤ 24 order table and ΔX's self-convergence over t 200, into a convergence appendix with the
      rescaled ΔX differences and the rescaled Hamiltonian and momentum norms, the order stated in words. The N 128
      scans stay, quoted as ratios with the base-grid offset stated.

### 3. Release and submission

- [ ] Merge into develop without `research/`, tag (e.g. `v1.1-bondi-dipole`), GitHub release, then Zenodo
      "Sync now" (CLAUDE.md, Publishing) and check the version DOI under concept 10.5281/zenodo.23245933.
- [ ] arXiv v2 of 2608.24577: account page → Articles You Own → Replace icon → upload the full source again (tex,
      bbl, figures, `anc/` movies) → compiler **pdflatex** → update the abstract and comments ("v2: presentation
      revised, convergence study added") → submit. Same identifier; v1 stays visible. The monthly cap counts new
      submissions only (two per calendar month, three active); replacements have their own limit, one per week
      after v5.
- [ ] Journal submission (EPJC), on the same day as the v2.

### After Bondi

The merger paper (arXiv:2610.13206), withdrawn from GRG on 2026-10-22: the same writing pass, then its own arXiv
replacement and the next journal.
