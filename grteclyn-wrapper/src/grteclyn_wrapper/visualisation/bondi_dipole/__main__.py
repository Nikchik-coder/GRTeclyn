"""Rebuild the Bondi-dipole figures.

    python -m grteclyn_wrapper.visualisation.bondi_dipole            # all
    python -m grteclyn_wrapper.visualisation.bondi_dipole article    # data
    python -m grteclyn_wrapper.visualisation.bondi_dipole bend       # cartoon
    python -m grteclyn_wrapper.visualisation.bondi_dipole convergence  # both resolution sets
"""

import argparse

from . import article_figures, plot_convergence, spacetime_bend


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bondi_dipole", description=__doc__)
    ap.add_argument("target", nargs="?", default="all",
                    choices=("all", "article", "bend", "convergence"),
                    help="which figures to rebuild (default: all)")
    args = ap.parse_args(argv)

    if args.target in ("all", "article"):
        article_figures.main()
    if args.target in ("all", "bend"):
        spacetime_bend.main([])
    if args.target in ("all", "convergence"):
        for study in sorted(plot_convergence.STUDIES):
            plot_convergence.main(["--study", study])


if __name__ == "__main__":
    main()
