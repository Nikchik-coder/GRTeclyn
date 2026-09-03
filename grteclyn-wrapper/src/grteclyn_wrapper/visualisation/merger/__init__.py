"""Figure generation for the wormhole-merger campaign.

``plot_bbh_vs_wormhole_psi4`` draws the object-vs-object comparison: the
p = 0.12 wormhole twin against the vacuum BBH control on the identical orbit
(same ADM masses, separation and momenta), from the packed campaign in
results/merger.  Both series come from the in-code Weyl4 mode integrals, the
extraction chain validated against independent quadrature.

Writes into results/merger/figures/ by default (``--out`` overrides).
"""

__all__ = ["plot_bbh_vs_wormhole_psi4"]
