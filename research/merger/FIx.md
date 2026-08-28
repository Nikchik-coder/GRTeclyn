# Building and Merging Two Regular Exotic-Matter Wormhole Throats in 3D Cartesian CCZ4: A Methodology

## Implementation plan — status board

Started 2026-08-28. This section is the working checklist; everything below it is the
deep-research report it was derived from, unedited.

| Stage | What it settles | Status |
| --- | --- | --- |
| 0 | Kill the coordinate bug — a throat with χ = O(1) at the minimal surface | **done 2026-08-28** |
| 1 | Single regular throat holds still, charge/geometry drift bounded | next |
| 2 | Two-throat data: superposition + correction, then a CTTK solve | not started |
| 3 | Head-on merger with ADM mass, Ψ₄ out | not started |
| 4 | Write | not started |

**One deliberate departure from the report, recorded here because it changes Stage 0.**
The report says to swap the isotropic chart for the proper-radial (Ellis) chart
`ds² = −e^{2u}dt² + e^{−2u}[dl² + (l²+a²)dΩ²]`. That chart covers `l ∈ (−∞,∞)`, so its
spatial slice has topology `R × S²`, which **cannot** be embedded in one Cartesian box —
§3(a) of the report says as much. The two charts are related by the exact map
`l = r̄ − a²/(4r̄)`, and the isotropic form is *equally regular at the throat*; what it does
extra is compactify the far universe to `r̄ → 0`, which is unavoidable in a single box.

So the isotropic chart was never the bug. **The bug was earning the ADM mass with a
Brill–Lindquist puncture**, `ψ += m/(2r̄)`, which drives χ → 0 *at the throat itself*. The
massive drainhole earns the same ADM mass from the **lapse** instead, and leaves the
spatial conformal factor bounded. That is the fix, and it is a ~15-line change to the
initial data rather than a new chart.

### Stage 0 — regular throat (kill the coordinate bug)

- [x] **0.1** Derive the massive Ellis–Bronnikov drainhole in the isotropic coordinates the
  code already uses; verify it solves the Hamiltonian constraint exactly
- [x] **0.2** Standalone check, no GPU: interior minimum of R exists, χ at the throat,
  proper cell width, the m/a ceiling, the collar zone, free-fall time
- [x] **0.3** Implement as a new **default-off** initial-data mode in
  [BinaryWormholeInitialData.hpp](../../Examples/BinaryWormholeMerger/BinaryWormholeInitialData.hpp);
  no archived run may change
- [x] **0.4** Parameters + sanity net in
  [SimulationParameters.hpp](../../Examples/BinaryWormholeMerger/SimulationParameters.hpp)
- [x] **0.5** Build clean (CPU, then CUDA)
- [x] **0.6** In-code verification at t = 0: χ_throat O(1) and R_min preserved at
  `max_level` 0, 1 **and** 2 — the AMR test the puncture failed

**Proceed-benchmark (report Stage 0): PASSED**, 2026-08-28. χ_throat within a small factor
of 1, R_min stable to < 1 % under refinement, before the first timestep.

#### What 0.6 measured

`params_stage0_drainhole.txt`, one throat, a = 2, m = 1, L = 64, N = 128, run at three
refinement depths. Analytic prediction: r̄ = 1.6180, R_min = 3.8895, χ_throat = 0.1731.

| `max_level` | dx at the throat | throat under the **puncture** | throat under the **drainhole** | error vs analytic |
| --- | --- | --- | --- | --- |
| 0 | 0.5 | present | present, R = 3.908 | 0.48 % |
| 1 | 0.25 | **gone — monotonic** | present, R = 3.890 | **0.01 %** |
| 2 | 0.125 | **gone — monotonic** | present, R = 3.892 | 0.06 % |

Refinement now **sharpens** the throat instead of erasing it, and it is still there after
two timesteps, unmoved to four digits. The 0.48 % at `max_level` 0 is the grid straddling
the minimum (nearest sample r̄ = 1.785), not an error in the data.

The proper-distance picture at `max_level` 2, which is the number that mattered:

| | throat areal radius | width of one cell there, in proper distance |
| --- | --- | --- |
| Brill–Lindquist puncture (measured 2026-08-28) | 4.5 | **6.2 — wider than the throat** |
| massive drainhole (measured 2026-08-28) | 3.89 | **0.31** |

The throat region now spans ~16 cells of proper width 0.2–0.5. That is a factor of ~20 in
proper resolution at the throat, bought with no extra grid at all — the same L = 64,
N = 128 box that could not resolve the puncture.

**The block's first half is cleared.** MatterDebug.md's exit condition has two parts —
χ of order 1 at the minimal surface, and Noether charge conserved to a few per cent. The
first is done. The second cannot even be posed yet: the merger's matter is a *real*
phantom scalar, which carries no Noether charge. It becomes a Stage 1 question.

#### What 0.1–0.2 established

The solution, in the isotropic radius the code already uses. With
`X = (r̄ − a²/4r̄)/a` and `Ω = 1 + a²/(4r̄²)`:

| | |
| --- | --- |
| static lapse exponent | `u = (m/a)(arctan X − π/2)`, → 0 at infinity |
| lapse | `α = e^u` — part of the solution, not a gauge choice |
| conformal factor | `χ = e^{2u} / Ω²` |
| scalar | `φ = √(a²+m²)/(a√(4π)) · arctan X` |
| | `K = 0`, `A_ij = 0`, `Π = 0`, `M_ADM = m` |

The amplitude is fixed by the field equations (`4π C² = a² + m²`), not chosen, which is
what makes both constraints hold **identically** at t = 0 for a single throat — the
superposed puncture data carried a Hamiltonian defect by construction. Verified to
roundoff (residual 1e-10, growing as h shrinks, i.e. pure roundoff) by
[drainhole_throat_check.py](../../grteclyn-wrapper/scripts/validation/drainhole_throat_check.py).

Three properties are **derived, and two of them contradict the obvious guess**:

- the minimal surface is at `l = m`, i.e. `r̄ = (m + √(m²+a²))/2` — *not* at `l = 0`, which
  is where the massless case puts it;
- `R_min = e^{−u(m)}√(m²+a²)`;
- **χ at the throat barely moves with mass**: 0.25 at m/a = 0, 0.19 at 0.3, 0.15 at 1.0.
  The throat migrates outward as m grows, and the larger Ω⁻² almost exactly cancels the
  smaller e^{2u}. Proper cell width there is 2.0–2.6 dx *whatever the mass*.

That last one is the whole result. **Mass no longer costs resolution.** Against the
puncture it replaces:

| | proper cell width at the minimal surface | and inward |
| --- | --- | --- |
| Brill–Lindquist puncture | 4 dx (χ = 1/16, mass-independent) | keeps falling — 12.5 dx measured at dx = 0.5, m = 2 |
| massive drainhole | 2.0–2.6 dx | χ < 0.01 only inside r̄ = 0.98, against a throat at 2.69 |

The unresolvable region does not go away — χ still vanishes like r̄⁴ at the compactified
far infinity, which is intrinsic to holding a wormhole in one Cartesian box — but it now
sits **well inside** the minimal surface, so the origin-isolating collar can freeze it
without touching the throat. That is lapse type 6.

**The one new design constraint**, which the report does not state: `m/a` is capped near 1.
Past that, χ_throat starts falling back toward puncture values. A heavier binary wants a
*bigger* throat, not a heavier one — and a bigger throat means a longer free-fall time
(t_ff ∝ a at fixed m/a), so this is the trade that now sets the grid.

### Stage 1 — single regular throat, static hold

- [ ] **1.1** Params file: one throat, α = e^u exactly, 1+log, Gamma-driver from β = 0,
  `covariantZ4 = 0`, Kreiss–Oliger σ ≈ 1–2, Sommerfeld out
- [ ] **1.2** Run to t ≳ 20–30 M and measure: R_min drift, constraint norms, whether the
  lapse collar is still needed once χ is O(1) at the throat
- [ ] **1.3** Decide the collar's fate — if a regular throat no longer needs it, delete it

**Benchmark:** no gauge detonation, R_min drift attributable to the known EB unstable mode
(one growing mode, timescale ~ throat/c) rather than to the grid.

### Stage 2 — two-throat initial data

- [ ] **2.1** Superpose two drainholes with the **Helfer/Ning correction**
  (`γ_ij = γ_ij^A + γ_ij^B − γ_ij^B(x_A)`), not plain superposition
- [ ] **2.2** Measure the Hamiltonian defect vs separation; establish the d/a floor
- [ ] **2.3** If the defect is too large: GRTresna **CTTK** solve (algebraic K, no source
  rescaling — the escape hatch for phantom matter). Watch for K² < 0 nodes

**Benchmark:** Ham and Mom L₂ converging at ≥ 2nd order; χ = O(1) at *both* throats.

### Stage 3 — the run

- [ ] **3.1** Head-on first (axisymmetric, cheapest, still gives ℓ = 2 Ψ₄)
- [ ] **3.2** Ψ₄ at multiple radii; apply the v ≈ c propagation test to separate physical
  radiation from superluminal CCZ4 constraint modes
- [ ] **3.3** Convergence and error budget

### Stage 4 — write

- [ ] **4.1** If 1–3 hold: two-throat head-on with Ψ₄
- [ ] **4.2** If 2 or 3 stalls: methods Letter on the regular two-throat data (report
  fallback c), or the exotic-lump head-on (fallback e)

### Decision gates (from the report, kept literally)

| If | Then |
| --- | --- |
| Regular-chart single throat still loses charge > few % | the instability is *physical*, not numerical — reframe as collapse/expansion of a two-throat system |
| CTTK returns K² < 0 with two exotic lumps | past the existence boundary — reduce ADM mass, increase separation, and **report the boundary as a finding** |
| Timelike inner boundary (excision) unstable | abandon true topology for this paper |

---


## TL;DR
- **Your blocker is a coordinate choice, not a physics wall.** You mapped the *second universe onto the grid origin* (compactified infinity, χ→0) — exactly what the single-throat GRTeclyn paper (arXiv:2604.00071) does. The fix is to place the throat at a **finite** radius where the conformal factor is O(1): in isotropic coordinates the throat sits at r̄ = b₀/2 where ψ = √(1+b₀²/4r̄²) = √2 and χ = ψ⁻⁴ = 1/4 (proper cell width ≈ 2·dx), and better still in the proper-radial (Ellis) chart ds² = −e^{2u}dt² + e^{−2u}[dl² + (l²+a²)dΩ²], where the throat at l=0 is regular by construction (χ = e^{2u} is O(1), R(l) never reaches zero).
- **The most time-efficient route to a two-throat merger with Ψ₄ extraction** is: (i) build each throat in the proper-radial chart; (ii) add ADM mass through the massive Bronnikov/"drainhole" branch (M = mγ) so the pair attracts; (iii) superpose the two with the Helfer/Ning conformal-factor-correction; (iv) solve the constraints with GRTresna's **CTTK** method, which is purpose-built to avoid the wrong-sign Lichnerowicz existence problem for exotic (phantom) sources.
- **If a clean constraint-satisfying two-throat solve is out of reach in a month, two honest fallbacks are near-guaranteed:** an axisymmetric (2+1) two-throat head-on, or a two-exotic-lump (boson-star-style) head-on. Both keep χ~O(1), have direct 3D Cartesian precedent, and give inspiral/merger + Ψ₄ — at the cost of the literal "first wormhole-topology merger" claim.

## Key Findings

**1. Your diagnosed blocker is precisely the construction in arXiv:2604.00071 — and that paper is a cautionary tale, not a template.** Shirokov's single-throat GRTeclyn run explicitly maps "the secondary asymptotic region … compactified such that its spatial infinity maps exactly to the grid origin r̄→0 (ψ→∞)," then evolves χ = (4r̄²/(4r̄²+b₀²))² which "smoothly vanishes at the origin (χ→0)." That is the same χ→0 puncture interior you are fighting. It did *not* hold: with a χ_min=10⁻⁸ floor, interior noise from the compactified origin destroyed the static equilibrium by t≈1.5M and the moving-puncture gauge failed at v>0.6c "anti-collapse." The paper's own "Future work" calls for "fully constraint-satisfying initial data (via an elliptic solver)." Reuse its numerical *settings* (κ₁=3, κ₂=0, covariantZ4=0, octant symmetry, AMR on χ-gradients, Sommerfeld outer BCs, RK4), but reject its *geometry*.

**2. There is a regular chart that keeps χ finite at the throat — the one every 1D/2D wormhole evolution uses.** The proper-radial (Ellis) form ds² = −e^{2u(l)}dt² + e^{−2u(l)}[dl² + (l²+a²)dΩ²], with u(l) = (m/a)(arctan(l/a) − π/2), has areal radius R(l) = e^{−u}√(l²+a²) that never reaches zero, and the spatial conformal factor e^{−2u} is finite and O(1) at the throat (e^{πm/a} at l=0; exactly 1 in the massless m=0 case, giving ds² = −dt² + dl² + (l²+a²)dΩ², φ ∝ arctan(l/a)). This is the chart of Shinkai–Hayward (gr-qc/0205041), González–Guzmán–Sarbach (0806.0608, 0806.1370), and Kain (2210.04905, 2602.18231).

**3. The isotropic chart can be made regular too — the key is that the isotropic radial coordinate is double-valued.** The map l = r̄ − b²/(4r̄) sends *both* r̄∈(b/2,∞) and r̄∈(0,b/2) onto the two universes, throat at the finite radius r̄ = b/2 where ψ is finite. Compactifying one universe to r̄→0 (as 2604.00071 did) is a *choice* that produces χ→0, not a necessity. Placing the throat at r̄ = b/2 with χ = 1/4 and handling the far universe by truncation/excision (rather than crushing it to a point) is the fix.

**4. Two-throat initial data has an exact precedent (Smirnov, 2312.09622) and a robust, generalizable superposition fix (Helfer 2022 / Ning 2024).** Smirnov gives a rigorous existence proof for two-mouth phantom data but for *one* wormhole (topology S²×S¹ minus a point); the boson-star superposition-plus-correction machinery is the transferable route for two *independent* throats.

**5. Adding ADM mass while keeping the throat regular is analytically solved:** the massive Bronnikov/drainhole branch (M = mγ) does exactly this in the proper-radial chart, and the Lanzhou group (2407.09591) gives a regular ansatz on a compactified coordinate with ADM mass tunable through zero.

## Details

### 1. Regular wormhole coordinates for Cartesian NR

**Proper-radial / global chart (recommended primary route).** Write each throat as
ds² = −e^{2u(l)}dt² + e^{−2u(l)}[dl² + (l²+a²)(dθ²+sin²θdφ²)],
massless case u=0. The two sheets l>0 and l<0 are two copies of R³ glued at the l=0 throat two-sphere. In a single Cartesian box one radial coordinate cannot cover both sheets — that is the crux — so you choose one of the far-universe treatments in §3. The 3+1 split γ_ij = e^{−2u}(dl²+(l²+a²)dΩ²) gives χ = e^{2u} that is O(1) everywhere; your exit condition is met by construction, and the interior minimum of R(l) survives because the chart never compresses it to a point.

*Consequence of the second asymptotic region.* Every self-consistent evolution covering both universes uses a 1D radial line: Shinkai–Hayward's dual-null grid "covers both universes connected by the wormhole throat"; González–Guzmán–Sarbach evolve x∈(−∞,∞) with outgoing-wave BCs "pushed far from the throat" so the extraction region is causally disconnected from the artificial boundary. In 3D Cartesian you cannot hold both R³ sheets in one chart. You must (a) use a multi-block/wormhole-adapted grid (not native to GRTeclyn/GRChombo), (b) excise/truncate the second universe near the throat, or (c) compactify it (the failed 2604.00071 route).

**Kain's codes (2210.04905, 2602.18231) — the gold standard for regularity.** Kain uses **double-null coordinates** ds² = −e^{2σ(u,v)}dudv + r²(u,v)dΩ² and evolves the areal radius r directly, so regularity at the throat is automatic (r has a nonzero minimum, σ is finite, no conformal factor to blow up). Static seed: ds² = −(1/a²)dt² + a²dx² + a²(x₀²+x²)dΩ², a(x)=exp[−a₁arctan(x/x₀)], φ=φ₁arctan(x/x₀), x∈(−∞,∞), throat at x_th = a₁x₀, r_th = a₂x₀√(1+a₁²)e^{−a₁arctan(a₁)}, ADM masses M_± = ±a₁a₂x₀e^{∓a₁π/2}; a₁=0 is the massless symmetric zero-mass wormhole. This is spherically symmetric (1+1D) and radiates no gravitational waves (lowest radiative multipole ℓ=2) — which is exactly why you need 3D — but the coordinate philosophy (evolve the areal radius / use a regular chart with no puncture) is what transfers.

**González–Guzmán–Sarbach (0806.0608 linear; 0806.1370 nonlinear).** Metric ds² = e^{2a}(−e^{4λc̄}dt²+dx²) + (x²+b²)e^{2c̄}dΩ², x∈(−∞,∞), gauge d = a+2λc̄ (λ=0 gives principal part = flat wave operator ∂_t²−∂_x², no shock formation, good for expansion; λ=1 is singularity-avoiding, good for collapse). Static solution d = −a = γ₁arctan(x/b), c̄ = −γ₁arctan(x/b), Φ = Φ₁arctan(x/b), with −κΦ₁² = 2(1+γ₁²), throat at x_th = γ₁b, r_th = b√(1+γ₁²)e^{−γ₁arctan(γ₁)}, ADM masses m_∞ = bγ₁e^{−γ₁π/2}, m_{−∞} = −bγ₁e^{γ₁π/2}. Per González, Guzmán & Sarbach (CQG 26, 015010, 2009, arXiv:0806.0608), "all these solutions are unstable with respect to linear fluctuations and possess precisely one unstable, exponentially in time growing mode. The associated time scale is shown to be of the order of the wormhole throat divided by the speed of light." Transferable technique: they build constraint-satisfying time-symmetric perturbed data by perturbing c̄ (areal radius) and solving the Hamiltonian constraint for Φ_x.

**Shinkai–Hayward (gr-qc/0205041).** Dual-null, grid covers both universes; positive-energy pulse → black-hole collapse, negative-energy (ghost) pulse → inflationary expansion — the bifurcation you will see. Confirms substantial mass can be radiated during destabilization.

### 2. Isotropic Ellis throat without a puncture — the crucial point

The isotropic radius is *double-valued* under the inversion r̄ → b²/(4r̄) (Smirnov's map J: ρ ↦ a²/4ρ, throat as fixed point). Two copies of r̄>0 each cover one universe, glued at r̄ = b/2, where ψ = √(1+1) = √2, so χ = ψ⁻⁴ = 1/4 — O(1), proper cell width dx/√χ = 2·dx, fully resolvable. **This is the fix.** Your error (and 2604.00071's) was using a *single* r̄∈(0,∞), which forces one universe onto r̄→0, the compactified point where χ→0.

To place the throat at finite radius with χ~O(1): make the box *one universe plus the throat*, physical region r̄∈[b/2,∞), throat two-sphere at r̄ = b/2 (χ = 1/4). The region r̄<b/2 is the other universe — do **not** compactify it to the origin. Either (a) include a finite shell of it (a second copy — impractical in one box), (b) excise it just inside the throat (§3), or (c) fold both universes onto r̄∈(0,∞) via the inversion with an isometry (inversion) boundary condition at the throat sphere — Smirnov's construction. The proper-radial chart of §1 makes all of this automatic (l=0 throat, l≷0 the two sheets) and is preferable.

### 3. Excision vs. full-domain

- **(a) Both universes in the box.** Tractable only in 1D/2D (dual-null, spherical). In 3D Cartesian AMR no single chart smoothly covers both R³ sheets glued at a two-sphere; you'd need multi-block/wormhole-adapted grids not native to GRTeclyn/GRChombo. **Not recommended in a month.**
- **(b) Excision at/just inside the throat.** Turns each wormhole into a one-sided object. The obstacle: a traversable throat has **no horizon**, so the excision boundary is **timelike**, and you genuinely need physical inner boundary conditions (unlike BH excision, where the boundary sits inside a horizon and can be pure outflow). Standard BH excision (Alcubierre–Brügmann gr-qc/0008067) and turduckening (Brown et al. 0707.3101, "Excision without excision") both rely on the excised region being causally disconnected inside a horizon; turduckening's rigorous guarantee that "constraints propagate causally and so any constraint violations introduced inside the black holes cannot affect the exterior" holds only for the BSSN parameter range 1/4<m≤1 **and** a horizon. Neither transfers to a horizonless throat. Isometry/inversion boundary conditions at the throat (Smirnov; classic Misner-data work) are the principled choice, but **no one has demonstrated them stably in 3D Cartesian CCZ4** — flag as research-grade risk.
- **(c) Compactify the second universe (2604.00071 route).** Produces χ→0 and NaNs. **This is your blocker. Do not use.**

**Bottom line:** for a first result, avoid the timelike-inner-boundary problem by using the proper-radial chart with the far universe truncated at large-but-finite |l| under a Sommerfeld condition (as GGS do at finite x), or reframe the objects as horizonless lumps (§7) so there is no second universe.

### 4. Two-throat / multi-throat initial data

**Smirnov (2312.09622).** Time-symmetric (K_ij=0) IDP for GR + phantom scalar (+Maxwell). The phantom kinetic term's wrong sign forces the metric potential ψ to be a *complex* harmonic function, ψ(ρ) = 1 + iA/ρ, generalizing the real Brill–Lindquist potential; complexifying the *Misner* image-charge series ψ = 1 + Σ aₙ(1/|r+dₙ| + 1/|r−dₙ|) yields data for two interacting mouths. Per Smirnov (arXiv:2312.09622), "the main focus is on initial data sets describing two interacting mouths of the same traversable wormhole. These data sets are similar in many respects to the Misner initial data with two black holes," and — importantly for your use — the paper's own conclusions note that "the formal proof of the regularity of data sets has not been given." Two caveats for you: (i) it is a punctured-R³ construction, so naive moving-puncture χ evolution reinherits puncture-interior issues; (ii) it is two mouths of *one* wormhole (an intra-universe "handle," topology S²×S¹ minus a point), not two independent wormholes. Generalizing to two distinct wormholes (four asymptotic ends) is not done in the paper and is non-trivial. Use it as the rigorous existence proof and as the natural target for a methods Letter (§7c).

**The wrong-sign Lichnerowicz problem, and why CTTK is your tool.** The standard York–Lichnerowicz method conformally rescales the source; for a phantom scalar the negative energy density flips the sign of the source in Δψ = −(source)ψ^p, and the maximum principle guaranteeing a unique positive ψ can fail. GRChombo/GRTresna's **CTTK** method is built for exactly this. Per Aurrekoetxea, Clough & Lim (CQG 40, 075003, 2023, arXiv:2207.03125): "instead of solving the Hamiltonian constraint as a 2nd order elliptic equation for a choice of mean curvature K, we solve an algebraic equation for K for a choice of conformal factor. By doing so, we evade the existence and uniqueness problem of solutions of the Hamiltonian constraint without using the usual conformal rescaling of the source terms." Removing the source rescaling is precisely the escape hatch for phantom matter. It is implemented in GRTresna (Aurrekoetxea, Brady, Aresté-Saló, Clough, Helfer, Lim et al., "GRTresna: An open-source code to solve the initial data constraints in numerical relativity," arXiv:2501.13046, 2025), "a multigrid solver … based on the formalism in arXiv:2207.03125," released at github.com/GRTLCollaboration/GRTresna, outputting a GRChombo/GRTeclyn-compatible checkpoint. **Caveat to check at runtime:** with two exotic lumps the algebraic equation for K² can go negative near the existence boundary — monitor for K²<0 nodes.

**Boson-star superposition fix (Helfer et al.; Ning et al.).** Plain superposition γ_ij = γ_ij^A + γ_ij^B − δ_ij spuriously alters the volume element at each center, mimicking a squeeze that triggers pulsation/collapse — worse for horizonless objects "due to the lack of a horizon and its potentially protective character." Per Helfer, Sperhake, Croft, Radia, Ge & Lim ("Malaise and remedy of binary boson-star initial data," CQG 39, 074001, 2022, arXiv:2108.11995), "evolutions starting from a plain superposition of individual boosted boson-star spacetimes are vulnerable to significant unphysical artefacts … we argue that this vulnerability is universal and present in other kinds of exotic compact systems and hence needs to be addressed." The fix (their Eq. 45): γ_ij = γ_ij^A + γ_ij^B − γ_ij^B(x_A) — subtract the companion's value at *this* star's center rather than the flat metric. Ning et al. (arXiv:2604.15240) extend this to a "one-body conformal-factor correction" for BS–BH binaries and find it "substantially suppresses these artifacts." **Directly transferable to two regular throats once the puncture is removed:** superpose the two proper-radial-chart metrics and subtract the companion's conformal-factor contribution at each throat. Exact only for equal masses; use the weighted-subtraction generalization (Croft et al.) for unequal masses. This cures the near-throat constraint defect.

### 5. Gauge and evolution variables

**Lapse.** The massless Ellis throat is ultrastatic (α=1 is the exact static lapse), and a flat α(t=0)=1 is required to keep Π=0 for the phantom field, since ∂_tΠ ∝ ∇α·∇φ (2604.00071). But 1+log slicing ∂_tα = −2α(K−K₀) keeps α=1 as long as K=0, so α=1 initial data is fully compatible with 1+log — the lapse only moves once the throat dynamically evolves (K≠0), which is what you want. **Recommendation: α(t=0)=1, 1+log slicing, Gamma-driver shift from β=0** — the combination used in essentially all boson-star runs and in the single-throat wormhole paper. Do **not** use a pre-collapsed α=χ or a "type-4 collar": a spatially varying α near χ→0 induces immediate slicing shear, and with χ in the denominator it detonates. Your collar that "relaxes and detonates by t~2.4" is almost certainly a *symptom of the puncture coordinate* and should vanish in a regular chart. If a residual gauge instability persists after the coordinate fix, treat it as an independent problem with Kreiss–Oliger dissipation and Gamma-driver η tuning.

**The χ-in-the-denominator problem.** CCZ4 divides by χ and α; χ→0 at a compactified origin NaNs. The single-throat paper's χ_min=10⁻⁸ floor is exactly what seeded the noise that destroyed its equilibrium. In a regular chart χ~O(1) at the throat, so the denominator problem does not arise there. It *can* arise if a horizon forms during collapse (χ→0 physically) — there the moving-puncture machinery is designed to cope, and setting covariantZ4=0 avoided extreme stiffness as α→0 in 2604.00071. Adopt that. Keep CCZ4 constraint damping (κ₁~0.1–3, κ₂=0) and the Θ-field on so the scalar (spin-0) constraint residual is damped independently and does not contaminate Ψ₄.

### 6. Making the merger gravitationally bound

Two massless Ellis throats (M_ADM=0) do not attract. Add positive ADM mass *without* re-introducing a puncture:

- **Massive Bronnikov/drainhole branch (recommended — scalar only).** ds² = −e^{2u(l)}dt² + e^{−2u(l)}[dl²+(l²+a²)dΩ²], u(l) = (m/a)(arctan(l/a) − π/2). Asymptotics e^{2u} → 1−2m/l (l→+∞) give ADM mass m on the "+" side; the throat stays regular because e^{−2u} is finite and O(1) there (e^{πm/a} at l=0). In the isotropic-massive form the ADM mass is M = mγ with the field-equation constraint 2δ² = 1+γ² (γ=0 recovers the massless symmetric wormhole). The two ends carry *opposite-sign* masses (m_+ = +bγ₁e^{−γ₁π/2}, m_− = −bγ₁e^{+γ₁π/2}); the far universe is repulsive — fine if you have truncated/excised it. Use two positive-mass "+" ends so the pair attracts. This keeps the gravity+scalar sector you already have.
- **Lanzhou regular ansatz (Su, Hao, Fang & Wang).** ds² = −e^{B}dt² + Ce^{−B}[dr²+(r²+r₀²)dΩ²], r∈(−∞,∞), compactified via r = tan(πx/2), x∈(−1,1), ADM mass from g_tt = −1+2M/r+…. Per Su, Hao, Fang & Wang ("Generalized Bronnikov–Ellis wormhole with nonlinear electromagnetic field," Eur. Phys. J. C 85, 1040, 2025, arXiv:2407.09591), the solution "violates the Null Energy Condition (NEC), and as the parameters change, the ADM mass of the entire spacetime changes from positive to negative": a "type 0" branch with constant positive ADM mass and "type I"/"type II" branches reaching negative ADM mass (e.g. M<0 for throat radius r₀<0.153). Advantage: mass symmetric on both sides (positive both ends). Cost: introduces a Hayward nonlinear-EM sector — new matter physics in your code.
- **Simplest pragmatic choice:** massive drainhole branch (scalar only), truncate the negative-mass far side, let the two positive-mass "+" ends attract.

### 7. Fallback strategies, ranked for a one-month first paper

**(d) Axisymmetric (2+1) two-throat head-on — BEST risk/reward.** Cuts cost by ~two orders of magnitude, still a genuine first *dynamical two-throat* result, still extracts ℓ=2 Ψ₄ (head-on is axisymmetric). χ~O(1) in the proper-radial chart, two centers on the symmetry axis in one asymptotically flat domain. Run effectively-2D via the modified-cartoon method in GRChombo/GRTeclyn or a dedicated 2+1 code. Failure modes: the timelike-inner-boundary problem for the far universes remains (mitigate by truncation); axisymmetry forbids the spiralling phase (head-on only).

**(e) Two boson-star-style exotic lumps (no throat topology) — MOST ROBUST, honest reframing.** Represent each object as a horizonless NEC-violating lump (phantom/ghost or solitonic scalar configuration) with fully regular, constraint-satisfying data — χ~O(1) everywhere, no second universe, no excision, no puncture. This is the mature 3D Cartesian program (Palenzuela et al.; Helfer et al.; Ge et al. 2410.23839; Bezares et al.; in GRChombo/BAM/SpEC) and gives inspiral + merger + Ψ₄ directly. **What is lost:** the actual wormhole *topology* and the literal "first wormhole merger" claim — you'd be simulating "the merger of two exotic negative-energy compact objects," scientifically honest and novel if the matter model genuinely violates the NEC, but not a topological wormhole. Recommend as the guaranteed-deliverable backbone with the topological version as the stretch goal.

**(c) Publish the two-throat REGULAR initial-data construction + short evolution as a methods Letter.** Build constraint-satisfying two-throat data (Smirnov-style complexified potential, or superposition + CTTK + Helfer correction), demonstrate χ~O(1) at both throats and Noether-charge conservation over a short stable evolution, and present the machinery. Initial-data papers are a recognized genre; this de-risks the full inspiral for a follow-up. Lower novelty ceiling, very high completion probability.

**(a) Thin-shell / Visser wormhole.** Cut-and-paste at r=a with a surface layer (Darmois–Israel). Each glued copy is regular, so it avoids χ→0 in that sense, but it introduces a **distributional** (delta-function) stress-energy at the junction, hard to represent in finite-difference CCZ4 and, to my knowledge, **never evolved in 3D Cartesian NR** — all thin-shell "dynamics" in the literature is the 1D Israel-junction ODE ä = f(a) (Poisson–Visser and successors), not a field evolution. **Not recommended for 3D in a month.**

**(b) Rounded/regularized throat with a χ floor by construction.** Give χ a small positive floor by construction, not a numerical clamp. This is option (e) in disguise once χ_min is O(1); push it toward the true throat value and you re-inherit the resolution problem. Useful as a *continuation parameter* (dial χ_min from O(1) toward the throat value to study convergence), not as an endpoint.

## Recommendations

**Stage 0 (days 1–3): kill the coordinate bug.** Re-derive the single throat in the proper-radial chart ds² = −e^{2u}dt² + e^{−2u}[dl²+(l²+a²)dΩ²]; verify in-code that χ = e^{2u} is O(1) at l=0 (≈1 massless, e^{πm/a} massive) and that R_min survives on max_level 1 and 2. **Proceed-benchmark:** χ_throat within a small factor of 1, R_min preserved to <1% under refinement, before the first timestep.

**Stage 1 (days 3–10): single regular throat, static hold + Noether charge.** Evolve one massless throat, α=1, 1+log, Gamma-driver, covariantZ4=0, Kreiss–Oliger σ≈1–2, far universe truncated at large |l| with Sommerfeld BCs. **Benchmark (your exit condition):** complex-scalar Noether charge conserved to a few percent over t≳20–30M, no gauge detonation. If the collar death recurs even in the regular chart, it is an independent gauge issue — retune Gamma-driver η, add dissipation.

**Stage 2 (days 8–18): constraint-satisfying data via GRTresna/CTTK.** Solve the single-throat constraints with CTTK (algebraic-K, no source rescaling); watch for K²<0 nodes. Then superpose two throats with the Helfer/Ning conformal-factor correction and re-solve. **Benchmark:** Hamiltonian and momentum L₂ norms converging at ≥2nd order; χ~O(1) at *both* throats.

**Stage 3 (days 15–25): the run.** Add ADM mass via the massive drainhole branch (M = mγ). Do the **head-on** first (axisymmetric, cheapest, ℓ=2 Ψ₄). Extract Ψ₄ at multiple radii; apply the v≈c propagation test (2604.00071 Eq. 19) to separate physical radiation from superluminal CCZ4 constraint modes. **Inspiral-benchmark:** clean head-on with χ~O(1) through merger and a coherent outgoing Ψ₄ wavefront.

**Stage 4 (days 25–30): write.** If Stages 1–3 hold, publish the two-throat head-on with Ψ₄. If Stage 2 or 3 stalls, pivot to the methods Letter (fallback c) at whatever stage you reached, or to the exotic-lump head-on (fallback e), which is essentially guaranteed.

**Decision thresholds that change the plan:**
- Regular-chart single throat still loses Noether charge >few% → the instability is *physical* (Ellis throats have exactly one unstable mode; GGS 0806.0608), not numerical. Reframe as "collapse/expansion of a two-throat system," lean on the short-evolution Letter.
- CTTK returns K²<0 with two exotic lumps → past the existence boundary; reduce ADM mass / increase separation / reduce phantom support until a real K solution exists, and report the boundary as a finding.
- Timelike inner boundary (excision) unstable → abandon true topology for this paper; use truncated-far-universe or the exotic-lump reframing.

## Caveats

- **arXiv:2604.00071 is a preprint by an independent researcher whose central geometric choice is the very bug you diagnosed.** Treat its methods (compactified second universe, χ_min floor) as what to avoid; its numerical settings are reasonable to reuse. Its physics claims (phantom bounce, "effectively infinite damping time τ~5×10⁶M" QNM) are explicitly flagged *in the paper itself* as grid-contamination artifacts, not physical results.
- **No one has demonstrated a stable horizonless-throat excision (timelike inner boundary) in 3D Cartesian CCZ4.** The turduckening/excision guarantees require a horizon and a specific BSSN parameter range; they do not transfer to a traversable throat. This is the single biggest research risk in the "true topology" route.
- **Ellis–Bronnikov throats are linearly unstable** (exactly one exponentially growing mode, timescale ~throat/c; GGS 0806.0608/0806.1370, Shinkai–Hayward gr-qc/0205041). A "long-lived bound inspiral" of two of them may be physically impossible on the orbital timescale — they may collapse to BHs or inflate before completing an orbit. This may be a *feature*: a merger-and-collapse with a distinctive burst signal. Frame the science accordingly.
- **Smirnov's construction is two mouths of ONE wormhole**, and the paper states "the formal proof of the regularity of data sets has not been given"; generalizing to four asymptotic ends (two distinct wormholes) is unproven.
- **The Lanzhou massive solution requires a nonlinear-EM matter sector** — new gravity-sector-adjacent physics with its own well-posedness burden. The scalar-only massive drainhole branch avoids this.
- The isotropic-massive coefficients (e.g. M = mγ, 2δ² = 1+γ²) are quoted from a secondary accretion-paper's presentation of the standard Ellis/Bronnikov solution and are cross-checked against GGS and Kain; verify the exact coefficients against Bronnikov's original (Acta Phys. Polon. B 4, 251, 1973) before publication.