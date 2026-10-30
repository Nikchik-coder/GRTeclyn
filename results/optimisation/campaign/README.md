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

The finite-resolution comparison with the spinning paper rebuilds with
`-m grteclyn_wrapper.visualisation.optimisation.plot_instability_curve`.
Add `--with-history --out /tmp/d21_growth_with_history` to include the two
radius histories beside the growth-rate plot. The article uses the compact
single-column version, replacing its standalone CMA-ES progress figure.
It uses N=128 for every plotted model. Classical inputs and background
headers remain in `results/spinningwormhole/`; potential D21 uses the streams
here and the archived e140 fields to calculate its own throat area. The
physical area includes the saved length scale squared. The x coordinate
therefore uses each solution's own J/A, not the search reference's spin label.

`../figures/instability_curve.tsv` records all plotted rates and fitting times.
The fit is the spinning paper's `rate_tau`: the slope of ln|dR_A/dt| while
the radius changes by 0.2–1%. As in that figure, expansion takes precedence
if a run first contracts and later expands through the interval. For D21,
tau is 6.59223 without the potential and 9.49047 with it, a 30.54% lower
measured rate at N=128. These are neither radial-eigenvalue-screen outputs
nor continuum-extrapolated rates. The article caption records the different
J and outer drive settings; STATUS documents the existing sponge control.
