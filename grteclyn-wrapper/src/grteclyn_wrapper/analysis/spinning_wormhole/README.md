# Spinning-wormhole background solver

This package computes exact rotating Ellis–Bronnikov wormholes and writes them as `.spinbg`
tables. Those tables are the t = 0 data of the 3D spinning runs (`Examples/SpinningWormhole`).
Plan and execution notes: [`research/spinningwormhole/SpinningSolver.md`](../../../../../research/spinningwormhole/SpinningSolver.md).

## The idea in four steps

1. **Guess** the shape of the spinning wormhole: three unknown functions f, ω and ν on a 2D grid.
2. **Measure** how wrong the guess is: plug it into Einstein's equations and see how far each one
   is from zero.
3. **Fix** the guess: Newton's method says which way to move every number to make the error
   smaller. Repeat until the error is about 1e-12.
4. **Spin it up** a little and repeat, using the last answer as the next guess.

Everything else is plumbing that makes those four steps work:
- the coordinate maps exist because space is infinite;
- dividing by sin θ is there because the axis would otherwise cause divisions by zero;
- the Chebyshev method gives accuracy with few grid points;
- J is the label because ω₋∞ turns back on itself;
- the extra checks exist because the published eq. (12) is misprinted.

## Why it exists

No formula exists for a spinning wormhole; only the static one is known exactly.

Before this solver, the only rotating data was the slow-spin O(J²) approximation.
- Its error grows like J⁴: the Einstein residual is 3e-5 at J = 0.25 and 1e-2 at J = 1.
- The static throat is unstable, so that error acts as a push that picks the outcome. The Step 1
  holds inflated with ε ≈ −3e-5 and −7e-3, which is ×230 for ×4 in J, i.e. J⁴, the size of
  the data's error.
- So that inflation cannot be credited to rotation; spin's own effect there was the throat
  flattening, which grew like J².
- The J = 1 hold on this solver's exact data settles it.

The solver's data is exact to 1e-10 to 4e-10 in Einstein's equations, about 10⁸ times better than
O(J²) at J = 1. On the 3D grid its largest error is the C++ loader's bilinear interpolation of the
table: ~2e-7 at v_e 0.5, ≤ 1e-7 in f up to v_e 0.9, and 2e-6 to 7e-5 at v_e 0.95–0.99. That is
10⁴ times below the old push at v_e 0.5. The near-extremal end wants a bicubic loader.

## How we know the answer is right

The solver imposes only some of Einstein's equations; everything else is checked, never imposed.
- **All of Einstein's equations from scratch** (`check_einstein.py`): the Ricci tensor is rebuilt
  from the metric alone, without CKK's printed equations. It gives 1e-10 to 4e-10, against a 2e-11
  floor on the exact static wormhole; the O(J²) data gives 3e-5 to 1e-2.
- **Quantities that must come out constant:** D² is the same everywhere, the angular-momentum
  flux is the same at every radius, and the Smarr relation μ₊ + μ₋ = 2ω₋∞J holds, all to
  1e-9 or better.
- **Independent of the grid:** the Chebyshev tails are at or below 1e-11, the observables are
  identical to 10 digits on three grids, and the two radial maps agree.
- **Known answers recovered:** the static wormhole to 1e-13, the slow-spin solution up to its
  J⁴ error, CKK's D values for γ = 0 and −1 to every printed digit, the Kleihaus–Kunz 2014
  Fig. 1 curves, and the extremal-Kerr limit (J/R_e² → 1/4, M/R_e → 1/2, D → 0).
- **On the 3D grid at t = 0:** the constraints converge at 4th order inside the throat, and the
  throat radii match the table.

## What is solved

The metric (Chew, Kleihaus & Kunz 2016, arXiv:1608.05253, "CKK"):

    ds² = −e^f dt² + e^{−f} [ e^ν (dη² + h dθ²) + h sin²θ (dφ − ω dt)² ],   h = η² + η₀²

- f is the clock rate and carries the mass; ω is the frame dragging and carries the spin;
  ν sets the shape of the meridian plane and flattens the throat.
- The phantom field is solved by hand: ψ = D (arctan(η/η₀) − π/2), with the scalar charge D
  unknown.
- Boundary conditions: f = ω = ν = 0 at η → +∞; f = γ, ω = ω₋∞, ν = 0 at η → −∞.

Every CKK equation is a piece of Einstein's equations R_ab = −2 ∂_aψ ∂_bψ for this metric:
- **(10) and (11): f and ω, solved together by Newton.** They come from the t–φ block, and
  (11) = −2h e^{ν−f} sin θ · R^t_φ. ν does not appear in them, so they are solved first.
- **(13) and (19): ν and D², as one linear least-squares solve.** (13) = 2h sin θ · R_ηθ, and
  (19) is R_ηη − R_θθ/h = −2ψ_η² solved for D². Both are first order, so they give ν's slopes
  directly, and ν = 0 at both ends fixes ν.
- **(12) is never used.** As printed it fails on extremal Kerr, an exact solution of the
  ansatz, and solving it left a J⁴ constraint violation at every resolution. Derived
  2026-10-13 from −2 sin θ · R_θθ + (10), the correct form is

      ∂η(h sinθ ∂ην) + sinθ ∂θ²ν − cosθ ∂θν + sinθ (∂θf)² − h sin³θ e^{−2f} [ h(∂ηω)² + 2(∂θω)² ] = 0

  The printed (12) has −2(∂θω)² and lacks sinθ (∂θf)². Both errors are invisible at slow spin
  (∂θf ~ J², ∂θω ~ J³), which is why they enter at J⁴. On extremal Kerr the corrected form
  vanishes to 60 digits; the printed one leaves 1e-3 to 5e-2.

## How the code works

**One solve** (`continuation.solve_point`):
1. **Grid:** Chebyshev–Lobatto points in ξ (the radial map of η) and y = cos 2θ. A field is its
   values at the points, and derivative matrices give exact derivatives.
2. **Unknowns:** δf and δω at every point, plus ω₋∞; for example 2,211 numbers at 64×16. The
   fields are f = (γ/2)(1 − ξ) + δf and ω = ω₋∞ q(ξ) + δω, so both corrections are 0 at the
   ends.
3. **Residual:** eqs. (10) and (11) at every interior point, δf = δω = 0 at the ends, and one
   row J(ω) − J_target = 0.
4. **Newton** (`newton.py`): solve Jacobian · du = −residual, where the Jacobian is exact from JAX
   automatic differentiation. Rows are equilibrated, the system is solved by dense LU, steps are
   halved if they do not lower the residual, and the LU is reused while convergence is fast. It
   stops at 1e-12, usually after 3–5 iterations (~2 s).
5. **ν and D²** from (13) + (19) (`CollocationProblem.solve_N_constrained`).
6. **Checks and numbers** (`observables.py`): the identity gates plus M, J, D, v_e, R_eq, R_pol,
   Ω and the throat.

**A family** (`continuation.run_family`): start from the O(J²) solution at small J, then step in
log(J/η₀²).
- Each new guess extends the line through the last two solutions.
- After 3 or fewer Newton iterations the step grows ×1.5; after 7 or more, or a failure, it halves.
- If the Chebyshev tails exceed 1e-11, the grid grows ×1.5 and the same J is solved again.
- Every converged point is saved, so a run can restart from any of them (`seed_npz`).

**The two families:**
- **(a) η₀ = 2, γ = −π:** the merger paper's drainhole (a = 2, M = 1) spun up. This is the
  physics line of the 3D runs. It reaches v_e = 0.9908, the last stretch on the log-stretched
  map.
- **(b) η₀ = 1, γ = 0:** the symmetric family Kleihaus and Kunz published, used for benchmarks
  and the overspin test. It reaches v_e = 0.9907 on the arctan map.

## Where things are

Two folders share the name `spinning_wormhole`:

- **This package** (`grteclyn-wrapper/src/grteclyn_wrapper/analysis/spinning_wormhole/`) is the
  solver library, imported by everything else:
  - `spectral.py`: the grid points, derivative matrices, radial maps (arctan, log-stretch),
    Chebyshev coefficients and tail check;
  - `equations.py`: `residual_forms`, the one place the equations are written, and
    `CollocationProblem`, the discrete system with its residual, Jacobian, J flux and ν solve;
  - `newton.py`: the damped Newton solver;
  - `continuation.py`: one solve (`solve_point`) and a whole family (`run_family`);
  - `solution.py`: the `Solution` container, with save/load and evaluation anywhere;
  - `observables.py`: the physical numbers and identity gates;
  - `conventions.py`: every sign and normalisation;
  - `backgrounds.py`: the `.spinbg` writer, static and O(J²) generators, and `full` for a
    solver `Solution`.
- **`grteclyn-wrapper/scripts/analysis/spinning_wormhole/`** holds the command-line tools that use
  it:
  - `solve_family.py`: runs a family;
  - `check_einstein.py`: the full-Einstein check;
  - `derive_xy_equations.py`: the symbolic proof that the solver's equations equal CKK's, and the
    extremal-Kerr regression;
  - `t0_checks.py`: the 3D t = 0 checks;
  - the O(J²) and Azad checks.

Outputs: the solver's saved solutions and the 15 tables live in `runs/spinning_p3/`, which is
untracked. Every solution's numbers are packed in `results/spinningwormhole/solver/solutions.tsv`.

## The `.spinbg` table

- **Header:** a text header with `SPINBG_V1`, η₀, the grid sizes, the x range, the component
  names, and `meta` provenance lines (the solution, grid, map, J, ω₋∞, D, v_e, gate values and
  the measured interpolation error).
- **Body:** float64 [n_μ][n_x][6] on a uniform grid in x = (2/π) arctan(η/η₀) ∈ [−1, 1] and
  μ = cos θ ∈ [0, 1].
- **Columns:** f, ν/sin²θ, ω, ∂ηω, (∂θω)/sin θ, and φ, the phantom field in the evolution's
  normalisation.
- **Use in C++:** `Examples/SpinningWormhole/SpinningWormholeInitialData.hpp` turns it into
  α = e^{f/2}, β^φ = −ω, the spatial metric, a traceless K_ij and Π = 0.

## Running

From the repo root, on the CPU, with a memory cap (CLAUDE.md, "Environment"):

    (ulimit -v 67108864; grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/solve_family.py \
        --eta0 2 --mass 1 --j-start 0.25 --ve-stop 0.9 --out <dir> --name fam_a)

    grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.analysis.spinning_wormhole.backgrounds \
        full <solution.npz> --n-x 2049 --n-mu 129 --out <table.spinbg>
