#!/usr/bin/env python3
"""Open LIGO data from gwosc.org: which seconds exist, and fetching them.

A :class:`..interfaces.StrainSource`.

THE CACHE, AND WHERE IT LIVES
-----------------------------
Downloads are cached as float64 ``.npz`` keyed by
``(ifo, gps_start, gps_end, rate)``.  Two reasons this matters more than
convenience:

* the background estimate is re-derived every time the ranking or the slide
  count changes, and re-running the analysis must not mean re-downloading
  the observing run;
* a cached block is the same bytes every time, so a number in the article
  can be regenerated years later without depending on what the archive
  serves that day.

The cache is bulk detector data, not source, so it lives OUTSIDE the package
-- ``<repo>/runs/gw_search/strain_cache``, which the repository already
ignores -- and ``GW_SEARCH_CACHE`` overrides it.  It briefly defaulted to a
``data_cache/`` folder inside this package directory, which is how 16 MB of
O3 strain per block ended up sitting next to the source; that path is
ignored too, so an old checkout does not start committing it.

THE SEGMENT QUERY IS NOT OPTIONAL
---------------------------------
``*_DATA`` means only "the detector was locked".  ``*_CBC_CAT3`` is the cut
the compact-binary searches are actually run on, and the difference is not
cosmetic: the excluded time is excluded precisely because it is full of the
transient artefacts a burst search triggers on.  Searching un-vetoed time
and then reporting the triggers is a way to rediscover the observatory's
own known glitches and call them candidates.

THE TIMEOUT IS NOT OPTIONAL EITHER
----------------------------------
The fetch runs in a spawned process with a wall-clock kill.  GWOSC's own
per-request timeout does not always fire, and a scan asks for hundreds of
blocks; one wedged socket would otherwise cost the run rather than the
block.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import pathlib
import queue
from typing import Sequence

import numpy as np

__all__ = ["CACHE_DIR", "GwoscStrainSource"]


def _default_cache() -> pathlib.Path:
    env = os.environ.get("GW_SEARCH_CACHE")
    if env:
        return pathlib.Path(env)
    from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import REPO
    return REPO / "runs" / "gw_search" / "strain_cache"


CACHE_DIR = _default_cache()


def _with_retry(fn, *, what: str, tries: int = 4, base_delay: float = 5.0):
    """Run ``fn`` again on a transport failure, backing off.

    Queries here cross a proxy, and a proxy under load closes connections
    rather than answering: a day of ``L1_CBC_CAT3`` is over a hundred
    paginated requests and a single dropped one aborts the whole query.
    Observed as ``ProxyError(RemoteDisconnected)`` mid-pagination, which is
    also what silently cost 46 of 48 blocks in an early scan -- a transport
    failure that arrives as "no data" is the most expensive kind.
    """
    import time
    for attempt in range(tries):
        try:
            return fn()
        except Exception as exc:
            if attempt == tries - 1:
                raise
            delay = base_delay * 2 ** attempt
            print(f"  [gwosc] {what} failed ({type(exc).__name__}); "
                  f"retry {attempt + 1}/{tries - 1} in {delay:.0f}s",
                  flush=True)
            time.sleep(delay)


class _Sink:
    """Swallows the worker's status when it is called in-process."""

    def put(self, status):
        if status != "ok":
            raise RuntimeError(f"GWOSC fetch failed: {status}")


def _worker(ifo, start, end, rate, host, out_q, path, request_timeout=120.0):
    try:
        from gwpy.timeseries import TimeSeries as GwpyTS
        # An EXPLICIT per-request timeout, not just the watchdog process.
        # Inside a Pool worker the watchdog is unavailable (daemonic), and a
        # proxy that accepts a connection and then never answers will hang
        # the block forever -- observed as a scan sitting at 2 of 24 blocks
        # with no error and no progress, which is worse than a failure.
        gw = _with_retry(
            lambda: GwpyTS.fetch_open_data(ifo, float(start), float(end),
                                           sample_rate=int(rate), host=host,
                                           cache=False,
                                           timeout=float(request_timeout)),
            what=f"{ifo} strain {start:.0f}")
        # Write beside the target and rename: rename is atomic on POSIX, so
        # a reader can never open a half-written cache entry and a second
        # process fetching the same block cannot interleave with the first.
        # Learned the hard way -- two scans running at once left truncated
        # .npz files that every later block then failed to load.
        tmp = f"{path}.{os.getpid()}.tmp.npz"     # savez keeps a .npz suffix
        np.savez(tmp, values=np.asarray(gw.value, dtype=np.float64),
                 dt=float(gw.dt.value), epoch=float(gw.t0.value))
        os.replace(tmp, path)
        out_q.put("ok")
    except Exception as exc:                        # pragma: no cover
        out_q.put(repr(exc))


class GwoscStrainSource:
    """Segments and strain from the Gravitational Wave Open Science Center."""

    def __init__(self, cache_dir: pathlib.Path | str | None = None,
                 host: str = "https://gwosc.org", timeout_s: float = 900.0,
                 flag: str = "CBC_CAT3", min_segment_s: float = 512.0):
        self.cache_dir = pathlib.Path(cache_dir or CACHE_DIR)
        self.host = host
        self.timeout_s = timeout_s
        self.flag = flag
        self.min_segment_s = min_segment_s

    def segments(self, start: float, end: float,
                 ifos: Sequence[str] = ("H1", "L1")):
        """Science time common to ``ifos``, longest first.

        CACHED, like the strain.  The segment query is small but SLOW and
        rate-limited: a day of ``L1_CBC_CAT3`` is over two thousand
        intervals served across a hundred pages, and gwosc.org throttles a
        client that asks repeatedly.  Re-running an analysis must not depend
        on the archive's mood, so the answer is stored as JSON beside the
        strain and keyed by the same ``(ifos, flag, window)``.
        """
        import json
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        key = f"segments_{'-'.join(ifos)}_{self.flag}_{start:.0f}_{end:.0f}.json"
        path = self.cache_dir / key
        if path.exists():
            try:
                return [tuple(x) for x in json.loads(path.read_text())]
            except Exception:
                path.unlink(missing_ok=True)

        from gwpy.segments import DataQualityFlag
        active = None
        for ifo in ifos:
            f = _with_retry(lambda: DataQualityFlag.fetch_open_data(
                f"{ifo}_{self.flag}", start, end), what=f"{ifo} segments")
            active = f.active if active is None else (active & f.active)
        out = [(float(s[0]), float(s[1])) for s in active
               if float(s[1] - s[0]) >= self.min_segment_s]
        out.sort(key=lambda s: s[1] - s[0], reverse=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(out))
        os.replace(tmp, path)
        return out

    def _deadline(self, start: float, end: float) -> float:
        """Seconds to allow one fetch, scaled by how much data it asks for.

        A flat timeout is a trap here, because gwpy downloads the whole
        enclosing 4096 s GWOSC file however little is asked for, and the
        transfer rate to gwosc.org is not something this side controls -- it
        was measured at 49 kB/s to 320 kB/s on 2026-09-18, against a file of
        about 130 MB.  A 600 s limit sized for a 512 s block therefore killed
        4096 s blocks after they had already pulled 171 MB, which looks in
        the log exactly like an unreachable archive.  Allow time in
        proportion to the request, with the flat value as a floor.
        """
        return max(float(self.timeout_s), 2.0 * (float(end) - float(start)))

    def path_for(self, ifo: str, start: float, end: float, rate: int):
        return (self.cache_dir /
                f"{ifo}_{float(start):.0f}_{float(end):.0f}_{int(rate)}.npz")

    def prefetch(self, blocks, ifos=("H1", "L1"), sample_rate: int = 4096,
                 workers: int = 6, verbose: bool = True):
        """Download every block before any of them is filtered.

        Downloads are network-bound and filtering is CPU-bound, and mixing
        them inside process workers cost this search twice: a daemonic
        worker cannot run the watchdog subprocess, and a hung proxy socket
        then stalls a block with no error at all.  Fetching first, in
        THREADS in the parent (gwpy releases the GIL on network I/O, and
        the parent is not daemonic), keeps the timeout and the retry where
        they can act and leaves the compute fan-out to deal only with files
        that are already on disk.

        Returns the blocks that are fully cached.
        """
        from concurrent.futures import ThreadPoolExecutor

        want = [(ifo, bs, be) for bs, be in blocks for ifo in ifos]
        todo = [w for w in want
                if not self.path_for(w[0], w[1], w[2], sample_rate).exists()]
        if verbose and todo:
            print(f"[fetch] {len(todo)} of {len(want)} block-detectors to "
                  f"download, {workers} at a time", flush=True)

        def one(job):
            ifo, bs, be = job
            try:
                self.fetch(ifo, bs, be, sample_rate)
                return None
            except Exception as exc:
                return f"{ifo} {bs:.0f}: {exc}"

        if todo:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for i, err in enumerate(pool.map(one, todo), 1):
                    if err and verbose:
                        print(f"  [fetch] FAILED {err}", flush=True)
                    elif verbose and i % 5 == 0:
                        print(f"  [fetch] {i}/{len(todo)}", flush=True)

        ok = [(bs, be) for bs, be in blocks
              if all(self.path_for(ifo, bs, be, sample_rate).exists()
                     for ifo in ifos)]
        if verbose:
            print(f"[fetch] {len(ok)}/{len(blocks)} blocks cached", flush=True)
        return ok

    def fetch(self, ifo: str, start: float, end: float,
              sample_rate: int = 4096, retries: int = 2):
        from pycbc.types import TimeSeries
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self.path_for(ifo, start, end, sample_rate)

        if not path.exists():
            # A Pool worker is DAEMONIC and may not have children, so the
            # watchdog subprocess below is unavailable there and trying to
            # start one raises "daemonic processes are not allowed to have
            # children" -- which, caught per block, silently skipped all 48
            # of them and produced an empty search that looked like a quiet
            # sky.  Inside a worker the pool is already the supervisor, so
            # fetch inline and let the block fail if the socket wedges.
            if mp.current_process().daemon:
                _worker(ifo, start, end, sample_rate, self.host, _Sink(),
                        str(path), self._deadline(start, end))
                if not path.exists():
                    raise RuntimeError(f"GWOSC fetch {ifo} {start:.0f} failed")
                d = np.load(path)
                return TimeSeries(d["values"], delta_t=float(d["dt"]),
                                  epoch=float(d["epoch"]))
            ctx = mp.get_context("spawn")
            q = ctx.Queue(maxsize=1)
            p = ctx.Process(target=_worker,
                            args=(ifo, start, end, sample_rate, self.host,
                                  q, str(path), self._deadline(start, end)),
                            daemon=True)
            p.start()
            try:
                status = q.get(timeout=self._deadline(start, end))
            except queue.Empty:
                p.terminate(); p.join(2.0)
                path.unlink(missing_ok=True)
                raise TimeoutError(
                    f"GWOSC fetch {ifo} {start:.0f} timed out after "
                    f"{self.timeout_s:.0f}s")
            p.join(2.0)
            if status != "ok":
                path.unlink(missing_ok=True)
                raise RuntimeError(f"GWOSC fetch {ifo} {start:.0f}: {status}")

        d = np.load(path)
        return TimeSeries(d["values"], delta_t=float(d["dt"]),
                          epoch=float(d["epoch"]))
