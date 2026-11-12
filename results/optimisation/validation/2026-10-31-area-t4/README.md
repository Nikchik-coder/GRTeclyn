# D21 fixed-area, four-times-reference tidal pilot

Completed 2026-10-31 at 14:57 MSK, exit 2, code 368a445b.
Configuration: research/optimisation/studies/d21_fixed_area.toml,
case potential-t4, seed 7, 150x30 search, 200-evaluation cap.
The matched massless reference passes 150x30, 180x36 and 210x42.

The search ended after 88 proposals. Ten search-grid passes were independently
refined; none passed all three grids. Search-best X_full = 2.188430376039,
reference X_full = 4.684238262942. These are not a validated improvement.
The exact CMA stopping dictionary was not recorded. Refinement rejects unused
stationary constraints despite small Newton residuals; investigate solve
accuracy before expanding the matrix. Radial stability remains unassessed.

The archive includes all saved fields, evaluation records, reference checks,
ten finalist refinements, outcome, comparison plots and the job log.
Deployment prefixes in text files were made repository-relative; numerical
payloads are unchanged. SHA256SUMS hashes this archive.
