"""Matched stationary experiments starting from a saved optimisation solution.

No stability classification or evolution export is made here. Search-grid
results remain provisional; a separate fine solve must reproduce the gain.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from grteclyn_stationary.numerics.spectral import MAPS
from grteclyn_stationary.numerics.spectral import cheb_eval
from grteclyn_stationary.numerics.spectral import lobatto
from grteclyn_stationary.numerics.spectral import tail_ratio
from grteclyn_stationary.geometry.exoticity import exotic_x, throat
from grteclyn_stationary.matter.potentials import BernsteinKinkPotential, PolynomialPotential

FIELDS = ("F", "W", "N", "B", "PSI")
EXTRA_FIELDS = ("CHI", "Z", "surface_coefficients")


def load_seed(path):
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        state = {k: np.array(z[k]) for k in (*FIELDS, "sx", "sy")}
        state.update({k:np.array(z[k]) for k in EXTRA_FIELDS if k in z})
        cfg = meta.get('config', meta)
        if 'cloud' in z and not any(k in state for k in ('CHI','Z')):
            kind = cfg.get('matter')
            if kind not in ('cloud','winding'):
                raise ValueError('cloud archive has no matter type')
            state['CHI' if kind=='cloud' else 'Z'] = np.array(z['cloud'])
    state.update({k: float(meta[k]) for k in ("sigma", "xi_t", "omega", "psim")})
    state["gamma"] = float(meta["gamma"])
    frequency = meta.get('frequency',meta.get('diagnostics',{}).get('frequency'))
    if frequency is not None:
        state['frequency'] = float(frequency)
    if any(k in state for k in ('CHI','Z')) and frequency is None:
        raise ValueError('matter archive has no harmonic frequency')
    params = dict(meta["radial_map"])
    name = params.pop("name")
    params.pop("class", None)
    params.pop("eta0", None)
    state["map"] = MAPS[name](eta0=1.0, **params)
    return state, meta


def interpolate(state, sx, sy, key):
    rows = cheb_eval(state["sx"], state[key], sx)
    return cheb_eval(state["sy"], rows.T, sy).T


def physical_throat(state):
    _, dx = lobatto(len(state["sx"])-1)
    th = throat(1.0, state["map"], state["sx"], state["sy"], dx,
                state["F"], state["N"], state["B"])
    if 'surface_coefficients' in state:
        from grteclyn_stationary.geometry.surfaces import surface_geometry
        th = surface_geometry(1.,state['map'],state['sx'],state['sy'],
                              state['F'],state['N'],state['B'],state['surface_coefficients'])
    for key in ("R_e", "R_A", "R_pol", "eta_throat"):
        th[key] *= state["sigma"]
    th["area_throat"] *= state["sigma"]**2
    return th


def make_problem(state, config, nx, ny, pin, *, frequency=None, amplitude=None):
    from grteclyn_stationary.matter.equations import MatterCollocationProblem
    m, q = config["m"], tuple(config["q"])
    controls = config.get("controls")
    potential = (lambda pm: PolynomialPotential.kink_q(m, pm, q)) if controls is None else (
        lambda pm: BernsteinKinkPotential(m, pm, tuple(controls)))
    extra = {}
    kind = config.get("matter")
    if kind:
        if frequency is None:
            frequency = state.get('frequency', .8*config['matter_mass'])
        mass = config["matter_mass"]
        pot = PolynomialPotential((0., 0., mass**2, 0., config.get("quartic", 0.)))
        if kind == "cloud":
            extra = dict(chi=(pot, frequency), pin_chi=amplitude)
        elif kind == "winding":
            extra = dict(winding=(pot, frequency, config.get("winding_k", 1)),
                         pin_zeta=amplitude,
                         zeta_anchor_xi=config.get('zeta_anchor_xi', 0.) if amplitude is not None else 0.)
        else:
            raise ValueError(kind)
    rotation = config.get('rotation_control', 'J')
    if rotation not in ('J', 'J_xi0', 'nonrotating_ends'):
        raise ValueError('unknown rotation_control')
    prescribed = (('J_xi0', config['J_xi0']) if rotation == 'J_xi0' else
                  ('J', config['J']) if rotation == 'J' else ('omega_inf', 0.))
    return MatterCollocationProblem(
        eta0=1.0, gamma=config["gamma"], radial_map=state["map"], nx=nx, ny=ny,
        prescribe=prescribed,
        pin=pin, potential=potential, **extra)


def angular_momentum_diagnostics(p, diag, sigma, config):
    """Check total-flux conservation separately from the chosen rotation pin."""
    profile = sigma**2*(diag['j_of_x']+diag.get('j_matter_tail', 0.))
    measured = float(profile[p.mid-1])
    rotation = config.get('rotation_control', 'J')
    target = config['J'] if rotation == 'J' else measured
    mask = diag['C2_i'] >= .05**2
    error = float(np.max(abs(profile[mask]-target)))/max(1., abs(target))
    geometric = float(sigma**2*diag['j_of_x'][p.mid-1])
    flux_error = (abs(geometric-config['J_xi0'])/max(1., abs(config['J_xi0']))
                  if rotation == 'J_xi0' else 0.)
    return dict(J_measured=measured, J_error=max(error, flux_error),
                J_conservation_error=error, J_flux_error=flux_error,
                J_geometric_flux_xi0=geometric)


def matter_anchor(values, sx, config):
    """Evaluate the same amplitude border during seeding and diagnostics."""
    xi = config.get('zeta_anchor_xi', 0.) if config.get('matter') == 'winding' else 0.
    if xi == 0.:
        return float(values[len(sx)//2, -1])
    return float(cheb_eval(sx, values[:, -1], [xi])[0])


def pack_seed(p, state, cloud=None, frequency=None):
    F, W, N, B, psi = (interpolate(state, p.sx, p.sy, k) for k in FIELDS)
    # Continue the asymptotic redshift itself, not a mismatched boundary row.
    F += 0.5*(p.gamma-state["gamma"])*(1-p.sx)[:, None]
    kw = {}
    if p.chi is not None:
        kw.update(dchi=cloud if cloud is not None else interpolate(state,p.sx,p.sy,'CHI'),
                  omega_chi=frequency if frequency is not None else state.get('frequency'))
    if p.winding is not None:
        kw.update(dzeta=cloud if cloud is not None else interpolate(state,p.sx,p.sy,'Z'),
                  omega_z=frequency if frequency is not None else state.get('frequency'))
    return p.pack(F-p.f_bg, W-state["omega"]*p.q, N, B-1,
                  psi-state["psim"]*p.psi_prof, omega_inf=state["omega"],
                  psi_minus=state["psim"], sigma=state["sigma"],
                  xi_t=state["xi_t"], surface_coefficients=state.get('surface_coefficients'), **kw)


def bound_mode(state, config, pin, nx=40, ny=10):
    """Seed a nonzero cloud from its linear equation on the frozen metric.

    Only the cloud block is differentiated; no full dense Einstein Jacobian
    is built. Dirichlet endpoints are eliminated before the eigensolve.
    Both asymptotic mass gaps must be open in their own time/azimuth frame.
    """
    import scipy.linalg as sla
    import jax
    import jax.numpy as jnp
    n = (nx+1)*(ny+1)
    indices = np.arange(n).reshape(nx+1, ny+1)[1:-1].ravel()
    matrices = []
    sigma = state["sigma"]
    for grid_frequency in (0., 1., -1.):
        p = make_problem(state, config, nx, ny, pin,
                         frequency=grid_frequency/sigma)
        u = jnp.asarray(pack_seed(p, state, np.zeros((nx+1, ny+1))))
        block = slice(5*n, 6*n)
        def residual_cloud(v):
            return p._residual(u.at[block].set(v), p.value)[block]
        matrix = np.asarray(jax.jit(jax.jacfwd(residual_cloud))(jnp.zeros(n)))
        matrices.append(matrix[np.ix_(indices, indices)])
    L0, plus, minus = matrices
    L1, L2 = (plus-minus)/2, (plus+minus)/2-L0
    count = len(indices)
    eye, zero = np.eye(count), np.zeros((count, count))
    vals, vecs = sla.eig(np.block([[-L1, -L0], [eye, zero]]),
                         np.block([[L2, zero], [zero, eye]]))
    mass = config["matter_mass"]
    k = config.get("winding_k", 1) if config["matter"] == "winding" else 0
    options = []
    for i in np.where(np.isfinite(vals) & (np.abs(vals.imag)<1e-8))[0]:
        w = float(vals[i].real)/sigma
        if not (0 < w < mass and abs(w+k*state["omega"]/sigma)
                < mass*np.exp(config["gamma"]/2)):
            continue
        v = vecs[count:, i].real
        op = L0 + vals[i].real*L1 + vals[i].real**2*L2
        error = np.linalg.norm(op@v)/(np.linalg.norm(op)*np.linalg.norm(v)+1e-300)
        mode = np.zeros(n)
        mode[indices] = v
        mode = mode.reshape(nx+1, ny+1)
        peak = np.max(np.abs(mode))
        loc = np.max(np.abs(mode[np.abs(p.sx)>.99]))/max(peak, 1e-300)
        anchor = mode[nx//2, -1]
        if error < 1e-9 and loc < .05 and abs(anchor) > .05*peak:
            options.append((w, mode/anchor, error, loc))
    if not options:
        raise RuntimeError("no localized bound mode in BOTH asymptotic mass gaps")
    w, mode, error, loc = min(options, key=lambda v: v[0])
    return dict(frequency=w, cloud=mode, sx=p.sx, sy=p.sy,
                mode_residual=error, mode_tail=loc)


def solve_trial(state, config, nx, ny, pin, d2, *, mode=None,
                max_iter=14, stall_ok=1e-9, newton_tol=1e-14, min_updates=0,
                chord_ratio=.1, min_damping=1/64, verbose=False, failure_path=None):
    if not 0 < newton_tol <= stall_ok:
        raise ValueError("Newton stopping tolerance must not exceed acceptance tolerance")
    from grteclyn_stationary.numerics.newton import newton
    kind = config.get("matter")
    frequency = cloud = None
    if kind:
        if mode is not None:
            frequency = mode["frequency"]
            cloud = config["amplitude"] * interpolate(mode, lobatto(nx)[0], lobatto(ny)[0], "cloud")
        else:
            key = 'CHI' if kind=='cloud' else 'Z'
            if key not in state:
                raise ValueError("matter trial needs a mode or finite-amplitude seed")
            frequency = state['frequency']
            cloud = interpolate(state,lobatto(nx)[0],lobatto(ny)[0],key)
            anchor = matter_anchor(cloud, lobatto(nx)[0], config)
            if abs(anchor)<1e-15:
                raise ValueError('zero matter anchor')
            cloud = cloud*(config['amplitude']/anchor)
    p = make_problem(state, config, nx, ny, pin, frequency=frequency,
                     amplitude=config.get("amplitude") if kind else None)
    u, info = newton(p.residual, p.jacobian, pack_seed(p, state, cloud, frequency),
                     tol=newton_tol, max_iter=max_iter, min_updates=min_updates,
                     chord_ratio=chord_ratio, min_damping=min_damping, verbose=verbose)
    residual = float(info["res_scaled_inf"])
    if not np.isfinite(residual) or residual > stall_ok or len(info['newton_steps'])<min_updates:
        if failure_path is not None:
            # Preserve the unaccepted iterate and Newton history for diagnosis.
            path = Path(failure_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(path, u=u, sx=p.sx, sy=p.sy,
                metadata=json.dumps(dict(accepted=False, config=config, pin=list(pin),
                    nx=nx, ny=ny, newton=info), default=float))
        raise RuntimeError(f"Newton residual {residual:.3e}: {info.get('reason', 'iteration cap')}")
    fields = [np.asarray(v) for v in p.fields(u)]
    if not all(np.isfinite(v).all() for v in fields):
        raise RuntimeError("nonfinite fields")
    F, W, N, B, psi = fields[:5]
    omega, psim = p.unpack(u)[-2:]
    sigma, xi_t = p.scale(u)
    if sigma <= 0 or np.min(B) <= 0:
        raise RuntimeError("nonpositive scale or B")
    diag = p.diagnostics(u)
    mask = diag["C2_i"] >= .05**2
    e19 = float(np.max(np.abs(diag["E19"][mask])))/d2
    ec = float(np.max(np.abs(diag["E_c"][mask])))
    angular = angular_momentum_diagnostics(p, diag, sigma, config)
    measured_j, jerr = angular['J_measured'], angular['J_error']
    x = exotic_x(1., p.map, p.sx, p.sy, p.Dx, F, N, B, psi)
    th = p.throat(u)
    held = th["R_e"] if pin[0] == "R_e" else th["area"]
    global_held = sigma*x["R_e"] if pin[0] == "R_e" else sigma**2*x["area_throat"]
    if pin[0] == 'minimal_area':
        from grteclyn_stationary.geometry.surfaces import surface_geometry
        geometry = surface_geometry(1.,p.map,p.sx,p.sy,F,N,B,p.surface_coefficients(u))
        global_held = sigma**2*geometry['area_throat']
    pin_error = max(abs(held/pin[1]-1), abs(global_held/pin[1]-1))
    tail = max(tail_ratio(v, axis=ax) for v in (psi-psim*p.psi_prof, B-1, *fields[5:]) for ax in (0, 1))
    interval_ok = float(np.min(psi/psim)) >= -1e-8 and float(np.max(psi/psim)) <= 1+1e-8
    row = dict(nx=nx, ny=ny, newton=residual, iters=int(info["iters"]),
               newton_updates=len(info['newton_steps']),
               newton_converged=bool(info['converged']),
               newton_reason=info.get('reason', 'converged'),
               newton_history=info['res_history'],
               newton_steps=info['newton_steps'],
               jacobian_evals=info['jacobian_evals'],
               X=x["X"], X_A=x["X_A"], VIQ=sigma*x["VIQ"],
               R_e=sigma*x["R_e"], R_A=sigma*x["R_A"], R_pol=sigma*x["R_pol"],
               sigma=sigma, E19=e19, E_c=ec, J_error=jerr, J_measured=measured_j, pin_error=pin_error,
               tails=float(tail), lapse_min=float(np.exp(F.min()/2)),
               stability="not_assessed", scalar_in_vacuum_interval=interval_ok)
    row.update(angular)
    if kind:
        frequency = p.omega_chi_of(u) if kind == "cloud" else p.omega_z_of(u)
        k = config.get("winding_k", 1) if kind == "winding" else 0
        bound = (0 < frequency < config["matter_mass"] and
                 abs(frequency+k*omega/sigma)<config["matter_mass"]*np.exp(config["gamma"]/2))
        amp = matter_anchor(fields[5], p.sx, config)
        row.update(frequency=frequency, cloud_peak=float(np.max(np.abs(fields[5]))),
                   amplitude_error=float(abs(amp/config["amplitude"]-1)), bound=bool(bound))
        if kind == "winding":
            row["J_matter_positive_half"] = float(sigma**2*diag["j_matter_tail"][p.mid-1])
    acceptable = (max(e19, ec) <= 1e-8 and jerr <= 1e-6 and pin_error <= 1e-8
                  and interval_ok and row.get("bound", True)
                  and row.get("amplitude_error", 0) <= 1e-6)
    row["verdict"] = "PASS" if acceptable else "ABOVE_GATE"
    result = {k:v for k,v in zip(FIELDS, fields[:5])}
    result.update(sx=p.sx, sy=p.sy, sigma=sigma, xi_t=xi_t, omega=omega, psim=psim,
                  gamma=config["gamma"], map=p.map)
    if kind:
        result.update(cloud=fields[5]/config["amplitude"], frequency=frequency)
        result['CHI' if kind=='cloud' else 'Z'] = fields[5]
    if p.surface_order:
        result['surface_coefficients'] = np.asarray(p.surface_coefficients(u))
        row.update(R_A=sigma*geometry['R_A'], R_e=sigma*geometry['R_e'],
                   R_pol=sigma*geometry['R_pol'])
    return result, row


def save_trial(path, state, config, row, pin):
    import dataclasses
    meta = dict(config=config, diagnostics=row, pin=list(pin),
                schema_version=2,
                radial_map=dataclasses.asdict(state["map"]),
                **{k:state[k] for k in ("sigma", "xi_t", "omega", "psim", "gamma")})
    arrays = {k:state[k] for k in (*FIELDS, "sx", "sy")}
    arrays.update({k:state[k] for k in EXTRA_FIELDS if k in state})
    if 'frequency' in state:
        meta['frequency'] = state['frequency']
    path=Path(path)
    tmp=path.with_suffix('.tmp.npz')
    np.savez_compressed(tmp, meta=json.dumps(meta, allow_nan=False), **arrays)
    tmp.replace(path)
