# consume_plotfiles

Stream AMReX plotfiles during a run: extract small-data time series, render diagnostic PNG frames, optionally delete processed HDF5 to save disk.

Invoked as a sidecar by `plot_consumer.build_consume_command` or directly:

```bash
python -m grteclyn_wrapper.visualisation.process_wave.consume_plotfiles --help
```

## Layout

| Path | Role |
|------|------|
| `driver.py` | `main()` — argparse, watch loop, parallel dispatch |
| `worker.py` | `_process_single_plotfile()` — one plotfile → outputs |
| `config.py` | Frame DPI, color limits, default paths |
| `plotfiles.py` | Discover plotfile dirs, readiness, restart detection |
| `fields.py` | Field aliases and yt derived-field registration |
| `sphere.py` | Sphere sampling grid and spin-weighted Y₂₀ |
| `state.py` | `consume_state.json` and `.dat` append helpers |
| `extraction/` | Psi4 mode, shell stats, areal radius, FTL timeseries, orientation-corrected horizon scan, spectral MOTS |
| `frames/` | Slice/projection/embedding PNG rendering and cleanup |

## Public API

```python
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles import main
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles import (
    get_extraction_points,
    spin_weighted_sph_harm_s2_l2_m0,
)
```

## Spectral MOTS (`--mots-spectral`, own files `mots_spectral.dat`, `mots_spectral_alm.jsonl`)

Off by default; on in the production head-on profile (`headon-modes-prod`) since
2026-10-01.
- **Why.** The horizon scan (below) and the oriented scan report the outermost fully trapped
  *round* sphere, which sits inside a deformed MOTS. On the mode-3 head-on's t = 51–60 slices
  they read R 4–11 % and 3–7 % low (HFL-ho). The true surface was found offline, which meant
  keeping every plotfile.
- **What.** Per plotfile, the common MOTS r = h(θ, φ) about the centre (`--mots-spectral-center`,
  default `--center`), in real Y_lm to `--mots-spectral-lmax`:
  - found once by the flow of `scripts/validation/ah_flow_finder.py` from the seed radii, then
    followed from plotfile to plotfile by Newton from the previous surface;
  - Newton runs until every projected θ_out harmonic is below `--mots-spectral-tol`;
  - the box is ±`--mots-spectral-half` on the finest level ≤ `--mots-spectral-level` that covers
    it, since a covering grid fills uncovered cells with injected coarse data.
- **Output.** One row per plotfile:
  - R, its Hawking mass, the area, the extent along each axis, the deformation, the residual;
  - the spherical first law's rates from the phantom flux and the shear on the surface;
  - the coefficients go to the JSONL file and the state, the next plotfile's start.
- **Implementation.** The finder is `scripts/analysis/merger_feedback/headon_first_law.py`, loaded
  from the wrapper (one implementation; its `--selftest` checks Kerr–Schild Schwarzschild and a
  flat spheroid).
- **Cost and needs.** About 20 s per plotfile at level 3 once it is following a surface. It needs
  full-state plotfiles plus lapse, phi and Pi. Plotfiles before `--mots-spectral-from` are skipped.

## Horizon scan (`--horizon-scan`, own file `horizon_scan.dat`)

Off by default.  Per plotfile and per mouth (`--horizon-centers x y z ...`, or
`--horizon-track <binary_throat_diagnostics.dat>` to follow moving mouths), the
pass scans coordinate spheres about the mouth with outward = *increasing areal
radius* -- inside a throat +r points toward the other mouth, so the naive
orientation computes the ingoing expansion and calls every throat interior
"trapped".  It writes the corrected areal minimum (the throat radius), the
health metric `R_min/R_exact - 1` (`--horizon-r-exact`), the outermost MOTS with
its Misner-Sharp mass and its depth (the most negative outgoing expansion
inside it -- a crossing whose interior never gets below a few per cent of the
scan's typical |theta| is marginal, not a horizon), both expansions on the
minimal surface, the trapped and anti-trapped shell counts, and the
outermost-surface count over the plotfile (1 when a common MOTS encloses both
mouths; the merger criterion is 2 -> 1).  Zero crossings at an extremum of
R(r), where the outward direction itself flips, are rejected: an inflating
throat's inner sheet grows a local maximum of R that would otherwise read as
a horizon of absurd mass.
Needs full-state plotfiles (chi K h_ij A_ij); about one second per plotfile at
level 3.  Analytic checks live in `tests/visualisation/test_horizon_scan.py`:
Kerr-Schild Schwarzschild finds its horizon at R = 2M with M_MS = M and a
trapped interior; a time-symmetric Ellis throat has no MOTS and no trapped
shell.  A marginal reading (theta_out within the discretisation offset of 0 on
a contracting throat) is not a horizon claim: the MOTS stability eigenvalue,
not implemented, is what separates a throat from a black-hole horizon.
