"""Extractors for the 'waves' area: research.tex Sec. "Gravitational waves" and its
subsections (collapsing throat, head-on ringdown, spiral burst, fly-by burst,
vacuum twin, scalar channel and its sign, horizon censorship), plus the places
where the abstract, captions, Discussion, Limitations and the detector section
re-quote those numbers.

SAME CODE AS THE FIGURES.  Every number is recomputed through the module that
draws the figure it belongs to, so the ledger cannot drift from the page:

  plot_psi4_gallery.ARMS     the scenario table (stream, mode, innermost sphere,
                             gate) that both wave figures share -- peaks,
                             wavefront speeds, the correlated front;
  plot_psi4_ligo.prepare     energies (band integrals over a common retarded
                             window, +-m doubled) and their sphere spread, the
                             envelope, strain slope and frequency track;
  plot_scalar_channel        |E_phi| / E_GW, the wave-zone mode sum, multipoles;
  plot_scalar_censorship     the running-max envelope, its fits, post-horizon E_phi;
  plot_seed_linearity        the rms amplitudes of the quadrupole-seed arms;
  plot_fill_insensitivity    the fill-window twin;
  analysis/queue2e_gates.py  (in the pack) the five gates of the lone throat's wave.

The grteclyn_wrapper modules are imported INSIDE the extractors, so claims.py
still loads with a numpy-only Python for the other areas.

Runs are resolved by NAME in the tracked pack (lib.run_dir), with a fallback
directory search under results/merger/campaign for the few packed directories
that carry no run marker (the glued v2_spiral_d12_p012_L128_SERIES).  Nothing
here reads runs/.

SCALAR SIGN.  scalar_modes.dat stores the canonical flux_kin = -R^2 oint Pi d_r phi
(outgoing canonical wave > 0).  Gravity couples to minus that stress tensor, so
the physical energy flux is -flux_kin; every signed E_phi returned here carries
the PHYSICAL sign (plot_scalar_channel's docstring, FIGURES.md).
"""

from __future__ import annotations

import functools
import importlib
import math
import pathlib
import re

import numpy as np

from lib import PACK, extractor, params, run_dir

WM = "grteclyn_wrapper.visualisation.wormhole_merger"


# ---------------------------------------------------------------- plumbing
def _mod(name: str):
    """A wormhole_merger figure module, imported on first use."""
    return importlib.import_module(f"{WM}.{name}")


def _q2e():
    """The pack's own analysis/queue2e_gates.py (lib put analysis/ on sys.path)."""
    return importlib.import_module("queue2e_gates")


@functools.lru_cache(maxsize=None)
def _run_path(run: str) -> pathlib.Path:
    try:
        return run_dir(run)
    except LookupError:
        hits = sorted(d for d in (PACK / "campaign").glob(f"**/{run}") if d.is_dir())
        if not hits:
            raise
        return hits[0]


@functools.lru_cache(maxsize=None)
def _arms() -> dict:
    """plot_psi4_gallery.ARMS keyed by scenario name, the run given by NAME."""
    out = {}
    for name, _knob, mode, rel, m, R0, t_max, _note in _mod("plot_psi4_gallery").ARMS:
        p = pathlib.PurePosixPath(rel)
        out[name] = dict(run=p.parent.name, file=p.name, m=m, R0=R0, t_max=t_max, mode=mode)
    return out


def _arm(scenario: str) -> dict:
    arms = _arms()
    if scenario not in arms:
        raise KeyError(f"no scenario {scenario!r} in plot_psi4_gallery.ARMS; have {sorted(arms)}")
    return arms[scenario]


@functools.lru_cache(maxsize=None)
def _series(scenario: str, gated: bool = True):
    """(t, {R: complex r Psi4}, radii, R_in) exactly as the gallery reads it."""
    a = _arm(scenario)
    streams = _mod("streams")
    path = _run_path(a["run"]) / a["file"]
    if a["m"] is None:
        t, ser = streams.load_mode(path)
        ser = dict(ser)
    else:
        t, d = streams.load_l2_all(path)
        ser = {r: d[(mm, r)] for (mm, r) in d if mm == a["m"]}
    if gated and a["t_max"] is not None:
        keep = t <= a["t_max"] + 1e-9
        t, ser = t[keep], {r: y[keep] for r, y in ser.items()}
    radii = sorted(ser)
    R_in = min(radii, key=lambda r: abs(r - a["R0"]))
    return t, ser, radii, R_in


@functools.lru_cache(maxsize=None)
def _ligo_arms() -> dict:
    """plot_psi4_ligo.prepare(pack), keyed by scenario name (the figure's own numbers)."""
    return {a["name"]: a for a in _mod("plot_psi4_ligo").prepare(PACK)}


def _ligo_arm(scenario: str) -> dict:
    arms = _ligo_arms()
    if scenario not in arms:
        raise KeyError(f"no scenario {scenario!r} in plot_psi4_ligo.prepare(); have {sorted(arms)}")
    return arms[scenario]


def _band_peak(y: np.ndarray, dt: float) -> float:
    """f_pk of the smoothed burst PSD, bins 1.. (plot_psi4_ligo's convention)."""
    pm, L = _mod("psi4_math"), _mod("plot_psi4_ligo")
    f, S = pm._burst_psd(y, 1.0 / dt)
    return float(f[1:][np.argmax(pm._smooth_psd(S, L._smooth_window(S.size), 5)[1:])])


def _pick(values: list[float], stat) -> float:
    if isinstance(stat, int):
        return float(values[stat])
    return float({"min": min, "max": max, "mean": np.mean}[stat](values))


# ---------------------------------------------------------------- Psi4: peaks, speeds
@extractor
def waves_peak(scenario: str, sphere: float | None = None) -> float:
    """Peak |r Psi4| of the dominant mode (gallery gate) at the innermost sphere,
    or at sphere R."""
    t, ser, radii, R_in = _series(scenario)
    return float(np.abs(ser[R_in if sphere is None else float(sphere)]).max())


@extractor
def waves_peak_fall(scenario: str) -> float:
    """100 (1 - peak_outer/peak_inner), %, each sphere read over the SAME retarded
    window (the gallery gate applied in retarded time, as plot_psi4_ligo does for
    the energies): a coordinate-time gate would truncate the outer spheres' burst."""
    G = _mod("plot_psi4_gallery")
    t, ser, radii, R_in = _series(scenario, gated=False)
    a = _arm(scenario)
    u_max = (a["t_max"] - R_in) if a["t_max"] is not None else math.inf
    pk = {}
    for R in radii:
        keep = (t - R) <= u_max + 1e-9
        _, y = G.trim_zeros_tail(t[keep], ser[R][keep])
        pk[R] = float(np.abs(y).max())
    return 100.0 * (1.0 - pk[radii[-1]] / pk[R_in])


@extractor
def waves_speed(scenario: str, pair="min") -> float:
    """Wavefront speed v/c between neighbouring spheres from the lag of the whole
    complex waveform (psi4_math.wavefront_speeds_xcorr, the gallery's numbers):
    pair = index of the sphere pair (0 = innermost) or min / max over pairs."""
    t, ser, radii, _ = _series(scenario)
    sp = _mod("psi4_math").wavefront_speeds_xcorr(t, ser, radii)
    return _pick([v for _, _, v, _ in sp], pair)


@extractor
def waves_peak_speed(scenario: str) -> float:
    """v/c from PEAK timing, innermost to outermost sphere (the estimator the
    gallery caption says fails on flat-topped envelopes)."""
    t, ser, radii, R_in = _series(scenario)
    R_out = radii[-1]
    t_in = t[int(np.argmax(np.abs(ser[R_in])))]
    t_out = t[int(np.argmax(np.abs(ser[R_out])))]
    return float((R_out - R_in) / (t_out - t_in))


@extractor
def waves_front_u(scenario: str, sphere: int = -1) -> float:
    """Retarded time t - R of the correlated wavefront at a sphere (index), as the
    gallery's gold dots place it: the innermost envelope's tallest interior crest,
    advanced sphere to sphere by the correlation lags."""
    from scipy.signal import find_peaks
    G = _mod("plot_psi4_gallery")
    t, ser, radii, R_in = _series(scenario)
    tt, yy = G.trim_zeros_tail(t, ser[R_in])
    env = np.abs(yy)
    crests, _ = find_peaks(env)
    i = crests[np.argmax(env[crests])] if crests.size else int(np.argmax(env))
    u = float(tt[i] - R_in)
    lags = [r for _, _, _, r in _mod("psi4_math").wavefront_speeds_xcorr(t, ser, radii)]
    k = sphere % len(radii)
    return u + float(sum(lags[:k]))


@extractor
def waves_peak_time(run: str, file: str, R: float, t_min: float | None = None,
                    t_max: float | None = None, retarded: bool = False) -> float:
    """Time (or retarded time t - R) of max |r Psi4| at sphere R over [t_min, t_max]."""
    t, ser = _mod("streams").load_mode(_run_path(run) / file)
    y = np.abs(ser[float(R)])
    keep = np.ones(t.size, bool)
    if t_min is not None:
        keep &= t >= t_min
    if t_max is not None:
        keep &= t <= t_max + 1e-9
    tp = float(t[keep][int(np.argmax(y[keep]))])
    return tp - float(R) if retarded else tp


@extractor
def waves_trough_time(run: str, file: str, R: float, t_min: float, t_max: float) -> float:
    """Time of MIN |r Psi4| at sphere R over (t_min, t_max) -- where a decaying
    burst meets a growing contaminant and |r Psi4| turns back up."""
    t, ser = _mod("streams").load_mode(_run_path(run) / file)
    y = np.abs(ser[float(R)])
    keep = (t > t_min) & (t < t_max)
    return float(t[keep][int(np.argmin(y[keep]))])


@extractor
def waves_swing(run: str, file: str, R: float, t_min: float, t_max: float,
                sign: int = 1, what: str = "time") -> float:
    """One swing of Re(r Psi4) at sphere R: the extreme sample (max for sign = +1,
    min for -1) inside [t_min, t_max]; what = 'time' or 'value'."""
    t, ser = _mod("streams").load_mode(_run_path(run) / file)
    y = np.real(ser[float(R)])
    idx = np.nonzero((t >= t_min) & (t <= t_max))[0]
    i = idx[int(np.argmax(sign * y[idx]))]
    return float(t[i] if what == "time" else y[i])


@extractor
def waves_arms_gate(scenario: str) -> float:
    """The gallery/LIGO gate t_max of a scenario (plot_psi4_gallery.ARMS)."""
    g = _arm(scenario)["t_max"]
    if g is None:
        raise ValueError(f"scenario {scenario!r} is not gated")
    return float(g)


@extractor
def waves_figure_const(module: str, name: str, index: int | None = None) -> float:
    """A module-level constant of a wave figure script (its declared set-up)."""
    v = getattr(_mod(module), name)
    return float(v if index is None else v[index])


@extractor
def waves_stream_radius(run: str, file: str, index: int) -> float:
    """The index-th extraction sphere named in a packed stream's header
    (Re(R=10) / Re_m-2(R=14) / R30_phi_... / '# r = 20 20 28 28 ...')."""
    radii: list[float] = []
    with (_run_path(run) / file).open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            found = (re.findall(r"\(R=?([\d.]+)\)", line)
                     or re.findall(r"(?:^|\s)R([\d.]+)_", line))
            if not found and re.search(r"\br\s*=", line):
                found = re.findall(r"[\d.]+(?:[eE][+-]?\d+)?", line.split("=", 1)[1])
            for x in found:
                if float(x) not in radii:
                    radii.append(float(x))
    if not radii:
        raise ValueError(f"{run}/{file}: no sphere radii in the header")
    return radii[index]


# ---------------------------------------------------------------- Psi4: energy, detector track
@extractor
def waves_energy(scenario: str, which: str = "E") -> float:
    """E_rad/M in the dominant multipole (plot_psi4_ligo.prepare): 'E' at the
    innermost sphere, 'lo'/'hi' over the spheres (common retarded window),
    'spread' = 100 (hi - lo)/E in %."""
    a = _ligo_arm(scenario)
    if which == "spread":
        return 100.0 * (a["E_hi"] - a["E_lo"]) / a["E"]
    return float({"E": a["E"], "lo": a["E_lo"], "hi": a["E_hi"]}[which])


@extractor
def waves_energy_run(run: str, file: str, R: float, m: int, M: float,
                     t_max: float | None = None) -> float:
    """E_rad/M of one (l=2, m) mode on one sphere of any packed stream, with the
    LIGO figure's band integral (psi4_math._compute_radiated_energy cut against the
    smoothed band peak; m != 0 doubled for +-m)."""
    streams, pm = _mod("streams"), _mod("psi4_math")
    path = _run_path(run) / file
    if file.startswith("psi4_mode_l2_all"):
        t, d = streams.load_l2_all(path)
        y = d[(int(m), float(R))]
    else:
        t, ser = streams.load_mode(path)
        y = ser[float(R)]
    if t_max is not None:
        keep = t <= t_max + 1e-9
        t, y = t[keep], y[keep]
    u, w = (t - float(R)) / M, y * M
    f_pk = _band_peak(w, float((u[-1] - u[0]) / (u.size - 1)))
    return float(pm._compute_radiated_energy(u, w, m=int(m), f_peak=f_pk))


@extractor
def waves_ligo_env_peak(scenario: str) -> float:
    """Peak of the analytic-signal envelope |r Psi4| M (panel a of psi4_ligo)."""
    L = _mod("plot_psi4_ligo")
    a = _ligo_arm(scenario)
    env, _ = L.envelope_and_frequency(a["y"], a["dt"], _band_peak(a["y"], a["dt"]))
    return float(env.max())


@extractor
def waves_ligo_slope(scenario: str) -> float:
    """Logarithmic slope of the strain ASD from the record's corner to 5 kHz at
    30 Msun / 10 Mpc (panel b of psi4_ligo)."""
    L, pm = _mod("plot_psi4_ligo"), _mod("psi4_math")
    a = _ligo_arm(scenario)
    to_hz = 1.0 / (L.MASS_MSUN * pm.M_SUN_SEC)
    f, S = pm._burst_psd(a["y"], 1.0 / a["dt"])
    S = pm._smooth_psd(S, L._smooth_window(S.size), 5)
    f_hz, Sh = pm._scale_to_physical(f, pm._psd_psi4_to_strain(f, S), L.MASS_MSUN, L.DIST_MPC)
    f_corner = to_hz / float(a["u"][-1] - a["u"][0])
    band = (f_hz >= f_corner) & (f_hz <= 5000.0) & np.isfinite(Sh) & (Sh > 0)
    return float(np.polyfit(np.log(f_hz[band]), np.log(np.sqrt(Sh[band])), 1)[0])


@extractor
def waves_ligo_track(scenario: str, which: str) -> float:
    """The energy-weighted instantaneous frequency of panel c of psi4_ligo:
    'min'/'max' in Hz over the drawn body, or 'fM_peak' = f M at the envelope peak."""
    L, pm = _mod("plot_psi4_ligo"), _mod("psi4_math")
    a = _ligo_arm(scenario)
    to_hz = 1.0 / (L.MASS_MSUN * pm.M_SUN_SEC)
    f_pk = _band_peak(a["y"], a["dt"])
    env, fM = L.envelope_and_frequency(a["y"], a["dt"], f_pk)
    if which == "fM_peak":
        return float(fM[int(np.argmax(env))])
    keep = L.body(env, L.GATE) & (fM * a["dt"] <= 1.0 / L.MIN_SPP)
    hz = fM[keep] * to_hz
    return float({"min": hz.min, "max": hz.max}[which]())


@extractor
def waves_ligo_ref(which: str) -> float:
    """The reference frequencies of psi4_ligo in Hz at its calibration mass:
    'isco' (Schwarzschild ISCO of the total mass) or 'qnm' (l = m = 2 Kerr mode of
    the equal-mass remnant, Berti-Cardoso-Will fit)."""
    L, pm = _mod("plot_psi4_ligo"), _mod("psi4_math")
    to_hz = 1.0 / (L.MASS_MSUN * pm.M_SUN_SEC)
    return float({"isco": L.f_isco_M, "qnm": L.f_qnm_M}[which]() * to_hz)


# ---------------------------------------------------------------- the lone throat's wave
@functools.lru_cache(maxsize=None)
def _q2e_records():
    Q = _q2e()
    t_s, cols_s = Q.load(_run_path(Q.STRONG) / "psi4_mode_l2m0.dat")
    t_w, cols_w = Q.stitch([_run_path(n) / "psi4_mode_l2m0.dat" for n in Q.WEAK])
    ctrl = _run_path(Q.CONTROL) / "psi4_mode_l2m0.dat"
    return t_s, cols_s, t_w, cols_w, ctrl


@functools.lru_cache(maxsize=None)
def _q2e_period() -> float:
    """Gate 4's ringdown period (a ~7 s scan fit), computed once per check."""
    t_s, cols_s, *_ = _q2e_records()
    return float(np.mean(_q2e().gate4(t_s, cols_s, [])[0]))


@extractor
def waves_q2e(gate: str, stat: str = "mean") -> float:
    """The lone throat's wave gates (analysis/queue2e_gates.py, on its own arms):
    'arrival_speed' (gate 1, stat min/max over sphere pairs), 'peak_spread'
    (gate 2, % on the peak), 'eps_ratio' (gate 3, mean amplitude ratio for the
    five-fold seed), 'period' / 'period_short' (gate 4: period in M, and % short of
    the Schwarzschild target at the script's M_MS), 'floor_ratio' (gate 5, burst
    over the spherical control's floor)."""
    Q = _q2e()
    t_s, cols_s, t_w, cols_w, ctrl = _q2e_records()
    junk: list[str] = []
    if gate == "arrival_speed":
        arr = []
        for R in sorted(cols_s):
            m = Q.clean(t_s, R)
            e, tt = np.abs(cols_s[R][m]), t_s[m]
            hit = [tt[i] for i in range(len(e) - 1)
                   if e[i] > Q.ARRIVAL_FLOOR and e[i + 1] > Q.ARRIVAL_FLOOR]
            arr.append((R, float(hit[0]) if hit else math.nan))
        v = [(R2 - R1) / (t2 - t1) for (R1, t1), (R2, t2) in zip(arr[:-1], arr[1:])]
        return _pick(v, stat)
    if gate == "peak_spread":
        return float(Q.gate2(t_s, cols_s, junk)[0])
    if gate == "eps_ratio":
        u_win = Q.gate2(t_s, cols_s, junk)[2]
        return _pick(Q.gate3(t_s, cols_s, t_w, cols_w, u_win, junk), stat)
    if gate in ("period", "period_short"):
        per = _q2e_period()
        return per if gate == "period" else 100.0 * (Q.TARGET_PERIOD - per) / Q.TARGET_PERIOD
    if gate == "floor_ratio":
        floor, sig = Q.gate5(t_s, cols_s, ctrl, junk)
        return float(sig / floor)
    raise ValueError(f"unknown gate {gate!r}")


@functools.lru_cache(maxsize=None)
def _seed_amps():
    """plot_seed_linearity's rms amplitudes: ({eps2: {R: rms}}, {R: rms pure})."""
    P = _mod("plot_seed_linearity")
    amps = {eps: {R: P._rms(*_pick_col(P, _run_path(f) / "psi4_mode_l2m0.dat", R)) for R in P.RADII}
            for eps, f in P.ARMS.items()}
    pure_dir = _run_path(P.PURE)
    pure = pure_dir / "small_data" / "psi4_mode_l2m0.dat"
    if not pure.exists():
        pure = pure_dir / "psi4_mode_l2m0.dat"
    amp_pure = {R: P._rms(*_pick_col(P, pure, R)) for R in P.RADII}
    return amps, amp_pure


def _pick_col(P, path, R):
    t, ys = P._l2m0(path)
    return t, ys[R]


@extractor
def waves_seed_ratio(R: float, num: float, den: float) -> float:
    """rms(Re Psi4^20, t = 30-50) of the eps2 = num arm over the eps2 = den arm at
    sphere R (plot_seed_linearity)."""
    amps, _ = _seed_amps()
    return amps[num][float(R)] / amps[den][float(R)]


@extractor
def waves_seed_lin_dev(stat: str) -> float:
    """Departure from linearity in %, |amp / (eps2/0.01 * amp_0.01) - 1|, over the
    0.005 and 0.05 arms and the three spheres: min or max (plot_seed_linearity)."""
    P = _mod("plot_seed_linearity")
    amps, _ = _seed_amps()
    e0 = 0.010
    dev = [100.0 * abs(amps[e][R] / (amps[e0][R] * e / e0) - 1.0)
           for e in amps if e != e0 for R in P.RADII]
    return _pick(dev, stat)


@extractor
def waves_seed_pure_dev(stat: str = "max") -> float:
    """|pure-quadrupole rms / kicked eps2 = 0.01 rms - 1| in %, over the spheres."""
    P = _mod("plot_seed_linearity")
    amps, amp_pure = _seed_amps()
    return _pick([100.0 * abs(amp_pure[R] / amps[0.010][R] - 1.0) for R in P.RADII], stat)


# ---------------------------------------------------------------- spiral fill window
def _weyl_modes(run: str, mode: str):
    radii = [float(x) for x in params(run)["extraction_radii"].split()]
    return _mod("streams").load_mode(_run_path(run) / f"Weyl4_mode_{mode}.dat", radii)


@extractor
def waves_fill_twin(R: float) -> float:
    """max |dPsi4^22| / peak in %, fill twin against the freeze arm over their
    shared record from the engagement time (plot_fill_insensitivity's numbers)."""
    F = _mod("plot_fill_insensitivity")
    ta, ya = _weyl_modes(pathlib.PurePosixPath(F.ARM_A).name, "22")
    tb, yb = _weyl_modes(pathlib.PurePosixPath(F.ARM_B).name, "22")
    n = min(len(ta), len(tb))
    if not np.allclose(ta[:n], tb[:n]):
        raise ValueError("the two fill arms' clocks disagree")
    keep = ta[:n] >= F.T_ENGAGE
    a, b = ya[float(R)][:n][keep], yb[float(R)][:n][keep]
    return 100.0 * float(np.abs(a - b).max() / np.abs(a).max())


@extractor
def waves_mode_diff(run_a: str, run_b: str, R: float, mode: str = "22") -> float:
    """max |Psi4_a - Psi4_b| over the two arms' common samples, over the peak
    |Psi4_a| at sphere R (in-code Weyl4 streams)."""
    ta, ya = _weyl_modes(run_a, mode)
    tb, yb = _weyl_modes(run_b, mode)
    common = np.intersect1d(np.round(ta, 4), np.round(tb, 4))
    ia, ib = np.isin(np.round(ta, 4), common), np.isin(np.round(tb, 4), common)
    d = np.abs(ya[float(R)][ia] - yb[float(R)][ib])
    return float(d.max() / np.abs(ya[float(R)]).max())


# ---------------------------------------------------------------- the scalar channel
def _scalar_channel(run: str, R: int):
    S = _mod("plot_scalar_channel")
    p = _run_path(run)
    tg, fg = S._gw_flux(p / "psi4_mode_l2_all.dat", int(R))
    ts, kin, per_l = S._scalar(p / "scalar_modes.dat", int(R))     # kin = PHYSICAL flux
    return S, tg, S._cum(tg, fg), ts, S._cum(ts, kin), per_l


@functools.lru_cache(maxsize=None)
def _band_egw(run: str, R: int, t_cut: float, M: float = 2.0) -> float:
    """E_GW through sphere R by t_cut in Fig. psi4_ligo(d)'s convention, code units:
    the band integral of |int r Psi4_22 dt'|^2 about the record's resolved Psi_4 peak
    (plot_psi4_ligo.prepare's band_energy), doubled for +-m.  Unlike the running
    integral of plot_scalar_channel it does not accumulate the low-frequency drift of
    the time-integrated Psi_4."""
    pm, streams = _mod("psi4_math"), _mod("streams")
    t, d = streams.load_l2_all(_run_path(run) / "psi4_mode_l2_all.dat")
    keep = t <= t_cut + 1e-9
    u, w = (t[keep] - float(R)) / M, d[(2, float(R))][keep] * M
    dt = (u[-1] - u[0]) / (u.size - 1)
    return float(pm._compute_radiated_energy(u, w, m=2, f_peak=_band_peak(w, dt))) * M


@extractor
def waves_scalar_ratio(run: str, R: int, t_cut: float, estimator: str = "kin") -> float:
    """|E_phi| / E_GW through sphere R by t_cut (plot_scalar_channel): the
    kinematic-flux integral over the figure's running E_GW; estimator = 'wavezone'
    for sum_lm |dA_lm/dt|^2 over the same E_GW; 'band' for the kinematic integral
    over the band-limited E_GW of Fig. psi4_ligo(d) (_band_egw)."""
    S, tg, Eg, ts, Ep, per_l = _scalar_channel(run, R)
    if estimator == "band":
        return abs(S._at(ts, Ep, t_cut)) / _band_egw(run, int(R), float(t_cut))
    g = S._at(tg, Eg, t_cut)
    if estimator == "kin":
        return abs(S._at(ts, Ep, t_cut)) / g
    k = ts <= t_cut
    return float(sum(np.trapezoid(per_l[l][k], ts[k]) for l in S.ELLS) / g)


@extractor
def waves_id_sphere(run: str, R: float, field: str, stat: str = "min", n: int = 181) -> float:
    """The initial data on the coordinate sphere of radius R about the box centre,
    from the run's own params and research.tex Sec. II (alpha = e^u, chi = e^(2u)
    psi^-4, u = u_A + u_B, psi = 1 + sum_i (sqrt(Omega_i) - 1)): field 'alpha', 'chi',
    or 'flux_factor' = alpha^2 chi^-1/2, the factor between the kinematic scalar flux
    and Eq. scalarflux at zero shift on a conformally flat sphere; stat min / max /
    mean (area-weighted) over the sphere.  No stream records alpha or chi on the
    sphere, so this is the only reading there is -- the t = 0 value."""
    p = params(run)

    def vec(key):
        return np.array([float(x) for x in p[key].split()[:3]])

    th = np.linspace(0.0, math.pi, n)
    ph = np.linspace(0.0, 2.0 * math.pi, 2 * n, endpoint=False)
    T, P = np.meshgrid(th, ph, indexing="ij")
    x = R * np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), np.cos(T)], axis=-1)
    u = np.zeros(T.shape)
    psi = np.ones(T.shape)
    for b in ("A", "B"):
        a, m = float(p[f"wormhole_throat_radius_{b}"]), float(p[f"wormhole_drainhole_mass_{b}"])
        r = np.linalg.norm(x - vec(f"wormhole_center{b}"), axis=-1)
        X = (r - a * a / (4.0 * r)) / a
        u += (m / a) * (np.arctan(X) - 0.5 * math.pi)
        psi += np.sqrt(1.0 + a * a / (4.0 * r * r)) - 1.0
    alpha, chi = np.exp(u), np.exp(2.0 * u) * psi ** -4
    vals = {"alpha": alpha, "chi": chi, "flux_factor": alpha ** 2 / np.sqrt(chi)}[field]
    if stat == "mean":
        wgt = np.sin(T)
        return float((vals * wgt).sum() / wgt.sum())
    return float({"min": vals.min, "max": vals.max}[stat]())


@extractor
def waves_scalar_energy(run: str, R: int, t_cut: float, M: float = 1.0,
                        signed: bool = False) -> float:
    """E_phi = int^t_cut (-flux_kin) dt through sphere R (physical sign), in units
    of M; its magnitude unless signed."""
    S, _, _, ts, Ep, _ = _scalar_channel(run, R)
    e = S._at(ts, Ep, t_cut) / M
    return e if signed else abs(e)


@extractor
def waves_scalar_multipole(run: str, R: int, t_cut: float, stat: str) -> float:
    """log10 of the l = 1 dominance of the scalar power sum_m |dA_lm/dt|^2 by t_cut:
    'share' = l1 / (l0 + l2), 'gap' = min(l1/l0, l1/l2)."""
    S, _, _, ts, _, per_l = _scalar_channel(run, R)
    k = ts <= t_cut
    E = {l: np.trapezoid(per_l[l][k], ts[k]) for l in S.ELLS}
    if stat == "share":
        return float(np.log10(E[1] / (E[0] + E[2])))
    return float(np.log10(min(E[1] / E[0], E[1] / E[2])))


@extractor
def waves_mouth_crossing(run: str, R: float) -> float:
    """When the per-mouth areal radius first passes sphere R (plot_scalar_channel)."""
    t = _mod("plot_scalar_channel")._mouth_crossing(_run_path(run) / "horizon_scan.dat", R)
    if t is None:
        raise ValueError(f"{run}: the mouths never reach R = {R}")
    return float(t)


# ---------------------------------------------------------------- censorship (envelopes)
def _flux(run: str, R: int):
    return _mod("plot_scalar_censorship")._flux(_run_path(run) / "scalar_modes.dat", int(R))


@functools.lru_cache(maxsize=None)
def _envelope(run: str, R: int):
    t, k = _flux(run, R)
    return t, _mod("plot_scalar_censorship")._envelope(t, k)


@extractor
def waves_env_efold(run: str, R: int, t0: float, t1: float, kind: str = "decay") -> float:
    """e-fold time of the |F_phi| running-max envelope (plot_scalar_censorship) from
    a log-linear fit over [t0, t1]: -1/slope for a decay, 1/slope for a growth."""
    t, e = _envelope(run, R)
    fit = (t >= t0) & (t <= t1)
    s = float(np.polyfit(t[fit], np.log(e[fit]), 1)[0])
    return -1.0 / s if kind == "decay" else 1.0 / s


@extractor
def waves_env_drop(run: str, R: int, t: float) -> float:
    """Envelope maximum over the envelope at time t (how far it has fallen)."""
    tt, e = _envelope(run, R)
    return float(e.max() / np.interp(t, tt, e))


@extractor
def waves_post_energy(run: str, R: int, t0: float, M: float = 1.0) -> float:
    """Post-horizon E_phi = int_{t >= t0} (-flux_kin) dt at sphere R, physical sign,
    in units of M (the censorship figure's numbers are in code units, M = 1)."""
    t, k = _flux(run, R)
    s = t >= t0
    return float(-np.trapezoid(k[s], t[s]) / M)


@extractor
def waves_flux_sign_stretch(run: str, t0: float, min_len: float, radii: list | None = None) -> float:
    """Median length of the constant-sign stretches of the raw flux_kin after t0,
    pooled over spheres, dropping brief flips shorter than min_len."""
    stretches = []
    for R in (radii or [10, 14, 18]):
        t, k = _flux(run, R)
        s = t >= t0
        tc = t[s][:-1][np.diff(np.sign(k[s])) != 0]
        stretches += [d for d in np.diff(tc) if d >= min_len]
    return float(np.median(stretches))


# ---------------------------------------------------------------- horizons on the scalar arms
def _scan(run: str, centre: str):
    h = np.genfromtxt(_run_path(run) / "horizon_scan.dat", dtype=None, encoding=None, names=True)
    return h[h["centre"] == centre]


@extractor
def waves_first_mots(run: str, centre: str = "C", permanent: bool = False) -> float:
    """First scan time with a MOTS on the given centre; with permanent, the first
    time from which every later scan row carries one."""
    a = _scan(run, centre)
    has = a["n_mots"] > 0
    if not has.any():
        raise ValueError(f"{run}: no MOTS on centre {centre}")
    if not permanent:
        return float(a["time"][has][0])
    for i in range(len(has)):
        if has[i:].all():
            return float(a["time"][i])
    raise ValueError(f"{run}: the MOTS on centre {centre} is never permanent")


@extractor
def waves_mots_radius(run: str, centre: str = "A", t: float | None = None) -> float:
    """Areal radius of the scan's MOTS: at the first MOTS row, or at time t."""
    a = _scan(run, centre)
    has = a["n_mots"] > 0
    rows = a[has]
    if t is None:
        return float(rows["R_mots"][0])
    i = int(np.argmin(np.abs(rows["time"] - t)))
    if abs(rows["time"][i] - t) > 0.26:
        raise ValueError(f"{run}: no MOTS row at t = {t} on centre {centre}")
    return float(rows["R_mots"][i])


# ---------------------------------------------------------------- the vacuum pass
@extractor
def waves_newtonian_momentum(run: str, kind: str, mass: float = 1.0) -> float:
    """Newtonian momentum per body of an equal-mass pair at the run's separation
    (bh offsets in its params), masses = the per-hole ADM mass: circular
    p = (m/2) sqrt(2m/d), parabolic p = (m/2) sqrt(4m/d)."""
    p = params(run)
    d = abs(float(p["bh2.offset"].split()[0]) - float(p["bh1.offset"].split()[0]))
    v_rel = math.sqrt({"circular": 1.0, "parabolic": 2.0}[kind] * 2.0 * mass / d)
    return 0.5 * mass * v_rel
