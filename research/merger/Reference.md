# BinaryWormholeMerger — reference: prior art, validated initial data, code design

**This is not a plan.** The plan is [Plan.md](Plan.md), Stages 0–4. This file holds what
stays true whichever stage is running: the novelty scan, the initial-data gates and what
they measured, the standing physics decisions, and the file-by-file design of the example.
Kept under `research/merger/` for the same reason as the rest — out of the public tree.

Superseded and removed 2026-08-31: the Phase 3–8 execution checklists (now Plan.md Stages
2–4) and the 2026-08-28 blocker banners, which described a puncture throat that no longer
exists. Code comments citing phase numbers resolve through the map below.

| old phase | where it lives now |
| --- | --- |
| 0 — build and smoke test | done 2026-08-27; the launcher contract is below |
| 1 — initial-data gates | **kept below**, passed 2026-08-28; its `d/b ≥ 8` constraint still binds |
| 2 — single-throat regression | **kept below**; superseded as a goal by Plan.md Stage 1, which met its exit condition on the drainhole |
| 3 — head-on merger | Plan.md Stage 3.1 |
| 4 — spiralling merger | Plan.md Stage 3, after the head-on |
| 5 — waveforms and energetics | Plan.md Stage 3.2 |
| 6 — convergence and error budget | Plan.md Stage 3.3 |
| 7 — constraint-solved data | Plan.md Stage 2.2 (GRTresna/CTTK) |
| 8 — paper | Plan.md Stage 4 |

---

## Part 1 — Prior art: has anyone simulated a wormhole–wormhole merger?

**No.** No full nonlinear (3+1 NR) simulation of two traversable, exotic-matter-supported
wormholes colliding or merging exists — nor any axisymmetric/2D, double-null, or
lower-dimensional dynamical two-throat evolution. The novelty claim holds across every
category checked, scoped to traversable NEC-violating matter-supported throats and
explicitly excluding vacuum-puncture Einstein–Rosen topology.

| category | state of the art |
| --- | --- |
| full 3+1 NR of two wormholes | **none** — genuinely first-of-kind |
| axisymmetric / 2D NR of two throats | none found |
| double-null / characteristic, two throats | none; Xu–Chew–Yeom (2503.07610) collide two *pulses* at a *single* throat |
| lower-dimensional two-wormhole dynamics | none; closest is a ghost-field collision *forming* one wormhole in 2D dilaton gravity (2205.15748) |
| analytic multi-wormhole solutions | several, all **static** (1603.09552, 2505.16361, 2412.05236, 1512.08029) |
| wormhole–black hole collisions | semi-analytic/perturbative only (2007.09135, 2605.01216, 2304.06098) |
| wormhole binary, any level | Newtonian and analytic only (2311.00348) |

**The frontier is uniformly single-throat.** Shinkai–Hayward (gr-qc/0205041) first
established the sign-dependent bifurcation — positive-energy input collapses the throat,
negative-energy input inflates it. González–Guzmán–Sarbach (0806.0608 linear, 0806.1370
nonlinear) proved exactly one unstable exponential mode with timescale ~ throat/c. Xu–Chew–
Yeom (2503.07610) and Kain (2210.04905, 2602.18231) are double-null single throat. Our own
3D single-throat run is arXiv:2604.00071.

**The methodological template is exotic compact object binaries**, which are mature in 3D:
boson-star binaries (Palenzuela et al.; Bezares–Palenzuela; Helfer et al. CQG 39 074001;
Ge et al. 2410.23839; review 2406.04901), boson-star–black hole binaries with the
**one-body conformal-factor correction** (Ning et al. 2604.15240 — plain superposition
"can strongly perturb the BS core, leading to large constraint violations and unphysical
radial oscillations"), and Proca-star mergers including the GW190521 interpretation
(2009.05376, PRL 126 081101) — the key precedent for exotic-collision-versus-real-data.

**The two initial-data precedents a referee will raise.** Brill–Lindquist/Misner data is
standard multi-throat *vacuum* data and already has Einstein–Rosen topology — it must be
explicitly excluded from the claim. Smirnov (2312.09622) gives a time-symmetric initial
data problem for GR + phantom scalar using a complexified Misner potential, but it is two
mouths of **one** wormhole, intra-universe, and initial data only with no evolution. Both
distinctions belong in the introduction.

**Benchmarks for the head-on.** Radiated energy from rest in 4D vacuum BBH is 0.055 % of
total mass-energy (Witek et al. 1006.3081), rising to (14±3) % ultrarelativistically
(Sperhake et al. 0806.1738); post-merger ringdown is ℓ = 2, m = 0 dominated with a small
ℓ = 4, m = 0 contribution (gr-qc/0503071). Boson-star head-ons can radiate *more* than the
equivalent BBH (2607.09494), so treat 0.055 % as a reference point, never an expected value.

**Scoop risk is low but real** over 6–12 months: GRChombo/GRTL, Chew–Yeom and the Lanzhou
group are all active in adjacent single-throat work, and none has announced two throats.

**Caveats on the scan.** arXiv:2604.00071 and 2602.18231 are single-author and possibly
unrefereed — treat quantitative claims accordingly. The GW190521 wormhole-echo reading
(2509.07831) is disfavoured by its own Bayesian analysis (ln ℬ ≈ −2.9); cite as motivation
only. 100 % coverage of Russian- and Chinese-language venues cannot be guaranteed. Static
multi-throat solutions are plentiful and a referee may point at them — the distinction
between a static exact solution and a dynamical merger of two distinct throats has to be
made explicitly and repeatedly.

---

## Part 2 — Standing decisions

**Static throats only** (2026-08-27). Each throat is non-spinning, supported by a phantom
scalar; orbital angular momentum comes from transverse Bowen–York momenta, not from spin.
A rotating-throat generalisation is out of scope for this paper.

**The merger is gravity-driven** (2026-08-27). A *massless* Ellis–Bronnikov throat is
ultrastatic — lapse exactly 1, all curvature in the spatial metric. It bends light, but a
mass at rest feels no pull at any distance: the phantom scalar's negative energy exactly
cancels the positive field energy, the 1/r piece of the metric is absent, M_ADM = 0.
Curved does not mean attracting; two massless throats released from rest just sit there.
The fix is the other branch of the same family — drainholes with genuine positive ADM mass.

> **Corrected 2026-08-28.** The original mechanism was `wormhole_bare_mass_A/B`, a
> Brill–Lindquist m/(2r) term added to ψ. The decision stands; the mechanism was wrong. A
> puncture buys ADM mass at the price of χ → 0 **at the minimal surface**, which is what
> made the throat unresolvable. The drainhole buys the same mass from the **lapse** and
> costs nothing in resolution — χ_throat falls only 0.25 → 0.15 as m/a goes 0 → 1.
> `wormhole_bare_mass_A/B` is **rejected outright** under `wormhole_id_type = 1`.

**Every run goes through the campaign launcher**
([wormhole_merger/](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/)), never a
bare `./main3d….ex params.txt`. The launcher registers `launcher.pid` so
`stop_campaign.sh` works, keeps `.dat` streams on the runs dir, and sends plotfiles to
node-local `/tmp` scratch, per the
[campaign contract](../../grteclyn-wrapper/scripts/campaigns/README.md). What
[run_single.sh](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh)
does:

- registers the launcher pid → stoppable with `stop_campaign.sh [--dry-run] <runs_dir>`;
- clones the params template into the run dir and re-emits `output_path` (NFS run dir) and
  `amr.plot_file` / `amr.check_file` (node-local scratch), each asserted to occur exactly
  once — plotfiles never touch NFS;
- runs attached in the foreground; detached launches need explicit permission;
- knobs: `WHM_PARAMS`, `WHM_GPU`, `WHM_RUNS_DIR`, `WHM_NAME`, `WHM_EXE`, `WHM_DRYRUN=1`.

**No seeded scalar perturbation.** The single-throat example carries a Gaussian
`φ → φ + (A₀ + A_φ Y₂₀)exp(−r²/w²)` because picking the compressive or rarefactive branch
by hand *is* that experiment. A merger must not: the other throat is the perturbation, and
pre-destabilising the throats contaminates the very thing the run measures. The three keys
were **removed** rather than defaulted to zero, and a params file that still sets one is
rejected, so a stale file cannot silently mean something else.

---

## Part 3 — Initial-data gates (Phase 1) — **passed 2026-08-28**

The single most likely failure mode is bad initial data, not a bad evolution. All checks
are run by
[phase1_initial_data.sh](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/phase1_initial_data.sh)
with `max_steps = 0`; the measurement is the t = 0 row `specific_post_init` writes.

**One operating constraint came out of it, and it still binds: run at `d/b ≥ 8`.**

### Single-throat limit is exact (check A)

With `wormhole_throat_radius_B = 0` and no bare mass, `fcompare` against
`Examples/SupportedWormholeCollapse` on an identical grid gives a maximum absolute
difference in χ of **8.88e-16** — one unit in the last place of a number of order 1. `K`,
`lapse`, `phi` and `Pi` agree **exactly**, so the subtracted asymptotic constant is handled
identically on both sides too.

### Momentum constraint is zero at t = 0 (checks B, D)

With momenta off, `L2_Mom = 0.0` **exactly, to the last bit**: A_ij is identically zero, so
every derivative of it is too. With Bowen–York momenta on, the constraint is analytically
zero but its *discrete* divergence carries the stencil's truncation error, so the gate is
convergence, not a bit-level zero. Over N = 192 → 288 → 384 at L = 32, b = 1:

| N | L2_Mom |
| --- | --- |
| 192 | 9.87e-5 |
| 288 | 2.61e-5 |
| 384 | 9.65e-6 |

**Order 3.3 → 3.5**, monotone, heading to zero. (A first pass reported a non-monotonic
mess. That run carried a bare mass — a puncture, where χ → 0 and the constraint is formally
singular, so a whole-domain L2 of it has no continuum limit — on a throat 1–2 cells across.
It was measuring the puncture and the under-resolution, not the stencil.)

### Hamiltonian defect scales as expected (check E)

The naive form of this test compares `L2_Ham` at different `d` on one grid, and it
flattens: at any affordable resolution most of that number is truncation error, and
subtracting "the floor" subtracts two numbers of the same size. So the defect is extracted
as the part refinement cannot remove — fit `L2_Ham(N) = A + B·N⁻ᵖ` to a three-point ladder
at each separation and read off `A`.

| ladder | A |
| --- | --- |
| single throat (exact solution — the zero control) | **−1.6e-4**, i.e. the error bar on every other row |
| d = 4 | 2.27e-3 |
| d = 8 | 2.9e-4 |
| d = 16 | 3.7e-4 |

Over the one doubling above the noise, **d = 4 → 8, the defect falls by a factor 8** — at
least as fast as the required 4. Beyond that it cannot be tracked: at `d ≥ 8` the
superposition defect is already **below the code's own discretisation floor**, which is why
d = 8 and d = 16 are indistinguishable. That is the substance of the gate — the analytic
superposition is a controlled approximation whose error, at `d/b ≥ 8`, is smaller than the
numerical error of the evolution it feeds. At `d/b = 4` it is an order of magnitude larger
and no longer negligible.

> **A retired box.** "`L2_Ham(t=0)` falls at 4th order under refinement at fixed d" was
> mis-stated. A genuine superposition defect is a property of the *continuum* data, so it
> does not fall under refinement — it plateaus. Demanding it vanish would be demanding the
> superposition be exact. What converges at 4th order is the *discretisation* error, and it
> does (order 3.3 → 3.5, check D above). The plateau is the physics, the decay is the
> numerics, and the fit separates them.

### φ tends to 0 at the outer boundary (check F)

Measured by differencing two runs identical but for
`wormhole_subtract_phi_asymptote`, rather than by fitting. They differ by **0.443113 at
every radius, with a spread of 1.1e-16** — machine epsilon, so what the flag removes is a
pure constant and nothing else. (0.443113 is half the ≈ 0.886 originally quoted: 0.886 is
the *total* change across the wormhole, −0.443 to +0.443.) At the outermost shell,
subtraction off leaves φ = +0.424 — what Sommerfeld would otherwise be applied to — against
φ = −0.019 with it on. The residual is the physical tail and it is clean: `φ·r` is constant
to 0.3 % over r = 6…15.

> **The original "≲ 1e-3" bound is not achievable and was the wrong test.** Once the
> constant is gone, what remains falls like 1/r, so 1e-3 needs a domain hundreds of throat
> radii across. Fitting the constant out of a *single* run does not work either — over the
> radii a finite box offers, a constant, a 1/r and a 1/r² term are not separable, and the
> fitted constant moves with the radius range and even changes sign. Differencing two runs
> has none of that freedom.

### No trapped surface at t = 0 (θ₊ scan)

Verified 2026-08-27 on the Phase 0 smoke: θ₊ ≈ **+0.150** about A, about B and about the
midpoint at every step, `ah_r_* = 0` throughout, A and B agreeing to the last digit as the
symmetry demands.

**This gate initially failed, and the cause was the diagnostic, not the data** (θ₊ = −1.26
at r = 5.02). It reduced a **global minimum** of θ₊ over all points, so one point of a large
sphere about A grazing throat B — where B's steep χ gradient beats the 2√χ/r term of the
distant centre A — condemned the whole sphere. A surface is trapped only when θ₊ ≤ 0
*everywhere* on it, so the reduction is now a **maximum per radial shell**, and the phantom
surface vanishes exactly. No exclusion radius could have fixed it: the grazing region sits
at a radius set by the *separation*, not by the throat radius.

### Bare-mass tail is right (check G)

Throats at z = ±4, b = 1, m = 0.25 each, so M should be 0.5. Fitting
ψ − 1 = a₁/r + a₂/r² + a₃/r³ — no constant term, since ψ → 1 exactly by construction and
leaving that free is what made the φ fit degenerate — gives **M = 0.5023, 0.45 % high** on
an L = 64 domain. The gate is read across two domains rather than from one number, because
ψ − 1 is an asymptotic series and each truncation lands on alternating sides of the truth:
on L = 32, where only r = 8…15 is far field, M comes out 0.587 / 0.452 / 0.524 at one / two
/ three terms. Opening the far field to r = 30 collapses that spread and the deviation falls
**4.79 % → 0.45 %**, with the fit residual dropping too.

---

## Part 4 — Single-throat regression (Phase 2), and the instability it exposed

**Superseded as a goal by Plan.md Stage 1**, which met its exit condition on the drainhole.
Kept because the instability measured here is the physics Plan.md's growing mode is a
*different* manifestation of, and because the arithmetic below is what killed the massless
route.

Configuration `params_phase2_symmetric.txt`, physics settings **identical** to
`results/wormhole-dynamics/unperturbed/params_2gpu.txt` on every key that matters (σ, all
three κ, `formulation`, `covariantZ4`, `eta`, `shift_Gamma_coeff`, `lapse_coeff`, both
floors, `wormhole_support_strength`, `phantom_mass`); only `N_full` (192 vs 256) and
`stop_time` differ.

**The unperturbed throat expands, exactly as the reference does.** The reference shows
R_areal flat at 0.500 then climbing to 0.64, with λ = 9.0120 fitted from it. Ours:
R = 0.4998 ± 0.0001 flat to t = 1.2, departure from t ≈ 1.33, |ΔR| e-folding cleanly after.
The reference run also terminates near t ≈ 3 despite asking for `stop_time = 30`.

**The rate could not be recovered, for a diagnostics reason, not a physics one.** The
published fit spans t = 0.1…1.0, where |ΔR| runs 1e-8 → 1e-4; our readout floor is ~1e-4, so
that entire window is under our noise. Fitting the only part we can see (t = 1.33…2.13,
already past the linear phase) gives 5.8, and the reference curve is also flatter than 9.012
there — the two are not in conflict. Recovering it needs a sub-grid fit through the minimum
of R(r) instead of the smallest grid sample, plus output every coarse step rather than every
twentieth.

**The expansion is published physics, not a bug.** An Ellis–Bronnikov throat is a saddle:
any nudge and it runs away, collapsing or expanding depending on sign.

**Refinement cannot fix it** — tested, not assumed. Three things rule it out: the reference
is finer than anything we ran and expands identically; the t = 0 constraint violation, which
is what kicks the throat off the saddle, is **1.38165e-2 at both `max_level` 4 and 5,
identical to six digits**; and the growth is exponential, so halving the kick buys exactly
one e-folding — worth ~0.1 in time.

**Better initial data cannot fix it either.** The window closes when the instability reaches
a few per cent: window = ln(0.03/ε)/λ. A seed of 1e-9 gives 1.9; 1e-16 gives 3.7; 1e-30
gives 7.3. Buying the free-fall time the merger needs would take a seed of ~1e-37. The
logarithm is the whole problem.

**What it cost the massless route.** Usable window t ≲ 2, against free-fall
t_ff ≈ π√(d³/(8 M_total)) for throats of radius b = 0.5:

| d | d/b | m = 0.25 | m = 0.5 | m = 1.0 |
| --- | --- | --- | --- | --- |
| 1.5 | 3 | 2.89 | **2.04** | 1.44 |
| 2 | 4 | 4.44 | 3.14 | 2.22 |
| 3 | 6 | 8.16 | 5.77 | 4.08 |
| 4 | 8 | 12.57 | **8.89** | 6.28 |

Phase 1's `d/b ≥ 8` lands on t_ff = 8.89 — **4.4× longer than the window**. Raising the mass
does not rescue it: m/b must stay ≲ 1 or the horizon swallows the throat and the run is a
black-hole merger. **And the problem is scale-invariant**: with d = 8b and m = αb,
t_ff = πb√(32/α) ∝ b while λ ∝ 1/b makes the window ∝ b as well. The ratio is a pure number;
rescaling b moves both sides equally.

*This is what sent the project to the drainhole. Plan.md Stage 1 measured a 40 M window on
the massive throat with the mass in the lapse — the same object, a different branch.*

---

## Part 5 — Implementation, file by file

Code: [Examples/BinaryWormholeMerger/](../../Examples/BinaryWormholeMerger/).

### Initial data (Route A — analytic superposition)

`BinaryWormholeInitialData.hpp`, following `BinaryBHInitialData` conventions. **Historical
form**, `wormhole_id_type = 0`; the drainhole (`id_type = 1`, Plan.md Stage 0) replaces the
bare-mass terms with the lapse:

```
psi   = 1 + [sqrt(1 + b_A²/4r_A²) − 1] + [sqrt(1 + b_B²/4r_B²) − 1]
          + m_A/(2 r_A) + m_B/(2 r_B)
chi   = psi⁻⁴,   h_ij = δ_ij,   K = 0,   Theta = 0
phi   = (1/√4π) Σ_X atan[(r_X − b_X²/4r_X)/b_X]  −  n_throats·(1/√4π)(π/2)
Pi    = 0
Â_ij  = Σ_X (3/2r_X²)[P_i n_j + P_j n_i − (δ_ij − n_i n_j) P·n]
A_ij  = chi^{3/2} Â_ij            (CCZ4 conversion, = psi⁻⁶ Â_ij)
```

Facts the gates lean on:

- **Momentum constraint exact at t = 0.** K = 0 and Pi = 0 make the matter momentum density
  vanish, and superposed Bowen–York Â_ij is flat-space divergence-free. Any nonzero
  momentum-constraint output is a bug, not superposition error.
- **Hamiltonian defect is the entire error budget:** O(b²/d²) throat–throat — better than
  BBH puncture superposition, which is O(m/d), because a pure throat has no 1/r tail — plus
  O(m/d) once masses are on, plus the near-throat massless-profile defect.
- **φ asymptote:** each atan → π/2, so a plain N-throat sum tends to N·(1/√4π)(π/2) ≈ 0.886
  for N = 2, while `StateVariables` declares φ's asymptotic value as 0 and Sommerfeld uses
  that. `wormhole_subtract_phi_asymptote = 1` (default) removes the constant — exactly free
  for a massless field; the parameter reader warns if combined with `phantom_mass ≠ 0`.
- **Single-throat regression mode:** `wormhole_throat_radius_B = 0` removes object B
  entirely — geometry, scalar and asymptote count all skip B. A bare-mass-only puncture
  (b = 0, m > 0) is a plain Brill–Lindquist term, giving a cross-check against `BinaryBH`.

### Why a single-throat drainhole run can give a clean answer at all

The massive drainhole is not merely good initial data — it is an **exact fixed point of the
whole evolved system**, which the puncture data never was:

| evolved variable | at t = 0 | why its RHS vanishes |
| --- | --- | --- |
| `chi`, `h_ij` | γ̃_ij = δ_ij exactly | γ_ij = e^{−2u} Ω² δ_ij is conformally flat |
| `Gamma^i` | 0 | follows from γ̃_ij = δ_ij; initialising to 0 is *correct* here, not an omission |
| `K`, `A_ij`, `Theta` | 0 | time-symmetric slice of a static spacetime |
| `lapse` | e^u | 1+log is ∂_t α = −2αK, and K = 0 |
| `shift`, `B^i` | 0 | Gamma-driver is sourced by ∂_t Γ̃^i, which is 0 |

No initial transient to ride out, no gauge relaxation to disentangle from the physics. Any
drift is either discretisation or the genuine Ellis–Bronnikov mode. The one deliberate
exception is the collar — α = e^u · collar is *not* the static lapse — which is why 1.3 was
run as a straight one-line A/B through `WHM_LAPSE_TYPE`.

### Matter models available in-tree

The throat expansion measured in Part 4 is a property of the **massless real phantom scalar
with a zero potential** — `ExoticScalarField` + `DefaultPotential`, which is what this
example uses. It is a saddle because it has no preferred size: nothing pulls the throat
back. That is not a property of wormholes in general, and `Source/Matter` already carries
the alternatives.

| Model | Kind | Already used by |
| --- | --- | --- |
| `ExoticScalarField` | real, phantom | **`BinaryWormholeMerger` today**, `SupportedWormholeCollapse` |
| `ComplexExoticScalarField` | complex, phantom, templated potential, conserved U(1) charge | `RotatingWormholeCollapse` |
| `BiComplexScalarField` | canonical **and** phantom complex pair | `RadialRecipe` (Bondi campaign) |
| `EffectiveTeoMatter` | prescribed rotating-wormhole stress-energy | `RotatingWormholeCollapse` |
| `ComplexScalarField`, `ScalarField`, `DustMatter`, `NoMatter` | canonical / vacuum | — |

Potentials: `DefaultPotential` (zero — **what EB uses**), `PhantomDecayPotential` (½m²φ²),
`OscillonPotential` (real sextic, self-described as metastable), `ComplexScalarPotential`
(**complex sextic on |Φ|², a true Q-ball**), `GRTresnaScalarPotential` (solver side).

The constraint solver is **not** something to be built: `RotatingWormholeCollapse` already
drives a GRTresna solve for exotic complex-scalar throats through a CLI pipeline, and it
produces data with zero initial constraint defect. Changing matter is model selection, not
a research programme. What is *not* established is that any member of that family is a
traversable throat at all.

### Route B — GRTresna-solved data (Plan.md Stage 2.2)

- GRTresna already sums two punctures (`PsiAndAijFunctions.cpp`); `bh1_*`/`bh2_*` keys exist
  end-to-end through the wrapper's params writer. **No solver C++ changes needed.**
- `recipe_initial_data_file = <path>.gridinit` switches `initData()` to
  `ExternalGridInitialData`, the same bridge as the rotating example.
- **Gate before use:** calibrate a *single* solved throat against the analytic profile
  first. There is an unresolved factor of 2 between the comment and the value in
  `../GRTresna/Examples/BosonStarBH/params_rotating_wormhole_test.txt`
  (`bh1_bare_mass = 0.25` for a throat the comment calls `b0 = 0.5`). Measure it; do not
  assume it.
- Two exotic lumps sit closer to the Lichnerowicz/York existence boundary than one, so
  expect the **solve** to be the stall point, not the evolution. Amplitude ladder first.
- The `.gridinit` bridge pins the evolution to near-unigrid resolution; the planned fix is a
  split-ID loader — interpolate only the regular part of ψ and re-add the singular part
  analytically at each AMR level.

### Files

| File | Role |
| --- | --- |
| `BinaryWormholeInitialData.hpp` | two-throat superposition, drainhole branch, Bowen–York |
| `BinaryWormholeLevel.hpp/.cpp` | level class; Route A/B branch in `initData()`; diagnostics + Weyl extraction in `specificPostTimeStep()`; tagger branch |
| `Main_BinaryWormhole.cpp` | `BHAMR<2>` so the Weyl4 particle interpolator exists |
| `SimulationParameters.hpp` | all `wormhole_*` / `binary_diag_*` keys, defaults, sanity net |
| `BinaryThroatDiagnostics.hpp` | own module, own file, default-off |
| `ThroatTracker.hpp` | throat locator for the moving boxes (Plan.md Stage 2.0), default-off |
| `StateVariables.hpp` | CCZ4 + `c_phi`, `c_Pi` (both even parity, asymptote 0) |
| `PhantomDecayPotential.hpp`, `ExternalGridInitialData.hpp` | copied from the single-throat examples |
| `params_*.txt` | smoke, gate ladders, Stage 0/1/2 templates |

`ExoticScalarField` is reused as-is; `wormhole_metric_type = 2` makes its causal
support-ramp machinery measure retarded time from the *nearest* of the two throats. The key
scheme (`wormhole_throat_radius_A/B`, `wormhole_centerA/B`) is shared between the initial
data and the matter class deliberately — one set of values.

### Diagnostics

`collapse_diagnostics.dat` keeps the **unchanged 13-column single-throat contract** so
existing analysis scripts keep working. Binary information lives in its own module and file,
default off: `binary_throat_diagnostics.dat`, **17 columns** — separation; barycentre plus
χ/lapse minima per half-space (split by `binary_diag_axis`/`split_coord`); θ₊ and the
outermost trapped radius about throat A, throat B and their midpoint.

**How θ₊ is reduced.** A closed surface is trapped only when θ₊ ≤ 0 *everywhere on it*, so
the scan bins points into radial shells about each centre and takes the **maximum** per
shell; the reported radius is the outermost shell whose maximum is ≤ 0. Shells the finest
AMR level does not cover carry **no** verdict — an empty shell must read "unknown", never
"trapped" — and if none is covered the column holds the sentinel 1e30.

**θ₊ caveat that remains:** for an EB throat θ₊ = 2(1−u)/(r(1+u)²) with u = b²/4r², so
θ₊ < 0 over the *whole* sphere for r < b/2 — that is the coordinate inversion (r → 0 is the
other asymptotic end), not a horizon. `binary_diag_min_radius` (default max(b_A, b_B), i.e.
twice what is needed) excludes it. The common-centre scan raises its own cut to
sep/2 + min_radius automatically, so a sphere counts as "common" only once it encloses both
throats; **only that scan going trapped is evidence of fusion**, and it is a proxy, not an
apparent-horizon finder.

Ψ₄: in-code `WeylExtraction` on the `BHAMR<2>` interpolator — modes (2,0), (2,1), (2,2),
(4,0) at ≥ 2 radii.

### Parameter sanity net (`SimulationParameters::check_params`)

- **error:** b_A ≤ 0, b_B < 0, negative bare masses, coincident centres;
- **error:** any of `wormhole_phi_{monopole_amplitude,perturbation_amplitude,perturbation_width}`
  still present — see "no seeded scalar perturbation" above;
- **warn:** `subtract_phi_asymptote` with `phantom_mass ≠ 0`; separation ≤ 4·b_max
  (O(b²/d²) no longer small); m_total ≥ 0.2·d (O(m/d) no longer small);
- **warn:** **all of** m = 0, P = 0, support = 1 — "massless throats do not attract; the pair
  will not fall together", the exact trap this design exists to avoid;
- **warn:** momentum on an absent object B (junk Bowen–York term).

### Symmetry notes (not exploited)

Equal head-on along z: z-reflection maps A↔B and φ is even, so octant symmetry is valid. The
spiral run breaks z-reflection and keeps nothing usable under the current reflective-BC
machinery — full box. An optimisation to revisit only if head-on wall times demand it.

---

## Part 6 — Standing risks

| Risk | Why it bites | Mitigation |
| --- | --- | --- |
| M_ADM = 0 for a *massless* throat | ultrastatic: curved, bends light, pulls on nothing — released from rest the pair never falls | `wormhole_id_type = 1` + `drainhole_mass` selects the massive branch, so the pair attracts by real gravity; keep one massless control to show the contrast |
| Route-A data is not exact | the analytic φ profile supports the massless throat, so mass adds a near-throat Hamiltonian defect and an O(m/d) superposition error | keep m/b and m/d small on Route A; the GRTresna solve removes the defect |
| Constraint solve fails | two exotic lumps sit closer to the existence boundary than one | amplitude ladder before any production solve; Route A needs no solve |
| θ₊ < 0 near each throat | r → 0 is the *other* infinity, not a centre — the proxy always fires there | `binary_diag_min_radius`; max per radial shell; only the common-centre scan is evidence of fusion |
| φ asymptote | a plain sum of two atan profiles tends to ≈ 0.886, but the boundary condition assumes 0 | subtract the constant in the initial data — free for a massless field |
| Solved-ID resolution wall | the `.gridinit` bridge pins the evolution near-unigrid | split-ID loader |
| `wormhole_support_strength` re-read footgun | `ExoticScalarField` re-reads the key from ParmParse when constructed with strength exactly 1.0 | keep the key present in every params file |
| **Massless throat expands before the merger finishes** | window t ≲ 2 against free-fall 8.89 at `d/b = 8`; not fixable by refinement (t = 0 violation identical at `max_level` 4 and 5), by a better seed (~1e-37 needed), or by rescaling b (both sides ∝ b) | **superseded**: the massive drainhole holds 40 M (Plan.md Stage 1). The complex-scalar Q-ball route was tried on the puncture throat and returned no verdict — see "Route B traps" in Plan.md |
| **Puncture throat cannot be resolved** | one cell 6.2 proper units wide against a throat of areal radius 4.5; refinement erases it before the first step; 80 % of the Noether charge dissolves in the interior | **solved** — the drainhole puts the mass in the lapse; one cell is 0.31 proper units against 3.89, and refinement sharpens the throat (Plan.md Stage 0) |
| Compactified origin blows up when centred | χ ~ r̄⁴ there and CCZ4 divides by χ; the published single-throat example dodges it with octant symmetry, which a binary cannot use — two origins, neither on a corner | **cleared as the killer** by Plan.md 1.6: refining the origin made every error *smaller* and moved the wall past 40 M. The collar (`initial_lapse_type = 6`) still buys ~3.5× on origin survival at 20 % of the throat radius |
| Lapse collar thinner than the stencil | the type-4 collar spans 0.053 in r — 0.9 cells at `max_level` 3 — so the stencil sees a step and the run dies at t ≈ 0.2 | `wormhole_lapse_core_fraction` / `_power` expose the shape; f = 0.2, p = 4 gives 25 % more collar with a bit-identical throat |
