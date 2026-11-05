# Optimisation figures

Grouped by what they show, as in [the railgun figure tree](../../railgun/figures/README.md).
Rebuild commands use the wrapper Python. Standalone numeric companions stay
in `../article/` and `../physics/`; search traces stay in `../opt/`.

## Search

CMA-ES coverage and progress at fixed throat size and spin.

- [Ten completed searches: parameter projections and running minima](search/potential_scans.png)
  ([PDF](search/potential_scans.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_potential_scans`.
- [D0 search history](search/cma_progress_d0.png)
  ([PDF](search/cma_progress_d0.pdf)).
- [D21 search history](search/cma_progress_d21.png)
  ([PDF](search/cma_progress_d21.pdf)).
- [D51 search history](search/cma_progress_d51.png)
  ([PDF](search/cma_progress_d51.pdf)).

Rebuild a progress panel with
`-m grteclyn_wrapper.visualisation.optimisation.plot_cma_progress --tsv`
and the packed TSV under `../opt/`.

## Stationary solutions

Selected backgrounds and the D21 mechanism comparison.

- [Exoticity against rotation for both families](stationary/exotic_spin.png)
  ([PDF](stationary/exotic_spin.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_exotic_spin`.
- [D21 profiles against the massless reference](stationary/mechanism_d21.png)
  ([PDF](stationary/mechanism_d21.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_physics`.

## Evolution

Three-dimensional runs at N=128, and the D21 resolution study.

- [D21 constraint and diagnostic histories](evolution/convergence_d21.png)
  ([PDF](evolution/convergence_d21.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_convergence`.
- [Time to 1% throat contraction](evolution/contraction_delay.png)
  ([PDF](evolution/contraction_delay.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_contraction_delay`.
- [Fitted growth rates against the classical family](evolution/instability_curve.png)
  ([PDF](evolution/instability_curve.pdf)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_instability_curve`.

## Quantum budget

Campaign F measurement.

- [log10 F at a 1 m throat against v_e](quantum-budget/f_curve.png).
  Rebuild with `grteclyn-wrapper/scripts/analysis/quantum_budget/plot_f_curve.py`.

## Setup

Explanatory artwork, not a solved field.

- [Weak ring around a two-ended throat](setup/wormhole-ring-setup.png)
  ([SVG](setup/wormhole-ring-setup.svg)). Rebuild with
  `-m grteclyn_wrapper.visualisation.optimisation.plot_wormhole_ring_setup`.
