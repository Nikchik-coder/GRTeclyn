# BinaryWormholeMerger

Merger of **two phantom-supported Ellis–Bronnikov wormhole throats** — the binary
generalisation of `Examples/SupportedWormholeCollapse`, built on the two-body
conventions of `Examples/BinaryBH`. Governing plan:
`research/merger/Plan.md`, with the prior art and file-by-file design in
`research/merger/Reference.md` (both kept out of the public tree).

## The one piece of physics you need to know

A *massless* Ellis–Bronnikov throat is **ultrastatic**: its lapse is exactly 1
everywhere, so all of its curvature sits in the spatial metric. It bends light,
but a mass at rest feels no pull at any distance — the phantom scalar's negative
energy exactly cancels the positive field energy, so ψ has no 1/r piece and
M_ADM = 0. Two such throats released from rest **never fall together**.

`wormhole_bare_mass_A/B` adds the puncture-like m/(2r) piece of the *massive*
drainhole branch. Each throat then carries M_ADM ≈ m and the pair genuinely
attracts: released from rest for a head-on merger, or with transverse
Bowen–York momenta setting the initial orbit for a spiralling merger — exactly
as in a binary-black-hole run, where the momenta only choose the orbit and
gravitational-wave emission does the inspiralling.

## Initial data (Route A, analytic superposition)

```
psi   = 1 + [sqrt(1 + b_A²/4r_A²) − 1] + [sqrt(1 + b_B²/4r_B²) − 1]
          + m_A/(2 r_A) + m_B/(2 r_B)
chi   = psi⁻⁴,  h_ij = δ_ij,  K = 0,  Theta = 0
phi   = (1/√4π) [atan(...r_A...) + atan(...r_B...)]  − asymptote,  Pi = 0
A_ij  = chi^{3/2} · Σ Bowen–York(P_X)      (BinaryBHInitialData convention)
```

With K = 0 and Pi = 0 the **momentum constraint is satisfied exactly**; only the
Hamiltonian constraint carries the superposition defect — O(b²/d²) between pure
throats, plus O(m/d) once bare masses are on, plus a near-throat defect because
the analytic φ profile supports the *massless* throat. GRTresna-solved data
(`recipe_initial_data_file`, Route B) removes all of it.

Setting `wormhole_throat_radius_B = 0` (with `wormhole_bare_mass_B = 0`) removes
object B entirely — the single-throat regression mode.

## Constraint-solved data (`constraint_solve = 1`)

With Π = 0, K = 0 and conformally flat data the Hamiltonian constraint for this
matter is `lap Psi − V Psi + (1/8) Ahat·Ahat Psi⁻⁷ = 0`, `V = π s |grad φ|²`
(`Psi⁴ = 1/chi`, `s = wormhole_support_strength`). The single drainhole solves
it exactly; the superposition does not. `DrainholeConstraintSolve.cpp` adds a
correction `w` to the superposed `Psi` so that it does, on the whole initial
hierarchy at once with AMReX's `MLABecLaplacian` (a Newton iteration when a
Bowen–York term is present; three passes at `p = 0.12`–`0.45`), holding φ,
`Ahat_ij`, the lapse and Π fixed: the momentum constraint stays exact. Each
throat keeps a puncture coefficient `c` (`Psi → c/r` at its centre); the
default is the superposition's own, so the throats keep their superposed size
and the solve adds the scalar interaction energy the superposition leaves out
(M_ADM 2.00 → 2.63 at d = 8). Refused with a conformal-factor seed (the solve
would erase it), the Helfer correction, a boosted scalar, `id_type = 0`,
`phantom_mass ≠ 0` or an external grid. Full account: the class comment of
`BinaryWormholeInitialData.hpp`.

| Key | Meaning |
| --- | --- |
| `constraint_solve` | 0 (default, bit for bit) / 1 |
| `constraint_solve_background` | 0 = the superposition (default); 1 = bare punctures `1 + Σ c/r` (validation: must rebuild the drainhole) |
| `constraint_solve_puncture_mode` | 0 = the superposition's `c` (default); 1 = the isolated throat's `(a/2)e^{πm/2a}`; 2 = explicit |
| `constraint_solve_puncture_coefficient_A/B` | the explicit `c` for mode 2 (B defaults to A) |
| `constraint_solve_tolerance`, `_tolerance_abs`, `_max_iter` | MLMG (1e-10, 0, 200) |
| `constraint_solve_max_newton`, `_newton_tolerance` | Newton on the Bowen–York term (30, 1e-10) |
| `constraint_solve_verbose` | 1 = one line per Newton pass; 2 = MLMG's own output |

The log reports the puncture coefficients, `max |w|` per level and an ADM-mass
estimate. Grade the result with
`grteclyn-wrapper/scripts/validation/constraint_solve_t0_check.py <plt00000>
--params <run>/params.txt --mass` on the t = 0 plotfile (plot `constraints`;
set `G_Newton = 1.0`): the finest-level
Hamiltonian on the throat shell drops from ~1e-2 to the exact throat's
discretisation floor (~5e-6 at level 3). The base-grid `L2_Ham` does not see
the difference — it cannot resolve a throat.

## Key parameters

| Key | Meaning |
| --- | --- |
| `wormhole_throat_radius_A/B` | throat radii b (B defaults to A; 0 removes B) |
| `wormhole_bare_mass_A/B` | puncture masses m — the gravity (B defaults to A) |
| `wormhole_centerA/B` | offsets from `center` (B defaults to −A) |
| `wormhole_momentumA/B` | Bowen–York momenta (B defaults to −A) |
| `wormhole_subtract_phi_asymptote` | shift φ → 0 at infinity (default 1; free only for `phantom_mass = 0`) |
| `binary_throat_diagnostics` | own module, own file, **default off** |
| `recipe_initial_data_file` | `.gridinit` from GRTresna (Route B) — overrides the analytic ID |

## Outputs

- `constraint_norms.dat` — as elsewhere.
- `collapse_diagnostics.dat` — the **unchanged 13-column single-throat contract**.
- `binary_throat_diagnostics.dat` — 17 columns: separation, per-throat barycentre
  /χ/lapse minima, θ₊ and the outermost trapped radius about throat A, throat B and
  their midpoint. θ₊ is reduced as a **maximum per radial shell**, since a surface is
  trapped only when θ₊ ≤ 0 everywhere on it; a shell the finest AMR level does not
  cover gets no verdict and reads 1e30. θ₊ < 0 inside `binary_diag_min_radius` of a
  throat is the coordinate inversion, not a horizon — only the common-centre scan,
  whose cut is raised to sep/2 + min_radius so the sphere encloses both throats, is
  evidence of fusion.
- `Weyl4_mode_*.dat` — in-code Ψ₄ spherical-harmonic extraction (`BHAMR`).

## Running

Always through the wrapper campaign launcher (registers `launcher.pid`, keeps
plotfiles on node-local scratch):

```bash
WHM_PARAMS=params_test.txt   bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh  # smoke
WHM_PARAMS=params_headon.txt bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh  # from rest
WHM_PARAMS=params_spiral.txt bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh  # headline
```

Stop with `bash grteclyn-wrapper/scripts/campaigns/stop_campaign.sh <runs_dir>`.
