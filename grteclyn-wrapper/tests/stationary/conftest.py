"""Controlled script entry points and numerical doubles for workflow tests."""
import importlib
import os
import sys

import pytest


@pytest.fixture
def cuda_device():
    """GPU regressions run only in an explicitly selected CUDA environment."""
    if os.environ.get('JAX_PLATFORMS') != 'cuda':
        pytest.skip('requires explicit JAX_PLATFORMS=cuda')
    from grteclyn_stationary.numerics.device import configure_jax
    jax = configure_jax()
    assert all(device.platform == 'gpu' for device in jax.devices())


@pytest.fixture
def command():
    def load(name):
        if name in {'pipeline', 'compare_backgrounds'}:
            return importlib.import_module(f'grteclyn_workflows.campaigns.stationary.{name}')
        return importlib.import_module(f'grteclyn_stationary.commands.{name}')
    return load


@pytest.fixture
def invoke(monkeypatch):
    def call(module, *args):
        monkeypatch.setattr(sys, 'argv', [module.__name__, *map(str, args)])
        return module.main()
    return call
