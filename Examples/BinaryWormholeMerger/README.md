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
throat keeps a puncture coefficient `c` (`Psi → c/r` at its centre). Refused
with a conformal-factor seed (the solve would erase it), the Helfer
correction, a boosted scalar, `id_type = 0`, `phantom_mass ≠ 0` or an
external grid. Full account: the class comment of
`BinaryWormholeInitialData.hpp`.

**Which throats the pair is made of.** A mouth's identity is its far side:
`Psi = c/r + d` near the centre is, after `r' = c²/r`, an asymptotically flat
end with ADM mass `M_far = 2cd` and scalar charge `Q_far = 4Cc²/a`, both
frozen in time. The isolated `a = 2, m = 1` throat has −4.8105 and 3.0344
(R\* = 3.8895). The superposition's mouths are ~13 % larger in every length
(the companion's constants rescale them), and the default solve keeps them so:

| d = 8, L = 64, level 3, t = 0 | R_min | M_far | Q_far | one-body m′ | M_ADM |
| --- | --- | --- | --- | --- | --- |
| isolated throat | 3.890 | −4.810 | 3.034 | 1 | 1 |
| superposed pair | 4.466 | −5.363 | 3.436 | 1.149 | 2.00 (not a solution) |
| solved, mode 0 (CS-1) | 4.523 | −5.368 | 3.436 | 1.148 | 2.738 |
| solved, mode 3 | 3.892 | −4.810 | 3.034 | 1.000 | 2.362 |

Mode 0 is therefore the solved twin of a superposed run (same mouths, the
data changed); mode 3 builds the pair from two isolated throats, so a momentum
`p` is in units of the true one-body mass. `M_ADM − Σ m′` is +0.36 for this
flipped pair and −0.62 for the like pair (mode 3): their mean is the Newtonian
`−m²/d`, the rest the ghost scalar's cross energy, which is positive where the
throats attract.

| Key | Meaning |
| --- | --- |
| `constraint_solve` | 0 (default, bit for bit) / 1 |
| `constraint_solve_background` | 0 = the superposition (default); 1 = bare punctures `1 + Σ c/r` (validation: must rebuild the drainhole) |
| `constraint_solve_puncture_mode` | 0 = the superposition's `c` (default); 1 = the isolated throat's `(a/2)e^{πm/2a}`; 2 = explicit; 3 = far-side matched (iterated at t = 0) |
| `constraint_solve_puncture_coefficient_A/B` | the explicit `c` for mode 2 (B defaults to A) |
| `constraint_solve_match_charge` | mode 3: 1 = match `M_far` and `Q_far` through `c` and each throat's coordinate scale σ = (c/c_iso)² (default); 0 = `M_far` alone through `c` |
| `constraint_solve_match_tolerance`, `_match_max_iter` | mode 3: stop at max \|M_far/M_iso − 1\| below this (1e-6), or after this many passes (10) |
| `constraint_solve_tolerance`, `_tolerance_abs`, `_max_iter` | MLMG (1e-10, 0, 200) |
| `constraint_solve_max_newton`, `_newton_tolerance` | Newton on the Bowen–York term (30, 1e-10) |
| `constraint_solve_verbose` | 1 = one line per Newton pass; 2 = MLMG's own output |

The log reports the puncture coefficients, `max |w|` per level, each mouth's
`c`, coordinate scale, far-side mass and charge and one-body drainhole, and
`M_ADM` from the volume identity `2Σc − (1/2π)∫[V Psi − ⅛Â·Â Psi⁻⁷] dV`
(1.0014 on the exact throat). The same numbers go to one t = 0 row of
`constraint_solve.dat` in the data directory. The older "`M_ADM ~` background
+ 2⟨r w⟩" line reads the Robin face, which leaves `w` a constant ≈ −1e-3 in
the box, and comes out low (2.58 against 2.74). Superposed runs (solve off)
log each mouth's far side in closed form.

Grade the result with
`grteclyn-wrapper/scripts/validation/constraint_solve_t0_check.py <plt00000>
--params <run>/params.txt --mass [--solve-data <run>/data/constraint_solve.dat]`
on the t = 0 plotfile (`--solve-data` is required for mode 3). With the
`constraints` plot field (set `G_Newton = 1.0`) it grades the finest-level
Hamiltonian on the throat shell, which drops from ~1e-2 to the exact
throat's discretisation floor (~5e-6 at level 3); the base-grid `L2_Ham` does
not see the difference — it cannot resolve a throat. `--mass` needs only
`chi`: each mouth's R_min, far-side mass and charge, and M_ADM three ways.

## Key parameters

| Key | Meaning |
| --- | --- |
| `wormhole_throat_radius_A/B` | throat radii b (B defaults to A; 0 removes B) |
| `wormhole_bare_mass_A/B` | puncture masses m — the gravity (B defaults to A) |
| `wormhole_centerA/B` | offsets from `center` (B defaults to −A) |
| `wormhole_momentumA/B` | Bowen–York momenta (B defaults to −A); under momentum model 1, each throat's ADM momentum γmv |
| `wormhole_momentum_model` | 0 = Bowen–York on the static throat with the scalar at rest (default, bit for bit; the mismatch kicks a moving throat toward inflation as p²); 1 = the exact Lorentz-boosted drainhole: metric, K_ij, φ and Π together, lapse type 5 or 6, no solve yet (see "EXACT BOOST" in `BinaryWormholeInitialData.hpp`) |
| `wormhole_boost_initial_shift` | momentum model 1: 1 = the boosted solution's own shift (default), 0 = zero shift |
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
