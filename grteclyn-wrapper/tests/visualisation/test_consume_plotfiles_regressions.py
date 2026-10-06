"""Regressions for two silent failures in the plotfile consumer.

Both were found while wiring BinaryWormholeMerger into the campaign, and both
failed in the worst way available: they produced no output and no error, which
is indistinguishable from a run that has not written anything yet.
"""

from __future__ import annotations

import numpy as np
import pytest

from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.shell import (
    _extract_shell_field_stats,
)
from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.plotfiles import (
    _iter_plotfile_dirs,
)


def _make_plotfile(root, name):
    d = root / name
    d.mkdir()
    (d / "Header").write_text("plotfile")
    return d


class TestPlotfileDiscovery:
    """Discovery used a hard-coded list of four example prefixes, so every
    plotfile a new example wrote was skipped."""

    def test_finds_plotfiles_regardless_of_example_name(self, tmp_path):
        for name in (
            "BinaryWormholePlt00000",   # the one that was invisible
            "WormholePlt00010",
            "SupportedWormholePlt00002",
            "RadialRecipePlt007",
            "plt000123",
            "SomeFutureExamplePlt00001",
        ):
            _make_plotfile(tmp_path, name)
        found = {p.rsplit("/", 1)[-1] for p in _iter_plotfile_dirs(str(tmp_path))}
        assert len(found) == 6

    def test_excludes_checkpoints_and_non_plotfiles(self, tmp_path):
        _make_plotfile(tmp_path, "BinaryWormholePlt00000")
        # Checkpoints carry a Header too; only the trailing-digit *Plt* shape
        # keeps them out.
        _make_plotfile(tmp_path, "BinaryWormholeChk00000")
        _make_plotfile(tmp_path, "PltButNoTrailingDigits")
        (tmp_path / "small_data").mkdir()
        found = {p.rsplit("/", 1)[-1] for p in _iter_plotfile_dirs(str(tmp_path))}
        assert found == {"BinaryWormholePlt00000"}

    def test_directory_without_header_is_not_a_plotfile(self, tmp_path):
        (tmp_path / "BinaryWormholePlt00001").mkdir()  # no Header
        assert _iter_plotfile_dirs(str(tmp_path)) == []


class _FakeDS:
    """Mimics the one yt behaviour that matters here: a request for a single
    field comes back as a flat per-point array, not a length-1 sequence."""

    def __init__(self, values):
        self._values = values
        self.domain_left_edge = np.array([0.0, 0.0, 0.0])
        self.domain_right_edge = np.array([32.0, 32.0, 32.0])
        self.field_list = [("boxlib", f) for f in values]

    def find_field_values_at_points(self, fields, pts):
        cols = [np.full(len(pts), self._values[f[1]]) for f in fields]
        return cols[0] if len(cols) == 1 else cols


class TestShellExtractionFieldCount:
    """`zip(fields, vals)` paired the lone field name with a single scalar, so
    every radius failed the sample-count test and the caller was told the
    plotfile had no valid samples anywhere."""

    CENTER = [16.0, 16.0, 16.0]
    RADII = [8.0, 10.0]

    def test_single_field_produces_stats(self):
        ds = _FakeDS({"chi": 0.75})
        out = _extract_shell_field_stats(ds, self.RADII, 16, self.CENTER, ["chi"])
        assert out, "single-field extraction produced nothing"
        for r in self.RADII:
            mean, lo, hi = out[f"chi_mean_R{r:g}"]
            assert mean == pytest.approx(0.75)
            assert lo == pytest.approx(0.75)
            assert hi == pytest.approx(0.75)

    def test_single_field_agrees_with_multi_field(self):
        ds = _FakeDS({"chi": 0.75, "phi": -0.25})
        one = _extract_shell_field_stats(ds, self.RADII, 16, self.CENTER, ["chi"])
        many = _extract_shell_field_stats(
            ds, self.RADII, 16, self.CENTER, ["chi", "phi"]
        )
        for r in self.RADII:
            assert one[f"chi_mean_R{r:g}"] == many[f"chi_mean_R{r:g}"]

    def test_multi_field_keeps_fields_distinct(self):
        ds = _FakeDS({"chi": 0.75, "phi": -0.25})
        out = _extract_shell_field_stats(
            ds, self.RADII, 16, self.CENTER, ["chi", "phi"]
        )
        assert out["chi_mean_R8"][0] == pytest.approx(0.75)
        assert out["phi_mean_R8"][0] == pytest.approx(-0.25)
