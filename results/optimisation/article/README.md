# Article selection ledger

`ledger_models.tsv` records the exact source and 1-based TSV record of every
selected candidate. Search rows are the minimum finite X with verdict PASS
and both background Einstein residuals <=1e-8 in the latest fixed-size,
fixed-spin trace for that model. This is a search-grid selection, not a
stability or finer-grid certificate. D51 has no PASS row in its main trace
and therefore has no selected table row. S50 now uses the same background
selection as the other models, rather than filtering on the old radial screen.

D21fine is a separate candidate: the archived e140 210x42 background. Its
fields and physical throat metadata are in `d21_e140_210x42.npz`; the obsolete
`lam_eta0` metadata is ignored. It is distinct from the D21 search minimum.
The NPZ is identical to the original e140 input retained with the extension
archive; no extension trial enters these tables.

Classical X values for D0, D21, D30, D80, D90 and S0 come from their search's
`best_clean.npz` X_v0 metadata. S27, S50 and S85 retain the five-decimal
classical reference values recorded in STATUS. The paper prints fewer
significant figures. The rotation label refers to the reference family.

The checked ledger generates both parameter and exoticity tables, with the
same selection and row order. The spin figure reads this ledger too.
Run the wrapper Python with `research/optimisation/article/claims/claims.py
check`, then `... claims.py tex` to regenerate `numbers.tex`. Evolution
order and contraction-time macros are generated from the packed streams.

`instability_curve.tsv` records the measured growth rates and fitting intervals
for the classical and potential-bearing models. The figure script regenerates
it here; `figures/` holds only the rendered plots.

`ledger_physics.tsv` selects the stationary D0/D21/D30 comparison with each
model's exact massless reference. These are the selected fine-grid fields
documented in `../physics/sources.json`, not the original search minima.
The claims checker validates the ledger against `../physics/summary.tsv`
and generates the physics table and prose macros. The article pairs this
table with the mechanism profiles; the redundant NEC map and trade-off
plot have been removed.

The physics table displays dimensionless V=0 and optimized values side by
side for each model, rather than ratios alone.
