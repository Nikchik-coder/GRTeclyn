"""The consumer on a symmetry-reduced (octant) run, and the inflation extractions.

An octant run (the params' lo_boundary = 2 2 2) holds [0, L]^3 of a box that is
mirror-symmetric about x = y = z = 0.  Every extraction that samples round the
centre must see the same numbers as on the full box: sphere samplers fold their
points across the planes, frames mirror the simulated quadrant into the full
plane.  Also the pieces the inflation arms rely on: the t = 0 colour lock, the
full-metric areal radius, and the neck/horizon tracker.
"""

from __future__ import annotations

import numpy as np
import pytest
import yt
from scipy.optimize import brentq

from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction import (
    neck_horizons as nh,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.areal import (
    _extract_areal_radius_min,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.scalar_modes import (
    extract_scalar_modes,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.symmetry import (
    fold_points,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames import zlim as zlim_mod
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames.mirror import (
    mirrored_window,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.frames.zlim import (
    _T0_KEY,
    _lock_frame_zlims_from_plotfile,
    _resolve_plot_zlim,
)

yt.funcs.mylog.setLevel(40)


def _even(x, y, z):
    """Even in x, y and z separately (exactly, in floating point)."""
    r = np.sqrt(x * x + y * y + z * z)
    return np.cos(0.3 * r) + 0.01 * (x * x + 2.0 * y * y) + 0.5


def _grid(lo, hi, n, funcs):
    edges = np.linspace(lo, hi, n + 1)
    c = 0.5 * (edges[:-1] + edges[1:])
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    data = {name: f(X, Y, Z) for name, f in funcs.items()}
    return yt.load_uniform_grid(data, (n, n, n), length_unit=1.0,
                                bbox=np.array([[lo, hi]] * 3, dtype=float))


# --------------------------------------------------------------------- folding
class TestFoldPoints:
    def test_folds_only_the_named_axes(self):
        x, y, z = np.array([-3.0, 2.0]), np.array([-1.0, -4.0]), np.array([5.0, -6.0])
        fx, fy, fz = fold_points(x, y, z, (0.0, 0.0, 0.0), ["x", "z"])
        assert fx.tolist() == [3.0, 2.0]
        assert fy.tolist() == [-1.0, -4.0]
        assert fz.tolist() == [5.0, 6.0]

    def test_folds_about_the_centre_not_the_origin(self):
        fx, _, _ = fold_points(np.array([7.0, 13.0]), np.zeros(2), np.zeros(2), (10.0, 0.0, 0.0), ["x"])
        assert fx.tolist() == [13.0, 13.0]


class _SphereDS:
    """Enough of a yt dataset for the scalar-mode sampler: phi and Pi are
    functions of position, the domain is a box."""

    def __init__(self, lo, hi, phi, pi):
        self.domain_left_edge = np.array([lo] * 3, dtype=float)
        self.domain_right_edge = np.array([hi] * 3, dtype=float)
        self.field_list = [("boxlib", "phi"), ("boxlib", "Pi")]
        self._phi, self._pi = phi, pi

    def find_field_values_at_points(self, fields, pts):
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        return [self._phi(x, y, z), self._pi(x, y, z)]


class TestScalarModesOnAnOctant:
    """Without the fold the octant sampler keeps 1/8 of each sphere, and the
    renormalised projection onto l >= 1 picks up the octant's own shape."""

    PHI = staticmethod(lambda x, y, z: 1.0 / (1.0 + np.sqrt(x * x + y * y + z * z)))
    PI = staticmethod(lambda x, y, z: 0.1 * np.exp(-0.01 * (x * x + y * y + z * z)))

    def _modes(self, lo, reflect):
        ds = _SphereDS(lo, 64.0, self.PHI, self.PI)
        phi, pi, flux = extract_scalar_modes(ds, radii=[20.0], n_points=48, center=(0.0, 0.0, 0.0),
                                             ells=(0, 1, 2), reflect=reflect)
        return phi, pi, flux

    def test_folded_octant_equals_full_sphere(self):
        full = self._modes(-64.0, None)
        octant = self._modes(0.0, ["x", "y", "z"])
        for l in (0, 1, 2):
            for m in range(-l, l + 1):
                assert octant[0][l][0][m] == pytest.approx(full[0][l][0][m], abs=1e-12)
                assert octant[1][l][0][m] == pytest.approx(full[1][l][0][m], abs=1e-12)
        assert octant[2][0] == pytest.approx(full[2][0], rel=1e-12)

    def test_unfolded_octant_is_wrong(self):
        full = self._modes(-64.0, None)
        octant = self._modes(0.0, None)
        l1 = max(abs(v) for v in octant[0][1][0].values())
        assert l1 > 1e-2 * abs(full[0][0][0][0])  # a monopole reads as a dipole


# --------------------------------------------------------------------- frames
@pytest.fixture(scope="module")
def boxes():
    """The same even field on the full box [-16, 16]^3 and its octant [0, 16]^3."""
    return _grid(-16.0, 16.0, 32, {"chi": _even}), _grid(0.0, 16.0, 16, {"chi": _even})


class TestMirroredFrames:
    """A frame of the octant, mirrored, is the frame of the full box."""

    def test_octant_frame_equals_full_frame(self, boxes):
        full, octant = boxes
        arr, extent, plane = mirrored_window(octant, "chi", "z", 0.0, 32.0, (0.0, 0.0, 0.0), ["x", "y", "z"])
        n = arr.shape[0]
        slc = yt.SlicePlot(full, "z", ("stream", "chi"), center=full.arr([0.0, 0.0, 0.0], "code_length"),
                           buff_size=(n, n))
        slc.set_width((32.0, "code_length"))
        ref = np.asarray(slc.frb[("stream", "chi")], dtype=float)
        assert arr.shape == ref.shape
        assert extent == [-16.0, 16.0, -16.0, 16.0]
        assert plane == 0.0
        np.testing.assert_allclose(arr, ref, rtol=0.0, atol=1e-12)

    def test_full_width_pixel_count_as_the_full_box(self, boxes):
        _full, octant = boxes
        arr, _, _ = mirrored_window(octant, "chi", "z", 0.0, 32.0, (0.0, 0.0, 0.0), ["x", "y", "z"])
        assert arr.shape[0] == arr.shape[1] and arr.shape[0] % 2 == 0

    def test_odd_parity_field_is_refused(self, boxes):
        _full, octant = boxes
        with pytest.raises(ValueError, match="odd parity"):
            mirrored_window(octant, "shift1", "z", 0.0, 32.0, (0.0, 0.0, 0.0), ["x", "y", "z"])

    def test_nothing_to_mirror(self, boxes):
        _full, octant = boxes
        assert mirrored_window(octant, "chi", "z", 0.0, 32.0, (0.0, 0.0, 0.0), []) is None
        # the slice normal is not an in-plane axis
        assert mirrored_window(octant, "chi", "z", 0.0, 32.0, (0.0, 0.0, 0.0), ["z"]) is None


# --------------------------------------------------------------- t = 0 colours
class TestT0ColourLock:
    CFG = {"zlim": (0.995, 1.005), "cmap": "viridis", "label": "lapse"}

    def test_t0_lock_beats_auto_and_preset(self):
        zl = {"lapse": [0.397, 0.997], _T0_KEY: ["lapse"]}
        win = np.linspace(0.2, 1.0, 100)
        got = _resolve_plot_zlim("lapse", win, self.CFG, auto_zlim=True, frame_zlims=zl, use_global_zlim=False)
        assert got == (0.397, 0.997)

    def test_other_fields_keep_their_scale(self):
        zl = {"lapse": [0.397, 0.997], _T0_KEY: ["lapse"]}
        got = _resolve_plot_zlim("K", np.linspace(-1e-3, 1e-3, 100), {"zlim": (-5e-4, 5e-4)},
                                 auto_zlim=True, frame_zlims=zl, use_global_zlim=False)
        assert got != (0.397, 0.997)

    def test_lock_takes_min_max_and_skips_flat_fields(self, monkeypatch):
        ds = _grid(-8.0, 8.0, 16, {"lapse": lambda x, y, z: 0.4 + 0.6 * np.tanh(np.sqrt(x * x + y * y + z * z)),
                                     "K": lambda x, y, z: 0.0 * x})
        monkeypatch.setattr(zlim_mod.yt, "load", lambda _p: ds)
        args = {"frames_axis": "z", "frames_zoom": 16.0, "frames_center": [0.0, 0.0, 0.0],
                "frames_coord": 0.0, "frames_corner": False}
        got = _lock_frame_zlims_from_plotfile("Plt00000", args, t0_minmax_fields=["lapse", "K"])
        assert got[_T0_KEY] == ["lapse"]
        assert "K" not in got
        lo, hi = got["lapse"]
        # the z = 0.5 layer of cells: nearest (0.5, 0.5), farthest (7.5, 7.5)
        assert lo == pytest.approx(0.4 + 0.6 * np.tanh(np.sqrt(0.75)), rel=1e-12)
        assert hi == pytest.approx(0.4 + 0.6 * np.tanh(np.sqrt(2 * 7.5**2 + 0.25)), rel=1e-12)

    def test_lock_on_an_octant_equals_the_full_box(self, monkeypatch):
        f = {"lapse": lambda x, y, z: 0.4 + 0.6 * np.tanh(0.3 * np.sqrt(x * x + y * y + z * z))}
        full, octant = _grid(-16.0, 16.0, 32, f), _grid(0.0, 16.0, 16, f)
        args = {"frames_axis": "z", "frames_zoom": 32.0, "frames_center": [0.0, 0.0, 0.0],
                "frames_coord": 0.0, "frames_corner": False}
        monkeypatch.setattr(zlim_mod.yt, "load", lambda _p: full)
        want = _lock_frame_zlims_from_plotfile("P", args, t0_minmax_fields=["lapse"])
        monkeypatch.setattr(zlim_mod.yt, "load", lambda _p: octant)
        got = _lock_frame_zlims_from_plotfile("P", dict(args, reflect=["x", "y", "z"]),
                                              t0_minmax_fields=["lapse"])
        assert got["lapse"] == pytest.approx(want["lapse"], abs=1e-12)


# ------------------------------------------------------- the throat's geometry
A, R0 = 2.0, 3.0  # the throat: areal radius A at coordinate radius R0


def _R(r):
    return A + (r - R0) ** 2 / (2.0 * A)


def _throat(K0=0.0, h=1.0, lo=-8.0, n=64, with_h=True):
    """A spherical throat: R = r sqrt(h/chi) has its minimum A at r = R0."""
    def rr(x, y, z):
        return np.sqrt(x * x + y * y + z * z)
    f = {
        "chi": lambda x, y, z: h * (rr(x, y, z) / _R(rr(x, y, z))) ** 2,
        "K": lambda x, y, z: K0 + 0.0 * x,
        "lapse": lambda x, y, z: 1.0 + 0.0 * x,
        "h11": lambda x, y, z: 1.0 / h**2 + 0.0 * x,
        "A11": lambda x, y, z: 0.0 * x,
        "phi": lambda x, y, z: 0.0 * x,
    }
    if with_h:
        f["h22"] = lambda x, y, z: h + 0.0 * x
        f["h33"] = lambda x, y, z: h + 0.0 * x
    return _grid(lo, -lo, n, f)


class TestFullMetricArealRadius:
    def test_full_metric_reads_the_throat(self):
        ds = _throat(h=1.44)  # chi = 1.44 r^2/R^2, h22 = h33 = 1.44
        full, r_full = _extract_areal_radius_min(ds, center=(0.0, 0.0, 0.0), min_radius=0.5, full_metric=True)
        flat, _ = _extract_areal_radius_min(ds, center=(0.0, 0.0, 0.0), min_radius=0.5)
        assert full == pytest.approx(A, rel=3e-3)
        assert flat == pytest.approx(full / 1.2, rel=1e-9)  # r/sqrt(chi) misses sqrt(h22)
        assert r_full == pytest.approx(R0, abs=0.2)

    def test_full_metric_refuses_a_plotfile_without_h(self):
        ds = _throat(with_h=False)
        with pytest.raises(KeyError, match="h22"):
            _extract_areal_radius_min(ds, center=(0.0, 0.0, 0.0), min_radius=0.5, full_metric=True)
        flat, _ = _extract_areal_radius_min(ds, center=(0.0, 0.0, 0.0), min_radius=0.5)
        assert flat == pytest.approx(A, rel=3e-3)


class TestNeckAndHorizons:
    def test_static_throat_is_its_own_double_horizon(self):
        # K = 0: both expansions vanish at the neck (Shinkai-Hayward's
        # degenerate double trapping horizon), so both horizons sit there
        row, x_neck = nh.neck_horizons_row(_throat(), (0.0, 0.0, 0.0), None)
        dx = 16.0 / 64
        assert x_neck == pytest.approx(R0, abs=0.2)
        assert row[2] == pytest.approx(A, rel=3e-3)          # R_neck, half a cell off the minimum
        assert row[6] == pytest.approx(0.0, abs=1e-12)       # rate: K = 0
        assert row[9] == pytest.approx(x_neck, abs=dx) and row[13] == pytest.approx(x_neck, abs=dx)
        assert row[10] == pytest.approx(A, rel=3e-3) and row[14] == pytest.approx(A, rel=3e-3)

    def test_expanding_throat_is_bracketed_by_its_horizons(self):
        K0 = -0.3  # K_q = 2 K0/3 < 0: both expansions positive at the neck
        row, x_neck = nh.neck_horizons_row(_throat(K0=K0), (0.0, 0.0, 0.0), R0)
        x_hl, x_hk = row[9], row[13]
        assert x_hl < x_neck < x_hk
        assert row[6] == pytest.approx(-K0 / 3.0, rel=1e-9)  # rate = -(K - K_ss)/2
        # theta = 0 where 2 |dR/dl| / R = -K_q, dR/dl = (r - R0)/A * r/R
        g = lambda r: 2.0 * abs((r - R0) / A * r / _R(r)) / _R(r) + 2.0 * K0 / 3.0
        r_l, r_k = brentq(g, 1.0, R0 - 1e-9), brentq(g, R0 + 1e-9, 7.0)
        dx = 16.0 / 64
        assert x_hl == pytest.approx(r_l, abs=dx) and x_hk == pytest.approx(r_k, abs=dx)

    def test_tracker_ignores_an_inner_dip(self):
        x = np.linspace(0.05, 10.0, 2000)
        R = _R(x) - 3.0 * np.exp(-(((x - 0.6) / 0.15) ** 2))  # the compactified end's fiction
        assert x[nh._find_neck(x, R, None)] == pytest.approx(0.6, abs=0.05)
        assert x[nh._find_neck(x, R, R0)] == pytest.approx(R0, abs=0.01)

    def test_refuses_a_plotfile_without_its_fields(self):
        with pytest.raises(KeyError, match="h22"):
            nh.neck_horizons_row(_throat(with_h=False), (0.0, 0.0, 0.0), None)
