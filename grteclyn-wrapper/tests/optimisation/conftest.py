"""Controlled script entry points and numerical doubles for workflow tests."""
import importlib
import sys

import pytest


@pytest.fixture
def command():
    def load(name):
        return importlib.import_module(f'grteclyn_wrapper.optimisation.commands.{name}')
    return load


@pytest.fixture
def invoke(monkeypatch):
    def call(module, *args):
        monkeypatch.setattr(sys, 'argv', [module.__name__, *map(str, args)])
        return module.main()
    return call
