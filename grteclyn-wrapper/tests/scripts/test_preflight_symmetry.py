"""The launch preflight's checks for the inflation arms and symmetry-reduced boxes.

preflight.py (scripts/campaigns/wormhole_merger/) refuses, before a GPU is
touched, a consumer asked for something the plotfiles cannot give (the
full-metric areal radius or the neck/horizon record without their fields) and
a symmetry-reduced box whose data, centre or consumer do not respect its
mirror planes.  The last test runs its command line in static mode on a stand-in
binary, the way run_single.sh calls it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PREFLIGHT = (Path(__file__).resolve().parents[2]
             / "scripts" / "campaigns" / "wormhole_merger" / "preflight.py")


@pytest.fixture(scope="module")
def pf():
    spec = importlib.util.spec_from_file_location("whm_preflight", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["whm_preflight"] = mod
    spec.loader.exec_module(mod)
    return mod


PLOT_VARS = "chi K lapse shift1 shift2 shift3 h11 h12 h13 h22 h23 h33 A11 A12 A13 A22 A23 A33 phi Pi"
INFLATION = "--areal-radius --areal-full-metric --areal-min-radius 0.5 --neck-horizons --radii 40 60"


def full_box(**over) -> dict[str, str]:
    p = {"L": "512.0", "N1": "256", "N2": "256", "N3": "256", "center": "256.0 256.0 256.0",
         "lo_boundary": "1 1 1", "hi_boundary": "1 1 1", "isPeriodic": "0 0 0",
         "amr.plot_vars": PLOT_VARS, "wormhole_centerA": "0.0 0.0 0.0",
         "wormhole_momentumA": "0.0 0.0 0.0", "activate_extraction": "1",
         "extraction_center": "256.0 256.0 256.0"}
    p.update(over)
    return p


def octant(**over) -> dict[str, str]:
    p = full_box(L_full="512.0", N_full="256", center="0.0 0.0 0.0", lo_boundary="2 2 2",
                 extraction_center="0.0 0.0 0.0")
    for k in ("L", "N1", "N2", "N3"):
        p.pop(k)
    p.update(over)
    return p


# ------------------------------------------------------------- consumer flags
class TestConsumerFlags:
    def test_full_metric_with_its_fields_passes(self, pf):
        err, warn, s = pf.consumer_check(full_box(), INFLATION, True)
        assert err == [] and warn == []
        assert s["areal_radius"].startswith("full metric") and s["neck_horizons"]

    def test_full_metric_without_h22_is_refused(self, pf):
        p = full_box(**{"amr.plot_vars": "chi K lapse h11 A11 phi"})
        err, _, _ = pf.consumer_check(p, "--areal-radius --areal-full-metric", True)
        assert any("h22, h33" in e for e in err)

    def test_full_metric_alone_extracts_nothing(self, pf):
        err, _, _ = pf.consumer_check(full_box(), "--areal-full-metric", True)
        assert any("without --areal-radius" in e for e in err)

    def test_flat_radius_is_allowed_with_a_warning(self, pf):
        err, warn, s = pf.consumer_check(full_box(), "--areal-radius", True)
        assert err == [] and any("lower bound" in w for w in warn)
        assert s["areal_radius"].startswith("flat")

    def test_neck_horizons_needs_its_eight_fields(self, pf):
        p = full_box(**{"amr.plot_vars": "chi K lapse h22 h33 phi"})
        err, _, _ = pf.consumer_check(p, "--neck-horizons", True)
        assert any("--neck-horizons needs h11, A11" in e for e in err)

    def test_no_consumer_no_checks(self, pf):
        err, warn, s = pf.consumer_check(full_box(**{"amr.plot_vars": "chi"}), INFLATION, False)
        assert err == [] and warn == [] and not s["consume"]


# ---------------------------------------------------------------- the planes
class TestSymmetry:
    def test_full_box_has_no_planes(self, pf):
        err, warn, s = pf.symmetry_check(full_box())
        assert (err, warn, s["reflect"]) == ([], [], [])

    def test_octant_passes_and_names_its_full_box(self, pf):
        err, warn, s = pf.symmetry_check(octant())
        assert err == [] and warn == []
        assert s["reflect"] == ["x", "y", "z"]
        assert s["full_box"] == [512.0] * 3 and s["cells_fraction"] == 0.125

    def test_octant_from_L_and_N_reports_the_doubled_box(self, pf):
        p = octant(L="256.0", N1="128", N2="128", N3="128")
        for k in ("L_full", "N_full"):
            p.pop(k)
        assert pf.symmetry_check(p)[2]["full_box"] == [512.0] * 3

    @pytest.mark.parametrize("key,value,needle", [
        ("center", "128.0 0.0 0.0", "center"),
        ("wormhole_centerA", "0.0 0.0 5.0", "throat A sits off"),
        ("wormhole_momentumA", "0.1 0.0 0.0", "moves across"),
        ("extraction_center", "0.0 64.0 0.0", "extraction_center"),
        ("hi_boundary", "1 1 2", "UPPER face"),
    ])
    def test_asymmetric_octant_is_refused(self, pf, key, value, needle):
        err, _, _ = pf.symmetry_check(octant(**{key: value}))
        assert any(needle in e for e in err), err

    def test_a_second_throat_must_sit_on_the_planes(self, pf):
        p = octant(wormhole_throat_radius_B="2.0", wormhole_centerB="0.0 0.0 -8.0")
        err, _, _ = pf.symmetry_check(p)
        assert any("throat B sits off" in e for e in err)
        # a head-on pair along z on an x-y quadrant box is legitimate
        p = octant(lo_boundary="2 2 1", wormhole_throat_radius_B="2.0", wormhole_centerB="0.0 0.0 -8.0",
                   wormhole_centerA="0.0 0.0 8.0")
        assert pf.symmetry_check(p)[0] == []

    def test_consumer_must_reflect_exactly_the_params_planes(self, pf):
        planes = pf.symmetry_check(octant())[2]["reflect"]
        err, _, _ = pf.consumer_check(octant(), INFLATION, True, reflect=planes)
        assert any("--reflect names none" in e for e in err)
        err, _, _ = pf.consumer_check(octant(), INFLATION + " --reflect x y", True, reflect=planes)
        assert any("wrong domain" in e for e in err)
        err, _, _ = pf.consumer_check(full_box(), INFLATION + " --reflect x y z", True, reflect=[])
        assert any("make no plane" in e for e in err)
        err, _, _ = pf.consumer_check(octant(), INFLATION + " --reflect x y z", True, reflect=planes)
        assert err == []

    def test_star_scan_and_off_plane_frames_are_refused_on_an_octant(self, pf):
        planes = ["x", "y", "z"]
        args = INFLATION + " --reflect x y z"
        err, _, _ = pf.consumer_check(octant(), args + " --horizon-scan", True, reflect=planes)
        assert any("--horizon-scan" in e for e in err)
        err, _, _ = pf.consumer_check(octant(), args + " --frames-center 256 256 256", True, reflect=planes)
        assert any("--frames-center" in e for e in err)
        err, _, _ = pf.consumer_check(octant(), args + " --frames-center 0 0 0", True, reflect=planes)
        assert err == []


# ------------------------------------------------------------ the command line
class TestCommandLine:
    """preflight.py --mode static, as run_single.sh runs it: the consumer flags
    arrive in $WHM_CONSUME_ARGS; exit 0 passes, 1 refuses."""

    @staticmethod
    def _write(tmp_path, params: dict[str, str]):
        (tmp_path / "params.txt").write_text("".join(f"{k} = {v}\n" for k, v in params.items()))
        # a stand-in binary: every key's name appears in it, so the static
        # key check passes and only the checks under test decide
        (tmp_path / "fake.ex").write_bytes(b"\0".join(k.encode() for k in params) + b"\0")
        return str(tmp_path / "params.txt"), str(tmp_path / "fake.ex")

    def test_octant_inflation_launch_passes(self, pf, tmp_path, monkeypatch, capsys):
        params, exe = self._write(tmp_path, octant())
        monkeypatch.setenv("WHM_CONSUME_ARGS", INFLATION + " --reflect x y z --frames-center 0 0 0")
        code = pf.main(["--mode", "static", "--exe", exe, "--params", params, "--workdir", str(tmp_path / "w")])
        out = capsys.readouterr().out
        assert code == 0, out
        assert "mirror planes x y z" in out and "--reflect x y z" in out

    def test_octant_without_reflect_is_refused(self, pf, tmp_path, monkeypatch, capsys):
        params, exe = self._write(tmp_path, octant())
        monkeypatch.setenv("WHM_CONSUME_ARGS", INFLATION)
        code = pf.main(["--mode", "static", "--exe", exe, "--params", params, "--workdir", str(tmp_path / "w")])
        assert code == 1
        assert "REFUSED" in capsys.readouterr().out
