# Validation Audit — external review of the drainhole-binary campaign

*External audit received 2026-09-04. Compacted here, with our own data checked
against every claim. Where our measurements contradict the audit that is said
plainly and marked **CONTESTED** — this document is a review to be tested, not
a verdict to be adopted.*

---

## TODO — the audit's action list, with our real status

`[x]` done · `[~]` partial, or evidence exists but is not conclusive · `[ ]` not started

### Tier (i) — must fix before publication

- [ ] **1. Constraint-solved initial data.** Replace superposition with GRTresna
  CTTK / CTTK-Hybrid (arXiv:2207.03125, 2501.13046). *Benchmark:* the Hamiltonian
  defect converges at 4th order in Δx, not the d^−1.6 we measure now.
  **Status: not started. Highest priority. GRTresna is already in our stack.**
- [~] **2. Horizon-finder orientation bug.** Compute θ± with outward = increasing
  *areal* radius; classify with the MOTS stability eigenvalue; adopt BHaHAHA.
  *Benchmark:* zero trapped surfaces on a demonstrably healthy throat.
  **Status: the bug is identified and written up as Defect 2 in GPU_PLAN
  ("a trapped shell inside a throat is not a horizon"), still OPEN. Defect 1
  (coarse-level scans reading the wrong region) is FIXED.**
- [~] **3. Isolated-throat stability control.** Evolve one exact static throat, long.
  **Status: IN FLIGHT — `single_hold_t100`, launched 2026-09-04 on card 0,
  production settings, t = 100. Seven older Stage-1 arms exist and they do NOT
  support the audit; see CONTESTED below.**
- [x] **4. Remove `core_matter_damping` and the interior freeze.** *"If the run then
  NaNs immediately, that is the physical result."*
  **Status: DONE, and the audit's expectation is not what happened.** The
  `nodamp` arms ran without it: `merge_twin_p012_nodamp_t060` died at t = 51.53
  and `..._nodamp_cf10` at 44.94 — squarely inside the same 44–56 wall as the
  damped arms. Damping is not what was holding the runs up, and removing it is
  not what kills them. It stays off in all new arms.

### Tier (ii) — the audit's proposed cause of the wall

- [~] **5. The single unstable radial mode**, truncation-seeded. **LOOKING
  CONFIRMED at t = 33 of 100** — the isolated throat is contracting exponentially
  with e-folding ≈ 2.6 units, constraints flat, error profile peaked at the throat
  and decaying both ways. Extrapolates to death at t ≈ 53, inside the 44–56 binary
  wall. See STAGE 0 INTERIM RESULT. Not final: the fit is 6 points and a growing
  oscillation is not yet excluded.
- [ ] **6. Gauge shock in 1+log** amplifying the midpoint blob. Test the
  shock-avoiding Bona–Massó family f(α) = 1 + κ/α² (arXiv:2207.06376) and a flat
  initial lapse. **Status: not started.** Our `lc1` arm (lapse_coeff 1 instead of
  2, died 43.64) probes lapse *sensitivity*, not shock-avoidance — a different test.

### Tier (iii) — accept, do not fight

- [x] **7. Topology-changing "fusion" is forbidden** without CTCs (Geroch 1967) or a
  singular slice (Tipler 1977); topological censorship (Friedman, Schleich &
  Witt, PRL 71, 1486, 1993) blocks a smooth fused exterior. **Accepted.**
- [x] **8. No common apparent horizon in the phantom-dominated midpoint** — Raychaudhuri
  focusing needs the NEC, which the phantom violates by construction. A horizon can
  form only around an individually collapsed throat. **Accepted.**
- [x] **9. No "clean merger waveform"** exists if the constituents are unstable on the
  dynamical timescale. **Accepted conditionally — it rests on item 5.**

### Tier (iv) — what the paper actually claims

- [x] **Scalar force law.** Like-signed throats repel, |F_φ/F_grav| = (a²+m²)/m² = 5;
  distance law confirmed inverse-square in an effective separation d + 3.5, blind-
  predicted to 0.3%. Like-signed pairs provably cannot merge. **Done (#8b).**
- [x] **Gauge-independent throat contraction**, ~1.0%/unit and ~0.9%/unit on two arms. **Done.**
- [x] **Matched vacuum-BBH control** validating the extraction chain (clean chirp,
  Kerr remnant M ≈ 1.9–2.0, finished clean at t = 150). **Done.**
- [~] **Corrected diagnostics** showing no common trapped surface outside the areal
  minimum. **Blocked on item 2.**
- [ ] **Endpoint statement** (singular/degenerate slice, not a merged wormhole). **To write.**
- [ ] **Drop from the paper:** any black-hole-remnant claim, any Ψ₄-only "waveform",
  any use of the word "merger".
- [~] **Report as a limitation:** the a² *magnitude* law overshoots by 2.2× at a = 3.
  Already flagged in GPU_PLAN §2 as NOT verified.

### Added by us, not in the audit

- [ ] **Scalar-channel extraction** E_Φ = ∫dt (d(rφ)/dt)² alongside Ψ₄, so the energy
  budget is complete (audit §7 is right that Ψ₄ misses the scalar channel entirely).
- [ ] **CFL halving test** — cheap, and immediately rules the gauge-speed violation
  in or out. One card, a few hours.
- [ ] **Controlled ±ε sign test** to select the collapse vs expansion branch per
  González et al., converting an uncontrolled truncation-seeded blow-up into a
  physics result. Note `BinaryWormholeInitialData` deliberately seeds **no**
  perturbation, so this needs a code change.

---

## STAGE 0 INTERIM RESULT (t = 33 of 100, 2026-09-04) — the audit is looking RIGHT

**The isolated throat is going unstable, and it looks like the real thing.** The
CONTESTED section below is preserved as written, but its conclusion is now
superseded: the Stage-1 arms were simply too short, exactly as the caveat there
warned. Read this block first.

**Phase structure of R_areal_min(t)** (exact: 3.8895):

| window | behaviour |
|---|---|
| t = 0–8 | flat to **9 significant figures**. A genuine fixed point. |
| t = 8–26 | slow swell, +7×10⁻⁴, turning over at t = 26 |
| t = 26–33 | **monotone contraction, rate growing exponentially** |

Successive dR/dt: −1.04e-4, −1.86e-4, −2.94e-4, −4.34e-4, −6.07e-4, −7.03e-4.
Fit over t ≥ 28: **e-folding τ ≈ 2.6 coordinate units.** R crossed below the exact
value at t ≈ 31.5. Excursions are growing, not ringing: 7.7e-6 → 7.1e-4 → 2.0e-3.

**Four independent reasons this is physical, not numerical:**

1. **Constraints are flat.** L2_Ham = 2.5058e-03 at t = 33 against 2.5089e-03 at
   t = 1 — slightly *decreasing* while the throat collapses. This is the audit's
   Finding 5 exactly: a growing mode *satisfies* the constraints, so global norms
   give no warning. It is also Mode A of B1, now reproduced in a one-body system.
2. **The origin is not the culprit.** chi at the compactified origin *rose* from
   7.7e-7 to 8.9e-6 — twelve times further from the 1e-8 floor. The Stage-1
   failure mode is absent.
3. **The error profile discriminator says THROAT, not origin.** `drainhole_hold_
   report.py` at t = 31/32/33 (|chi_num − chi_exact|/chi_exact):

   | rbar | t=31 | t=32 | t=33 | |
   |---|---|---|---|---|
   | 0.33 | 4.89e-3 | 4.19e-3 | 3.08e-3 | falling |
   | 0.82 | 2.13e-3 | 1.57e-3 | 7.21e-4 | falling |
   | 1.19 | 1.16e-3 | 7.96e-4 | 2.58e-4 | falling |
   | **1.57 ← throat** | 5.34e-5 | 3.16e-4 | **6.77e-4** | **growing 13×** |
   | 1.94 | 9.41e-4 | 1.17e-3 | 1.45e-3 | growing |
   | 2.94 | 1.76e-3 | 1.98e-3 | 2.22e-3 | growing |
   | 4.88 | 1.08e-3 | 1.27e-3 | 1.48e-3 | growing |
   | 9.76 | 1.53e-4 | 1.23e-4 | 8.07e-5 | falling |

   The interior is getting **cleaner** while the throat and near-exterior degrade.
   An origin front would do the opposite. This is the test the script was built
   for and it returns the answer that favours a genuine mode.
4. **The growing structure has the right shape.** It is a bump peaking near
   rbar ≈ 3, decaying both inward and outward, gone by rbar ≈ 10 — regular at the
   throat, exponentially decaying in the asymptotic region. That is González,
   Guzmán & Sarbach's description of their unstable radial mode.

**The number that matters for the campaign.** At τ = 2.6, growing the current
5.2×10⁻⁴ relative deviation to O(1) takes ≈ 20 further units → **death at t ≈ 53**.
The binary wall is 44–56. **A single throat, alone, with no companion, no orbit
and no superposition defect, dies on the same clock as every binary arm.** If that
holds, the wall was never a binary phenomenon and B1/B5 need rewriting around it.

**What is still open at t = 33.** Six points in the fit; successive ratios are
still drifting down (1.79 → 1.40), so τ could be 2.6–3.8. A growing *oscillation*
is not yet excluded — it swelled before it shrank, and one more turnover would
change the reading. The measured T = τ_proper/R_throat ≈ 0.38 (using α_throat =
e^{u(X=½)} = 0.575) is **faster than González et al.'s 0.590–0.846 range**, which
is either a real parametrisation difference, an artefact of the unconverged fit,
or a sign the (a,m) ↔ (B,γ₁) mapping in the Caveats is wrong. Do not quote T until
the run finishes. The next ~10 units settle all of it.

**Prediction scorecard.** The prediction fixed this morning — "≈5% off exact by
t = 100, O(1) at t ≈ 117" — is wrong in the conservative direction. It assumed the
2.85e-9 t=0→1 drift was the seed and τ = 5.97. In fact the settling transient
(7×10⁻⁴ by t = 26) is the effective seed and τ ≈ 2.6, roughly 4× faster.

---

## CONTESTED — where our data does not match the audit

*(Written at t = 0 of Stage 0. Superseded by the interim result above — kept
because the reasoning about the Stage-1 arms is still correct, and because the
record should show what we believed before the test rather than after.)*

**The audit's Finding 1 predicts the isolated throat destroys itself in a few
proper-time units. Our seven Stage-1 single-throat arms show the throat holding
its exact radius until something else kills the run.**

Exact answer: R_areal_min = 3.8895 at rbar = 1.618.

| arm | σ | max_level | throat R, last good t | what actually ended it |
|---|---|---|---|---|
| `stage1_lapse5_sg01` | 0.1 | 2 | **3.8960** at t = 22.5 | NaN at 24.2, **at the origin** |
| `stage1_lapse6_sg01` | 0.1 | 2 | 3.1274 at t = 31.4 | NaN at 31.4 (collar costs 20% on R) |
| `stage1_lapse5_sg00` | 0.0 | 2 | **3.87–3.95** through t = 34.7 | **GPU out of memory** at 35.2, never unstable |
| `stage1_lapse5` | 2.0 | 2 | 2.578 at t = 40 | **reached stop_time** — the shrink is dissipation |
| `s1uni128` | 0.1 | 0 | — | NaN at 6.6, origin (dx = 0.50) |
| `s1uni256` | 0.1 | 0 | — | NaN at 1.2, origin (dx = 0.25) |

Three things follow, and they cut against the audit:

1. **The deaths are at the compactified origin, not the throat.** chi → 0 like
   rbar⁴ at rbar → 0 (the other universe's infinity), so halving dx drops chi at
   the innermost cell by 2⁴ — measured ratios 18.4 and 18.5 against a predicted 16.
   That is why the *finer* unigrid arm died *sooner* (t = 1.2 vs 6.6), which is the
   exact opposite of a truncation-seeded instability, where finer means a smaller
   seed and longer survival. It is a coordinate/floor problem.
2. **`drainhole_hold_report.py` already separates the two hypotheses** and has
   already returned an answer once: at σ = 2.0 the error profile is a front that
   *starts at the origin and creeps outward*, reaching the throat around t ≈ 20 —
   so the apparent throat collapse in that arm is contamination. A genuine
   Ellis–Bronnikov mode would **peak at the throat instead**. That discriminator
   is built, tested, and will be run on `single_hold_t100`.
3. **Refinement is the protector, not the killer.** Removing refinement entirely
   made survival 4× worse; refining uniformly made it 20× worse. This does not fit
   "each finer level lowers the truncation seed and buys e-folds".

**But the audit is not refuted yet, and we should not claim it is.** Lapse at the
throat is α = e^(−πm/2a) = 0.456, so t = 35 coordinate is only ~16 proper units —
about 6 e-folds on the audit's own T ≈ 0.68–0.76. A truncation seed would still be
at the percent level, which is precisely the size of the wander those arms show
(3.87–3.95 is ±1%, and it is non-monotonic, which is noise, not growth). **That
window is too short to decide.** Also, all seven arms are max_level = 2 and predate
the current code. `single_hold_t100` fixes both: production settings, and t = 100
coordinate ≈ 46 proper ≈ 15–18 e-folds, where any seed at all is driven to O(1).

**One more caution.** The audit reads our "+1.4 units per refinement level, linear"
as the fingerprint of truncation-seeded exponential growth. That inference is
sound *if* the seed is truncation error. But B1 established that our merging arms
die with **globally clean, even falling, constraint norms** (Mode A: p012 L5 cf10
dies at 44.94 with L2_Ham at 4.0e-3, 1.3× the floor and *decreasing*), which is
consistent with the audit's reading — a local physical blow-up that global norms
cannot see. So on Mode A the audit and B1 agree. It is Finding 1's *timescale*,
not its mechanism, that our data strains against.

---

## TL;DR of the audit

- **The target is ill-posed and the wall may be physics, not gauge.** González,
  Guzmán & Sarbach prove every Ellis–Bronnikov/drainhole throat carries exactly one
  exponentially growing radial mode, on a timescale of order the throat radius over c.
  The 44–56-unit wall, its linear +1.4/level scaling, and its chi-floor and
  lapse-coefficient sensitivity are argued to be that mode, truncation-seeded.
  *(Our counter-evidence above.)*
- **Two concrete gaps: no constraint-solved initial data, and a horizon finder with
  an orientation bug.** The superposition defect is expected; the standard elliptic
  fix is itself obstructed because the Lichnerowicz uniqueness proofs assume ρ ≥ 0.
  The radial-ray "θ with s = +∂_r" proxy computes the *ingoing* expansion inside a
  throat and mislabels every throat as trapped, so "the merger forms a black hole"
  is currently unsupported.
- **An honest paper is achievable but it is not a "wormhole merger" paper.** Topology
  change is forbidden without CTCs or a singular slice, and no common trapped surface
  can form in the phantom-dominated inter-throat region. The defensible result is a
  scattering/decay study.

---

## Findings

**1. Instability of the constituent object is proven and generic.** González, Guzmán
& Sarbach (CQG 26, 015010 = arXiv:0806.0608; 26, 015011 = arXiv:0806.1370) prove via
a nodal-theorem argument that *every* static spherically symmetric ghost-scalar
wormhole — massless and massive — has precisely one unstable, exponentially growing,
everywhere-regular radial mode. Their T := τ_unstable/r_throat (proper time at the
throat), Table I:

| mass parameter γ₁ | T |
|---|---|
| 0.0 (zero-mass Ellis) | 0.846 |
| 0.5 | 0.758 |
| 1.0 | 0.675 |
| 2.0 | 0.618 |
| → ∞ | → 0.590 |

Adding mass makes it *faster* in throat units. Shinkai & Hayward (PRD 66, 044005,
gr-qc/0205041) had already shown the throat "suffers a bifurcation of horizons and
either explodes to form an inflationary universe or collapses to a black hole if the
total input energy is, respectively, negative or positive."

**2. The branch is selected by the sign of the perturbation.** Positive perturbation
of the areal-radius function → collapse to Schwarzschild; small negative → runaway
expansion; a second, more-negative threshold (ε_c ≈ −0.05) re-triggers collapse.
Truncation error has no controlled sign, so a static-data run falls onto whichever
branch numerical noise seeds first. Measured nonlinear e-foldings (≈0.836 collapse,
≈0.85 expansion, as ε→0) match the linear 0.846.

**3. "Negate T_ab, evolve canonical KG with V = 0" is equivalent to a genuine ghost
field.** With V ≡ 0, □φ = +dV/dφ = 0 = −dV/dφ, so the scalar sector is identical, and
∇_μT^μν = 0 holds regardless of the overall sign of T. The system stays strongly
hyperbolic. The real subtlety is that the Hamiltonian-constraint source flips sign,
which breaks the initial-data elliptic theory — not the evolution's hyperbolicity.
*(This confirms the modelling note we independently flagged in GPU_PLAN M2/M7:
identical only at V ≡ 0, which needs a deliberate decision before any massive-scalar run.)*

**4. Constraint-solved initial data is missing, and the naïve fix is obstructed by
ρ < 0.** Our non-converging Hamiltonian defect (2.87×10⁻⁴, 352× the floor, scaling
d^−1.6) is the standard superposition error (Lovelace arXiv:0812.3132; Zhang &
Szilágyi PRD 88, 084033). But Lichnerowicz–York uniqueness rests on the maximum
principle with ∂f/∂ψ ≥ 0, guaranteed only for ρ ≥ 0 (Gourgoulhon arXiv:0704.0149;
Baumgarte–Ó Murchadha–Pfeiffer on XCTS non-uniqueness). With ρ < 0 you can generically
lose existence or uniqueness. The workaround is already in our stack: **CTTK**
(Aurrekoetxea, Clough & Lim, CQG 40, 075003, arXiv:2207.03125), in **GRTresna**
(arXiv:2501.13046) — solve an *algebraic* equation for K at chosen conformal factor,
which "evade[s] the existence and uniqueness problem … without using the usual
conformal rescaling of the source terms", the last clause mattering because
"reconstructing the fields' configurations from the rescaled quantities is potentially
problematic." CTTK-Hybrid is the natural fit; the momentum constraint goes via the
standard York vector-Laplacian, unaffected by the sign of ρ (our K = 0, Π = 0
Bowen–York data already satisfies it exactly).

**5. CCZ4 constraint damping is not guaranteed here.** Gundlach, Martín-García,
Calabrese & Hinder (CQG 22, 3767, 2005) prove damping of low-amplitude, high-frequency
constraint modes for κ₁ > 0 by linearising about a background; it assumes no energy
condition per se, but the nonlinear negative-energy regime is uncharted (Weyhausen,
Bernuzzi & Hilditch, PRD 85, 024038, explored it numerically for Z4c). κ₂ = 0 is the
standard recommendation (Alic et al. arXiv:1307.7391) and κ₁ = 3.0 is a common value,
so our choices are fine. **The key point:** Mode A (Ham norm at its floor and
*decreasing* just before the NaN) is not a damping failure at all — it is a local
physical blow-up, invisible to global norms because it is spatially localised. Damping
cannot help, because the growing structure *satisfies* the constraints. Treat
κ-tuning as cosmetic here.

**6. The horizon finder is wrong in a way that invalidates the black-hole claim.** A
static throat is a minimal surface with θ₊θ₋ = 0 that a naïve finder reads as
marginal; worse, "outward" as +∂_r inside a throat points toward the *other* mouth
where areal radius decreases, so θ computed with s = +∂_r is the *ingoing* expansion
and its negativity is meaningless. Correct discriminators: (a) Hochberg–Visser — a
throat is a marginally **anti**-trapped surface (PRD 58, 044021, gr-qc/9802046);
(b) the MOTS stability-operator principal eigenvalue (Andersson, Mars & Simon 2008,
gr-qc/0506013; Jaramillo arXiv:1410.0509) — a strictly stable MOTS (λ₁ > 0) is a
black-hole horizon, a throat is not. Recommended tool: **BHaHAHA** (Etienne et al.,
CQG 43, 075007, arXiv:2505.15912), infrastructure-agnostic and usable from AMReX —
but it parametrises surfaces as star-shaped about a centre, so seed it on each mouth
separately; it cannot represent the non-star-shaped throat tube.

**7. A trapped surface cannot form where the phantom dominates.** Trapped-surface
formation needs focusing of the outgoing null congruence, which by Raychaudhuri needs
R_μνk^μk^ν ≥ 0, i.e. the NEC (Penrose 1965). The phantom violates the NEC by
construction — that is what holds the throat open. With ρ ≈ −1.7×10⁻² (shell mean) at
the midpoint and ρ ~ −1.2 pointwise on the throat rings, the inter-throat region is
phantom-dominated and cannot host a common MOTS.

**8. The midpoint blob is real, plausibly amplified by a gauge shock.** It is
resolution-converged with bounded 3-Ricci and only 1–3% Hamiltonian violation, so it
is not a grid artifact. Negative ρ at the midpoint with K > 0 (contraction) is exactly
the *compressive* configuration González et al. show drives collapse. The gauge layer:
1+log's singularity avoidance rests on SEC-type focusing of the normal congruence, and
with ρ < 0 and negative S that sign flips, so 1+log is outside its design regime; it is
independently known to form coordinate shocks (Alcubierre gr-qc/0210050, gr-qc/0503030).
**Prediction worth testing:** shock-avoiding slicing will move or soften the blob if it
is gauge-amplified, and will *not* remove it if it is the physical collapse branch —
a clean discriminator either way. That the Helfer/Ning correction makes the blob
nucleate *earlier* fits it feeding the physical mode rather than curing constraint error.

**9. Waveform extraction is not yet meaningful.** With a 1/r scalar tail
(|φ| ~ 6×10⁻³ at the extraction sphere) the exterior is non-vacuum; Ψ₄ captures only
the spin-2 tensor sector and **misses the scalar channel entirely** — the Bondi news,
not Ψ₄, includes it. The absence of chirp/ringdown, the superposition of the p = 0.12
and p = 0.45 waveforms over t = 0–25, and the fly-by radiating harder than the merger
arm are all consistent with the "waveform" being initial-data junk plus the throat
mode. The matched vacuum-BBH control validates the chain, which only sharpens the
contrast.

---

## Details worth keeping

**Is "merger" well-posed?** Three layers of theorem: Geroch (1967) — compact cobordism
between non-diffeomorphic slices without CTCs is impossible; Tipler (Ann. Phys. 108,
1977) — with Einstein plus the WEC, topology change in a finite region *must* carry
singularities, no causality assumption needed, and NEC/WEC violation buys topology
change only through a *degenerate* slice; topological censorship (FSW, PRL 71, 1486,
1993) — the domain of outer communication is simply connected under the averaged NEC.
So the three candidate meanings resolve as: **(a)** two mouths fusing = genuine
spatial-topology change, forbidden; numerically it can only appear as a degenerate
slice where det g → 0 and curvature blows up — **which would be indistinguishable from
the h11/K NaN we see**; **(b)** a single black hole forming and swallowing both throats
— allowed, and what Shinkai–Hayward and González et al. see for one throat, but it
produces a black hole, not a wormhole; **(c)** scattering/decay with no common horizon.

**No published NR simulation of two wormholes merging exists.** The closest is the
single-object 3D GRTeclyn study (arXiv:2604.00071), which notes that "classical GR
evolution mathematically preserves the underlying spatial topology (ℝ×S²)" and models
pinch-off as metric degeneration. **Note for us: that is our own prior paper on this
code stack.** It uses the same naïve θ₊-on-coordinate-spheres proxy and the same
reduce-phantom-support trick flagged here, so the audit is in effect telling us the
same limitations propagate forward — read it as precedent *and* as a list of what to
fix, not as independent corroboration.

**Infrastructure gaps.** (i) The chi/lapse floors plus ad-hoc `core_matter_damping`
are not a defensible scheme — zeroing φ and Π in a lapse window manufactures and
destroys energy in the region that dominates the dynamics. The standard alternatives
(excision/turduckening — Brown, Diener, Sarbach, Schnetter & Tiglio) require an actual
horizon to hide violations behind, which we do not have; that neither standard fix
applies is itself evidence the target is ill-posed. *(We have already run without the
damping — see TODO item 4 — and the wall did not move.)* (ii) The strength-4 sponge at
r = 24→32 is fine as a crude absorber but not for quantitative waveforms; the phantom's
1/r tail reflects. Use radiative/constraint-preserving boundaries, ideally CCE, for any
radiation claim. (iii) First-NaN on a freshly regridded finest level: with 4th-order
stencils, prolongation must be ≥5th-order and buffered; but given Finding 1 it is more
likely the physical instability reaching newly resolved short-wavelength content first.
(iv) **CFL:** with CCZ4 gauge modes up to √2·c and α ~ 1 over most of the domain, a
Courant factor tuned for collapsed-lapse BBH may be marginal where α ~ 1. A
factor-of-2 test is cheap and decisive.

**Area theorem with NEC violation.** Hawking's area theorem *requires* the NEC.
González et al. explicitly observe a horizon whose areal radius *decreases* as it
swallows negative-energy scalar, and report a quasi-universal final BH mass
m_AH ≈ 0.22 in throat units for small positive amplitudes. **Do not assume monotonic
horizon growth.** Our gauge-independent throat contraction (~1.0%/unit, ~0.9%/unit) is
the robust reportable quantity.

**Updating literature.** Batic & Dutykh (EPJ C 85, 144, 2025, arXiv:2502.05486) find
purely-imaginary QNMs tied to the Schwarzschild-radius/throat ratio that direct-
integration studies missed: scalar instabilities "arise when this ratio exceeds 1.0,
with the threshold value of 1.0 itself included", and axial onset is at smaller ratios
— more of parameter space is unstable than thought, relevant because a binary
necessarily excites non-radial channels. Azad, Kunz et al. (PLB 848, 138349, 2023,
arXiv:2403.08387) show slow rotation can *quench* the radial mode: "there arises always
a critical angular momentum, when the mode reaches zero". **Our data has no spin, so no
quenching applies** — but it is the one route to a stabilised constituent. Also: the
simplified re-derivation in GRG 51, 19 (2019), arXiv:1805.02602; the charged
generalisation (PRD 80, 024023, arXiv:0906.0420) preserves the instability; Kain, CQG
43, 045014 (2026) again finds expansion/collapse.

**Foundational refs.** Ellis, J. Math. Phys. 14, 104 (1973); Bronnikov, Acta Phys.
Polon. B4, 251 (1973).

---

## Recommended sequence

**Stage 0 (days, decisive) — RUNNING.** Isolated single throat, exact static data,
production settings, t ≳ 100. `single_hold_t100`, card 0, launched 2026-09-04.
Measurement: R_areal_min(t) from `small_data/areal_radius.dat`, scored by
`drainhole_hold_report.py`, which also gives the error profile err(r,t) that separates
a throat-peaked mode from an origin-born front. *If it diverges with e-folding ~R_throat,
the wall is the physical instability and the paper pivots to scattering/no-merger
immediately. If it holds to t = 100 at production resolution, Finding 1 does not
explain our wall and the audit's Tier (ii) fails for our parametrisation.*

### Stage 0's falsifiable prediction, fixed before the answer is known

First two samples, 2026-09-04 (exact closed form: R = 3.8895):

| t | R_areal_min | r_at_min |
|---|---|---|
| 0.0 | 3.8899727479802544 | 1.5944 |
| 1.0 | 3.8899727590573252 | 1.5944 |

Discretisation error is 0.012% (vs 0.06% for the old max_level = 2 arms), and R is
**stationary to nine significant figures** over the first unit. The drift is
ΔR = 1.11×10⁻⁸ absolute, 2.85×10⁻⁹ relative — real, not roundoff (double-precision
eps on 3.89 is ~9×10⁻¹⁶). **Take that as the seed amplitude.**

If the González–Guzmán–Sarbach mode is present at the audit's rate, it e-folds in
τ ≈ T·R_throat ≈ 0.7 × 3.89 = 2.72 units of proper time at the throat, i.e.
2.72/0.456 = **5.97 units of coordinate time**. Growing a 2.85×10⁻⁹ seed through
t = 100 gives 16.7 e-folds, a factor 1.8×10⁷:

> **Prediction: R_areal_min should be ≈ 5% off the exact value by t = 100, with a
> clean exponential visible over the last ~30 units. Reaching O(1) — throat
> destroyed — would take t ≈ 117.**

So this run is correctly sized: it catches the onset with margin, and it cannot
return an ambiguous "too short to tell" like the Stage-1 arms did. **If R is still
flat at the 10⁻⁶ level at t = 100, the mode is absent or very much slower than
claimed, and Tier (ii) fails.** Either way the run also gives the seed-vs-growth
data needed to state the result quantitatively rather than as a survival anecdote.

Caveat on the seed: the t = 0→1 drift may be settling rather than the mode itself.
That only makes the prediction conservative — a larger true seed blows up sooner.

**Stage 1 (weeks, mandatory for publication).** GRTresna CTTK-Hybrid initial data
(benchmark: defect scales as Δx⁴, not d^−1.6); fixed horizon diagnostics (benchmark:
zero trapped surfaces on a demonstrably healthy throat); damping and freeze already off.

**Stage 2 (weeks, to characterise the wall).** Repeat d = 12 with shock-avoiding
slicing and a flat initial lapse — if the wall is unchanged it is the instability, if
it moves substantially gauge is contributing. Add scalar-channel extraction and report
the full energy budget. Run the controlled ±ε sign test.

**Stage 3.** Write it as the no-merger/scattering paper. Lead with the scalar force
law and the topology/NEC no-go arguments; present the corrected diagnostics as the
methodological contribution (how *not* to find a wormhole horizon); state the
singular-slice endpoint.

**Suggested title thrust:** *"Phantom-scalar drainhole binaries do not merge:
instability-limited scattering and the impossibility of a common horizon."*

**Thresholds that would change the recommendation.** (a) If a constraint-solved,
spin-stabilised (Azad et al.) or otherwise mode-quenched throat is individually stable
to t ≳ 500, a genuine dynamical-binary study becomes conceivable — but only for the
stabilised variant. (b) If, with corrected diagnostics, a strictly stable MOTS (λ₁ > 0)
appears *outside* the areal minimum around a collapsed throat, a black-hole-formation
sub-result becomes defensible — still not a "wormhole merger" paper.

---

## Caveats (the audit's own, plus ours)

- The e-folding in *coordinate* time for our (a = 2, m = 1) drainhole under our slicing
  is not tabulated anywhere. T = 0.68–0.76 is a proper-time-at-throat quantity
  interpolated from Table I of arXiv:0806.0608, and the translation to the 44–56-unit
  wall involves the uncertain truncation seed and the lapse redshift. The *qualitative*
  chain is robust; the numbers need Stage 0.
- The mapping between our (a, m) and González et al.'s (B, γ₁) was **inferred, not
  verified line by line.** The trend and the single-mode existence are certain; the
  exact T at m/a = 0.5 is an interpolation. **Worth checking properly before we cite it.**
- Batic & Dutykh's ratio-threshold instabilities are recent and not yet independently
  confirmed; treat as provisional.
- Whether 1+log specifically forms a *shock* in this negative-energy configuration is a
  plausible inference from Alcubierre's analysis, not a published result for phantom
  matter. Stage 2 is the test.
- **Ours:** the audit's Finding 1 is stated with more confidence than our own
  single-throat data currently supports. It is the single most consequential claim in
  the document and it is under test right now. Nothing in the paper should be reframed
  around it until `single_hold_t100` reports.
