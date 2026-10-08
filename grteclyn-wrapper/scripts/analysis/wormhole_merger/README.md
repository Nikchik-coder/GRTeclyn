# Wormhole-merger checks

Standalone checks behind numbers the merger paper quotes. Most of these numbers are
entered by hand in the claims ledger (`research/merger/article/claims/ledger_*.tsv`,
status `manual`), and the row's `source` names the script that printed them; the
`auto` rows are recomputed by the ledger's own extractors instead. Five of the scripts
read plotfiles or checkpoints rather than the pack, and one of them is the MOTS finder
the plotfile consumer runs on every plotfile.

These are scripts, not package modules: several import the claims code under
`research/merger/article/claims/`, the figure modules, or yt, sympy and astropy. The
importable reductions of the pack are the package `grteclyn_wrapper.analysis.wormhole_merger`.
Run them from the repository root with the wrapper's environment:

```bash
grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/wormhole_merger/<script>.py [args]
```

The pack-only scripts print a report and write nothing. The plotfile and checkpoint
tools run where those files are (a GPU node's scratch), in the background:
`OMP_NUM_THREADS=4 nice -n 19 ...`.

## Scripts

| script | reads | what it settles |
|---|---|---|
| `spherical_horizon_law.py` | nothing (sympy) | in spherical symmetry a massless phantom scalar can only shrink a MOTS |
| `horizon_first_law.py` | plotfiles | whether the single throat's collapse horizon obeys that first law, on round shells |
| `headon_first_law.py` | plotfiles | the spectral MOTS finder and the same law on the head-on remnant's found surface; `--selftest` runs two analytic checks |
| `local_hamiltonian.py` | plotfiles, or `--analytic EPS` | the Hamiltonian constraint near the horizon on a covering grid |
| `checkpoint_hamiltonian.py` | checkpoints | shell averages of H_ADM and Theta; `--out` wrote `results/merger/analysis/convfz_constraints_t100.tsv` |
| `seed_constraints.py` | pack | what the declared seed does to the constraints: measured, analytic, reproduced |
| `large_seed_fates.py` | pack | the eps = ±0.1 arms: how each collapses and dies |
| `horizon_regrowth_fits.py` | pack | fits to the single-throat MOTS histories |
| `linear_mode.py` | nothing (sympy, scipy) | the linear growth rate of the production throat, three ways |
| `pit_throats.py` | plotfiles | one throat or two: areal radius of spheres about each chi pit |
| `waves_seed_ladder.py` | pack | the quadrupole-seed ladder against the matched level-4 floor |
| `waves_throat_ringdown.py` | pack | the collapsing throat's ringdown period, fitted independently |
| `cosmology_lisa.py` | pack | LISA burst SNRs, the background, the little-red-dot abundances |

Every script's docstring states its method and its caveats.

## Dependencies between them

`checkpoint_hamiltonian.py` uses `local_hamiltonian.py`, which uses `horizon_first_law.py`.
`headon_first_law.py` builds on the flow finder `scripts/validation/ah_flow_finder.py`, and
the consumer (`grteclyn_wrapper.visualisation.process_wave.consume_plotfiles`) loads it from
this folder to write `mots_spectral.dat`; keep its path and its `fields_on_box` and
`analyse_fields` functions stable.
