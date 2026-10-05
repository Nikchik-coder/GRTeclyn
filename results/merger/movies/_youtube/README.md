# Upload-ready videos

Ten files, 1920x1080 H.264, 10 fps, ready to upload without further editing.
Built by

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube
```

**Layout (2026-10-05, the user's design): four panels, 2x2, in sync** -- curvature
K (top left), lapse (top right), conformal factor chi (bottom left), the wave Re(Psi4)
(bottom right), each named in the margin beside it. Exceptions, each because
that run has no usable alternative: 01 shows phi in place of the wave (the run
rendered no Weyl scalar); 02 shows Pi in place of the wave (its Psi4 frames were
drawn on a scale set by late junk and have no slice cache to redraw); 08 and 09
show |Psi4| in place of K (their K was drawn live on a flooding symlog scale,
again with no cache to redraw). **03, 04, 05 and 07 are zoomed x2** about the
centre (`zoom_frames.py`: the cached slices cropped to the central half and
redrawn on fixed scales measured over the zoomed series); 01 and 10 are redrawn
unzoomed with better scales (01's chi on a log scale, 10's wave on 2.5 decades
of symlog). Every wave panel is symmetric-log, K is linear. The sources are the
`youtube/` and `youtube_zoom2/` subsets beside each curated set.

**Branding.** The channel is First Interstellar Institute: its mark `FII` is
printed inside every panel's plot area, so it cannot be cropped off without
cropping the data. **Gravity Frontiers, the research sponsor,** is named in full
beside the grid ("Research sponsored by GRAVITY FRONTIERS"); the credit line at
the foot carries both names.

**Playback is real time, 1x.** The frames are one per code-time unit and the
`t =` label drawn on each panel is the true simulation time. Pass `--speed 2`
if a particular upload wants it; the on-frame note follows automatically. The
one exception is `01`: its run's frames are 2 units apart, so it plays
t = 0–218 at 2x and its frame says so; `10`'s frames are 0.5 units apart, so it
plays at 0.5x and its frame says so. Every video stops at its run's trust
window (02 at t = 60, the user's call on 2026-10-05).

| file | length | shows | run |
|---|---|---|---|
| `01_wormhole_throat_inflates.mp4` | 11.1 s | one throat, kicked inward: it keeps opening (to its trust window, t = 218) | `01_single_throat/single_eps_m1e2_L512_ml5_oct_t400` |
| `02_wormhole_throat_collapses.mp4` | 6.1 s | the same throat, seeded the other way: it closes | `01_single_throat/single_pureq_q1e2_ml4_t100` |
| `03_headon_collision_makes_black_hole.mp4` | 10.2 s | two wormholes collide head-on and make a black hole (horizon born common at t = 18) | `04_binary_headon/headon_csm_L128_stitched_t0_t100` |
| `04_spiral_merger_makes_black_hole.mp4` | 10.2 s | the orbital merger — and a horizon DOES form (MOTS from t = 13) | `05_binary_spiral/spiral_d6_p010_L128_csm_stitched_t0_t100` |
| `05_wormhole_flyby_no_merger_mouths_inflate.mp4` | 6.5 s | a fly-by: no merger, no horizon, both mouths inflate | `06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` |
| `06_plunge_merger_no_horizon_yet.mp4` | 8.2 s | a deeper plunge: the pair merges as wormholes and the horizon stalls | `06_binary_flyby/merge_orbit_flip_d12_p060_L128_csm_stitched_t0_t80` |
| `07_hardest_plunge_mouths_inflate.mp4` | 4.7 s | the hardest plunge: the mouths inflate on the approach and the merging core starts to inflate | `06_binary_flyby/merge_orbit_flip_d12_p090_L128_csm_stitched_t0_t45` |
| `08_control_two_black_holes_merge.mp4` | 30.2 s | vacuum control: black holes merge and ring down | `07_bbh_control/bbh_control_d12_p012_t150` |
| `09_control_two_black_holes_fly_apart.mp4` | 20.2 s | vacuum control: the fly-by's momentum, no scalar | `07_bbh_control/bbh_control_d12_p045_t100` |
| `10_control_two_black_holes_collide_headon.mp4` | 20.2 s | vacuum control: the head-on's twin — bare black holes fall together and ring down | `07_bbh_control/bbh_headon_d8_L128_lvl5_t100` |

**Publish 01 and 02 together, and publish the controls with the channels they
control.** Alone, the inflating throat invites "so it is just unstable"; beside
its collapsing twin it shows the branch being chosen. Publish 05–07 as the
momentum ladder they are: the same pair at p = 0.25, 0.60 and 0.90 — scatter,
stalled merger, inflating plunge — is one story told three times louder. The
head-on pair is 03 with 10 (the same collision with and without the exotic
matter); 08 is the textbook vacuum merger (the d = 12 spiral's parameters) and
09 the vacuum fly-by at p = 0.45, the references for the wormhole channels.

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

TOP LEFT: the curvature K - the expanding shell is the throat opening up.
TOP RIGHT: the lapse, the rate at which time runs at each point.
BOTTOM LEFT: the conformal factor (log scale) - the throat, then the bright
inflating shell. BOTTOM RIGHT: the phantom scalar, the exotic matter that holds
the throat open; its dark core widens as the throat inflates.

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

TOP LEFT: the curvature K. TOP RIGHT: the lapse, the rate at which time runs
at each point - it dips at the centre as the throat closes. BOTTOM LEFT: the
conformal factor, the throat as a dark pit that deepens. BOTTOM RIGHT: the
scalar field's momentum, the exotic matter falling in. The lapse falls in the
inflating video too; what tells the two apart is the search for trapped
surfaces, which finds a horizon here and none there. The video stops at t = 60,
after which grid noise dominates the curvature panel.

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

Zoomed 2x on the collision. TOP LEFT: the curvature K. TOP RIGHT: the lapse,
collapsing at the centre as the horizon forms. BOTTOM LEFT: the conformal
factor - two dark pits approach, meet, and become one. BOTTOM RIGHT: the
gravitational wave, Re(Psi4), on a log-type scale so the ringdown stays visible.

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

Zoomed 2x on the merger. TOP LEFT: the curvature K. TOP RIGHT: the lapse, the
rate at which time runs, collapsing over the remnant. BOTTOM LEFT: the conformal
factor, the two throats as dark pits that merge into one. BOTTOM RIGHT: the
gravitational wave, Re(Psi4), its two-armed pattern turning with the remnant.

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

Zoomed 2x on the encounter. TOP LEFT: the curvature K, the field that shows
expansion - the growing structure is the mouths opening. TOP RIGHT: the lapse.
BOTTOM LEFT: the conformal factor, the two mouths. BOTTOM RIGHT: the
gravitational wave, Re(Psi4).

The pull is the surprise. Without the exotic field, black holes with even
more momentum than this simply coast apart (video 09, the vacuum control at
momentum 0.45): the phantom field makes the mutual attraction several times
stronger, which is what drags this pair in so close. And the pass radiates
through a second channel a vacuum binary cannot have at all: the exotic scalar
field itself radiates, in a dipole pattern, carrying its energy with the
opposite sign.

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

TOP LEFT: the curvature K. TOP RIGHT: the lapse. BOTTOM LEFT: the conformal
factor, the two pits plunging and merging. BOTTOM RIGHT: the gravitational wave
itself, Re(Psi4), spiralling out - this plunge is the loudest gravitational-wave
source in the whole campaign.

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

## 7. `07_hardest_plunge_mouths_inflate.mp4`

**Title:** The Hardest Wormhole Plunge: The Mouths Inflate As They Merge | Numerical Relativity

```
Momentum 0.90 per mouth - the hardest plunge in the campaign. The pair falls
from separation 11.8 to 2.6 in forty time units. Watch the curvature panel on
the approach: both mouths visibly INFLATE as they close in - the same opening-up
the fly-by shows - and as they merge, the merging core starts to inflate too.

Zoomed 2x on the plunge. TOP LEFT: the curvature K - the expanding structure is
the mouths opening. TOP RIGHT: the lapse. BOTTOM LEFT: the conformal factor.
BOTTOM RIGHT: the gravitational wave, Re(Psi4).

No horizon is found at any time. The video ends at t = 45.3, where this
simulation stops: the inflating core outruns the grid's resolution.
```

## 8. `08_control_two_black_holes_merge.mp4`

**Title:** Control: Two Black Holes Merge, Same Setup Without the Exotic Matter

```
A control run. The d = 12 wormhole spiral's separation and momentum, with the
exotic scalar field removed. What is left is an ordinary binary black hole.

TOP LEFT: the magnitude of the Weyl scalar, the gravitational wave's strength.
TOP RIGHT: the lapse. BOTTOM LEFT: the conformal factor, two punctures orbiting
and merging. BOTTOM RIGHT: the wave itself, Re(Psi4).

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

Two black holes at the fly-bys' separation, 12, each with momentum 0.45, and
no scalar field. In vacuum that momentum is unbound: the holes begin at their
closest approach and coast apart, the separation opening from 12 to 21.

TOP LEFT: the magnitude of the Weyl scalar. TOP RIGHT: the lapse. BOTTOM LEFT:
the conformal factor. BOTTOM RIGHT: the wave itself, Re(Psi4).

Now compare it with the wormhole fly-by (video 05). There the exotic matter
makes the attraction several times stronger: even at the lower momentum 0.25
the pair falls in to a separation of 2.33 before it swings apart, and the
mouths inflate as they pass. The difference between the two videos is the
exotic matter's pull, made visible.

A caveat stated plainly: the momentum here is high enough that the standard
boosted-black-hole initial data is outside its strict validity range, which
inflates this run's emission.
```

## 10. `10_control_two_black_holes_collide_headon.mp4`

**Title:** Control: Two Black Holes Collide Head-On, No Exotic Matter

```
A control run: the wormhole head-on collision (video 03) with the exotic
scalar field removed. Two ordinary black holes of the same mass are released
from rest at the same separation, on the same grid. They fall together, merge,
and ring down.

TOP LEFT: the curvature K. TOP RIGHT: the lapse. BOTTOM LEFT: the conformal
factor, the two punctures falling together. BOTTOM RIGHT: the gravitational
wave, Re(Psi4), on a log-type scale so the ringdown stays visible.

Watch it beside video 03. There, the horizon closes over two still-open
wormholes, and the remnant then LOSES mass to the negative-energy field it
swallows. A vacuum remnant can only grow. Played at half speed: this run
saved a frame every half unit of time.
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
  02 at t = 60, 05 at t = 63, 06 at t = 80, 07 at t = 45 (where that simulation
  stops), the others at their full records. Nothing on screen after a
  trust window exists in any video.
- **Nothing on screen is quantitative.** Every number in the paper and in these
  descriptions is measured from the data files, never from an image.

To rebuild, restyle, or change the field pairing, edit `PANELS` in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger/make_youtube.py`
and re-run it. `--only <substring>` builds one, `--force` overwrites.
