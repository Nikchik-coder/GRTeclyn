# Campaign M (minimal exotic wormhole search): status

Started 2026-10-27 on branch `feature/optimisation`. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md); its ten steps are the checklist below.
Code: `grteclyn-wrapper/src/grteclyn_wrapper/analysis/spinning_wormhole/` (`matter_equations.py`, `potentials.py`) and
`grteclyn-wrapper/scripts/analysis/spinning_wormhole/` (`derive_matter_equations.py`, `check_matter_n_row.py`,
`validate_matter_v0.py`, `diagnose_matter_v0.py`). Test set: the spinning solver's 200 saved solutions,
`results/spinningwormhole/solutions/`.
Runs: CPU only, on the H100 test node (JAX is in the node's venv, not the workstation's), through
`grteclyn-wrapper/scripts/ops/capped_job.sh`; logs in the node's `runs/capped_jobs/` (untracked).
Commits so far: fc086e35, 7f090b51, 424fbe66, fdd8bd9b, 76f4bebf, then the N-row fix (2026-10-27).

## Now (2026-10-27)

**Running:** the V = 0 record sweep on the node (`v0-record-newton`, `v0-record-decoupled`; CPU, 4 threads each).

N is settled: the saved (constraint-fitted) N was right, and the imposed E_N row was at fault. Newton now imposes the
axis-regular row E_Nr. The gate passes everywhere except the near-extremal log-grid members, where the E19 monitor
sits at its sensitivity floor ([record](#step-1-record)). Accepting that floor is the open decision before step 1 is
ticked.

## Steps

- [ ] **1. The phantom becomes an unknown with a potential.** Done when V → 0 reproduces the KK family to 1e-10 on
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
  - [ ] V = 0 record sweep over the 200 members (running).
  - [ ] Decide the near-extremal E19 floor and the fam_a_log_0050 exception; tick step 1.
  - [ ] Optional, on the go: the solver on the node's H100 ([GPU notes](#gpu-notes)).
- [ ] **2. Pin the throat, measure the bill.** Done when the observable reproduces the published Fig. 3e values on
  the 200 saved solutions and the traversability observables match their closed forms on the static Ellis throat.
  - [ ] J pin: the `prescribe=("J", value)` row is coded (B³-weighted flux) but not yet tested.
  - [ ] Size pin: the R_e row first ([design below](#step-2-design-worked-out-not-coded)), then the area pin, which
    frees the throat's shape.
  - [ ] Exoticity module: the Fig. 3e integral and the NEC violation along throat-threading rays, with the
    traversability observables beside it (tidal acceleration at the throat, transit time, blueshift).
  - [ ] Fig. 3e reproduced on the 200 members; the traversability observables checked on the static Ellis throat.
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
- **Sweep so far:** Newton 149 of 150 pass (fam_a_log_0018: dF 5.4e-10 between two converged solves of the same f, ω
  rows, to check). Decoupled: the arctan members pass; fam_a_log 56–64 (144×30, v_e 0.97–0.99) fail on E19/D² only,
  1.1e-8 to 3.7e-8, with fields within 3e-11 of the reference and the saved family itself at 0.7e-8 to 1.6e-8.
- **The E19 floor there.** At 120×25, Newton and the block solve of fam_a_log_0050 agree to 4e-12 in f and N yet
  give E19/D² 1.4e-9 and 1.6e-8; fam_a_log_0064 falls from 3.7e-8 to 1.0e-8 between 144×30 and 180×36.
- **Leg ends.** fam_a_log_0049 fails on 96×20 and passes at 120×25. fam_a_log_0050 misses dN by 1.6e-10 on both
  grids: the reference N carries a grid-scale wiggle at the throat equator (its last ξ coefficient 3e-12, against
  5e-14 for E_Nr's N).

## Next

1. Finish the record sweep (the 108×28 members and the large grids); check fam_a_log_0018.
2. Decide: gate the near-extremal members on the saved family's own monitor level and accept fam_a_log_0050's
   reference wiggle, then tick step 1.
3. Step 2: test the J pin, then the R_e row.

## GPU notes

The step-1 solver can run on the node's H100. Nothing starts on the card without the go.
- **CPU only today**, three ways: the wrapper's `spinning-solver` extra pulls the CPU-only `jax`; the solver sets
  `jax_platforms` from `JAX_PLATFORMS`, default `cpu`; `capped_job.sh` exports `JAX_PLATFORMS=cpu` unless given
  `--gpu`.
- **Where the time goes.** One Newton pass from a saved member, compilation included, on four CPU threads (the
  record sweep, 2026-10-27): 1 s at 48×12, 3 s at 72×18, 7 s at 96×20, 15 s at 108×28; the block solve of the large
  grids, 19 s at 144×30, 64 s at 162×42 (the morning sweep measured about 4× more). Outside compilation the cost is the
  dense Jacobian (`jax.jacfwd`) and its LU (scipy, on the host). The Jacobian is about 5(n_x+1)(n_y+1) square: 2 GB
  at 108×28, 4 GB at 144×30, 10 GB at 162×42. What overflows on the two largest grids is the unchunked `jacfwd`,
  whose intermediates carry every column at once.
- **The port.** A CUDA build of JAX in the node's venv; `newton.py`'s `lu_factor`/`lu_solve` moved to
  `jax.scipy.linalg`, so the Jacobian stays on the card; the Jacobian built in chunks of columns (chunking alone
  would also let the CPU solve the large grids, at an estimated few minutes per pass). Jobs then run through
  `capped_job.sh --gpu`, after `nvidia-smi`, since the card is shared.
- **Expected, to be measured.** The H100 is fast in float64, which the solver needs, so a pass on the large grids
  should drop to seconds, and the 30 large-grid members get full Newton solves. The small grids gain
  little, since compilation dominates them, until candidates are batched (the plan's Split card, step 6). It speeds
  up the sweep and the ladders.

## Step 2: design worked out (not coded)

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

- Code reaches the node only through git: commit, push to the fork, then `git pull myfork feature/optimisation` on
  the node. Never scp. Commands go over ssh as a `bash -s` heredoc, because the gateway runs a bare command without a
  shell.
- Every node job goes through `capped_job.sh start <name> --threads 4 --mem <GB> --timeout <s> -- <cmd>`, then
  `status`, `tail` and `stop` by name; check for leftovers when it ends. Node quota: 12 CPUs and 195 GB, with
  `memory.oom.group = 1`, so one runaway kills everything in the container.
- No JAX in the workstation venv (decided 2026-10-27); local work uses at most 4 of its 8 cores.
- No GPU start-up of any kind without the go: the solver's GPU port ([GPU notes](#gpu-notes)) as much as the step-9
  evolutions.
