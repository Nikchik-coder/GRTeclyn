# Campaign M (minimal exotic wormhole search): status

Started 2026-10-27 on branch `feature/optimisation`. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md); its ten steps are the checklist below.
Code (its own package since 2026-10-28; layout and rules in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)):
`grteclyn-wrapper/src/grteclyn_wrapper/optimisation/` (`matter_equations.py`, `potentials.py`, `exoticity.py`, and
`solver/`: Newton, the Jacobians, the jax device) and `grteclyn-wrapper/scripts/optimisation/` (`pipeline.py` +
`pipeline.toml`, `first_matter_solve.py`, `validate_matter_v0.py`, `check_matter_pins.py`, `check_tidal.py`,
`check_matter_n_row.py`, `diagnose_matter_v0.py`, `derive_matter_equations.py`); tests in
`grteclyn-wrapper/tests/optimisation/`. It reads the published spinning package, which never imports it.
Test set: the spinning solver's 200 saved solutions, `results/spinningwormhole/solutions/`.
Runs: on the H100 test node (JAX is in the node's venv, not the workstation's), CPU by default and on a card with the
go, through `grteclyn-wrapper/scripts/ops/capped_job.sh`; logs in the node's `runs/capped_jobs/` (untracked).
Commits so far: fc086e35, 7f090b51, 424fbe66, fdd8bd9b, 76f4bebf, 4bea3ebd (the N-row fix), then step 2's pins and
bill, and the step-2 close — tidal and the first V ≠ 0 solves (2026-10-27); then the move into the `optimisation`
package with the GPU port and the pipeline (2026-10-28).

## Now (2026-10-28)

**Nothing is running** (everything stopped on the word, ~06:05 UTC / 09:05 MSK; both cards verified clear). The
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
- fam_b_0025 (v_e 0.85), stopped mid-ladder after m = 0.2: X 1.46184 → 1.37131 (m 0.1) → 1.29815 (m 0.2, −11 %);
  E19 8.9e-7 / 8.4e-8. The bill falls with the kink mass at every spin measured; the relative fall shrinks
  with spin.
- The m = 0.1 rung misses the 1e-8 gate at every grid so far (8.6e-6 at 120×25 CPU, 1.2e-6 at 150×30); the 180×36
  rung (`first-v-0003-180`) was launched and stopped on the word after its clean m = 0 solve (E19 1.1e-10).

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
- [ ] **3. First science run: potential only.** Optimize the potential at three spins, bare field, no layers; the
  end-mass asymmetry γ gets the same scan. Done when the bill-vs-potential curve exists at three spins; a flat
  landscape shifts the weight to layers and angular structure.
- [ ] **4. Normal-matter layer.** A second, canonical scalar χ; the J = 0 limit cross-checked against the Bondi
  paper's dressed star; 2–3 radial layers with free signs; a double throat allowed as a measured lineage. Done when
  the identity gates pass with two fields and the layered bill beats or matches step 3 at matched R_e and J.
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

1. Finish `first-v-0025-150` (stopped after m = 0.2) and the 180×36 rung for the m = 0.1 gate
   (`pipeline.py run <stage> --gpu N`; each is about a minute on a card).
2. Step 3 proper: scan Q(ψ) beyond the pure kink at three spins, same gates and pins.

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
  `XLA_PYTHON_CLIENT_PREALLOCATE=false` so a solve takes only what it uses on a shared card.
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
