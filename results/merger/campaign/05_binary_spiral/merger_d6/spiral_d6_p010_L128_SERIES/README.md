# The d = 6 merger chain, glued into one wave record

`Weyl4_mode_22.dat` (spheres R = 20/28/36/44, dt = 0.05) is the chain's (2,2) record on one
time axis, built 2026-10-05 from the packed legs:

| span | leg | note |
|---|---|---|
| 0 – 25.5 | `spiral_d6_p010_L128_lvl5from0_t060_lbf_csm` | cut at its trust window (core K runaway; the wave zone is pre-burst there) |
| 25.5 – 30.01 | linear bridge | no leg covers it; pre-burst, amplitude < 1e-3 of the burst peak |
| 30.01 – 35.01 | `spiral_d6_p010_L128_lvl5from30_sig10_chi1e4_t060_lbf_csm_r03000` | its packed stream ends t = 36.67 |
| 35.01 – 100 | `spiral_d6_p010_L128_lvl4from35_t100_lbf_csm_r03500` | the settle leg, clean to its stop |

Seam check on the 35.01–36.67 overlap at R = 20: the two legs agree to 4.6e-7 in |r Psi4|,
0.002 % of the burst peak (2.12e-2). Built by the figure pass; the gluing script is inline in
the session log (GPU_PLAN 2026-10-05) and reproducible from the three packed streams above.

## The scalar record (added 2026-10-05)

`scalar_modes.dat`: the chain's scalar stream (four spheres R = 14/20/30/44,
dt = 1) on one time axis. Unlike the Ψ4 glue above, no bridge is needed: the
sigma-1.0 leg (`spiral_d6_p010_L128_lvl5from25_sig10_t060_lbf_csm_r02500`,
trust to t = 30.5, and the leg the chi leg's checkpoint came from) covers
25.5–30.5, so the legs tile the axis — leg 1 to t = 25, the sig10 leg t = 26–30,
the chi leg t = 31–35, the settle leg t = 36–100. Seam check: on the shared
dt = 1 rows (t = 26 and t = 36) the flux agrees to 1.9e-8, 2 % of nothing
(scale ~1e-3). The common MOTS sits at t = 13 (the chain's own mots_spectral);
the censorship figure's merger arm and the clmGwCensMerger* rows read this file.
