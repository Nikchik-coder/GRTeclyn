"""Figure generation for the Bondi-dipole article.

``article_figures`` rebuilds every panel of the article (research/bondi_dipole/article/)
from the packed campaign in results/bondi-dipole-runaway and prints each number the
text quotes.  ``spacetime_bend`` draws the schematic embedding cartoon, which
uses no data at all.  ``plot_convergence`` draws the two resolution sets.

All write into results/bondi-dipole-runaway/figures/, where the article looks first.
"""

__all__ = ["article_figures", "plot_convergence", "spacetime_bend"]
