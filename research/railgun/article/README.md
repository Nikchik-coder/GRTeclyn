# Scalar-ring paper scaffold

Working title: **Frame dragging and spin-dependent transport in self-gravitating scalar rings**.

`research.tex` follows the spinning-wormhole paper's REVTeX layout. It contains
a results-focused abstract, model, stationary initial data, numerical setup,
diagnostics and criteria, four results sections, conclusions, and appendices.
The native TikZ diagram distinguishes the JAX stationary GPU solve from the
Cartesian preparation and GRTeclyn CUDA evolution. Four existing scientific
figures are included directly from `results/railgun/figures/`.

The author list, affiliations and acknowledgments follow the spinning-wormhole
paper. This is a manuscript scaffold. The extended literature discussion,
full elliptic equations, particle velocity relation and detailed validation
tables are expansion points. Source comments identify the places to expand.
The results text covers completed stationary and particle studies and the
short-time three-resolution evolution; it makes no dynamical-stability or
energy-extraction claim.

## Numbers and builds

From the repository root:

```bash
grteclyn-wrapper/.venv/bin/python research/railgun/article/claims/claims.py check
grteclyn-wrapper/.venv/bin/python research/railgun/article/claims/claims.py tex
```

The local `claims/ledger_results.tsv` records the exact diagnostic source,
JSON pointer, source value, rounded manuscript value and source SHA-256.
The checker refuses changed sources or values. `numbers.tex` is generated;
edit the ledger and regenerate it when updating a claim.

From this directory, build outside the source tree:

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=/tmp/railgun-paper-lua research.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/railgun-paper-pdf research.tex
```

In a restricted environment, set `TEXMFVAR` and `TEXMFCACHE` to an existing
writable temporary directory for LuaLaTeX's font cache. Both engines must
build before a manuscript revision is considered checked. Render the PDF
pages with Poppler and inspect the diagram, captions and tables after edits.

## Included evidence

- `particles/ergoregion-372-cross-section.pdf`: accepted stationary ring,
  matter distribution, ergoregion and observer rates.
- `two-rings/annular-cross-section.pdf`: counter-rotating pair, component
  densities, channel and local dragging.
- `particles/strong-uphill-073.pdf`: matched-energy finite arrival versus
  turnaround under particle-spin reversal.
- `evolution/ring070-evolution-convergence.pdf`: completed three-resolution
  constraint and charge-change convergence study.

The stronger stationary rings and the weaker evolved ring are distinct models.
The explanatory poster that includes a rejected candidate is not used as an
accepted-result figure.
