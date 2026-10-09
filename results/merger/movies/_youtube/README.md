# Upload-ready videos

Twelve files, 1920x1080 H.264, 10 fps (20 for the half-unit records), ready to upload without further editing.
Built by

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube
```

**Layout (2026-10-05, the user's design): four panels, 2x2, in sync, on the
left** -- curvature K (top left), lapse (top right), conformal factor chi (bottom
left), the wave Re(Psi4) (bottom right) -- as tall as the frame allows, each
labelled on a band right above it with its role and its field ("CURVATURE
trace K"). Every other word except the title sits in a column on the right:
the two captions, justified, then the sponsor and the credit. **Every word is set in Computer Modern** (matplotlib's bundled
cmr10/cmb10 and its `cm` maths, no TeX engine needed), in one ink and no
colour coding: PRD style, the user's word. Exceptions, each because
that run has no usable alternative: 01 shows phi in place of the wave (the run
rendered no Weyl scalar); 02 shows Pi in place of the wave (its Psi4 frames were
drawn on a scale set by late junk and have no slice cache to redraw); 08 and 09
show |Psi4| in place of K (their K was drawn live on a flooding symlog scale,
again with no cache to redraw); 12 shows phi in place of the wave, as 01 does (its inflating
mouths are the point, and phi carries them). **03, 04, 05 and 07 are zoomed x2** about the
centre (`zoom_frames.py`: the cached slices cropped to the central half and
redrawn on fixed scales measured over the zoomed series); 01 and 10 are redrawn
unzoomed with better scales (01's chi on a log scale, 10's wave on 2.5 decades
of symlog). Each colour bar states its own scale: K is linear except 02's
(symmetric-log), and every wave panel is symmetric-log except 09's |Psi4|
(linear). Sources: 01 and 10 from the `youtube/` subsets, 03, 04, 05 and 07
from `youtube_zoom2/`, and 02, 06, 08, 09, 11 and 12 straight from the curated sets.

**Branding.** The channel is First Interstellar Institute: its mark `FII` is
printed inside every panel's plot area, so it cannot be cropped off without
cropping the data. **Gravity Frontiers, the research sponsor,** is named in full
at the foot of the right-hand column ("Research sponsored by GRAVITY
FRONTIERS"); the credit line under it carries both names.

**Playback is real time, 1x**: ten code units per second, and the `t =`
label drawn on each panel is the true simulation time. Pass `--speed 2` if a
particular upload wants it; the on-frame note follows automatically. The
vacuum controls 08, 09 and 10 and the receding pair 12 saved a frame every half unit, so they play at
20 fps and stay real time (the user's call, 2026-10-05). The one exception is
`01`: its run's frames are 2 units apart, so it plays t = 0–218 at 2x and its
frame says so. Every video stops at its run's trust window (02 at t = 60, the
user's call on 2026-10-05).

| file | length | shows | run |
|---|---|---|---|
| `01_wormhole_throat_inflates.mp4` | 11.1 s | one throat, kicked inward: it keeps opening (to its trust window, t = 218) | `01_single_throat/single_eps_m1e2_L512_ml5_oct_t400` |
| `02_wormhole_throat_collapses.mp4` | 6.1 s | the same throat, seeded the other way: it closes | `01_single_throat/single_pureq_q1e2_ml4_t100` |
| `03_headon_collision_makes_black_hole.mp4` | 10.2 s | two wormholes collide head-on and make a black hole (horizon born common at t = 18) | `04_binary_headon/headon_csm_L128_stitched_t0_t100` |
| `04_spiral_merger_makes_black_hole.mp4` | 10.2 s | the orbital merger — and a horizon DOES form (MOTS from t = 13) | `05_binary_spiral/spiral_d6_p010_L128_csm_stitched_t0_t100` |
| `05_wormhole_flyby_no_merger_mouths_inflate.mp4` | 6.5 s | a fly-by: no merger, no horizon, both mouths inflate | `06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm` |
| `06_plunge_merger_no_horizon_yet.mp4` | 8.2 s | a deeper plunge: contact at t ≈ 40, the mouths merge, and no horizon closes (to its trust window, t = 80) | `06_binary_flyby/merge_orbit_flip_d12_p060_L128_csm_stitched_t0_t80` |
| `07_hardest_plunge_mouths_inflate.mp4` | 4.7 s | the hardest plunge: the mouths inflate on the approach and the merging core starts to inflate | `06_binary_flyby/merge_orbit_flip_d12_p090_L128_csm_stitched_t0_t45` |
| `08_control_two_black_holes_merge.mp4` | 15.2 s | vacuum control: two black holes plunge, merge and ring down | `07_bbh_control/bbh_control_d12_p012_t150` |
| `09_control_two_black_holes_fly_apart.mp4` | 10.2 s | vacuum control at p = 0.45: two black holes coast apart | `07_bbh_control/bbh_control_d12_p045_t100` |
| `10_control_two_black_holes_collide_headon.mp4` | 10.2 s | vacuum control: the head-on's twin — bare black holes fall together and ring down | `07_bbh_control/bbh_headon_d8_L128_lvl5_t100` |
| `11_headon_collision_far_zone_waves.mp4` | 25.3 s | the head-on of 03 in a box four times wider, to t = 250, with wave detectors out to R = 180: the same horizon at t = 18 | `08_convergence/farzone_headon_flip_d8_L512_lvl6_t250_csm` |
| `12_wormholes_push_apart_mouths_inflate.mp4` | 8.2 s | two like-signed wormholes released from rest repel, fly apart, and both mouths inflate (to its trust window, t = 80) | `03_two_throats/csm/ctrl_rest_d12_csm_t100` |

**Publish 01 and 02 together, and publish the controls with the channels they
control.** Alone, the inflating throat invites "so it is just unstable"; beside
its collapsing twin it shows the branch being chosen. Publish 05, 06
and 07 together: the same pair at p = 0.25, 0.60 and 0.90, a scatter, a plunge
with no horizon and an inflating plunge. The
head-on pair is 03 with 10 (the same collision with and without the exotic
matter), and 11 goes with 03 (the same collision in a box four times wider, run
to t = 250 for the far-zone waves). Publish 12 with 01 and 05: a lone throat, a fly-by
and a receding pair, all three inflating; 08 (a vacuum plunge at d = 12, p = 0.12) and 09 (a vacuum fly-by at
p = 0.45) are references for the wormhole channels, not twins of any video
here.

---

# YouTube descriptions

Paste-ready: each block is one video's whole description, footer included. The footer is the same in all twelve; change them together.

## 1. `01_wormhole_throat_inflates.mp4`

**Title:** A Wormhole Throat Blows Open | Full Numerical Relativity

**YouTube:** https://youtu.be/RIQCitu4tSc

```
A wormhole throat, held open by exotic matter, gets a tiny inward nudge. It does not collapse: it keeps opening, 3.8 times wider by t = 218, and no black-hole horizon forms.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 2. `02_wormhole_throat_collapses.mp4`

**Title:** A Wormhole Throat Collapses Into a Black Hole | Full Numerical Relativity

**YouTube:** https://youtu.be/Cc87mHcBPOA

```
The same wormhole throat as in the companion video, perturbed differently: this time it closes, and a black-hole horizon forms at t = 33.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 3. `03_headon_collision_makes_black_hole.mp4`

**Title:** Two Wormholes Collide Head-On and Form a Black Hole | Numerical Relativity

**YouTube:** https://youtu.be/3sx9GHRTYVs

```
Two wormhole throats are released from rest and fall together. They touch while both are still open, and a single horizon closes over the pair at t = 18.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 4. `04_spiral_merger_makes_black_hole.mp4`

**Title:** Two Wormholes With Orbital Momentum Merge and Form a Black Hole | Numerical Relativity

**YouTube:** https://youtu.be/jNnMAXPjyRA

```
Two wormhole throats at separation 6, with tangential momentum 0.10, fall together, turning only 15 degrees, and a single horizon closes over both at t = 13 while they are still wormholes.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 5. `05_wormhole_flyby_no_merger_mouths_inflate.mp4`

**Title:** A Wormhole Fly-By: No Merger, No Horizon, and the Mouths Inflate | Numerical Relativity

**YouTube:** https://youtu.be/fh3pU7xCU_I

```
Two wormholes start at separation 12, each with momentum 0.25. They swing past each other, closest approach 2.32 at t = 48, and separate: no merger, no horizon, and both mouths INFLATE as they pass.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 6. `06_plunge_merger_no_horizon_yet.mp4`

**YouTube:** https://youtu.be/-ejFKpetL1Y (uploaded 2026-10-06)

**Title:** A Deeper Wormhole Plunge: The Mouths Merge, and No Horizon Closes | Numerical Relativity

```
Two wormholes start at separation 12, each with momentum 0.60, past the circular value. The pair plunges, reaches contact at t = 40 and merges as wormholes. No trapped surface converges on the merged core through t = 80, the end of the trustworthy record, on either of two grids: unlike the head-on and the close orbit, this merger is not hidden behind a horizon as far as the simulation can see. It is not the loudest encounter either: the p = 0.45 fly-by, which just escapes, radiates more.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

Released 2026-10-06 (the user), after P060-EXT: held back since 10-05, its on-frame
captions rewritten (the old "loudest source", "separation 3.5 to 0" and "closure
at t = 110-115" lines did not hold).

## 7. `07_hardest_plunge_mouths_inflate.mp4`

**Title:** The Hardest Wormhole Plunge: The Mouths Inflate As They Merge | Numerical Relativity

**YouTube:** https://youtu.be/yzvwjC46lJY

```
Momentum 0.90 per mouth, the hardest plunge in the campaign: the pair falls from separation 12 to 2.4 by t = 40. On the approach both mouths visibly INFLATE, as in the fly-by, and as they merge the core starts to inflate too.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 8. `08_control_two_black_holes_merge.mp4`

**Title:** Control: Two Black Holes Plunge and Merge, No Exotic Matter

**YouTube:** https://youtu.be/NkcpGiJIxXI

```
A control run: two ordinary black holes at separation 12, each with momentum 0.12, and no exotic matter. They plunge, merge and ring down.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 9. `09_control_two_black_holes_fly_apart.mp4`

**Title:** Control: Two Black Holes Fly Apart, No Exotic Matter

**YouTube:** https://youtu.be/65_3kw4obvE

```
A control run, and the point is what does NOT happen. Two ordinary black holes at separation 12, each with momentum 0.45, no exotic matter: in vacuum that momentum is unbound, and the holes coast apart, 12 to 27 by t = 100.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 10. `10_control_two_black_holes_collide_headon.mp4`

**Title:** Control: Two Black Holes Collide Head-On, No Exotic Matter

**YouTube:** https://youtu.be/aRWvD4W8OOg

```
A control run: the wormhole head-on collision with the exotic matter removed. Two ordinary black holes of the same mass start from rest at the same separation and base resolution, in a box half the size, and fall together, merge and ring down.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 11. `11_headon_collision_far_zone_waves.mp4`

**Title:** The Wormhole Head-On Collision in a Four Times Wider Box | Numerical Relativity

**YouTube:** (link once uploaded)

```
The head-on collision of video 3, run again in a box four times wider, to t = 250, with gravitational-wave detectors out to 180 units, 76 times the pair's mass. A single horizon closes over both throats at t = 18, as in the smaller box. On the far detectors the radiated energy settles as the detector moves out, and the near ones agree with the production run to 1%.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

## 12. `12_wormholes_push_apart_mouths_inflate.mp4`

**Title:** Two Wormholes Push Each Other Apart, and Both Mouths Inflate | Numerical Relativity

**YouTube:** (link once uploaded)

```
Two identical wormholes, released from rest at separation 12 with like-signed phantom fields, repel each other and fly apart, to separation 26 by t = 60. As they go, both mouths inflate: each throat widens from 3.88 to 4.78 by t = 30 and keeps growing, and no horizon forms. The video stops at t = 80; after that the edge of the simulation box spoils the picture.

Paper: "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers, fly-bys and gravitational waves", Nikita M. Shirokov and Ilya Nachevsky
Code and data: https://github.com/Nikchik-coder/GRTeclyn
First Interstellar Institute: https://www.firstinterstellarinstitute.com/
Research sponsored by Gravity Frontiers: https://www.gravityfrontiers.org/en
```

---

## Tags

```
numerical relativity, general relativity, wormhole, Einstein-Rosen bridge, exotic matter, negative energy, black hole, event horizon, gravitational waves, spacetime, Einstein equations, astrophysics, computational physics, GPU simulation, CCZ4, gravitation, theoretical physics
```

---

## Honest limits, worth knowing before captioning anything

- **The panels are not upscaled.** Each source frame (about 640x538) is drawn
  at about 560x460, a 0.85x reduction. The x2 zooms (03, 04, 05, 07) crop the
  cached slices to their central half, so each cached pixel spans twice the
  screen it would unzoomed; that is the only magnification. Native
  high-resolution rendering is no longer possible for most of these: the
  plotfiles were pruned after each run.
- **Colour bars are fixed** over each whole series, so a colour means the same
  value in the first frame and the last. K is drawn on one fixed scale (the
  series' own envelope) since 2026-10-05. K is identically zero in the initial
  data of 01, 02, 03, 10, 11 and 12, so their first K frame is uniformly the zero
  colour: correct, not a blank frame. The boosted pairs start with K structure
  from the boost, faint in 04 and 05 and clear in 06 and 07.
- **Late speckle in any wave or curvature panel is noise, not structure.** It is
  real grid-scale noise, confined to the refined mesh levels, and it becomes
  visible only because the physical signal has decayed far below the fixed
  colour scale by then. The paper gates every measurement window ahead of its
  onset. The measurement is explained in `../README.md`.
- **Every video stops at its run's trust window** (`../../trust_windows.tsv`):
  01 at t = 218 (its record runs to t = 392), 02 at t = 60, 05 at t = 63, 06 at
  t = 80, 07 at t = 45 (its last frame; the simulation stops at t = 45.3) and 12
  at t = 80 (the box's edge spoils its frames by t = 95; the run died at 95.08);
  03, 04, 08, 09, 10 and 11 run to the end of their records. Nothing on screen after a
  trust window exists in any video.
- **Nothing on screen is quantitative.** Every number in the paper and in these
  descriptions is measured from the data files, never from an image.

To rebuild, restyle, or change the field pairing, edit `PANELS` in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger/make_youtube.py`
and re-run it. `--only <substring>` builds one, `--force` overwrites.
