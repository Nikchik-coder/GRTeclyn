"""Figures of the spinning-wormhole research, drawn from packed solver data.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.solutions
        collects every saved fast-spin Solution under runs/spinning_p3/ into
        results/spinningwormhole/solver/solutions.tsv (tracked; runs/ is not)

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_fig1
        the published Kleihaus & Kunz 2014 Fig. 1 with our symmetric family
        on it as open circles, written to results/spinningwormhole/figures/solver/

The figures read only the packed table (and, for an overlay, the published
raster kept beside the papers in research/spinningwormhole/article/articles/),
so they rebuild from a clean checkout.
"""
