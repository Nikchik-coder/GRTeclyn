"""Prepare a bounded, unperturbed 3+1 ring pilot from a certified export."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evolution import COMPONENTS, digest, grid_layout


def prepare(data_directory, template, *, checkpoints):
    if checkpoints != 'off':
        raise ValueError('this first pilot is prepared without checkpoints')
    data_directory = Path(data_directory).resolve()
    manifest = json.loads((data_directory/'manifest.json').read_text())
    outcome = json.loads((data_directory/'outcome.json').read_text())
    core = json.loads((data_directory/'corridor.json').read_text())
    grid = data_directory/'initial.gridinit'
    if (not outcome.get('accepted') or not core.get('accepted')
            or core.get('join_continuity') != 'C6; degree-13 Bernstein step'
            or core.get('radius') != .4 or core.get('degree') != 6
            or core.get('comparison_degree') != 8 or core.get('tolerance') != 1e-8
            or manifest.get('components') != COMPONENTS
            or manifest.get('matter_model') != 'grtresna_complex_scalar'
            or manifest.get('perturbation') != 'none'
            or manifest.get('n') not in (96, 128) or manifest.get('length') != 32.
            or manifest.get('ghosts', 0) < 4 or abs(manifest.get('frequency', 0)-.70) > 1e-10
            or digest(grid) != outcome['gridinit_sha256']):
        raise ValueError('certified, hash-matched omega=.70 / L=32 / N=96 or 128 export required')
    n = manifest['n']
    layout = grid_layout(grid)
    width = n + 2*manifest['ghosts']
    if (layout['components'] != COMPONENTS or layout['shape'] != [width]*3
            or layout['spacing'] != [32/n]*3
            or layout['origin'] != [-manifest['ghosts']*32/n]*3):
        raise ValueError('grid layout does not match the evolution cell centres')
    # Paths in this generated run template may be absolute. It belongs under
    # runs/, alongside its initial data, and must not enter a tracked archive.
    text = f'''# Unperturbed omega=0.70 canonical ring; finite 3+1 plumbing pilot.
verbosity = 1
output_path = "."
amr.plot_file = "RingPlt"
amr.check_file = "RingChk"
amr.plot_files_output = 1
amr.checkpoint_files_output = 0
checkpoint_interval = -1
plot_interval = 25
amr.plot_vars = {' '.join(COMPONENTS)}
amr.derive_plot_vars = Weyl4 constraints
pout_subpath = pout
data_subpath = data
print_progress_only_to_rank_0 = 1
recipe_initial_data_file = "{grid}"
recipe_matter_model = grtresna_complex_scalar
recipe_scalar_mass = {manifest['mass']:.17g}
recipe_scalar_sign = 1
recipe_scalar_lambda = 0
recipe_scalar_mu = 0
recipe_exotic_matter = 0
rl_enabled = 0
trajectory_mode = 0
controller_reservoir_mode = 0
rl_pump_stop_time = 0
L_full = 32
N_full = {n}
center = 16 16 16
max_level = 0
regrid_interval = 16
regrid_threshold = 0.01
max_box_size = 32
min_box_size = 16
isPeriodic = 0 0 0
hi_boundary = 1 1 1
lo_boundary = 1 1 1
dt_multiplier = 0.02
stop_time = 2
max_steps = -1
max_spatial_derivative_order = 4
nan_check = 1
min_chi = 1e-8
min_lapse = 1e-10
lapse_advec_coeff = 1
lapse_coeff = 2
lapse_power = 1
shift_advec_coeff = 0
shift_Gamma_coeff = 0.75
eta = 1
formulation = 1
kappa1 = 0.1
kappa2 = 0
kappa3 = 1
covariantZ4 = 1
sigma = 0.1
G_Newton = 1
calculate_constraint_norms = 1
calculate_complex_scalar_diagnostics = 1
constraint_norms_interior_radius = 8
calculate_energy_conditions = 0
calculate_curvature_invariants = 0
'''
    template = Path(template)
    template.parent.mkdir(parents=True, exist_ok=True)
    if template.exists():
        if template.read_text() != text:
            raise ValueError('refusing to overwrite an existing run template')
    else:
        template.write_text(text)
    return dict(template=str(template), n=n, length=32., stop_time=2.,
                dx=32/n, checkpoints=False, max_level=0,
                gridinit_sha256=outcome['gridinit_sha256'],
                perturbation='none', stability='not_assessed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--checkpoints', required=True, choices=['off'])
    args = parser.parse_args()
    print(json.dumps(prepare(args.data_dir, args.template, checkpoints=args.checkpoints), indent=2))


if __name__ == '__main__':
    main()
