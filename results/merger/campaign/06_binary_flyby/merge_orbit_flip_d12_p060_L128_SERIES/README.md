# The p = 0.60 plunge chain, glued into one wave record

`Weyl4_mode_22.dat` (spheres R = 20/28/36/44, dt = 0.05) joins the chain's packed legs:

| span | leg | note |
|---|---|---|
| 0 – 40 | `merge_orbit_flip_d12_p060_L128_lvl4_t040_lbf_csm` | the exploratory leg |
| 40 – 50 | `..._t100_lbf_csm_r04000` | exact checkpoint restart (Chk04000); the 40-seam has no overlap to compare — the quoted 1.8 % is interpolation clamping at the boundary, not a mismatch |
| 50 – 100 | `..._lvl4from50_chi1e4_t100_lbf_csm_r05000` | the chi-floor leg; on the 50 – 55.4 overlap it agrees with the 1e-8 extension to 1.1e-5 in \|r Psi4\| at R = 20 (0.02 % of the burst peak 7.0e-2) |

Trust t <= 80 (the chi leg's trust window; Weyl4 junk visible on the frames from ~78).
Built 2026-10-05 in the figure pass, reproducible from the three packed streams.
