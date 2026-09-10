# 03_two_throats — what do two throats do to each other?

Answer: **two identical throats push each other apart, and reversing the field
direction of one turns that push into a pull.** Measured 2026-08-31, four runs.

Same body throughout: drainhole initial data (`wormhole_id_type = 1`, ADM mass carried
in the lapse), a = 2, m = 1, separation d = 12 on the x-axis, L = 64, N = 128,
`max_level = 3`, lapse type 5, sigma 0.1, moving refinement boxes on both throats.
Each run below changes exactly one thing from that baseline.

| run | the one thing it changes | result |
| --- | --- | --- |
| `orbit_d12_p012` | tangential push P = ±0.12 | **separates.** Stopped at t = 20 having opened 2.02 units, still accelerating apart |
| `ctrl_rest_d12` | nothing — released from rest | **separates anyway:** +0.0127 outward, +0.47 by t = 11.5 |
| `ctrl_rest_a1` | throat width a = 1 | **separates 3.0× weaker:** +0.0042 outward |
| `ctrl_flip_d12` | `wormhole_phi_sign_B = -1` | **falls together:** −0.0196 inward, −0.56 by t = 10.5 |

## Why these four and not one

Each kills a competing explanation for the baseline's separation.

- **Was it the initial sideways push?** No — `ctrl_rest_d12` has zero momentum and still
  separates, at the same acceleration.
- **Does the repelling force track mass, or throat width?** Width. Halving the radius in
  `ctrl_rest_a1` cut the push 3.0×; a mass-tracking force would not have moved at all.
  (Predicted 4.0×; the gap is the coordinate under-read, which does not cancel here
  because the two arms have different widths.)
- **Does the field orientation set the sign?** Yes, and by the predicted amount. This is
  the decisive measurement, because `ctrl_flip_d12` differs from `ctrl_rest_d12` in one
  parameter and nothing else, so even the coordinate under-read cancels between them:

      |infall_C| / |escape_A| = (1 + 5)/(5 - 1) = 1.500   predicted
                              = 1.511 +/- 0.033           measured, 15 times, t = 3.5 .. 10.5

| t | A: like charges | C: opposite | ratio |
| --- | --- | --- | --- |
| 4.0 | +0.0146 apart | −0.0219 together | 1.49 |
| 6.0 | +0.0679 apart | −0.0998 together | 1.47 |
| 8.0 | +0.1672 apart | −0.2478 together | 1.48 |
| 10.0 | +0.3172 apart | −0.4827 together | 1.52 |

## How the numbers were measured

Not from `throat_track.dat` — its quantum is ~0.03 at dx = 0.0625, which is the entire
early displacement. Every number here is an inverse-χ-weighted centroid of the pit taken
from the cached slices in `<run>/frames/_slice_cache/chi_z/`, which is sub-cell and smooth
at the 1e-4 level. Coordinates also under-read physical motion for roughly the first five
time units while the gauge settles, so nothing before t ≈ 3 is used.

Full argument, with the scalar-charge derivation: `research/merger/Plan.md` §8.
