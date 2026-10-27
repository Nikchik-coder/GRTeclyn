# Bondi dipole runaway — results pack

The data behind N. M. Shirokov and I. Nachevsky, *The Bondi dipole in full numerical relativity: a self-accelerating
positive–negative mass binary*, arXiv:2608.24577 (v2). A star of a positive-mass scalar field and a star of a
negative-mass one, released at rest in full 3+1 numerical relativity from constraint-solved initial data, accelerate
together at constant separation while their total momentum stays zero.

**This is version 2 of the pack (2026-10-26).** Every simulation was rerun on 2026-10-23 to 10-25 with fourth-order
time integration and corrected initial data (see "What changed from v1"), so every number differs from v1. The v1
pack, behind the paper's v1, is the tag `v1.0-bondi-dipole`.

**Cite this pack** as the `results/bondi-dipole-runaway/` tree of <https://github.com/Nikchik-coder/GRTeclyn> at the
release `v2.0-bondi-dipole`, archived on Zenodo as version DOI 10.5281/zenodo.23662692 (concept DOI
10.5281/zenodo.23245933, which resolves to the newest version). The same repository holds the evolution code (`Examples/RadialRecipe/`) and the launchers
(`grteclyn-wrapper/scripts/campaigns/bondi_dipole/`). Every figure of the paper is drawn, and every number it quotes is
printed, from this pack alone by `python -m grteclyn_wrapper.visualisation.bondi_dipole` ("The figures", below); where
a number here and the script disagree, the script is the arbiter.

The pack holds the light artefacts: per-run time series, the parameter files and launch record of each run, stills of
the runs the figures draw, the five videos the paper links, and the figures. Plotfiles, the initial-data files and the
full frame sets stay in the untracked run tree.

## Names

The paper's two fields are Φ₊ (positive mass) and Φ₋ (negative mass). The data streams call them `canon` and `phantom`;
the launchers call them sector 0 and sector 1 (`BONDI_S0`, `BONDI_S1`). Run labels are the paper's Table II: P and M name
a positive- and a negative-mass star, followed by the initial separation d₀ (PM10 is the reference pair, MP10 the same
pair with the two stars exchanged); E labels the equal-mass pairs by their mass relative to PM20, R the unequal-mass
pairs by |M₋|/M₊. A run's folder is its label, its box side and its cells per side (`PM10_L64_N256`), with a stop time
other than 200 appended (`PM10_L64_N128_t400`).

## The result

The paper's Table III is the complete list; these are its main rows.

| test | runs | measured | Bondi's prediction |
|---|---|---|---|
| displacement of the midpoint, ΔX(200) | PM10, N 256 | 2.87 ± 0.03 | 2.86 for a = M̄/d₀² |
| acceleration a, in 10⁻⁴ | PM10, N 256 / 192 / 128 | 1.45 / 1.43 / 1.27 (order of convergence 4.2) | 1.43 |
| change of the separation, t ≤ 200 | PM10, N 256 | +0.05 % | 0 |
| signed momentum, \|P\|/P⁽⁺⁾ at t 200 | PM10, N 256 | 0.001 | 0 |
| stars exchanged, a relative to PM10 | MP10, N 128 | −1.0001 | −1 |
| a against d₀, exponent | PM8–PM20 | −1.95 | −2 |
| a against M̄, exponent | E0.64, PM20, E1.34, E1.57 | 0.97 ± 0.16 | 1 |
| pull on the star whose partner changed, relative to PM10 | R0.60, R0.80, R1.33 | 0.610, 0.806, 0.751 | 0.600, 0.803, 0.747 |
| largest displacement over t ≤ 200 | PP10, MM10 (centroid); P (core) | 4, 3, 3 × 10⁻¹³ | 0 |
| speed at t 1000, leading / trailing star | PM10-rec | 0.115 / 0.108 | equal |

No gravitational radiation is detected: in PM10-L128 the ℓ = 2 amplitude of Ψ₄ falls as R^−4.7 out to R = 40
(R^−1 if radiative), so every extraction sphere lies in the near zone. The isolated negative-mass star M-t1000 changes
its peak field by +0.11 % over t ≤ 1000.

## What is where

| path | contents |
|---|---|
| `campaign/<group>/<run>/` | every run, filed by the question it answers; the guide, with the files of a run, is [`campaign/README.md`](campaign/README.md) |
| [`runs_registry.tsv`](runs_registry.tsv) | one line per run: its folder, its Table II label, where the paper uses it, its outcome |
| [`binaries.tsv`](binaries.tsv) | the evolution and solver builds, and the repository commit each run was launched from |
| [`trust_windows.tsv`](trust_windows.tsv) | the last trustworthy time of a run that stops being trustworthy before its end (none) |
| [`LAUNCH.md`](LAUNCH.md) | how a run is launched, what each launch variable selects, the settings of every run |
| [`MATTER_MODEL.md`](MATTER_MODEL.md) | the two-field model, the star initial data, the code modifications |
| `stars/` | the August 2026 star tables (r, φ₀(r), α(r)) and the M(ω) scans; the reruns rebuild each table at launch (see "What changed from v1"), and their dressed masses are in `campaign/06_mass/mass_law.csv` |
| `patches/` | the solver and wrapper modifications this model needs |
| [`movies/youtube/`](movies/youtube/README.md) | the five videos the paper links (PM10 at N 256, PM10-t400, PM10-rec, PP10, MM10), with their descriptions |
| `figures/` | the paper's figures, one folder per group, each a PDF beside its PNG; [`figures/FIGURES.md`](figures/FIGURES.md) maps each to its label, script and runs |

The groups:

| folder | runs | the question |
|---|---|---|
| `02_lone_star/` | P, M-t1000 | does an isolated star stay at rest, and does the negative-mass star last |
| `03_same_sign/` | MP10, PP10, MM10 | does the motion reverse with the stars exchanged; do pairs without a mass dipole stay at rest |
| `04_runaway/` | PM10-t400, PM10-rec, PM10-L128 | the pair beyond t 200 and to t 1000; the doubled domain and the wave extraction |
| `05_separation/` | PM8, PM12, PM16, PM20 | a against the separation |
| `06_mass/` | E0.64, E1.34, E1.57, R0.60, R0.80, R1.33; `mass_law.csv` | a against the mass; each star against its partner's mass |
| `09_convergence/` | PM10 and M at N 128, 192, 256 | the resolution study, and the reference run PM10 at N 256 |

### The paper's quantities in the streams

Every `.dat` carries a `#` header naming its columns.

| file | columns | the paper's quantity |
|---|---|---|
| `sector_barycenters.dat` | `bary_x_canon`, `bary_x_phantom` | the barycentres x̄⁽⁺⁾, x̄⁽⁻⁾ (Eq. 6); their mean is the midpoint X, and ΔX = X(t) − X(0) |
| `sector_dynamics.dat` | `core_x_canon`, `core_x_phantom`; `coord_sep`; `proper_sep` | the cores; the separation d; its proper length ∫√γ_xx dx |
| `sector_dynamics.dat` | `px_canon`, `px_phantom`, `px_total` | the matter momenta P⁽⁺⁾, P⁽⁻⁾ and P = P⁽⁺⁾ − P⁽⁻⁾ (Eq. 10) |
| `sector_dynamics.dat` | `shift_x_canon`, `shift_x_phantom` | the shift β^x at each core |
| `constraint_norms.dat` | `L2_Ham`, `L2_Mom` | ‖H‖₂ and ‖M‖₂ over the domain (downsampled to Δt 0.5) |
| `constraint_shells.dat` | `Ham_r<k>`, `Mom_r<k>` | the constraints in unit shells k ≤ r < k + 1 about the centre, which Appendix A combines into its regions |
| `psi4_mode_l2m0.dat`, `psi4_mode_l2_all.dat` | per sphere | the multipoles of Ψ₄ on the extraction spheres |

The acceleration a is twice the quadratic coefficient of a least-squares fit of X(t) over 5 ≤ t ≤ t_end (Eq. 8).
Positions are coordinates in the box, whose centre is (32, 32, 32) for L 64, so PM10's stars start at x = 37 (Φ₊)
and x = 27 (Φ₋); PM10-L128's centre is (64, 64, 64). PM10-rec's box moves with the pair: every 2 units of drift the
data shift back by 2 units (31 shifts by t 1000), so its positions jump at each shift, while separations and matter
totals do not; `treadmill.dat` in its folder records the shifts.

## What changed from v1

The v1 runs carried two defects, fixed before the reruns:

- **Time integration.** The evolution refilled the ghost cells on every Runge–Kutta stage by interpolating the old and
  new states in time, which overwrote the stage values and made RK4 first order. Fixed in c12664fd
  (`RadialRecipeLevel::specificEvalRHS`); in the reruns ΔX(200) and a converge at orders 4.4 and 4.2.
- **Initial data.** Each tabulated star joined its interior lapse to the exterior with a small step (fixed in the
  wrapper's profile builder, `_lapse_join`); the converter filled each face's outermost layer from a solve cell outside
  the evolution box (fixed in e3992acf); and the solver and the evolution's painting of the matter divided Π by
  different lapses and interpolated the star tables differently (fixed in GRTresna 9a85e6a, below).

Each rerun repeats its v1 run's grid, stars, separation, absorbing layer, gauge, time step and stop time, except
M-t1000 and PM10-rec, which moved from N 128 to N 192. Dropped in v2: the star-family stationarity runs (P and the resolution study of M cover both stars), the three
numerical checks of v1 (a tighter solve, one refinement level, doubled shift damping; each moved ΔX(200) by less than
0.01 % in v1), PM10-off, and the same-sign pairs at N 192 and 256. Added: M at N 192 and 256; PM10-rec now runs to
t 1000.

## The figures

Rebuild them from the repository root on a machine with TeX Live (the labels go through pdflatex):

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.bondi_dipole            # all
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.bondi_dipole article    # Figs. 1-7 and the quoted numbers
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.bondi_dipole convergence  # Figs. 8-9 (Appendix A)
```

The `article` target also prints every number the text quotes, in order of appearance. `figures/FIGURES.md` lists
each figure with its label, file, drawing function and runs.

## Reproducing

To repack from the run tree (copies only the light artefacts and scrubs machine paths; the packer lives with the
paper's source on the repository's `trunk` branch, since `research/` is not part of the release line):

```bash
bash research/bondi_dipole/pack_runaway.sh
```

To rerun a simulation, see [`LAUNCH.md`](LAUNCH.md): each run's `launch_config.sh` is the exact command that produced
it.

## Provenance

- Initial data: GRTresna (constraint solve with a signed matter source per star), branch
  `fix/bondi-solve-matches-painter` of <https://github.com/Nikchik-coder/GRTresna>, commit 9a85e6a; the fix itself is
  `patches/grtresna-solve-matches-painter.diff`.
- Evolution: GRTeclyn (`RadialRecipe`, CCZ4 with the two scalar fields), one build for every run: commit aa0dc4a1 with
  the time-integration fix c12664fd (`binaries.tsv`). One NVIDIA H100 per run, a single rank, no mesh refinement.
- Compute: about 95 GPU-hours for the 24 evolutions; a run to t 200 takes about 1, 4 and 11 hours at N 128, 192 and
  256.
- Each run's `metadata.json` records the repository commit it was launched from, and `launch_config.sh` its full
  environment.
