# Waveform plots

`plot_extracted_psi4.py` plots extracted ASCII mode streams, including strain
and propagation diagnostics. `plot_psi4.py` reads simulation plotfiles directly.
`plot_rotating_wormhole_support.py` plots support-scan diagnostics.

```bash
python -m grteclyn_workflows.plotting.waveforms.plot_extracted_psi4 --help
```

Generic plots default to `runs/plots/`; use `--out` for a run's plot directory
or a curated figure location under `results/`.
Live extraction belongs to [`postprocessing`](../../postprocessing/README.md).
