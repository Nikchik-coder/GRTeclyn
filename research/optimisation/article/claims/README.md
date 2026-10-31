# Article numbers

The source ledger is `results/optimisation/article/ledger_models.tsv`.
`claims.py check` verifies its selected records, parameters, X and constraint
residuals against the raw TSV/NPZ inputs, and verifies the packed evolution
streams and order calculations. `claims.py tex` runs those checks and writes
`../numbers.tex`; do not edit generated macros by hand. Both tables and the
spin figure share the same selection ledger.

`results/optimisation/article/ledger_physics.tsv` selects the six stationary
comparison rows for D0/D21/D30 and their massless references. `physics.py`
checks them against the measured summary, verifies the source hashes,
matching R_e/J and numerical checks, then generates the comparison-table
rows and the physics section's measured numbers. These selected fine-grid
solutions are separate from the search minima in the original tables.

`ledger_selected.tsv` records the exact potential parameters and independent
residuals of the three fine-grid fields used in the physics section.
`ledger_analytic.tsv` records the static analytical benchmarks, resolution-onset
slopes and the fixed-area spin-sensitivity estimate. `claims/analytic.py` checks
the static formulas with independent infinite-domain quadratures and a numerical
peak search, compares the displayed values with the physics ledger, and rebuilds
the timing estimates from the packed streams. The inferred seeding order assumes
a common growth time; it is not an independently converged instability rate.
