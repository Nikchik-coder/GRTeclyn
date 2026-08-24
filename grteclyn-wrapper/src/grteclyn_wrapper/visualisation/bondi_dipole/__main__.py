"""Rebuild the Bondi-dipole figures.

    python -m grteclyn_wrapper.visualisation.bondi_dipole            # all
    python -m grteclyn_wrapper.visualisation.bondi_dipole article    # data
    python -m grteclyn_wrapper.visualisation.bondi_dipole bend       # cartoon
"""

import argparse

from . import article_figures, spacetime_bend


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bondi_dipole", description=__doc__)
    ap.add_argument("target", nargs="?", default="all",
                    choices=("all", "article", "bend"),
                    help="which figures to rebuild (default: all)")
    args = ap.parse_args(argv)

    if args.target in ("all", "article"):
        article_figures.main()
    if args.target in ("all", "bend"):
        spacetime_bend.main([])


if __name__ == "__main__":
    main()
