"""Shared pieces of the claims ledger: pack access and generic extractors.

An extractor is a function registered with @extractor that returns ONE float,
recomputed from the tracked pack (results/merger/campaign/...), never from the
untracked run tree -- so every check is reproducible from a clone.  Ledger rows
name the extractor and give its keyword arguments as JSON (claims.py).

Generic extractors live here; section modules (extract_<area>.py) register
their own with the same decorator.  Every extractor takes keyword arguments
only, and the run argument is a packed run NAME (resolved through
results/merger/analysis/pack_paths.py, so the pack layout can change freely).
"""

from __future__ import annotations

import functools
import pathlib
import re
import sys
from typing import Callable

import numpy as np

ARTICLE = pathlib.Path(__file__).resolve().parents[1]
REPO = ARTICLE.parents[2]
PACK = REPO / "results" / "merger"
sys.path.insert(0, str(PACK / "analysis"))
from pack_paths import find_run, iter_runs  # noqa: E402

EXTRACTORS: dict[str, Callable[..., float]] = {}


def extractor(fn: Callable[..., float]) -> Callable[..., float]:
    """Register fn under its own name.  Names must be unique across modules."""
    if fn.__name__ in EXTRACTORS:
        raise RuntimeError(f"extractor {fn.__name__} registered twice")
    EXTRACTORS[fn.__name__] = fn
    return fn


# ---------------------------------------------------------------- pack access
def run_dir(run: str) -> pathlib.Path:
    d = find_run(PACK, run)
    if d is None:
        raise LookupError(f"run {run!r} is not in the pack (results/merger/campaign)")
    return d


@functools.lru_cache(maxsize=256)
def stream(run: str, file: str) -> tuple[tuple[str, ...], np.ndarray]:
    """(column names, rows) of a packed .dat stream.  Names come from the last
    '#' line before the data; a header-less file gets c0, c1, ..."""
    path = run_dir(run) / file
    names: list[str] = []
    rows: list[list[float]] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                if not rows:
                    toks = line.lstrip("#").split()
                    # a prose comment has lower-case words and punctuation; a
                    # header is a list of identifiers
                    if toks and all(re.fullmatch(r"[A-Za-z_][\w\[\]().,:+-]*", t) for t in toks):
                        names = toks
                continue
            vals = line.split()
            if not vals:
                continue
            try:
                rows.append([float(v) for v in vals])
            except ValueError:
                continue
    if not rows:
        raise ValueError(f"{run}/{file}: no data rows")
    width = max(len(r) for r in rows)
    arr = np.full((len(rows), width), np.nan)
    for i, r in enumerate(rows):
        arr[i, : len(r)] = r
    if len(names) != width:
        names = [f"c{i}" for i in range(width)]
    return tuple(names), arr


def column(run: str, file: str, col: str | int) -> np.ndarray:
    names, arr = stream(run, file)
    if isinstance(col, int):
        return arr[:, col]
    if col not in names:
        raise KeyError(f"{run}/{file}: no column {col!r}; columns are {list(names)}")
    return arr[:, names.index(col)]


def window(run: str, file: str, col: str | int, tcol: str | int = 0,
           t0: float | None = None, t1: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    t = column(run, file, tcol)
    y = column(run, file, col)
    keep = np.isfinite(t) & np.isfinite(y)
    if t0 is not None:
        keep &= t >= t0
    if t1 is not None:
        keep &= t <= t1
    if not keep.any():
        raise ValueError(f"{run}/{file}:{col}: no finite rows in [{t0}, {t1}]")
    return t[keep], y[keep]


def params(run: str) -> dict[str, str]:
    """The packed evolution_params.txt of a run (key -> raw value)."""
    out: dict[str, str] = {}
    path = run_dir(run) / "evolution_params.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        body = line.split("#", 1)[0]
        m = re.match(r"\s*([A-Za-z_][\w.]*)\s*=(.*)$", body)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


# ---------------------------------------------------------------- generic extractors
@extractor
def param(run: str, key: str, index: int = 0) -> float:
    """A numeric parameter of a run (the index-th value of a list)."""
    return float(params(run)[key].split()[index].strip('"'))


@extractor
def value_at(run: str, file: str, col: str | int, t: float, tcol: str | int = 0) -> float:
    """col at time t (linear interpolation between samples)."""
    tt, y = window(run, file, col, tcol)
    if not tt[0] - 1e-9 <= t <= tt[-1] + 1e-9:
        raise ValueError(f"{run}/{file}: t = {t} outside [{tt[0]}, {tt[-1]}]")
    return float(np.interp(t, tt, y))


@extractor
def first(run: str, file: str, col: str | int, tcol: str | int = 0) -> float:
    return float(window(run, file, col, tcol)[1][0])


@extractor
def last(run: str, file: str, col: str | int, tcol: str | int = 0, back: float = 0.0) -> float:
    """col at the last time minus `back` (back = 0.5 is make_summary's 'last clean')."""
    tt, y = window(run, file, col, tcol)
    return float(np.interp(tt[-1] - back, tt, y))


@extractor
def last_time(run: str, file: str, tcol: str | int = 0) -> float:
    t = column(run, file, tcol)
    return float(t[np.isfinite(t)][-1])


@extractor
def extreme(run: str, file: str, col: str | int, kind: str = "min", tcol: str | int = 0,
            t0: float | None = None, t1: float | None = None, what: str = "value") -> float:
    """min/max of col over [t0, t1]; what = 'value' or 'time' (when it occurs)."""
    tt, y = window(run, file, col, tcol, t0, t1)
    i = int(np.argmin(y) if kind == "min" else np.argmax(y))
    return float(y[i] if what == "value" else tt[i])


@extractor
def first_time(run: str, file: str, col: str | int, op: str, threshold: float,
               tcol: str | int = 0, t0: float | None = None) -> float:
    """First time col op threshold holds (op one of < <= > >= ==)."""
    tt, y = window(run, file, col, tcol, t0)
    test = {"<": y < threshold, "<=": y <= threshold, ">": y > threshold,
            ">=": y >= threshold, "==": y == threshold}[op]
    if not test.any():
        raise ValueError(f"{run}/{file}:{col} never {op} {threshold}")
    return float(tt[int(np.argmax(test))])


@extractor
def slope(run: str, file: str, col: str | int, t0: float, t1: float, tcol: str | int = 0,
          log: bool = False) -> float:
    """Least-squares slope of col (or of ln col) against time over [t0, t1]."""
    tt, y = window(run, file, col, tcol, t0, t1)
    if log:
        y = np.log(y)
    return float(np.polyfit(tt, y, 1)[0])


@extractor
def count_runs(pattern: str) -> float:
    """How many packed runs have a name matching the regex."""
    rx = re.compile(pattern)
    return float(sum(1 for _, d in iter_runs(PACK) if rx.search(d.name)))


@extractor
def expr(formula: str, **terms: dict) -> float:
    """Arithmetic over other extractors: expr(formula="a/b", a={...}, b={...}),
    each term {"fn": name, <kwargs>}.  Only + - * / ** ( ) abs min max are allowed."""
    vals = {k: evaluate(v) for k, v in terms.items()}
    if not re.fullmatch(r"[\w\s+\-*/().,]*", formula):
        raise ValueError(f"formula {formula!r} has characters outside + - * / ( ) ,")
    return float(eval(formula, {"__builtins__": {}, "abs": abs, "min": min, "max": max}, vals))


def evaluate(spec: dict) -> float:
    """Run one extractor spec {"fn": name, **kwargs}."""
    spec = dict(spec)
    fn = spec.pop("fn")
    if fn not in EXTRACTORS:
        raise KeyError(f"no extractor {fn!r}")
    return EXTRACTORS[fn](**spec)
