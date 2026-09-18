#!/usr/bin/env python3
"""The orchestrator.

:class:`Search` knows the ORDER of a search -- pick science time, condition
it, place the bank once against real noise, filter every template through
every detector, coincide, slide, rank -- and nothing else.  Every collaborator
arrives through the constructor as one of the protocols in
:mod:`..interfaces`, so this module imports no detector, no noise curve and
no waveform.  Point it at a different ``StrainSource`` and the same code
searches simulated data; give it a different ``BackgroundEstimator`` and the
same triggers yield a different significance.

THE REACH STATEMENT
-------------------
Templates are generated at 1 Mpc, so a template's PSD-weighted norm
``sigma`` IS the distance in Mpc at which it would ring up SNR 1 in that
block.  The horizon at threshold is ``sigma / rho_threshold``, at OPTIMAL
orientation (:data:`..templates.nr.SKY`) and optimal sky position; divide by
:data:`SKY_AVERAGE` for the sky-and-orientation-averaged range.  This is the
only volume statement the search makes that does not import a population
model, and it is the one a null result is quoted as.
"""

from __future__ import annotations

import dataclasses
import json
import multiprocessing as mp
import pathlib
import time

import numpy as np

__all__ = ["Search", "SearchResult", "SKY_AVERAGE"]

BLOCK_S = 512.0
OVERLAP_S = 32.0
SKY_AVERAGE = 2.26      # optimal -> sky-and-orientation-averaged


def _filter_block(job):
    """One block, start to finish.  Module level so it survives ``spawn``.

    Blocks are independent by construction -- each carries its own PSD and
    its own crop -- which is what makes this safe to fan out.  The pieces
    travel to the worker by pickle, so every collaborator has to be
    picklable; that is a real constraint on :mod:`..interfaces`
    implementations and the reason none of them hold an open file or a
    socket.
    """
    (source, conditioner, noise, bank, triggers, ifos, sample_rate,
     block_s, bs, be) = job
    t0 = time.time()
    try:
        cond = {ifo: conditioner(source.fetch(ifo, bs, be, sample_rate))
                for ifo in ifos}
    except Exception as exc:
        return {"error": f"{bs:.0f}: {exc}", "gps": bs}
    psds = {ifo: noise.for_series(cond[ifo]) for ifo in ifos}

    found = {ifo: [] for ifo in ifos}
    horizon: dict = {}
    for bt in bank:
        tmpl = bt.series(sample_rate)
        for ifo in ifos:
            got = triggers(cond[ifo], tmpl, psds[ifo], ifo=ifo, key=bt.key,
                           arm=bt.arm, mass_msun=bt.mass_msun,
                           f_lower=bt.f_lower_hz())
            found[ifo].extend(got)
            if got:
                horizon.setdefault(bt.arm, []).append(got[0].sigma / 8.0)
    return {"triggers": found, "horizon": horizon, "gps": bs,
            "livetime": block_s - conditioner.lost_s - 2.0 * noise.lost_s,
            "seconds": time.time() - t0,
            "n": sum(len(v) for v in found.values())}


@dataclasses.dataclass
class SearchResult:
    ifos: tuple
    blocks: int
    livetime_s: float
    bank_size: int
    foreground: list
    background: object
    horizon_mpc: dict
    loudest_single: dict
    meta: dict = dataclasses.field(default_factory=dict)

    def to_json(self, path) -> None:
        bg = self.background
        payload = {
            "ifos": list(self.ifos),
            "blocks": self.blocks,
            "livetime_s": self.livetime_s,
            "livetime_hours": self.livetime_s / 3600.0,
            "bank_size": self.bank_size,
            "background": {
                "n_slides": bg.n_slides,
                "livetime_s": bg.livetime_s,
                "livetime_days": bg.livetime_s / 86400.0,
                "n_coincidences": int(bg.ranks.size),
                "loudest_rank": float(bg.ranks[-1]) if bg.ranks.size else None,
                "floor_far_per_year": bg.floor_far_per_year,
            },
            "foreground": [
                {"rank": c.rank, "template": c.template, "arm": c.arm,
                 "times": c.times, "dt_ms": c.dt_ms,
                 "far_per_year": bg.far_of(c.rank)}
                for c in self.foreground[:50]],
            "n_foreground": len(self.foreground),
            "horizon_note": ("median over the channel's mass ladder of "
                             "sigma/8: single-detector SNR 8, optimal "
                             "orientation and sky position"),
            "horizon_mpc_optimal_snr8_single_ifo": self.horizon_mpc,
            "horizon_mpc_sky_averaged_snr8_single_ifo": {
                k: v / SKY_AVERAGE for k, v in self.horizon_mpc.items()},
            "loudest_single_detector": self.loudest_single,
        }
        payload.update(self.meta)
        pathlib.Path(path).write_text(json.dumps(payload, indent=2,
                                                 sort_keys=True))


class Search:
    """Assemble a search from its parts, then run it over a GPS interval."""

    def __init__(self, source, conditioner, noise, bank, triggers,
                 coincidence, background, *, sample_rate: int = 4096,
                 block_s: float = BLOCK_S, overlap_s: float = OVERLAP_S,
                 workers: int = 1, verbose: bool = True):
        self.source = source
        self.conditioner = conditioner
        self.noise = noise
        self.bank = bank
        self.triggers = triggers
        self.coincidence = coincidence
        self.background = background
        self.sample_rate = sample_rate
        self.block_s = block_s
        self.overlap_s = overlap_s
        self.workers = max(1, int(workers))
        self.verbose = verbose

    def _blocks(self, seg):
        s, e = seg
        step = self.block_s - 2 * self.overlap_s
        t = s
        while t + self.block_s <= e:
            yield (t, t + self.block_s)
            t += step

    def _absorb(self, out, by_ifo, horizon, k, total):
        if "error" in out:
            print(f"  block {k + 1}/{total} SKIPPED -- {out['error']}",
                  flush=True)
            return
        for ifo, trigs in out["triggers"].items():
            by_ifo[ifo].extend(trigs)
        for arm, v in out["horizon"].items():
            horizon.setdefault(arm, []).extend(v)
        if self.verbose:
            print(f"  block {k + 1}/{total} {out['gps']:.0f}  "
                  f"+{out['n']:6d} triggers  [{out['seconds']:.0f}s]",
                  flush=True)

    def run(self, start: float, end: float, ifos=("H1", "L1"),
            max_blocks: int = 8) -> SearchResult:
        segs = self.source.segments(start, end, ifos)
        if not segs:
            raise SystemExit("no coincident science time in that window")
        if self.verbose:
            total = sum(b - a for a, b in segs)
            print(f"[search] {len(segs)} coincident segments, "
                  f"{total / 3600:.1f} h total; longest "
                  f"{segs[0][1] - segs[0][0]:.0f} s at {segs[0][0]:.0f}")

        todo = [b for seg in segs for b in self._blocks(seg)][:max_blocks]
        if self.verbose:
            print(f"[search] {len(todo)} blocks of {self.block_s:.0f} s")

        # Fetch everything first, if the source knows how.  Downloads are
        # network-bound and filtering is CPU-bound; interleaving them inside
        # the compute workers put a hung socket where nothing could time it
        # out.  A source that cannot prefetch (a simulated one, say) simply
        # does not have the method, and the loop below fetches as it goes.
        if hasattr(self.source, "prefetch"):
            todo = self.source.prefetch(todo, ifos, self.sample_rate,
                                        workers=min(6, max(1, self.workers)),
                                        verbose=self.verbose)
            if not todo:
                raise SystemExit("no block could be fetched")

        # The bank is placed ONCE, against the noise of the first block
        # that fetches: spacing is a property of the data the search is run
        # on, not of a design curve.  It has to happen before any fan-out,
        # because every worker must filter the SAME bank -- a per-worker
        # bank would mean per-worker template keys and no coincidence.
        first = None
        for i, (bs, be) in enumerate(todo):
            try:
                probe = self.conditioner(
                    self.source.fetch(ifos[0], bs, be, self.sample_rate))
            except Exception as exc:
                print(f"  block {i + 1} {bs:.0f} SKIPPED -- {exc}")
                continue
            self.noise.for_series(probe)
            first = i
            break
        if first is None:
            raise SystemExit("no block could be fetched")

        print("[bank] placing rungs on the live noise curve:")
        self.bank.place(self.noise, self.sample_rate, verbose=self.verbose)
        print(f"[bank] {len(self.bank)} templates", flush=True)

        jobs = [(self.source, self.conditioner, self.noise, self.bank,
                 self.triggers, tuple(ifos), self.sample_rate, self.block_s,
                 bs, be) for bs, be in todo[first:]]

        by_ifo: dict = {ifo: [] for ifo in ifos}
        horizon: dict = {}
        livetime = 0.0
        done = 0

        if self.workers > 1:
            print(f"[search] {len(jobs)} blocks over {self.workers} workers",
                  flush=True)
            ctx = mp.get_context("spawn")
            with ctx.Pool(self.workers) as pool:
                results = pool.imap_unordered(_filter_block, jobs)
                for k, out in enumerate(results):
                    self._absorb(out, by_ifo, horizon, k, len(jobs))
                    if "error" not in out:
                        livetime += out["livetime"]
                        done += 1
        else:
            for k, job in enumerate(jobs):
                out = _filter_block(job)
                self._absorb(out, by_ifo, horizon, k, len(jobs))
                if "error" not in out:
                    livetime += out["livetime"]
                    done += 1

        if done == 0:
            raise SystemExit("no block could be analysed")

        fg = sorted(self.coincidence(by_ifo[ifos[0]], by_ifo[ifos[1]]),
                    key=lambda c: -c.rank)
        bg = self.background.estimate(by_ifo, livetime)

        loudest = {}
        for ifo in ifos:
            if by_ifo[ifo]:
                t = max(by_ifo[ifo], key=lambda x: x.stat)
                loudest[ifo] = {"stat": t.stat, "snr": t.snr,
                                "chisq_r": t.chisq_r, "time": t.time,
                                "template": t.template}

        return SearchResult(
            ifos=tuple(ifos), blocks=done, livetime_s=livetime,
            bank_size=len(self.bank), foreground=fg, background=bg,
            horizon_mpc={k: float(np.median(v)) for k, v in horizon.items()},
            loudest_single=loudest,
            meta={"gps_start": start, "gps_end": end,
                  "sample_rate": self.sample_rate})


def report(res: SearchResult) -> None:
    """The result, in the order a referee reads it: background, then events."""
    bg = res.background
    print("\n" + "=" * 74)
    print(f"SEARCH RESULT  {'+'.join(res.ifos)}  {res.blocks} blocks, "
          f"{res.livetime_s / 3600:.2f} h livetime, {res.bank_size} templates")
    print("=" * 74)
    print(f"background : {bg.ranks.size} accidental coincidences over "
          f"{bg.livetime_s / 86400:.1f} days ({bg.n_slides} slides)")
    if bg.ranks.size:
        q = bg.quantiles()
        print(f"             rank  median {q[0]:.2f}  90th {q[1]:.2f}  "
              f"99th {q[2]:.2f}  loudest {q[3]:.2f}")
    print(f"             smallest reportable FAR = "
          f"{bg.floor_far_per_year:.0f}/yr "
          f"(1 per {bg.livetime_s / 86400:.1f} days)")
    print(f"\nforeground : {len(res.foreground)} zero-lag coincidences")
    for c in res.foreground[:5]:
        print(f"   rank {c.rank:6.2f}  {c.template:<26s} "
              f"dt {c.dt_ms:+7.1f} ms   FAR {bg.far_of(c.rank):.3g}/yr")
    if not res.foreground:
        print("   (none)")
    print("\nhorizon at SINGLE-DETECTOR SNR 8, median over each channel's"
          "\nmass ladder [Mpc, optimal orientation | sky-averaged]:")
    for arm, d in sorted(res.horizon_mpc.items(), key=lambda kv: -kv[1]):
        print(f"   {arm:<18s} {d:8.1f} | {d / SKY_AVERAGE:8.1f}")
