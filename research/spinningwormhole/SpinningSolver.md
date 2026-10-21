# Fast-spin Ellis–Bronnikov solver: execution plan

Build a Python pseudo-spectral Newton solver for the two Ernst fields (f, ω) in the existing Kleihaus–Kunz gauge, then get ν and D from linear solves. It feeds the existing `SPINBG_V1` tables, so nothing in the C++ changes. Every equation below was machine-checked against CKK eqs. 10–13 and 19 (`derive_xy_equations.py`, max relative difference 2e−41 at 40 digits on generic test fields).

The test that decides success is in 3D, not in the solver. STATUS shows that the O(J²) data's own J⁴ error acts as a radial kick (ε ≈ −7e−3 at J = 1) that picks the throat's branch. With full data, the J = 1 hold must fall to the static hold's truncation floor.

Order of work: P0 → P1 → P2 (**M1**, first validated solution) → P3 (**M2**, both families at v_e ≈ 0.9) → P4 (**M3**, v_e ≥ 0.95). P5 (tables and 3D acceptance) starts at M1 and runs beside P3–P4. Each phase starts only when the previous gate passes.

---

## 1. Goal and acceptance criteria

The solver is done when both families pass every row from v_e = 0 to at least 0.95. Thresholds are proposals; P1 measures the round-off floor and may move them by an order of magnitude.

| Criterion | Threshold | Measured by |
|---|---|---|
| Coverage | family (a) η₀ = 2, γ = −π and family (b) γ = 0, both v_e 0 → ≥ 0.95 (0.99 stretch) | continuation log |
| Full-Einstein residual | ≤ 1e−8, or the check's round-off floor if higher; never above 1e−6 | generalized `check_slowspin_einstein.py` (independent sympy Ricci) |
| Internal identities | D² spread ≤ 1e−9, constraint ≤ 1e−9, J-flux spread ≤ 1e−10, Smarr ≤ 1e−10 (all relative) | `observables.py` on every solution |
| Spectral convergence | last 3 Chebyshev coefficients ≤ 1e−11 of the largest, per field and direction | tail monitor |
| Benchmarks | CKK D anchors to 5 digits; agreement with O(J²) scaling as J⁴ | P2–P3 |
| Runtime | ≤ 5 min per solution on one CPU workstation | wall clock |
| Table fidelity | bilinear table vs spectral value ≤ 1e−7 in f | midpoint sampling |
| 3D acceptance | J = 1 hold kick at the static hold's floor; t = 0 L2_Ham ≤ 2.5e−3 at L64 ml3 | GRTeclyn hold run |

---

## 2. Formulation

Solve (f, ω) nonlinearly; N = ν/sin²θ and D² then follow without iteration. The printed eq. 12 (E_N below) is wrong: the production solver takes N and D² from E_c and D² instead (execution notes, 2026-10-12).

**Coordinates.** x = (2/π) arctan(η/η₀) as now, and y = cos 2θ, with C = cos(πx/2) and S = sin(πx/2). Since cos(2kθ) = T_k(y), the planned even cosine basis is Chebyshev in y. The axis is y = 1 and the equator y = −1. Regularity and equatorial symmetry are built in, so y needs no boundary rows. N is exactly the table's `nu_bar`.

**Nonlinear system** (eq. 10 = sin θ · E_f, eq. 11 = h sin³θ e^{−2f} · E_ω):

$$
E_f:\quad \frac{4}{\pi^2}C^2 f_{xx} + 4(1-y^2) f_{yy} - (6y+2) f_y - \eta_0^2\,\frac{1-y}{2}\,e^{-2f}\Big[\frac{4}{\pi^2}\omega_x^2 + \frac{4(1-y^2)}{C^2}\omega_y^2\Big] = 0
$$

$$
E_\omega:\quad \frac{4}{\pi^2}\big[C^2(\omega_{xx}-2f_x\omega_x) + \pi S C\,\omega_x\big] + 4(1-y^2)\omega_{yy} - (10y+6)\omega_y - 8(1-y^2) f_y\omega_y = 0
$$

**Linear solve for N** (eq. 12 = sin³θ · E_N). Its operator is negative definite (angular eigenvalues −[2k(2k+3) + 2]), so it always inverts:

$$
E_N:\quad \frac{4}{\pi^2}C^2 N_{xx} + 4(1-y^2)N_{yy} - (10y+6)N_y - 2N - \eta_0^2 e^{-2f}\Big[\frac{4}{\pi^2}\omega_x^2 - \frac{8(1-y^2)}{C^2}\omega_y^2\Big] = 0
$$

**Monitored, never imposed** (eq. 13 = (2η₀/π) sin²θ cos θ · E_c; D² is eq. 19 rewritten):

$$
E_c:\quad 4f_xf_y + N_x + \frac{\pi S}{C}\big(N-(1-y)N_y\big) - \frac{2\eta_0^2(1-y)}{C^2}e^{-2f}\omega_x\omega_y = 0
$$

$$
\frac{D^2}{\eta_0^2} = 1 + \frac{f_x^2}{\pi^2} - \frac{(1-y^2)f_y^2}{C^2} - \frac{S(1-y)}{2\pi C}N_x + \frac{(1+y)N-(1-y^2)N_y}{2C^2} - \frac{(1-y)\eta_0^2}{2C^2}e^{-2f}\Big[\frac{\omega_x^2}{\pi^2} - \frac{(1-y^2)\omega_y^2}{C^2}\Big]
$$

The 1/C² factors amplify round-off near x = ±1, so the gates use nodes with C ≥ 0.05; the full-grid value is logged alongside.

**Boundary conditions.** At x = +1: f = ω = N = 0. At x = −1: f = γ, ω = ω₋∞, N = 0. At x = ±1 the operators degenerate (C = 0) and force f and ω to be θ-independent there, consistent with the Dirichlet data.

**Observables, in exact integral form** (μ = cos θ):

- J(x) = −(η₀³ / 4πC²) ∫₋₁¹ (1 − μ²) e^{−2f} ω_x dμ. It is the conserved flux of eq. 11, constant in x and equal to J₊. On the O(J) profile it returns J exactly.
- μ₊ = (η₀/π) f_x(+1) and μ₋ = −(η₀/π) f_x(−1), in CKK's eq. 17 sign convention. The Komar function (η₀/2π) ∫₋₁¹ f_x dμ runs from −μ₋ to μ₊. Smarr: μ₊ + μ₋ = 2ω₋∞J₊ (CKK eq. 28).
- v_e = R_eq · Ω_throat at the area-minimising η = const surface, as `_throat_numbers` does now; R_eq = e^{−f/2}√h on the equator.
- Ergosurface: e^{−f} h sin²θ ω² = e^f.
- Table columns: ∂_ηω = (2C²/πη₀) ω_x, (∂_θω)/sin θ = −4μ ω_y, φ = (D/η₀)(π/2)(x − 1)/√(4π).

---

## 3. Discretization and Newton solver

Use tensor Chebyshev–Lobatto collocation in (x, y), Newton on (f, ω) with an exact JAX Jacobian, then one linear solve for N. At the planned sizes a dense LU is affordable, so the first version needs no preconditioning or sparse machinery.

- **Grid.** N_x + 1 Lobatto nodes in x (start at 64, grow to 128 or more) and N_y + 1 in y (start at 16, grow to 32). That is 2,210 unknowns at 64 × 16 and 8,514 at 128 × 32.
- **Rows.** Dirichlet rows at x = ±1 for every y. The PDE everywhere else, including y = ±1, where its coefficients stay regular.
- **Unknown split.** f = (γ/2)(1 − x) + δf and ω = ω₋∞ q(x) + δω, with q = w₁/w₁(−∞) from `slow_rotation_omega`. The corrections then carry zero boundary data, and q already has the η⁻³ tails at both ends.
- **The radial map is a parameter.** The residual takes η(ξ), η′(ξ), η″(ξ) at the nodes; the arctan map is the default. This keeps P4's stretched grids a configuration change, not a rewrite.
- **Jacobian and linear algebra.** Residual in JAX with float64 (`jax_enable_x64`) under `jit`; Jacobian by `jax.jacfwd`; row equilibration; `scipy.linalg.lu_factor`. Dense works to about 10k unknowns (about 0.6 GB at 8.5k). Beyond that, assemble the Kronecker form, which has about 2(N_x + N_y) nonzeros per row, and use `scipy.sparse.linalg.splu`.
- **Newton control.** Armijo backtracking on ‖R‖₂. Converged at ‖R‖∞ ≤ 1e−12 after scaling each equation by its operator norm; at most 12 iterations. Reuse the factorization (chord steps) while the contraction ratio stays below 0.1.
- **Resolution control.** After each solve, compute the tail ratio (largest of the last 3 Chebyshev coefficients over the largest coefficient) per field and direction. Above 1e−11, raise that N by 1.5× and re-seed by spectral interpolation.
- **Evaluation anywhere.** Barycentric interpolation in x and y (move `_cheb` and `_cheb_eval` out of `backgrounds.py`), with derivatives from the differentiated series. Table columns and the Einstein check then get exact derivatives.

---

## 4. Continuation along fixed-γ families

Label solutions by J, not ω₋∞. CKK find that ω₀ (and so ω₋∞) turns over along a family, giving two branches, while J grows without bound as v_e → 1. Prescribing J steps straight past that turning point. J's own monotonicity is checked, not assumed.

- **Bordered system.** Make ω₋∞ an unknown and add one equation, J(x = 0) − J_target = 0, evaluated with Gauss–Legendre in μ (exact for the polynomial integrand). The Jacobian gains one row and one column. This also makes the P2 comparison with O(J²) an equal-J comparison, which is how that generator is labelled.
- **Stepping.** Step in log(J/η₀²), the scale-free spin. Predict with a secant through the last two solutions, or a tangent from the existing factorization. Grow the step 1.5× after ≤ 3 Newton iterations; halve it after ≥ 7 or a failure; stop and report below a step of 1e−4.
- **Fold guard.** Track the sign of the Jacobian determinant from the LU diagonal, and the slope dω₋∞/dJ. If J itself folds, switch to pseudo-arclength continuation in (state, J).
- **Family (a).** η₀ = 2, γ = −π, seeded from O(J²) at J = 0.25 and continued upward.
- **Family (b).** γ = 0 at η₀ = 1 (CKK's normalization), seeded from O(J²) at small J. Rescaling to the evolution's normalization happens only when tables are written.
- **Anchor runs.** Short families at η₀ = 1 with γ = 2, 1, −1, taken only as far as ω₋∞ = 0.5. Each ω₋∞ has two solutions there. Record both; the one matching CKK's D fixes which is their "upper branch".
- **Persistence.** Save every converged step (coefficients `.npz` plus a JSON of observables and gate values), so any J can be re-seeded or re-tabled without re-running the family.

---

## 5. Near-extremal strategy (v_e 0.9 → 0.99)

Choose the grid by measurement: run the single-domain arctan grid until its tails fail, then switch. The switch point and the N needed at 0.95 and 0.99 are unknown today and become results of P4.

**Why it gets hard.** At fixed η₀ the mass grows without bound as v_e → 1, so two scales separate: the throat η₀ and the Kerr scale M. In x, the region η₀ ≲ |η| ≲ M is squeezed into a layer of width about η₀/M at each end, where the near-horizon structure varies roughly like log η. Monitor along the family: log M/η₀, the tail ratios, Newton iteration counts and D.

Three options, in the order to try:

1. **More nodes.** Lobatto nodes already cluster as 1/N² at x = ±1, so raising N_x may carry 0.95 alone. No code change; the sparse path past about 10k unknowns.
2. **Log-stretched single domain.** ξ = tanh(asinh(η/η₀)/L) with L = 2k, k an integer. L = 2 gives ξ = η/(η₀ + √h), equivalent in character to the arctan map. For even L, 1/η stays analytic in (1 − ξ), so spectral convergence at the ends survives, while nodes spread evenly in log η out to η ≈ η₀ e^{2L}/2. This map is our derivation; P0's script verifies it.
3. **Three domains.** Split at |η| = η_c = √(η₀M): an inner arctan domain on [−η_c, η_c] and two outer domains compactified in η_c/η, with value and normal derivative matched at the interfaces. Most reliable, most code.

**Physics checks in this regime.** D falls monotonically to 0. For γ = 0, μ₊/R_e → 1/2, J/R_e² → 1/4 and Q/R_e³ → 1/8. The polar Gaussian curvature of the throat turns negative near v_e = 0.9 (CKK §III.D). Use 1/4 for J/R_e², not the brief's 1/2: Volkov 2026 §X finds CKK's figure matches only if it plots 2J/R₀², and extremal Kerr with R_e = 2M gives J/R_e² = M²/4M² = 1/4.

If 0.99 cannot pass the gates, stop at the highest v_e that does and say so, as the paper plan's Step 5 already allows. The same two-scale throat will set the AMR depth of the 3D runs, so record the measured layer width.

---

## 6. Code layout in grteclyn-wrapper

New modules sit beside `backgrounds.py` in `src/grteclyn_wrapper/analysis/spinning_wormhole/`. `write_spinbg` and the table format stay untouched.

| File | Holds |
|---|---|
| `spectral.py` | Lobatto nodes, differentiation matrices, transforms, tail ratio, radial maps; `_cheb` and `_cheb_eval` move here |
| `equations.py` | JAX residuals E_f and E_ω, the linear E_N operator, E_c and D² diagnostics, all for a generic radial map |
| `newton.py` | damped Newton, the bordered J system, dense/sparse switch |
| `continuation.py` | family driver, predictor, step control, fold guard, arclength fallback |
| `observables.py` | μ±, J(x), D, ω₀, ω₋∞, throat by area minimum, R_eq, R_pol, R_A, Ω, v_e, Q, ergosurface, polar curvature; generalizes `_throat_numbers` to θ-dependent ω and ν |
| `solution.py` | `Solution` dataclass: parameters, map, coefficients, `eval(eta, theta, derivs)`, `.npz` + JSON save/load |
| `backgrounds.py` | new `full` subcommand that writes a `.spinbg` from a saved `Solution` |

Scripts in `scripts/analysis/spinning_wormhole/`:

- `derive_xy_equations.py`: the symbolic check behind section 2, extended to emit coefficients for any radial map.
- `solve_family.py`: runs a family and writes its catalogue under `results/spinningwormhole/backgrounds/<family>/`.
- `check_einstein.py`: `check_slowspin_einstein.py` generalized. Its `ricci_lambdas` already take general f, ν, ω of (η, θ). Only `residuals` assumes slow spin (w_01 = w_02 = w_11 = 0, ν = n(η) sin²θ); feed it jets from `Solution` instead.

Tests go in `tests/spinning_wormhole/`: static exactness, manufactured solutions, J⁴ scaling, identities, γ = 0 mirror symmetry and a table round trip. New dependency: `jax` (CPU, float64); the rest is already used.

---

## 7. Phases, tasks and gates

### P0 · Lock the formulation

- [ ] Commit `derive_xy_equations.py`; extend it to emit operator coefficients for a generic radial map, and verify the log-stretched map's end analyticity
- [ ] One conventions module (μ±, J±, D, v_e, R_eq, γ, ω₋∞) with unit tests on the static member
- [ ] Add `jax` (CPU, x64) to the wrapper's environment

**Gate:** forms match CKK to ≤ 1e−30 at 40 digits (done: 2e−41); the static members satisfy E_f, E_ω, E_N, E_c and D² exactly.

### P1 · Core solver

- [ ] `spectral.py`, `equations.py`, `solution.py`
- [ ] Linear E_N solver, with a manufactured-solution test
- [ ] Newton on (f, ω) with ω₋∞ prescribed (simplest form first)
- [ ] Manufactured-solution test of the full nonlinear system, with matching boundary data and a source term
- [ ] Static drainhole and γ = 0 static recovered from a perturbed guess

**Gate:** manufactured errors fall exponentially in N_x and N_y to ≤ 1e−12; static members to ≤ 1e−13; one solve at 64 × 16 in under 30 s.

### P2 · First validated solution → M1

- [ ] Seed from `slow_rotation_solution`: f₀ + J²(A + B P₂), ω = J w₁, N = J² n, with P₂ = (3y + 1)/4
- [ ] Bordered J system
- [ ] `observables.py` with every identity in the validation matrix
- [ ] `check_einstein.py`, with its round-off floor measured on the static member
- [ ] J⁴ test on the drainhole at J = 0.05, 0.1, 0.2, 0.4: ‖f − f_O(J²)‖/J⁴ and ‖N − N_O(J²)‖/J⁴ constant within 5 %, ‖ω − J w₁‖/J³ likewise
- [ ] Drainhole at J = 1 (v_e ≈ 0.24): compare M_ADM 1.128, D 2.196, Ω_throat 0.0587, R_eq 4.087, ω₋∞ 0.0936; differences should match the size of the O(J²) error
- [ ] Write the first full table with `backgrounds.py full`

**Gate (M1):** all identities pass; full-Einstein residual ≤ 1e−8 (against 1e−2 for O(J²)); J⁴ scaling confirmed.

### P3 · Continuation to v_e ≈ 0.9 → M2

- [x] `continuation.py`
- [x] Family (b): mirror symmetry f(x) = f(−x), ω(x) + ω(−x) = ω₋∞, ω₀ = ω₋∞/2 to 1e−12, checked and not imposed; ergoregion onset at v_e = 1/2; the ergosurface law arctan(η_ergo/η₀) = arccos(2ω₀) (identities at 1e−14; law exact once η_ergo > 0)
- [x] Anchor runs: D = 0.33984, 0.43155, 0.55277, 0.71636 for γ = 2, 1, 0, −1 at η₀ = 1, ω₋∞ = 0.5 (γ = 0, −1 to all their digits; γ = 1, 2 grid-converged on our side, offsets 2e−4 and 7e−3 are their error — see execution notes)
- [x] Family (a) to v_e ≈ 0.9 (0.9087)
- [x] Resolution study at v_e = 0.5 and 0.9 (10 digits across three grids)

**Gate (M2): PASSED 2026-10-13** — both families at v_e ≥ 0.9 with every gate green along the path; anchors: two matched to all five CKK digits, two grid-converged against CKK values whose own error grows with γ (adjudicated by the absent third crossing; execution notes).

### P4 · Near-extremal → M3

- [x] Pick option 1, 2 or 3 of section 5 at the first tail failure; implement it (option 1 carried family (b) to 0.99 outright; family (a)'s arctan grid failed at v_e 0.961 — tails 1.5e−11, the 244×64 refinement over the memory cap — and option 2, the log-stretch map with L = 4, carried it to 0.99 on 144×30)
- [x] Overlap check: the last two arctan-grid solutions re-solved on the new grid agree to ≤ 1e−10 (ω∞ at 1e−10; M, D, R_eq at 1e−8–1e−9, the stored-precision/tail floor of those stretched arctan endpoints)
- [x] Extremal trends: D → 0 (family (a): 2.23 → 0.325; family (b): 0.99 → 0.408, monotone), μ₊/R_e → 1/2 (γ = 0: 0.487 at v_e 0.991), J/R_e² → 1/4 (0.2458 — confirming Volkov's 1/4 over the brief's 1/2); polar curvature sign change near 0.9 NOT yet computed (needs the throat-surface curvature formula; small follow-up)
- [x] Record the N needed at v_e = 0.95 and 0.99: family (b) 72×18 at both; family (a) 162×42 (arctan) at 0.95, 144×30 (log, L = 4) at 0.99

**Gate (M3): PASSED 2026-10-13** — v_e = 0.9500/0.9521 and 0.9908/0.9907 on families (a)/(b) with every P2 gate green (tails ≤ 5e−14 at the endpoints); 0.99 reached.

### P5 · Tables and 3D acceptance (starts at M1, runs beside P3–P4)

- [x] Table resolution study: choose n_x, n_mu so bilinear interpolation stays ≤ 1e−7 in f (met through v_e ≈ 0.9: 2049 × 129 at v_e 0.5 up to 8193 × 513 at 0.9; beyond that even 8193 × 513 leaves 2e−6 (a, 0.95) to 7e−5 (a, 0.99) — the bicubic-loader case; every table's meta records its measured error)
- [ ] 3D J = 1 hold with full data, set up like `spin_hold_L64_ml3_J100_t100`; compare its kick ε with the O(J²) run's −7e−3 and with the static hold (GPU — awaiting the go)
- [ ] t = 0 constraint convergence at three resolutions for v_e ≈ 0.5 (GPU — awaiting the go)
- [x] Production catalogue tables for both families (section 9): 15 tables in `runs/spinning_p3/tables/` (v_e 0.5–0.99 each family + family (b)'s ergoregion-onset pair), 2.1 GB

**Gate:** the J = 1 kick sits at the static hold's floor; t = 0 L2_Ham is no worse than the static hold's.

---

## 8. Validation matrix

Every saved solution carries the per-solution rows in its JSON; the phase rows run once. The checks are independent of the solve: the solver imposes only E_f, E_ω, E_N and the boundary data, so everything else tests it.

| Check | Threshold | When | Basis |
|---|---|---|---|
| (x, y) forms against CKK 10–13, 19 | ≤ 1e−30 rel at 40 digits | P0 (done, 2e−41) | `derive_xy_equations.py` |
| Static members exact | ≤ 1e−13 | every build | exact solution |
| Manufactured solution | exponential decay to ≤ 1e−12 | P1 | test suite |
| Newton residual ‖R‖∞ | ≤ 1e−12 | every solution | solver |
| Chebyshev tails | ≤ 1e−11 | every solution | tail ratio |
| D² constancy (nodes with C ≥ 0.05) | spread ≤ 1e−9 rel | every solution | CKK eq. 19 |
| Constraint E_c, over the sum of its term magnitudes | ≤ 1e−9 | every solution | CKK eq. 13 |
| J(x) constancy across x | spread ≤ 1e−10 rel | every solution | flux of CKK eq. 11 |
| Smarr μ₊ + μ₋ − 2ω₋∞J₊ | ≤ 1e−10 rel | every solution | CKK eq. 28 |
| Full-Einstein residual | ≤ 1e−8 or the static floor | every catalogue entry | independent sympy Ricci |
| Equal-J agreement with O(J²) | f, N ∝ J⁴; ω − Jw₁ ∝ J³; ratios within 5 % | P2 | `backgrounds.py slowspin` |
| γ = 0 mirror symmetry | ≤ 1e−12 | family (b) | CKK symmetric family |
| D anchors at η₀ = 1, ω₋∞ = 0.5 | 5 digits | P3 | CKK |
| Ergoregion onset and ergosurface law | onset at v_e = 1/2; deviation reported | P3 | CKK eq. 62, Fig. 7 |
| Extremal trends μ₊/R_e, J/R_e², Q/R_e³, D | → 1/2, 1/4, 1/8, 0 | P4 | CKK §III; Volkov 2026 §X |
| Polar Gaussian curvature | negative beyond v_e ≈ 0.9 | P4 | CKK §III.D |
| Table against spectral evaluation | ≤ 1e−7 in f | every table | midpoint sampling |
| 3D J = 1 hold | kick at static floor; L2_Ham ≤ 2.5e−3 | P5 | STATUS, Step 1 |

---

## 9. Integration with GRTeclyn

A `Solution` becomes a `.spinbg` through the existing `write_spinbg`, so `RotatingBackgroundTable.hpp` and `SpinningWormholeInitialData.hpp` stay as they are. The six columns come from section 2's table formulas, evaluated spectrally on the uniform (x, μ) grid.

- **Rescaling at write time.** The solver works at fixed η₀ per family. Under η → λη: f, N, φ and x are unchanged; ω → ω/λ, ∂_ηω → ∂_ηω/λ², (∂_θω)/sin θ → (∂_θω)/(λ sin θ), D → λD, and the header's `eta0` becomes λη₀.
- **Table size.** Bilinear error grows like Δx² f_xx, and f_xx steepens near x = ±1 at high spin. Size each table by measured midpoint error, not by default. If the uniform grid grows unreasonable near extremality, bicubic interpolation in the loader is the follow-up, outside this plan.
- **Provenance.** Each table's `meta` lines carry the solver commit, N_x × N_y, the radial map, J, ω₋∞, D, v_e and every gate value, so a run directory alone shows what data it used.
- **Catalogue.** Per family: the paper plan's slow-spin points (J/J_max = 0, 0.05, 0.1, 0.2, 0.3, 0.4), dense sampling around J_max/3, then v_e = 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, and 0.99 if reached. For γ = 0, add points either side of the v_e = 1/2 ergoregion onset.
- **3D acceptance protocol.** One J = 1 hold on the Step 1 grid; t = 0 constraints at three resolutions at v_e ≈ 0.5; ADM M and J from the 3D data against μ₊ and J₊; R_eq and R_pol at t = 0 against the background.

---

## 10. Risks and mitigations

| Risk | Early sign | Mitigation |
|---|---|---|
| Two-scale near-extremal solution | tails rise with v_e at fixed N | section 5 options 1 → 3; report the highest v_e that passes |
| J not monotone along a family | determinant sign flip, dω₋∞/dJ blows up | pseudo-arclength in (state, J) |
| Log terms in the asymptotics | algebraic, not exponential, tail decay in x | subtract the known falloffs, or use the stretched map |
| Weak non-smoothness at the throat ring (η = 0, θ = π/2), where the Weyl form is singular | y-tails concentrate near the equator | map in y; the KK gauge is expected regular, as CKK solve there |
| Newton stalls far from the seed | step size collapses | tangent predictor; homotopy in γ from the symmetric family |
| Dense LU too large | memory above about 1 GB | sparse Kronecker assembly with `splu` |
| Table interpolation dominates the error | midpoint check fails before the solver's | finer table; bicubic loader later |
| Convention slips (μ sign, J factor 2, η₀ factors) | identities fail on static or O(J²) members | one conventions module; no hand-transcribed equations |
| Round-off floor of the Einstein check | residual stalls as N grows | measure the floor on the static member; quote residuals against it |

---

## Execution notes

**2026-10-12 (P0-P2 done, M1 passed).** The published eq. (12) is wrong:
closed-form extremal Kerr (a = M, eta0 = 0, which fits the ansatz exactly)
satisfies eqs. (10), (11), (13) and (19) exactly but leaves ~1e-2 in the
printed eq. (12), and solutions of the printed elliptic system carry a
J^4-sized violation of (13)/(19) at every resolution (first seen as
D^2 spread 5.5e-7 at J = 0.25).  The production solver therefore imposes
(10), (11) by Newton and obtains N and D^2 jointly from the CONSTRAINTS
(13) + (19) as one linear least squares (`solve_N_constrained`); the
printed eq. (12) is a reported diagnostic only, and
`derive_xy_equations.py --stage kerr` keeps the finding as a regression
check.  Measured gates at 64 x 16: D^2 spread 1.4e-12, E_c <= 1.3e-9,
J-flux spread <= 1.3e-9 (floors, C >= 0.05), Smarr <= 9e-11, tails <=
5e-12; independent full-Einstein residual (masked) 1.0e-10 at J = 0.25
and 4.2e-10 at J = 1 against the static member's 2e-11 floor; the O(J^2) data give 3e-5
and 1e-2.  J^4 agreement with the O(J^2) generator:
ratios constant to 1 %.  First table written (1025 x 65, midpoint error
in f 1.8e-7, just above the 1e-7 target; P5 sizes the grid).

**2026-10-13 (P3 done, M2 passed).** Both families reached the target on
CPU (48 x 12 auto-refining to 108 x 28 along the way): family (a)
(eta0 = 2, gamma = -pi) to v_e = 0.9087 at J = 169, M = 12.9; family (b)
(eta0 = 1, gamma = 0) to v_e = 0.9060.  Every gate green along both paths
(tails <= 5e-12 at acceptance, E_c <= 1e-9, D^2 spread <= 1e-11).
Family-(b) identities hold to machine precision along the family:
mirror defects and omega(0) = omega_inf/2 at 1e-14..1e-15; the CKK
equatorial-ergosurface law is satisfied to 1e-12 once the surface sits
at eta > 0 (v_e >= 0.77).  Resolution study at v_e = 0.51 and 0.90
(family a): D, M, R_eq, omega_inf identical to 10 digits across three
grids up to 240 x 60.

CKK anchors (eta0 = 1, omega_inf = 0.5): every omega_inf is reached
twice along a family (rise, turnover, descent); CKK's table is the
post-turnover branch.  Our exact solves there, each grid-converged:
gamma = 0: D = 0.552771 (CKK 0.55277, 1.4e-6); gamma = -1: 0.716368
(0.71636, 1.2e-5); gamma = 1: 0.43146543 (8 digits stable vs their
0.43155, 2e-4); gamma = 2: 0.3375993 (7 digits stable vs their 0.33984,
6.6e-3).  No third omega_inf = 0.5 crossing exists (the gamma = 2 family
was continued to J = 172 with omega_inf falling monotonically to 0.14),
so the two positive-gamma offsets are their finite-difference error,
growing with gamma into the relativistic regime (their points sit at
v_e > 1).  The lower (pre-turnover) branch at omega_inf = 0.5 is new
data: D = 1.048161, 1.008136, 0.986013, 0.969194 for gamma = 2, 1, 0,
-1.  The slow-spin seed only converges near its regime: positive-gamma
families need j_start well below eta0^2 omega_target/w1(-inf) (gamma = 1
at J = 0.05 stalls; J = 0.01 walks in cleanly).

**2026-10-13 (P4 done, M3 passed).** Family (b) never left the arctan
map: 72 x 18 carried it through v_e = 0.9907 (tails 4.7e-12), with the
Kerr-limit ratios closing in (J/R_e^2 = 0.2458 -> 1/4, M/R_e = 0.487 ->
1/2, D monotone to 0.408) -- also settling Volkov's 1/4 normalisation
for CKK Fig. 2.  Family (a) is the two-scale case: the arctan grid
failed at v_e 0.961, as section 5 expected (tails 1.5e-11 at 162 x 42, the 244 x 64
refinement's Jacobian over the 64 GB cap), and the section-5 option 2
log-stretch map (L = 4) retraced the family from J = 0.25 and carried
it to v_e = 0.9908 at J = 19413, M/eta0 = 70, on a 144 x 30 grid with
tails 4.9e-14: the two-scale layer needs the map, not more
nodes.  Overlap between maps at the last two arctan points: omega_inf
to 1e-10, M, D, R_eq to 1e-8..1e-9 (their own floor).  Observables mass
read-off is map-generic (far-field mu at the first interior node;
the arctan end-node formula kept as the exact special case).  The
retrace doubles as a full-family cross-map check: every shared J agrees
at the same level.  Open P4 item: the polar-curvature sign change near
v_e 0.9 (CKK III.D) still needs the throat-surface curvature formula.
The measured two-scale layer width (for the 3D AMR depth): at
v_e 0.99, M/eta0 = 70, so the layer eta0/M ~ 0.014 of the Kerr scale.

Ops notes: runs continue across wall-time cuts via
`run_family(seed_npz=...)` (exact restart from any saved point, verified
in production); jax honours JAX_PLATFORMS (CUDA build installed; GPU
reproduces CPU to all printed digits but XLA GPU compile dominates at
P3 sizes, so GPU is reserved for P4 grids); near the extremal end at
nx = 192 the tails grow past the gate (4e-9 at v_e 1.03, gamma = 2) --
exactly the P4 two-scale regime, section 5 options apply.  Outputs
mirror to `runs/spinning_p3/` (untracked).

---

## 11. Parallel track: data request to Oldenburg

Send now, as a cross-check only; nothing in the plan waits for a reply. Their finite-difference data (constraint norms around 1e−4 to 1e−3 in the group's related papers) cannot replace ours, but an independent family is useful in P3.

To: Burkhard Kleihaus, Jutta Kunz, Fech Scen Khoo (Oldenburg); cc Jose Luis Blázquez-Salcedo (Madrid). Addresses as on the Khoo et al. 2024 title page.

> **Subject:** Rotating Ellis–Bronnikov backgrounds for 3D nonlinear evolutions
>
> Dear Prof. Kunz, Dr. Kleihaus and Dr. Khoo,
>
> I evolve Ellis–Bronnikov wormholes nonlinearly in 3+1 (arXiv:2604.00071) and am now extending this to rotating ones, from slow spin to near-extremal Kerr. I am building a spectral solver for your quasi-isotropic ansatz and would value your backgrounds as an independent check.
>
> Would you be willing to share, in any format: (1) the symmetric family at η₀ = 1 across both ω₀ branches, up to v_e ≈ 0.95, as f, ν, ω on your grid; (2) any non-symmetric family, ideally near γ = −π; (3) your grid sizes and accuracy; (4) whether CKK's Fig. 2 plots J/R_e² or 2J/R_e², as Volkov's 2026 paper suggests; (5) whether an erratum exists for CKK's eq. (12) — in our tests extremal Kerr in your ansatz satisfies eqs. (10), (11), (13) and (19) exactly but not the printed (12), and we instead fix ν from (13) and (19); and (6) your estimated accuracy for the γ = 1 and γ = 2 scalar charges at ω∞ = 0.5 (upper branch) — our grid-converged spectral values are D = 0.4314654 and 0.3375993 against CKK's printed 0.43155 and 0.33984, while γ = 0 and γ = −1 agree to all printed digits? I will cite and acknowledge the data, and share our solutions and 3D results.
>
> Best regards,
> [name]

---

## 12. Decisions needed

None of these blocks P0–P2; the first two must be settled before the P5 catalogue is written.

1. **What stays fixed across the 3D catalogue:** η₀ (as now, so M_ADM grows with spin and the box and AMR must grow too), or M_ADM, or R_eq. Tables can be rescaled either way.
2. **Which scaled J the predicted mode merger at J_max/3 refers to** (Azad et al.'s definition). It sets where the catalogue is sampled densely.
3. **Residual threshold:** keep 1e−8, or relax to 1e−6 if P1 shows a higher round-off floor.
4. **JAX as a dependency:** faster to write with an exact Jacobian; the alternative is a hand-assembled numpy Jacobian with no new dependency.