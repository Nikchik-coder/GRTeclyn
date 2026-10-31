"""Stationary wormhole optimisation and independent numerical validation.

Physics lives in matter_equations, potentials and exoticity; solver contains
physics-independent numerics. commands dispatches workflows and search;
checks and derivations test the equations independently. See README.md for
the search flow, output meanings and runnable module names.

This package reads the published spinning-wormhole solver, never the reverse.
Its own visualisation package is the only allowed external importer.
Importing optimisation starts no solver and does not initialise JAX.
"""
