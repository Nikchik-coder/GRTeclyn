"""Stationary Einstein--scalar solutions, search and independent validation.

spinning_wormhole holds the massless rotating backgrounds; matter_equations
extends them to interacting phantom and canonical fields; railgun holds
regular-centre scalar rings. The shared numerical algorithms live in
grteclyn_stationary.numerics. Commands and workflows compose these models;
search proposes candidates and independent checks qualify their solutions.

Evolution, analysis and plotting can consume this package. Importing it
starts no solver and does not initialise JAX.
"""
