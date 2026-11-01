# Accepted omega=0.73 resolution recovery

Independent three-grid validation passes on 96x12 / 128x16 / 160x20, with two fresh Newton corrections per grid and observable relative drift 1.1599867707e-9 against 1e-6.

Only grids changed. The unimposed constraint C falls from 3.25009e-8 on the old 72x10 grid to 7.77588e-10, 6.99426e-11 and 2.01051e-10, all below the unchanged 1e-8 gate. Residuals do not decrease monotonically at their smallest magnitudes. The rejected coarse field was an initial guess only; its archive remains unchanged, and seed_provenance.json records its SHA.

Final M=1.2973467762442072, J=-1.3571709385611497, minimum sampled lapse=0.49280423128552964, maximum shift/lapse=0.35420574542928956, maximum sampled g_tt=-0.2171948085947071. No sampled ergoregion. Density peak near cylindrical radius 1.44861. Stability and particle transport on this stronger background remain untested; this is not a maximum-spin result.

Three solves, code e7fed22c, November 1, 2026, 17:45:27–17:47:04 MSK. Second GPU node/card 0, four threads, 160 GiB address-space cap, 1800 s hard timeout, Jacobian chunks 128. No AMR checkpoints or scratch plotfiles. Lower frequencies were not launched.
