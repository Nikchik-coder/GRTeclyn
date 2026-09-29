# 02_moving_throat -- does a MOVING throat survive?

Moved out of the old top-level `INDEX.md` on 2026-08-31 when this folder
was split by campaign stage. Content unchanged.

`s20_boost_p02`, 2026-08-31.

Stage 2.0 shakedown: the Stage 1 baseline (a=2, m=1, sigma=0.1, lapse 5,
max_level=3, tagging_L=64) with a Bowen-York boost P=0.2 along z, followed by
the new moving-box tagger (tagging_type=2) driven by ThroatTracker
(throat_track.dat: offsets from center, pit chi, cells averaged).  Questions:
(1) do the moving boxes hold a throat crossing the grid; (2) where does the
wall land when the seed is 4.5e-6 (BY discretisation) instead of exact zero.
t=0: Ham 2.1e-3 (unchanged), Mom 4.5e-6, pit chi 4.11e-7 at (0,0,0), 18.3 u/h.

**Outcome: completed t = 40.** Crossed 3.3 grid units, zero lost rows, no NaN.
This is the shakedown the whole two-throat programme is built on.

## `contraction_t0/` (2026-09-29) -- the moving throat is Lorentz-contracted

Five exact-boost throats (momentum model 1), p = 0 / 0.12 / 0.25 / 0.35 / 0.45, L = 64
level 3, each a start-up to t = 0.5. The throat's chi-contour axis ratio (along / across
the motion) matches 1/gamma = 1/sqrt(1 + p^2) to 3e-5 at every p and three contour
levels: 1.00000 / 0.99288 / 0.97015 / 0.94387 / 0.91195. The source of
`figures/02_moving_throat/boost_contraction` (`plot_boost_contraction`; the table and
slices are packed as `boost_contraction_t0.tsv` / `_slices.npz`).

## `csm/` (2026-09-29) -- the Bowen-York momentum probes

`single_rest_csm_t050`, `single_boost_p012_csm_t050`, `single_boost_p045_csm_t050`:
Bowen-York momentum on a round throat with its scalar at rest inflates it (+9.9 % at
t = 32 for p = 0.12, +24 % at t = 25 for p = 0.45); the rest throat stays put. A setup
artefact, not physics: see `contraction_t0/` and STATUS, "CRITICAL FINDING".
