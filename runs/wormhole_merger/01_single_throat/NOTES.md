# 01_single_throat -- does ONE throat just sit still?

Single-throat "does it just sit still?" test (Stage 1 of `research/merger/FIx.md`).
Initial data: massive Ellis-Bronnikov drainhole, a = 2, m = 1, so M_ADM = 1.
The exact answer the code should reproduce is a throat that **does not move**:

    minimal surface at rbar = 1.6180,  areal radius R_min = 3.8895,  chi = 0.1731

Two knobs are varied, plus the refinement depth:

* **lapse type** -- `5` = the drainhole's own static lapse, nothing else.
  `6` = the same lapse times an "origin-isolating collar" that drives alpha -> 0
  in a small ball around the coordinate origin.
* **sigma** -- Kreiss-Oliger dissipation.  `2.0` was inherited from the puncture era.
* **max_level** -- 2 by default; `0` is the unigrid control (Stage 1.4).

## Results, in one place

**sigma = 2.0 must not ship.**  It shrinks the throat 34% over 40 M while every
constraint norm reads flat.  At sigma = 0.1 / 0.0 the same run holds it to 0.1-0.5%.

**The collar stays.**  The plan predicted it was a needless perturbation; the origin
diagnostic says the opposite -- it is worth a factor 3.5 in how long the run survives.
Its cost is 20% on the throat radius.  Two independent trade-offs, not one setting.

**Refinement is the protector, not the killer.**  Both sigma = 0.1 arms NaN'd on
level 2, which looks like a refinement-boundary bug.  Removing refinement entirely
makes it 4x worse, and refining uniformly makes it 20x worse.

**...but the refinement CRITERION is now the binding problem.**  The best arm
(sigma = 0, no collar) did not go unstable at all -- it ran the card out of memory
at t = 35.2.  This example tags on chi gradients (`ChiTagger`), so as the
undissipated numerical junk grows and spreads, the mesh chases it: level 2 reached
**1000 grids / 32.8M cells / 24% of the domain**, and the footprint went 3.9 GB ->
30.6 GB.  Zero dissipation is therefore not free either -- it buys throat accuracy
and pays in runaway regridding.  The framework already ships `FixedGridsTagger`
(Source/Tagging/), which refines a static nested box around the centre; that is
where this problem actually needs resolution (chi -> 0 at the origin), and it does
not chase error.  Switching this example onto it is Stage 1.5.

## The runs

| dir | lapse | sigma | max_level | outcome |
| --- | --- | --- | --- | --- |
| `stage1_lapse5`        | 5 (no collar) | 2.0 | 2 | ran to t = 40; throat destroyed (2.578) |
| `stage1_lapse6`        | 6 (collar)    | 2.0 | 2 | NaN at t = 21.7 |
| `stage1_lapse5_sg01`   | 5 (no collar) | 0.1 | 2 | NaN at t = 24.2, throat still 3.894 |
| `stage1_lapse6_sg01`   | 6 (collar)    | 0.1 | 2 | NaN at t = 31.4, throat drifted to 3.127 |
| `stage1_lapse5_sg00`   | 5 (no collar) | 0.0 | 2 | **OUT OF MEMORY** at t = 35.2 -- never went unstable; throat still 3.87-3.95 |
| `s1uni128_lapse5_sg01` | 5 (no collar) | 0.1 | **0**, dx = 0.50 | NaN at t = 6.6 (`K`, level 0) |
| `s1uni256_lapse5_sg01` | 5 (no collar) | 0.1 | **0**, dx = 0.25 | NaN at t = 1.2 (`h11`, level 0) |

All are L = 64, centre (32,32,32), stop_time = 40; N = 128 except `s1uni256` (N = 256).

### Throat radius R_min(t)   (exact answer: 3.8895, flat)

| t | l5 sig2.0 | l6 sig2.0 | l5 sig0.1 | l6 sig0.1 | l5 sig0.0 |
| --- | --- | --- | --- | --- | --- |
| 2  | 3.8867 | 3.8911 | 3.8917 | 3.8913 | 3.8917 |
| 5  | 3.8873 | 3.8824 | 3.8916 | 3.8796 | 3.8916 |
| 10 | 3.7846 | 3.8486 | 3.8918 | 3.8689 | 3.8916 |
| 20 | 4.4022 | 3.7697 | 3.8960 (22.5) | 3.7540 (24.7) | 3.9530 (31.4) |
| 30 | 2.7662 | NaN 21.7 | NaN 24.2 | 3.1274 (31.4) | 3.8725 (34.7) |
| 40 | 2.5782 | | | NaN 31.4 | |

### L2 Hamiltonian constraint -- READ WITH CARE

It is flat (~1.3e-3) for the whole 40 M of the sigma = 2.0 arm, the arm whose throat
shrank 34%.  Heavy dissipation smooths the solution, and a smoothed solution violates
the constraints *less*, so this norm cannot see its own failure mode.  Only the low-
sigma arms report honestly: sigma = 0 grows 2e-3 -> 1.1e-1, doubling every ~5 M.

### Origin health -- `chiA_min` in `data/binary_throat_diagnostics.dat`

That column is NOT the throat (for a wormhole the global chi minimum is the other
universe's infinity, compactified to rbar -> 0, where chi vanishes like rbar^4).  Read
as an origin monitor it is the controlling variable in every arm:

| arm | dx at origin | chi at origin, t = 0 | reaches the 1e-8 floor |
| --- | --- | --- | --- |
| unigrid, no collar    | 0.5   | 2.44e-3 | t = 6.6 |
| unigrid, no collar    | 0.25  | 1.33e-4 | t = 1.2 |
| ml2, no collar, sg0.1 | 0.125 | 7.19e-6 | t = 9.0 |
| ml2, **collar**, sg0.1| 0.125 | 7.19e-6 | t = 31.4 |
| ml2, no collar, sg0.0 | 0.125 | 7.19e-6 | never |

Halving dx drops chi at the innermost cell by 2^4 -- measured ratios 18.4 and 18.5
against the predicted 16.  CCZ4 divides by chi, so a *uniform* grid cannot be refined
at the origin without refining it everywhere.  Hitting the floor is a precursor, not
the death: the no-collar sg0.1 arm floored at t = 9.0 and ran on to t = 24.2.
