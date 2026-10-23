#!/usr/bin/env python3
"""One report on a Bondi resolution study: progress, constraint orders, and the motion against the paper.

Studies (members N 128 / 192 / 256; a member that has not started is listed and skipped):

  pair  rkfix_pair_d10_L64_N{n}_lev0_t200, against the paper's runaway_pair_d10_L64_N{n}_lev0
  lone  rkfix_lone_m_L64_N{n}_lev0_t200 (the negative-mass star 5 units off centre), against the paper's
        control_lone_phantom_L64_N128_lev0
Runs are looked up in runs/bondi/staging/ and then in its numbered groups (runs/bondi/NN_*/), the paper's v1 cells in
their archive (runs/bondi/00_archive/superseded_2026-10-23/results_campaign/, since 2026-10-23) and its groups.

Sections:
  1. Runs: t, stop time, speed (two reads --speed-window seconds apart), ETA in hours and Moscow time, minutes since
     the last write (the runs may live on another node; the data are on the shared disk), NaN lines in run.log, and
     this node's scratch.
  2. Orders p = ln(e1/e2) / ln(N2/N1) of the interior norms (constraint_norms.dat cols 18-19, r <= 24), consecutive
     members, read off the last row at or before each time.
  3. pair: Delta X (eq. mid), the barycentre separation d, the change of the proper core distance, and the
     acceleration a (twice the quadratic coefficient of X(t) fitted over 5 <= t <= T, eq. fit, T the last sample
     shared with the paper's runs), each per N against the paper's run at the same N; Q = (q1 - q2) / (q2 - q3)
     with the order it implies (Q 2.86 at order 2, 5.94 at order 4); the N 256 values with the N 192 - 256
     difference as the error bar, as the paper quotes Delta X(200) = 3.00 +- 0.01 and a = (1.55 +- 0.01) e-4.
     lone: the largest shift of the star's core and barycentre on any axis over t' <= t, per N and in the paper's
     N 128 control (its text: core <= 1.8e-3, barycentre 1.3e-2 over t <= 200), with the order between members.
Times default to 10 / 20 / 50 / 100 / 150 / 200 up to the time every started member has reached, plus that time.
Motion quantities use the last plotfile sample (every 0.8) at or before each time that every series shares.

Usage (from the repo root, with the wrapper's venv):
  study_report.py [--study pair|lone] [--times 10 20 50] [--speed-window 60]
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

RUNS = Path("runs/bondi")
PAPER = Path("runs/bondi/00_archive/superseded_2026-10-23/results_campaign")  # the v1 cells, archived 2026-10-23
NN = (128, 192, 256)
STUDIES = {
    "pair": ("rkfix_pair_d10_L64_N{n}_lev0_t200/bondi_sg_pair_pm_eqm_w075",
             {n: f"runaway_pair_d10_L64_N{n}_lev0" for n in NN}),
    "lone": ("rkfix_lone_m_L64_N{n}_lev0_t200/bondi_sg_single_m_w07603",
             {128: "control_lone_phantom_L64_N128_lev0"}),
}
DEFAULT_TIMES = (10.0, 20.0, 50.0, 100.0, 150.0, 200.0)
FIT_START = 5.0
SCRATCH = Path("/tmp/grteclyn_scratch")
MSK = dt.timezone(dt.timedelta(hours=3))


def locate(root: Path, rel: str) -> Path:
    """A run or packed cell by name, wherever it is filed: staging/ while live, a numbered group after close-out."""
    for cand in (root / "staging" / rel, root / rel, *sorted(root.glob(f"*/{rel}"))):
        if cand.exists():
            return cand
    return root / "staging" / rel


def find(d: Path, name: str) -> Path:
    """A run dir keeps data/ and small_data/; a packed paper cell holds every file flat."""
    for cand in (d / "data" / name, d / "small_data" / name, d / name):
        if cand.is_file():
            return cand
    return d / "data" / name


def load(path: Path) -> np.ndarray | None:
    if not path.is_file():
        return None
    rows = [l.split() for l in path.read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not rows:
        return None
    widths = [len(r) for r in rows]
    width = max(set(widths), key=widths.count)
    return np.array([r for r in rows if len(r) == width], dtype=float)


def last_time(path: Path) -> float | None:
    if not path.is_file():
        return None
    with path.open("rb") as fh:
        fh.seek(0, 2)
        fh.seek(max(fh.tell() - 4096, 0))
        lines = [l for l in fh.read().decode(errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
    return float(lines[-1].split()[0]) if lines else None


def stop_time(member: Path) -> float | None:
    p = member / "params.txt"
    m = re.search(r"^\s*stop_time\s*=\s*([0-9.eE+-]+)", p.read_text(), re.M) if p.is_file() else None
    return float(m.group(1)) if m else None


def nan_lines(member: Path) -> int | None:
    log = member / "run.log"
    if not log.is_file():
        return None
    with log.open(errors="ignore") as fh:
        return sum(1 for l in fh if "nan" in l.lower() and "nan_autopsy" not in l)


def order(e1, e2, n1, n2) -> float | None:
    if e1 is None or e2 is None or e1 * e2 <= 0:
        return None
    return math.log(e1 / e2) / math.log(n2 / n1)


def q_order(q: float, ns: tuple[int, int, int]) -> float | None:
    """Order p with (n1^-p - n2^-p) / (n2^-p - n3^-p) = Q (bisection)."""
    n1, n2, n3 = ns
    f = lambda p: (n1 ** -p - n2 ** -p) / (n2 ** -p - n3 ** -p) - q
    lo, hi = 0.05, 12.0
    if not math.isfinite(q) or f(lo) * f(hi) > 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(lo) * f(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def fmt(v, spec: str) -> str:
    return "–" if v is None or not math.isfinite(v) else format(v, spec)


def table(head: list[str], rows: list[list[str]]) -> None:
    print("| " + " | ".join(head) + " |")
    print("|---" * len(head) + "|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    print()


def runs_section(members: dict[int, Path], window: float) -> None:
    files = {n: find(m, "collapse_diagnostics.dat") for n, m in members.items()}
    t0 = {n: last_time(f) for n, f in files.items()}
    if window > 0:
        time.sleep(window)
    t1 = {n: last_time(f) for n, f in files.items()}
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for n, m in members.items():
        stop = stop_time(m)
        if t1[n] is None:
            rows.append([f"N {n}", "not started (solving or queued)", fmt(stop, "g"), "–", "–", "–", "–"])
            continue
        age = (now.timestamp() - files[n].stat().st_mtime) / 60
        speed = (t1[n] - t0[n]) / window * 3600 if window > 0 and t0[n] is not None else None
        done = stop is not None and t1[n] >= stop - 1e-6
        if done:
            eta = f"done {dt.datetime.fromtimestamp(files[n].stat().st_mtime, MSK):%H:%M} MSK"
        elif speed:
            hours = (stop - t1[n]) / speed
            eta = f"{hours:.1f} h, {now.astimezone(MSK) + dt.timedelta(hours=hours):%H:%M} MSK"
        else:
            eta = "–"
        state = "done" if done else ("running" if age < 10 else f"no write for {age:.0f} min")
        rows.append([f"N {n}", f"{t1[n]:.2f} ({state})", fmt(stop, "g"), fmt(speed, ".1f"), eta,
                     f"{age:.1f}", str(nan_lines(m))])
    print(f"## Runs ({now.astimezone(MSK):%H:%M} MSK)\n")
    table(["member", "t", "stop", "u/h", "ETA", "min since write", "NaN lines"], rows)
    entries = sorted(SCRATCH.iterdir()) if SCRATCH.is_dir() else []
    free = shutil.disk_usage(SCRATCH if SCRATCH.is_dir() else "/tmp").free / 2**30
    if entries:
        sizes = subprocess.run(["du", "-sh", *map(str, entries)], capture_output=True, text=True).stdout
        listing = "; ".join(f"{Path(p).name} {s}" for s, p in (l.split("\t") for l in sizes.splitlines()))
    else:
        listing = "empty"
    print(f"Scratch on this node ({free:.0f}G free): {listing}")
    print("(Runs on another node: its scratch is not listed here.)\n")


def orders_section(members: dict[int, Path], times: list[float]) -> None:
    norms = {n: load(find(m, "constraint_norms.dat")) for n, m in members.items()}
    ns = [n for n in members if norms[n] is not None]
    if len(ns) < 2:
        print("## Orders\n\nFewer than two members have data.\n")
        return

    def at(n, t, col):
        tab = norms[n]
        if tab[-1, 0] + 1e-9 < t or tab.shape[1] <= col:  # binaries before 8d0771d4 lack the interior norm
            return None
        return tab[max(np.searchsorted(tab[:, 0], t + 1e-9, side="right") - 1, 0), col]

    pairs = " / ".join(f"{a}→{b}" for a, b in zip(ns, ns[1:]))
    print(f"## Orders, interior r ≤ 24 (N {pairs})\n")
    rows = []
    for name, col in (("Ham L0", 17), ("Mom L0", 18)):
        cells = []
        for t in times:
            v = [at(n, t, col) for n in ns]
            cells.append(" / ".join(fmt(order(v[i], v[i + 1], ns[i], ns[i + 1]), ".1f") for i in range(len(ns) - 1)))
        rows.append([name, *cells])
    table(["", *[f"t {t:g}" for t in times]], rows)


def shared_samples(tabs: list[np.ndarray]) -> np.ndarray:
    common = set(np.round(tabs[0][:, 0], 3))
    for tab in tabs[1:]:
        common &= set(np.round(tab[:, 0], 3))
    return np.array(sorted(common))


def row_at(tab: np.ndarray, s: float) -> np.ndarray:
    return tab[int(np.argmin(abs(tab[:, 0] - s)))]


def snap(samples: np.ndarray, times: list[float]) -> list[float]:
    out = []
    for t in times:
        below = samples[samples <= t + 1e-6]
        if below.size and float(below[-1]) not in out:
            out.append(float(below[-1]))
    return out


def pair_section(members: dict[int, Path], paper: dict[int, Path], times: list[float]) -> None:
    new = {n: (load(find(m, "sector_barycenters.dat")), load(find(m, "sector_dynamics.dat")))
           for n, m in members.items()}
    ns = [n for n in members if new[n][0] is not None and new[n][1] is not None and n in paper]
    if not ns:
        print("## Motion\n\nNo member has barycentres yet.\n")
        return
    old = {n: (load(find(paper[n], "sector_barycenters.dat")), load(find(paper[n], "sector_dynamics.dat")))
           for n in ns}
    samples = shared_samples([new[n][0] for n in ns] + [old[n][0] for n in ns])
    snapped = snap(samples, times)
    t_fit = float(samples[-1])

    def quantities(bary, dyn, s):
        x = 0.5 * (bary[:, 2] + bary[:, 7])
        r, r0 = row_at(bary, s), bary[0]
        return {"dX": 0.5 * (r[2] + r[7]) - x[0], "d": r[2] - r[7],
                "proper": row_at(dyn, s)[10] - dyn[0, 10]}

    def accel(bary, t_end):
        w = (bary[:, 0] >= FIT_START - 1e-9) & (bary[:, 0] <= t_end + 1e-6)
        if w.sum() < 4:
            return None
        return 2.0 * np.polyfit(bary[w, 0], 0.5 * (bary[w, 2] + bary[w, 7]), 2)[0]

    qn = {(n, s): quantities(*new[n], s) for n in ns for s in snapped}
    qo = {(n, s): quantities(*old[n], s) for n in ns for s in snapped}

    def q_row(vals_by_n):
        if len(ns) != 3:
            return "–"
        v = [vals_by_n[n] for n in ns]
        if v[1] == v[2]:
            return "–"
        q = (v[0] - v[1]) / (v[1] - v[2])
        return f"{q:.1f} ({fmt(q_order(q, tuple(ns)), '.1f')})"

    head = ["", *[f"t {s:g}" for s in snapped]]
    print("## Motion against the paper's runs (cell: new value, then the paper's run at the same N)\n")
    print("ΔX = X(t) − X(0), X the midpoint of the two barycentres (cell: new (Δ vs paper %)):\n")
    rows = [[f"N {n}", *[f"{qn[n, s]['dX']:.4e} ({100 * (qn[n, s]['dX'] / qo[n, s]['dX'] - 1):+.2f} %)"
                         if qo[n, s]["dX"] else f"{qn[n, s]['dX']:.4e}" for s in snapped]] for n in ns]
    rows.append(["Q (p), new", *[q_row({n: qn[n, s]["dX"] for n in ns}) for s in snapped]])
    rows.append(["Q (p), paper", *[q_row({n: qo[n, s]["dX"] for n in ns}) for s in snapped]])
    table(head, rows)

    print("Separation d of the barycentres (cell: new (new − paper)):\n")
    rows = [[f"N {n}", *[f"{qn[n, s]['d']:.6f} ({qn[n, s]['d'] - qo[n, s]['d']:+.1e})" for s in snapped]] for n in ns]
    rows.append(["Q (p), new", *[q_row({n: qn[n, s]["d"] for n in ns}) for s in snapped]])
    table(head, rows)

    print("Proper core distance, change since t 0 (cell: new / paper; below ~2e-3 it is the core tracker's "
          "sub-cell steps):\n")
    rows = [[f"N {n}", *[f"{qn[n, s]['proper']:+.2e} / {qo[n, s]['proper']:+.2e}" for s in snapped]] for n in ns]
    table(head, rows)

    print(f"Acceleration a, fit over {FIT_START:g} ≤ t ≤ {t_fit:g} (the last sample shared with the paper's runs):\n")
    an = {n: accel(new[n][0], t_fit) for n in ns}
    ao = {n: accel(old[n][0], t_fit) for n in ns}
    rows = [[f"N {n}", fmt(an[n], ".4e"), fmt(ao[n], ".4e"),
             f"{100 * (an[n] / ao[n] - 1):+.2f} %" if an[n] and ao[n] else "–"] for n in ns]
    if len(ns) == 3 and all(an.values()) and all(ao.values()):
        rows.append(["Q (p)", q_row(an), q_row(ao), ""])
    table(["", "new", "paper", "Δ"], rows)

    if 256 in ns and 192 in ns:
        s = snapped[-1]
        dxn, dxo = qn[256, s]["dX"], qo[256, s]["dX"]
        ex_n, ex_o = abs(qn[192, s]["dX"] - dxn), abs(qo[192, s]["dX"] - dxo)
        line = f"At N 256: ΔX({s:g}) = {dxn:.4e} ± {ex_n:.1e} (paper {dxo:.4e} ± {ex_o:.1e})"
        if an.get(256) and an.get(192):
            line += (f"; a = {an[256]:.4e} ± {abs(an[192] - an[256]):.1e}"
                     f" (paper {ao[256]:.4e} ± {abs(ao[192] - ao[256]):.1e}), fit to t {t_fit:g}")
        print(line + ". Error bars: the N 192 − 256 difference.\n")


def lone_section(members: dict[int, Path], paper: dict[int, Path], times: list[float]) -> None:
    series = {}
    for n, m in members.items():
        bary, dyn = load(find(m, "sector_barycenters.dat")), load(find(m, "sector_dynamics.dat"))
        if bary is not None and dyn is not None:
            series[f"N {n}"] = (n, bary, dyn)
    for n, cell in paper.items():
        series[f"paper N {n}"] = (n, load(find(cell, "sector_barycenters.dat")), load(find(cell, "sector_dynamics.dat")))
    news = [k for k in series if not k.startswith("paper")]
    if not news:
        print("## Star drift\n\nNo member has barycentres yet.\n")
        return
    samples = shared_samples([series[k][1] for k in news])
    snapped = snap(samples, times)

    def drift(bary, dyn, s):
        """Of the occupied sector: the core's largest shift on any axis over t' <= s, the barycentre's at s, and
        the barycentre's largest over t' <= s."""
        size = np.nan_to_num(np.abs(bary[0, [1, 6]]))
        peak = np.nan_to_num(np.abs(dyn[0, [4, 8]]))
        bc = slice(2, 5) if size[0] > size[1] else slice(7, 10)
        cc = slice(1, 4) if peak[0] > peak[1] else slice(5, 8)
        b, c = bary[bary[:, 0] <= s + 1e-6], dyn[dyn[:, 0] <= s + 1e-6]
        shift = np.abs(b[:, bc] - bary[0, bc]).max(axis=1)
        return np.abs(c[:, cc] - dyn[0, cc]).max(), shift[-1], shift.max()

    vals = {(k, s): drift(series[k][1], series[k][2], s) if series[k][1][-1, 0] + 1e-6 >= s else None
            for k in series for s in snapped}
    print("## Star drift (cell: core, largest shift on any axis since t 0 / barycentre at t (its largest since "
          "t 0))\n")
    rows = [[k, *[f"{v[0]:.2e} / {v[1]:.2e} ({v[2]:.2e})" if (v := vals[k, s]) else "–" for s in snapped]]
            for k in series]
    ns = [series[k][0] for k in news]
    for i in range(len(news) - 1):
        a, b = news[i], news[i + 1]
        cells = []
        for s in snapped:
            va, vb = vals[a, s], vals[b, s]
            cells.append("–" if not (va and vb) else
                         f"{fmt(order(va[0], vb[0], ns[i], ns[i + 1]), '.1f')} / "
                         f"{fmt(order(va[1], vb[1], ns[i], ns[i + 1]), '.1f')}")
        rows.append([f"order {ns[i]}→{ns[i + 1]}", *cells])
    table(["", *[f"t {s:g}" for s in snapped]], rows)
    print("The paper's text (N 128): the core moves at most 1.8e-3 on any axis over t ≤ 200 (both lone stars); the "
          "barycentre of this star moves 1.3e-2 (its shift at t 200).\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", choices=sorted(STUDIES), default="pair")
    ap.add_argument("--times", type=float, nargs="+")
    ap.add_argument("--speed-window", type=float, default=60.0,
                    help="seconds between the two reads that give the speed (0: no speed)")
    args = ap.parse_args()

    pattern, paper_cells = STUDIES[args.study]
    members = {n: locate(RUNS, pattern.format(n=n)) for n in NN}
    paper = {n: locate(PAPER, c) for n, c in paper_cells.items()}
    runs_section(members, args.speed_window)

    reached = [t for t in (last_time(find(m, "collapse_diagnostics.dat")) for m in members.values()) if t]
    if not reached:
        return 0
    t_common = min(reached)
    times = args.times or [t for t in DEFAULT_TIMES if t <= t_common + 1e-6]
    if not args.times and (not times or t_common - times[-1] > 0.5):
        times.append(math.floor(t_common * 10) / 10)
    orders_section(members, times)
    if args.study == "pair":
        pair_section(members, paper, times)
    else:
        lone_section(members, paper, times)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
