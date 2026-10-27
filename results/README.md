# Publishable simulation results

Light, GitHub-friendly extracts of campaign outputs. Full evolutions (frames,
plotfiles, gridinit, metric stacks) stay in the gitignored `/runs` tree on the
machine that produced them.

One directory per paper. Everything a paper depends on lives inside its own
directory — there are no loose campaign folders at this level.

| Paper pack | Status |
|---|---|
| [`bondi-dipole-runaway/`](bondi-dipole-runaway/) | Complete, version 2 (2026-10-26): the 24 reruns on the fixed code behind the paper's v2, [arXiv:2608.24577](https://arxiv.org/abs/2608.24577). |
| [`wormhole-dynamics/`](wormhole-dynamics/) | Complete. Published as [arXiv:2604.00071](https://arxiv.org/abs/2604.00071). |
| [`merger/`](merger/) | Complete. The colliding-wormholes campaign behind [arXiv:2610.13206](https://arxiv.org/abs/2610.13206) (v2); the paper cites tag `v1.0.1-wormhole-merger`. |
| [`spinningwormhole/`](spinningwormhole/) | Complete. Rotating drainholes: the solver's solutions and the 3D runs of the rotating-wormholes paper. |

The pack scripts scrub machine identity at runtime through the shared scrubber
[`grteclyn_wrapper.packaging.scrub_paths`](../grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py)
— host, user and home-path tokens are derived from the environment, never
hard-coded — and then gate the pack: a surviving token fails the run.

### `bondi-dipole-runaway/`

A star of positive mass and a star of negative mass, released at rest in full 3+1 numerical relativity from
constraint-solved initial data, accelerate together at constant separation, as Bondi predicted, while the same-sign
pairs and the isolated stars stay at rest. The acceleration follows Newton's law in both separation and mass
(`a ∝ d₀^−1.95`, `a ∝ M̄^0.97±0.16`) and converges at fourth order with resolution. Version 2 of the pack
(2026-10-26) holds the 24 reruns on the fixed code behind the paper's v2.

The pack holds each run's time series, parameter files and launch record, stills of the runs the figures draw, the
videos the paper links, the figures, the matter model and the launch reference. Every figure and every number the
paper quotes is redrawn from the pack without a GPU:

```bash
# from the repository root
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.bondi_dipole
```

Start with [`bondi-dipole-runaway/README.md`](bondi-dipole-runaway/README.md), then
[`campaign/README.md`](bondi-dipole-runaway/campaign/README.md) for how to read a run name and the files of a run.

### `wormhole-dynamics/`

Nonlinear collapse of a traversable wormhole and the gravitational waves it
emits, published as [arXiv:2604.00071](https://arxiv.org/abs/2604.00071). Two
configurations share throat radius `R = 0.5` and width `sigma = 0.5`:

- `unperturbed/` — `A0 = 0.0`, `A2 = 0.0`: the control.
- `perturbed/` — `A0 = 0.0`, `A2 = 0.02`: the quadrupolar perturbation that
  drives the collapse and sources the `ℓ = 2` signal.

Each holds the constraint and collapse-diagnostic plots, the embedding and
`K_z` panels, the six-panel `psi4` gravitational-wave analyses at several
mass/distance configurations, the run parameters (`params_2gpu.txt`) and the
consume-state record.

Figures ship as `.pdf` and `.png`. The `.eps` renders of the three `psi4`
panels were dropped: matplotlib emitted every scatter point as vector geometry,
making them ~215× the size of the `.pdf` of the same figure at no added
fidelity.

### `merger/`

Pairs of Ellis–Bronnikov wormhole throats, held open by a phantom scalar field, in full 3+1
numerical relativity: the data of *Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity:
mergers, fly-bys and gravitational waves* ([arXiv:2610.13206](https://arxiv.org/abs/2610.13206), v2).
An isolated throat collapses to a black hole or inflates, depending on the sign of a small
perturbation. Throats with opposite scalar charges attract and merge: a head-on collision forms
a common horizon around both throats while they are still open, and the horizon then loses 28 %
of its area as it absorbs the scalar field. Pairs that fly past each other form no horizon, and
both throats inflate. No throat survives more than a few orbital periods, so these binaries do
not inspiral.

Holds the four evolution streams per run (thinned, with the death window kept whole), the
extracted waveforms at two radii, the launch and parameter provenance, movies, thinned
stills, the offline horizon scan, and generated summary tables.

### `spinningwormhole/`

The data of *Rotation slows the instability of Ellis–Bronnikov wormholes*
([arXiv:2610.29941](https://arxiv.org/abs/2610.29941)). Stationary rotating Ellis–Bronnikov
wormholes from slow rotation to 99 % of the speed of
light, and their nonlinear 3+1 evolution: rotation slows the static wormhole's radial
instability, near 30 % of the extremal angular momentum the unperturbed throat expands
instead of collapsing, and from 58 % upward no growth is found over the evolved times.
Holds the spectral solver's solutions, the headers of the background tables, and
the parameter files and diagnostic streams of the 61 runs the paper uses, with a registry
saying where the paper uses each. Every figure rebuilds from the pack without a GPU; start
with [`spinningwormhole/README.md`](spinningwormhole/README.md).
