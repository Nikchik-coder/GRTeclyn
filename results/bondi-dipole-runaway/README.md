# Bondi dipole runaway — publishable results pack

**Cite this pack as** the `results/bondi-dipole-runaway/` tree of
<https://github.com/Nikchik-coder/GRTeclyn>, browsable at
<https://github.com/Nikchik-coder/GRTeclyn/tree/develop/results/bondi-dipole-runaway>.
The same repository holds the evolution and initial-data code that produced it;
the version behind the article is identified by its git tag. The article is
`research/bondi_dipole/bondi_dipole.tex`, and every number and figure in it is
reprinted by `grteclyn-wrapper/src/grteclyn_wrapper/visualisation/bondi_dipole/article_figures.py` from this pack
alone — if a number here and a number there disagree, the script is the arbiter.

A positive-active-mass and a negative-active-mass soliton, released at rest in
full 3+1 numerical relativity with dynamical, constraint-solved matter,
**self-accelerate in the same direction** while both same-sector controls stay
put. This pack holds every light artefact behind that claim: per-cell time
series, the dressed-star tables, the solve/evolution parameters, the code
patches, curated frames and movies, and the derived article tables.

Heavy artefacts (plotfiles, gridinit, HDF5 metric stacks, the movies, and the
full ~250-frame-per-field series) stay in the gitignored `runs/` tree on the
machine that produced them. Cells run with frames keep one still per field every
`dt = 10` here. Everything in this pack is small enough to live in git.

## Headline result

A mixed pair — one positive-mass canonical star, one negative-mass phantom star
of matched |ADM| — accelerates as a unit, and **the effect survives grid
refinement**:

| grid | cells | drift at `t = 200` | separation | acceleration |
|---|---|---|---|---|
| coarse | 128³ | `+2.8815` | `10.000 → 10.003` | `1.448e-04` |
| middle | 192³ | `+3.0139` | `10.000 → 9.930` | `1.557e-04` |
| **fine** | **256³** | **`+3.0016`** | `10.000 → 9.915` | **`1.549e-04`** |

Accelerations are twice the quadratic coefficient of the pair midpoint over
`5 ≤ t ≤ 200` — the article's convention, and the one
`article_figures.py` prints. Separations are barycentre gaps.

The two finest grids agree to `0.4%` on drift and `0.5%` on acceleration. That
is the shape of a converging quantity: refining does not push the effect toward
zero, it settles it onto a value. Quote the `256³` number.

Independent checks bracket it:

| check | cell | result |
|---|---|---|
| does the box matter? | `L = 128`, doubled | drift within `4%` of `L = 64` |
| does it keep accelerating? | `t = 400` | `a` = `1.451 / 1.422 / 1.417e-04` over `[133,266]` / `[300,400]` / `[350,400]` — steady to `2%` |
| does the pull follow the source? | phantom `0.7995 ×` mass | canonical pull ratio `0.810` vs `0.803` predicted (`+0.9%`); the untouched phantom's own pull `1.011` |
| does mesh refinement change it? | `max_level = 1` | level 1 never tagged; drift matches to `0.001%` |
| is the base grid just under-solved? | initial data solved `4.4×` deeper | drift moves `0.0015%`; refining the grid moves it `4.6%` |
| is the drift coordinate dragging? | shift read at both cores | the translational (mean) part of `β^x` is `1.07e-05` against a core velocity of `3.04e-02` — `2830×` apart |
| is the separation gauge? | proper gap, `∫√γ_xx dx` | `10.0001 → 10.0244` at `256³`, `+0.24%` — the coordinate gap moves `+0.13%` |

**And the sign flips with the mass ordering.** Four cells spanning mass ratios
`0.597` to `1.333`:

| `\|M−\|` ÷ `M+` | `1.333` | `1.000` | `0.799` | `0.597` |
|---|---|---|---|---|
| separation, 0 → 200 | 10.00 → **10.60** | 10.00 → 10.00 | 10.00 → 9.41 | 10.00 → 8.62 |
| | **opens** | flat | closes | closes more |

The gap opens, sits flat, or closes strictly according to which star is heavier,
crossing zero at the equal-mass point. That is the test that separates a real
gravitational effect from an artefact: no artefact story predicts a sign reversal
that tracks the mass ordering, still less one that crosses exactly where the
masses match.

And the separation law across five cells at `d = 8/10/12/16/20` gives
`a ∝ d^−2.028` against `−2` exact, with `a·d²` returning the partner star's mass
to within `0.1%` from `d = 12` outward. The widest cell was run to test whether
the `3.1%` excess at the closest separation was a finite-size correction or a
floor in the measurement: it decays monotonically to `GM` and does not level
off, so it is the former.

**Two things the campaign found rather than assumed, stated up front.**

*Both same-sign pairs merge — and that is the campaign's sharpest test of what
holds the stars together.* The PP frames show the two wells closing
`8.78 → merged` at `t = 33.6`; the MM frames, added 2026-08-24, show the two
phantom hills closing `8.57 → merged` at `t = 32.8`. Newtonian gravity's sign is
opposite between those two cells — two positive masses attract, two negative
masses repel, which is Bondi's own result — so if gravity set the timescale one
would coalesce and the other fly apart. They instead collapse within 2.4% of
the same time, which means the dominant force is **blind to the sign of the
mass**. It is the overlap of two copies of the *same* scalar field, some `35×`
stronger than gravity at this separation. Both lumps of every pair here are
seeded **in phase** (relative internal `U(1)` phase `δ = 0`): the
`trajectory_lump{k}_phase0` knob in the launch configs is an *azimuthal
placement* angle — `0` and `π` put the two lumps at `x = ±d/2` — and the matter
painter gives a non-winding star a real, positive field, so both get the same
internal phase. `δ = 0` is the *attracting* configuration for two Q-balls of one
field (Battye–Sutcliffe; Palenzuela–Lehner–Liebling for boson stars), which is
what these cells show, and it is the configuration that permits fusion into a
single centred lump rather than holding a node at the midplane. The mixed pair has no such channel at
all, because its two stars are different fields with no cross-term, leaving
gravity as their only interaction — which is why the runaway cell is the clean
one and these are controls.

The ×7 box-activity growth that follows each merger is ejecta draining out
through the sponge, not a boundary artefact (net inward boundary flux stays at
round-off all run; an earlier version of this pack claimed a boundary wave at
`t ≈ 32`, and the flux measurement retires that). The null verdict is
*strengthened* by the merger rather than weakened: the pair centroid moves
≤ `7.8e-04` over the full `t = 200`, through infall, coalescence and ringdown. The
*mirror* cell, zero net mass, remains the cleanest null.

*No wave zone is reached.* With shells at `R = 16/24/32/40`, `ψ₄(l=2)` falls as
`r^−4.8`; radiation would give `r^−1`. Every shell is in the near zone, so this
pack reports no gravitational radiation rather than a measurement of it — which
is consistent with a pair whose total momentum is zero and whose mass dipole is
therefore static.

**The headline numbers are not artefacts of the gauge, and the pack carries the
columns that show it.** `sector_dynamics.dat` records the shift at each core and
the proper separation between them, so both questions a referee asks about a
coordinate drift are answered by reading the pack rather than by running
anything:

| question | column | answer at `256³` |
|---|---|---|
| is the pair being dragged by the shift? | `shift_x_canon`, `shift_x_phantom` | `β^x` at the two cores is **antisymmetric** (`−7.68e-04` / `+7.46e-04` at `t = 200`), so the only part that can *translate* the pair is the mean: `≤ 1.07e-05`, against a measured core velocity of `3.04e-02`. Integrated over the run it accounts for `4.0e-04` of displacement — `0.013%` of the measured `+3.03` |
| is "constant separation" a coordinate statement? | `proper_sep` = `∫√γ_xx dx` | coordinate gap `10.0000 → 10.0127` (`+0.13%`), proper gap `10.0001 → 10.0244` (`+0.24%`). At `128³` the proper gap is the steadier of the two (`+0.06%` vs `+1.07%`) |
| is the late gap opening real? | same, on the `t = 400` cell | coordinate `11.844`, proper `11.877` — physical, not gauge |

Two more monitors worth quoting because they are easy to ask for and already
measured. **Energy conditions** (`energy_conditions.dat`): the minimum NEC is
`−2.20e-04` in every cell containing a phantom and **flat over the run**
(`−2.19e-04` at `t = 0`, `−2.19e-04` at the end), while the lone *canonical*
star returns `+7.5e-42` — no violation at all. The violation is localised to the
phantom sector and does not grow as the pair accelerates. **Radiation budget**:
the signed mass quadrupole of a zero-momentum pair is `Q ≃ 2M̄dX(t)`, so at
constant separation and constant acceleration `Q̈ = 2M̄ad` is *constant* —
measured `4.5e-05` against `4.4e-05` predicted, steady to `7%`. A constant `Q̈`
radiates nothing at leading order: `|Q⃛| ≤ 6.2e-08`, luminosity `~3.7e-17`,
`~7.4e-15` radiated over the whole run, **ten orders of magnitude below the
pair's total mass** of `5.5e-05`. The near-zone null above is therefore a
prediction confirmed, not merely a bound stated.

Per-cell numbers, the caveats in full, and how to read a cell name are in
[`campaign/README.md`](campaign/README.md). The pre-submission review of the
article, what it asked for, and the two runs it asked for — the gauge twin
(the drift moves `-0.007%`) and the lone phantom to `t = 1000` (the peak
decays `0.63%` per 100 time units), both since run and folded in — are
recorded with the campaign working notes, which are not part of this pack.

## What is where

| path | contents |
|---|---|
| [`MATTER_MODEL.md`](MATTER_MODEL.md) | the bicomplex model, where the sign flip lives, dressed-star initial data, code map |
| [`LAUNCH.md`](LAUNCH.md) | how a cell is launched, what every knob selects, and the configuration table for all of them — the authoritative per-cell record is each `campaign/<cell>/launch_config.sh` |
| `campaign/<cell>/` | every run — the resolution ladder, the separation series, the nulls, the wave-zone box and the long run (see the data dictionary below, and `campaign/README.md` for the guide) |
| `stars/` | dressed-star profile tables `r φ₀(r) α(r)` + the M(ω) family scan |
| `analysis/` | derived tables and the scripts that regenerate them |
| `campaign/<cell>/frames/` | one still per field every `dt = 10`, for the cells run with frames. The movies themselves stay in the gitignored run tree |
| `patches/` | the matter-model modifications this campaign required |

### Data dictionary — `campaign/<cell>/`

Every `.dat` stream carries its own `#` header line naming each column.

| file | what it is | key columns |
|---|---|---|
| `sector_barycenters.dat` | **the trajectory record** — per-sector integrals | 1 `t`, 2 `total_canon`, 3 `bary_x_canon`, 6 `rms_canon`, 7 `total_phantom`, 8 `bary_x_phantom`, 11 `rms_phantom` |
| `confinement.dat` | core health / grip | 3 `peak_activity`, 5 `confined_frac`, 18 `min_chi` |
| `psi4_mode_l2m0.dat`, `psi4_mode_l2_all.dat`, `psi4_directional.dat` | radiation extraction; shells are per-cell — `R = 8, 16` on the `L = 64` cells, `R = 16, 24, 32, 40` on the wave-zone cell | — |
| `shell_profiles.dat` | metric on extraction shells (χ, lapse, K) | — |
| `constraint_norms.dat` | **constraint violation during the evolution** (downsampled to Δt = 0.5; column names are supplied by the pack script, the raw stream has none) | 1 `t`, 2 `L2_Ham`, 3 `L2_Mom`, 16 `Linf_Ham_amr` (worst single point). Columns 7–8 are relative measures — see the caution in the constraint section |
| `energy_conditions.dat`, `curvature_invariants.dat` | NEC/WEC monitors and invariants (downsampled; column names supplied by the pack script) | — |
| `collapse_diagnostics.dat` | **horizon watch** — how deep the gravity well gets and whether a trapped surface appears (downsampled; column names are supplied by the pack script, the raw stream has none) | 1 `t`, 2 `min_lapse`, 3 `min_chi`, 4 `max_abs_K`, 8 `max_ah_r`, 9 `min_theta_plus` |
| `boundary_flux.dat`, `areal_radius.dat`, `ftl_timeseries.dat` | outflow, minimal areal radius, geodesic diagnostics | — |
| `grtresna_params.txt` | the constraint-solve input (couplings, per-lump seeds, tolerances) | — |
| `evolution_params.txt` | the GRTeclyn evolution input (grid, AMR, boundaries, dt) | — |
| `Ham_and_Mom_errors.txt` | per-iteration constraint residuals (last row = final) | — |
| `metadata.json` | provenance: git commit, overrides, solve convergence | — |
| `initial_data.matter.json` | the matter configuration actually seeded | — |

Grid geometry is **not** the same for every cell — it is what the cell name
records. Most cells are `L = 64`, `N = 128`, centre at `32 32 32`, so a star
seeded at `x = ±5` reads as `bary_x = 37 / 27`; the ladder rungs raise `N` to
192 and 256 at the same `L`, and the wave-zone cell doubles `L` to 128 with
`N = 256` (centre `64 64 64`). Barycentre coordinates in the streams are
absolute; drifts quoted anywhere in this pack are `x(t) − x(0)`.

### `analysis/`

| file | contents |
|---|---|
| `summary.csv`, `summary.md` | one row per cell: birth checks → final state |
| `trajectories.csv` | drift / separation / core series for every cell, sampled every Δt = 4 |
| `newtonian_reference.csv` | point-mass Bondi integration with the measured ADM masses, aligned to the NR output |
| `separation_scaling.csv`, `separation_scaling.py` | the separation series: measured drift against a point-mass integration of the *same* configuration, at separations 8 / 12 / 16 — the test that isolates the overlap |
| `convergence_check.csv`, `convergence_check.md` | drift / gap / control artefact across grid resolutions, with the spread between grids |
| `wave_check.csv`, `wave_check.md` | gravitational-wave amplitude on each extraction shell in retarded time, and whether the shells agree |
| `constraint_check.csv`, `constraint_check.md` | constraint violation at both stages — the initial-data solve and the evolution — plus whether refining the grid reduces it |
| `make_tables.py` | regenerates `summary.*` and `trajectories.csv` for the Δx = 0.5 production cells |
| `newtonian_reference.py` | regenerates the point-mass reference (pure stdlib RK4) |
| `convergence_check.py` | regenerates `convergence_check.*` from `campaign/` |
| `wave_check.py` | regenerates `wave_check.*` from `campaign/` |
| `constraint_check.py` | regenerates `constraint_check.*` from `campaign/` |
| `star_family_scan.py` | regenerates `stars/star_family.csv` — the M(ω) table the matched pairing was chosen from (needs the wrapper venv) |
| `star_family_massratio_scan.py` | regenerates `stars/star_family_massratio.csv` — both branches out to ω = 1.0, and the phantom branch's floor on how light its stars get (needs the wrapper venv) |

## campaign/ — the cells behind the result (complete)

Thirty-one cells, one folder each, all on **uniform** grids: the convergence
argument needs a single cell size everywhere, so nothing here uses mesh
refinement — with one deliberate exception, `amrcheck_*`, which switches it on
once to show the choice costs nothing. Each folder carries the same streams and provenance files — the
per-sector time series, the four evolution diagnostics downsampled to
`dt = 0.5`, the elliptic residual history, the solve and evolution parameter
files, and the exact launch environment.

`campaign/README.md` is the detailed guide: how to read a cell name, what every
file is, the per-cell numbers, and the caveats. The short version:

| group | cells | what it settles |
|---|---|---|
| `runaway_pair_d{08,10,12,16,20}_L64_N128` | 5 | the separation law, `a ∝ d^−2.028` |
| `runaway_pair_d10_L64_N{192,256}` | 2 | the resolution ladder's finer rungs — `d10_N128` above is its base. **The headline** |
| `control_lone_{canonical,phantom}` | 2 | a lone star does not drift over `t = 200` |
| `control_lone_phantom_t1000_L64_N128` | 1 | the same phantom to `t = 1000` — it decays `−0.632%` per 100 units and the pack's stability claim stops at `t = 400` |
| `control_pair_{pp,mm}_d10_L64_N128` | 2 | same-sign pairs merge yet their centroid never moves — no runaway |
| `control_pair_pp_d10_L64_N{192,256}` | 2 | the null's own resolution ladder |
| `control_pair_mm_d10_L64_N192` | 1 | the mm null's second rung |
| `control_pair_mm_d10_L64_N128_lev0_frames` | 1 | the phantom pair's per-star fate — it merges too, on the pp pair's clock |
| `control_mirror_mp_d10_L64_N128` | 1 | flipping the pair reverses the runaway exactly |
| `massscale_*` + `massratio_*` (2) | 3 | the pull follows the partner's mass — and reverses with it |
| `amrcheck_pair_d10_L64_N128_lev1` | 1 | mesh refinement changes nothing (six-digit match) |
| `deepsolve_pair_d10_L64_N128` | 1 | a `4.4×` deeper constraint solve changes nothing — the base rung is grid-limited |
| `gaugetwin_pair_d10_eta2_L64_N128` | 1 | doubling the Gamma-driver damping moves the shift `−4.95%` and the drift `−0.007%` — not gauge-limited |
| `wavezone_pair_d10_L128_N256` | 1 | doubled box, four extraction shells |
| `longrun_pair_d10_t400_L64_N128` | 1 | the acceleration is steady to `t = 400` |
| `stability_canonical_w{075,080,085,090}` | 4 | the star family is stable at all |

### What the campaign shows

1. **The runaway converges.** N=192 and N=256 agree to `0.4%` on drift. A
   discretisation artefact shrinks toward zero under refinement; this does not.
2. **It obeys an inverse-square law.** Across `d = 8/10/12/16/20`, `a·d²`
   returns the star's mass to better than `3.1%`, tightening monotonically
   (`1.031 → 1.011 → 1.003 → 1.001 → 1.002`) exactly where finite-size
   corrections predict, and the widest cell shows the excess decaying rather
   than levelling onto a measurement floor.
3. **It reverses when the pair is mirrored,** to within `0.002%` — a sign flip
   no artefact story reproduces.
4. **It scales with the partner's mass.** Lightening the phantom to `0.7995` of
   matched cuts the canonical's pull to `0.810` of its matched value (`0.803`
   predicted, `+0.9%`) and leaves the phantom's own pull at `1.011` — the
   internal control, predicted `1`.  Constants come from a separation-corrected
   per-star fit on the **core** tracker (`C` in `ẍ = ±C/d(t)²`, regressing each
   core on `{1, t, I₂(t)}` with `I₂` the double time integral of the measured
   `d(t)⁻²`, `t ≥ 5`); ratios only, never the constants.
5. **It is steady, not explosive.** At `t = 400` the acceleration is still
   `1.42e-04` in the final quarter against `1.45e-04` early — steady to `2%`.

### Two limits this pack does not paper over

**The same-sign cells have no per-star tracking.** The sector splitter assigns
matter by field sign, so both stars of a same-sign pair land in one sector: the
tracker reports a single core at the pair midpoint and `separation = nan`.
Their sevenfold activity growth (onset `t ≈ 40`, peak `t ≈ 95`, flat across
N = 128/192/256) is, where frames allow it to be measured, the *merger* of the
two stars — the PP wells close `8.78 → merged` at `t = 33.6`, the MM hills
`8.57 → merged` at `t = 32.8` (`analysis/track_wells.py`), and the ejecta later
drains through the sponge, with net inward boundary flux at round-off
throughout. (An earlier revision blamed a boundary wave arriving at `t ≈ 32`;
the flux measurement retires that.) The centroid null holds over the full run:
≤ `7.8e-04` (PP) and `5.3e-04` (MM) against the runaway's `+2.88`. Centroid
bounds anywhere in this pack are **maxima over the whole run**, not endpoint
values — the endpoint numbers are smaller (`7.3e-04` PP) and quoting the two
interchangeably was an inconsistency with the article, now removed. That the phantom pair merges on the PP
pair's clock, when gravity's sign is opposite between the two, is what identifies
the dominant force as same-field overlap rather than gravity; Bondi's `−−`
repulsion is real but `~35×` too weak to see here. The flux diagnostic cannot
arbitrate it either way — it reads zero in a phantom-only box. The mirror cell,
zero net mass, is the cleanest null.

**No wave zone is reached.** `r·ψ₄` should be flat in the radiation zone. Across
`R = 16/24/32/40`, `r·ψ₄` drops by a factor `31`, a power law of `r^−4.8` against
`r^−1` for radiation. Every shell available in this box is near-field. This pack
therefore reports *no measurable gravitational radiation* out to `R = 40`,
which is consistent with a pair of zero total momentum whose mass dipole is
static — not a measurement of a wave.

### Frames and movies

Cells run with frames keep one still per field every `dt = 10` under
`<cell>/frames/`, with a `FRAMES.md` listing the times kept. The full series
(~250 frames per field) and the stitched movies stay in the gitignored run tree
— 19 movies per cell, redrawn against a single fixed colour scale measured over
the whole run so a colour means the same value in every frame.

The `t = 400` cell keeps no stills: it exists for one moving picture, is twice
as long as every other cell, and no number in the analysis is read off it.

### An earlier campaign lived here

Twenty `convA_*`/`boxC_*` cells occupied this folder until 2026-08-22. They
were run before the initial-data grid alignment was fixed, so every star was
born displaced from the centre of its own gravitational well by a fraction of a
cell — an artefact the same size as the signal. They are in git history and
nothing here depends on them.

## Reproducing

Regenerate this whole pack from the run tree:

```bash
bash research/bondi_dipole/pack_runaway.sh          # every cell -> campaign/ + stars/
FRAME_DT=20 bash research/bondi_dipole/pack_runaway.sh   # fewer stills
```

Safe to re-run at any time, including while cells are still evolving: each cell
folder is rebuilt from scratch, and cells with no time series yet are skipped
with a note. It copies only small artefacts and scrubs absolute machine paths at
runtime (`grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py`) — no
host, user, or site identity enters git.

`FRAME_DT` sets the frame spacing (default 10) and `FRAMES_SKIP` names cells
whose stills are not packed at all; the `t = 400` cell is skipped by default.
Frame thinning itself lives in `research/bondi_dipole/thin_frames.py`.

Two earlier packers, `pack_results.sh` and `pack_campaign.sh`, are **superseded
and refuse to run** — they read run trees that no longer exist. They are kept
for the reasoning in their headers.

To re-run the physics itself, see [`LAUNCH.md`](LAUNCH.md).

## Provenance

- Initial data: **GRTresna** (CTTKHybrid, `BosonStarBH` example, complex scalar
  matter with per-lump signs), 32 MPI ranks on CPU, one solve at a time.
- Evolution: **GRTeclyn** (`RadialRecipe`, CCZ4 + bicomplex scalar matter),
  single rank, one GPU per cell, no mesh refinement.
- Compute: **≈99 GPU-hours** of NVIDIA H100 time across the 34 evolutions, one
  card per evolution. At `N = 128`, `L = 64` the cost is `5.44` GPU-hours per
  1000 units of evolution time, flat to `2%` across sixteen cells; the ladder
  rungs scale `4.4×` (N=192) and `13.4×` (N=256) off that, shallower than the
  naive `N⁴`. The elliptic solves are CPU work on top of this — 20 min (256³) to
  ~4 h (512³) per cell on 32 ranks, overlapping other cells' GPU time. The
  per-cell ledger is kept with the campaign working notes.
- Working notes are narrative and deliberately not part of this pack — every
  number quoted here is re-derivable from the data shipped alongside it.
- Code state: wrapper commit recorded per cell in `campaign/<cell>/metadata.json`;
  the GRTresna matter modifications are in [`patches/`](patches/).
