Campaign M — matter architectures for rotating wormholes

# Minimal exotic wormhole search

The AI designs the matter recipe — layered fields, sculpted potentials, spin — that holds a wormhole open with the least exotic matter. Every recipe that balances Einstein's equations is a new metric; the cluster then evolves it.

Everything known about rotating wormholes uses the simplest possible recipe: one massless exotic field, spread evenly, nothing else. Each restriction is a door. Spin alone already cut the exotic bill a hundredfold in the computed families, and the dressed phantom star showed that layering with a sculpted potential survives nonlinear evolution. This campaign opens all the doors at once, at fixed throat size and spin so the optimizer cannot cheat toward a black hole — and restricts itself to matter the GPU code already evolves, so every optimum goes straight to 3+1.

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

## The campaign in ten cards

- Knob 1**Potential sculpting**

  A mass and sextic terms on the phantom stop it spreading: the exotic band squeezes into a thin shell at the throat, where it actually works. The dressed-star result already proved the mechanism survives evolution.
- Knob 2**Normal-matter layers**

  A canonical field around or inside the exotic core. Ordinary gravity does part of the structural work free of charge; the phantom pays only for the flare-out nothing else can supply. Which layer goes where is the optimizer's call.
- Knob 3**Spin in the matter**

  A winding complex field carries angular momentum in the matter phase instead of pure frame dragging — centrifugal support that violates nothing.
- Knob 4**Equatorial focusing**

  Rotation flattens the throat, so the exotic matter may only be needed in an equatorial ring, not a full shell. Angle-dependent exotic profiles are completely untouched territory.
- Knob 2+**Multilayer onions — a measured question**

  One exotic band at the throat is forced by theorem; every extra exotic shell starts in debt and must earn its place. Two mechanisms can pay for it: a long near-cylindrical neck held by marginal normal matter with only a tiny exotic pinch at the minimum, and normal layers stiffening stability like a composite. The ansatz carries 2–3 radial layers with free signs and amplitudes — a layer the physics rejects dies by its amplitude going to zero, a thickness floor keeps the ringing trap closed, and "how many layers does the optimal wormhole have?" becomes a result, not an assumption.
- Knob 3+**Counter-rotating layers**

  Total J is pinned, but two layers rotating oppositely let the optimizer shape where the frame dragging sits — support where it helps, without growing the ergoregion where it hurts. One lineage of its own.
- Objective**Minimize the bill, pin the throat**

  Minimize the integrated NEC violation per throat radius — the same quantity as the published Fig. 3e — at fixed equatorial throat radius and fixed J, imposed as extra Newton rows like the existing J(ω) = J row. Without the pin, the optimizer slides to extremal Kerr and declares victory. A smoothness penalty and a hard cap on the θ-modes keep every proposal inside what the spectral basis can resolve.
- Discipline**Accepted only on unimposed identities**

  Smarr, flux equality, full Einstein rebuild, grid change — plus three regression limits: potential → 0 reproduces the KK family, layer → 0 reproduces the bare throat, J = 0 cross-checks the dressed-star machinery.
- Split**CPU searches, GPU certifies**

  Every candidate is a seconds-long 2D spectral solve on CPU. The C++ never sees the search: it receives only the winners, as extended background tables — and the matter classes it needs are already compiled (phantom with potential, canonical partner fields, winding complex). Only example-level wiring is new.
- Outcomes**Both endings deliver the headline**

  Recipes well below the KK family: AI-discovered metrics, each getting its first-ever nonlinear evolution — does the cheaper design keep the stability spin bought? Every knob crawling back to KK: a rigidity result — the textbook wormhole is the optimum of its matter class — found by search. Either way: AI proposes the metric, the cluster evolves it.

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

   Two constraint rows (equatorial throat radius R_e, angular momentum J) added to the Newton system, plus the exoticity observable — the Fig. 3e integral and the NEC violation along throat-threading rays.

   *done when: the observable reproduces the published Fig. 3e values on the existing 200 solutions*
3. **First science run: potential only**

   Optimize the potential coefficients at three spins, bare field, no layers. The earliest possible answer to "is the landscape flat?"

   *done when: the bill-vs-potential curve exists at three spins · decision: a flat landscape here raises the weight on layers and angular structure*
4. **Add the normal-matter layer**

   Second canonical scalar χ in the solver; the J = 0 limit cross-checked against the 1D dressed-star machinery from the Bondi paper — the published object becomes the test case. Then layered optimization: core/envelope orderings, widths, amplitudes — generalized to 2–3 radial layers with free signs, so onion structures and neck-plus-pinch designs are reachable; a rejected layer dies by its amplitude going to zero, and a thickness floor keeps the ringing trap closed.

   *done when: identity gates pass with two fields and the layered bill beats or matches step 3 at matched R_e, J*
5. **Winding field and angular freedom**

   The winding complex brick, and θ-dependent scalar profiles in a widened ansatz — spin carried by matter, and exotic rings instead of shells. The θ-ansatz carries its hard ℓ-cap and the objective its gradient penalty from day one, so the optimizer cannot sharpen a ring past what the basis resolves. A counter-rotating layer pair at pinned total J joins as its own lineage, shaping where the frame dragging sits without changing the global spin.

   *done when: all four knobs optimize together and a Gibbs-driven Newton failure is demonstrably reported as a resolution verdict, not a physics one*
6. **Converge the search**

   Gradients by implicit differentiation at the converged solution (one linear solve on the factored Jacobian, never unrolled Newton), CMA-ES on standby as the derivative-free fallback. The m = 0 growth rate joins the loop as a CPU-side observable, so the archive becomes the campaign's central object: the Pareto frontier of exotic bill vs instability rate vs spin.

   *done when: the frontier is stationary under further budget and each member passes a grid-change re-solve*
7. **Extend the hand-off**

   The background-table format grows columns for the new fields and momenta; the C++ table loader reads them.

   *done when: a bare-field table round-trips bit-compatibly through the extended format*
8. **Wire the multi-field example**

   A variant of the spinning-wormhole example mapping the extended table into the compiled matter classes, with the t = 0 cross-code consistency check in the profile-contract style.

   *done when: the contract check passes and a bare-KK table evolves identically through the new path*
9. **Evolve the winners**

   The frontier recipes go to the cluster under the standing launch discipline — triplet, MOTS, gravitational-wave extraction, operator go. The question each run answers: did saving exotic matter cost the stability that spin bought?

   *done when: each frontier member has a three-resolution verdict*
10. **Publish by the outcome tree**

    Paper one: the minimal-exoticity landscape of rotating wormholes, with the bill-vs-stability Pareto frontier as its central figure — what stability costs in exotic matter. Paper two: the nonlinear dynamics of the optimal designs, the first evolutions of AI-proposed wormhole metrics. And if every knob crawls back to KK: the rigidity theorem of the matter class, proven by automated search.

    *every branch ends in a paper, and both carry the grant's headline*

## Code touchpoints

- Python · search side**Where the campaign lives**

  `analysis/spinning_wormhole/equations.py` (matter terms), `continuation.py` (R_e and J rows, knob continuation), a new exoticity-observable module, the optimizer loop over JAX gradients. All CPU, seconds per solve, parallel under the standing memory caps.
- C++ · certificate side**Touched only for winners**

  Background-table columns + `RotatingBackgroundTable.hpp` reader; a multi-field `SpinningWormhole` example variant. No new matter physics: `ExoticScalarField<PhantomDecayPotential>`, the signed-pair classes and the winding complex field are already compiled. No GRTresna anywhere.

Schematic. The bill factors, descent rates and floors in both panels are illustrative; the measured landscape is the campaign's output. Real anchors: the hundredfold spin reduction and the dressed-star survival from the published papers.