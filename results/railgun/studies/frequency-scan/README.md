# Fixed-frequency compactness continuation

Four points, omega=0.85 / 0.82 / 0.79 / 0.76, passed independent three-grid validation on 72x10 / 96x12 / 128x16. Each accepted state is under its frequency_NN directory. All require two fresh Newton corrections per grid, unchanged equation and convergence gates, nonvacuum charge and a nodeless scalar.

The omega=0.73 point converged in Newton but failed the unimposed constraint_c on 72x10: 3.2500948527e-8 exceeds 1e-8. The bounded scan stopped there; omega=0.70 and 0.67 were not attempted. No accepted state exists for the rejected point. This is not a physical maximum or proof that the branch ends.

Last accepted omega=0.76: M=1.3138907701823674, J=-1.379462933768464, sampled lapse minimum 0.5581755286136367, sampled maximum shift/lapse 0.2519070390151452, sampled g_tt maximum -0.2954543563393655. No sampled ergoregion. Density peak near cylindrical radius 1.7753; dynamical stability and particle transport on this stronger ring remain untested.

Thirteen solves, code 023f4384, 17:35:17–17:40:03 MSK on November 1, 2026. Four threads, 160 GiB address-space cap, GPU card 0 on the second node, 1800 s hard timeout, Jacobian chunks 128. No AMR checkpoints or scratch plotfiles. Source SHA and exact settings are in manifest.json. Every completed and rejected field, diagnostic and execution log is retained.
