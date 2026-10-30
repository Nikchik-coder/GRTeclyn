# D21 final evolution diagnostics

Final streams for the N=96,128,192 resolution study, copied on 2026-10-30
from `runs/optimisation/evolution/convergence/`. Each run used L=64,
three extra refinement levels, dt/dx=0.02, dissipation=0.1, and the same
D21 e140 potential. Deployment paths in `params.txt` are placeholders;
all numerical settings are retained.

The `.dat.gz` streams are losslessly compressed. `stream_manifest.json`
records SHA-256 hashes of the original uncompressed bytes. Missing values
in sphere/MOTS diagnostics remain missing. No plotfiles or frames are
needed to rebuild the appendix figure. `constraint_orders.tsv` is generated
from the complete per-level constraints, interpolated to t=10,20,30,40,50;
the two columns are 96->128 and 128->192 using ln(error ratio)/ln(N ratio).

Last finite diagnostic times: 87.5333333, 97.7, 112.16. All runs subsequently
terminated with NaNs. These endpoints are not survival times or statements
of late-time convergence. The figure displays the final histories; the
constraint-order comparison uses t<=50. The first 1% equatorial-radius
contraction occurs at 58.2666667, 67.31, and 80.7, respectively.

Rebuild with the wrapper Python:
`-m grteclyn_wrapper.visualisation.optimisation.plot_convergence`.
