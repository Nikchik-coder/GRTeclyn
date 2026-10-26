# Upload-ready videos

Five files, 1920×1080 H.264, 20 fps, ready to upload without further editing. Built by
`grteclyn-wrapper/scripts/plot/youtube_sidebyside.sh` from the revision's runs (fourth-order time integration,
the fixed initial data; 2026-10-26). Each puts the matter view and the geometry view side by side, in sync, for one
run. The v1 set, made from the runs on first-order time integration, is superseded and kept in the run tree's
`runs/bondi/00_archive/superseded_2026-10-23/movies/`.

| file | length | shows | on YouTube |
|---|---|---|---|
| `PM10_L64_N256.mp4` | 12.7 s | the result — the self-accelerating mixed pair, finest grid, to `t = 200` | https://youtu.be/zz8_5i7A6zo |
| `PM10_L64_N128_t400.mp4` | 25.2 s | the same pair carried to `t = 400` on the coarse grid | https://youtu.be/n5y8fBBCDUs |
| `PM10-rec_L64_N192_t1000.mp4` | 31.5 s | the same pair followed to `t = 1000` in a box that moves with it | https://youtu.be/VeqhSRbtVas |
| `PP10_L64_N128.mp4` | 12.7 s | control — two positive masses, they merge | https://youtu.be/ANS986k4RsA |
| `MM10_L64_N128.mp4` | 12.7 s | control — two negative masses, they merge too | https://youtu.be/YKgzOYMcjk4 |

**Publish the controls alongside the result, not separately.** Alone, the runaway invites "that is just gravity".
The controls close that off.

---

# YouTube descriptions

Paste-ready. Every one states the 2× playback, because the frames are one per plotfile and only the rate was
changed — a viewer who misses that misreads every timescale. The `t =` label drawn on each panel is the real
simulation time.

Shared boilerplate, reused at the foot of each description:

```
📄 Paper: "The Bondi dipole in full numerical relativity: a self-accelerating
positive–negative mass binary", Nikita M. Shirokov and Ilya Nachevsky,
arXiv:2608.24577
💻 Code and data: https://github.com/Nikchik-coder/GRTeclyn
🌐 Gravity Frontiers: https://www.gravityfrontiers.org/en
🔬 First Interstellar Institute: https://www.youtube.com/@First_Interstellar_Institute

Method: initial data from a constraint-solved elliptic system (GRTresna),
evolved in full 3+1 numerical relativity with the CCZ4 formulation and
fourth-order Runge–Kutta time stepping on GPUs (GRTeclyn / AMReX). Two
independent complex scalar fields sharing a sextic potential; no cross term
between them. Uniform grid, no mesh refinement, with solve and evolution cell
sizes matched exactly. Playback is 2× — the on-screen t = value is the true
simulation time.
```

---

## 1. `PM10_L64_N256.mp4` — the headline

**Title:** A Positive Mass and a Negative Mass Star Accelerate Themselves | Full Numerical Relativity

**Published:** https://youtu.be/zz8_5i7A6zo

```
Two boson stars are released at rest, side by side. One has positive mass, the
other negative. Nothing pushes them — and the pair accelerates away together,
keeping its separation.

This is the Bondi dipole: a 1957 prediction that a positive and a negative mass
chase each other forever, gaining speed without any external force and without
violating conservation of momentum. It has been argued about for decades on
paper. This is it solved in full 3+1 numerical relativity, with matter that
satisfies the Einstein constraints at t = 0 and no horizon forming.

LEFT: the matter — where the two stars are.
RIGHT: the geometry — how each star curves spacetime. The positive mass digs a
well; the negative mass raises a hill. That asymmetry is the entire mechanism.

Why this configuration and not another: the two stars are DIFFERENT scalar
fields with no cross term in the potential, so they cannot touch each other
except through the metric. Gravity is their only interaction, by construction.
Two stars of the SAME field also pull on each other directly where they
overlap — a force much stronger than gravity and blind to the sign of the
mass — which is why the same-sign controls on this channel merge instead.

The measured acceleration falls with the separation as d^-1.95 across
separations 8 to 20, close to Newton's inverse square, and grows with the mass
as M^0.97 across a 2.5× range of mass.
```

## 2. `PM10_L64_N128_t400.mp4` — sustained

**Title:** The Runaway Does Not Stop: 400 Time Units of a Positive–Negative Mass Binary

**Published:** https://youtu.be/n5y8fBBCDUs

```
The same self-accelerating pair as before, carried twice as long — to t = 400
in code units — on a coarser grid.

The question this run answers is whether the effect is a transient of the
initial data. It is not: both stars keep accelerating in the same direction to
the end of the run.

LEFT: the matter. RIGHT: the geometry — the well and the hill travelling
together.

What you also see is the coarse grid's error. The gap widens slowly, from 10 to
10.9, and the acceleration fades, because on this grid the stars slowly lose
matter (6 % by t = 400). On a grid 1.5× finer the widening is four times
smaller; the t = 1000 video on this channel uses that finer grid.
```

## 3. `PM10-rec_L64_N192_t1000.mp4` — followed to t = 1000

**Title:** Chasing the Bondi Dipole to t = 1000: 0.11 c Without a Push

**Published:** https://youtu.be/VeqhSRbtVas

```
The positive–negative pair, carried to t = 1000 in code units — five times the
headline run — on a grid 1.5× finer than the t = 400 video.

The box moves with the pair: whenever the stars drift two units forward, the
grid shifts under them, so they stay in view while the pair travels 63 units,
six times its own separation. By the end the stars move at 0.11 c (the leading
positive star 0.115 c, the trailing negative star 0.108 c).

The momentum stays balanced: the positive star carries +1.6 × 10^-3, the
negative star -1.5 × 10^-3, so the pair gains speed without gaining momentum
(up to the same 6 % by which the trailing star lags).

At 0.11 c the Lorentz factor is only 1.006: the stars are 0.6 % shorter along
the motion, far below what the picture can show.

The gap widens from 10 to 13.5 over the run. That is the grid's error, not
gravity: the same widening at t = 200 is 0.071, 0.016 and 0.005 on grids of
128, 192 and 256 cells across the box.

LEFT: the matter. RIGHT: the geometry. One frame per 1.6 time units, so this
video runs through simulation time twice as fast as the others.
```

## 4. `PP10_L64_N128.mp4` — control, both positive

**Title:** Control: Two Positive-Mass Stars — They Fall Together and Merge

**Published:** https://youtu.be/ANS986k4RsA

```
A control run. Both stars have positive mass, at the same separation as the
runaway.

They attract, fall together, and merge at t ≈ 34.

Watch this one next to the two-negative-mass control. Newtonian gravity's sign
is opposite between them — two positive masses should attract, two negative
masses should repel — yet both pairs collapse in almost exactly the same time,
within 2.3 % of each other. That is the tell: the force closing them is not
gravity.

Both stars here are the SAME scalar field, started in phase, so where their
profiles overlap the field itself pulls them together — a direct short-range
force much stronger than gravity, and one that does not care about the sign of
the mass.

This is exactly the channel the positive–negative pair does not have, which is
what makes that configuration the clean gravitational case.
```

## 5. `MM10_L64_N128.mp4` — control, both negative

**Title:** Control: Two Negative-Mass Stars Should Repel — They Merge Anyway

**Published:** https://youtu.be/YKgzOYMcjk4

```
A control run. Both stars have NEGATIVE mass.

Newtonian gravity is unambiguous here: two negative masses repel. They should
fly apart. Instead they fall together and merge at t ≈ 34 — within 2.3 % of
the time taken by the two-positive-mass control.

That near-coincidence is the point of the run. A force that produces the same
collapse whether both masses are positive or both are negative cannot be
gravity. Both stars are the SAME scalar field, so where their profiles overlap
the field pulls them together, and that pull is blind to the sign of the mass.
It is much stronger than gravity, which is why it dominates completely.

Bondi's predicted repulsion between two negative masses is real, but far too
weak to see against it here.

The positive–negative pair has no such channel — its two stars are different
fields with no cross term — which is why that configuration isolates gravity
and shows the runaway.
```

---

## Tags

```
numerical relativity, general relativity, negative mass, Bondi dipole,
boson star, exotic matter, spacetime, Einstein equations, astrophysics,
computational physics, GPU simulation, CCZ4, gravitation, theoretical physics
```

---

## Honest limits — worth knowing before you caption anything

- **The panels are redrawn, not live frames.** Each view is redrawn from the run's cached 2-D slices against one
  fixed colour scale over the whole run, so a colour means the same value from first frame to last. The source
  panels are ~890 px wide, so the 1080p frame is a near-native ~1.05× enlargement.
- **Nothing on screen is quantitative.** Every number in the paper is measured from the data files, never from an
  image. The numbers above come from `../../runs_registry.tsv` and `research/bondi_dipole/STATUS.md`.
- **The two long runs show the grid's error as well as the physics.** The widening gap in the `t = 400` and
  `t = 1000` videos is numerical (it shrinks fast with resolution); the paper quotes pair quantities for `t ≤ 200`.
- The merge times are the first frame in which the two lumps of `|χ − 1|` have become one: `34.4` for the positive
  pair and `33.6` for the negative pair (`../../campaign/03_same_sign/*/well_tracking.dat`).

To rebuild, restyle, or run at real speed: the sources are each run's fixed-scale matter and geometry movies,
`<run>/<episode>/fixed_scale/movies/` (the chase: `<run>/<episode>/movies/`) in the run tree, gathered as one folder
per run holding `movie_scalar_activity_z.mp4` and `movie_chi_minus_1_z.mp4`; then

```bash
SPEED=1 bash grteclyn-wrapper/scripts/plot/youtube_sidebyside.sh <src_dir> <dest_dir>
```
