# Quantum-budget campaign — measured data

Campaign F (plan: `research/optimisation/Quantum Budget Wormhole Search.md`,
status: `research/optimisation/STATUS.md`).  Everything here rebuilds from a
clean checkout on CPU; no run output is involved.

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
