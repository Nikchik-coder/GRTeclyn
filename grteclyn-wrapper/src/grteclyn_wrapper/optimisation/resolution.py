"""Finer-grid screening and independent re-solves of search incumbents.

A screen evaluates the existing spectral polynomial at new nodes; it does
not establish solution convergence. Only successful independent re-solves
may produce a resolution-validated best. Neither test assesses stability.
"""
from __future__ import annotations

import dataclasses
import gc
import json
from pathlib import Path
import time

import numpy as np

from .exploration import FIELDS, make_problem, pack_seed, solve_trial, save_trial
from .exoticity import exotic_x
from .potentials import PolynomialPotential
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import tail_ratio


def refinement_grids(nx, ny):
    """Three increasing grids, keeping the radial midpoint a node."""
    return [(nx, ny), (2*int(np.ceil(.6*nx)), int(np.ceil(1.2*ny))),
            (2*int(np.ceil(.7*nx)), int(np.ceil(1.4*ny)))]


def screen_trial(state, config, nx, ny, pin, d2):
    """Check all five imposed equations and unused constraints, without LU.

    Interior thresholds use the campaign's existing C >= .05 domain.
    Far-end raw residuals are recorded separately: these coordinate-weighted
    rows cannot be compared directly with Cartesian evolution constraints.
    """
    p = make_problem(state, config, nx, ny, pin)
    u = pack_seed(p, state)
    arrays = [np.asarray(v) for v in p.fields(u)]
    if not all(np.isfinite(v).all() for v in arrays):
        raise RuntimeError("nonfinite interpolated fields")
    F, W, N, B, psi = arrays
    sigma, xi_t = p.scale(u)
    omega, psim = p.unpack(u)[-2:]
    if sigma <= 0 or B.min() <= 0 or psim == 0:
        raise RuntimeError("invalid scale, B or scalar endpoint")
    diag = p.diagnostics(u)
    mask = diag['C2_i'] >= .05**2
    residual = np.asarray(p.residual(u))
    blocks = residual[:5*p.n].reshape(5, nx+1, ny+1)
    imposed = {tag: float(np.max(abs(v[1:-1][mask])))
               for tag, v in zip(p.tags, blocks)}
    far = {tag: float(np.max(abs(v[1:-1]))) for tag, v in zip(p.tags, blocks)}
    e19 = float(np.max(abs(diag['E19'][mask])))/d2
    ec = float(np.max(abs(diag['E_c'][mask])))
    jerr = float(np.max(abs(sigma**2*diag['j_of_x'][mask]-config['J'])))/max(1.,abs(config['J']))
    x = exotic_x(1., p.map, p.sx, p.sy, p.Dx, F, N, B, psi)
    held = sigma*x['R_e'] if pin[0] == 'R_e' else sigma**2*x['area_throat']
    pinerr = abs(held/pin[1]-1)
    boundary = float(np.max(abs(blocks[:, [0,-1], :])))
    border = float(np.max(abs(residual[5*p.n:])))
    tail = max(tail_ratio(v, axis=ax) for v in
               (F-p.f_bg, W-omega*p.q, N, B-1, psi-psim*p.psi_prof) for ax in (0,1))
    interval = bool(np.min(psi/psim) >= -1e-8 and np.max(psi/psim) <= 1+1e-8)
    ok = (max(e19, ec, *imposed.values()) <= 1e-8 and jerr <= 1e-6
          and pinerr <= 1e-8 and boundary <= 1e-10 and border <= 1e-8
          and np.isfinite(tail) and interval and np.isfinite(residual).all())
    row = dict(nx=nx, ny=ny, X=x['X'], X_A=x['X_A'],
               R_e=sigma*x['R_e'], R_A=sigma*x['R_A'], R_pol=sigma*x['R_pol'],
               E19=e19, E_c=ec, J_error=jerr, pin_error=pinerr,
               imposed_core=imposed, imposed_all=far, boundary=boundary,
               border=border, tails=float(tail), scalar_in_vacuum_interval=interval,
               verdict='PASS' if ok else 'ABOVE_GATE', stability='not_assessed')
    result = dict(zip(FIELDS, arrays))
    result.update(sx=p.sx, sy=p.sy, sigma=sigma, xi_t=xi_t, omega=omega,
                  psim=psim, gamma=config['gamma'], map=p.map)
    return result, row


def consistent(records, score_key='X'):
    """Reject missing, failed or nonfinite checks; compare the last two bills."""
    if len(records) < 2 or any(r.get('verdict') != 'PASS' for r in records):
        return False, None
    values = [float(r.get(score_key, np.nan)) for r in records]
    if not all(np.isfinite(v) and v > 0 for v in values):
        return False, None
    drift = abs(values[-1]/values[-2]-1)
    return drift <= 1e-6, drift


def check_candidate(state, config, grids, pin, d2, directory, *,
                    method='refine', score_key='X'):
    """Persist every check, fail closed, and never export a failed candidate."""
    if method not in ('screen', 'refine'):
        raise ValueError(method)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    (directory/'manifest.json').write_text(json.dumps(dict(
        method=method, config=config, grids=grids, pin=pin,
        newton_acceptance=1e-9, independent_constraint_gate=1e-8,
        relative_bill_tolerance=1e-6, score_key=score_key,
        stability='not_assessed'), indent=2)+'\n')
    records, source = [], state
    for nx, ny in grids:
        start = time.monotonic()
        try:
            if method == 'screen':
                state, row = screen_trial(source, config, nx, ny, pin, d2)
            else:
                state, row = solve_trial(state, config, nx, ny, pin, d2,
                                        max_iter=24, newton_tol=1e-9)
            row['seconds'] = time.monotonic()-start
            save_trial(directory/f'diagnostic_{nx}x{ny}.npz', state, config, row, pin)
        except (RuntimeError, ValueError, FloatingPointError) as err:
            row = dict(nx=nx, ny=ny, verdict='FAILED', error=str(err),
                       seconds=time.monotonic()-start)
        records.append(row)
        with (directory/'checks.jsonl').open('a') as fh:
            fh.write(json.dumps(row)+'\n')
        print(f"  resolution {method} {nx}x{ny}: {json.dumps(row)}", flush=True)
        gc.collect()
        import jax
        jax.clear_caches()
        if row['verdict'] == 'FAILED':
            break
    ok, drift = consistent(records, score_key)
    ok = ok and len(records) == len(grids)
    result = dict(passed=bool(ok), method=method, relative_bill_drift=drift,
                  records=records)
    (directory/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result, state


def save_checked(path, state, config, metadata, result):
    """Write actual checked fields; screening is explicitly provisional."""
    if not result['passed']:
        raise ValueError('cannot export a failed resolution check')
    row = result['records'][-1]
    pot = PolynomialPotential.kink_q(config['m'], state['psim'], tuple(config['q']))
    meta = dict(metadata)
    # A stationary refinement provides no perturbative stability result.
    meta.pop('lam_eta0', None)
    meta.pop('j0', None)
    meta.update(config)
    meta.update(row)
    meta.update(**{k:float(state[k]) for k in ('sigma','xi_t','omega','psim')},
                potential_coeffs=list(map(float, pot.coeffs)),
                radial_map={'class':type(state['map']).__name__, **dataclasses.asdict(state['map'])},
                resolution=result, stability='not_assessed',
                slot='best_clean' if result['method']=='refine' else 'best_screened',
                resolution_validated=result['method']=='refine')
    # Replace atomically so an interrupted write cannot destroy the incumbent.
    path = Path(path)
    tmp = path.with_suffix('.tmp.npz')
    np.savez_compressed(tmp, meta=json.dumps(meta), **{k:state[k] for k in (*FIELDS,'sx','sy')})
    tmp.replace(path)


def main():
    import argparse
    from .exploration import load_seed, physical_throat
    from .solver.device import select_device
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("seed")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--method", choices=("screen", "refine"), default="screen")
    ap.add_argument("--gpu", type=int)
    args = ap.parse_args()
    select_device(args.gpu, 512)
    state, metadata = load_seed(args.seed)
    config = {k: metadata[k] for k in ("m", "q", "gamma", "J")}
    th = physical_throat(state)
    pin = (("area", th["area_throat"]) if metadata.get("pin") == "area"
           else ("R_e", th["R_e"]))
    result, checked = check_candidate(
        state, config, refinement_grids(len(state["sx"])-1, len(state["sy"])-1),
        pin, (state["psim"]*state["sigma"]/np.pi)**2, args.out,
        method=args.method, score_key="X_A" if pin[0]=="area" else "X")
    if result["passed"]:
        save_checked(args.out/("validated.npz" if args.method=="refine" else "screened.npz"),
                     checked, config, metadata, result)
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
