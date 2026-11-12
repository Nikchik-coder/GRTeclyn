# Research plotting

This package creates figures from simulation data and saved research results.
The streaming plotfile consumer lives in
[`grteclyn_workflows.postprocessing`](../postprocessing/README.md).

## Common commands

```bash
python -m grteclyn_workflows.plotting.constraints RUN/data/constraint_norms.dat -o RUN/plots/constraints
python -m grteclyn_workflows.plotting.diagnostics.diagnostic --help
python -m grteclyn_workflows.plotting.waveforms.plot_extracted_psi4 --help
python -m grteclyn_workflows.plotting.slices --help
bash grteclyn-wrapper/scripts/plot/plot_diagnostic.sh RUN
```

`waveforms/` owns waveform panels, `constraints/` owns constraint and convergence
plots, `diagnostics/` owns collapse panels, and `slices/` owns direct field slices.
The other subpackages group figures by study: `bondi_dipole`, `wormhole_merger`,
`wormhole_dynamics`, `spinning_wormhole`, `railgun`, `optimisation`, `radial`,
`geometry_atlas` and `search`.

Generic plotters default to `runs/plots/`. Campaign helpers write to the run's
`plots/`, `frames/` and `movies/` directories. Curated reproducible figures belong
under `results/`. Source directories never serve as output folders.

For fixed-scale movies, use `scripts/plot/rerender_frames.py` with the saved slice
cache, then `scripts/plot/make_movies.sh`. Existing frames are retained.
