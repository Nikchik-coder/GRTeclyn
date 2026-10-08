"""Readers for the packed files: evolution_params.txt and the .dat streams."""

from __future__ import annotations

import pathlib
import re

import numpy as np


def parse_params(path: pathlib.Path) -> dict[str, str]:
    """AMReX ParmParse-style: '#' comments, 'key = value', '\\' continuation,
    last definition wins.  Lines whose key contains blanks are not keys."""
    out: dict[str, str] = {}
    pending = ""
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.endswith("\\"):
            pending += line[:-1] + " "
            continue
        line = pending + line
        pending = ""
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if not k or re.search(r"\s", k):
            continue
        out[k] = v.strip()
    return out


def read_stream(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    """(time, the other columns) of a whitespace .dat with '#' header lines."""
    rows = [line.split() for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")]
    if not rows:
        return np.empty(0), np.empty((0, 0))
    a = np.array([[float(x) for x in r] for r in rows])
    return a[:, 0], a[:, 1:]


def read_columns(path: pathlib.Path) -> dict[str, np.ndarray]:
    """A .dat stream as {column name: values}; the names are those of the last
    '#' line that mentions 'time'."""
    names = None
    with path.open() as fh:
        for line in fh:
            if line.startswith("#") and "time" in line:
                names = line.lstrip("#").split()
    data = np.loadtxt(path)
    return {n: data[:, i] for i, n in enumerate(names)}
