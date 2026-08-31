# 00_archive -- dead ends kept for the record

Moved out of the old top-level `INDEX.md` on 2026-08-31 when this folder
was split by campaign stage. Content unchanged.

Kept for the record, nothing current depends on them.

* `phase2_puncture/` -- the pre-drainhole setup (Brill-Lindquist puncture mass).
  `p2_ml3/4/5`, `p2_sym`, `p2_watch_l4` all NaN; `p2_ml2_lapse0` reached t = 8.
  Superseded: the puncture drives chi -> 0 *at the throat*, which is what made the
  throat unresolvable.  The drainhole carries its mass in the lapse instead.
* `stage0_t0/` -- t = 0 only, at max_level 0/1/2.  These verified that the numerical
  initial data reproduces the closed-form drainhole to ~1e-16 at every radius.
* `stage1_probes/` -- short diagnostic runs: the refinement ladder
  (`stage1_ml0_*` NaN at t = 0.22, `stage1_ml1_lapse6` NaN at t = 1, so *more*
  refinement helps here, opposite to puncture data), the dense origin probe
  (`ml0probe_lapse5`), and the first sigma A/B (`sig00_lapse5`, `sig05_lapse5`,
  both to t = 2 at max_level 0).
