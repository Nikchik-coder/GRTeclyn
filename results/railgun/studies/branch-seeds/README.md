# Discrete-field homotopy starts

All six GPU quadratic KG eigenproblems found resolved nodeless modes on the fixed accepted weak k=1 metric. The original source stays a separate k=1 species; the new field is added at amplitude 0.001. These are unaccepted, non-self-consistent homotopy starts.

New k=+2, even, m=2.5: frequency 2.27550495976450. New k=+2, even, m=3: 2.71592329657889. New k=+1, odd, m=1: 0.954517406940391. Two-grid relative differences are 5.27e-15, 2.62e-14 and 6.51e-15, respectively. Printed scalar-equation errors remain below 1e-8.

Next requires a nonlinear amplitude homotopy: grow the new field and remove the original species, then recover a pure heavy or odd branch independently. Only after recovering a pure heavy inner ring can an outer k=-6 or -8 species be seeded. This screen makes no final two-ring, stacked, vacuum-gap or stability claim.

Six eigenproblems, code dc576c85, second GPU node/card 1, 18:39:30–18:39:42 MSK on November 1, 2026. Numerical work 8.53 s. Four threads, 160 GiB, 1800 s hard timeout, chunks 128; no AMR checkpoints or plotfiles. Every seed remains validated=false.
