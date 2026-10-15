# Spectral solver solutions (the families' source of truth)

The spinning-wormhole solver's converged solutions, copied verbatim from the
untracked `runs/spinning_p3/<leg>/` on 2026-10-15 so that no session has to
re-solve a spin to get the real f, omega, nu fields. Each leg is one
continuation branch: `<leg>.tsv` (one row per step: v_e, J, the gates) plus
`<leg>_<step>.json` (scalars + unimposed-constraint gates) and
`<leg>_<step>.npz` (the spectral coefficients) per step.

| leg | family | v_e range |
|---|---|---|
| fam_a | a | 0.057 - 0.198 |
| fam_a_r1 | a | 0.212 - 0.909 |
| fam_a_p4 | a | 0.912 - 0.950 |
| fam_a_p4b | a | 0.952 - 0.961 |
| fam_a_log | a | 0.057 - 0.991 |
| fam_b, fam_b_low, fam_b_p4, fam_b_p4b, fam_b_r1 | b | the mirror-symmetric branch |

The evolution tables (`.spinbg`, 13 MB - 193 MB each, 2.1 GB the set) are NOT
tracked: they regenerate from these solutions with
`grteclyn_wrapper.analysis.spinning_wormhole.backgrounds.full_background`
(doubling from 1025x65 until midpoint_err_f <= 1e-7, the
`runs/spinning_p3/p5_catalogue.py` code path, ~minutes per table on CPU).
These solutions are the small, slow-to-recompute part; keep them tracked.
