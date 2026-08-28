# Rotating Wormhole Collapse — consolidated plan, lab record and open work

Single source of truth for the rotating-wormhole line of work. Merged 2026-08-28
from four separate documents (`RotatingWormholePlan.md`, `OrbitalPumpPlan.md`,
`NextSteps.md`, `PRDM2CampaignPlan.md`), which are deleted — everything
load-bearing in them is here.

The manuscript and figures live in [`article/`](article/). This file is the **lab
record**, not paper prose.

**Where the project stands.** A rotating Q-torus wormhole, held open by a support
coupling, collapses on command when the support is ramped off and radiates a
gravitational-wave burst — with no imposed perturbation. That is the headline and
it reproduces on three grids. Three things are honestly unfinished: there is no
clean non-rotating control, the in-code C++ waveform extraction is broken (the
Python one is used instead), and the burst is **matter-driven, not
rotation-driven** — which, as §8 shows, is close to a theorem for this
configuration rather than a fixable defect.

---

## 1. Headline result (2026-07-16) — collapse-on-command produces a GW burst

**Run.**
`runs/rotating_wormhole/evo_omega_p0p25_m1_kappa_1p00_dx0p5_ml3_mass0p5_qball_lam170_mu614450_torus_wh_collapse_ml3_gw`
(m=1, ω=0.25067, κ=1.0, N=128, dx=0.5, `max_level=3`, t→40, dense in-code Weyl4 +
Python Ψ₄ extraction.)

**No kick.** `wormhole_phi_perturbation_amplitude = 0`,
`wormhole_phi_monopole_amplitude = 0`. The *only* trigger is the support ramp
`support_ramp_t_start=8 → support_ramp_t_end=10`, `support_ramp_floor=0`.

| Quantity | Result |
| --- | --- |
| `min_lapse` | 1.000 → **9.85e−4**, recovering to 0.033 at t=40 |
| `min_chi` | → **0.0185** (throat pinch) |
| `max\|K\|` | → 0.62 |
| Trapped-surface proxy | **forms**: `max_ah_r = 9.18`, `min_theta_plus = −1.90` |
| Constraints | Ham L2 ≤ 3.25e-2, Mom L2 ≤ 9.67e-3, flat to t=40, no NaN |
| GW (Python ℓ=2,m=0) | near-zone response t≈6–8, **main burst t≈13–24**, then decay |
| Extraction sanity | m=0 imaginary part RMS ~1e-5 (≈0, as required) |

Causally consistent: support off at t=8–10 → throat collapse → proxy horizon →
radiation reaching r=12. `small_data/psi4_mode_l2m0.dat` already stores **rΨ₄** —
do not multiply by radius again.

**Reproduce the figures** (see `grteclyn-wrapper/README.md` §Visualization):
```bash
RUN=runs/rotating_wormhole/evo_omega_p0p25_..._torus_wh_collapse_ml3_gw/output
bash grteclyn-wrapper/scripts/plot/plot_diagnostic.sh "$RUN" 12 18 24
bash grteclyn-wrapper/scripts/plot/make_movies.sh   "$RUN" --framerate 10
```

### Caveats attached to the headline

- **No non-rotating control** (see §6, A3). Three attempts failed; burst
  attribution rests on m=0 power dominance in the rotating run, not on a twin.
- **No global conservation.** `J_z` drifts ~141% and `Q_total` ~116% (both change
  sign). ∫pump_work = 0, so this is **not** pump injection. `Q_sphere` is retained
  (~5% drift). Do not quote global conservation.
- **The in-code C++ Weyl4 output is buggy** — see §7. Physics uses the Python
  post-hoc extraction.
- **"Collapse anytime on command" is not demonstrated.** What is demonstrated is
  "early support cut → deep collapse + GW". No-ramp and late-ramp both NaN near
  t≈19 without ever reaching deep lapse (§6, A1).
- **M_ADM ≈ 0.209**, not 1. Any physical-unit claim must be anchored to it; older
  169 Hz / 5 Hz numbers assumed code mass = 1.

---

## 2. Verified file map

All paths relative to repo root `GRTeclyn/`.

| What | Where | Status |
| --- | --- | --- |
| Wormhole evolution example | `Examples/RotatingWormholeCollapse/` (`Main_SupportedWormhole.cpp`, `SupportedWormholeLevel.cpp`, `SimulationParameters.hpp`) | builds CPU + CUDA; `complex_scalar` branch (~line 241) uses `ComplexExoticScalarField<ComplexScalarPotential>` |
| Matter class used | `Source/Matter/ComplexExoticScalarField.{hpp,impl.hpp}` | has the pump hook + 7-arg `add_matter_rhs(...,coords,time)` |
| Pump reference implementation | `Source/Matter/ComplexScalarField.{hpp,impl.hpp}` | PD target-soliton drive ~lines 146–215 (`k_p>0` closed loop; `k_p<=0` legacy open loop) |
| Trajectory machinery | `Source/GRTeclynCore/RL/{TrajectoryParams,TrajectoryEvaluator,RLMatterPumpParams,RLLumpState}.hpp` | complete, example-agnostic |
| Wiring reference | `Examples/RadialRecipe/` — params ~94–123, per-step update `Main_RadialRecipe.cpp` ~38–110, `build_rl_pump()` in `RadialRecipeMatterDispatch.hpp` ~70–130 | validated in QD campaigns |
| GRTresna multi-lump ID | `../GRTresna/Source/Matter/BosonStarParams.hpp` — `num_lumps` + per-lump `lump<k>_{amp,width,center,velocity,omega,mode,exotic,winding,profile,profile_path}` (~499–540) | multi-lump, per-lump velocity + exotic flag supported |
| Single/constellation ID driver | `grteclyn-wrapper/scripts/wormhole/id/solve_kappa_family.{sh,py}` | κ family, `NUM_LUMPS/ORBIT_RADIUS/ORBIT_OMEGA` |
| 2D Q-torus ID driver | `grteclyn-wrapper/scripts/wormhole/id/solve_torus.{sh,py}` | genuine spinning eigenstate, GRTresna profile 4 |
| Torus eigenstate solver | `grteclyn_wrapper.grtresna.profiles.qball_torus` | bordered Newton + amplitude continuation |
| Run CLI | `grteclyn-wrapper/scripts/wormhole/run/wormhole_case.{sh,py}` | renders params from template + flags, launches with plotfile-deleting sidecar |
| Embedding diagrams | `grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_embedding.py` | 3-panel to-scale funnel / cross-section / equatorial \|Φ\| |
| Postrun tools | `scripts/wormhole/postrun/{adm_quantities,charge_energy_budget,psi4_extrapolate,richardson_convergence}.py` | ADM integrals, ΔJ/ΔQ/E_GW proxy, 1/r fit, Richardson/GCI |

### `collapse_diagnostics.dat` column map (1-based)

This has burned us once — an early Phase-3 table was read with an off-by-one map
and reported `min_lapse` as `min_chi` and `rho_sum` as `J_z`.

```
1 time   2 min_lapse   3 min_chi   4 max_abs_K   5-7 min_lapse_xyz
8 max_ah_r   9 min_theta_plus   10 r_at_min_theta_plus
11 min_phi  12 max_phi  13 min_Pi  14 max_Pi   15-17 barycenter_xyz
18 rho_sum  19 J_z  20 Q_total  21 Q_sphere  22 rho_sphere  23 pump_work
```

All global integrals (`Q_total`, `Q_sphere`, `J_z`, barycenter) are computed on
the **level-0 synchronised grid**, so they are AMR-correct.

---

## 3. Lessons already paid for — do not relearn

| # | Lesson | Evidence |
| --- | --- | --- |
| L1 | **Frozen prescribed sources are fatal.** `EffectiveTeoMatter` (empty `add_matter_rhs`) diverges on unigrid, spin-independent, no gauge choice rescues it. Matter must co-evolve | `weak_spin ≡ a0` blow-up; Ham → 2.21 under fixed gauge |
| L2 | **Never evolve finer than the ID file's native dx** — trilinear `ExternalGridInitialData` interpolation makes C0 kinks → NaN at the throat. AMR below native dx is OK only with `regrid_interval` given **one entry per level** (AMReX aborts otherwise) | `max_level=5` crash at t≈0.13; `ml=1` NaN at t≈0.17 |
| L3 | **A single real scalar cannot rotate smoothly** — `cos(mφ)` density modulation *is* the four-lobe pattern, and it disperses | first rotating run |
| L4 | **The cure is a complex phantom scalar with phase winding**: Φ = f(r,θ)e^{i(mφ−ωt)}, axisymmetric \|Φ\|², J_z from the winding | Route B design |
| L5 | **GRTresna rotating solves work** — ω=0.05 lump converged Ham 0.74%, Mom 0.012%, evolved cleanly to t=4.0 | 6 Jun validation |
| L6 | **Disk discipline.** Never launch the bare binary. `plot_interval ≥ 10`, consumer sidecar with `--delete --keep-last 2` running *during* the evolution, checkpoint pruning on exit | 112 GB incident |
| L7 | **`Q_sphere` (col 21) is the confinement metric — never `rho_sum` (col 18).** At unigrid `rho_sum` ≈ the conserved box total, so it stays flat *even as the matter leaves the throat* | Rung 1a: `rho_sum` 0.50→0.39 while `Q_sphere` → 0 |
| L8 | **Coupled potential only.** The complex branch must evaluate `ComplexScalarPotential` on \|Φ\|², never per-component — the quartic/sextic is non-separable, and per-component evaluation silently breaks U(1) and the Noether charge at t=0 | correctness fix, Rung 1a |
| L9 | **Param consistency across codes.** `phantom_mass` (evolution) == `scalar_mass` (solve); same λ, μ₆ both sides; shared convention `V = ½μ²\|Φ\|² − ¼λ\|Φ\|⁴ + ⅙μ₆\|Φ\|⁶` | — |
| L10 | **Exotic amplitude ceiling.** Total painted exotic amplitude near the 0.1-equivalent; Lichnerowicz divergence shows up as Ham stuck ≫ 1%. Reduce per-lump amplitude or raise lump count — do not fight the solver | natural φ_c≈1.3 Q-ball: Ham 84.96% / Mom 37.2% |
| L11 | **Gauge kick is built in.** Maximal-slicing (K=0, α=1) ID loaded into a 1+log evolution spikes `max_K` ≈ 2.2 at t ≈ 0.5. Keep it (all baselines share it) but note it; `--initial-lapse-type 1` is the lever if it interferes | boundary study |
| L12 | **The pump violates Bianchi by design.** Constraint drift proportional to pump work is expected and *scored*, not a bug — but growth > ~5× initial means gains too high or governor mis-set | Phase 4 |

**On "Teo":** the literal Teo metric is a stationary *geometry* with unspecified
matter; evolving it as a frozen source is exactly L1 and cannot work. The correct
physical target is a **rotating phantom-scalar wormhole** (Kleihaus–Kunz class),
which limits to Ellis–Bronnikov at ω=0. The analytic-Teo `.gridinit` path is
regression-only.

---

## 4. How we got here — the physics record

Ordered by what was learned, not by date. Every entry is a completed measurement.

### 4.1 Constraint-clean initial data is what makes rotation work (Phase B, 2026-07-08)

The first production 128³ pair said rotation was unstable. It was not:

| Run | Init L2_Ham | Trend | min_lapse | Outcome |
| --- | --- | --- | --- | --- |
| Static ω=0, m=0 | 0.0097 | *decreases* → 0.0027 | holds ~0.91 | **stable, throat holds** |
| Rotating ω=0.05, m=1 (analytic ID) | 0.029 (3×) | *grows* | 1.0 → 0.31 | **NaN at t≈2.8** |

The rotating analytic ID starts with a 3× larger Hamiltonian defect — the O(ω)
`K_ij = 0` momentum-constraint defect — which grows and destroys the run. Feeding
the same evolution a GRTresna-solved `.gridinit` removes it:

| Quantity | Analytic ID | **GRTresna solved ID (κ=1, ω=0.05)** |
| --- | --- | --- |
| Outcome | NaN at t≈2.8 | **stable to t=3.5, no NaN** |
| Ham | 0.029, growing | 5.7e-3 → **2.2e-3, decreasing** |
| Mom | growing | 6.6e-4 → **1.3e-4, decreasing** |
| J_z | — | **conserved: 77.5677 at t=0 and t=3.5** |
| Throat | collapses | **holds**, min_chi 0.86 → 0.98 |

**The rotating instability was numerical, not physical.** κ ∈ {1.0, 0.9, 0.7, 0.5}
IDs solve to Ham ≤ 0.99% / Mom ≤ 0.77%; at dx=0.5 with `max_level=3` all evolve to
t=8 with constraints bounded and decreasing and no cross-level kinks.

The **amplitude-reduction trigger** is the reason the κ family exists: paint the
throat with a reduced amplitude f → κf and let GRTresna re-solve both constraints.
The result is an exact Einstein solution that simply is not in equilibrium, so it
evolves with **zero** initial constraint defect — unlike the article's `S_support`
trigger, which injects a t=0 defect that then grows.

### 4.2 The "exotic Hamiltonian never converges" blocker was a diagnostic artefact

Every exotic (ρ<0) complex solve reported Ham pinned at exactly 100% for every
nonlinear iteration. The solve was fine; the *metric* was broken.

`Diagnostics.impl.hpp`'s `c_Ham_abs` normaliser summed `+24πG·rho` **without
`abs()`**, while every sibling term used a magnitude. For ρ<0 under maximal
slicing the converged constraint drives `12·lap(ψ)·ψ⁻⁵ → −24πGρ`, so the signed
term cancels the Laplacian term, `c_Ham_abs → 0`, and `Ham/Ham_abs` divides by ~0.
The real-scalar path escaped it only because its mixed-sign ρ never fully cancels.

Fix: `abs(emtensor.rho)` in `c_Ham_abs`, plus per-iteration `max|dψ|` /
`psi_reg` instrumentation in `GRSolver::run()` that positively confirmed the
ψ-solve had been moving all along (`dψ 0.049→0.001`, `psi_reg 1.0→0.896`).
Post-fix the same config converges `100 → 40.4 → 19.3 → 9.8 → 5.1 → 2.7 → 1.4 →
0.76 %` alongside Mom → 0.63%.

**Generalisable lesson:** eight controls were run against the wrong hypothesis
("only the matter class flips the outcome") before anyone questioned the
denominator. Both classes converged; only one *reported* it.

Two real GRTresna edits were needed and are in (`ComplexScalarField.cpp` +
`BosonStarParams.hpp`): genuine phase winding (φ₁=f cos mφ, φ₂=f sin mφ,
Π₁=(ω/α)φ₂, Π₂=−(ω/α)φ₁ — previously `phi2 ≡ 0` and rotation was faked by a
*real* `cos(mφ)` modulation, i.e. exactly L3), and a two-channel momentum density
`Sᵢ = −(Π₁∂φ₁ + Π₂∂φ₂)` so the winding actually sources `j_φ`. The momentum
sector then solves to **Mom ≈ 0.009%**.

### 4.3 Why the matter disperses — physical, and boundary-timed

Box-size test (κ=1.0, ω=0.05, m=1, dx=0.5, ml=3, L=96 vs L=64, to t=46):

| Quantity | L=64 (r_bdy=32) | L=96 (r_bdy=48) |
| --- | --- | --- |
| `rho_sum` half-gone | t≈4.7 | **t≈5.1** |
| `rho_sum` ≈ 0 | t≈5.0 | **t≈6.0** |
| Horizon | none | none |
| min_chi | → 0.91 (opens toward flat) | → 0.91 |

Dispersal time moves with the box, and `boundary_flux.dat` shows a clear
net-outward peak at t≈5.6 coincident with the `rho_sum` collapse. So the matter
**does** leave through the Sommerfeld faces, and *when* it fully leaves is
boundary-set — but *that* it leaves is physics, for two compounding reasons:

1. **Phantom-scalar wormhole equilibria are dynamically unstable.** The
   Ellis–Bronnikov / massless-ghost throat has an unstable fundamental radial mode
   (Gonzalez–Guzmán–Sarbach 2009; Shinkai–Hayward 2002). GRTresna gives a genuinely
   constraint-satisfying slice, but it sits on an unstable saddle. Here the seed is
   the L11 gauge transient.
2. **No confining potential.** A massless ghost spreads as dispersive radiation;
   there is no well to hold the cloud together.

The throat *geometry* is fine throughout — constraints decrease, min_chi rises
smoothly. What fails is **matter confinement**, not the metric solve. The
rotating equilibrium doesn't collapse; it evaporates its own support and relaxes
toward flat.

### 4.4 A bare mass does not confine — the profile must be a bound eigenstate

Threading a field mass μ through both codes (`MASS` → `scalar_mass`, `--mass` →
`phantom_mass`) only *delays* dispersal:

| μ | peak `rho_sum` | dispersal |
| --- | --- | --- |
| 0.1 | ~100% (no spike) | ~t=13, → 0 by t=15 |
| 0.3 | **219%** @ t=5 | crashes t=5→6 |
| 0.5 | **266%** @ t=5 | crashes t=7→8.5 |

Deeper wells make the cloud *spike then crash harder*, not plateau. The cause is
that the painted lump was an **analytic Gaussian** (`lump0_profile = 0`), which is
not a stationary eigenstate of *any* massive Klein–Gordon operator. A Gaussian is
a superposition of many radial modes; the non-eigenstate part radiates away
whether or not there is a mass term. A mass shifts the dispersion relation (hence
the ~1 M delay) but cannot turn a non-eigenstate into a bound one.

Note also: `min_chi` drifts *above* 1 for μ ≥ 0.3 (deeper-well contraction, not a
horizon — `min_theta_plus` stays > 0), and **late-time rebounds are
boundary-reflection junk**, not revival.

**Ordering correction worth keeping.** The plan originally preferred
`PROFILE_SELFGRAV_BOUND` (self-gravitating boson star) "because it needs no C++
change". That is physically wrong for a phantom field: a boson star is bound by
its *own gravity*, which is effectively repulsive when the field sources gravity
with the phantom sign. Only the **Q-ball** (`PROFILE_ODE_BOUND`) binds through its
potential, a mechanism independent of the gravitational sign.

### 4.5 The Q-ball trilemma — both amplitude regimes fail, for different reasons

*Rung 1a (2026-07-12).* Q-ball profile implemented end to end (coupled potential
L8, `LAMBDA`/`MU6`/`LUMP_OMEGA` in the ID driver, Noether-charge diagnostics
L7). Against a Gaussian baseline at ω=0.05, both lose `Q_sphere` by t≈15–18. The
Q-ball did **not** confine better, because at the throat-convergent amplitude
(amp≈0.1, forced by L10) the nonlinear binding terms are ~10⁻³–10⁻⁵ — the
"Q-ball" is effectively a free massive field with a non-eigenstate shape. At its
natural amplitude φ_c ≈ 1.3 the solve diverges (Ham 85% / Mom 37%).

*Rung 1a′ (2026-07-13).* Removed the clash by stiffening the couplings so the
Q-ball's *natural* φ_c ≈ 0.1 equals the throat-convergent amplitude. Three IDs at
N=128, dx=0.5, all Ham ≤ 0.91%:

| ω (λ, μ₆) | `Q_sphere` retained at t = 6/10/15/20/30 | Q half-life | throat |
| --- | --- | --- | --- |
| 0.05 (170, 14450) | 0.99 / 0.92 / 0.56 / 0.27 / **0.05** | 15.8 | 0.63 → 0.87 (opens) |
| 0.30 (160, 12800) | 1.00 / 0.95 / 0.31 / 0.08 / **0.01** | ~14 | 0.61 → 0.98 |
| 0.40 (120, 7200) | 1.00 / 0.97 / 0.28 / 0.08 / **0.01** | 12.9 | 0.60 → 0.98 |

`Q_total` conserved to ≤5% and `J_z` to ≤5% — the field is evolved correctly; the
charge physically leaves the throat.

1. **Higher spin does not help.** Half-life *falls* 15.8 → 12.9 as ω rises. The
   high-ω window hypothesis is falsified for this ansatz.
2. **Root cause:** the painter builds a *spherical* Q-ball and twists it into an
   `m=1` torus by `f·(sinθ)^m·e^{imφ}`. That torus is not a stationary solution of
   the rotating Einstein–Klein–Gordon system, so it relaxes and radiates.
3. **The geometry is rarefactive opening, not collapse** — min_chi → 1, max|K| →
   0, min_theta_plus stays +0.025, no horizon. The Ψ₄ "burst" at r=12/24 is the
   dispersing matter shell crossing the extraction spheres (r·|Ψ₄| *grows* with r,
   so it is not a clean 1/r wave-zone signal), not a boundary reflection.
4. **The sponge is OFF** for `RotatingWormholeCollapse` (only Sommerfeld + KO σ=2
   + z=0 reflection symmetry). No visible reflection by t=30 is a light-crossing
   effect, not evidence of a sponge.

**Verdict: the passive single-lump path is exhausted.** Dense φ_c → solver
diverges; matched φ_c → non-eigenstate torus disperses.

### 4.6 Active support — the pump is an igniter, not a prop

*Phase 3 — passive constellation.* A 2-lump orbital constellation (R0=6,
ω_orb=0.1, Ham 0.62% / Mom 0.89%) holds `Q_sphere` ~92% to t=12 and then suffers a
**violent NaN blowup at t≈13.5** — not the single torus's smooth dispersal. It
reproduces at ml=0 and ml=1, so it is physical, not an AMR artefact: passive
phantom lumps do not orbit stably.

*Phase 4 — k_p sweep.* Weak pumps (k_p ≤ 0.5) reproduce the passive blowup;
**k_p = 1.0 survives to t=30**. But the native constellation then collapses into a
spinning black hole at t≈8.8 (`min_theta_plus` crosses to −5.5). `pump_work` is
negligible (~1e-6) at every gain — the PD trap does almost no *net* work because
the field tracks the target; its value is the restoring force, not energy
injection. L2_Ham stays ≤ 0.028, so the blowups are the code failing to resolve
an unsupported collapse, not constraint runaway.

*Phase 4b — can more pump prevent collapse? No.*

| config | horizon at t |
| --- | --- |
| k_p=1.0, target_amp=0.1 | 8.8 |
| k_p=2.0 / 4.0, amp=0.1 | 8.57 / 8.51 |
| k_p=1.0, amp=0.15 / 0.2 | 7.61 / **6.94** |

Tighter tracking does not delay collapse (slightly *hastens* it), and more matter
collapses ~2 t **earlier** — the rotating cloud is net-attractive, so adding
"support" mass accelerates the black hole. **Collapse resistance is not a pump
knob.**

*Phase 4c — mass reduction is the lever.* Four hand-tuned IDs, all Ham/Mom < 1%,
each with k_p=1.0:

| ID | knob | outcome |
| --- | --- | --- |
| A: R0=6, ω_orb=0.13, κ=1.0 | more spin | horizon @ t=8.29 (**earlier** — orbital KE dominates) |
| C: R0=10, ω_orb=0.07, κ=1.0 | spread out | horizon @ t=7.29 (**starves the throat**) |
| **B: R0=6, ω_orb=0.1, κ=0.6** | less mass | **open throat, no horizon, min_chi plateau ≈0.86 t≈8→30** |
| D: R0=8, ω_orb=0.1, κ=0.7 | spread + less mass | no horizon but slow dispersal (min_chi 0.43→0.97) |

Spin and spread both make it worse; there is a Goldilocks band in (amplitude, R0)
with B inside it and D just above.

*Phase 6 — what the pump actually does.* Cutting the pump from an **established**
stable state (t ≳ 8–10) does essentially nothing; cutting it at t=4–6 gives
delayed collapse; never turning it on gives a horizon at t≈10. So the pump is a
transient **igniter** that shepherds a sub-critical constellation into the stable
open-throat basin over roughly the first t≈7–9, after which the wormhole is
self-supporting. That is a real result — an engineered rotating throat that
becomes autonomous — but it means "collapse on command by ramping the pump" only
works inside the ignition window.

*Phase 6 result — and the correction that killed config B.* Ramping
`wormhole_support_strength` (the quantity that actually gravitates) on config B at
L=128 to t=50, against a held-support control, bit-identical until the ramp:

| t | confined_frac (r<10) | matter rms radius | Q_sphere |
| --- | --- | --- | --- |
| 0 | 0.75 | 8.6 | −0.84 |
| 20 | 0.23 | 16.3 | ~0 |
| 50 | **0.004** | **35.7** | ~0 |

**No black hole in either arm**, and ~99.5% of the matter has left the throat by
t=50. Even the *control* opens to min_chi → 0.99 by t≈28. **The earlier "config B
is stable" claim was an artefact of stopping at t≈30 on the smaller L=64 box.**

Two things block collapse here: the support matter is not bound (a Q-ball twisted
onto an orbit is not a stationary eigenstate, so it spreads regardless of
support), and there is almost no positive gravitating mass — config B is light and
exotic-dominated, so removing the exotic support just lets the deformation heal to
flat. By contrast the static `SupportedWormholeCollapse` *did* collapse on an
`S_support` cut because it had a substantial **bare-mass throat**. That mass
balance is what the rotating case lacked.

### 4.7 The 2D Q-torus eigenstate — the fix that worked

Instead of twisting a 1D radial soliton by `(sinθ)^m`, solve the **genuine 2D
spinning Q-ball eigenstate** Φ = f(ρ,z) e^{i(mφ − ωt)} and paint `f(ρ,z)`
directly.

- **Solver** (`grteclyn_wrapper.grtresna.profiles.qball_torus`): the flat-space
  PDE `∂²_ρ f + (1/ρ)∂_ρ f + ∂²_z f − (m²/ρ² + κ²)f + λf³ − μ₆f⁵ = 0`
  (κ² = mass² − ω²) solved by a **bordered Newton** that pins the off-axis peak
  amplitude and lets ω float — so it cannot collapse to the f≡0 vacuum, which is
  the failure mode of fixed-ω Newton and Newton–Krylov — wrapped in amplitude
  continuation to hit the target ω. Residual ~1e-9; grid-convergent
  (f_max → 0.09173, Q → 3.098 at N=80/120/160); vanishes on axis.
- **GRTresna profile 4:** 2D table loader + bilinear interpolation;
  `lump_winding_modulus` returns `amp·f(ρ,z)/f_max` with **no** `(sinθ)^m` factor.
- **ID:** throat-free, centered, full-box, ω=0.25 (thick-wall; ω=0.05 is extreme
  thin-wall and does not fit the box — the solver detects box-escape and errors).
  Converged Ham 0.095% normal / 0.62% exotic, Mom 0.48%.

| t | **Q-torus** \|Q_sphere/Q0\| | twisted-sphere baseline |
| --- | --- | --- |
| 6 | 0.98 | 0.99 |
| 10 | 0.93 | 0.92 |
| 15 | **0.89** | 0.56 |
| 20 | **0.80** | 0.27 |
| 30 | **0.40** | 0.05 |

Charge half-life ≈ 27–28 vs 13–16 — **roughly doubled** — and the violent t≈13.5
blowup is **gone**. Honest caveat: the torus still slowly spreads
(confined_frac 0.81 → 0.43 by t=20), for two reasons — it is a *flat-space*
eigenstate, only approximately stationary once gravity is on, and it is
**phantom**, whose repulsive self-gravity actively unbinds it. A large
improvement, not a permanent soliton.

This eigenstate + profile-4 pipeline is what the headline run of §1 is built on.

---

## 5. Superseded claims — do not resurrect

| Claim once made here | Status |
| --- | --- |
| "Rotation is dynamically unstable" | **Wrong.** It was the O(ω) analytic-ID momentum defect (§4.1) |
| "The exotic Hamiltonian solve is stuck at 100%" | **Wrong.** Diagnostic denominator artefact (§4.2) |
| "Dispersal at t≈5 is purely numerical" | **Wrong.** Physical instability + massless spreading; only the *removal time* is boundary-set (§4.3) |
| "Low-res κ family shows a monotonic collapse trend" | **Superseded.** At dx=0.5/ml=3 no κ arm collapses; they all disperse κ-independently (§4.1) |
| "Prefer the self-gravitating boson-star profile first" | **Wrong for a phantom field** — its binding is gravitational, hence repulsive here (§4.4) |
| "Higher ω opens a usable Q-ball window" | **Falsified** — half-life falls with ω (§4.5) |
| "Config B is a stable actively-supported throat" | **Artefact of stopping at t=30 on L=64.** At L=128, t=50 it disperses with or without support (§4.6) |
| "The pump injects the energy that holds the throat" | **Wrong.** ∫pump_work ≈ 0; it is a shaping force and a transient igniter (§4.6) |
| "The burst radiates at 169 Hz / 5 Hz" | **Wrong normalisation** — assumed code mass 1; M_ADM ≈ 0.209 (§6, A4) |
| "`rho_sum` measures confinement" | **Wrong** — see L7 |
| MAP-Elites stability campaign is on the critical path | **No.** Phase 4c found a working config by hand; the campaign is optional paper enrichment (§9) |

---

## 6. Article-hardening runbook (2026-07-15 → 16)

Headline ID for all arms unless noted:
`runs/rotating_torus_id/torus_m1_om0p250_kappa1p00_dx0p5_L64_lam170_mu614450_exotic_throat1/initial_data.gridinit`.
Launch always via `wormhole_case.py` with `--no-frames` and the delete sidecar.

### Tier 1

**A1 causality controls — DONE (both alternatives NaN).**

| Arm | Ramp | Outcome |
| --- | --- | --- |
| `noramp_ctrl` | none | NaN in `K` @ **t≈18.82**; min_lapse never < 0.15; max_ah → 15.6 |
| `ramp_t16` | [16,18]→0 | NaN in `h11` @ **t≈18.85**; same shallow-lapse runaway |
| headline | [8,10]→0 | clean to t=40, min_lapse → 9.8e−4 |

Bit-identical to the headline until the early ramp would have acted. **Early
support cut selects the resolvable deep-collapse branch**; no-ramp and late-ramp
do not hold a quiet throat, they abort without deep lapse.

**A2 the t≈2.3 θ₊ crossing — DONE.** Identical in noramp and headline at t=2.26,
while still inside the gauge transient ⇒ it is the throat's minimal-surface proxy,
not collapse. Robust collapse markers only after the support cut (t ≳ 12).

**A3 modes + non-rotating control — PARTIAL. This is the open blocker.**

Why it matters: reviewers will want a non-spinning baseline with the same trigger,
box and extraction. The goal is not a twin deep collapse — it is to show the
**morphology differs without angular momentum**. Without it, "rotation matters" is
circumstantial, resting today on m=0 power dominance (burst power ≳ 99.999% in
m=0; directional beam ratio ~1e−5).

Non-rotating ID exists and needs no re-solve
(`torus_m0_om0p000_kappa1p00_..._exotic_throat1`, Ham ~0.51%, J_ADM = 0,
M_ADM ≈ −0.24). Three attempts:

| # | Setup | Outcome |
| --- | --- | --- |
| 1 | L=64, ml=3, thr=0.01, dt=0.02, σ=2, 1 GPU | **Arena OOM** @ t≈9.6 |
| 2 | same + MPI×2 | **Killed ~t=13.5** as pathological — see below |
| 3 | ml=2 (cap depth), same proven thr/dt/σ, `--full-box` | **NaN in `h11` @ t=12.34** |

Attempt 2 vs the spinning twin at similar t: min_lapse ~0.81 (no deep puncture)
against ~10⁻³; AH proxy **17.9 and still growing** (already > 1 at t≈5.6, *before*
the ramp ends) against ~9-then-shrinking; θ₊ ~−16 (runaway) against ~−0.5;
`Q_sphere` −3.24 → **+0.81** (not retained); Ham **4.2e−2 climbing** (~12× t0) and
Mom ~2000× t0; level-3 cells ~37M against ~12.6M; ~77 GB FAB/rank.

Attempt 3 memory at t≈9.5: headline ml=3 ~15 GB (L1 ~0.59M cells); norot ml=2
~33.5 GB (L1 already the full 2.1M box, L2 ~7.9M). Same tagger, larger tagged
*volume* — `ChiTagger` uses second derivatives of χ with **no radial cutoff**, and
the non-rotating χ / AH-proxy feature spreads. Diagnostics were healthy until
t≈12.32 (lapse ≈ 0.992), then |K| → 10⁵⁹ in one step.

**Verdict:** this m=0/ω=0 ID with a support ramp does not reproduce the headline
morphology and has not yielded a clean control. The next retry needs a *different*
strategy — tighter `regrid_threshold`, a radial tag cutoff, or a better-matched ID
— **not** more GPUs and not more KO dissipation on the same trajectory.

**A4 ADM — DONE.** On the exotic_throat1 gridinit, R ∈ {16,20,24,28}:
**M_ADM = 0.209 ± 0.001**, **J_ADM_z ≈ −1.93** (volume J_z(t=0) ≈ −1.47, same
sign). Physical frequency scales with M_ADM (≈ ×0.21): ~35 Hz at 30 M☉, ~1 Hz at
10³ M☉ if M_ADM is identified with the astrophysical mass.

**A5/A6 budget — DONE.** ∫pump_work dt = **0** (the PD pump is off in the
headline; only the support ramp acts). Q_sphere retained (~5% drift); Q_total
+116%, J_z +141% with a sign change — **do not claim conservation**, and the drift
is not pump injection. E_GW (ℓ=2,m=0 NP proxy) ≈ 0.025 ≈ 0.12 M_ADM
(order-of-magnitude, near-zone). Propagation v = 1.00 ± 0.08 c
(sampling-limited) — not "exactly 1.00".

### Tier 2

**B1 three-resolution ladder — DONE.** Matched-ID runs at dx ≈ 0.667/0.5/0.4,
ml=3, L=64, all clean to t=40. Collapse, AH-proxy growth and shrinkage, lapse
recovery and the m=0 burst reproduce on all three. Richardson for unequal ratios
(`h_c/h_m = 4/3`, `h_m/h_f = 5/4`), `Q(h) = Q0 + C h^p` with p solved numerically:

| Quantity | coarse / medium / fine | p | continuum / fine GCI |
| --- | --- | --- | --- |
| max\|K\| | 0.545 / 0.623 / 0.646 | 3.78 | 0.663 / 3.31% |
| max AH proxy | 9.110 / 9.175 / 9.215 | 0.91 | 9.391 / 2.39% |
| t(max AH) | 15.520 / 15.140 / 14.968 | 2.09 | 14.678 / 2.42% |
| max Mom L2 | 9.83e−3 / 9.67e−3 / 9.60e−3 | 1.82 | 9.45e−3 / 1.95% |
| max Ham L2 | 3.10e−2 / 3.25e−2 / 3.40e−2 | — | **no positive p** |
| min lapse / chi | deepen with h | — | extrapolation negative (non-asymptotic) |

**Convergence is quantity-dependent, not a single order.** The coarse Ψ₄ record
has no samples over part of the principal burst, so there is **no defensible
three-point burst-waveform order**.

**B2 large-box extraction — DONE, intermediate-zone only.** `bigbox_L128_ml2` ran
clean to t=80 (L=128, dx=0.5, ml=2, R_ext = {36,48}, sponge 52–62). Retarded
waveforms overlap **0.993** after a residual 0.35 time shift, with **12.3%**
relative L2 residual — supports approximate 1/r scaling. **Not** a wave-zone proof
and not a fourth resolution rung. Constraints are acceptable through t=40 but
later peak at Ham 0.155 / Mom 0.0417, so the late R=36 rise is not treated as
clean radiation. The collapse proxy peaks at 8.79 and disappears by t≈78.4,
extending the collapse–rebound morphology past the headline stop time.

**B3 relative constraints — DONE enough.** Ham L2 max ≈ 10× the t=0 residual; Mom
similarly elevated. No Θ/Z_i or L∞ columns in `constraint_norms.dat`.

**B4 apparent-horizon finder — GAP.** None in GRTeclyn; the coordinate θ₊ proxy
stands, documented as a proxy.

**B5 energy budget — DONE** at proxy level (A6).

### Campaign disposition

Finished: `torus_wh_collapse_ml3_gw`, `rerun_allm`, `conv_dx067`, `conv_dx040`,
`bigbox_L128_ml2`. Killed or pruned: `noramp_ctrl`, `ramp_t16`,
`torus_wh_control_ml3` (NaN arms); `conv_dx033` (bonus rung, paused);
`norot_m0_ramp` (pathological); `norot_m0_ramp_ml2_thr01_proven` (NaN @ 12.34).
`ml=3` with MPI at L=128 deadlocks at init. **No simulations remain running.**

---

## 7. Known defects and gaps

### The in-code C++ Weyl4 extraction is broken — DEFERRED, not fixed

`data/Weyl4_mode_2{0,1,2}.dat` disagrees with the validated Python post-hoc
extraction: ~8× larger RMS at r=12 and **uncorrelated** with it (corr ≈ 0.07); an
O(0.6) value at t≈0 where near-stationary ID should radiate ≈0; an O(1) m=0
imaginary part (Python: ~1e-5); and ~80 per-shell `1e51`-scale blowups at r=18/24
clustered at violent/regridding phases.

Verified **not** the cause: extraction centre, mode list, component map, and the
projection math are all identical to the working BinaryBH example. AMReX `derive`
is not under-filling ghosts (`ngrow_src = ngrow + 2` gives the 4 ghosts the
4th-order stencil needs).

Root cause, from comparison with GRChombo: `BinaryBHLevel::specificPostTimeStep`
does `fillAllGhosts()` → compute Weyl4 into a **stored diagnostic** on valid cells
→ `fill_multilevel_ghosts(diagnostic)` → extract. GRTeclyn instead computes Weyl4
**on the fly** inside the interpolator via `derive("Weyl4", ...)`, with no stored
diagnostic and no multilevel diagnostic-ghost fill. The `1e51` spikes are most
likely quartic particle interpolation near freshly-created coarse–fine boundaries
and/or time interpolation against a just-regridded level.

**Why it is deferred, not fixed:** the GRTL collaboration lists "Weyl scalar / CCE
extraction" as *in progress* in GRTeclyn's development status. This is a partial
upstream port, not a bug in our wiring. Fixing it properly means adding a
diagnostic state and `fill_multilevel_ghosts` (neither exists in
`Source/GRTeclynCore`) — a real port. Revisit when upstream marks it done.

**Interim policy, in force:** all physics uses
`small_data/psi4_mode_l2m0.dat` (Python). The dense C++ files are debugging-only.
Cheap pre-step if the port is attempted: a t≈2 run with `write_extraction = 1` to
localise *where* on the sphere the `1e51` originates.

### Other gaps

- **No apparent-horizon finder.** Everything horizon-flavoured is a coordinate θ₊
  proxy. Needed before quoting horizon mass or spin. BHaHAHA is open-source and
  code-agnostic — integrating it would also close the angular-momentum budget
  `J_ADM = J_horizon + J_matter,ejected + J_GW(≈0)`.
- **Extraction is near/intermediate-zone.** R_ext = 12–24 inside a sponge at
  28–30 in the headline; B2 reaches 36/48. No wave-zone proof, no CCE.
- **`‖H‖₂ = 3.25e−2` is the level-0, unmasked, domain-diluted norm** — not
  quotable as an accuracy figure. Use the composite AMR columns, or restrict to
  within-protocol comparisons and say so. The non-converging Hamiltonian maximum
  may partly *be* the unmasked refinement-boundary contribution.

---

## 8. Why the GW signal is matter-driven, not rotation-driven

This is close to a theorem for this configuration, not a patchable bug — worth
stating carefully because it reshapes what the paper can claim.

The initial data has |Φ|² **exactly axisymmetric by construction**; all the angular
momentum lives in the phase winding, not in any moving density feature. GWs couple
to time-varying mass and current multipoles, and for an axisymmetric,
equatorially-symmetric configuration the non-vanishing moments are the even mass
multipoles (M₀, M₂, M₄…) and the odd current multipoles (S₁, S₃…). So when the
torus collapses axisymmetrically:

- the changing **mass quadrupole M₂** radiates ℓ=2, m=0, even parity — exactly the
  burst that is observed;
- the **current dipole S₁ = J_z** is conserved and never radiates;
- the **current quadrupole S₂ vanishes** by equatorial symmetry. This matters for
  how the null test is described: the measured `Im Ψ₄^{2,0}/Re Ψ₄^{2,0} ≲ 1.2e−3`
  is **not** evidence that rotation is weak, it is enforced by symmetry. That test
  confirms equatorial symmetry, not rotational radiation.
- the first channel where axisymmetric rotation is *allowed* to radiate is the
  **current octupole S₃ → ℓ=3, m=0, odd parity**, sourced by radial redistribution
  of angular momentum during collapse.

To make rotation radiate you must either look where it is permitted (ℓ=3, m=0) or
break axisymmetry in the *density*.

**A related trap.** The non-rotating control (§6, A3) was pathological for a
physical reason worth stating rather than hiding: a toroidal scalar density
*without* winding is not close to any equilibrium — the `m²/ρ²` term in the field
equation is what supports an off-axis amplitude peak, so removing the winding while
keeping the torus shape hands the evolution a violently out-of-equilibrium state.
A same-shape zero-spin control is **ill-posed in this matter model**; rotation and
toroidal geometry are inseparable here. The honest replacements are *differential*
controls (§9, tier 2).

**On terminology.** The `m=1` in the ID is the scalar **phase winding** in
Φ = f(ρ,z)e^{i(mφ−ωt)}. Because |Φ|² = f² is axisymmetric, it does **not** imply
GW m=1 or m=2. Name them apart in outputs and prose: `m_az` for the scalar winding,
`m_GW` / `m_density` for extracted modes. And do not read a scalar `m_az=2`
eigenstate or a quadrupolar kick as a bar mode — either can stay axisymmetric in
density, or simply impose the desired answer.

---

## 9. Open work, ranked

### Tier 1 — mine the existing runs (no new GPU time)

1. **Extract Ψ₄^{3,0} and its parity content** from the stored plotfiles. A
   coherent odd-parity ℓ=3, m=0 burst tracking the collapse *is* the rotational
   radiation of this spacetime, and its energy can be quoted relative to the m=0
   quadrupole. This turns "rotation doesn't radiate" from a limitation into a
   measured result.
2. **Angular-momentum flux.** dJ_z/dt in GWs is proportional to m mode by mode, so
   m=0 radiation carries exactly **zero** J_z. That licenses a sharp statement the
   paper currently only gestures at: the burst radiates energy but essentially no
   angular momentum, and the remnant retains ≈100% of J_ADM. It also connects to
   the rebound — if the collapse cannot shed J, the phantom bounce may be partly
   centrifugal, which is testable in tier 2.
3. **Flat-space quadrupole-formula estimate** from the matter density history,
   compared with the extracted burst morphology — proves the matter-quadrupole
   attribution *positively* instead of by elimination.
4. **Matter-side mode decomposition** `C_m(t)` of |Φ|² on a few rings. Showing the
   density stays axisymmetric to < 10⁻³ through the burst both explains m=0
   dominance quantitatively and connects to the instability literature (the run is
   far too short and too interrupted for bar-mode growth).
5. **Replace the θ₊ proxy in the analysis** (highest-leverage manuscript fix): the
   pointwise minimum is structurally unfit — pinned at the reduction-footprint
   edge, tracking global max|K|. A shell-averaged replacement exists but is **not
   field-validated**; run the A/B before any proxy number from a new binary enters
   the paper.

### Tier 2 — a spin ladder, replacing the broken non-rotating control

Since a same-shape zero-spin control is ill-posed (§8), use **differential**
controls instead:

- an `m_az=2` winding torus at matched M_ADM (same topology, ~2× J);
- an ω ladder within `m_az=1` (the κ-family driver already does amplitude
  families; a small ω family is the same machinery);
- optionally a matched-mass spherical `m_az=0` Q-ball under the same support-cut
  protocol, as the "no rotation, no torus" baseline.

If waveform, collapse depth and rebound radius shift systematically with J across
the ladder, rotation's dynamical role is isolated even though it does not dominate
the radiation. If they don't shift, that is a **clean negative worth publishing as
such**.

### Tier 3 — a genuinely non-axisymmetric campaign (a separate paper)

To get radiation *caused by* rotation you need a rotating m≠0 **density** pattern:
seed an m=2 perturbation on the torus, or use two orbiting compact tori. The
literature supplies the mechanism — spinning scalar stars are generically unstable
to non-axisymmetric modes (Sanchis-Gual / Di Giovanni 2020), with m=1 quenchable by
repulsive self-interaction in some windows (Siemonsen & East 2021) — but growth
timescales are hundreds to thousands of M. Our run is 40 time units with the
support cut at t=8–10, so **spontaneous bar-mode growth can never appear on this
window; it must be seeded at finite amplitude.**

A bar mode cannot be *forced*. The evidence bar for calling one natural:

- fitted growth rate γ agrees **across seed amplitudes** (roundoff, 1e−6, 1e−5)
  and at three resolutions, within uncertainty;
- onset times shift as ≈ −ln(ε)/γ while saturation amplitude and pattern speed
  agree;
- `C_2` grows in the **matter** before Ψ₄^{2,2} reaches the detector;
- the m=2 amplitude does not converge to zero, and m=1,3,4 are reported to exclude
  a different dominant instability;
- the GW satisfies expected +m/−m relations across extraction radii.

Search strategy: build constraint-solved ID families scanning **measured**
quantities (M_ADM, J_ADM, Q, torus radius/thickness, peak |Φ|, residuals), not
assumed ones — for Q-balls J = m_az·Q, and ω also changes charge, radius, thickness
and compactness. Stage as `m_az=1` at low/mid/high compactness, then `m_az=2` over
the same *measured* compactness range, then a narrow throat-mass bracket if needed.
Do **not** use the fluid threshold `T/|W| = 0.27` as universal for a phantom
scalar — context only. Pilot cheaply with constant support; promote only candidates
with ≥ 3 clean e-foldings of matter m=2, bounded constraints, and no simultaneous
numerical pathology. Reject anything whose apparent m=2 tracks constraint growth,
regridding, boundaries, or seed amplitude linearly.

Prerequisites before spending GPU time on that search: matter multipoles
`C_m(t) = ∫w e^{imφ}dV / ∫w dV` for m=1..4 with a non-cancelling weight
(|Φ|² or |ρ|); equatorial quadrupole, bar amplitude, phase and pattern speed;
radial profiles of charge and angular momentum; a `bar_mode_analysis.py` that
fits |C₂| = A e^{γt} only over an objectively selected linear-growth interval;
matter-aware refinement (verified not to change the axisymmetric headline
diagnostics); and dense in-situ all-m extraction validated against the Python path
(plotfile cadence is too sparse for growth rates and spectra).

Wave-zone requirements for such a campaign: a dense finite-radius bridge on the
proven L=128 / ml=2 / MPI×2 setup with R_ext = {24,36,48}, sponge 52–62, Δt ≤ 0.25,
stop ≥ 80, requiring outer-radius overlap ≥ 0.98 and stable three-radius 1/r
extrapolation; then L=256, R ≈ {60,80,100}, sponge outside 104, t ≈ 150, accepting
only if |rΨ₄^{2,2}| varies ≤ 5% across outer radii after retarded-time alignment.
Add CCE if available; otherwise keep the claim explicitly finite-radius with error
bars — especially for m=0, which is unusually gauge-sensitive.

### Also open

- **Stationary rotating solve (the principled passive fix).** Solve the coupled
  *stationary axisymmetric* system for F(ρ,z) **together with** χ, lapse, shift and
  ω — not just the gravitational constraints around a fixed profile. Numerical
  continuation from the exact ω=0 Ellis–Bronnikov equilibrium, marching ω up the
  branch (rotating Ellis / Kleihaus–Kunz class). Acceptance: low scalar-EOM
  residual at t=0 **and** `Q_sphere` high and flat to t=30, not merely a slow leak.
  The §4.7 torus is the flat-space version of this; the self-gravitating version is
  the remaining step.
- **Document the support-coupling model honestly.** `support_strength` multiplies
  the phantom stress tensor while the Klein–Gordon RHS is unchanged — state the
  resulting Bianchi/conservation violation explicitly in the manuscript. Also
  resolve a code/manuscript mismatch: the implementation uses a **linear** ramp
  while the article gives a **cosine** ramp. Prefer implementing the cosine ramp
  and recording it in `params.txt`.
- **Audit AMR initialisation for the search runs.** Base-grid ID spacing is 0.5
  while AMR evolves finer levels; for subtle non-axisymmetric growth, generate ID
  at adequate source-region resolution and measure level-by-level residuals after
  initialisation.
- **MAP-Elites stability campaign — OPTIONAL, paper enrichment only.** It would map
  the boundary surface in (per-lump amplitude, R0, ω_orb, k_p) between the three
  fates already seen by hand: collapse-to-BH, open throat, dispersal-to-flat. Spec
  if ever wanted: QD pipeline, genome ~4 + 7·N_lumps dims, fitness
  `w1·Q_retention + w2·throat_persistence − w3·constraint_growth − w4·pump_energy −
  w5·horizon_flag` starting at (1.0, 0.5, 0.3, 0.3, 1.0), 8×8 archive over
  (orbital-AM proxy, log pump_energy), 200 evals on 8 GPUs, acceptance coverage
  > 10% with ≥ 1 elite at Q_retention ≥ 0.7.
- **Reproducibility deposit.** Archive promoted and control runs, exact ID files,
  dense mode data, parameter manifests, analysis scripts, code commit/tag and
  figure-generation commands in a DOI-backed deposit.

### Manuscript decision gate

If natural, convergent matter m=2 growth is ever found, pivot to a
non-axisymmetric-instability result and use the present m_GW=0 run as the
low-spin/control case. If no candidate passes the growth tests, **do not
manufacture an m=2 headline** — submit the narrower engineered support-removal
paper after correcting the ramp equation, documenting controls, adding wave-zone
evidence, and removing any implication that rotation sources the observed
quadrupole. Either outcome is publishable: a detected bar instability with a
measured threshold, or a constrained null result over a documented
rotating-Q-torus family.

---

## 10. Design notes kept for reference

**Scale matching (the Phase-7 design that was never built).** Config B is
geometrically a *tiny neck buried inside two huge clouds*: throat areal radius
b0 = 0.5 while each Q-ball lump has half-max radius ≈ 5.7 centred at R0 = 6. So the
lumps do not really orbit anything, and the object is better described as one
exotic blob with a coordinate pinch. The intended fix was a **hugging ring**:
b0 ≈ 2–3 comparable to lump size, N = 6–12 compact Q-balls at R0 ≈ b0 + r_lump so
neighbours nearly touch, optionally with a central exotic core for the flaring-out
support and the ring purely for spin.

**A hard constraint not to design around:** a traversable throat stays open only if
NEC-violating stress exists **at the throat itself** (Morris–Thorne flaring-out).
That is a theorem, and our own data confirms it — Phase 4c config C, with lumps
spread to R0 = 10, starved the throat and collapsed at t ≈ 7.3. Support fields must
blanket the neck. Relatedly, a wormhole has no horizon, so matter is not captured —
matter not in a bound orbit **plunges through the throat to the other universe**.

**AMR for any collapse arm.** At `max_level = 0` the forming puncture is unresolved
and NaNs. The static `SupportedWormholeCollapse` that did extract GW through
collapse used `max_level = 5` with ChiTagger and no puncture tracker. The rotating
case has **no x/y/z symmetry** (the static octant run computed 1/8 the box), so the
full-domain base grid plus refined patches is memory-heavy — use the fewest levels
that resolve the puncture and tag tightly on the centre.

**Science targets this line of work was set up to answer**, restated for whoever
picks it up: does angular momentum delay or prevent throat collapse, and is there a
critical ω separating collapse from a spinning remnant? Is there a natural ℓ=2 GW
family versus (ω, m, κ)? What is the remnant spin from a Kerr QNM fit, cross-checked
against swallowed J_z? Does the phantom bounce go non-axisymmetric? Of these, only
the collapse/burst morphology has been measured; the rest are open and most are
gated on §9's tier 2–3.

**Binary wormhole merger** is a separate line, now in
[`../merger/Plan.md`](../merger/Plan.md) — and currently blocked on throat
resolution, see [`../merger/MatterDebug.md`](../merger/MatterDebug.md).
