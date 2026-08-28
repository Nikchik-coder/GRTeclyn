# Matter Debug — why no matter model can currently be tested on this throat

> **Status 2026-08-28: BLOCKING.** The merger execution plan
> ([Plan.md](Plan.md)) is halted at Phase 3 until the issue on this page is fixed.
> Everything here was split out of the Plan on 2026-08-28 so that the Plan stays a plan
> and this stays a debug log. All runs from this investigation are **stopped**.

## The one-paragraph version

We set out to test whether a Q-ball-type charged phantom scalar
(`ComplexExoticScalarField` + complex sextic potential) gives a wormhole throat a
preferred size, and so removes the Ellis–Bronnikov runaway that costs Phase 3 its margin.
**The test ran and it does not answer that question.** The matter itself is clean; the
*geometry it was placed in* cannot be resolved. The throat is a Bowen–York puncture, and
at the grid this project can afford, a single cell at the puncture is **wider in proper
distance than the whole throat**. On top of that, mesh refinement — which a puncture needs
— provably erases the throat before the first timestep. Until the throat is replaced by a
**regular, finite-χ** one, no matter model can be evaluated here, this one included.

## The blocker, stated as a contradiction

1. A puncture throat **requires** mesh refinement to resolve χ → 0.
2. Refining below the gridinit's own dx **destroys** the throat (measured, below).
3. So the initial data must already be fine enough everywhere — which costs N ≈ 1600
   uniform, a ~7 TB gridinit.

There is no setting of the existing knobs that satisfies all three.

**Exit condition for the block:** a throat whose χ stays of order 1 at the minimal
surface, so that proper cell width ≈ dx there, and on which the Noether charge holds to a
few per cent over the run. That is mitigation row 8 below.

## What is stopped, and where the evidence is

| Run directory (under `runs/`) | What it is |
| --- | --- |
| `rotating_wormhole/evo_..._ml2_..._qbtest_thr1` | `bh1_bare_mass` = 1, `max_level` 2 |
| `rotating_wormhole/evo_..._ml2_..._qbtest_thr2` | `bh1_bare_mass` = 2, `max_level` 2 |
| `rotating_wormhole/evo_..._ml1_..._qbtest_thr2_ml1` | `bh1_bare_mass` = 2, `max_level` 1 |
| `rotating_wormhole/evo_..._ml0_..._qbtest_thr2_ml0` | `bh1_bare_mass` = 2, **unigrid** — the only valid throat measurement |
| `rotating_wormhole_id/rotwh_..._thr1_cz32`, `..._thr2_cz32` | the two GRTresna solves behind them |

Diagnostics are in `<run>/output/data/collapse_diagnostics.dat`; frames in
`<run>/output/frames` (216 each). The `THROAT_MASS` = 4 solve was **deleted** — it stalled
and falsely reported convergence (see below).

---

## Matter available in-tree — the constraint is EB's, not the project's

The throat expansion that Phase 2 of [Plan.md](Plan.md) measured is a property of the
**massless real phantom scalar** with a zero potential, which is what
`ExoticScalarField` + `DefaultPotential` gives and what `BinaryWormholeMerger`
currently uses. It is a saddle because it has no preferred
size: nothing pulls the throat back. That is not a property of wormholes in general,
and `Source/Matter` already carries the alternatives.

| Model | Kind | Already used by |
| --- | --- | --- |
| `ExoticScalarField` | real, phantom | **`BinaryWormholeMerger` today**, `SupportedWormholeCollapse` |
| `ComplexExoticScalarField` | complex, phantom, templated potential, conserved U(1) charge | `RotatingWormholeCollapse` |
| `BiComplexScalarField` | canonical **and** phantom complex pair | `RadialRecipe` (Bondi campaign) |
| `EffectiveTeoMatter` | prescribed rotating-wormhole stress-energy | `RotatingWormholeCollapse` |
| `ComplexScalarField`, `ScalarField`, `DustMatter`, `NoMatter` | canonical / vacuum | — |

Potentials: `DefaultPotential` (zero — **what EB uses**), `PhantomDecayPotential`
(½m²φ²), `OscillonPotential` (real sextic, self-described as metastable),
`ComplexScalarPotential` (**complex sextic on |Φ|², a true Q-ball**),
`GRTresnaScalarPotential` (solver side).

**The Q-ball claim in earlier drafts of this section was wrong. 2026-08-28, on inspection
of the run's own diagnostics.** The run cited as proof,
`runs/rotating_wormhole/evo_omega_p0p00_m0_kappa_1p00_dx0p5_ml2_..._qball_lam170_mu614450_..._proven`,
does not do what it was said to do:

| | claimed here | what `collapse_diagnostics.dat` says |
| --- | --- | --- |
| usable window | ~11 | lapse collapses 1.0 → 0.31 by t = 3.5; NaN at t = 12.34 |
| horizon | none | outgoing-ray expansion θ₊ ≤ 0 from t = 2.25 at r = 0.43 |
| matter | held | `rho_sum` 23.6 → 9.4 by t = 7 — **42 % kept** |
| what the run is | a stability test | a **collapse** test: `support_ramp` cuts the exotic support to zero over t = 8–10 |

The constraint norms are healthy throughout (Ham 3.6e-3 → 1.5e-2, Mom 2.9e-5 → 2.4e-2), so
none of that is numerical junk — the configuration really does shed most of its matter and
really does die. Note also that θ₊ ≤ 0 near a puncture is not by itself a dynamical
horizon: an Einstein–Rosen bridge has a minimal surface at t = 0 by construction. The
matter loss and the lapse collapse are the load-bearing numbers, not the θ₊ flag.

**What the cause is not.** A first pass at this blamed the internal frequency: the run is
tagged `omega_p0p00`, and with ω = 0 there would be no Noether charge and so no preferred
size. That is wrong — the tag records the solver's *target* frequency while the initial
data carries the *solved* eigenfrequency, and the run's charge is Q = −3.30, conserved to
4.7 % over t = 0 → 8. It is charged. Recorded here because the tag will mislead the next
reader the same way.

**What distinguishes it from the runs that behave, then, is still open.** Over the same
pre-ramp window t = 0 → 8:

| t = 0 → 8 | the "proven" run (m = 0) | ω = 0.25 m = 1, L = 128 N = 256 | ω = 0.25 m = 1, L = 64 ml = 3 |
| --- | --- | --- | --- |
| charge drift | **−4.7 %** | −0.5 % | −0.1 % |
| `rho_sum` | 23.6 → 10.0 (**42 % kept**) | 13.3 → 29.6 (223 %) | 13.3 → 31.6 (238 %) |
| `min_chi` | 0.091 → 0.194 | 0.086 → 0.117 | 0.084 → 0.117 |
| J_z | 0 | −1.47 → −1.30 | −1.47 → −1.29 |

The two well-behaved runs are at different box sizes and different refinement depths and
agree with each other to 7 %, so their behaviour is a property of the configuration, not of
the grid. They also both **spin**, and they both cut their support at t = 8, so neither is
the run the merger needs.

The best available hypothesis for the m = 0 run's matter loss is that **its matter was
never a stationary solution**. It was painted from the 2D Q-torus solver at m_az = 0, and
that solver imposes axis regularity as f(0, z) = 0 — correct for a winding torus, wrong for
a spherical lump, which should have zero *derivative* on the axis instead. It now refuses
m_az < 1 outright for exactly this reason. A hollow, non-stationary lump disperses. This is
a hypothesis and not a measurement: that initial data no longer exists on disk. The runs
under test avoid the question by taking their profile from the 1D spherical Q-ball radial
ODE solver, which has the right boundary condition.

### The throat is not in the initial data

Measured directly from a freshly solved gridinit (ω = 0.25, m = 0, `bh1_bare_mass` = 0.25,
the base-file value, at the L = 64 / N = 128 grid every run in this family uses):

```
   r      chi      R = r/sqrt(chi)
 0.250   0.3841        0.403
 0.750   0.6092        0.961
 1.250   0.7440        1.449
 1.750   0.8233        1.929      ... monotonic all the way out
```

**R has no interior minimum.** There is no throat in this initial data — only a mild
central dip in a nearly flat space. The reason is arithmetic, and it applies to the whole
family:

- the solver builds the throat as a Bowen–York puncture, ψ = 1 + m/(2r), whose areal
  radius R = ψ²r bottoms out at **isotropic r = m/2** with **R_min = 2m**;
- the solved data is flattened to the evolution's level-0 dx before it is evolved
  (lesson L2), so anything below one cell is simply **absent from the initial data**, and
  no amount of AMR during the evolution puts it back;
- at `bh1_bare_mass` = 0.25 the throat sits at r = 0.125 = **a quarter of one cell** at
  dx = 0.5.

So the resolution rule is **m/2 ≥ 2 dx**, i.e. **m ≥ 4 dx**, giving an areal throat radius
R = 2m ≥ 8 dx. At L = 64 / N = 128 that is m ≥ 2 and R ≥ 4. The `_proven` run's m = 1 puts
the throat on the single innermost cell — present, but on the edge of meaning anything.

> **Superseded 2026-08-28.** This rule is necessary but nowhere near sufficient: it is
> stated in coordinate distance, and what the evolution resolves is *proper* distance
> dx/√χ, which blows up at a puncture. Measured below, m = 2 satisfies this rule and the
> throat is still only ~1 cell wide in proper distance.

The matter side of that same solve is correct and worth recording as the positive result:
the painted amplitude φ(0) = 0.0997 matches the independently solved flat-space Q-ball
eigenstate (0.0991), and Π₂ = −ωφ holds to every printed digit, so the charge really is
there. The Hamiltonian residual converges 100 % → 0.77 % and the momentum residual is
identically zero, as it must be for a non-rotating, unboosted configuration.

**What this costs the merger geometry.** Three constraints now have to hold at once:
a resolved throat (b ≥ 8 dx in areal radius), isolation (d ≥ 8 b as Phase 1 requires), and
a boundary far enough away (d ≲ L/3). Together they force **N ≥ 96**, and at L = 64 /
N = 128 they leave d ∈ [16, 21] with m = 2. Free-fall over that separation is
t_ff ≈ 50 rather than 8.89. That is a much longer run than Phase 3 was scoped for — though
not an impossible one: the archived charged runs already reach t = 40 and t = 80. This is
now the binding design constraint, and it is a *resolution* constraint, not a matter one.

> **Tested 2026-08-28 — the test ran, and it does not answer the question.** The missing
> cell was run: charged (ω = 0.25), non-rotating (m = 0), support held on, full box with
> the throat centred, `bh1_bare_mass` raised to 1 and 2, out to t = 14, at three
> refinement depths. Two default-off additions made it runnable: `EVO_CZ` in
> `solve_kappa_family.py` (the ID solver could only place matter on a symmetry corner)
> and `--areal-radius` in `wormhole_case.py` (the throat readout was never wired into
> this campaign). `THROAT_MASS` overrides the puncture mass. What came back is below.

### Refinement below the gridinit's own dx destroys the throat

The first result is a pipeline bug, not physics, and it invalidates every AMR run in this
family as a throat measurement.

The gridinit is ingested **exactly** — chi on the evolution's level 0 matches the file
cell for cell to the last digit, verified for both `bh1_bare_mass` = 1 and 2. At m = 2
that file contains a genuine throat: an interior minimum of R at r = 1.299, R = 4.507
(analytic: r = 1.0, R = 4.0). At m = 1 there is none — the throat sits below one cell,
exactly as the rule above predicts.

But the *evolved* data at max_level 1 or 2 has **no interior minimum at any time,
including t = 0**. Prolongation fills the puncture interior with a nearly constant
chi ≈ 0.0064, so R rises linearly from the centre and the minimum is gone before the
first step. Lesson L2 is usually read as "do not evolve finer than the ID's native dx or
you lose accuracy". The sharper statement is: refining below the ID's dx does not fail to
add detail, it **invents smooth wrong detail**, and here that detail is the absence of a
wormhole. Only `max_level = 0` preserves the throat.

| max_level | throat in the ID file | throat at t = 0 in the evolution |
| --- | --- | --- |
| 0 | yes (r = 1.299, R = 4.507) | **yes**, R = 4.507 |
| 1 | yes | **no** — monotonic |
| 2 | yes | **no** — monotonic |

### At unigrid the throat is real, and it closes

| t | 0 | 2 | 4 | 6 | 14 |
| --- | --- | --- | --- | --- | --- |
| throat radius R | 4.51 | 4.43 | 4.00 | **gone** | gone |

By t = 6 R is monotonic; by t = 14 the lapse is 0.28 and the trapped region has grown to
r = 11.7. The Q-ball matter did not hold the throat open. All three refinement depths end
in the same state (lapse ≈ 0.3, Q ≈ −2.1, trapped region ≈ 11.8), so the collapse itself
is robust to the grid — refinement changed only whether the throat was visible at t = 0.

### Why that number cannot be believed either: the charge is not conserved

| | t = 0 | t = 14 |
| --- | --- | --- |
| Noether charge Q | −10.52 | −2.09 (**−80 %**) |
| charge inside the extraction sphere | −10.52 | tracks Q_total to 3 digits until t ≥ 12 |
| net flux through the outer boundary | — | ~1e-11, i.e. nothing |

Nothing leaves the box, so the charge is being destroyed *in the interior*, and it decays
fastest over exactly the interval in which the throat closes (t = 1 → 6). The field
amplitude meanwhile barely moves (max φ 0.0997 → 0.075). A conserved quantity losing 80 %
while its own field stands still is a numerical statement, not a physical one — and the
matter whose conservation law was supposed to hold the throat open is the thing
dissolving. This is [check matter before believing geometry] applied to the charge rather
than the density.

### The binding number: one cell is wider than the throat

The coordinate-resolution rule stated above (m ≥ 4 dx) is **not sufficient**, and the
reason is that it is stated in the wrong distance. What the evolution resolves is proper
distance, dx/√chi, and near a puncture chi → 0. Measured on the m = 2 gridinit that
*does* contain a throat:

```
   r      chi     R_areal   proper cell width dx/sqrt(chi)
 0.433  0.00644    5.396          6.231
 0.829  0.03297    4.567          2.754
 1.299  0.08309    4.507          1.735   <- the throat
 1.785  0.14430    4.700          1.316
 2.278  0.20828    4.991          1.096
```

The throat's areal radius is 4.5. The innermost cell is **6.2 proper units wide — wider
than the throat it is meant to resolve**, and the whole throat region spans ~13 proper
units in 5 cells. The throat is resolved by of order *one* cell. Neither the closure time
nor the charge loss survives that.

Getting proper cell width down to ~0.5 at the puncture needs dx ≈ 0.04, i.e. **N ≈ 1600**
uniform — the gridinit alone would be ~7 TB. This is not a grid that can be bought.

**Raising the puncture mass is not the way out either.** `bh1_bare_mass` = 4 was tried:
the GRTresna nonlinear solve **stalls** — Ham residual 100 % → 99.08 % in one iteration
with max|δψ| = 0.005, versus a clean 100 % → 0.48 % at m = 2. It exits early reporting
"Converged" and writes an `InitialDataFinal` that does not solve the constraints. Anything
built on it would be garbage; the solve was deleted.

### What this means for option 1

The Q-ball matter model is **not the thing that failed, and it has still not been tested.**
Its own numbers are clean: the painted amplitude matches the independently solved
flat-space eigenstate, Π₂ = −ωφ holds to every digit, the Hamiltonian residual converges
to 0.48 %, and the momentum residual is identically zero. What failed is the *geometry it
was placed in*: a Bowen–York puncture throat cannot be resolved in proper distance on a
uniform gridinit, and the uniform gridinit is forced by L2 because AMR cannot be allowed
to touch it.

That is a contradiction in the pipeline, not a physics result:

- a puncture throat **requires** mesh refinement to resolve chi → 0;
- refinement below the gridinit's dx **destroys** the throat (measured above);
- so the ID must already be fine enough everywhere, which costs N ≈ 1600.

The way out is to stop using a singular throat. A **regular** Ellis–Bronnikov throat keeps
chi of order 1 at the throat, so proper cell width ≈ dx and the resolution problem
disappears. Until the throat geometry is regular, no matter model can be evaluated on it —
including this one.

One correction to earlier drafts survives all of this and is worth keeping: the constraint
solver is **not** something to be built. `RotatingWormholeCollapse` already drives a
GRTresna solve for exotic complex-scalar throats through a CLI pipeline, and it produces
data with *zero* initial constraint defect — precisely the 1.4e-2 seed that drives the EB
runaway. Changing matter is not a research programme here; it is selecting a model that is
already implemented and already solved for. What is *not* yet established is that any
member of this family is a traversable throat at all.

## Mitigation — ranked, with what each actually buys

| # | Approach | What it buys | Verdict |
| --- | --- | --- | --- |
| 1 | **`ComplexExoticScalarField` + Q-ball sextic, on GRTresna-solved data** | charge conservation gives the matter a preferred size, which the massless EB phantom has no analogue of | **Blocked, not refuted.** Ran 2026-08-28: the matter solves clean, but on a puncture throat it cannot be evaluated — the throat is ~1 cell wide in proper distance and 80 % of the charge dissolves. Needs a regular throat first (row 8) |
| 2 | Sharpen the throat readout (sub-grid minimum + per-step output) | makes λ measurable, closes the Phase 2 tick | Do regardless; cheap, no new physics, no new runs to design it |
| 3 | Same as 1 but rotating (ω ≠ 0) | a *natural* ℓ = 2 quadrupole with no artificial perturbation | Hold for Phase 4 — spin makes the head-on a different problem |
| 4 | Keep EB, use solved data to reach d/b ≈ 3 | t_ff = 2.04 against a window of 2 | Works, but marginal by construction, and fights the instability rather than removing it |
| 5 | Accept that both throats destabilise and study *that* | the bifurcation this document already predicts | Legitimate science, but a different paper — decide deliberately, not by discovering it late |
| 6 | Reduce the t = 0 seed by other means | ~0.25 of window per decade | Nowhere near sufficient alone |
| 7 | Refine the grid | nothing — measured, not assumed | Ruled out |
| 8 | **Replace the singular puncture throat with a regular (finite-χ) Ellis–Bronnikov throat** | proper cell width ≈ dx at the throat instead of 6× the throat radius; makes every other row testable | **Now the prerequisite for all of them.** Nothing above can be measured until this is done |

**Recommended reading of this:** do 2 now. Do **8 before anything else in this table** —
as of 2026-08-28 no matter model can be evaluated on a puncture throat at any grid this
project can afford, so rows 1, 3 and 4 are all blocked behind it, and Phase 3 cannot be
committed to any of them. The open work after that is still a **two-centre solve**, which
has not been done. The resolution bill is now quantified and it is not payable in
coordinate resolution: at dx = 0.5 one cell at the puncture is 6.2 proper units, against a
throat of areal radius 4.5.


## Standing risks owned by this document

Moved out of the Plan on 2026-08-28. These are all one fault seen from four sides; the
first three are the block, the fourth is its diagnostic, the fifth is the tooling that
made it visible.

| Risk | Why it bites | Mitigation |
| --- | --- | --- |
| **Solved initial data contains no throat** | the throat is a Bowen–York puncture, ψ = 1 + m/(2r), whose minimal surface sits at isotropic r = m/2; the `.gridinit` bridge flattens the solve to the evolution's level-0 dx, so a throat below one cell is absent from the data and AMR cannot put it back. At the family's standard `bh1_bare_mass` = 0.25 and dx = 0.5 the throat is at r = 0.125 — **a quarter of a cell**. Measured: R = r/√chi rises monotonically from the first cell out, no interior minimum | `THROAT_MASS` now overrides the puncture mass, and at m ≥ 4 dx the throat does appear in the file (m = 2, dx = 0.5: interior minimum at r = 1.299, R = 4.507). **But that is not enough, and the coordinate rule is superseded** — see the next two rows. **The binding constraint on Phase 3 is resolution, not matter** |
| **Refining below the gridinit's dx destroys the throat** | prolongation cannot recover sub-cell structure, so it fills the puncture interior with a nearly constant χ ≈ 0.0064; R then rises linearly from the centre and the interior minimum is gone **before the first step**. Measured 2026-08-28 on identical data: `max_level` 0 keeps the throat at t = 0, `max_level` 1 and 2 both lose it. Level-0 ingestion itself is byte-exact, so the file is not the problem | run throat diagnostics at **`max_level = 0` only**, or teach the evolution to set χ analytically at the puncture instead of interpolating. Every AMR run in this family is void as a throat measurement |
| **A puncture throat cannot be resolved in proper distance** | the evolution resolves dx/√χ, and χ → 0 at a puncture. On the m = 2 gridinit — which satisfies m ≥ 4 dx and does contain a throat of areal radius 4.5 — the innermost cell is **6.2 proper units wide**, wider than the throat itself, and the whole throat region spans ~13 proper units in 5 cells. Reaching ~0.5 proper units needs dx ≈ 0.04, i.e. N ≈ 1600 uniform (~7 TB of gridinit). Raising the mass instead does not work: at m = 4 the GRTresna solve stalls at 99.08 % Ham residual and falsely reports convergence | **use a regular, finite-χ throat**, where proper cell width ≈ dx. Until then no matter model can be evaluated on this geometry, this one included |
| **The Noether charge is not conserved on this geometry** | Q falls −10.52 → −2.09 (**−80 %**) by t = 14 while the field amplitude barely moves and the boundary flux is ~1e-11 — so it is destroyed in the interior, fastest over exactly the interval in which the throat closes. The quantity whose conservation was supposed to give the matter a preferred size is the quantity dissolving | a consequence of the row above, not an independent fault. **Treat charge conservation as a resolution diagnostic**: until Q holds to a few per cent, no collapse or survival time from this family means anything |
| Throat readout lands on the innermost cell | R = r/√chi *diverges* at the compactified origin, but the unresolved inner cells report it as small, so a bare argmin tracks a "collapse" that is not happening — 0.152 instead of 0.498 on a b = 0.5 throat | `--areal-min-radius` excludes an inner ball. **Archived `areal_radius.dat` columns predating this are unreliable** — several older runs report exactly dx/2, i.e. pure grid artefact |
