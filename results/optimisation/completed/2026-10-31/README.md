# Completed D0 evolution and D30/D40 searches

D30 completed 400 CMA-ES evaluations on 2026-10-30 at 23:15 MSK (exit 0).
`d30/*_best_clean.npz` contains the accepted e0316 fields on 210x42. All
three full Newton/constraint checks pass; X = 1.9187333594400104 at matched
J = 1.6059341928143887 and R_e = 4.268787555383. The V=0 bill is
4.3756522176099315. `resolution/` contains every screen decision and the
finalist's independent checks and fields. Zero Newton updates were needed
at each final grid because the initial residual already met its tolerance.
The result is a numerically cleared background; stability is not assessed.
Evolution of this D30 candidate is authorized; see the campaign STATUS for live progress.

D0 failed at t = 88.4175 with a NaN in K on level 3; last finite diagnostic
time is 88.41. The manifest finished at 02:24 MSK on 2026-10-31. Its equatorial
throat first contracts by 0.2%, 1%, 10% at t = 47.35, 59.96, 78.18. The
terminal constraints diverge: late data are diagnostic, not a trustworthy
solution or a survival claim. The article figure fits the areal-radius derivative over the early 0.2–1%
contraction interval (t = 48–60): tau = 7.770715, versus classical
tau = 5.439145, a 30.00% lower growth rate at N128. No continuum claim is made. The matched classical static run is in the spinning pack.

`d0/summary.json` records SHA-256 hashes of all seven original streams;
`.dat.gz` files are losslessly compressed. Parameters retain numerical
settings with deployment paths replaced by `<repo>`. The failure log tail
is included. Frames, slice caches and movies remain on persistent cluster
storage and are never removed by plotfile cleanup. The optimisation instability figure reads the D0 areal-radius stream directly.

D40 completed 400 CMA-ES evaluations at 09:43 MSK on 2026-10-31 (exit 0).
`d40/*_best_clean.npz` contains e0362 on 210x42: X = 1.820747219398,
versus the matched massless X = 4.014901700046 (54.65% reduction).
All three grids pass the existing Newton and independent-constraint gates.
The final E19 and E_c are 9.19e-10 and 4.24e-9; R_e = 4.583555081219
and J = 2.407781150213. No Newton updates were needed on the refined grids,
so their agreement is an interpolation/constraint check, not an independent
continuum-convergence demonstration. Stability remains unassessed.
The archive retains the trace, winning search fields, screened and refined
winners, all screening decisions and the finalist's three diagnostic fields.
Screen-only field arrays remain on the cluster. `archive_manifest.json`
records original and archived hashes; deployment paths are replaced by
`<repo>` in text and NPZ metadata. Numerical arrays are retained unchanged.
The D40 N128 evolution is authorized with checkpoints off; live progress
and its start checks are recorded in the campaign STATUS.
