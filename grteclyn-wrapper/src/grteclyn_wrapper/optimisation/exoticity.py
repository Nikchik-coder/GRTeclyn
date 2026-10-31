"""The exotic-matter bill of a matter-solver solution (campaign M, step 2).

The bill is the published Fig. 3e quantity X = |VIQ| / R_e: the phantom's
volume integral quantifier (Visser, Kar & Dadhich, PRL 90, 201102) over
the throat's equatorial radius.  For the matter ansatz

    ds^2 = -e^f dt^2 + B^2 e^{-f} [e^nu (d eta^2 + h d theta^2)
                                   + h sin^2 theta (d phi - omega dt)^2]

rho + p_eta = -g^{eta eta} psi_eta^2 in the solver's psi normalization
(the potential cancels between rho and p_eta) and the slice's volume
element is B^3 e^{-3f/2 + nu} h sin theta, so nu drops out and

    VIQ = -(1/2) int d eta int d mu  B e^{-f/2} h psi_eta^2,   mu = cos theta,

which at B = 1, psi_eta = D/h is the spinning package's
observables.exotic_matter, -(D^2/2) int d eta/h int d mu e^{-f/2}.  The
throat is the minimum of the
eta = const area 2 pi h int d mu B^2 e^{-f + nu/2}, and R_e = B e^{-f/2}
sqrt(h) on its equator (observables._throat's R_eq at B = 1, which
places the minimum by golden section, to about 1e-8).

Fields are node arrays on the solver's tensor Chebyshev-Lobatto grid,
evaluated off the nodes by spinning_wormhole.spectral.cheb_eval (which
returns the node value on an exact hit, so a throat on the xi = 0 node is
safe).  numpy only.
"""

from __future__ import annotations

import math

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval

__all__ = ["bill", "throat", "nec_rays", "exotic_x", "tidal"]


def _grid_eval(sx, sy, A, xi, y):
    """A on the tensor grid xi x y, shape (len(xi), len(y))."""
    rows = cheb_eval(sx, np.asarray(A), np.atleast_1d(xi))
    return cheb_eval(sy, rows.T, np.atleast_1d(y)).T


def bill(eta0, rmap, sx, sy, Dx, F, B, PSI, n_x: int = 96,
         n_mu: int = 48) -> float:
    """VIQ (negative), Gauss-Legendre in xi on the solver's radial map and
    in mu, the quadrature of observables.exotic_matter."""
    xg, wx = np.polynomial.legendre.leggauss(n_x)
    mg, wm = np.polynomial.legendre.leggauss(n_mu)
    y = 2.0 * mg**2 - 1.0
    f = _grid_eval(sx, sy, F, xg, y)
    b = _grid_eval(sx, sy, B, xg, y)
    psi_x = _grid_eval(sx, sy, Dx @ np.asarray(PSI), xg, y)
    h = rmap.eta(xg) ** 2 + eta0**2
    # d eta = eta' d xi and psi_eta = psi_x / eta'
    weight = (h / rmap.deta(xg))[:, None]
    integ = b * np.exp(-0.5 * f) * weight * psi_x**2
    return float(-0.5 * np.einsum("i,j,ij->", wx, wm, integ))


def throat(eta0, rmap, sx, sy, Dx, F, N, B, n_mu: int = 64) -> dict:
    """The area-minimizing eta = const surface: eta_t, its area and R_e.
    A node scan brackets the minimum and the root of dA/dxi, from the
    spectral xi-derivatives, places it to round-off (a golden section on
    A itself stops near 1e-8: the minimum is flat, and R_e is not)."""
    from scipy.optimize import brentq

    mu, wmu = np.polynomial.legendre.leggauss(n_mu)
    y = 2.0 * mu**2 - 1.0
    sin2 = 1.0 - mu**2
    F, N, B = (np.asarray(a) for a in (F, N, B))
    jets = (F, N, B, Dx @ F, Dx @ N, Dx @ B)

    def parts(xi):
        xi = np.atleast_1d(np.asarray(xi, float))
        f, nn, b, f_x, n_x, b_x = (_grid_eval(sx, sy, A, xi, y)
                                   for A in jets)
        g = b**2 * np.exp(-f + 0.5 * nn * sin2)
        eta = rmap.eta(xi)
        return eta, eta**2 + eta0**2, g, g * (2.0 * b_x / b - f_x
                                             + 0.5 * n_x * sin2)

    def area(xi):
        _, h, g, _ = parts(xi)
        return 2.0 * math.pi * h * (g @ wmu)

    def darea(xi):
        eta, h, g, g_x = parts(xi)
        return float((2.0 * math.pi * (2.0 * eta * rmap.deta(xi) * (g @ wmu)
                                       + h * (g_x @ wmu)))[0])

    xi_i = sx[1:-1]
    k = int(np.argmin(area(xi_i)))
    lo = xi_i[min(k + 1, xi_i.size - 1)]       # xi falls with node index
    hi = xi_i[max(k - 1, 0)]
    xi_t = brentq(darea, lo, hi, xtol=1e-15, rtol=4.0 * np.finfo(float).eps)
    eta_t = float(rmap.eta(np.array([xi_t]))[0])
    xi_v, y_eq = np.array([xi_t]), np.array([-1.0])
    f_eq = _grid_eval(sx, sy, F, xi_v, y_eq)[0, 0]
    b_eq = _grid_eval(sx, sy, B, xi_v, y_eq)[0, 0]
    h_t = eta_t**2 + eta0**2
    area_t = float(area(xi_t)[0])
    # R_pol (KK eq. 6 with B): meridian half-length / pi.
    th_g, wth = np.polynomial.legendre.leggauss(64)
    th = 0.5 * math.pi * (th_g + 1.0)
    y_th = np.cos(2.0 * th)
    f_m = _grid_eval(sx, sy, F, xi_v, y_th)[0]
    n_m = _grid_eval(sx, sy, N, xi_v, y_th)[0]
    b_m = _grid_eval(sx, sy, B, xi_v, y_th)[0]
    nu_m = n_m * np.sin(th) ** 2
    r_pol = math.sqrt(h_t) / math.pi * (0.5 * math.pi) * float(
        (b_m * np.exp(0.5 * (nu_m - f_m))) @ wth)
    return {"eta_throat": eta_t, "area_throat": area_t,
            "R_e": float(b_eq * math.exp(-0.5 * f_eq) * math.sqrt(h_t)),
            "R_A": math.sqrt(area_t / (4.0 * math.pi)),
            "R_pol": r_pol}


def nec_rays(eta0, rmap, sx, sy, Dx, N, B, PSI, n_x: int = 96) -> dict:
    """The NEC integral int T_ab k^a k^b d lambda along the two radial null
    geodesics through the throat with zero angular momentum: the axis
    (y = 1) and the equator (y = -1), the only places such a ray keeps
    theta.  With unit energy at infinity, t' = e^{-f} and eta' =
    e^{-nu/2} / B (the ray co-rotates, phi' = omega t'); the potential
    drops out on a null vector and T_ab k^a k^b = -(k.d psi)^2 / (4 pi), so

        I = -(1/(4 pi)) int d eta e^{-nu/2} psi_eta^2 / B,

    -D^2 / (8 eta0^3) for the static Ellis throat."""
    xg, wx = np.polynomial.legendre.leggauss(n_x)
    deta = rmap.deta(xg)
    out = {}
    for name, yv in (("axis", 1.0), ("equator", -1.0)):
        y = np.array([yv])
        nu = _grid_eval(sx, sy, N, xg, y)[:, 0] * (1.0 - yv) / 2.0
        b = _grid_eval(sx, sy, B, xg, y)[:, 0]
        psi_x = _grid_eval(sx, sy, Dx @ np.asarray(PSI), xg, y)[:, 0]
        # d eta = eta' d xi and psi_eta = psi_x / eta'
        integ = np.exp(-0.5 * nu) * psi_x**2 / (b * deta)
        out[name] = float(-(wx @ integ) / (4.0 * math.pi))
    return out


def exotic_x(eta0, rmap, sx, sy, Dx, F, N, B, PSI) -> dict:
    """The Fig. 3e quantity X = |VIQ| / R_e, with VIQ and the throat.

    ``X_A = |VIQ| / R_A`` is the same bill per areal radius, used when
    the search pins area instead of $R_e$ (so flattening cannot cheat
    $X$ by growing $R_e$ at fixed $A$).  ``X`` itself is unchanged.
    """
    viq = bill(eta0, rmap, sx, sy, Dx, F, B, PSI)
    th = throat(eta0, rmap, sx, sy, Dx, F, N, B)
    return {"VIQ": viq, **th, "X": abs(viq) / th["R_e"],
            "X_A": abs(viq) / th["R_A"]}


class _Jet:
    """Value, gradient and Hessian in (eta, theta), including mixed terms."""

    __slots__ = ("v", "g", "H")

    def __init__(self, v, g=None, H=None):
        self.v = float(v)
        self.g = np.zeros(2) if g is None else np.asarray(g, float)
        self.H = np.zeros((2, 2)) if H is None else np.asarray(H, float)

    def __neg__(self):
        return _Jet(-self.v, -self.g, -self.H)

    def __add__(self, o):
        return _Jet(self.v + o.v, self.g + o.g, self.H + o.H)

    def __sub__(self, o):
        return self + (-o)

    def __mul__(self, o):
        if not isinstance(o, _Jet):
            return _Jet(self.v * o, self.g * o, self.H * o)
        return _Jet(self.v * o.v, self.v * o.g + o.v * self.g,
                    self.v * o.H + o.v * self.H
                    + np.outer(self.g, o.g) + np.outer(o.g, self.g))

    __rmul__ = __mul__

    def exp(self):
        e = math.exp(self.v)
        return _Jet(e, e * self.g, e * (self.H + np.outer(self.g, self.g)))


def tidal(eta0, rmap, sx, sy, Dx, Dy, F, W, N, B, xi, v: float = 0.0,
          theta: float = math.pi / 2, *, spectral_jets=None, return_curvature=False) -> dict:
    """The tidal tensor E_ij at any latitude (equator by default) at radial position xi,
    in the orthonormal frame of a traveler crossing radially with speed v
    relative to the zero-angular-momentum observer u = e^{-f/2}
    (d_t + omega d_phi); frame legs 1, 2, 3 = radial (boosted), theta, phi.

    E_ij = R(e_i, u', e_j, u') with the MTW sign of Riemann, so geodesic
    deviation is a^i = -E_ij xi^j per unit separation: a positive eigenvalue
    compresses.  Morris and Thorne's bounds cap max |eig| times the
    traveler's size.  Static Ellis closed form (their lateral tidal, AJP 56,
    395, box 2 with b = eta0^2/r): E_rad = 0 and E_theta = E_phi =
    -gamma_L^2 v^2 eta0^2 / h^2, so a throat transit stretches sideways.

    Curvature uses spectral jets with the full y = cos(2 theta) chain rule,
    including angular and mixed second derivatives. At the coordinate axis
    two even extrapolations give the regular orthonormal limit and its error.
    Off-axis return_curvature supplies the unboosted orthonormal Ricci tensor
    for the independent Einstein check instead of the tidal eigenvalues.
    """
    if not (-1 < v < 1) or not (0 <= theta <= math.pi/2):
        raise ValueError("tidal: |v| < 1 and 0 <= theta <= pi/2 required")
    if theta == 0:
        if return_curvature:
            raise ValueError('Ricci check requires an off-axis point')
        # Smooth-axis limit: even diagonal entries; axial symmetry removes
        # radial/transverse mixing and makes the two transverse entries equal.
        samples = [tidal(eta0,rmap,sx,sy,Dx,Dy,F,W,N,B,xi,v,t,spectral_jets=spectral_jets)
                   for t in (.004,.002,.001)]
        diagonals = [np.diag(s['E']) for s in samples]
        coarse = (4*diagonals[1]-diagonals[0])/3
        fine = (4*diagonals[2]-diagonals[1])/3
        fine[1:] = np.mean(fine[1:])
        out = dict(samples[-1], E=np.diag(fine), eigs=np.sort(fine),
                   rad=float(fine[0]), theta=float(fine[1]), phi=float(fine[2]),
                   max_abs=float(np.max(abs(fine))),
                   axis_error=float(np.max(abs(fine-coarse))))
        return out
    xi_v = np.array([float(xi)])
    yy = math.cos(2*theta)
    y_eq = np.array([yy])
    yt, ytt = -2*math.sin(2*theta), -4*yy
    ep = float(rmap.deta(xi_v)[0])
    epp = float(rmap.d2eta(xi_v)[0])

    def jet(A, index):
        A = np.asarray(A)
        def at(a):
            return _grid_eval(sx,sy,a,xi_v,y_eq)[0,0]
        if spectral_jets is None:
            derivatives=(Dx@A,A@Dy.T,Dx@(Dx@A),(Dx@A)@Dy.T,(A@Dy.T)@Dy.T)
        else:
            derivatives=spectral_jets[index]
        gx,gy,gxx,gxy,gyy=map(at,derivatives)
        return _Jet(at(A), [gx/ep,yt*gy],
                    [[(gxx-gx*epp/ep)/ep**2,yt*gxy/ep],
                     [yt*gxy/ep,yt*yt*gyy+ytt*gy]])

    fj, wj, bj, nj = (jet(a,i) for i,a in enumerate((F,W,B,N)))
    # A constant azimuthal coordinate rotation sets W=0 at this point while
    # retaining all its derivatives. It prevents catastrophic cancellation
    # in g_tt*g_phiphi-g_tphi**2 at the rotating asymptotic end.
    wj = _Jet(0.,wj.g,wj.H)
    f0, w0 = fj.v, 0.
    s2j = _Jet(math.sin(theta)**2, [0.,math.sin(2*theta)],
               [[0.,0.],[0.,2*math.cos(2*theta)]])
    nuj = nj*s2j
    eta = float(rmap.eta(xi_v)[0])
    hj = _Jet(eta**2+eta0**2,[2*eta,0.],[[2.,0.],[0.,0.]])

    ef = fj.exp()
    pj = bj * bj * (-fj).exp()               # B^2 e^{-f}
    phs = pj * hj * s2j
    gjet = [[None] * 4 for _ in range(4)]
    gjet[0][0] = -ef + phs * wj * wj
    gjet[0][3] = gjet[3][0] = -(phs * wj)
    gjet[3][3] = phs
    gjet[1][1] = pj * nuj.exp()
    gjet[2][2] = pj * nuj.exp() * hj

    g4 = np.zeros((4, 4))
    dg = np.zeros((4, 4, 4))                 # dg[k, i, j] = d_k g_ij
    ddg = np.zeros((4, 4, 4, 4))             # ddg[k, l, i, j]
    for i in range(4):
        for j in range(4):
            jj = gjet[i][j]
            if jj is None:
                continue
            g4[i, j] = jj.v
            dg[1:3, i, j] = jj.g
            ddg[1:3, 1:3, i, j] = jj.H

    ginv = np.linalg.inv(g4)
    # Gam^a_ij = (1/2) g^al (d_i g_lj + d_j g_li - d_l g_ij), and its
    # derivative with d_k g^al = -g^am (d_k g_mn) g^nl
    brace = np.einsum("ilj->ilj", dg) + np.einsum("jli->ilj", dg) \
        - np.einsum("lij->ilj", dg)
    gam = 0.5 * np.einsum("al,ilj->aij", ginv, brace)
    dginv = -np.einsum("am,kmn,nl->kal", ginv, dg, ginv)
    dbrace = np.einsum("kilj->kilj", ddg) + np.einsum("kjli->kilj", ddg) \
        - np.einsum("klij->kilj", ddg)
    dgam = (0.5 * np.einsum("kal,ilj->kaij", dginv, brace)
            + 0.5 * np.einsum("al,kilj->kaij", ginv, dbrace))
    # MTW: R^a_bij = d_i Gam^a_jb - d_j Gam^a_ib
    #               + Gam^a_il Gam^l_jb - Gam^a_jl Gam^l_ib
    riem = (np.einsum("iajb->abij", dgam) - np.einsum("jaib->abij", dgam)
            + np.einsum("ail,ljb->abij", gam, gam)
            - np.einsum("ajl,lib->abij", gam, gam))
    rlow = np.einsum("am,mbij->abij", g4, riem)

    u = math.exp(-0.5 * f0) * np.array([1.0, 0.0, 0.0, w0])
    e1 = np.array([0.0, 1.0 / math.sqrt(g4[1, 1]), 0.0, 0.0])
    e2 = np.array([0.0, 0.0, 1.0 / math.sqrt(g4[2, 2]), 0.0])
    e3 = np.array([0.0, 0.0, 0.0, 1.0 / math.sqrt(g4[3, 3])])
    if return_curvature:
        frame=np.array([u,e1,e2,e3])
        ricci=np.einsum('abad->bd',riem)
        return {'ricci_frame':frame@ricci@frame.T}
    gam_l = 1.0 / math.sqrt(1.0 - v * v)
    ub = gam_l * (u + v * e1)
    legs = [gam_l * (e1 + v * u), e2, e3]
    E = np.array([[float(np.einsum("abcd,a,b,c,d->", rlow, ei, ub, ej, ub))
                   for ej in legs] for ei in legs])
    eigs = np.linalg.eigvalsh(E)
    return {"E": E, "eigs": eigs, "rad": float(E[0, 0]),
            "theta": float(E[1, 1]), "phi": float(E[2, 2]),
            "max_abs": float(np.max(np.abs(eigs))), "v": float(v),
            "eta": eta}
