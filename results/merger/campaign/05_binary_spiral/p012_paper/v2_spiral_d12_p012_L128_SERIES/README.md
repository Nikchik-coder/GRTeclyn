# v2_spiral_d12_p012_L128_SERIES — the p = 0.12 production spiral as one history

The paper's p = 0.12 arm ran in two legs at different resolutions. This is the
two glued into one continuous record, **t = 0 → 60.445**, so a figure draws the
history rather than the schedule.

| leg | run | levels | dx | rows used |
|---|---|---|---|---|
| 1 | `v2_spiral_d12_p012_L128_lvl3_t050` | 3 | 0.0625 | t < 36 (3599–3600 of 5002) |
| 2 | `v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600` | 5 | 0.0156 | t ≥ 36 (all 2444) |

**The join is t = 36 and the finer leg wins the overlap.** Both legs cover
t = 36–50, and over that window their constraint norms agree to a **median
1.3 %** — the splice hides no jump, and refinement does not move the global
constraints. Every glued file carries a three-line provenance header naming the
legs and the rows taken from each.

## Reading it

- **Column order** in `collapse_diagnostics.dat` is `min_lapse, min_chi,
  max_abs_K`, then the min-lapse position and the φ/Π extrema — not
  alphabetical, and there is **no header on a restart**, so leg 2 begins
  mid-file without one.
- **`Weyl4_mode_*.dat` is the waveform to quote**: in-code extraction, four
  spheres at R = 20/28/36/44, ℓ = 2–4 all m, dt = 0.01. The consumer's `psi4_*`
  streams sample once per unit at the python default radii, not this arm's.
- **The ψ₄ here is near-zone, not wave-zone.** The analysis puts ~1 cycle on the
  whole record and returns a wavefront speed of **−0.899 c** between R = 28 and
  36; a negative speed is the signature of a near-zone field, not a propagating
  wave (λ ≈ 46 against R = 20–44). Do not read it as a clean waveform.
- Leg 1's constraint trace carries **22 isolated one- and two-row regrid spikes**
  up to 3.0 against a ~1e-3 baseline. Leg 2 has none above 1.6e-2. They are
  single output rows taken mid-regrid, not a physical excursion.
- **The core and the constraints do not grow together.** After t = 40,
  corr(log max|K|, log ‖H‖) = **−0.35** and corr(log max|K|, log ‖M‖) = **+0.04**.
  The constraint excursion is the merger transient — it peaks at t ≈ 41.2 and
  relaxes below where it started — while max|K| is 0.084 at that peak and only
  begins climbing near t = 49.

## Figures

Under `results/merger/figures/05_binary_spiral/p012_paper/`, each PNG + PDF,
each from a registered module of `grteclyn_wrapper.visualisation.wormhole_merger`:
`p012_collapse_diagnostics`, `p012_series_constraints`, `psi4_analysis_p012_series`.

## Frames and movies

Not packed (≈ 430 MB). The merged slice cache and the 12 re-rendered movies —
61 frames each, one fixed colour scale spanning both legs — are in the run tree
at `runs/wormhole_merger/05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_SERIES/`.
