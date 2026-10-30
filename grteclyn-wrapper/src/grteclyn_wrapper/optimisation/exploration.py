"""Matched stationary experiments starting from a saved optimisation solution.

No stability classification or evolution export is made here. Search-grid
results remain provisional; a separate fine solve must reproduce the gain.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import MAPS, cheb_eval, lobatto, tail_ratio
from .exoticity import exotic_x, throat
from .potentials import BernsteinKinkPotential, PolynomialPotential

FIELDS = ("F", "W", "N", "B", "PSI")


def load_seed(path):
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        state = {k: np.array(z[k]) for k in (*FIELDS, "sx", "sy")}
    state.update({k: float(meta[k]) for k in ("sigma", "xi_t", "omega", "psim")})
    state["gamma"] = float(meta["gamma"])
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
    for key in ("R_e", "R_A", "R_pol", "eta_throat"):
        th[key] *= state["sigma"]
    th["area_throat"] *= state["sigma"]**2
    return th


def make_problem(state, config, nx, ny, pin, *, frequency=None, amplitude=None):
    from .matter_equations import MatterCollocationProblem
    m, q = config["m"], tuple(config["q"])
    controls = config.get("controls")
    potential = (lambda pm: PolynomialPotential.kink_q(m, pm, q)) if controls is None else (
        lambda pm: BernsteinKinkPotential(m, pm, tuple(controls)))
    extra = {}
    kind = config.get("matter")
    if kind:
        mass = config["matter_mass"]
        pot = PolynomialPotential((0., 0., mass**2, 0., config.get("quartic", 0.)))
        if kind == "cloud":
            extra = dict(chi=(pot, frequency), pin_chi=amplitude)
        elif kind == "winding":
            extra = dict(winding=(pot, frequency, config.get("winding_k", 1)),
                         pin_zeta=amplitude)
        else:
            raise ValueError(kind)
    return MatterCollocationProblem(
        eta0=1.0, gamma=config["gamma"], radial_map=state["map"], nx=nx, ny=ny,
        prescribe=("J", config["J"]), pin=pin, potential=potential, **extra)


def pack_seed(p, state, cloud=None, frequency=None):
    F, W, N, B, psi = (interpolate(state, p.sx, p.sy, k) for k in FIELDS)
    # Continue the asymptotic redshift itself, not a mismatched boundary row.
    F += 0.5*(p.gamma-state["gamma"])*(1-p.sx)[:, None]
    kw = {}
    if p.chi is not None:
        kw.update(dchi=cloud, omega_chi=frequency)
    if p.winding is not None:
        kw.update(dzeta=cloud, omega_z=frequency)
    return p.pack(F-p.f_bg, W-state["omega"]*p.q, N, B-1,
                  psi-state["psim"]*p.psi_prof, omega_inf=state["omega"],
                  psi_minus=state["psim"], sigma=state["sigma"],
                  xi_t=state["xi_t"], **kw)


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
                max_iter=14, stall_ok=1e-9):
    from .solver.newton import newton
    kind = config.get("matter")
    frequency = cloud = None
    if kind:
        if mode is None:
            raise ValueError("matter trial needs a bound-mode seed")
        frequency = mode["frequency"]
        cloud = config["amplitude"] * interpolate(mode, lobatto(nx)[0], lobatto(ny)[0], "cloud")
    p = make_problem(state, config, nx, ny, pin, frequency=frequency,
                     amplitude=config.get("amplitude") if kind else None)
    u, info = newton(p.residual, p.jacobian, pack_seed(p, state, cloud, frequency),
                     tol=1e-14, max_iter=max_iter)
    residual = float(info["res_scaled_inf"])
    if not np.isfinite(residual) or residual > stall_ok:
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
    jtot = diag["j_of_x"] + diag.get("j_matter_tail", 0.)
    jerr = float(np.max(np.abs(sigma**2*jtot[mask]-config["J"]))) / max(1., abs(config["J"]))
    x = exotic_x(1., p.map, p.sx, p.sy, p.Dx, F, N, B, psi)
    th = p.throat(u)
    held = th["R_e"] if pin[0] == "R_e" else th["area"]
    global_held = sigma*x["R_e"] if pin[0] == "R_e" else sigma**2*x["area_throat"]
    pin_error = max(abs(held/pin[1]-1), abs(global_held/pin[1]-1))
    tail = max(tail_ratio(v, axis=ax) for v in (psi-psim*p.psi_prof, B-1, *fields[5:]) for ax in (0, 1))
    interval_ok = float(np.min(psi/psim)) >= -1e-8 and float(np.max(psi/psim)) <= 1+1e-8
    row = dict(nx=nx, ny=ny, newton=residual, iters=int(info["iters"]),
               X=x["X"], X_A=x["X_A"], VIQ=sigma*x["VIQ"],
               R_e=sigma*x["R_e"], R_A=sigma*x["R_A"], R_pol=sigma*x["R_pol"],
               sigma=sigma, E19=e19, E_c=ec, J_error=jerr, pin_error=pin_error,
               tails=float(tail), lapse_min=float(np.exp(F.min()/2)),
               stability="not_assessed", scalar_in_vacuum_interval=interval_ok)
    if kind:
        frequency = p.omega_chi_of(u) if kind == "cloud" else p.omega_z_of(u)
        k = config.get("winding_k", 1) if kind == "winding" else 0
        bound = (0 < frequency < config["matter_mass"] and
                 abs(frequency+k*omega/sigma)<config["matter_mass"]*np.exp(config["gamma"]/2))
        amp = fields[5][p.mid, -1]
        row.update(frequency=frequency, cloud_peak=float(np.max(np.abs(fields[5]))),
                   amplitude_error=float(abs(amp/config["amplitude"]-1)), bound=bool(bound))
        if kind == "winding":
            row["J_matter"] = float(sigma**2*diag["j_matter_tail"][p.mid-1])
    acceptable = (max(e19, ec) <= 1e-8 and jerr <= 1e-6 and pin_error <= 1e-8
                  and interval_ok and row.get("bound", True)
                  and row.get("amplitude_error", 0) <= 1e-6)
    row["verdict"] = "PASS" if acceptable else "ABOVE_GATE"
    result = {k:v for k,v in zip(FIELDS, fields[:5])}
    result.update(sx=p.sx, sy=p.sy, sigma=sigma, xi_t=xi_t, omega=omega, psim=psim,
                  gamma=config["gamma"], map=p.map)
    if kind:
        result.update(cloud=fields[5]/config["amplitude"], frequency=frequency)
    return result, row


def save_trial(path, state, config, row, pin):
    import dataclasses
    meta = dict(config=config, diagnostics=row, pin=list(pin),
                radial_map=dataclasses.asdict(state["map"]),
                **{k:state[k] for k in ("sigma", "xi_t", "omega", "psim", "gamma")})
    arrays = {k:state[k] for k in (*FIELDS, "sx", "sy")}
    if "cloud" in state:
        arrays["cloud"] = state["cloud"]*config["amplitude"]
    np.savez_compressed(Path(path), meta=json.dumps(meta, allow_nan=False), **arrays)
