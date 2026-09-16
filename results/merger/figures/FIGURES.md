# How each `psi4_analysis_*` figure is drawn — and which are stale

Written 2026-09-16, after the strain high-pass fix (`psi4_math`, commit
`b4cc397d`). Until then the corner of the 8th-order high-pass in
`_psd_psi4_to_strain` was `0.05 × freqs.max()`, i.e. 5 % of the **Nyquist** —
a property of how often the waveform was written out, not of the physics. Every
figure below was drawn through that filter, so **panel (f), the strain against
Advanced LIGO, is understated in all of them**, mildly where the stream was
coarse and catastrophically where it was fine.

The command lines were never recorded anywhere, which is why only some of these
could be regenerated. This file is the fix for that: **add the command here when
you draw a figure.**

## Regenerated and verified

Verified by redrawing and comparing pixel-for-pixel against the published PNG:
every panel except (f) came back identical, which is the proof the command line
is the one that drew the original.

| figure | command (after `python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_analysis`) |
|---|---|
| `07_bbh_control/psi4_analysis_bbh_control` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control` |
| `04_binary_headon/psi4_analysis_merge_headon_flip_d8_v1c_latefreeze_t100` | `--run merge_headon_flip_d8_v1c_latefreeze_t100 --group 04_binary_headon` |
| `05_binary_spiral/p012_paper/psi4_analysis_p012_series` | `--run v2_spiral_d12_p012_L128_SERIES --group 05_binary_spiral --name p012_paper/psi4_analysis_p012_series --stream Weyl4_mode_22.dat --m 2 --radii 20 28 36 44 --strain-radius 20` |

## STALE — still drawn through the old filter

Their command lines are not recorded and could not be reconstructed: every
attempt changed panels other than (f), so nothing was overwritten. Panel (f) of
each understates the strain.

| figure | closest reconstruction tried | panels other than (f) that moved |
|---|---|---|
| `07_bbh_control/psi4_analysis_bbh_control_m2` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control --stream psi4_mode_l2_all.dat --m 2` | 0.42 % |
| `05_binary_spiral/psi4_analysis_freeze_narrow_t100` | `--run merge_orbit_flip_d12_r03000+freeze_narrow_t080_r05000+freeze_narrow_t100_r08000 --group 05_binary_spiral` | 18.5 % |
| `05_binary_spiral/psi4_analysis_freeze_wide_t080_m2` | `--run merge_orbit_flip_d12_r03000+freeze_wide_t080_r05000 --group 05_binary_spiral --stream psi4_mode_l2_all.dat --m 2` | 28.8 % |
| `01_single_throat/psi4_analysis_q1e2_ml4_t50` | `--run single_eps_p1e2_q1e2_ml4_t100_r02500 --group 01_single_throat --t-max 50` | 12.0 % |
| `01_single_throat/psi4_analysis_q5e2_gated` | `--run single_eps_p1e2_q5e2_ml4_t100 --group 01_single_throat` | 48.2 % |

The `_m2` figures need `--stream psi4_mode_l2_all.dat` (the combined stream;
`--m` selects a mode out of it and is inert on a single-mode file). The freeze
figures need a restart CHAIN, `--run "parent+child"` — the arm alone starts at
its checkpoint, not at t = 0. Beyond that the missing flags are unknown: the
time window, the radii, the wavelet width and the spectral ceiling are all
options, and `q5e2_gated` was additionally passed through `gate_psi4_junk.py`.

**Before quoting panel (f) of any figure in the stale table, redraw it.** The
other five panels are unaffected by the fix and can be quoted as they stand.
