# Upload-ready videos

Nine files, 1920x1080 H.264, 10 fps, ready to upload without further editing.
Built by

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube
```

from the curated masters in `../<group>/<run>/`. Each puts two fields side by
side, in sync, for one encounter. **The channel is First Interstellar
Institute** — the in-panel ownership mark reads `FII` and the credit line on
every frame carries the full name; **Gravity Frontiers is the research
sponsor** and is credited there too. Rebuilt 2026-10-05 on the constraint-solved
(csm) records: 03–05 replaced their pre-solve versions, 06 and 07 are new, the
controls moved to 08/09, and the old `04_spiral_merger_without_a_horizon.mp4`
was DELETED — its claim did not survive the clean data (the d = 6 merger forms
a horizon; see 04).

**Playback is real time, 1x.** The frames are one per code-time unit and the
`t =` label drawn on each panel is the true simulation time. Pass `--speed 2`
if a particular upload wants it; the on-frame note follows automatically. The
one exception is `01`: its run's frames are 2 units apart, so it plays
t = 0–218 at 2x and its frame says so.

| file | length | shows | run |
|---|---|---|---|
| `01_wormhole_throat_inflates.mp4` | 11.1 s | one throat, kicked inward: it keeps opening (to its trust window, t = 218) | `01_single_throat/single_eps_m1e2_L512_ml5_oct_t400` |
| `02_wormhole_throat_collapses.mp4` | 10.2 s | the same throat, seeded the other way: it closes | `01_single_throat/single_pureq_q1e2_ml4_t100` |
| `03_headon_collision_makes_black_hole.mp4` | 10.2 s | two wormholes collide head-on and make a black hole (horizon born common at t = 18) | `04_binary_headon/headon_csm_L128_stitched_t0_t100` |
| `04_spiral_merger_makes_black_hole.mp4` | 10.2 s | the orbital merger — and a horizon DOES form (MOTS from t = 13) | `05_binary_spiral/spiral_d6_p010_L128_csm_stitched_t0_t100` |
| `05_wormhole_flyby_no_merger_mouths_inflate.mp4` | 6.5 s | a fly-by: no merger, no horizon, both mouths inflate | `06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` |
| `06_plunge_merger_no_horizon_yet.mp4` | 8.2 s | a deeper plunge: the pair merges as wormholes and the horizon stalls | `06_binary_flyby/merge_orbit_flip_d12_p060_L128_csm_stitched_t0_t80` |
| `07_hardest_plunge_hits_a_curvature_wall.mp4` | 4.7 s | the hardest plunge: mouths inflate on approach, the merged core hits the K wall | `06_binary_flyby/merge_orbit_flip_d12_p090_L128_csm_stitched_t0_t45` |
| `08_control_two_black_holes_merge.mp4` | 30.2 s | vacuum control: black holes merge and ring down | `07_bbh_control/bbh_control_d12_p012_t150` |
| `09_control_two_black_holes_fly_apart.mp4` | 20.2 s | vacuum control: the fly-by's momentum, no scalar | `07_bbh_control/bbh_control_d12_p045_t100` |

**Publish 01 and 02 together, and publish the controls with the channels they
control.** Alone, the inflating throat invites "so it is just unstable"; beside
its collapsing twin it shows the branch being chosen. Publish 05–07 as the
momentum ladder they are: the same pair at p = 0.25, 0.60 and 0.90 — scatter,
stalled merger, wall — is one story told three times louder.

---

# YouTube descriptions

Paste-ready. Shared boilerplate, reused at the foot of each description:

```
Paper: "Merger and Scattering of Traversable Wormholes: Gravitational
Radiation from Unstable Binaries", Nikita M. Shirokov
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.youtube.com/@First_Interstellar_Institute
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en

Method: Einstein equations coupled to a phantom (ghost) scalar field, the matter
that holds a drainhole wormhole open, evolved in full 3+1 numerical relativity
with the CCZ4 formulation on GPUs (GRTeclyn / AMReX). Adaptive mesh refinement.
Initial data by superposition of exact drainhole throats with the constraints
SOLVED (far-side matching), and horizons measured with a 3D spectral finder on
every output. The t = value on each panel is the simulation time in code units;
the corner note gives the playback speed.
```

---

## 1. `01_wormhole_throat_inflates.mp4`

**Title:** A Wormhole Throat Blows Open | Full Numerical Relativity

```
A single wormhole throat, held open by exotic matter, is given a tiny nudge
inward. It does not collapse. It keeps opening, 3.8 times wider by t = 218, and
no horizon forms around it.

LEFT: the phantom scalar field, the exotic matter that holds the throat open.
Its dark core is the throat, and it widens as the throat inflates.
RIGHT: the lapse, the rate at which time runs at each point.

A wormhole of this kind is an unstable fixed point, like a pencil balanced on
its tip. It has exactly two ways to fall, and the first perturbation decides
which: inflate, as here, or collapse to a black hole, as in the companion video.

Until t = 40 the throat grows exponentially in its own proper time, at close to
the rate Shinkai and Hayward found for such throats in spherical symmetry. Then
the lapse falls almost to zero at the throat, so the throat's own clock nearly
stops against the simulation's: from t = 40 to 218 only about 5 units of its
time pass, and its growth per unit of simulation time slows. That is the time
slicing, not the throat. No horizon forms: the throat stays anti-trapped, the
mirror image of a black hole's trapped surface.

The video stops at t = 218. After that a gauge wave reflected off the edge of
the simulation box comes back to the throat, and nothing later is trusted.
Played at 2x speed.

Watch it beside "A Wormhole Throat Collapses" - same throat, opposite fate.
```

## 2. `02_wormhole_throat_collapses.mp4`

**Title:** A Wormhole Throat Collapses Into a Black Hole | Full Numerical Relativity

```
The same wormhole throat as the companion video, given a different
perturbation. This time it closes, and a horizon forms at t = 33.

LEFT: the conformal factor, the throat as a dark pit that deepens.
RIGHT: the lapse, the rate at which time runs at each point. It dips at the
centre as the throat closes. It falls in the inflating video too; what tells the
two apart is the search for trapped surfaces, which finds a horizon here and
none there.

The pair of videos is the actual result. A drainhole wormhole is an unstable
fixed point with two branches, and the perturbation it is given selects which:
an inward spherical kick opens it, as in the companion video, and the
quadrupole used here closes it. With a spherical kick the choice is just as
sharp - push outward by one per cent and the horizon forms at t = 11, push
inward by the same amount and the throat inflates instead. The instability is
fast either way, an e-fold of a few code units, which is why a wormhole of this
class cannot survive long enough to do anything slow.

This particular run carries a quadrupole and no radial kick at all, which is
what lets it radiate: a perfectly spherical collapse cannot emit gravitational
waves, by symmetry. So it is both the collapse case and the campaign's cleanest
measurement of what a collapsing throat sounds like.
```

## 3. `03_headon_collision_makes_black_hole.mp4`

**Title:** Two Wormholes Collide Head-On and Form a Black Hole | Numerical Relativity

```
Two wormhole throats are released from rest and fall together. They touch while
both are still open wormholes - and then a single horizon closes over the pair
at t = 18.

LEFT: the conformal factor. Two dark pits approach, meet, and become one.
RIGHT: the lapse, collapsing at the centre as the horizon forms.

The detail that matters: neither mouth ever has a horizon of its own. At every
moment the 3D horizon finder sees either no trapped surface at all, or one that
encloses BOTH mouths together. The horizon is born common or not at all, so
this is not two black holes merging - it is two wormholes becoming one black
hole in a single step.

Then something a vacuum black hole cannot do. The remnant LOSES mass, from 2.82
at the horizon's birth to 2.39 by t = 100, because what it is swallowing is
negative-energy matter. By the end it sits almost perfectly round, its horizon
tracked on every output by a spectral finder solving the full trapped-surface
equation.

Honest notes: the initial data here has the constraints solved, not just
declared, and the record is a chain of three runs at different resolutions,
joined at t = 35 and t = 50 and verified to agree across each seam. The faint
speckle far from the remnant late in the video is grid-scale numerical noise
below the measurement floor, not structure.
```

## 4. `04_spiral_merger_makes_black_hole.mp4`

**Title:** Two Wormholes Spiral In, Merge, and Form a Black Hole | Numerical Relativity

```
Two wormhole throats, set orbiting at separation 6, spiral together in half an
orbit - and a single horizon closes over both while they are still wormholes.

LEFT: the conformal factor, the two throats as dark pits that merge into one.
RIGHT: the lapse, the rate at which time runs, collapsing over the remnant.

The horizon appears at t = 13, enclosing BOTH mouths at once: like the head-on
collision, the orbital merger makes its black hole in a single step, with
neither mouth ever trapped on its own. The remnant then does what a wormhole
remnant does and a vacuum one cannot - it loses mass, 2.80 to 2.44 by t = 100,
by swallowing the negative-energy field that held the throats open, and settles
toward a round, quiet black hole.

An honest note on the record: no single simulation survives this merger's core.
The movie is one certified chain of four runs - each restart verified against
its parent before the previous one failed - carried through two distinct
numerical walls (one cured by stronger dissipation, one by a floor on the
conformal factor). The constraints stay two orders of magnitude inside the
campaign's quality cut the whole way, and the horizon history is continuous
across every seam.
```

## 5. `05_wormhole_flyby_no_merger_mouths_inflate.mp4`

**Title:** A Wormhole Fly-By: No Merger, No Horizon, and the Mouths Inflate | Numerical Relativity

```
Two wormholes at separation 12, each carrying momentum 0.25. They swing past
each other - closest approach 2.33 - and separate. Nothing merges, no horizon
ever forms, and as the pair goes by, both mouths INFLATE.

LEFT: the trace of the extrinsic curvature, the field that shows expansion.
The growing structure is the mouths opening.
RIGHT: the lapse.

The encounter is loud. A close pass this deep radiates far more gravitational
energy than a vacuum black-hole pair on the same trajectory (video 09 is that
control: without the exotic field the same momentum just coasts apart, because
the phantom field makes the mutual pull several times stronger). And there is a
second channel a vacuum binary cannot have at all: the exotic scalar field
itself radiates, in a dipole pattern, carrying its energy with the opposite
sign.

The video stops at t = 63, where the quality of the solution (the constraint
norms) stops meeting the campaign's cut; the close pass and the whole burst
happen well inside it.
```

## 6. `06_plunge_merger_no_horizon_yet.mp4`

**Title:** Two Wormholes Merge and the Horizon Stalls | Numerical Relativity

```
The fly-by's momentum raised to 0.60 - and the pair no longer escapes. The
mouths plunge, touch at t = 40, and merge into one object. Then the expected
horizon... does not come.

LEFT: the conformal factor, the two pits plunging and merging.
RIGHT: the real part of the Weyl scalar - the gravitational wave itself. This
plunge is the loudest gravitational-wave source in the whole campaign.

Through the entire record the 3D horizon finder closes in on a trapped surface
that never quite closes: a pinched, peanut-shaped surface that stays marginally
untrapped, slowly rounding, heading for closure around t = 110-115 - past the
end of the simulation. That stall was tested, not assumed: rerunning the merger
at double the core resolution gives the same untrapped surface with the same
numbers. The delay is physics, not a numerical artefact - a wormhole merger
whose black hole takes this long to be born.

Honest notes: the simulation crossed a numerical wall at t = 55 (a single grid
cell's conformal factor steepening without limit) and was carried through it by
a floor on that one variable, a cure proven against an independent merger that
survived without it. The video stops at t = 80, where the solution leaves the
campaign's quality cut; the merger and the full wave burst sit well inside.
```

## 7. `07_hardest_plunge_hits_a_curvature_wall.mp4`

**Title:** The Hardest Wormhole Plunge Ends at a Curvature Wall | Numerical Relativity

```
Momentum 0.90 per mouth - the hardest plunge in the campaign. The pair falls
from separation 11.8 to 2.6 in forty time units and merges violently. Watch the
curvature field on the approach: both mouths visibly inflate as they close in,
the same opening-up the fly-by shows, now feeding straight into a merger.

LEFT: the conformal factor. RIGHT: the trace of the extrinsic curvature.

At t = 45.3 the record ends: the curvature at the merged core runs away, nearly
doubling every step, and the simulation dies. That wall is a result, not a
glitch. The same failure class appeared in the d = 6 orbital merger (video 04),
where only finer resolution at the core - not any numerical trick - carried the
evolution through. Here the burst of the merger had not yet cleared the
measurement spheres, so this encounter's energy budget is still an open item on
exactly that route: rerun the core finer and watch the wall move.

No horizon is found at any time before the end. Whether this remnant traps
behind a horizon - as the head-on and d = 6 mergers do - or stalls like the
p = 0.60 plunge is what the finer continuation will decide.
```

## 8. `08_control_two_black_holes_merge.mp4`

**Title:** Control: Two Black Holes Merge, Same Setup Without the Exotic Matter

```
A control run. The d = 12 wormhole spiral's separation and momentum, with the
exotic scalar field removed. What is left is an ordinary binary black hole.

LEFT: the conformal factor, two punctures orbiting and merging.
RIGHT: the magnitude of the Weyl scalar, the gravitational wave.

This is the textbook case, and it is here to be compared against. The frequency
climbs as the two holes spiral together - the chirp that gravitational-wave
detectors are built to find - and settles onto the ringdown tone of the final
Kerr black hole.

The wormhole channels never do this. They are short, they do not chirp, and
where a black hole remnant would hold its ringdown frequency, theirs falls or
drifts. That difference is the observational signature, and this video is the
reference it is measured against.
```

## 9. `09_control_two_black_holes_fly_apart.mp4`

**Title:** Control: The Same Fly-By Without Exotic Matter, and They Just Separate

```
A control run, and the point of it is what does NOT happen.

Two black holes with the wormhole fly-by's separation and momentum, and no
scalar field. In vacuum that momentum is unbound: the holes begin at their
closest approach and coast apart, the separation opening from 12 to 21.

LEFT: the conformal factor. RIGHT: the magnitude of the Weyl scalar.

Now compare it with the wormhole fly-by (video 05). There, the same class of
encounter is not unbound: the exotic matter makes the attraction several times
stronger, the pair falls deep, and the mouths inflate as they pass - and the
pass radiates far harder than this vacuum swing-by does. The pair of videos is
that difference made visible.

A caveat stated plainly: the momentum here is high enough that the standard
boosted-black-hole initial data is outside its strict validity range, which
inflates the vacuum emission - so the wormhole-to-vacuum energy ratio read
from this pair is a lower bound.
```

---

## Tags

```
numerical relativity, general relativity, wormhole, Einstein-Rosen bridge,
exotic matter, negative energy, black hole, event horizon, gravitational waves,
spacetime, Einstein equations, astrophysics, computational physics,
GPU simulation, CCZ4, gravitation, theoretical physics
```

---

## Honest limits, worth knowing before captioning anything

- **The 1080p is upscaled, not native.** Source panels are about 630 px wide, so
  this is roughly a 1.5x Lanczos enlargement. It looks clean because these are
  smooth fields rather than fine detail. Native high-resolution rendering is no
  longer possible for most of these: the plotfiles were pruned after each run.
- **Colour bars are fixed** over each whole series, so a colour means the same
  value in the first frame and the last. K is drawn on one fixed LINEAR scale
  (the series' own envelope) since 2026-10-05 — frame 0 of a K panel is
  uniformly the zero colour because K is identically zero in the initial data;
  that is correct, not a blank frame.
- **Late speckle in any wave or curvature panel is noise, not structure.** It is
  real grid-scale noise, confined to the refined mesh levels, and it becomes
  visible only because the physical signal has decayed far below the fixed
  colour scale by then. The paper gates every measurement window ahead of its
  onset. The measurement is explained in `../README.md`.
- **Every video stops at its run's trust window** (`../../trust_windows.tsv`):
  05 at t = 63, 06 at t = 80, 07 at t = 45 (there the simulation's death IS the
  record's end), the others at their full records. Nothing on screen after a
  trust window exists in any video.
- **Nothing on screen is quantitative.** Every number in the paper and in these
  descriptions is measured from the data files, never from an image.

To rebuild, restyle, or change the field pairing, edit `PANELS` in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger/make_youtube.py`
and re-run it. `--only <substring>` builds one, `--force` overwrites.
