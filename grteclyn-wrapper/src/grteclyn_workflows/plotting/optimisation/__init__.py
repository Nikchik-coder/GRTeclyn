"""Campaign M figures, from the packed TSVs under results/optimisation/.

The figures read only the packed data, never the optimisation package
itself (its layout rule: nothing outside it imports it, since develop
ships without it).  ``plot_convergence`` is the exception while the
D21 3+1 triplet is live: it reads the run dirs (or a packed copy).
``plot_exotic_spin`` reuses the spinning-wormhole packed solutions for
the classical curves and STATUS X for the CMA-ES finds.
"""
