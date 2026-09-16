# How each `psi4_analysis_*` figure is drawn

Every six-panel wave figure in this tree, with the command that draws it.
**Add the command here when you draw a figure** — the whole reason this file
exists is that none of them were recorded, and recovering eight command lines
from the pixels of the figures they produced cost a day.

Run each from the repository root, after

```
export PYTHONPATH=$PWD/grteclyn-wrapper/src
alias psi4="grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_analysis"
```

| figure | command |
|---|---|
| `01_single_throat/psi4_analysis_q1e2_ml4_t50` | `--run single_eps_p1e2_q1e2_ml4_t100_r02500 --group 01_single_throat --t-max 49` |
| `01_single_throat/psi4_analysis_q5e2_gated` | `--run single_eps_p1e2_q5e2_ml4_t100 --group 01_single_throat --stream psi4_mode_l2m0_gated.dat` |
| `04_binary_headon/psi4_analysis_merge_headon_flip_d8_v1c_latefreeze_t100` | `--run merge_headon_flip_d8_v1c_latefreeze_t100 --group 04_binary_headon` |
| `05_binary_spiral/psi4_analysis_freeze_narrow_t100` | `--run campaign/05_binary_spiral/p012/merge_orbit_flip_d12_r03000/part1/psi4_mode_l2m0.dat+merge_orbit_flip_d12_r03000+freeze_narrow_t080_r05000+freeze_narrow_t100_r08000 --group 05_binary_spiral` (first segment as an ABSOLUTE path) |
| `05_binary_spiral/psi4_analysis_freeze_wide_t080_m2` | `--run campaign/05_binary_spiral/psi4_merger_stitched_0_97.dat --group 05_binary_spiral --m 2 --t-max 80` (absolute path) |
| `05_binary_spiral/p012_paper/psi4_analysis_p012_series` | `--run v2_spiral_d12_p012_L128_SERIES --group 05_binary_spiral --name p012_paper/psi4_analysis_p012_series --stream Weyl4_mode_22.dat --m 2 --radii 20 28 36 44 --strain-radius 20` |
| `07_bbh_control/psi4_analysis_bbh_control` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control` |
| `07_bbh_control/psi4_analysis_bbh_control_m2` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control --stream psi4_mode_l2_all.dat --m 2` |

## How the commands were recovered, and why it can be trusted

Each candidate was redrawn and compared with the published PNG **panel by
panel**. A command is accepted only when every panel that the intervening code
fixes did not touch comes back pixel-identical — that identity, not plausibility,
is the proof. It caught real mistakes: `--m 2` is inert on a single-mode file and
needs `--stream psi4_mode_l2_all.dat`; the freeze figures need the pre-restart
segment, which was split out of its run's pack as `part1/` after the figures were
drawn; `q1e2_ml4_t50` was drawn while its arm was still running and its stream
ended at t = 49.

## What changed in the redraw, and what it means for reading them

Three fixes landed after most of these figures were first drawn. Panels not
listed here are unchanged.

**Panel (f), the strain against Advanced LIGO — every figure.** The corner of
the 8th-order high-pass in `_psd_psi4_to_strain` was `0.05 × freqs.max()`, i.e.
5 % of the **Nyquist** — a property of how often the waveform was written out,
not of the physics (`b4cc397d`). On the finely-sampled in-code streams that put
the corner at f = 2.5 while the burst sits at f = 0.033, suppressing it by
~1e15. The corner is now `1/T`, set by the record. **Panel (f) of every figure
published before 2026-09-16 understates the strain** — mildly where the stream
was coarse, catastrophically where it was fine.

**Panel (b), the ringdown fit — `bbh_control_m2`, `freeze_wide_t080_m2`,
`q1e2_ml4_t50`.** The fit was reaching its own bounds and being drawn anyway:
`q1e2_ml4_t50` published f = 1.959 1/M and `freeze_wide_t080_m2` f = 2.029 1/M,
both far **above their stream's Nyquist of 0.5 and 1.0** — aliases, not
frequencies. `f303b2a9` capped the fit at Nyquist, which then let it walk to the
LOWER bound instead (`bbh_control_m2`, f = 0.001, tau = 0.0: a flat line drawn
as a fit). It now tries three independent seeds, rejects any solution resting on
a bound, and rejects an e-fold more than 5x the segment it was fitted on —
returning no fit rather than a wrong one. Two figures consequently draw **no
ringdown curve**: `freeze_wide_t080_m2` and `q1e2_ml4_t50`, whose records do not
contain a measurable decay (`GPU_PLAN.md` already says so for the latter).

**Panels (c)-(f) of `freeze_wide_t080_m2`.** `--t-min/--t-max` used to clip the
x-axis of panel (a) only, so a figure captioned "to t = 80" analysed everything
the stream held — one figure describing two different records. They now clip the
record, so panels (c)-(f) of this figure are the t = 0-80 wide arm, as its name
has always claimed.
