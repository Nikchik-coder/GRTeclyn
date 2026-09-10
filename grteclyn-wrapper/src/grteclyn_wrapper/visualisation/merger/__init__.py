"""Figure and movie generation for the wormhole-merger campaign.

``plot_bbh_vs_wormhole_psi4`` draws the object-vs-object comparison: the
p = 0.12 wormhole twin against the vacuum BBH control on the identical orbit
(same ADM masses, separation and momenta), from the packed campaign in
results/merger.  Both series come from the in-code Weyl4 mode integrals, the
extraction chain validated against independent quadrature.
Writes into results/merger/figures/ by default (``--out`` overrides).

``plot_psi4_modes`` overlays one Weyl4 mode of several runs at every
extraction sphere and prints every pairwise difference as a percentage of the
peak -- the seam check for a run continued by restarts (finer grid, coarser
grid, a different interior fill).  Reads the every-step stream under
runs/wormhole_merger/<run>/data/ or the thinned pack copy.

``stitch_movies`` plays several runs' cached slices as one movie per field on
a single colour scale: RUN_1 T_1 RUN_2 [T_2 RUN_3 ...], each run covering its
own stretch of time.  The movies stay in the run tree.
"""

__all__ = ["plot_bbh_vs_wormhole_psi4", "plot_psi4_modes", "stitch_movies"]
