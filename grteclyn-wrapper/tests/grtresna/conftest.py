"""Shared fixtures for tests/grtresna."""

import pytest


@pytest.fixture(autouse=True)
def _isolate_aligned_solve_rail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the campaign env's alignment rail out of test fixtures.

    Campaign launchers export GRTRESNA_REQUIRE_ALIGNED_SOLVE=1 and then run
    this directory as their preflight pytest gate, so any fixture that builds
    an (intentionally) old-style solve grid would raise instead of warn.
    Tests that exercise the rail itself set or delete the variable explicitly
    via monkeypatch during the test body and are unaffected.
    """
    monkeypatch.delenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", raising=False)
