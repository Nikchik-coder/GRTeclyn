# The Bondi article's figures, and how each is drawn

One folder per campaign group, named as in `../campaign/` (2026-10-26, the layout of `results/merger/figures/`);
every figure is a PDF beside its PNG. The article reads them from here: `\graphicspath` in
`research/bondi_dipole/article/bondi_dipole.tex` and `\includegraphics{<group>/<name>.pdf}`. Every one is drawn from
the revision's runs on the fixed code (`../runs_registry.tsv`); nothing is drawn by hand.

Rebuild from the repository root on the workstation (the text goes through pdflatex, matplotlib's pgf backend):

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.bondi_dipole [article|bend|convergence]
```

| Fig. | label | file | drawn by | runs |
|---|---|---|---|---|
| 1 | `fig:schematic` | `00_overview/schematic` | `article_figures.fig_schematic` | none (drawn) |
| 2 | `fig:frames` | `04_runaway/chase_frames` | `article_figures.fig_chase_frames` | PM10 N 256 (its packed stills) |
| 3 | `fig:traj` | `04_runaway/trajectories` | `article_figures.fig_trajectories` | PM10 N 128 / 256, PM10-t400, P N 128, M N 256, PP10, MM10 |
| 4 | `fig:forcelaw` | `05_separation/forcelaw` | `article_figures.fig_forcelaw` | PM8–PM20, PM10 N 256; E0.64, PM20, E1.34, E1.57 through `../campaign/06_mass/mass_law.csv` (`grteclyn_wrapper.analysis.bondi_dipole.fit_mass_law`) |
| 5 | `fig:samesign` | `03_same_sign/samesign` | `article_figures.fig_samesign` | PP10, MM10 (their `well_tracking.dat`, from `grteclyn_wrapper.analysis.bondi_dipole.track_wells` at packing), PM10 N 256 |
| 6 | `fig:massscale` | `06_mass/massscale` | `article_figures.fig_massscale` | R0.60, R0.80, PM10 N 128, R1.33 |
| 7 | `fig:wavezone` | `04_runaway/wavezone` | `article_figures.fig_wavezone` | PM10-L128 |
| 8 (App. A) | `fig:constraints` | `09_convergence/convergence_pair` | `plot_convergence --study pair` | PM10 N 128 / 192 / 256 |
| 9 (App. A) | `fig:convergence_lone` | `09_convergence/convergence_lone` | `plot_convergence --study lone` | M N 128 / 192 / 256 |
| — | not in the article | `00_overview/spacetime_bend` | `spacetime_bend` | none (drawn) |

A referee-style audit (2026-10-26, second pass) switched Fig. 8(k) and the massscale curves to the core
separation (the paper's d; the barycentre separation takes in shed field at every N), renamed the forcelaw axes to
d_0 with the fit labelled by Mbar, tagged the frames' top row with the plotted sum w_+ + w_-, and trimmed the
single-column heights (massscale and wavezone 2.55 in, forcelaw 3.62, samesign 2.78).

Two figures left the article on 2026-10-26: the main-text resolution figure (`09_convergence/convergence`; the
appendix sets show the same data, and `article_figures.print_convergence` still prints the numbers Sec. VII A
quotes) and the star-family plot (`01_star_family/family`; the text states its two facts). The two appendix sets
share one float page.

The look, shared by every figure (`article_figures.RC`, `LADDER`, `ORDER_COLOUR`): data in black and grey; the
resolution ladder dotted, dashed and solid for N 128, 192 and 256; fits, order-2 curves and the signed momentum in
orange (`#D55E00`), the one accent; order-4 curves in grey; Computer Modern through pdflatex. Every line is named in a
key above its panel; inside the frame only small tags on rules and markers. Every save runs `style.label_audit`
with a margin, so a label resting on a curve is reported as well as one crossed by it.
