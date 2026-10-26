"""Figure generation for the Bondi-dipole article.

``article_figures`` rebuilds every panel of the article (research/bondi_dipole/article/)
from the packed campaign in results/bondi-dipole-runaway and prints each number the
text quotes.  ``spacetime_bend`` draws the schematic embedding cartoon, which
uses no data at all.  ``plot_convergence`` draws the two resolution sets.

All write into results/bondi-dipole-runaway/figures/<group>/, a PDF beside a PNG, where
the article reads them; figures/FIGURES.md is the index.
"""

__all__ = ["article_figures", "plot_convergence", "spacetime_bend"]
