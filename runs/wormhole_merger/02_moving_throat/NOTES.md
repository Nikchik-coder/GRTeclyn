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
