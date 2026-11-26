"""Retain both radial and angular coefficients of the cubic dragging field.

The v1 metric representation left H angularly nodal. Its small high-order
angular variations suffered the same rounding as f and b had. Keep every H
coefficient as well; the equations, origin conditions and infinity mode stay
unchanged. Old archives retain their original v1 interpretation.
"""

import numpy as np
from scipy.fft import dct

from grteclyn_stationary.railgun.smooth_spectral import SmoothSpectralProblem
from grteclyn_stationary.railgun.regular_dragging import RegularDraggingProblem, regular_operator

REPRESENTATION = "spectral_all_metric_cubic_dragging_smooth_origin_v2"


def angular_coefficients(values):
    c = dct(np.asarray(values, dtype=np.longdouble), type=1, axis=1) / (
        values.shape[1] - 1
    )
    c[:, [0, -1]] *= 0.5
    return np.asarray(c, dtype=float)


class SmoothFullSpectralProblem(SmoothSpectralProblem):
    discretisation = REPRESENTATION

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.representation = REPRESENTATION

    def dragging_coefficients(self, u):
        return u[self.n : 2 * self.n].reshape(self.shape)

    def raw_dragging(self, u):
        # Compatibility view for independent nodal checks and old APIs.
        xp = np if isinstance(u, np.ndarray) else self.xp
        return self.dragging_coefficients(u) @ xp.asarray(self.angular_basis).T

    def pack(self, arrays, frequencies):
        result = super().pack(arrays, frequencies)
        result[self.n : 2 * self.n] = angular_coefficients(
            result[self.n : 2 * self.n].reshape(self.shape)
        ).ravel()
        return result

    def h_derivative(self, u, radial=0, angular=0, xp=np):
        bx = (self.h_basis, self.h_first, self.h_second)[radial]
        by = (self.angular_basis, self.angular_first, self.angular_second)[angular]
        return xp.asarray(bx) @ self.dragging_coefficients(u) @ xp.asarray(by).T

    def dragging_jets(self, u, xp=np):
        h = self.h_derivative(u, xp=xp)
        hx = self.h_derivative(u, 1, xp=xp)
        hxx = self.h_derivative(u, 2, xp=xp)
        t = 1 - xp.asarray(self.s[:, None])
        return dict(
            w=t**3 * h,
            w_x=t**3 * hx - 3 * t * t * h,
            w_xx=t**3 * hxx - 6 * t * t * hx + 6 * t * h,
            w_y=t**3 * self.h_derivative(u, 0, 1, xp),
            w_yy=t**3 * self.h_derivative(u, 0, 2, xp),
        )

    def regular_rows(self, u, xp=np):
        arrays, freq = self.unpack(u)
        jets = self.state_jets(u, xp)
        h, hx, hxx, hy, hyy = (
            self.h_derivative(u, r, a, xp)[1:-1]
            for r, a in ((0, 0), (1, 0), (2, 0), (0, 1), (0, 2))
        )
        t = 1 - xp.asarray(self.s[1:-1, None])
        y = xp.asarray(self.y[None, :])
        sk = (1 - y) / 2
        source = xp.zeros_like(h)
        for i, (field, omega) in enumerate(zip(self.fields, freq)):
            ka = abs(field.winding)
            if ka:
                parity = (1 + y) / 2 if field.parity == "odd" else 1.0
                source += (
                    4
                    * field.winding
                    * (omega + field.winding * arrays["w"][1:-1])
                    * xp.exp(jets["N"] * sk)
                    * sk ** (ka - 1)
                    * parity
                    * jets[f"q{i}"] ** 2
                    / t**3
                )
        return regular_operator(
            xp.asarray(self.s[1:-1, None]),
            y,
            h,
            hx,
            hxx,
            hy,
            hyy,
            jets["f_x"],
            jets["f_y"],
            jets["B"],
            jets["B_x"],
            jets["B_y"],
            source,
            power=3,
            xp=xp,
        )

    def infinity_boundary(self, u, xp=np):
        arrays, _ = self.unpack(u)
        h, hs, hy, hyy = (
            self.h_derivative(u, r, a, xp)[0]
            for r, a in ((0, 0), (1, 0), (0, 1), (0, 2))
        )
        fx, bx = self.infinity_metric_derivatives(u, arrays, xp)
        drift = -2 * fx + 3 * bx / (1 + arrays["b"][0])
        drifty = xp.asarray(self.dy) @ drift
        y = xp.asarray(self.y)
        angular = 4 * (1 - y * y) * hyy - (10 * y + 6) * hy
        q, left = xp.asarray(self.mode), xp.asarray(self.left)
        robin = left @ (4 * hs + (6 + 3 * drift) * h + 4 * (1 - y * y) * drifty * hy)
        return angular - q * (left @ angular) + q * robin

    def origin_block(self, u, arrays, name, xp):
        if name != "w":
            return super().origin_block(u, arrays, name, xp)
        angular = 8 * xp.asarray(self.h_basis[-1]) @ self.dragging_coefficients(u)
        anisotropy = xp.asarray(self.angular_basis[:, 1:]) @ angular[1:]
        derivative = self.dragging_jets(u, xp)["w_x"][-1]
        return (anisotropy - xp.mean(anisotropy) + xp.mean(derivative))[None, :]

    def dragging_sample(self, u, s, y, *, derivative=False, one_minus_s=None):
        s, y = np.atleast_1d(s), np.atleast_1d(y)
        c = np.asarray(self.dragging_coefficients(np.asarray(u)))
        by = np.polynomial.chebyshev.chebvander(y, self.ny)
        h = np.polynomial.chebyshev.chebvander(s, self.nx) @ c @ by.T
        t = (1 - s if one_minus_s is None else np.atleast_1d(one_minus_s))[:, None]
        if not derivative:
            return t**3 * h
        dc = np.polynomial.chebyshev.chebder(c, axis=0)
        return (
            t**3 * (np.polynomial.chebyshev.chebvander(s, self.nx - 1) @ dc @ by.T)
            - 3 * t * t * h
        )

    def transfer(self, old, u, *, perturb=0.0):
        result = super().transfer(old, u, perturb=perturb)
        if (isinstance(old, RegularDraggingProblem)
                and old.length == self.length and old.power == self.power):
            c = (
                old.dragging_coefficients(np.asarray(u))
                if hasattr(old, "dragging_coefficients")
                else angular_coefficients(np.asarray(old.raw_dragging(np.asarray(u))))
            )
            target = np.zeros(self.shape)
            nr, na = min(c.shape[0], self.nx + 1), min(c.shape[1], self.ny + 1)
            target[:nr, :na] = c[:nr, :na]
            result[self.n : 2 * self.n] = target.ravel()
        return result
