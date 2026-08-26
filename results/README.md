# Publishable simulation results

Light, GitHub-friendly extracts of campaign outputs used by papers. Full
evolutions (frames, plotfiles, gridinit, metric stacks) stay in the gitignored
`/runs` tree on the machine that produced them.

One directory per paper. Everything a paper depends on lives inside its own
directory — there are no loose campaign folders at this level.

| Paper pack | Article | Regenerators |
|---|---|---|
| [`matter-first-automated-discovery-of-transient-spacetime-shortcuts/`](matter-first-automated-discovery-of-transient-spacetime-shortcuts/) | [`research/neuralspacetime/article/research.tex`](../research/neuralspacetime/article/research.tex) | [`pack_publishable_results.sh`](../research/neuralspacetime/pack_publishable_results.sh) (figures, tables, promotion runs) · [`pack_search_campaigns.sh`](../research/neuralspacetime/pack_search_campaigns.sh) (`search/`) |
| [`bondi-dipole-runaway/`](bondi-dipole-runaway/) | in preparation — source material in the pack itself | [`pack_results.sh`](../research/bondi_dipole/pack_results.sh) (published cells) · [`pack_campaign.sh`](../research/bondi_dipole/pack_campaign.sh) (`campaign/`) |
| [`wormhole-dynamics/`](wormhole-dynamics/) | [`research/wormholedynamics/article.md`](../research/wormholedynamics/article.md) — published as [arXiv:2604.00071](https://arxiv.org/abs/2604.00071) | [`plot_diagnostic.sh`](../grteclyn-wrapper/scripts/plot/plot_diagnostic.sh) (diagnostics, embedding, `K_z` panels) · [`plot_extracted_psi4.py`](../grteclyn-wrapper/src/grteclyn_wrapper/visualisation/process_wave/plot_extracted_psi4.py) (`--combined --strain` GW panels) |

All pack scripts scrub machine identity at runtime through the shared scrubber
[`grteclyn_wrapper.packaging.scrub_paths`](../grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py)
— host, user and home-path tokens are derived from the environment, never
hard-coded — and then gate the pack: a surviving token fails the run.

### `matter-first-automated-discovery-of-transient-spacetime-shortcuts/`

Automated search for transient spacetime shortcuts sourced by phantom matter,
carried from first discovery through to paper-resolution promotion runs.

- `search/` — **[the five search campaigns](matter-first-automated-discovery-of-transient-spacetime-shortcuts/search/)**,
  oldest first, each warm-started from the one before. Start with that
  directory's README: it explains the two objectives, why the deepest number
  and the headline number differ, and which evaluations survive on disk.
- `article/`, `figures/` — the plot data and figures the paper renders from.
- `runs/` — promotion (HQ) and geometry-atlas runs at paper resolution.
- `validation/`, `manifests/` — launch validation records and the run manifests.

Headline: **35.94 %** persistence-gated evolving-geodesic path saving, and
**48.38 %** ungated in the depth lineage.

### `bondi-dipole-runaway/`

A positive-active-mass and a negative-active-mass soliton, released at rest in
full 3+1 NR with constraint-solved matter, self-accelerate together; both
same-sector controls are null. Holds the per-cell time series, dressed-star
tables, solve/evolution parameters, code patches, curated frames and movies, and
the derived tables — plus the physics findings, the debugging trail, the matter
model, and the launch reference as standalone documents.

### `wormhole-dynamics/`

Nonlinear collapse of a traversable wormhole and the gravitational waves it
emits, in two configurations sharing throat radius `R = 0.5` and width
`sigma = 0.5`:

- `unperturbed/` — `A0 = 0.0`, `A2 = 0.0`: the control.
- `perturbed/` — `A0 = 0.0`, `A2 = 0.02`: the quadrupolar perturbation that
  drives the collapse and sources the `ℓ = 2` signal.

Each directory holds the constraint and collapse-diagnostic plots, the
embedding and `K_z` panels, the six-panel `psi4` GW analyses at several
mass/distance configurations, the run parameters (`params_2gpu.txt`) and the
consume-state record.

Figures ship as `.pdf` and `.png`. The `.eps` renders of the three `psi4`
panels were dropped: matplotlib emitted every scatter point as vector geometry,
making them ~215× the size of the `.pdf` of the same figure at no added
fidelity.
