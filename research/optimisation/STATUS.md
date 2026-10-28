# Campaign M (minimal exotic wormhole search): status

Started 2026-10-27 on branch `feature/optimisation`. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md); its ten steps are the checklist below.
Code (its own package since 2026-10-28; layout and rules in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)):
`grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` (`matter_equations.py`, `potentials.py`, `exoticity.py`, and
`solver/`: Newton, the Jacobians, the jax device) and `grteclyn-wrapper/scripts/optimisation/` (`pipeline.py` +
`pipeline.toml`, `first_matter_solve.py`, `scan_potential.py`, `validate_matter_v0.py`, `check_matter_pins.py`,
`check_tidal.py`, `check_matter_n_row.py`, `diagnose_matter_v0.py`, `derive_matter_equations.py`); tests in
`grteclyn-wrapper/tests/optimisation/`. It reads the published spinning package, which never imports it.
Test set: the spinning solver's 200 saved solutions, `results/spinningwormhole/solutions/`.
Runs: on the H100 test node (JAX is in the node's venv, not the workstation's), CPU by default and on a card with the
go, through `grteclyn-wrapper/scripts/ops/capped_job.sh`; logs in the node's `runs/capped_jobs/` (untracked).
Commits so far: fc086e35, 7f090b51, 424fbe66, fdd8bd9b, 76f4bebf, 4bea3ebd (the N-row fix), then step 2's pins and
bill, and the step-2 close — tidal and the first V ≠ 0 solves (2026-10-27); then the move into the `optimisation`
package with the GPU port and the pipeline (2026-10-28).

## Now (2026-10-28, after the first step-4 cloud solves)

**Nothing is running** (the step-4 cloud jobs finished ~09:10 UTC / 12:10 MSK; both cards verified clear, scratch
clean). **Step 4 has its first spinning two-field members** (`cloud_solve.py`; [record](#step-4-record-2026-10-28)):
on fam_b_0003 at pinned J and R_e a mini-boson-star cloud sits peaked at the throat, the bill-vs-amplitude curve has
a genuine optimum — on the pure kink m 0.3 the cloud buys a further −1.63 % clean (E19 2.4e-9 PASS) at φ_c 0.08,
and too much cloud costs, like γ — and on the step-3 best shape (2.4, 2.4) the layered bill reaches −27.46 % vs
V = 0, past step 3's −27.27 %, but on the monitor floor (frontier class, not clean; the record has the three-grid
trend).

**Step 3's answer: the landscape is NOT flat, and no bottom was found.** The
shape scan (Q = 1 + q₁u + q₂u², `potentials.kink_q`, `scan_potential.py`, 5×5 box at kink mass 0.3, J and R_e
pinned, 150×30 on the cards) lowers the bill monotonically toward +q₁, +q₂ at all three spins, and the open ray
walks past the box (decided 2026-10-28: no preset limits, the gates call the stop) kept descending until Newton or
the 1e-6 monitor ceiling ended every ray. With the q-plane fill to 3 and the four-direction ray fan (same day,
262 / 284 / 312 solved points per spin), best clean against the V = 0 member: **−27.3 % / −26.9 % / −20.6 %** at
v_e 0.27 / 0.50 / 0.85 (the last at (1.5, 4.5), found by the fan), frontier (monitors above the 1e-8 gate but
under 1e-6) −32 % / −30 % / −24 %. The γ scan
walks to the drainhole's −π and the bill RISES monotonically, ≈ +42 % at γ = −π at all three spins (a nearly
spin-independent relative penalty); asymmetry costs, it never pays ([Step 3 record](#step-3-record-2026-10-28)). The
solver now runs on the GPU ([GPU notes](#gpu-notes): port done and verified 2026-10-28), and the campaign has an
entry point: `grteclyn-wrapper/scripts/optimisation/pipeline.py plan | list | run <stage> [--gpu N]`, with the
stages in `pipeline.toml` beside it. The campaign's code moved out of `analysis/spinning_wormhole/` into the
`optimisation` package (2026-10-28), with the GPU port inside it (`solver/`); the spinning package is back at its
published state. Checked on CPU against the code before the move: every moved script prints the same output, and
the 48×12 ladder keeps its digits (X 2.75525806, σ 1.0013837069 at m = 0.1).

**The three-spin first-V ladders, 150×30 on the cards** (a full five-mass ladder took ~40 s against 7 min for
120×25 on CPU; per-pass 5–7 s):
- fam_b_0003 (v_e 0.27): X 2.99352 → 2.17547 at m = 0.5 (−27 %); E19/D² m 0.1/0.2/0.3/0.5 =
  1.2e-6 / 7.6e-8 / 1.4e-9 PASS / 3.2e-9 PASS.
- fam_b_0012 (v_e 0.50): X 2.62527 → 1.93361 (−26 %); E19 1.2e-6 / 3.5e-8 / 9.3e-10 PASS / 2.7e-7.
- fam_b_0025 (v_e 0.85), completed 2026-10-28: X 1.46184 → 1.37131 → 1.29815 → 1.24120 → 1.16133 at
  m 0.1/0.2/0.3/0.5 (−21 % at m = 0.5); E19 8.9e-7 / 1.9e-8 / 1.1e-9 PASS / 4.1e-9 PASS. The bill falls with the
  kink mass at every spin; the relative fall shrinks with spin (−27 % / −26 % / −21 % at v_e 0.27 / 0.50 / 0.85).
- The 180×36 rung (`first-v-0003-180`, 2026-10-28, run twice on the card): **m = 0.1 still misses the 1e-8 gate** —
  E19/D² 2.2e-7 (identical both runs), down from 8.6e-6 (120×25) and 1.2e-6 (150×30), ~6× per rung, so the gate
  sits near 240×48. X is already grid-converged there (2.7559726, vs 2.7559756 at 120×25). m = 0.2 passes and
  reproduces (2.9e-9). m = 0.3 and 0.5 sit on a run-to-run noisy floor at this n = 32k: across the two identical
  runs E19 1.2e-8 / 3.8e-7 (m 0.3, the second's Newton stalling at 6.4e-12) and 5.0e-8 / 1.3e-6 (m 0.5), both UP
  from 150×30 (1.4e-9, 3.2e-9), while X holds to 9 digits (2.41053484, 2.17547410) and σ to 8. The GPU solve's
  reductions are non-deterministic, and the dense solve's round-off floor rises with the grid. Chasing the
  m = 0.1 gate by grid alone runs into that floor; either accept the small-m rungs on their falling-with-grid
  trend or treat the fixed-small-m gate as resolution-limited.

The 120×25 CPU ladder (fam_b_0003, `first-v-0003-120`, 7 min): X converges to 6 digits against 96×20
(m = 0.1: X 2.75597558), E19 at m = 0.1 still 8.6e-6; m = 0.5 ticked up (2.9e-8 → 6.8e-8), floor-like.

Step 1 is done: 186 of 200 members pass every gate, and the other 14 were accepted on 2026-10-27 (below). Step 2 is
done except the observables skipped for now (transit time and blueshift, decided 2026-10-27): the J pin, the bill,
the size pins and the tidal acceleration all pass their gates. The first V ≠ 0 solves (the entry to step 3) exist,
pass the unimposed identities at resolution, and their bill FALLS with the kink mass ([Step 2 record](#step-2-record-2026-10-27)).

## Steps

- [x] **1. The phantom becomes an unknown with a potential.** Done when V → 0 reproduces the KK family to 1e-10 on
  the saved solutions' gates.
  - [x] Matter system (`matter_equations.py`). ψ and B join f, ω, N as grid unknowns, bordered by ψ₋ (ψ at
    η → −∞). B is the extra metric function (p = B², B ≡ 1 at V = 0) that a potential needs. Five imposed rows
    (E_f, E_w, E_Nr, E_B, E_ψ); E_c, E19 and the derived ν row E_N are unimposed monitors. Rotation is pinned by ω∞
    or by J (`prescribe`).
  - [x] Derivation check (`derive_matter_equations.py`): the seven rows span Einstein + KG both ways (rank 7);
    stage `nrow` proves (1 − y) E_Nr = E_N − (2/h) E19 + E_B/B exactly; `v0forms` shows 2 E_Nr is the printed
    eq. (12) with its two misprints corrected.
  - [x] Potentials (`potentials.py`): every potential is a kink ψ²(ψ − ψ₋)²Q(ψ), and Q is what the search varies
    (the plan's ½m²ψ² + sextic admits no wormhole).
  - [x] N row fixed: E_N → E_Nr (below).
  - [x] Closed-form test of both N rows (`check_matter_n_row.py`).
  - [x] Validation (`validate_matter_v0.py`): gates against the member re-converged by the V = 0 solver on the
    same grid (Newton ≤ 1e-11; f, ω, N ≤ 1e-10; |B − 1| ≤ 1e-10; ψ₋ ≤ 1e-9; E19/D², E_c ≤ 1e-8 inside C ≥ 0.05).
    `--nx/--ny` re-solves on another grid; `--decoupled` solves the two largest grids block by block (exact at V = 0).
  - [x] Diagnostic (`diagnose_matter_v0.py`) and capped job runner (`capped_job.sh`, tracks jobs by session).
  - [x] Settle which discrete N is right: the constraint N.
  - [x] V = 0 record sweep over the 200 members: 186 pass, 14 accepted (below).
  - [x] Near-extremal E19 floor and the reference-side misses accepted (2026-10-27).
  - [x] The solver on the node's H100 (go given 2026-10-28; [GPU notes](#gpu-notes)).
- [x] **2. Pin the throat, measure the bill.** Done when the observable reproduces the published Fig. 3e values on
  the 200 saved solutions and the traversability observables match their closed forms on the static Ellis throat
  (transit time and blueshift skipped for now, 2026-10-27; the tidal acceleration stays).
  - [x] J pin tested (`validate_matter_v0.py --prescribe-j`): hold J, start ω∞ off by 1e-3, Newton recovers it
    in 3–4 iterations, to ≤ 4.3e-13 against the V = 0 solver on all 170 Newton members; held exactly in the 30
    block solves. The 3 known accepted members (fam_a_log_0049/0050, fam_a_p4_0004) re-flag on their reference-side
    dN (1.0–2.0e-10) and E19 floor only — the pin itself is clean on them.
  - [x] Size pins coded (`pin=("R_e", value)` or `("area", value)`): a length scale σ and the throat position ξ_t join
    the unknowns, rows dA/dξ = 0 and σR_e (or σ²A) = target; the potential scales by σ², J by σ².
  - [x] Size pins tested at V = 0 (`check_matter_pins.py`): both pins pass on all 5 members (fam_b_p4_0005,
    fam_b_0003, fam_a_r1_0026, fam_a_log_0042, fam_a_r1_0028 at 108×28): from σ off by 1e-3, σ back to ≤ 8e-13,
    ω∞ to ≤ 1e-13, the fields to ≤ 2e-12. (The 108×28 five-field Jacobian OOMs a 40 GB cap; 120 GB ran in 123 s.)
  - [x] Exoticity module (`exoticity.py`): the Fig. 3e bill X = |VIQ|/R_e from the solver's own fields (B, ψ, f), the
    throat (root of dA/dξ, to round-off), the NEC integral along the axis and equatorial rays. Static Ellis closed
    forms reproduced to 1e-14 (VIQ, R_e, NEC −D²/(8η₀³)).
  - [x] Fig. 3e reproduced on the 200 members: within 1.8e-8 of the published X (gate 1e-7); ≤ 6.5e-10 away from
    the near-extremal tail, which carries the step-1 E19 floor.
  - [x] Tidal acceleration at the throat (`exoticity.tidal`, gated by `check_tidal.py`): the full tidal tensor at
    the throat's equator for a radial transit at speed v, from the metric's spectral jets through a numerical
    Christoffel → Riemann assembly. Gates: Morris and Thorne's closed form on static Ellis (E_rad = 0, lateral
    stretch −γ_L²v²η₀²/h², ≤ 2e-13), the γ ≠ 0 static drainhole against separately-derived class formulas
    (≤ 3e-13), and on a rotating member the exact identities (boost-invariant E_rad, reflection zeros) to
    round-off. The axis transit needs a Cartesian chart and waits with the transit time.
  - [ ] Transit time and blueshift: skipped for now (decided 2026-10-27); the transit time needs a choice of stations
    first.
- [x] **3. First science run: potential only.** Optimize the potential at three spins, bare field, no layers; the
  end-mass asymmetry γ gets the same scan. Done when the bill-vs-potential curve exists at three spins; a flat
  landscape shifts the weight to layers and angular structure. **Done 2026-10-28 as a first pass: the curves exist
  at the three spins and the landscape is not flat** ([record](#step-3-record-2026-10-28)); the best shape sits on
  the scanned box's +q₁,+q₂ edge, so the knob's true optimum waits for step 6's optimizer (or a wider box).
- [ ] **4. Normal-matter layer.** A second, canonical scalar χ; the J = 0 limit cross-checked against the Bondi
  paper's dressed star; 2–3 radial layers with free signs; a double throat allowed as a measured lineage. Done when
  the identity gates pass with two fields and the layered bill beats or matches step 3 at matched R_e and J.
  - [x] Two-field system derived and machine-checked (2026-10-28). χ = X e^{iω_χ t}, a canonical complex scalar
    (R_ab += 2Re(χ_aχ̄_b) + 𝒰g_ab): stationary, axisymmetric, no angular momentum, so the twist row keeps no χ
    source. `derive_matter_equations.py` extended (field x, symbols U, Up, OC2, the kg_x row): span rank 8 both
    ways at three exact points, forms vs the derived rows 2.6e-51 (gate 1e-30), v0/v0forms reductions identical,
    and (1 − y)E_Nr = E_N − (2/h)E19 + E_B/B holds identically WITH the cloud. The harmonic phase reaches the
    rows as ω_χ²e^{−f}X²: doubled in E_f, once in E_B and E_N, ω_χ²e^{−f}X in the new KG row E_chi; every ψ
    bilinear gains a sign-flipped X twin; E_w, E_c, E19, E_Nr carry no potential or harmonic term.
  - [x] Solver carries it: `MatterCollocationProblem(..., chi=(cal U, omega_chi))` adds X as a sixth grid unknown
    (zero Dirichlet, no background; the pack's `dchi` is the Newton seed — X = 0 always solves, a cloud is found
    boson-star style at prescribed ω_χ, and the radial node count of X is the layer count). 𝒰 must be even in X
    (`PolynomialPotential.solitonic` is the dressed-star form). chi=None is the five-field system bit for bit
    (`test_chi_layer.py`: the six-field residual with a zero cloud embeds the five-field one exactly; pytest 15).
  - [x] J = 0 cross-check against the Bondi dressed star (`check_chi_star.py`, 2026-10-28, job `chi-star`): the
    published ultraweak canonical sextic star (ω 0.550, φ_c 1.9695e-2, 𝒰 by `from_evolution`; the map X = √(4π)φ₀,
    ω_χ = ω, e^{f/2} = α, B = ψ_c²α at ν = 0) threaded by a micro-throat. Newton 1e-15 from the 1D seed at η₀ 0.2
    and 0.1 (200×8), spherical to 7e-14 (max|N|, X anisotropy 4e-16), X at the throat = √4π φ_c to 4 digits, and
    the φ₀ / α / ψ_c² profile errors converge toward the 1D star at the η₀² rate (×4.0 / ×6.3 / ×3.8; the honest
    gate — at finite η₀ the geometries differ by the throat itself, O(η₀²), and the η-chart vs isotropic-r
    identification is exact only through r = (η + √h)/2). E_c 2.4e-11; E19/D² 2.3e-5 at η₀ 0.2 is the phantom's
    near-throat layer at center-grid Chebyshev spacing (160× down from nx 120 → 200: truncation, not structure) —
    composites with η₀ ≪ the map scale need the map matched to the throat.
  - [x] First cloud solves on a spinning member and the layered bill at matched R_e and J (2026-10-28,
    `cloud_solve.py`; [record](#step-4-record-2026-10-28)): the cloud holds at every amplitude tried, the bill has
    an optimum in the cloud amplitude, the clean gain on the pure kink is −1.63 % (PASS), and the layered bill
    passes step 3's best clean by −0.27 % — on the monitor floor, so frontier class until the floor decision.
  - [ ] Layers proper: multi-node clouds (the radial node count of X is the layer count), the sign freedom, a
    double throat as a measured lineage; and the floor decision that certifies or demotes the layered frontier
    rows.
- [ ] **5. Winding field and angular freedom.** The winding complex field, θ-dependent profiles with a hard ℓ cap and
  a gradient penalty, a counter-rotating pair at pinned J, the exotic-free corridor lineage. Done when all four
  knobs optimize together and a Gibbs-driven Newton failure is reported as a resolution verdict, not a physics one.
- [ ] **6. Converge the search.** Gradients by implicit differentiation (CMA-ES as the fallback), the m = 0 growth
  rate in the loop, the traversability bounds and stability as inequality constraints, the batched GPU search as an
  option. Products: the Pareto frontier of bill against instability rate and spin, and the design chart. Done when
  the frontier is stationary under more budget, every member passes a grid-change re-solve, and the chart is filled.
- [ ] **7. Extend the hand-off.** New background-table columns, read by `RotatingBackgroundTable.hpp`. Done when a
  bare-field table round-trips bit-compatibly.
- [ ] **8. Wire the multi-field example.** A `SpinningWormhole` variant on the compiled matter classes, with the
  t = 0 contract check. Done when the check passes and a bare-KK table evolves identically through the new path.
- [ ] **9. Evolve the winners** on the GPU, under the standing launch rules (nothing starts without the go). Done
  when each frontier member has a three-resolution verdict.
- [ ] **10. Publish by the outcome tree.** The minimal-exoticity landscape (the Pareto frontier and the design chart)
  and the dynamics of the optimal designs; or, if every knob crawls back to KK, the rigidity result.

## Step 1 record

- **The defect.** E_N's angular part is ∂²ν/∂θ² alone, so its N operator degenerates on the axis, and its
  collocation has a near-null mode on the y node next to the axis, flat in ξ (equilibrated condition number 9e5 at
  48×12 to 1.4e7 at 96×24, growing as ny⁴). Newton turned 5e-12 residuals into N errors up to 5e-7, which E19 sees
  times h: that was all 27 failures and the rising ladder.
- **The fix.** E_Nr = (E_N − (2/h) E19 + E_B/B)/(1 − y), at V = 0 the corrected CKK eq. (12): a regular axis, condition
  number 6e2 to 2.5e3.
- **Closed-form test** (an N with the family's shape, solved with its exact source): E_N's error is 5e-11 to 2e-9,
  9× larger on the axis node and not falling with the grid; E_Nr's falls to 3e-14 to 2e-13.
- **Ladder** (masked E19/D², E_Nr; with E_N it rose to 2e-5):

| member | 48×12 | 60×15 | 72×18 | 84×21 | 96×24 | 108×27 |
|---|---|---|---|---|---|---|
| fam_b_p4_0005 | 9.2e-11 | 2.7e-10 | 1.2e-10 | 1.5e-10 | 1.1e-10 | 3.6e-10 |
| fam_a_r1_0026 | 1.4e-6 | 3.0e-8 | 1.5e-10 | 1.3e-10 | 1.0e-10 | 3.0e-10 |
| fam_b_p4b_0019 | 3.3e-6 | 7.1e-8 | 3.6e-10 | 3.4e-10 | 2.5e-10 | 7.7e-10 |
| fam_a_log_0036 | 2.3e-5 | 3.2e-7 | 1.9e-9 | 1.5e-10 | 1.6e-10 | 3.7e-10 |
| fam_b_p4b_0010 | 4.8e-8 | 1.2e-10 | 1.8e-10 | 3.2e-10 | 3.2e-10 | 4.6e-10 |

- **The reference.** The saved files stopped Newton at 1e-12; re-converged with their own solver, F moves by up to
  1.5e-9 and their monitors drop up to 600× (fam_a_log_0042: 1.3e-7 → 2e-10). On re-converged (f, ω) the two N agree
  to 1e-13 to 3e-12, so the field gates compare with the re-converged member, not the file.
- **Record sweep:** 186 of 200 pass every gate (Newton 165 of 170, block solve 21 of 30). Accepted 2026-10-27, all on
  the reference's side or the monitor's floor:
  - fam_a_log 56–64 (144×30, v_e 0.97–0.99) on E19/D² only, 1.1e-8 to 3.7e-8; fields within 3e-11 of the
    reference, and the saved family itself at 0.7e-8 to 1.6e-8 (in the J run 51–55 sit at 1.0e-8 to 1.3e-8 too);
  - fam_a_log_0049, fam_a_log_0050, fam_a_p4_0003, fam_a_p4_0004: N 1.1e-10 to 2.0e-10 from the reference, a
    grid-scale wiggle at the throat equator in the reference N (last ξ coefficient 3e-12 to 5e-12, against 1e-14 to
    5e-14 in E_Nr's N);
  - fam_a_log_0018: F 5.4e-10 from the reference, whose Newton stalled at 8.4e-15; on the same f, ω the two N agree
    to 1.5e-12.
- **The E19 floor there.** At 120×25, Newton and the block solve of fam_a_log_0050 agree to 4e-12 in f and N yet
  give E19/D² 1.4e-9 and 1.6e-8; fam_a_log_0064 falls from 3.7e-8 to 1.0e-8 between 144×30 and 180×36.
- **Leg ends.** fam_a_log_0049 fails on 96×20 and passes at 120×25. fam_a_log_0050 misses dN by 1.6e-10 on both
  grids: the reference N carries a grid-scale wiggle at the throat equator (its last ξ coefficient 3e-12, against
  5e-14 for E_Nr's N).

## Step 2 record (2026-10-27)

- **J pin + bill on all 200** (node logs `runs/capped_jobs/j-pin-newton{,2}`, `j-pin-decoupled{,2}`): ω∞ recovered
  to ≤ 4.3e-13 on the 170 Newton members, held exactly in the 30 block solves; X within 1.8e-8 of the published
  Fig. 3e values (gate 1e-7; ≤ 6.5e-10 away from the near-extremal tail, which carries the E19 floor). The 3 known
  accepted members re-flag on their reference-side dN and E19 floor only.
- **Size pins 5 of 5** (`pins-v0`, `pins-v0-r1-0028b`): σ back to ≤ 8e-13, fields ≤ 2e-12. The 108×28 five-field
  Jacobian OOMs a 40 GB cap (the unchunked jacfwd); 120 GB ran it in 123 s.
- **Tidal** (`exoticity.tidal`): E_ij = R(e_i, u', e_j, u') in the radially-boosted ZAMO frame at the throat's
  equator, MTW sign, a = −E ξ, a positive eigenvalue compresses. fam_b_0003's throat at v = 0.9: eigenvalues
  (−3.99, −3.84, −0.044) — the lateral stretch of Morris and Thorne's Ellis form. Gates in `check_tidal.py`:
  static Ellis ≤ 2e-13, the γ ≠ 0 drainhole against separately-derived class formulas ≤ 3e-13, exact identities
  (boost-invariant E_rad, reflection zeros) on a rotating member to round-off.
- **First V ≠ 0 solves** (`first_matter_solve.py`: fam_b_0003, J and R_e pinned, kink λψ²(ψ − ψ₋)², λ = m²/ψ₋²,
  the vacuum riding the bordered ψ₋ via `potential_at`), at 96×20:

| m | 0 | 0.1 | 0.2 | 0.3 | 0.5 |
|---|---|---|---|---|---|
| X | 2.99352 | 2.75596 | 2.56591 | 2.41054 | 2.17547 |
| E19/D² | 9e-11 | 3.5e-5 | 1.8e-6 | 2.9e-7 | 2.9e-8 |
| ψ₋ | −3.0919 | −2.9162 | −2.7639 | −2.6298 | −2.4059 |

  - **The bill falls 27 % at m = 0.5 at fixed J and R_e**: the landscape is not flat, and the first knob already
    pays. These are the campaign's first exact V ≠ 0 rotating wormholes.
  - E19 falls with the grid (m = 0.1: 1.8e-3 → 1.7e-4 → 3.5e-5 over 48×12 → 72×18 → 96×20) in step with the
    spectral tails: resolution-limited, not structural; the small-m Compton tail is the slow part, and m = 0.1
    needs about 120×25 for the 1e-8 gate. X, σ and ψ₋ converge to 7–8 digits between 72×18 and 96×20.
  - Field shifts scale ~ m, not m²: the potential lifts the V = 0 family's flat D direction.
  - Two detuned forms were measured first and rejected by the monitors, both at Newton 1e-15: a frozen vacuum with
    ψ₋ bordered drifts the end off the vacuum (non-flat, E19 = O(1)); ψ₋ fixed at the vacuum drops the E19 border
    row and the constraint system's free constant survives (E19 0.1–0.8, linear in m). The unimposed identities
    caught both — the step-1 discipline doing its job.

## Next

1. Step 4, continued: multi-node clouds (the layer count) and the sign freedom; the cloud knobs (m_χ, φ_c) at the
   other two spins; continuation between cloud rungs instead of per-rung star reseeding (two rungs failed Newton
   from the raw star seed on the stiff shape).
2. The shape knob's true bottom needs more than rays: the q₃ fan broke the m₋ collapse (two independent dials —
   m₋ and the mid-kink barrier profile), so step 6's optimizer should carry (m, q₁, q₂, q₃) together, on a finer
   grid for the frontier (the monitors there are the resolution tail).
3. Decide the floor acceptance (gate at the floor vs the falling-with-grid trend) before anything quotes m ≤ 0.1
   members or the layered frontier rows: the dense solve's round-off floor rises with n and flips PASS/ABOVE-GATE
   near the gate between identical runs, and on the stiff shape + cloud rows it sits at 2e-7–1e-6 while X holds
   to 9 digits across three grids.

## Step 3 record (2026-10-28)

All six scans through `pipeline.py run <stage> --gpu N` (capped jobs of the same names; TSVs packed into
`results/optimisation/scans/`, the kink ladders into `results/optimisation/ladders_150x30.tsv`, and the figure —
`plot_potential_scans.py` in `visualisation/optimisation/`, which reads only the packed TSVs — into
`results/optimisation/figures/potential_scans`), at 150×30, kink mass 0.3 (the gate-clean
anchor), J and R_e pinned per member, each point a full Newton solve continued from its nearest solved neighbour,
the step-1/2 gates on every row.

- **Shape scan** (Q = 1 + q₁u + q₂u², u = ψ/ψ₋, q₁, q₂ ∈ {−0.6, −0.3, 0, 0.3, 0.6}; (−0.6, −0.6) inadmissible,
  min Q < 0): X falls monotonically toward +q₁, +q₂ at every spin. Against pure kink m 0.3 → best clean PASS →
  box corner (+0.6, +0.6):
  - fam_b_0003 (v_e 0.27): 2.41053 → 2.34007 at (+0.6, +0.3) → 2.32622 (corner, E19 2.9e-7); V = 0 X 2.99352,
    so −21.8 % PASS / −22.3 % corner. One stall at (+0.6, −0.3), Newton 1.8e-11.
  - fam_b_0012 (v_e 0.50): 2.13174 → 2.06052 at the corner itself, PASS; V = 0 2.62527, so −21.5 %.
  - fam_b_0025 (v_e 0.85): 1.24120 → 1.22177 at (+0.6, 0) → 1.21174 (corner, E19 2.9e-7); V = 0 1.46184,
    so −16.4 % PASS / −17.1 % corner.
  - The X surface is smooth across neighbours (steps ~1e-2, far above any monitor noise); the scattered
    ABOVE-GATE rows (E19 up to ~1e-6 at min Q 0.1 points) are the small-m-style resolution tail, worst where Q
    nearly touches zero and the barrier deforms hardest.
- **γ scan** (pure kink m 0.3, γ from 0 to −π in π/8 steps, same pins): X rises monotonically at every spin —
  2.41053 → 3.42888 (v_e 0.27), 2.13174 → 3.03551 (v_e 0.50), 1.24120 → 1.76892 (v_e 0.85) at γ = −π: +42 % at
  all three spins, nearly spin-independent, with σ falling to ≈ 0.52–0.54 (the pinned throat compresses the
  solution). End-mass asymmetry buys nothing anywhere on the walk.
- **Open ray walks** (same day, the box's +q₁,+q₂ edge was never a bottom; `--rays "0.3,0;0,0.3;0.3,0.3"`, stages
  `q-rays-*-150`): no preset limits — a ray stops on Newton failure, monitors > 1e-6 twice running, or X rising
  three rungs. Every ray ended on Newton or the monitor ceiling with X still falling: the landscape descends past
  everything reached, and the limit is the solver/grid, not the physics. Frontiers: v_e 0.27 X 2.03657 at
  (5.4, 5.4); v_e 0.50 X 1.84193 at (7.2, 0) — its pure-q₁ ray ran to q₁ = 7.2 before the monitor stop; v_e 0.85
  X 1.10451 at (7.2, 7.2). Best clean: 2.17720 at (2.4, 2.4), 1.92007 at (2.7, 2.7); at v_e 0.85 no rung past the
  box came in under the 1e-8 gate (E19 sat at 1e-8–1e-6), so its best clean stays the box corner, 1.21174. The
  rung at (0.6, 0.6) re-solved PASS in the walks after flagging ABOVE-GATE in the box scan (X agreeing to 1e-5):
  the monitor verdict near the gate carries the known run-to-run floor noise.
- **Map fill and fan** (same day, stages `q-fill-*-150` and `q-fan-*-150`): the (q₁, q₂) square filled to 3 at 0.3
  step (169 points each; 15 / 14 / 4 Newton failures by spin — the solvable region widens with spin) and four more
  ray directions (slopes 3 and 1/3, and (0.3, −0.1) / (−0.1, 0.3) dipping below the axes, with the min Q ≤ 0
  admissibility stop added to the ray mode). The fan moved the v_e 0.85 best clean to X 1.16011 at (1.5, 4.5)
  (−20.6 % vs V = 0) and the v_e 0.50 frontier to 1.82861 at (6.6, 2.2); at v_e 0.27 the below-axis ray (0.3, −0.1)
  walked farthest, to (6, −2). The figure's (a)–(c) panels show every solved point.
- **q₃ fan — the far-well-mass collapse BREAKS at cubic order** (2026-10-28, job `q3-fan-0003-150`; the ray mode
  takes any shape order now, TSV `fam_b_0003_rays3_150x30.tsv`). Two findings at fixed m₋ = m√(1+Σq): (i) pure q₁
  beats pure q₃ at every matched Σq (X 2.24021 vs 2.32077 at Σq = 2.4, 2.21106 vs 2.30489 at 3.0 — weight at
  lower powers of u pays more); (ii) the m₋-NEUTRAL ray (+0.3, 0, −0.3) — Q = 1 + 0.3k·u(1 − u²), both vacua's
  curvatures untouched — walked to (4.8, 0, −4.8) with X falling the whole way, 2.41053 → 2.22486 (−7.7 % at
  CONSTANT m₋, Newton the stop), and its reverse (−0.3, 0, +0.3) rises immediately. So the shape family is at
  least two-dimensional: m₋ AND where Q's weight sits across the kink (mid-kink barrier height). Two knobs are
  not enough; step 6's optimizer should carry (m, q₁, q₂, q₃).
- Mechanics: `scan_potential.py` accepts a line-search stall at ≤ 1e-11 as a solve (the step-1 Newton gate;
  2026-10-28, the m-anchor chain stalled at 1.1e-14 against tol 1e-14). argparse needs the `--q2=-0.3,0` form for
  leading-dash lists (so the `pipeline.toml` stages use it). The ray TSVs are packed beside the others in
  `results/optimisation/scans/`, and the figure's (f) panel takes its best clean shape from box + rays.

## Step 4 record (2026-10-28)

The first spinning two-field members (`cloud_solve.py`, jobs `cloud-first` 48×12 CPU, then `cloud-150`,
`cloud-150-q`, `cloud-180-q`, `cloud-120-q` on the cards): fam_b_0003 (v_e 0.27), J and R_e pinned, phantom walked
to kink m 0.3 (and on to the shape (2.4, 2.4) in 0.3 steps), then the canonical cloud 𝒰 = m_χ²X², m_χ = 1. Each
rung solves the 1D self-gravitating mini star at central amplitude φ_c (lam = mu = 0; ω is its gravitational
eigenvalue, `solve_selfgrav_boson_star`), prescribes that ω as ω_χ and seeds X from the star's profile at
r = σ(|η| + √h)/2; the metric continues from the previous rung. X = 0 always solves, so every cloud found is the
nontrivial branch; every converged cloud peaks at the throat (max |X| = X_throat, anisotropy through ν only).

- **The clean cloud optimum on the pure kink** (150×30): X 2.41053 → 2.40847 / 2.40223 / 2.37704 / **2.37129** /
  2.37787 / 2.40405 / 2.41467 at φ_c 0.01 / 0.02 / 0.05 / 0.08 / 0.1 / 0.15 / 0.2 — a genuine minimum at
  φ_c ≈ 0.08 (ω_χ 0.849, max X 0.30, σ 0.781): −1.63 % below the kink baseline, −20.79 % vs V = 0, E19 2.4e-9
  PASS (0.05 and 0.15 also PASS; the others sit at 1e-8–9e-8, the near-gate noise). By φ_c 0.2 the cloud costs
  (+0.17 %): structure pays only in moderation, as with γ. R_e held to 1.04003606 on every row; σ falls to 0.70
  as the cloud deepens the well.
- **The layered bill vs step 3** (shape (2.4, 2.4), whose no-cloud baseline reproduces X 2.17719659 exactly):
  X 2.17501 at φ_c 0.02 and **2.17135 at φ_c 0.05** = −27.46 % vs V = 0, past step 3's best clean −27.27 %. X is
  frozen to 9 digits across 120×24 / 150×30 / 180×36 while E19/D² RISES with the grid (φ_c 0.05:
  2.7e-7 → 6.1e-7 → 9.5e-7; E_c stays ~1e-10): the dense solve's round-off floor, not a truncation tail (which
  falls) and not a wrong continuous equation (which would sit still; the J = 0 cross-check's E19 fell 160× with
  nx). Frontier class until the floor decision (Next 3); the step-4 done-when ("beats or matches step 3") is met
  on the frontier and matched within 0.3 % clean.
- Mechanics: `throat()` unpacks 6 fields now; two rungs on the stiff shape (φ_c 0.01, 0.08) failed Newton from
  the raw star seed (8.5e-6, 1.04e-11 — the second a hair over the 1e-11 stall gate), bracketed by converged
  neighbours: continuation between cloud rungs is Next 1. Heavier clouds are no slower (10–27 s per rung at
  150×30–180×36 on a card).

## GPU notes

**Ported 2026-10-28** (the go that morning). Nothing starts on a card without the go; the cards are shared, so
`nvidia-smi` before every launch (`pipeline.py run --gpu N` checks and refuses a busy card without `--force`).
- **The port, as landed** (in `optimisation/solver/` since the move, 2026-10-28). `newton.py` picks its backend
  from the first Jacobian: a CUDA-resident jax array keeps equilibration, LU and solve on the card
  (`jax.scipy.linalg`, cusolver in float64); anything else runs the old numpy + scipy path untouched, and the
  returned solution is numpy either way. The Jacobian can be built in column blocks (`jacobian.chunked_jacfwd`: one
  jit, `lax.map` over blocks, same values as `jacfwd`) — `WH_JAC_CHUNK` sets the block, default 1024 on gpu and
  unchunked on cpu; chunking is what fits the card (and would also let the CPU reach the grids the unchunked
  `jacfwd` OOMs). `MatterCollocationProblem` reads it through `jacobian.dense_jacobian`; the spinning package's
  V = 0 `CollocationProblem`, the validation reference, keeps its published CPU `jacfwd`. `first_matter_solve.py`
  takes `--gpu CARD` and `--jac-chunk` (`device.select_device`), which also sets
  `XLA_PYTHON_CLIENT_ALLOCATOR=cuda_async` so a solve takes only what it uses on a shared card and gives it back
  between solves. (2026-10-28: with jax's default allocator — a grow-only pool capped at 75 % of the card — the
  180×36 ladder solved m = 0 then OOM'd every m > 0 Jacobian on a contiguous 16.9 GiB ask into the fragmented
  pool; `cuda_async` ran the same ladder whole, twice.)
- **Verified 2026-10-28**: at 48×12 the GPU run reproduces the CPU ladder digit for digit (X 2.75525806,
  σ 1.0013837069, E19 1.8e-3), Newton at round-off; the CPU chunked path (`WH_JAC_CHUNK=256`) likewise. GPU jobs
  run with a 220 GB address-space cap: CUDA's virtual reservations need the headroom, the resident set stays small.
- **Where the time went on CPU** (the record sweep, 2026-10-27): 1 s at 48×12 to 15 s at 108×28 per pass, four
  threads; the dense Jacobian (`jax.jacfwd`) plus its host LU dominated, and the unchunked `jacfwd`'s intermediates
  OOM'd 40 GB at 108×28. **Measured on the card** (2026-10-28): a full Newton solve at 150×30 (n ≈ 23.4k,
  7–12 iterations) runs in 4–7 s; a five-mass ladder in ~40 s wall, against 7 min for the 120×25 ladder on four CPU
  threads — roughly 25× on the grids that matter.
- The small grids still gain little (compilation dominates) until candidates are batched (the plan's Split card,
  step 6).

## Step 2: design notes (coded, record above)

- **The bill.** The published Fig. 3e plots X = |VIQ|/R_e, built by `plot_spin_trends.family()` from
  `observables.exotic_matter(sol, D)` and the throat's equatorial radius; families (η₀, γ) = (2, −π) "drainhole"
  and (1, 0) "symmetric". The matter solver's form, valid for any V: VIQ = −½ ∫dη ∫dμ B e^{−f/2} h ψ_η². With
  ψ_η = D/h and B = 1 it is `exotic_matter`'s −(D²/2) ∫dη/h ∫dμ e^{−f/2}, so the published values are the gate.
- **NEC along rays.** For L = 0 null rays through the throat, normalized to unit energy at +∞:
  −(1/4π) ∫dη e^{−ν/2} B^{−1} ψ_η². Static check: −D²/(8η₀³).
- **R_e pin.** Solve on the dimensionless grid (η̃₀ = 1) with a length scale σ as a bordered unknown; the potential
  scales by σ², R_e = σ R̃_e and J = σ² J̃. The throat position ξ_t is a further unknown, with the row dA/dξ = 0 for
  A = 2πh ∫dμ B² e^{−f+ν/2}; then R_e = B e^{−f/2} √h at the throat's equator (at B = 1, the R_eq of
  `observables._throat`). The area pin replaces the R_e condition with σ²A(ξ_t) = A₀; a double throat needs every
  minimum of A tracked.
- **Values off the nodes** (the throat, the rays): Chebyshev coefficients and Clenshaw, not barycentric
  interpolation. Barycentric interpolation breaks on a node, and the symmetric family's throat sits on ξ = 0, which
  is a node.

## Rules for this campaign

- The campaign's code lives in the wrapper: importable code in `grteclyn_wrapper/optimisation/`, runnable scripts in
  `grteclyn-wrapper/scripts/optimisation/`, tests in `grteclyn-wrapper/tests/optimisation/`. None under `research/`
  (decided 2026-10-28), and nothing outside the package imports it: `develop` ships without it
  (`tests/optimisation/test_layout.py` holds both dependency rules).
- Code reaches the node only through git: commit, push to the fork, then `git pull myfork feature/optimisation` on
  the node. Never scp. Commands go over ssh as a `bash -s` heredoc, because the gateway runs a bare command without a
  shell.
- Every node job goes through `capped_job.sh start <name> --threads 4 --mem <GB> --timeout <s> -- <cmd>`, then
  `status`, `tail` and `stop` by name; check for leftovers when it ends. Node quota: 12 CPUs and 195 GB, with
  `memory.oom.group = 1`, so one runaway kills everything in the container.
- No JAX in the workstation venv (decided 2026-10-27); local work uses at most 4 of its 8 cores.
- No GPU start-up of any kind without the go: the solver's GPU port ([GPU notes](#gpu-notes)) as much as the step-9
  evolutions.
