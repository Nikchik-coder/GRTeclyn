# Upload-ready videos

Seven files, 1920x1080 H.264, 10 fps, ready to upload without further editing.
Built by

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube
```

from the curated masters in `../<group>/<run>/`. Each puts two fields side by
side, in sync, for one encounter.

**Playback is real time, 1x.** The frames are one per code-time unit and the
`t =` label drawn on each panel is the true simulation time, so nothing here
needs the "2x speed" disclaimer the Bondi set carries. Pass `--speed 2` if a
particular upload wants it; the on-frame note follows automatically. The one
exception is `01`: its run's frames are 2 units apart, so it plays t = 0–218 at
2x and its frame says so.

| file | length | shows | run |
|---|---|---|---|
| `01_wormhole_throat_inflates.mp4` | 11.1 s | one throat, kicked inward: it keeps opening (to its trust window, t = 218) | `01_single_throat/single_eps_m1e2_L512_ml5_oct_t400` |
| `02_wormhole_throat_collapses.mp4` | 10.2 s | the same throat, seeded the other way: it closes | `01_single_throat/single_pureq_q1e2_ml4_t100` |
| `03_headon_collision_makes_black_hole.mp4` | 20.2 s | two wormholes collide head-on and make a black hole | `04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100` |
| `04_spiral_merger_without_a_horizon.mp4` | 10.2 s | a spiral merger that never forms a horizon | `05_binary_spiral/v2_spiral_d12_p012_L128_lvl5from0_then_freeze_t0-100` |
| `05_wormhole_flyby_no_merger_mouths_inflate.mp4` | 10.2 s | a fly-by: no merger, both mouths inflate, loudest signal | `06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl5_t100` |
| `06_control_two_black_holes_merge.mp4` | 30.2 s | vacuum control: black holes merge and ring down | `07_bbh_control/bbh_control_d12_p012_t150` |
| `07_control_two_black_holes_fly_apart.mp4` | 20.2 s | vacuum control: the fly-by's momentum, no scalar | `07_bbh_control/bbh_control_d12_p045_t100` |

**Publish 01 and 02 together, and publish the controls with the channels they
control.** Alone, the inflating throat invites "so it is just unstable"; beside
its collapsing twin it shows the branch being chosen. Alone, the fly-by's
loudness invites "that is just a close pass"; beside `07`, which is the same
initial data without the scalar, it is a measurement.

---

# YouTube descriptions

Paste-ready. Shared boilerplate, reused at the foot of each description:

```
Paper: "Merger and Scattering of Traversable Wormholes: Gravitational
Radiation from Unstable Binaries", Nikita M. Shirokov
Code and data: https://github.com/Nikchik-coder/GRTeclyn
Gravity Frontiers: https://www.gravityfrontiers.org/en
First Interstellar Institute: https://www.youtube.com/@First_Interstellar_Institute

Method: Einstein equations coupled to a phantom (ghost) scalar field, the matter
that holds a drainhole wormhole open, evolved in full 3+1 numerical relativity
with the CCZ4 formulation on GPUs (GRTeclyn / AMReX). Adaptive mesh refinement
to five levels. Initial data by superposition of exact drainhole throats, with
the constraint defect declared rather than removed. The t = value on each panel
is the simulation time in code units; the corner note gives the playback speed.
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
both are still open wormholes - and then a single horizon closes over the pair.

LEFT: the conformal factor. Two dark pits approach, meet, and become one.
RIGHT: the lapse, collapsing at the centre as the horizon forms.

The detail that matters: neither mouth ever has a horizon of its own. At every
moment the measurement finds either no trapped surface at all, or one that
encloses BOTH mouths together. The horizon is born common or not at all, so
this is not two black holes merging - it is two wormholes becoming one black
hole in a single step.

Then something a vacuum black hole cannot do. The remnant LOSES mass, falling
from about 3.0 to 2.2 over the run, because what it is swallowing is
negative-energy matter. It settles toward a finite mass with an e-fold of 19.4
code units, and the exotic field's own radiation shuts off on the same clock -
the horizon censors the channel.

The record is one continuous run at maximum refinement from the initial data to
t = 100, with no restart and no mesh seam anywhere in it.
```

## 4. `04_spiral_merger_without_a_horizon.mp4`

**Title:** Two Wormholes Merge With No Horizon At All | Numerical Relativity

```
Two wormhole throats spiral inward and coalesce - and unlike the head-on
collision, no horizon ever appears.

LEFT: the lapse, showing the geometry deepening as the pair comes together.
RIGHT: the real part of the Weyl scalar, the gravitational wave itself, with
the two-lobed pattern of a rotating source sweeping outward.

Every horizon measurement through the whole record finds nothing: zero trapped
surfaces, on three separate centres, at every time sampled. The pair merges as
wormholes.

The run ends at t = 59.94, where the simulation hits a curvature wall and
stops. That is the result rather than a failure, and it was tested: running the
same problem from the start at the finest resolution, with no restart to blame,
kills it at the same place to within one per cent. A horizon can hide a
curvature problem from the outside universe and let a finer grid step past it.
This merger has no horizon to hide behind.

Two honest notes. After t = 59.94 the core of the simulation is frozen by
construction so the exterior can be carried on, so the dark centre stops
evolving and nothing should be read from it; the exterior is checked against
the free run and agrees to 0.1 per cent. And the speckle that appears late in
the wave panel is grid-scale numerical noise well below the measurement floor,
not structure.
```

## 5. `05_wormhole_flyby_no_merger_mouths_inflate.mp4`

**Title:** A Wormhole Fly-By: No Merger, Mouths Inflate, Loudest Signal | Numerical Relativity

```
The same two wormholes, the same separation, four times the momentum. This time
they swing past each other and separate. Nothing merges, and no horizon ever
forms - and as the pair goes by, both mouths inflate.

LEFT: the trace of the extrinsic curvature, which is the field that shows the
expansion. The mouths opening is what the growing structure is.
RIGHT: the lapse.

The surprise is the loudness. This encounter, in which nothing merges and no
horizon exists at any time, is the loudest gravitational-wave channel in the
whole campaign - roughly seventy times a pair of black holes carrying the same
momentum through the same separation. Watch it beside the vacuum control video,
which is this exact initial data with the exotic field removed: there the two
black holes simply coast apart.

There is also a second channel. On the same measurement sphere the exotic
scalar field carries more than twice the energy of the gravitational waves, in
a dipole pattern that a vacuum binary has no analogue for, and it carries that
energy with the opposite sign.
```

## 6. `06_control_two_black_holes_merge.mp4`

**Title:** Control: Two Black Holes Merge, Same Setup Without the Exotic Matter

```
A control run. Identical separation and momentum to the wormhole spiral, with
the exotic scalar field removed. What is left is an ordinary binary black hole.

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

## 7. `07_control_two_black_holes_fly_apart.mp4`

**Title:** Control: The Same Fly-By Without Exotic Matter, and They Just Separate

```
A control run, and the point of it is what does NOT happen.

This is the identical initial data to the wormhole fly-by - same separation,
same momentum, same grid - with the exotic scalar field removed. In vacuum that
momentum is unbound: the two black holes begin at their closest approach and
coast apart, the separation opening from 12 to 21.

LEFT: the conformal factor. RIGHT: the magnitude of the Weyl scalar.

Now compare it with the wormhole fly-by. There, the same momentum is not enough
to escape: the pair falls from 12 all the way in to 4.8, because the exotic
matter makes the attraction about six times stronger, and the mouths inflate as
they pass. The pair of videos is that difference made visible, and the energy
ratio between them is about seventy to one.

A caveat stated plainly: the momentum here is high enough that the standard
boosted-black-hole initial data is outside its strict validity range, which
inflates the vacuum emission. That makes the seventy-fold factor a lower bound.
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
  value in the first frame and the last. That is also why the late frames look
  noisy - see the next point.
- **Late speckle in any wave or curvature panel is noise, not structure.** It is
  real grid-scale noise, confined to the refined mesh levels, and it becomes
  visible only because the physical signal has decayed about two decades below
  the fixed colour scale by then. The paper gates every measurement window ahead
  of its onset. The measurement is explained in `../README.md`.
- **The spiral's last third has a frozen core** and nothing may be read from the
  dark centre there. It is labelled on the frame.
- **Nothing on screen is quantitative.** Every number in the paper and in these
  descriptions is measured from the data files, never from an image.

To rebuild, restyle, or change the field pairing, edit `PANELS` in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger/make_youtube.py`
and re-run it. `--only <substring>` builds one, `--force` overwrites.
