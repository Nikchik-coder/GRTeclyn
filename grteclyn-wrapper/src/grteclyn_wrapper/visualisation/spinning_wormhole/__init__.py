"""Figures of the spinning-wormhole research, drawn from packed solver data.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.solutions
        collects every saved fast-spin Solution under runs/spinning_p3/ into
        results/spinningwormhole/solver/solutions.tsv (tracked; runs/ is not)

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.headers
        copies the header (grid and meta numbers) of each background table
        the article's 3D runs use into results/spinningwormhole/backgrounds/
        (tracked; the 12.7 MB tables are not), where the figures read J,
        J/A and M_ADM

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.kk2014
        digitizes the wormhole curves of Kleihaus & Kunz 2014 Fig. 1 from the
        published raster into results/spinningwormhole/solver/
        kk2014_fig1_digitized.tsv, with the reading error measured on their
        Kerr curves

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_comparison
        THE PAPER FIGURE: our symmetric family as curves against KK 2014's
        digitized points and the closed-form Kerr curves; red/green/blue by
        default, --palette house or --colors C1,C2,C3 to redraw

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_fig1
        an internal check only: our solutions as circles on the published
        raster itself (a paper cannot reuse that image)

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends
        both families against v_e at fixed eta0: mass, J and size, J/M^2
        against the Kerr bound, the far side's mass, the flattening R_p/R_e,
        the scalar charge D and the throat's rotation rate, with the
        extremal-Kerr limits and the drainhole holds evolved in 3D

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_convergence
        the v_e = 0.9 hold's resolution triplet (N 128 / 192 / 256): the
        Hamiltonian and momentum constraints on every refinement level, with
        the finest member rescaled at 2nd and 4th order to bracket the
        coarsest, and a row on the throat and the wave zone (the equatorial
        radius against its exact value, the areal radius's drift, Psi4 (2,0)
        at R = 18, the far-side lapse); reads the packed runs and the solver
        table, writes results/spinningwormhole/figures/convergence_09c

The solver figures go to results/spinningwormhole/figures/solver/.  Every
paper figure reads only tracked files under results/, so it rebuilds from a
clean checkout (the instability curve falls back to a run's streams under
runs/ while it is unpacked).
"""
