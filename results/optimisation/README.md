# Quantum-budget campaign — measured data

Campaign F (plan: `research/optimisation/Quantum Budget Wormhole Search.md`,
status: `research/optimisation/STATUS.md`).  Everything here rebuilds from a
clean checkout on CPU; no run output is involved.

## Campaign M search figures

`figures/potential_scans.{png,pdf}` now shows the ten completed fixed-size,
fixed-spin CMA-ES searches through 2026-10-30, replacing the earlier
fixed-mass slice overview. Rebuild with the wrapper Python and
`-m grteclyn_wrapper.visualisation.optimisation.plot_potential_scans`.
Its explicit `SEARCHES` list selects the packed TSVs under `opt/`, including
the latest D30 and D80 traces. Parameter projections show every recorded
proposal, including failed solves; they are not interpolated response surfaces.
Diamonds and running minima use stored PASS/FRONTIER rows, the background
constraint ceiling of 1e-6, and do not represent stability or finer-grid clearance.
Each progress curve is divided by its own first qualifying candidate's X.
Evaluation numbers are TSV row indices; inadmissible proposals rejected before
the Newton solve are absent from these TSVs. Extension trials are excluded.

`figures/cma_progress_d21.{png,pdf}` uses
`opt/fam_a_r1_0000_opt4s_150x30_kink.tsv`. Rebuild with
`-m grteclyn_wrapper.visualisation.optimisation.plot_cma_progress --tsv`
followed by that file path. It shows the same constraint threshold, a running
minimum, and an inset resolving the second half of the recorded search.

## Campaign M article tables and resolution study

`article/ledger_models.tsv` is the common selection for the parameter table,
exoticity table and `figures/exotic_spin.{png,pdf}`. Nine search-grid minima
pass both background constraints at 1e-8; D21 on 210x42 is a separate selected
candidate. See `article/README.md` for provenance and the claims checker.

`campaign/` contains the final D21 N96/N128/N192 diagnostic streams and
numerical settings. Rebuild `figures/convergence_d21.{png,pdf}` with
`-m grteclyn_wrapper.visualisation.optimisation.plot_convergence`.
The plot and measured order table use these tracked inputs. Constraint orders
are measured through t=50; the later diagnostic histories show contraction.
The classical evolution has different angular momentum and sponge driving;
a controlled delay comparison is deferred in the campaign STATUS.

## Completed D0/D30 checks

`completed/2026-10-31/` archives the finished D30 search (400 evaluations,
final three-grid PASS, X = 1.918733359440, stability unassessed) and D0's
N128 evolution, which contracted and terminated with NaN in K at t = 88.4175.
The pack includes complete small diagnostic streams and the validated D30
fields; these outcomes have not yet been added to the article.

## Stationary mechanism and trade-offs

`physics/` compares saved D0/D21/D30 fields with their exact fixed-R_e,
fixed-J massless references. Optimisation localises the scalar gradients:
the total exoticity decreases while peak NEC violation, peak tides and
finite-endpoint light transit increase. See [definitions, results and
checks](physics/README.md). The reproducible figures are
`mechanism_d21`, `nec_distribution_d21` and `stationary_tradeoffs` under
`figures/`; the numerical inputs stay under `physics/`.

## Campaign F measurements

| path | what | rebuild |
|---|---|---|
| `binaries.tsv` | Campaign M GRTeclyn evolution builds and provenance | `grteclyn-wrapper/scripts/campaigns/optimisation/build_binary.sh` |
| `fcurve/f_curve.tsv` | one row per solution of both spin families (200 saved solutions + 2 synthesized static anchors): the Ford–Roman compliance factor fhat, its normalizations, gates | `grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/quantum_budget/measure_f.py` |
| `fcurve/measurement.json` | the measurement's configuration and provenance | written by the same script |
| `figures/f_curve.png` | log10 F at a 1 m throat against v_e | `.../plot_f_curve.py` |

Definitions (one place: `grteclyn_wrapper/analysis/quantum_budget/conventions.py`):
fhat is F with the code length unit read as one Planck length;
F at a physical throat is `fhat / R_eq^2 * (R_phys / l_p)^2`
(`log10_F_1m` in the TSV); `max_planck_throat` is the largest throat radius,
in Planck lengths, with F <= 1.  The bound is the flat Ford–Roman Lorentzian
one for the massless scalar, sampled by stationary observers with
tau0 = ell_c (the local curvature scale); `fhat_field_max` documents the
tail illegality of phantom-supported members (the pointwise budget grows
without bound off the throat), never the curve.
