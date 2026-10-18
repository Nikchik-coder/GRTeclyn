"""Figures of the spinning-wormhole research, drawn from packed solver data.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.solutions
        collects every saved fast-spin Solution under runs/spinning_p3/ into
        results/spinningwormhole/solver/solutions.tsv (tracked; runs/ is not)

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.kk2014
        digitizes the wormhole curves of Kleihaus & Kunz 2014 Fig. 1 from the
        published raster into results/spinningwormhole/solver/
        kk2014_fig1_digitized.tsv, with the reading error measured on their
        Kerr curves

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_comparison
        THE PAPER FIGURE: our symmetric family as curves against KK 2014's
        digitized points and the closed-form Kerr curves; red/green/blue by
        default (the spinning paper's colours; gold is the merger paper's),
        --palette house or --colors C1,C2,C3 to redraw

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_fig1
        an internal check only: our solutions as circles on the published
        raster itself (a paper cannot reuse that image)

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends
        both families against v_e at fixed eta0: mass, J and size, J/M^2
        against the Kerr bound, the far side's mass, the flattening R_p/R_e,
        the scalar charge D and the throat's rotation rate, with the
        extremal-Kerr limits and the drainhole holds evolved in 3D

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_convergence
        the 0.9c hold's resolution triplet (N 128 / 192 / 256): the
        Hamiltonian and momentum constraints on every refinement level, with
        the finest member rescaled at 2nd and 4th order to bracket the
        coarsest; reads the packed runs, writes
        results/spinningwormhole/figures/convergence_09c

The solver figures go to results/spinningwormhole/figures/solver/.  The paper
figure reads only the two packed tables, so it rebuilds from a clean checkout.
"""
