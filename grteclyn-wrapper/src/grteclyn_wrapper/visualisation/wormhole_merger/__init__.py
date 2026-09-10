"""Figures and movies for the wormhole-merger campaign — one package.

Merged 2026-09-10 from `merger` and `merger_ladder`, which were the same
campaign under two names, and renamed to match `runs/wormhole_merger/` and
`scripts/campaigns/wormhole_merger/`. Every module is run as
``python -m grteclyn_wrapper.visualisation.wormhole_merger.<module>``.

Runs are always resolved by NAME through `run_tree.find_run`, never by path,
so a run can be refiled without touching a figure script.

The waveform
  ``plot_psi4_modes``       one Weyl4 mode of several runs overlaid at every
                            extraction sphere, with every pairwise difference
                            as a percentage of peak — the seam check for a run
                            continued by restarts.
  ``plot_ladder_psi4``      the refinement-ladder arms overlaid at one detector.
  ``plot_bbh_vs_wormhole_psi4``  same masses, same orbit, different object:
                            the p = 0.12 wormhole against the vacuum control.
  ``plot_bbh_ringdown``     the control's ringdown and its quasi-normal fit.

The spacetime
  ``plot_merger_constraints``  Hamiltonian and momentum norms of the freeze arms.
  ``plot_branches``         the lone throat's two fates ACROSS RESOLUTION —
                            level 3 collapses, level 4 inflates — and writes
                            campaign/01_single_throat/BRANCHES.md with them.
  ``plot_seed_branches``    the same two fates chosen ON PURPOSE, by the sign
                            of a declared seed at one fixed resolution.

Movies
  ``stitch_movies``         several runs' cached slices played as one movie per
                            field on a single colour scale. Movies stay in the
                            run tree.
"""

__all__ = [
    "plot_bbh_ringdown",
    "plot_bbh_vs_wormhole_psi4",
    "plot_branches",
    "plot_ladder_psi4",
    "plot_merger_constraints",
    "plot_psi4_modes",
    "plot_seed_branches",
    "run_tree",
    "stitch_movies",
]
