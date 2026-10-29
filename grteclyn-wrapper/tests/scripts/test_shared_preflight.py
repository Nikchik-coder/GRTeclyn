"""Campaign-configured binary requirements for extended input tables."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "scripts" / "campaigns" / "lib" / "preflight.py"
CONFIG = ROOT / "scripts" / "campaigns" / "spinning_wormhole" / "preflight_campaign.json"


@pytest.fixture()
def pf():
    spec = importlib.util.spec_from_file_location("shared_preflight", PREFLIGHT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["shared_preflight"] = mod
    spec.loader.exec_module(mod)
    mod.apply_campaign_config(CONFIG)
    return mod


def _table(path: Path, ncomp: int, potential: bool = False) -> Path:
    lines = [
        "SPINBG_V1",
        "eta0 1.0",
        "n_x 2",
        "n_mu 2",
        "x_min -1.0",
        "x_max 1.0",
        f"num_components {ncomp}",
    ]
    if potential:
        lines.append("potential_coeffs 0.0 1.0")
    lines.append("END_HEADER")
    path.write_text("\n".join(lines) + "\n")
    return path


@pytest.mark.parametrize(("ncomp", "potential"), [(7, False), (6, True)])
def test_matter_table_is_refused_on_a_legacy_binary(pf, tmp_path, ncomp, potential):
    table = _table(tmp_path / "matter.spinbg", ncomp, potential)
    old = tmp_path / "main3d_old.ex"
    old.write_bytes(b"legacy")
    errors, checks = pf.header_binary_requirements_check(
        {"spinning_background_file": str(table)}, old, old.name)
    assert len(errors) == 1
    assert "compatible binary" in errors[0]
    assert checks[0]["triggered"] and not checks[0]["supported"]


def test_six_column_table_remains_backward_compatible(pf, tmp_path):
    table = _table(tmp_path / "old.spinbg", 6)
    old = tmp_path / "main3d_old.ex"
    old.write_bytes(b"legacy")
    errors, checks = pf.header_binary_requirements_check(
        {"spinning_background_file": str(table)}, old, old.name)
    assert errors == []
    assert not checks[0]["triggered"]


def test_matter_binary_accepts_the_extended_table(pf, tmp_path):
    table = _table(tmp_path / "matter.spinbg", 7, True)
    matter = tmp_path / "main3d_matter.ex"
    matter.write_bytes(b"potential_coeffs")
    errors, checks = pf.header_binary_requirements_check(
        {"spinning_background_file": str(table)}, matter, matter.name)
    assert errors == []
    assert checks[0]["supported"]
