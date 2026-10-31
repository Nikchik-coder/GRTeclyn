Campaign M — matter architectures for rotating wormholes

# Minimal exotic wormhole search

The AI designs the matter recipe — layered fields, sculpted potentials, spin — that holds a wormhole open with the least exotic matter. Every recipe that balances Einstein's equations is a new metric; the cluster then evolves it.

Everything known about rotating wormholes uses the simplest possible recipe: one massless exotic field, spread evenly, nothing else. Each restriction is a door. Spin alone already cut the exotic bill a hundredfold in the computed families [Spin26], and the dressed phantom star showed that layering with a sculpted potential survives nonlinear evolution [Bondi26]. This campaign opened those doors at fixed throat size and spin so the optimizer cannot cheat toward a black hole.

## Scope now (2026-10-29)

The 2D search is closed. Remaining work is **3+1 GRTeclyn evolutions** of the already-cleared bare-field tables (D51 X = 1.606 first). Dropped from this plan, not to be implemented: the rotating 2D stability eigenproblem, further 2D-solver development, and every extra matter recipe still open below (normal-matter layers, winding, equatorial focusing, onions, counter-rotating layers, exotic-free corridor, double throat, charge). Historical records of what already ran stay; nothing from those dropped knobs is queued. Every evolution waits for the go.

Posed in full, the search is a constrained optimization: minimize the exotic bill over exact solutions at fixed throat size and spin, under the traversability bounds Morris and Thorne wrote down as prose [MT88]. Its product grows from a curve into a design chart: what a wormhole of a given throat size, tidal tolerance and transit time costs in exotic matter, every cell a solved metric.

## Prior art and what is new

The objective is classic; the method and the regime are not. This is the map of what exists, which the paper must cite and position against. Keys in brackets point to [Sources](#sources) at the end.

**What the literature has done**

- **The "arbitrarily small" result.** Visser, Kar and Dadhich introduced the volume-integral quantifier, the ancestor of the published Fig. 3e [Spin26], and showed that the total violation can be made arbitrarily small by deforming toward thin shells [VKD03]. Fewster and Roman's quantum-inequality analysis then confined those models to submicroscopic throats or a large mismatch between throat size and curvature radius [FR05]. Related constructions: energy conditions, traversable wormholes and dust shells [Lob04].
- **The Kuhfittig line:** viable wormholes supported by small amounts of exotic matter, with hand-chosen shape functions squeezing the exotic region thin [Kuh08]. Analytic ansatz tuning, one or two parameters.
- **Thin-shell wormholes:** Visser's cut-and-paste [V89a] plus a large stability literature (e.g. plane-symmetric thin-shell wormholes [LL08]): exotic matter as a delta-function shell, stability as linearized radial perturbations under an assumed equation of state [PV95].
- **Modified-gravity ansatz papers** (f(R, L_m) [fRLm23], f(Q) [fQ21], f(Q, T) [fQT24], reviews [Lob12, Rev24]): pick a shape function, check which energy conditions survive. Geometry-first; the matter is never a field theory.
- **Recent ML entries** are adjacent but different: neural networks as ODE solvers, or the inverse reconstruction of a wormhole candidate in f(R) [Inv26]. No exoticity optimization, no dynamics.

**What none of them do, as far as we know: five differentiators**

1. **Smooth field-theoretic matter.** Thin shells are junction conditions, not fields: nothing can evolve them, and they are precisely the idealization that this campaign's resolvability cap (Trap 1) and the quantum-inequality accounting (campaign F) exclude. The literature's known answer, "make it a thin shell", is the degenerate boundary of this search space, not its interior. The real question, the smooth finite-thickness optimum, is untouched.
2. **Rotation.** The minimization literature is essentially all static and spherical. Nobody has minimized exotic matter over rotating solutions, even though the spinning families show spin to be the single biggest known lever (100×) [Spin26].
3. **Automated, high-dimensional search.** Existing "optimization" is one or two parameters tuned by hand in an ansatz. Ten coupled knobs (potential, layers, winding, focusing, shape at pinned area) are a different regime, reachable only by the machine.
4. **Stability in the objective.** Thin-shell stability is linearized and radial, under an assumed equation of state. A bill-vs-stability Pareto frontier with growth rates from the actual field theory exists nowhere.
5. **Nonlinear 3+1 verdicts.** No paper in this literature has evolved its optimized wormhole, because none of their objects can be evolved. Every winner of this search can be, and gets the certificate.

So the prior art strengthens the claim rather than threatening it. "How little exotic matter can a wormhole need?" has a twenty-year pedigree, which makes it a recognized open problem, and every previous answer either degenerates (thin shells), ignores spin, ignores stability, or ignores dynamics. The novelty sentence writes itself: *the first automated optimization of exotic matter over exact, rotating, field-theoretic wormhole solutions, with stability in the loop and nonlinear evolution as the judge.*

### Against Warp Factory

Warp Factory [WF24a, WF24b] evaluates T = G/8π for hand-specified warp metrics, and its optimizer perturbs a starting metric to shrink the energy-condition violations. But its outputs are not solutions of any matter theory, and it has no dynamics: nothing in it can say whether an optimized metric survives a millisecond. This campaign is the wormhole version with the two missing pieces installed: the optimizer moves only through exact field-theoretic solutions, and the cluster delivers the nonlinear verdict Warp Factory structurally cannot.

The one thing worth taking from it, the observer-sampled energy-condition evaluation, is already in the RadialRecipe diagnostics (`calculate_energy_conditions`). For this campaign's scalar matter the NEC needs no sampling: along a null vector k the potentials drop out and T_ab k^a k^b is a signed sum of squares of the fields' derivatives along k, so its minimum over directions can be computed exactly. That closes the gap a sampled check leaves around narrow violations [Wpx26], which matters most for the exotic-free corridor of Knob 4+.

## How the solver works, in plain English

Two loops, one inside the other. The inner one is the spinning paper's Newton solver [Spin26], grown: it turns a recipe into an exact wormhole. The outer one is new: it changes the recipe to cut the bill.

```text
┌─ OUTER LOOP · the architect (the optimizer) ───────────────────────────────┐
│ Picks the throat size and spin to hold, then turns the matter knobs        │
│ (potential, layers, winding, angular ring, end-mass asymmetry γ) to        │
│ cut the exotic bill.                                                       │
│                                                                            │
│ 1. Start from a wormhole we already have: a member of the published        │
│    spinning family, the bare recipe (one massless exotic field, no         │
│    potential, no layers).                                                  │
│ 2. Hand the engineer a recipe: one setting of every knob.                  │
│                   │                                                        │
│                   ▼                                                        │
│   ┌─ INNER LOOP · the engineer (the spinning paper's Newton solver) ───┐   │
│   │ Unknowns on a 2D grid (distance through the throat × angle from    │   │
│   │ the spin axis): the four functions that shape spacetime, f, ω, N,  │   │
│   │ B, and the exotic field ψ.                                         │   │
│   │                                                                    │   │
│   │ Repeat:  how far off is each equation? Einstein's, the field's,    │   │
│   │          and two rows that hold the throat size and the spin.      │   │
│   │          JAX works out exactly how every equation responds to      │   │
│   │          every unknown (the Jacobian); one linear solve gives the  │   │
│   │          fix.                                                      │   │
│   │ Until:   every equation is off by less than 1e-12.                 │   │
│   │ Accept:  only if the Einstein equations it never solved also come  │   │
│   │          out zero and the grid resolves the shape; otherwise the   │   │
│   │          recipe is logged as unresolved, never as impossible.      │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                   │ an exact wormhole for this recipe                      │
│                   ▼                                                        │
│ 3. Read the bill: the exotic integral of the published Fig. 3e, per        │
│    throat radius. Read the checks: tidal pull, transit time,               │
│    blueshift, stability (the m = 0 growth rate).                           │
│ 4. Ask which way to turn the knobs: implicit differentiation. One          │
│    more linear solve with the Jacobian Newton already factored gives       │
│    the slope for every knob at once; Newton is never re-run per knob.      │
│ 5. Turn the knobs downhill and go back to 2. The engineer starts from      │
│    the last wormhole, so a small turn costs only a few Newton steps.       │
└────────────────────────────────────────────────────────────────────────────┘
                    │ every solved wormhole joins the archive: the
                    ▼ bill-vs-stability frontier and the design chart
┌─ CERTIFICATE · the GPU cluster ────────────────────────────────────────────┐
│ The winners become background tables and are evolved in full 3+1:          │
│ does the cheaper wormhole keep the stability that spin bought?             │
└────────────────────────────────────────────────────────────────────────────┘
```

**What is new against the spinning paper.** There the engineer was the whole job: the matter was fixed (one massless exotic field in closed form), Newton found f and ω, and N came from a least-squares fit, once per family member. Here ψ and B join the unknowns, so the matter can take whatever shape a recipe asks for, and the architect calls the engineer again and again. The intro's "AI" is the architect: a gradient-based optimizer, with CMA-ES as its derivative-free fallback, not a trained network.

**Why the slope is cheap.** The engineer stops only where every equation balances. Turn a knob slightly and the solution has to shift to keep them balanced, and the size of that shift is set by the same Jacobian Newton has just factored (the implicit-function theorem). So one extra linear solve per measured quantity, the bill or a bound, gives its slope for every knob at once. Nudging each knob and re-solving would cost a full Newton solve per knob, and differentiating through Newton's iterations gives noisy slopes (Trap 2).

**Where the time goes.** Inside the engineer: building the dense Jacobian and factorizing it. In the step-1 sweep, one Newton pass from a saved wormhole, compilation included, took 2 s at 48 × 12, 3 s at 72 × 18 and 15 s at 108 × 28 on four CPU threads; on the two largest saved grids the five-field dense Jacobian does not fit the CPU job's memory cap, so there the V = 0 system is solved block by block, which is exact at V = 0 but not for a potential. That is the work the batched GPU option of the Split card moves to a card.

The engineer with ψ and B as unknowns is step 1, the size and spin rows and the bill are step 2, and the architect is step 6; [STATUS.md](STATUS.md) says which are done.

## The matter soup, by hand

The four knobs the optimizer turns. Left: the matter profile through the throat. Right: the exotic region's shape across the throat plane. The bill is a toy model — the real numbers are what the search computes.

potential sculpting

normal-matter layer

spin v_e

equatorial focusing

exotic bill vs bare static throat**1.00**

vs spin alone (the known trick)**1.00×**

recipe**bare massless phantom**

Spin's factor follows the measured hundredfold trend; the other factors are illustrative. Whether they multiply, saturate, or backfire is exactly what the search measures.

## What the search does with the knobs

lineages:

potential only + layers + winding + angular ring = queued for GPU certification

Click a point for its recipe. Each point is one CPU solve of a few seconds; floors and rates are illustrative.

Solves run**0**

Best bill vs static**—**

Below spin-only by**—**

Queued for GPU**0**

## The campaign in fifteen cards

- Knob 1**Potential sculpting**

  A mass and sextic terms on the phantom stop it spreading: the exotic band squeezes into a thin shell at the throat, where it actually works. The dressed-star result already proved the mechanism survives evolution.
- Knob 2**Normal-matter layers** — dropped 2026-10-29

  A canonical field around or inside the exotic core. Ordinary gravity does part of the structural work free of charge; the phantom pays only for the flare-out nothing else can supply. Which layer goes where is the optimizer's call.
- Knob 3**Spin in the matter** — dropped 2026-10-29

  A winding complex field carries angular momentum in the matter phase instead of pure frame dragging — centrifugal support that violates nothing.
- Knob 4**Equatorial focusing** — dropped 2026-10-29

  Rotation flattens the throat, so the exotic matter may only be needed in an equatorial ring, not a full shell. Angle-dependent exotic profiles are completely untouched territory.
- Knob 2+**Multilayer onions — a measured question** — dropped 2026-10-29

  One exotic band at the throat is forced by theorem; every extra exotic shell starts in debt and must earn its place. Two mechanisms can pay for it: a long near-cylindrical neck held by marginal normal matter with only a tiny exotic pinch at the minimum, and normal layers stiffening stability like a composite. The ansatz carries 2–3 radial layers with free signs and amplitudes — a layer the physics rejects dies by its amplitude going to zero, a thickness floor keeps the ringing trap closed, and "how many layers does the optimal wormhole have?" becomes a result, not an assumption.
- Knob 3+**Counter-rotating layers** — dropped 2026-10-29

  Total J is pinned, but two layers rotating oppositely let the optimizer shape where the frame dragging sits — support where it helps, without growing the ergoregion where it hurts. One lineage of its own.
- Knob 4+**An exotic-free corridor — a lineage of its own** — dropped 2026-10-29

  One optional constraint: no NEC violation along the travel path, so the passenger never touches the exotic region. It needs confinement and angular structure together, since the massless phantom violates the NEC all along every radial ray; the natural candidate is an exotic equatorial ring around a clean polar corridor. Visser's 1989 polyhedral wormholes [V89b] are the thin-shell precedent: exotic matter on the edges, none on the faces a traveler crosses. The measured question: does the comfort cost extra, and how much?
- Knob 5**Throat shape — pin the size, free the form** — dropped 2026-10-29

  The size pin moves from the equatorial radius R_e to what passage depends on: the throat's proper area (areal radius R_A = √(A/4π)), or its smallest circumferential radius, what fits through the door — for the oblate throats of the spinning families, the polar R_pol. Both are already columns of the spinning solutions table. The shape — oblate, prolate, how flattened — then becomes a free design variable. Rotation already flattens it (R_pol < R_A < R_e in every member of that table); now the optimizer asks which shape is cheapest at a fixed size. It costs one changed constraint row.
- Knob 5+**Double throat — a measured question** — dropped 2026-10-29

  Two minimal surfaces each pay the NEC toll, so the prior says a double throat loses; but the ansatz admits one, and "one throat is optimal" is itself a result. The throat finder then tracks every minimum of the area, and the size pin applies to the narrowest.
- Knob 6**Dials already half-built** — γ scan done; charge dropped 2026-10-29

  The end-mass asymmetry γ: the solver already carries it (the drainhole family is γ = −π, the symmetric one γ = 0), so "is an unequal wormhole cheaper than a symmetric one?" costs only search time. Charge Q joins when a Maxwell brick lands; none is in the code yet.
- Objective**Minimize the bill, pin the throat**

  Minimize the integrated NEC violation per throat radius — the same quantity as the published Fig. 3e — at fixed throat size and fixed J, imposed as extra Newton rows like the existing J(ω) = J row. The first size pin is the equatorial radius R_e, which reproduces Fig. 3e; the area pin of Knob 5 then frees the shape, with the bill taken per pinned radius. Without the pin, the optimizer slides to extremal Kerr and declares victory. A smoothness penalty and a hard cap on the θ-modes keep every proposal inside what the spectral basis can resolve.
- Constraints**Traversability as inequality rows**

  Morris and Thorne's engineering criteria [MT88], written then as prose, become inequality constraints on every solved metric: tidal acceleration at the throat below a bound, transit time below a bound, blueshift bounded, the m = 0 growth rate ≤ 0 (stable), and resolvable (the spectral-tail check of Trap 1). The campaign statement is then literally: minimize the exotic bill subject to an exact Einstein solution, throat area = A, J = J₀, the tidal, transit and blueshift bounds, stability and resolution. The deliverable grows from a curve into the wormhole design chart — cost as a function of throat size, tidal tolerance and transit time, every cell a solved metric: "a human-passable, 1 g-tidal, one-hour-transit wormhole costs X in exotic matter; relax tidal to 10 g and it costs X/40" (numbers illustrative). As far as we know, no such table exists. The bill per radius is scale-free but the bounds are not (rescaling a solution by σ multiplies its tidal accelerations by σ⁻² and its transit time by σ), so the bounds are what give the chart its size axis. Stability is a constraint in the chart; the bill-vs-instability frontier of Trap 3 keeps it as an axis.
- Discipline**Accepted only on unimposed identities**

  Smarr, flux equality, full Einstein rebuild, grid change — plus three regression limits: potential → 0 reproduces the KK family, layer → 0 reproduces the bare throat, J = 0 cross-checks the dressed-star machinery.
- Split**CPU searches, GPU certifies** — 2D search closed 2026-10-29; GPU side is 3+1 only

  Every candidate is a seconds-long 2D spectral solve on CPU. The C++ never sees the search: it receives only the winners, as extended background tables — and the matter classes it needs are already compiled (phantom with potential, canonical partner fields, winding complex). Only example-level wiring is new. That split is the conservative version; the aggressive one runs the search itself on a GPU. The 2D solver is JAX, so candidates batch (vmap over candidates, batched dense LU), and one card could solve thousands of search-grid wormholes per minute while the others run the 3+1 certification: a GPU wormhole design engine whose every output is an exact solution with a dynamics certificate behind it. The throughput is to be measured, not assumed: dense LU suits the search grids, but the largest saved grids are already too big for a dense Jacobian (`validate_matter_v0.py` solves them block by block, which only V = 0 allows). Like any GPU start-up, it waits for the go.
- Outcomes**Both endings deliver the headline**

  Recipes well below the KK family: AI-discovered metrics, each getting its first-ever nonlinear evolution — does the cheaper design keep the stability spin bought? Every knob crawling back to KK: a rigidity result — the textbook wormhole is the optimum of its matter class — found by search. Either way: AI proposes the metric, the cluster evolves it. Both endings also fill the design chart: what a throat of a given size, tidal tolerance and transit time costs.

## Three traps, designed against

- Trap 1 · numerics**Spectral ringing on sharp rings**

  Optimizers push to extremes: the equatorial ring will be sharpened until the Chebyshev-and-cosine basis cannot represent it, and Newton then fails for numerical reasons that look like physics. Guard: a hard cap on the θ-modes plus a gradient penalty in the objective, and any failure flagged by the spectral-tail check is logged as unresolved — never as "no solution exists".
- Trap 2 · gradients**Differentiating through Newton**

  Unrolling Newton iterations gives noisy or exploding derivatives. The gradient is taken by implicit differentiation at the converged solution instead — one extra linear solve with the already-factored Jacobian. If it still misbehaves, CMA-ES is the standing fallback: derivative-free, proven in the warp campaign, affordable at seconds per evaluation.
- Trap 3 · physics**Cheap can mean fragile**

  Exotic matter is also the restoring force against radial collapse: the cheapest recipe may be the fastest to die. So the m = 0 growth rate is computed in the CPU loop alongside the bill, and the campaign's product is the trade-off itself — the Pareto frontier of exotic bill against instability rate, with the GPU as the final judge of its members. "What stability costs in exotic matter" is the figure the paper is built around.

## Implementation plan, step by step

1. **Make the phantom an unknown with a potential**

   In the 2D solver, ψ leaves its closed form and joins f, ω as a grid unknown, with V(ψ) = ½m²ψ² + sextic terms in the residuals; the derivation-check script extends to the new forms.

   *done when: V → 0 reproduces the KK family to 1e-10 on the saved solutions' gates*
2. **Pin the throat, measure the bill**

   Two constraint rows (equatorial throat radius R_e, angular momentum J) added to the Newton system, plus the exoticity observable — the Fig. 3e integral and the NEC violation along throat-threading rays. The throat row is written once for both size pins: R_e first, since it reproduces Fig. 3e, then the area pin of Knob 5, which frees the shape. The traversability observables join the exoticity module: tidal acceleration at the throat, transit time and blueshift.

   *done when: the observable reproduces the published Fig. 3e values on the existing 200 solutions, and the traversability observables match their closed forms on the static Ellis throat*
3. **First science run: potential only**

   Optimize the potential coefficients at three spins, bare field, no layers. The earliest possible answer to "is the landscape flat?"

   The end-mass asymmetry γ (Knob 6), which the solver already carries, gets the same scan at the same spins.

   *done when: the bill-vs-potential curve exists at three spins · decision: a flat landscape here raises the weight on layers and angular structure*
4. **Add the normal-matter layer** — **dropped 2026-10-29** (first cloud solves already ran; no further layers)

   Second canonical scalar χ in the solver; the J = 0 limit cross-checked against the 1D dressed-star machinery from the Bondi paper — the published object becomes the test case. Then layered optimization: core/envelope orderings, widths, amplitudes — generalized to 2–3 radial layers with free signs, so onion structures and neck-plus-pinch designs are reachable; a rejected layer dies by its amplitude going to zero, and a thickness floor keeps the ringing trap closed. A double throat (Knob 5+) is reachable here too; the throat finder tracks every minimum of the area, so a second throat is measured rather than missed.

   *dropped: not remaining work*
5. **Winding field and angular freedom** — **dropped 2026-10-29** (open defect parked; not to be resumed)

   The winding complex brick, and θ-dependent scalar profiles in a widened ansatz — spin carried by matter, and exotic rings instead of shells. The θ-ansatz carries its hard ℓ-cap and the objective its gradient penalty from day one, so the optimizer cannot sharpen a ring past what the basis resolves. A counter-rotating layer pair at pinned total J joins as its own lineage, shaping where the frame dragging sits without changing the global spin. The exotic-free corridor (Knob 4+) joins as a lineage once rings exist: the NEC margin along the travel path becomes a constraint.

   *dropped: not remaining work*
6. **Converge the search** — bare-field CMA-ES done; rotating 2D eigenproblem **dropped 2026-10-29**

   Gradients by implicit differentiation at the converged solution (one linear solve on the factored Jacobian, never unrolled Newton), CMA-ES on standby as the derivative-free fallback. The m = 0 growth rate joins the loop as a CPU-side observable, so the archive becomes the campaign's central object: the Pareto frontier of exotic bill vs instability rate vs spin. The traversability bounds and stability enter as inequality constraints, and the same archive fills the design chart. The batched GPU search (the Split card) is this step's option for volume, measured against the CPU loop before it replaces it.

   *done when: the frontier is stationary under further budget, each member passes a grid-change re-solve, and the design chart is filled over its declared ranges*
7. **Extend the hand-off** — bare-field path done; extra-field columns **dropped 2026-10-29**

   The background-table format grows columns for the new fields and momenta; the C++ table loader reads them.

   *bare-field done; layered/winding tables not remaining work*
8. **Wire the multi-field example** — bare-field path done (D51 evolved); multi-field **dropped 2026-10-29**

   A variant of the spinning-wormhole example mapping the extended table into the compiled matter classes, with the t = 0 cross-code consistency check in the profile-contract style.

   *bare-field done; multi-field not remaining work*
9. **Evolve the winners** — **the remaining work**

   The frontier recipes go to the cluster under the standing launch discipline — triplet, MOTS, gravitational-wave extraction, operator go. The question each run answers: did saving exotic matter cost the stability that spin bought?

   *done when: each frontier member has a three-resolution verdict*
10. **Publish by the outcome tree**

    Paper one: the minimal-exoticity landscape of rotating wormholes, with the bill-vs-stability Pareto frontier and the design chart (cost against throat size, tidal tolerance and transit time) as its central figures — what stability and passage cost in exotic matter. Paper two: the nonlinear dynamics of the optimal designs, the first evolutions of AI-proposed wormhole metrics. And if every knob crawls back to KK: the rigidity theorem of the matter class, proven by automated search.

    *every branch ends in a paper, and both carry the grant's headline*

## Code touchpoints

- Python · search side**Where the campaign lives**

  The package `grteclyn_wrapper/optimisation/` (its own since 2026-10-28; entry points in `grteclyn_wrapper.optimisation.commands`, with independent `checks` and symbolic `derivations`): `matter_equations.py` (matter terms; the R_e, area and J rows), `exoticity.py` (the exoticity observable with the traversability observables beside it), `solver/` (Newton and the JAX Jacobians), and later the knob continuation and the optimizer loop over JAX gradients. CPU by default, seconds per solve on the search grids, parallel under the standing memory caps; the batched GPU search is the aggressive option.
- C++ · certificate side**Touched only for winners**

  Background-table columns + `RotatingBackgroundTable.hpp` reader; a multi-field `SpinningWormhole` example variant. No new matter physics: `ExoticScalarField<PhantomDecayPotential>`, the signed-pair classes and the winding complex field are already compiled. No GRTresna anywhere.

Schematic. The bill factors, descent rates and floors in both panels are illustrative; the measured landscape is the campaign's output. Real anchors: the hundredfold spin reduction and the dressed-star survival from the published papers [Spin26, Bondi26].

## Sources

**Prior art**

- [VKD03] M. Visser, S. Kar, N. Dadhich, "Traversable wormholes with arbitrarily small energy condition violations", Phys. Rev. Lett. 90, 201102 (2003). [arXiv:gr-qc/0301003](https://arxiv.org/abs/gr-qc/0301003)
- [FR05] C. J. Fewster, T. A. Roman, "On wormholes with arbitrarily small quantities of exotic matter", Phys. Rev. D 72, 044023 (2005). [arXiv:gr-qc/0507013](https://arxiv.org/abs/gr-qc/0507013)
- [Lob04] F. S. N. Lobo, "Energy conditions, traversable wormholes and dust shells" (2004). [arXiv:gr-qc/0410087](https://arxiv.org/abs/gr-qc/0410087)
- [Kuh08] P. K. F. Kuhfittig, "Viable models of traversable wormholes supported by small amounts of exotic matter" (2008). [arXiv:0806.1194](https://arxiv.org/abs/0806.1194)
- [V89a] M. Visser, "Traversable wormholes from surgically modified Schwarzschild spacetimes", Nucl. Phys. B 328, 203 (1989).
- [V89b] M. Visser, "Traversable wormholes: Some simple examples", Phys. Rev. D 39, 3182 (1989).
- [PV95] E. Poisson, M. Visser, "Thin-shell wormholes: Linearization stability", Phys. Rev. D 52, 7318 (1995). [arXiv:gr-qc/9506083](https://arxiv.org/abs/gr-qc/9506083)
- [LL08] J. P. S. Lemos, F. S. N. Lobo, "Plane symmetric thin-shell wormholes: solutions and stability", Phys. Rev. D 78, 044030 (2008). [arXiv:0806.4459](https://arxiv.org/abs/0806.4459)
- [fRLm23] "Wormhole solutions in f(R, L_m) gravity" (2023). [arXiv:2306.10969](https://arxiv.org/abs/2306.10969)
- [fQ21] "Traversable wormhole geometries in f(Q) gravity" (2021). [arXiv:2102.00915](https://arxiv.org/abs/2102.00915)
- [fQT24] Gul, Sharif, Shahid, Javed, "Viable wormhole structures and energy conditions in f(Q,T) theory" (2024). [arXiv:2411.03642](https://arxiv.org/abs/2411.03642)
- [Lob12] F. S. N. Lobo, "Time machines and traversable wormholes in modified theories of gravity", review (2012). [arXiv:1212.1006](https://arxiv.org/abs/1212.1006)
- [Rev24] Radhakrishnan et al., "A review of stable, traversable wormholes in f(R) gravity theories" (2024). [arXiv:2405.05476](https://arxiv.org/abs/2405.05476)
- [Inv26] "Finite-domain inverse reconstruction of a Morris–Thorne-type wormhole candidate with a derivative-consistent f(R) curvature sector" (2026). [arXiv:2608.27485](https://arxiv.org/abs/2608.27485)

The modified-gravity and ML entries each stand for a whole topic: they are representative papers, chosen 2026-10-27.

**Warp Factory**

- [WF24a] "Analyzing warp drive spacetimes with Warp Factory" (2024). [arXiv:2404.03095](https://arxiv.org/abs/2404.03095)
- [WF24b] "Warp Factory: a numerical toolkit for the analysis and optimization of warp drive geometries" (2024). [arXiv:2404.10855](https://arxiv.org/abs/2404.10855)
- [Wpx26] "Observer-robust energy condition verification for warp drive spacetimes" (2026). [arXiv:2602.18023](https://arxiv.org/abs/2602.18023)

**Traversability**

- [MT88] M. S. Morris, K. S. Thorne, "Wormholes in spacetime and their use for interstellar travel: a tool for teaching general relativity", Am. J. Phys. 56, 395 (1988).

**This campaign's anchors**

- [Spin26] "Rotation slows the instability of Ellis–Bronnikov wormholes" (2026): the published Fig. 3e and the hundredfold spin reduction. [arXiv:2610.29941](https://arxiv.org/abs/2610.29941)
- [Bondi26] "The Bondi dipole in full numerical relativity: a self-accelerating positive–negative mass binary" (2026): the dressed phantom star. [arXiv:2608.24577](https://arxiv.org/abs/2608.24577)