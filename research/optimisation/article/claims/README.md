# Article numbers

The source ledger is `results/optimisation/article/ledger_models.tsv`.
`claims.py check` verifies its selected records, parameters, X and constraint
residuals against the raw TSV/NPZ inputs, and verifies the packed evolution
streams and order calculations. `claims.py tex` runs those checks and writes
`../numbers.tex`; do not edit generated macros by hand. Both tables and the
spin figure share the same selection ledger.
