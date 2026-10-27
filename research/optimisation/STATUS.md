# Campaign M (minimal exotic wormhole search): status

Started 2026-10-27 on branch `feature/optimisation`. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md); its ten steps are the checklist below.
Code: `grteclyn-wrapper/src/grteclyn_wrapper/analysis/spinning_wormhole/` (`matter_equations.py`, `potentials.py`) and
`grteclyn-wrapper/scripts/analysis/spinning_wormhole/` (`derive_matter_equations.py`, `validate_matter_v0.py`,
`diagnose_matter_v0.py`). Test set: the spinning solver's 200 saved solutions, `results/spinningwormhole/solutions/`.
Runs: CPU only, on the H100 test node (JAX is in the node's venv, not the workstation's), through
`grteclyn-wrapper/scripts/ops/capped_job.sh`; logs in the node's `runs/capped_jobs/` (untracked).
Commits so far: fc086e35, 7f090b51, 424fbe66, fdd8bd9b, 76f4bebf.

## Now (2026-10-27)

**Nothing is running.** The node jobs were stopped on request and the node checked clean. Its checkout is at fdd8bd9b,
before the runner fix, so pull before the next job.

Step 1 is built, but its gate is not passed. At V = 0 the new solver reproduces f and ω of the saved family, but its N,
solved from the elliptic E_N row, differs from the saved N, which was fitted to the constraints. On 27 of the 166
members checked, that difference lifts the unimposed constraint monitors above the 1e-8 gate. Next: find out which of
the two discrete N is right ([next actions](#next-step-1)).

## Steps

- [ ] **1. The phantom becomes an unknown with a potential.** Done when V → 0 reproduces the KK family to 1e-10 on
  the saved solutions' gates.
  - [x] Matter system (`matter_equations.py`). ψ and B join f, ω, N as grid unknowns, bordered by ψ₋ (ψ at
    η → −∞). B is the extra metric function (p = B², B ≡ 1 at V = 0) that a potential needs: 𝒱 sources
    R^t_t + R^φ_φ = −2𝒱, which the three-function KK ansatz cannot carry. Five elliptic rows (E_f, E_w, E_N, E_B,
    E_ψ); the constraints E_c and E19 stay unimposed, as monitors. Rotation is pinned by ω∞ or by J (`prescribe`).
  - [x] Derivation check extended (`derive_matter_equations.py`). The seven rows, derived and checked in exact
    rational arithmetic, span the Einstein + Klein–Gordon system both ways (rank 7).
  - [x] Potentials (`potentials.py`; one polynomial object serves numpy, JAX and sympy). Deviation from the plan: its
    ½m²ψ² + sextic admits no wormhole. 𝒱 and 𝒱′ must vanish at both scalar end values, 0 and ψ₋, so every
    potential is a kink ψ²(ψ − ψ₋)²Q(ψ), and Q is what the search varies.
  - [x] Validation (`validate_matter_v0.py`): Newton from each saved member. Gates: Newton ≤ 1e-11; f, ω, N against
    the saved fields ≤ 1e-10; |B − 1| ≤ 1e-10; ψ₋ ≤ 1e-9 relative; monitors E19/D² and E_c ≤ 1e-8 inside
    C = η₀/√h ≥ 0.05 (the far-zone mask of `identity_gates`). `--nx/--ny` re-solves on another grid;
    `--residual-only` checks the saved fields on the two largest grids.
  - [x] Diagnostic (`diagnose_matter_v0.py`): re-evaluates the monitors with B, ψ and N reset one at a time, and
    re-solves the member the old way on the same grid.
  - [x] Capped job runner (`capped_job.sh`): thread, memory and time caps, its own session, `status`/`tail`/`stop`
    by name. Since 76f4bebf it tracks the whole session; on 2026-10-27 a stop by process group left the workloads
    running.
  - [ ] V = 0 sweep over the 200 members: 166 run, 139 pass, 27 fail, 34 not run.
  - [ ] Optional, on the go: the solver on the node's H100 ([GPU notes](#gpu-notes)). Full Newton solves for the 30
    large-grid members instead of `--residual-only`, and faster ladders; it does not settle N.
  - [ ] Settle which discrete N is right; fix the row or re-gate.
  - [ ] Gate passed on all 200; step-1 record written.
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

## Step 1: results so far

**Sweep** (V = 0, each member on its own grid, Newton from the saved fields with B = 1 and the closed-form ψ):
139 of the 166 checked pass. Every failure took one Newton step. In the four examined, f and ω stay with the saved
fields (5e-12), B and ψ at roundoff, while N moves by 6e-9 to 6e-8 and E19/D² rises to 6e-6 to 1e-4.
- Failed (27): fam_b_p4 4–5 (48×12); fam_a_r1 17, 22, 26 and fam_b_p4b 16–20 (72×18); fam_a_log 34–42, 49–50
  (96×20); fam_a_r1 27–28 and fam_a_p4 2–5 (108×28). Mostly leg ends before a grid switch, and members whose saved
  D2_spread is raised.
- Not run (34): fam_a_r1 29–32 (108×28, Newton), and the 30 members on 144×30 and 162×42 (fam_a_log 51–64,
  fam_a_p4 6–15, fam_a_p4b 0–5). These take `--residual-only`, because their dense Jacobian does not fit in memory.

**Diagnosis** (`diagnose_matter_v0.py` on fam_b_p4_0005 and fam_b_p4b_0019): the defect is entirely in N.
- Setting B = 1 and ψ to its closed form changes nothing; putting back the saved N brings E19/D² down to ~1e-10.
- Re-solved the old way on the same grid (Newton on f and ω, then N and D² by least squares on E_c and E19), the
  member returns the saved N. That N misses the new E_N row by only 3e-9 to 2e-8; the N solved from the row differs
  from it by 7e-9 to 6e-8 and breaks E19.
- |E19| peaks at the mask edge (|η| ≈ 18.7 η₀, C ≈ 0.053), on the y node next to the axis.

**Resolution ladder** (masked E19/D², each member re-solved on each grid from its spectrally interpolated fields):

| member | 48×12 | 60×15 | 72×18 | 84×21 | 96×24 | 108×27 |
|---|---|---|---|---|---|---|
| fam_b_p4_0005 | 5.6e-6 | 8.7e-7 | 2.8e-7 | 4.8e-7 | 3.0e-6 | 6.4e-6 |
| fam_a_r1_0026 | 6.8e-2 | 2.2e-3 | 1.6e-5 | 9.9e-8 | 2.6e-6 | 6.9e-6 |
| fam_b_p4b_0019 | 1.9e-1 | 1.3e-2 | 9.8e-5 | 2.2e-6 | 6.8e-6 | 1.8e-5 |
| fam_a_log_0036 | 1.2 | 2.3e-2 | 8.2e-4 | 3.7e-6 | 8.1e-6 | 2.1e-5 |
| fam_b_p4b_0010 (passes) | 3.7e-4 | 1.2e-10 | 1.8e-10 | 3.2e-10 | 3.2e-10 | 4.6e-10 |

The failing members converge spectrally to ~1e-7 near 84×21, then get worse as the grid grows. The rise follows the
angular resolution: fam_b_p4b_0019 gives 1.6e-6 at 96×18 against 6.8e-6 at 96×24. The continuum rows are proven
(rank 7), so the suspect is the discrete E_N row in the far zone next to the axis, either its truncation or its
conditioning there, amplified by the h-weighted terms of E19. For the passing control, the interpolated saved N
already satisfies the row (Newton takes no step), and the two N agree.

## Next (step 1)

1. Substitute closed-form fields into the discrete E_N row (the standing test for a solver): a smooth N with the
   solutions' axis and far-zone behaviour, with its exact source, read near the axis at |η| ≈ 20 η₀ across the
   72×18 to 108×27 grids. This separates truncation from conditioning and tests the row's near-axis treatment.
2. With that answer, either fix the row and re-run the 27 failures, or, if the elliptic N is the converged one, gate
   step 1 on N's self-convergence and the monitors at the converged grid instead of on 1e-10 against the
   least-squares N.
3. Finish the sweep: fam_a_r1 29–32 with Newton, then the 30 large-grid members with `--residual-only`.
4. Write the step-1 record and tick step 1.

## GPU notes

The step-1 solver can run on the node's H100. Nothing starts on the card without the go.
- **CPU only today**, three ways: the wrapper's `spinning-solver` extra pulls the CPU-only `jax`; the solver sets
  `jax_platforms` from `JAX_PLATFORMS`, default `cpu`; `capped_job.sh` exports `JAX_PLATFORMS=cpu` unless given
  `--gpu`.
- **Where the time goes.** One Newton pass from a saved member, compilation included, on four CPU threads (the
  sweep): 3 s at 48×12, 8–9 s at 72×18, 18–23 s at 96×20, 62–63 s at 108×28. Outside compilation the cost is the
  dense Jacobian (`jax.jacfwd`) and its LU (scipy, on the host). The Jacobian is about 5(n_x+1)(n_y+1) square: 2 GB
  at 108×28, 4 GB at 144×30, 10 GB at 162×42. What overflows on the two largest grids is the unchunked `jacfwd`,
  whose intermediates carry every column at once.
- **The port.** A CUDA build of JAX in the node's venv; `newton.py`'s `lu_factor`/`lu_solve` moved to
  `jax.scipy.linalg`, so the Jacobian stays on the card; the Jacobian built in chunks of columns (chunking alone
  would also let the CPU solve the large grids, at an estimated few minutes per pass). Jobs then run through
  `capped_job.sh --gpu`, after `nvidia-smi`, since the card is shared.
- **Expected, to be measured.** The H100 is fast in float64, which the solver needs, so a pass on the large grids
  should drop from a minute to seconds, and the 30 large-grid members get full Newton solves. The small grids gain
  little, since compilation dominates them, until candidates are batched (the plan's Split card, step 6). It speeds
  up the sweep and the ladders but does not decide which N is right.

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
