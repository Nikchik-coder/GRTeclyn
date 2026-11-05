"""Diagnose one production Jacobian without running a stationary search.

Run only inside an approved capped job. Logs and compiler reports stay in
the fresh output directory; no large matrix is copied back to the host.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)

    from .device import configure_jax
    from .newton import _donating_equilibrator
    from ..railgun_wormhole import read_restart, validate_plan
    from ..exploration import make_problem, pack_seed
    import numpy as np
    jax = configure_jax()
    plan = json.loads(Path('research/optimisation/studies/railgun_throat_validation.json').read_text())
    validate_plan(plan)
    state, config = read_restart(plan)
    nx, ny = plan['grids'][-1]
    problem = make_problem(state, config, nx, ny,
                           ('minimal_area', 4*np.pi*plan['throat_radius']**2),
                           frequency=state['frequency'], amplitude=config['amplitude'])
    seed = pack_seed(problem, state)
    device = jax.devices()[0]

    def mark(stage, **extra):
        print(json.dumps(dict(stage=stage, monotonic=time.monotonic(),
                              device_memory=device.memory_stats(), **extra), default=str), flush=True)

    def report(name, compiled):
        (args.out/f'{name}.hlo').write_text(compiled.as_text())
        mark(name, memory=str(compiled.memory_analysis()),
             inputs=str(compiled.input_formats), outputs=str(compiled.output_formats))

    mark('start', jax=jax.__version__, shape=[len(seed), len(seed)], dtype='float64')
    # Compile scaling before any dense matrix exists, separating compiler
    # allocations from the live producer buffer and execution temporaries.
    operation = _donating_equilibrator()
    compiled = operation.lower(jax.ShapeDtypeStruct((len(seed), len(seed)), np.float64)).compile()
    report('scaling_abstract', compiled)
    jac = problem.jacobian(seed)
    jac.block_until_ready()
    mark('jacobian_ready', format=str(jac.format), committed=jac.committed,
         bytes=jac.nbytes)
    actual = operation.lower(jac).compile()
    report('scaling_actual', actual)
    try:
        scaled, scale = actual(jac)
        scaled.block_until_ready()
        mark('scaling_done', format=str(scaled.format))
        import jax.scipy.linalg as jsl
        factor = jax.jit(jsl.lu_factor, donate_argnums=(0,)).lower(scaled).compile()
        report('lu', factor)
        lu, piv = factor(scaled)
        lu.block_until_ready()
        mark('lu_done')
        rhs = scale*problem.residual(seed)
        correction = jsl.lu_solve((lu, piv), rhs)
        correction.block_until_ready()
        if not np.isfinite(np.asarray(correction)).all():
            raise RuntimeError('nonfinite correction')
        mark('solve_done', correction_inf=float(jax.numpy.max(jax.numpy.abs(correction))))
    except Exception as exc:
        mark('failed', error=str(exc))
        raise


if __name__ == '__main__':
    main()
