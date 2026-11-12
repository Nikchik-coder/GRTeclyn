# Completed D80/D90 low-mass searches

Both original CMA-ES searches completed 400 proposals with exit 0. Each fixes
its classical reference's equatorial throat radius, spin and asymptotic redshift.
The mass box is [0.001,0.20], with q_i in [-2,8]. This is a potential-family
experiment, not a claim of a global minimum or dynamical stability.

The independent recovery fields are **d80/recheck/validated.npz** and
**d90/recheck/validated.npz**. D80 gives X=1.069974516105 versus massless
1.419239991186 (24.61% lower). D90 gives X=0.611923753610 versus massless
0.599549029786 (2.06% higher). The latter did not improve the massless model.

All three perturbed-seed recovery solves pass. D80 takes 2/3/2 Newton updates
on 150x30, 180x36 and 210x42; D90 takes 2/2/2. Last-pair relative X drifts are
2.52e-12 and 1.06e-11. Final unused Einstein residuals (E19,E_c) are
(1.13e-10,4.11e-10) and (1.08e-10,3.30e-10), respectively. Stability remains
not assessed.

The original searches' `search/*_best_clean.npz` and `*_refine` records are
retained for provenance. Those checks accepted the interpolated polynomial
without a Newton update, so their automatic resolution-validated label is
superseded by the perturbed recheck. The original arrays are not altered.
The recheck code is 87d52379; the original search code is 3e11fa5f.

The pack contains complete evaluation traces, selected coarse/screened/final
fields, all finer-grid acceptance decisions, original and recovery logs and
commands. Other candidate and screen field arrays remain on persistent cluster
storage. No live extension is packed here. `archive_manifest.json` records
source paths, source hashes and archived hashes; deployment prefixes in text
are removed. SHA256SUMS verifies the archive, including this description.
