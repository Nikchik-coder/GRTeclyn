# grteclyn-stationary

Stationary Einstein–scalar solvers with spectral collocation, Newton iteration,
continuation, parameter search and independent physical validation. This directory
is a standalone Python project: copy it to another repository or build its wheel.
It imports no `grteclyn_workflows` code and needs no GRTeclyn binary, yt, HDF5,
research checkout or Git executable to solve a supplied problem.

## Install and use

```bash
# From this directory, independently of the wrapper workspace:
pip install .
pip install '.[plots,symbolic]'  # optional reports and equation derivations
python -m grteclyn_stationary --help
python -m grteclyn_stationary optimize --help
```

Run the portable CPU checks with `pytest tests` after installing pytest.
Build distributable artifacts with `python -m hatchling build`. Both the wheel
and source archive contain the complete solver and license. Install the wheel in
another environment with `pip install /path/to/grteclyn_stationary-0.1.0-py3-none-any.whl`.
CUDA execution needs a matching JAX installation and explicit device selection.

Inside the wrapper workspace, `uv sync --extra stationary` installs the local
package plus its reporting/derivation extras. The wrapper depends on this package;
the dependency does not point back to the wrapper.

```python
from grteclyn_stationary.numerics.spectral import lobatto
from grteclyn_stationary.spinning_wormhole.backgrounds import static_background
from grteclyn_stationary.spinning_wormhole.equations import CollocationProblem
from grteclyn_stationary.numerics.newton import newton
```

## Code layout

- `numerics/`: physics-independent spectral grids, Jacobians, Newton and devices.
- `profiles/`: radial boson-star and Q-ball solvers and scalar couplings.
- `spinning_wormhole/`: rotating Ellis–Bronnikov backgrounds and saved solutions.
- `matter/`: coupled scalar equations, potentials, seeds and continuation.
- `geometry/`: minimal surfaces, exotic-matter integrals and tidal diagnostics.
- `railgun/`: regular-centre scalar rings, independent checks and test-body motion.
- `ringwormhole/`: coupled ring–wormhole studies and matched controls.
- `studies/`: fixed-area study orchestration, diagnostics, validation and reports.
- `search/`: optimisation engines, objectives and continuation between proposals.
- `validation/`, `checks/`, `derivations/`: refinement, independent equations and symbolic checks.
- `exports/`: background tables for evolution codes.
- `commands/`, `workflows/`: argument parsing and reusable solve workflows.

The public command dispatcher provides `optimize`, `validate`, `refine`, `rings`
and `continue-boson`; other tools run as `python -m grteclyn_stationary.commands.<name>`.
Commands that consume saved solutions or campaign configurations need those files
passed explicitly in a new project. Campaign-specific defaults name this research
repository's inputs; those data are not bundled in a solver distribution.

Independent Einstein/Klein–Gordon checks and fresh resolution solves remain part
of acceptance. Newton convergence alone does not validate the physical equations;
stationary validation does not certify dynamical stability.

Source hashes identify the implementation in saved manifests. A Git revision is
recorded only when the solver itself is in a checkout. Old resume certificates
must match the relocated source hashes before resuming.

GRTeclyn pipeline dispatch and movie orchestration belong to the wrapper's
`grteclyn_workflows.campaigns.stationary`, and are not shipped in this package.
