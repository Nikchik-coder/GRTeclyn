# Publishable simulation results

Light, GitHub-friendly extracts of campaign outputs. Full evolutions (frames,
plotfiles, gridinit, metric stacks) stay in the gitignored `/runs` tree on the
machine that produced them.

One directory per paper. Everything a paper depends on lives inside its own
directory — there are no loose campaign folders at this level.

| Paper pack | Status |
|---|---|
| [`bondi-dipole-runaway/`](bondi-dipole-runaway/) | Complete. Data, derived tables and the refit tooling ship together. |
| [`wormhole-dynamics/`](wormhole-dynamics/) | Complete. Published as [arXiv:2604.00071](https://arxiv.org/abs/2604.00071). |

The pack scripts scrub machine identity at runtime through the shared scrubber
[`grteclyn_wrapper.packaging.scrub_paths`](../grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py)
— host, user and home-path tokens are derived from the environment, never
hard-coded — and then gate the pack: a surviving token fails the run.

### `bondi-dipole-runaway/`

A positive-active-mass and a negative-active-mass soliton, released at rest in
full 3+1 numerical relativity with constraint-solved matter, self-accelerate
together; both same-sector controls are null. Both axes of `a = GM/d²` are
direct measurements — `a ∝ d^−2.028` across separations `d = 8…20`, and
`a ∝ M^0.966 ± 0.061` across a ×2.46 mass range.

The pack holds the per-cell time series, dressed-star tables, solve and
evolution parameters, code patches, curated frames and movies, and the derived
tables — plus the physics findings, the debugging trail, the matter model and
the launch reference as standalone documents.

You can re-derive the headline number without a GPU:

```bash
# from the repository root
uv run python results/bondi-dipole-runaway/tools/fit_mass_law.py
```

Start with [`bondi-dipole-runaway/README.md`](bondi-dipole-runaway/README.md),
then [`campaign/README.md`](bondi-dipole-runaway/campaign/README.md) for how to
read a cell name and every column in the data files.

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
consume-state record — as `.pdf` and `.png`.
