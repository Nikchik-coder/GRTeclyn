# Wormhole-merger analysis

Reductions of the packed wormhole-merger campaign in `results/merger/` (the *pack*):
finding runs, the notes and tables generated at every pack, and the measurements behind
several of the paper's numbers. The modules read the tracked pack, use numpy, draw no
figures, and run from the wrapper's environment as

```bash
PY=grteclyn-wrapper/.venv/bin/python
$PY -m grteclyn_wrapper.analysis.wormhole_merger.<subpackage>.<module> [<pack-root>]
```

`<pack-root>` defaults to `results/merger` in this checkout. On an unchanged pack, every
writer reproduces its committed output exactly. The figures drawn from the same pack are
in `grteclyn_wrapper.visualisation.wormhole_merger`; the one-off checks behind the paper's
hand-entered numbers, which need the claims code, plotfiles or heavier libraries, are the
scripts in `grteclyn-wrapper/scripts/analysis/wormhole_merger/`.

## Modules

| module | reads | writes |
|---|---|---|
| `pack/paths.py` | — | library: where a run lives, by name, in the pack or the run tree |
| `pack/readers.py` | — | library: `evolution_params.txt` and `.dat` stream readers |
| `pack/summary.py` | every run's streams, `runs_registry.tsv` | `summary.csv`, `summary.md` |
| `pack/name_check.py` | every run's params and streams | `name_grammar.tsv` (the run-name grammar, with counts) |
| `pack/run_index.py` | `run_manifest.json`, streams, the name check | `runs_index.tsv` |
| `pack/gpu_hours.py` | `run_tail.log`, streams | prints GPU-hours per group |
| `single_throat/instability.py` | the isolated throat's streams | `campaign/01_single_throat/INSTABILITY.md` |
| `single_throat/clock_comparison.py` | every arm's `binary_throat_diagnostics.dat` | `campaign/01_single_throat/CLOCK_COMPARISON.md` |
| `single_throat/inflating_population.py` | the L = 512 inflating arm and a level-4 scalar arm | prints the inflating branch's population numbers |
| `two_throats/sign_rule.py` | run tree: chi_z slice caches of the rest pairs | `campaign/03_two_throats/sign_rule_displacement.dat` |
| `two_throats/matched_rest.py` | run tree: chi_z slice caches of the matched pairs | `campaign/03_two_throats/matched_rest_displacement.dat` |
| `two_throats/boosted_adm_mass.py` | the exact-boost pairs' `constraint_solve.dat` and params | `analysis/boosted_adm_mass.tsv` |
| `waves/single_throat_gates.py` | the kicked throat's and its controls' psi4 streams | `campaign/01_single_throat/WAVE_GATES.md` |
| `waves/headon_axis_modes.py` | the head-ons' Weyl4 (2,0) and (2,2) streams | `*_mode_20_axis.dat` beside each (2,0) stream |
| `waves/scalar_memory_angmom.py` | psi4 and scalar mode streams | library: `budget()`, the memory and J of both channels |

Each module's docstring gives the method and its caveats.

## When they run

`research/merger/pack_results.sh` runs `pack.summary`, `pack.name_check`, `pack.run_index`,
`single_throat.instability`, `single_throat.clock_comparison` and
`waves.single_throat_gates` at every pack. The other writers are run by hand when their
input changes. The paper's claims ledger (`research/merger/article/claims/`) imports
`pack.paths`, `pack.gpu_hours`, `single_throat.instability`, `waves.single_throat_gates`,
`waves.headon_axis_modes` and `waves.scalar_memory_angmom` to recompute the numbers it
quotes.

## What needs the run tree

`two_throats/sign_rule.py` and `two_throats/matched_rest.py` measure separations from the
chi_z slice caches, which are not packed. They read the untracked run tree
(`runs/wormhole_merger`, or `--runs`) and write only their reduced tables into the pack.
`pack.name_check --templates` also checks the untracked launch templates there.
