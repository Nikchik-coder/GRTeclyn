"""Measure the linear solve and nonlinear residual at a stalled refinement."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('study', type=Path)
    ap.add_argument('--gpu', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    from ..solver.device import select_device
    select_device(args.gpu, 512)
    import numpy as np
    import jax.numpy as jnp
    import jax.scipy.linalg as jl
    from ..exploration import load_seed, make_problem, pack_seed
    from ..study import write_json
    rows = [json.loads(l) for l in (args.study/'evaluations.jsonl').read_text().splitlines()]
    best = min((r for r in rows if r.get('verdict') == 'PASS'), key=lambda r:r['X_full'])
    state, _ = load_seed(args.study/best['artifact'])
    manifest = json.loads((args.study/'reference/manifest.json').read_text())
    p = make_problem(state, best['config'], 180, 36, tuple(manifest['pin']))
    u = jnp.asarray(pack_seed(p, state))
    r = p.residual(u)
    j = p.jacobian(u)
    scale = 1/jnp.maximum(jnp.max(abs(j), axis=1), 1e-300)
    matrix, rhs = scale[:, None]*j, -scale*r
    lu = jl.lu_factor(matrix)
    du = jl.lu_solve(lu, rhs)
    linear = matrix@du-rhs
    output = dict(candidate=best['artifact'], grid=[180,36],
                  residual=float(jnp.max(abs(scale*r))),
                  step=float(jnp.max(abs(du))),
                  linear_relative=float(jnp.linalg.norm(linear)/jnp.linalg.norm(rhs)),
                  top_rows=[], trials=[], corrections=[])
    for i in np.argsort(-abs(np.asarray(scale*r)))[:12]:
        field, local = divmod(int(i), p.n)
        ix, iy = divmod(local, p.ny+1)
        output['top_rows'].append(dict(index=int(i),
            field=p.tags[field] if field<p.nf else 'border', ix=ix, iy=iy,
            x=float(p.sx[ix]) if ix<=p.nx else None,
            raw=float(r[i]), scaled=float(scale[i]*r[i])))
    norm = jnp.linalg.norm(scale*r)
    for damping in (1., .5, .1, .01, 1e-4):
        trial = p.residual(u+damping*du)
        output['trials'].append(dict(damping=damping,
            norm_ratio=float(jnp.linalg.norm(scale*trial)/norm),
            linearization_error=float(jnp.linalg.norm(scale*(trial-r)-damping*(matrix@du))/norm)))
    for iteration in range(3):
        du = du+jl.lu_solve(lu, rhs-matrix@du)
        trial = p.residual(u+du)
        output['corrections'].append(dict(iteration=iteration+1,
            linear_relative=float(jnp.linalg.norm(matrix@du-rhs)/jnp.linalg.norm(rhs)),
            norm_ratio=float(jnp.linalg.norm(scale*trial)/norm),
            step=float(jnp.max(abs(du)))))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out, output)
    print(json.dumps(output), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
