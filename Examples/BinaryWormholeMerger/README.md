# BinaryWormholeMerger

Merger of **two phantom-supported Ellis–Bronnikov wormhole throats** — the binary
generalisation of `Examples/SupportedWormholeCollapse`, built on the two-body
conventions of `Examples/BinaryBH`. Governing plan:
`research/merger/Plan.md` (kept out of the public tree).

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
  /χ/lapse minima, θ₊ minima and trapped radii about throat A, throat B and their
  midpoint. θ₊ < 0 inside `binary_diag_min_radius` of a throat is the coordinate
  inversion, not a horizon — only the common-centre scan is evidence of fusion.
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
