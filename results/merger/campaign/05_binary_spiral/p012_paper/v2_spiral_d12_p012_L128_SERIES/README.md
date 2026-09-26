# v2_spiral_d12_p012_L128_SERIES — the p = 0.12 production spiral as one history

The paper's p = 0.12 arm ran in three legs. This is the three glued into one
continuous record, **t = 0 → 100**, so a figure draws the history rather than the
schedule.

| leg | run | levels | dx | rows used |
|---|---|---|---|---|
| 1 | `v2_spiral_d12_p012_L128_lvl3_t050` | 3 | 0.0625 | t < 36 (3599–3600 of 5002) |
| 2 | `v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600` | 5 | 0.0156 | 36 ≤ t ≤ 60.44 (all 2444) — **no fill** |
| 3 | `v2_spiral_d12_p012_L128_lvl5_t100_freeze_r05700` | 5 | 0.0156 | t > 60.44 (3956 of 4300) — **core frozen from t = 57** |

**Two joins, two different rules.** At t = 36 the finer grid wins: both legs
cover t = 36–50 and their constraint norms agree to a median **1.3 %**. At
t = 60.44 the **unfrozen** leg wins, not the later one — leg 2 keeps its whole
record and leg 3 supplies only what nothing else can. Legs 2 and 3 overlap over
t = 57–60.44 and agree there to **6e-6 of peak** at R = 20 and **exactly** at
R = 36 and 44 (the M6 test, below). Every glued file carries a five-line
provenance header naming the legs and the rows taken from each.

**Leg 3 is why there is a waveform at all.** Leg 2 died at t = 60.445 with a NaN
in h11; on that record ψ₄ was near-zone, one cycle long, and returned a
*negative* wavefront speed. Carrying the same burst out to t = 100 turns it into
an ordered outgoing wave — see below.

## Reading it

- **Column order** in `collapse_diagnostics.dat` is `min_lapse, min_chi,
  max_abs_K`, then the min-lapse position and the φ/Π extrema — not
  alphabetical, and there is **no header on a restart**, so leg 2 begins
  mid-file without one.
- **`Weyl4_mode_*.dat` is the waveform to quote**: in-code extraction, four
  spheres at R = 20/28/36/44, ℓ = 2–4 all m, dt = 0.01. The consumer's `psi4_*`
  streams sample once per unit at the python default radii, not this arm's.
- **The (2,2) ψ₄ is now a wave, and was not before.** On the two-leg record
  (t ≤ 60.44) the analysis put ~1 cycle on the whole record and returned a
  wavefront speed of **−0.899 c** between R = 28 and 36 — the signature of a
  near-zone field. With leg 3 the record carries **3 cycles** and the front is
  ordered outward across every sphere pair: **0.908 c** (20→28), **0.928 c**
  (28→36), **0.931 c** (36→44). E_rad = 5.72e-4 M at R = 20.
- **The ringdown fit is NOT the remnant's.** It reads f = 0.0311 1/M,
  τ = 34.4 M — strikingly close to the BBH control's 0.0290 / 35.0 M — but the
  fill freezes the throat itself (the oriented scan puts it at r = 0.73–0.86,
  with the |K| spike on top of it and no horizon to hide the fill behind), so
  leg 3 transports a burst that was already generated and does not evolve a
  remnant. Quote the burst; do not quote this as a QNM.
- **(2,0) is still not clean:** its wavefront speed is **−0.601 c** between
  R = 28 and 36 and only 0.917 c on the outermost pair.
- Leg 1's constraint trace carries **22 isolated one- and two-row regrid spikes**
  up to 3.0 against a ~1e-3 baseline. Leg 2 has none above 1.6e-2. They are
  single output rows taken mid-regrid, not a physical excursion.
- **The core and the constraints do not grow together.** After t = 40,
  corr(log max|K|, log ‖H‖) = **−0.35** and corr(log max|K|, log ‖M‖) = **+0.04**.
  The constraint excursion is the merger transient — it peaks at t ≈ 41.2 and
  relaxes below where it started — while max|K| is 0.084 at that peak and only
  begins climbing near t = 49.

## Figures

`results/merger/figures/05_binary_spiral/p012_collapse_diagnostics` (PNG + PDF,
the paper's `fig:spiral_collapse`, by `plot_spiral_collapse`); its constraint
norms are panel (f) of `figures/00_code_health/constraint_evolution`. The
series' `psi4_analysis` and constraint pages were retired from `figures/` on
2026-09-26 (not in the paper); `plot_psi4_analysis` still draws them on demand.

## Frames and movies

Not packed (≈ 430 MB). The merged slice cache and the 12 re-rendered movies —
61 frames each, one fixed colour scale spanning both legs — are in the run tree
at `runs/wormhole_merger/05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_SERIES/`.

## M6: does the fill touch the waveform?

Leg 3 and leg 2 share t = 57.01–60.44 — same grid, same t = 57 checkpoint, the
only difference being `core_freeze_fill`. Over those 344 rows:

| mode | R | max \|Δ(r·Ψ₄)\| | % of peak | overlap |
|---|---|---|---|---|
| (2,2) | 20 | 1.62e-06 | 0.0057 % | 1.00000000 |
| (2,2) | 28 | 1.0e-14 | 0.0000 % | 1.00000000 |
| (2,2) | 36 / 44 | **0** | 0.0000 % | 1.00000000 |
| (2,0) | 20 | 2.55e-06 | 0.0133 % | 1.00000000 |
| (2,0) | 28 | 1.2e-15 | 0.0000 % | 1.00000000 |
| (2,0) | 36 / 44 | **0** | 0.0000 % | 1.00000000 |

The two outer spheres are **byte-identical**. The fill does not touch the
waveform over the window where the comparison exists.

**But read how the R = 20 difference arrives.** It is not a causal arrival: it
appears at t = 57.22, **0.22 units after engagement**, at 1e-13, and grows to
1.6e-6 by t = 60.44. A signal at speed 1 from the skin at r = 1.9 cannot reach
R = 20 before t = 75.1. Under 1+log slicing the gauge speed is √(2/α) ≈ 27 where
the lapse is 2.7e-3, which puts the transit at ~0.7 units — so **the causal
budget's light-speed bound does not hold for the gauge sector**, and what
protects the waveform is amplitude (five orders below signal), not causality.
The growth decelerates (e-fold 0.2 units early, 1.1 units by the end) but has
not stopped when the comparison window closes.

**M6 validates t = 57–60.44 against the unfrozen twin; the radius-insensitivity
twin covers the rest (2026-09-19).** `v2_spiral_d12_p012_L128_lvl5_t100_freeze2`
re-ran the freeze arm from the same t = 57 checkpoint and binary with only the
fill window moved, 1.40/1.90 → 1.25/1.75, and the (2,2) waveform moved by at
most **0.385 / 0.370 / 0.024 / 0.013 % of peak at R = 20/28/36/44** over
t = 57–100 (overlap 0.999999+). The fill is not in the physics, and **the late
record is quotable** — still as transported burst plus contamination clocks,
never as a remnant QNM (the physical caveats above stand unchanged).
