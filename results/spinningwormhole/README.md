# Rotating Ellis–Bronnikov wormholes — results pack

The data behind N. M. Shirokov and I. Nachevsky, *Rotation slows the instability of
Ellis–Bronnikov wormholes* (2026): the stationary rotating solutions, the 3D evolutions
the paper quotes, and the inputs of every figure and table. The evolution code is
`Examples/SpinningWormhole/`; the spectral solver, the analysis and the figure scripts
are in `grteclyn-wrapper/`.

## The paper

Every figure rebuilds from this directory without a GPU, with
`grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.spinning_wormhole.<script>`:

| In the paper | Data | Script |
|---|---|---|
| Fig. 2, Table II | `solver/solutions.tsv`, `solver/kk2014_fig1_digitized.tsv` | `plot_kk2014_comparison` |
| Fig. 3, Table III | `solver/solutions.tsv`, `solutions/`, `backgrounds/`, `scalar_charge_runs.tsv` | `plot_spin_trends` |
| Tables IV–V, Fig. 4 | `campaign/drainhole/00_paper_runs/`, `backgrounds/`, `runs_registry.tsv`, `trust_windows.tsv` | `plot_instability_curve` |
| Fig. 5 | `campaign/drainhole/00_paper_runs/`, `backgrounds/` | `plot_farzone_wave` |
| Fig. 6 / Fig. 7 | the D21 / D90 triplets in `campaign/drainhole/00_paper_runs/` | `plot_convergence --spin 0.2c` / `plot_convergence` |
| Sec. IV B, the t = 0 checks | `campaign/drainhole/03_t0_checks/`, `campaign/symmetric_massless/01_t0_checks/L128_A1/` | — |
| Sec. IV B, the static check | `campaign/drainhole/01_static_hold/` | — |
| Sec. IV C, the outer boundary | `campaign/drainhole/10_sponge_test/` | — |
| Sec. V, second-order data | `campaign/drainhole/02_spin_hold/` | — |
| Appendix B, the timestep | `campaign/drainhole/06_dt_ladder/` | — |
| Sec. VII, the GPU-hours | `campaign/drainhole/00_paper_runs/*/run_tail.log` | `grteclyn-wrapper/scripts/campaigns/spinning_wormhole/gpu_hours.py` |

## Layout

- `solver/solutions.tsv` — every accepted solution of the spectral solver (462 rows): the
  family and continuation leg, the grid, the global charges, the throat radii and the
  identity checks of the paper's Table I.
- `solver/kk2014_fig1_digitized.tsv` — the curves of Kleihaus and Kunz, Phys. Rev. D 90,
  121503(R) (2014), Fig. 1, digitized for Fig. 2 (reading error rms 1–6e-4).
- `solutions/<leg>/` — the solutions the figures read, one pair per solution: `.npz`, the
  metric functions on the spectral grid; `.json`, the parameters, charges and identity
  checks. `solver/solutions.tsv` names each one's leg and step.
- `backgrounds/` — the headers (grid and global numbers) of the background tables the
  Table IV runs start from; the solver exports the tables themselves (12.7 MB each).
- `campaign/` — one directory per 3D run; `runs_registry.tsv` lists them all, with what
  each run is, where the paper uses it and its outcome. `drainhole/` holds the drainhole
  family (η0 = 2, γ = −π), `symmetric_massless/` the symmetric family (γ = 0), rescaled to
  η0 = 2 for the 3D checks.
- `trust_windows.tsv` — the last converged time of each run that is not converged to its
  end; the paper quotes nothing later (Table V's t_conv).
- `binaries.tsv` — the GRTeclyn build each run used: hash, source commit, flags.
- `scalar_charge_runs.tsv` — the scalar charge measured on each run's t = 0 slice (Fig. 3).
- `figures/` — the paper's figures, as PDF and PNG.

## A run directory

- `evolution_params.txt` — the run's parameters (AMReX ParmParse format).
- `run_manifest.json` — the build (binary hash, source commit) and the launch time.
- `run_tail.log` — the end of the code's log: speed and memory.
- `constraint_norms.dat`, `constraint_norms_levels.dat` — L2 norms of the Hamiltonian and
  momentum constraints over the domain and per refinement level.
- `throat_geometry.dat`, `throat_spheres.dat` — the throat's equatorial and polar
  circumferential radii, and its areal radius.
- `collapse_diagnostics.dat` — extremes of the lapse, the conformal factor, K and the scalar
  field.
- `mots_spectral.dat`, `mots_spectral_alm.jsonl` — the marginally outer-trapped surface
  found on every output (areal radius, Hawking mass, extent) and its shape coefficients; a
  row of nan means none was found.
- `psi4_mode_l2_all.dat`, `psi4_mode_l2m0.dat`, `psi4_directional.dat` — the ℓ = 2 modes of
  Ψ4 on the extraction spheres.
- `boundary_flux.dat` — the net outward flux and the Ψ4 amplitude at the outer boundary.

Every `.dat` file names its columns in its header. A run's name encodes its box (`L`), base
cells (`N`, when not the box's default), background, damping layer (`spdrv0`/`spdrv1`),
Kreiss–Oliger strength (`sig`), timestep (`dt`) and stop time (`t`); `runs_registry.tsv`
spells each run out, and the `t0conv_…` runs are the t = 0 checks. Paths in the parameter
files (`runs/…`, `/tmp/grteclyn_scratch/…`) are where the run wrote its output.
