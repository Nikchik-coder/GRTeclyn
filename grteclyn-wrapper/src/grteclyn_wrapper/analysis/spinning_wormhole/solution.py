"""One converged background: parameters, map, node values, evaluation, I/O.

A Solution is what the continuation driver saves at every converged step
(SpinningSolver.md section 4, "Persistence") and what the table writer and
the Einstein check consume: fields are evaluated ANYWHERE by barycentric
interpolation, with derivatives from the spectrally differentiated node
values, so downstream code gets exact jets rather than finite differences.

On disk: ``<name>.npz`` (node arrays) + ``<name>.json`` (parameters,
observables, gate values) -- the JSON is the human-readable record, the
npz what re-seeding and tabling load.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import spectral

__all__ = ["Solution"]

FIELDS = ("f", "w", "N")


@dataclass
class Solution:
    eta0: float
    gamma: float
    omega_inf: float
    map_name: str
    map_params: dict
    F: np.ndarray                      # (nx+1, ny+1) node values, f
    W: np.ndarray                      # omega
    N: np.ndarray                      # nu / sin^2 theta
    observables: dict = field(default_factory=dict)
    gates: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nx = self.F.shape[0] - 1
        self.ny = self.F.shape[1] - 1
        self.sx, self._dx = spectral.lobatto(self.nx)
        self.sy, self._dy = spectral.lobatto(self.ny)

    # -- geometry -------------------------------------------------------------

    @property
    def radial_map(self):
        params = dict(self.map_params)
        params.pop("eta0", None)
        return spectral.MAPS[self.map_name](eta0=self.eta0, **params)

    def node_array(self, which: str) -> np.ndarray:
        return {"f": self.F, "w": self.W, "N": self.N}[which]

    # -- evaluation -----------------------------------------------------------

    def jet(self, which: str, dx_order: int = 0, dy_order: int = 0) -> np.ndarray:
        """Node values of d^a/dxi^a d^b/dy^b of one field (spectral)."""
        a = self.node_array(which)
        for _ in range(dx_order):
            a = self._dx @ a
        for _ in range(dy_order):
            a = a @ self._dy.T
        return a

    def eval_xy(self, which: str, xi, y, dx_order: int = 0,
                dy_order: int = 0) -> np.ndarray:
        """Barycentric evaluation at points (xi_k, y_k) (equal-length 1D)."""
        xi = np.atleast_1d(np.asarray(xi, float))
        y = np.atleast_1d(np.asarray(y, float))
        a = self.jet(which, dx_order, dy_order)
        rows = spectral.cheb_eval(self.sx, a, xi)        # (npts, ny+1)
        out = np.empty(xi.size)
        for k in range(xi.size):
            out[k] = spectral.cheb_eval(self.sy, rows[k], np.array([y[k]]))[0]
        return out

    def eval_grid(self, which: str, xi, y, dx_order: int = 0,
                  dy_order: int = 0) -> np.ndarray:
        """Barycentric evaluation on the tensor grid xi x y: (len(xi),
        len(y)), two 1-D passes (fast path for table writing)."""
        xi = np.atleast_1d(np.asarray(xi, float))
        y = np.atleast_1d(np.asarray(y, float))
        a = self.jet(which, dx_order, dy_order)
        rows = spectral.cheb_eval(self.sx, a, xi)        # (nxi, ny+1)
        return spectral.cheb_eval(self.sy, rows.T, y).T  # (nxi, nyv)

    def eval(self, which: str, eta, theta, deta_order: int = 0) -> np.ndarray:
        """Field (or its 1st/2nd eta-derivative) at (eta, theta).

        Angular derivatives come via eval_xy jets in y; this helper only
        chains the radial map (d/d eta = (1/eta') d/d xi).
        """
        eta = np.atleast_1d(np.asarray(eta, float))
        theta = np.broadcast_to(np.asarray(theta, float), eta.shape)
        m = self.radial_map
        xi = m.xi_of_eta(eta)
        y = np.cos(2.0 * theta)
        if deta_order == 0:
            return self.eval_xy(which, xi, y)
        ep, epp = m.deta(xi), m.d2eta(xi)
        g_x = self.eval_xy(which, xi, y, dx_order=1)
        if deta_order == 1:
            return g_x / ep
        if deta_order == 2:
            g_xx = self.eval_xy(which, xi, y, dx_order=2)
            return g_xx / ep**2 - g_x * epp / ep**3
        raise ValueError("deta_order must be 0, 1 or 2")

    # -- resolution monitor ----------------------------------------------------

    def tail_ratios(self) -> dict[str, float]:
        """Largest of the last 3 Chebyshev coefficients over the largest,
        per field and direction (gate: <= 1e-11).  omega is measured on the
        raw field, not its correction about omega_inf q; its tails decay
        the same way."""
        out = {}
        for which in FIELDS:
            a = self.node_array(which)
            out[f"{which}_x"] = spectral.tail_ratio(a, axis=0)
            out[f"{which}_y"] = spectral.tail_ratio(a, axis=1)
        return out

    # -- I/O --------------------------------------------------------------------

    def save(self, path: str | Path) -> tuple[Path, Path]:
        path = Path(path)
        npz = path.with_suffix(".npz")
        js = path.with_suffix(".json")
        np.savez_compressed(
            npz, F=self.F, W=self.W, N=self.N,
            params=json.dumps(self._params_dict()))
        with js.open("w", encoding="ascii") as fh:
            json.dump({**self._params_dict(),
                       "observables": self.observables,
                       "gates": self.gates, "meta": self.meta},
                      fh, indent=1, sort_keys=True)
        return npz, js

    def _params_dict(self) -> dict:
        return {"eta0": self.eta0, "gamma": self.gamma,
                "omega_inf": self.omega_inf, "map_name": self.map_name,
                "map_params": self.map_params,
                "nx": self.nx, "ny": self.ny}

    @classmethod
    def load(cls, path: str | Path) -> "Solution":
        path = Path(path).with_suffix(".npz")
        with np.load(path, allow_pickle=False) as data:
            params = json.loads(str(data["params"]))
            sol = cls(eta0=params["eta0"], gamma=params["gamma"],
                      omega_inf=params["omega_inf"],
                      map_name=params["map_name"],
                      map_params=params["map_params"],
                      F=np.asarray(data["F"]), W=np.asarray(data["W"]),
                      N=np.asarray(data["N"]))
        js = path.with_suffix(".json")
        if js.exists():
            with js.open(encoding="ascii") as fh:
                side = json.load(fh)
            sol.observables = side.get("observables", {})
            sol.gates = side.get("gates", {})
            sol.meta = side.get("meta", {})
        return sol
