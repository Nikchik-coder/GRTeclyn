Campaign F — spin-supported wormholes within the quantum budget

# Quantum budget wormhole search

Find a spinning wormhole whose negative-energy requirement is small enough, and shaped right enough, that quantum fields could legally supply it.

Every throat needs some negative energy — the theorems fix that. But quantum field theory really does produce it (Casimir effect), under strict rules on density, thickness and duration: the Ford–Roman bounds. One number scores a design against those rules — the compliance factor F, with F ≤ 1 meaning "nature could pay for this". Static wormholes fail by astronomical factors. Rotation cut the total exotic requirement a hundredfold in the backgrounds already computed; nobody has ever computed F for a rotating wormhole. The search minimizes F over shapes while the throat stays open and stable.

## The descent toward F = 1

lineages:

static anchor (Ford–Roman) existing spin family, F measured first +charge +winding +thin exotic band

Click any point for its card. All F values here are illustrative — measuring the real curve is Job 0.

Solutions measured**0**

Cards tried**0**

Best log₁₀ F**—**

Decades above budget**—**

## The stability window the search must also keep

card knob (charge / winding share) base family

radial collapse (m = 0) ergoregion risk (m ≥ 1, unchecked) safe window run: collapsed run: expanded run: no growth

In the base family the two danger zones overlap everywhere. Whether any card opens a real window is the search's question — the knob is illustrative.

## How the pipeline is adapted

- Catalog · frozen**One symmetry, one topology**

  Stationary axisymmetric × throat. Bricks: phantom (the budget being minimized), Maxwell charge, winding complex field, and a prescribed thin exotic band (the Teo-matter class). Dials: spin v_e, charge Q, end asymmetry γ, winding m, band position and thickness.
- Tier 2 · new headline**The compliance factor F**

  For the candidate's stress tensor: the worst violation of the Ford–Roman quantum bound over observers and sampling windows (within the curvature-scale validity of the curved-space bounds). F ≤ 1 means quantum fields can legally supply the exotic matter. This replaces "total exotic" as the objective, because small-but-wrongly-shaped still fails.
- Anti-cheat**Openness is pinned**

  Exotic → 0 along the spin family only because it slides toward extremal Kerr, where the throat closes. F is minimized at fixed usability — lapse at the throat, transit blueshift and traversal time bounded — or the optimizer trivially returns a black hole.
- Tier 3 · widened**Stability against everything**

  The published result is axisymmetric-only, and above v_e ≈ 0.46 the throat carries an ergoregion — a nonaxisymmetric danger. "Stable" now requires the m = 0, 1, 2 spectra. Exponentially slow ergoregion growth counts as effectively stable, with the rate reported.
- Method**Continue the boundaries, don't scan**

  A stability edge (γ = 0) or an F level set is one extra equation on the background-plus-mode system. Newton continuation traces these surfaces through card space directly, so the window question is answered by geometry, not by ten thousand samples.
- Job 0 · no new physics**Measure F on what exists**

  200 converged rotating solutions are already on disk. Computing F across both families, anchored at the Ford–Roman static value, gives the curve F(v_e) — a standalone paper before the search even starts, and it tells the search where to dig.
- Outcomes**Both endings publish**

  If the frontier extrapolates to F \~ 1 anywhere short of throat degeneration: the first wormhole design quantum fields could support. If F has a hard floor: the first quantitative measure of how far any spinning wormhole sits from the quantum budget — the number the "arbitrarily small violations" literature is missing.
- Before building**Check the literature edge**

  The rapid-rotation QNM paper and the charged-family perturbation work may already contain m ≥ 1 rates — if so, the ergoregion verdict starts from their surface. And keep the distinction sharp: small total violation (known since Visser–Kar–Dadhich) is not the same claim as quantum-suppliable; F is the bridge.

## Implementation plan, step by step

1. **Reproduce the anchors — no new code**

   Redo the Ford–Roman accounting for the static wormhole (the published astronomical F), and pull whatever m ≥ 1 or QNM rates already exist in the charged-family and rapid-rotation papers, so nothing below rediscovers known results.

   *done when: the static F anchor matches the literature and the known-rates table sits in the repo*
2. **Measure F on the 200 existing solutions**

   Build the F observable (job F1) and run it over both spin families. This is the first real number anyone has for a rotating wormhole, and it is the figure of paper one.

   *done when: F self-converges under grid change and the F(v_e) curve is plotted against the static anchor · decision: if F falls faster than the 100× total-exotic trend, spin reshapes as well as shrinks — push the spin side; if slower, shape is the lever — push the thin-band side*
3. **Settle the ergoregion question**

   Build the per-m stability tool (job F2): validate m = 0 against the known slow-rotation and static rates, then compute m = 1, 2 across the spin ladder. This is the verdict the published paper explicitly left open, and paper two on its own.

   *done when: growth rates per m per spin at three grids · decision: the stable-or-slow region defines where the search is allowed to live; if everything above v_e ≈ 0.46 grows fast, stabilizing below the ergoregion via charge or winding becomes the campaign’s main line*
4. **Add charge and winding, re-run steps 2–3 on them**

   Maxwell and winding bricks in the solver (job F3), the charged ladder checked against the published perturbative family. Three families now carry F curves and stability maps — the first cross-family comparison of price and safety.

   *done when: identity gates pass on the new families and their F and γ tables exist*
5. **Trace the boundaries instead of scanning**

   Boundary-continuation mode (job F5): impose γ = 0 or an F level as one extra equation and let Newton continue the surface through (v_e, Q, winding, asymmetry). The window question — does a fully safe region exist, and how big — is answered by geometry.

   *done when: the known mode crossing near 30% of extremal spin is recovered, then the window (or its emptiness) is mapped*
6. **Full search with the thin exotic band**

   Add the prescribed-band brick (job F4) and run the archive with both mutation arms: minimize F at fixed openness inside the allowed region, and find whether any stationary solution exists whose exotic band fits inside the quantum-allowed box with ordinary matter carrying the rest.

   *done when: the Pareto sheet F vs openness stops moving under further search budget*
7. **Certify the winners in 3+1**

   The best window members and lowest-F candidates go to the H100s under the standing launch rules: resolution triplet, MOTS, long evolution. Nonlinear confirmation is the certificate, not the search.

   *done when: the top candidates survive (or their failure modes are measured) at three resolutions*
8. **Publish by the outcome tree**

   Paper one: F(v_e) for rotating wormholes. Paper two: ergoregion rates. Paper three: either the first quantum-budget-compatible (or fully stable) spinning wormhole, or the quantitative no-go with the converged frontier as its central figure.

   *every branch of the tree ends in a paper*

## Job reference — acceptance criteria

- F1**F observable**

  Ford–Roman sampling over observer congruences on the spectral backgrounds. Accepted when the static Morris–Thorne anchor reproduces the published accounting and F self-converges under grid change.
- F2**Per-m eigenproblem**

  Linear modes of the rotating backgrounds for m = 0, 1, 2. Accepted when m = 0 reproduces the known slow-rotation rates and the static GGS rate. This tool alone yields the ergoregion-rates paper.
- F3**Charge and winding bricks**

  Maxwell and winding complex fields in the 2D solver, gated on the usual unimposed identities; charged family checked against the published perturbative one.
- F4**Thin-band brick**

  Prescribed-stress exotic band (Teo class) with QI-shaped parameters, plus ordinary matter carrying the rest. Feasibility region = where a stationary solution exists with the band inside the quantum-allowed box.
- F5**Boundary continuation**

  γ = 0 and F-level surfaces traced directly with the existing Newton machinery; validated by recovering the known mode-crossing near 30% of extremal spin.

Schematic. Every F value, descent rate and window edge in the animations is illustrative; the measured quantities come from Jobs F1–F5. Real anchors shown: the run outcomes of the rotating-collapse paper and its stability thresholds.