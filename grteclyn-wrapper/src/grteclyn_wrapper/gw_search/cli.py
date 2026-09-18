#!/usr/bin/env python3
"""Command line for the campaign's LIGO search.

    python -m grteclyn_wrapper.gw_search.cli <subcommand> [options]

    templates        the five arms as detector templates, and their quality
    validate         the Psi_4 -> h chain, against IMRPhenomD, on the BBH twin
    fitting-factor   would the modelled searches have recovered these signals?
    scan             matched-filter search of open data, with a background
    inject           add known signals to real strain and recover them
    events           the bank against the strain around catalogue events

This module is the ONLY one in the package that formats for a human, and it
is where the concrete pieces are chosen and injected -- which strain source,
which noise model, which ranking statistic.  Everything below it is written
against :mod:`.interfaces`, so a different assembly here is a different
search with no other edit.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")

SAMPLE_RATE = 4096


def _assemble(args, noise=None):
    """Wire the concrete pieces.  Dependency inversion happens here, once."""
    from grteclyn_wrapper.gw_search.pipeline import (
        CoincidenceEngine, NewSNR, Search, TimeSlideBackground, TriggerGenerator,
    )
    from grteclyn_wrapper.gw_search.strain import (
        GwoscStrainSource, StandardConditioner, WelchNoise,
    )
    from grteclyn_wrapper.gw_search.templates import MassLadderBank

    ranking = NewSNR()
    coincidence = CoincidenceEngine(ranking)
    return Search(
        source=GwoscStrainSource(),
        conditioner=StandardConditioner(),
        noise=noise or WelchNoise(),
        bank=MassLadderBank(arms=args.arm),
        triggers=TriggerGenerator(ranking, snr_floor=getattr(args, "snr_floor", 5.0)),
        coincidence=coincidence,
        background=TimeSlideBackground(coincidence,
                                       n_slides=getattr(args, "slides", 400)),
        sample_rate=SAMPLE_RATE,
        block_s=getattr(args, "block_s", 512.0),
        overlap_s=min(32.0, 0.0625 * getattr(args, "block_s", 512.0)),
        workers=getattr(args, "workers", 1))


def _design_noise():
    from grteclyn_wrapper.gw_search.strain import DesignNoise
    return DesignNoise()


def _cmd_templates(args) -> int:
    from grteclyn_wrapper.gw_search.templates import load_all_arms, template_timeseries
    print(f"{'arm':<18s} {'mode':<6s} {'T/M':>6s} {'f_Psi4 M':>9s} "
          f"{'f body (fM)':>17s} {'clamp':>7s} {'drift':>6s} {'max|H|':>10s}")
    for wf in load_all_arms():
        print(f"{wf.name:<18s} {wf.mode:<6s} {wf.duration_M:6.1f} "
              f"{wf.f_psi4_peak:9.4f} "
              f"[{wf.f_body[0]:.4f},{wf.f_body[1]:.4f}] {wf.f0:7.4f} "
              f"{wf.drift:6.2f} {np.abs(wf.H).max():10.3e}")
        for m in (args.mass or [30.0, 100.0, 300.0]):
            ts = template_timeseries(wf, m, 100.0, SAMPLE_RATE)
            print(f"    M = {m:6.1f} Msun: {len(ts):6d} samples, "
                  f"{len(ts) * ts.delta_t * 1e3:7.1f} ms, "
                  f"f_peak {wf.hz(wf.f_psi4_peak, m):6.1f} Hz, "
                  f"|h| at 100 Mpc {np.abs(ts.numpy()).max():.3e}")
    print("\n'drift' is |h| at the record's ends over |h| at its peak: how much "
          "of the\nreconstructed strain is integration pedestal rather than "
          "burst.  Below ~0.1\nthe record integrates cleanly; the head-on, "
          "spiral and fly-by sit at 0.3-0.4,\nand their low-frequency strain "
          "is an upper bound, not a measurement.")
    return 0


def _cmd_validate(args) -> int:
    from grteclyn_wrapper.gw_search.analysis import validate_bbh_twin
    print(__doc__.splitlines()[0])
    print("\nVALIDATION -- the campaign's vacuum BBH control through the "
          "search's own\ntemplate chain, matched against IMRPhenomD at "
          "aLIGO design sensitivity.\n")
    _, ok = validate_bbh_twin(_design_noise(), SAMPLE_RATE,
                              masses=args.mass or (60.0, 100.0, 150.0,
                                                   200.0, 300.0))
    return 0 if ok else 1


def _cmd_fitting_factor(args) -> int:
    from grteclyn_wrapper.gw_search.analysis import survey
    from grteclyn_wrapper.gw_search.templates.bank import MATCH_S
    psd = _design_noise().for_length(int(MATCH_S * SAMPLE_RATE), 1.0 / SAMPLE_RATE)
    print("Fitting factor against a quasi-circular IMRPhenomD bank "
          "(M 20-500 Msun, q 1-4,\nchi +-0.9) at aLIGO design sensitivity.  "
          "FF(bank) is what a modelled search\nrecovers; vol = FF^3 is the "
          "fraction of the optimal detection volume left.\nRead against the "
          "BBH control's own ceiling of 0.90-0.94, not against 1.\n")
    res = survey(psd, SAMPLE_RATE,
                 masses=args.mass or [60.0, 100.0, 150.0, 200.0, 300.0],
                 arms=args.arm)
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(
            [r.__dict__ | {"volume_fraction": r.volume_fraction} for r in res],
            indent=2))
        print(f"\nwrote {args.out}")
    return 0


def _cmd_scan(args) -> int:
    from grteclyn_wrapper.gw_search.pipeline.search import report
    search = _assemble(args)
    res = search.run(args.gps_start, args.gps_end, ifos=tuple(args.ifos),
                     max_blocks=args.max_blocks)
    report(res)
    if args.out:
        res.to_json(args.out)
        print(f"\nwrote {args.out}")
    return 0


def _cmd_inject(args) -> int:
    """End-to-end: is the pipeline able to find a signal that is there?"""
    from grteclyn_wrapper.gw_search.analysis import run_injections
    from grteclyn_wrapper.gw_search.pipeline import NewSNR, TriggerGenerator
    from grteclyn_wrapper.gw_search.strain import (
        GwoscStrainSource, StandardConditioner, WelchNoise,
    )
    from grteclyn_wrapper.gw_search.templates import MassLadderBank

    source, cond, noise = GwoscStrainSource(), StandardConditioner(), WelchNoise()
    strain = cond(source.fetch(args.ifos[0], args.gps_start,
                               args.gps_start + args.duration, SAMPLE_RATE))
    noise.for_series(strain)
    bank = MassLadderBank(arms=args.arm).place(noise, SAMPLE_RATE, verbose=False)
    print(f"injecting into {args.ifos[0]} at GPS {args.gps_start:.0f} "
          f"(+{args.duration:.0f} s), searching the full {len(bank)}-template "
          f"bank each time\n")
    res = run_injections(strain, noise, bank,
                         TriggerGenerator(NewSNR(), snr_floor=args.snr_floor),
                         ifo=args.ifos[0], target_snr=args.target_snr)
    found = sum(r.found for r in res)
    eff = [r.efficiency for r in res if r.found]
    if not eff:
        print("\nVERDICT: FAIL -- nothing was recovered at all")
        return 1
    chi = [r.chisq_r for r in res if r.found]
    print(f"\nfound {found}/{len(res)}; recovered/optimal SNR "
          f"{np.min(eff):.2f}-{np.max(eff):.2f} (median {np.median(eff):.2f}); "
          f"chi2_r {np.min(chi):.2f}-{np.max(chi):.2f}")
    ok = found == len(res) and np.median(eff) > 0.8 and np.max(chi) < 4.0
    print(f"VERDICT: {'PASS' if ok else 'CHECK'} -- every injection found, "
          f"median efficiency > 0.8, no injection vetoed (chi2_r < 4)")
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(
            [r.__dict__ | {"efficiency": r.efficiency} for r in res], indent=2))
    return 0 if ok else 1


def _cmd_events(args) -> int:
    import urllib.request
    from grteclyn_wrapper.gw_search.pipeline import NewSNR, TriggerGenerator
    from grteclyn_wrapper.gw_search.strain import (
        GwoscStrainSource, StandardConditioner, WelchNoise,
    )
    from grteclyn_wrapper.gw_search.templates import MassLadderBank

    with urllib.request.urlopen("https://gwosc.org/eventapi/json/GWTC/",
                                timeout=60) as fh:
        events = json.load(fh)["events"]

    source, cond = GwoscStrainSource(), StandardConditioner()
    gen = TriggerGenerator(NewSNR(), snr_floor=args.snr_floor)
    bank = MassLadderBank(arms=args.arm).place(_design_noise(), SAMPLE_RATE,
                                               verbose=False)
    print(f"bank: {len(bank)} templates; searching +-0.5 s about each event\n")

    rows = []
    for name in (args.event or sorted(events)):
        key = next((k for k in events if k.startswith(name)), None)
        if key is None:
            print(f"  {name}: not in GWTC"); continue
        gps = float(events[key]["GPS"])
        try:
            noise = WelchNoise()
            data = {ifo: cond(source.fetch(ifo, gps - 128, gps + 128,
                                           SAMPLE_RATE)) for ifo in args.ifos}
            psds = {ifo: noise.for_series(data[ifo]) for ifo in args.ifos}
        except Exception as exc:
            print(f"  {key}: fetch failed -- {exc}"); continue

        best = None
        for bt in bank:
            tmpl = bt.series(SAMPLE_RATE)
            for ifo in args.ifos:
                for t in gen(data[ifo], tmpl, psds[ifo], ifo=ifo, key=bt.key,
                             arm=bt.arm, mass_msun=bt.mass_msun,
                             f_lower=bt.f_lower_hz()):
                    if abs(t.time - gps) < 0.5 and (best is None
                                                    or t.stat > best.stat):
                        best = t
        if best is None:
            print(f"  {key:<16s} nothing above SNR {args.snr_floor} "
                  f"within 0.5 s of GPS {gps:.2f}")
        else:
            print(f"  {key:<16s} best {best.arm}@{best.mass_msun:.0f} in "
                  f"{best.ifo}: SNR {best.snr:.2f}, chi2_r {best.chisq_r:.2f}, "
                  f"newsnr {best.stat:.2f}, dt {(best.time - gps) * 1e3:+.0f} ms")
            rows.append({"event": key, "arm": best.arm,
                         "mass_msun": best.mass_msun, "snr": best.snr,
                         "chisq_r": best.chisq_r, "newsnr": best.stat,
                         "dt_ms": (best.time - gps) * 1e3})
    if args.out and rows:
        pathlib.Path(args.out).write_text(json.dumps(rows, indent=2))
        print(f"\nwrote {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="gw_search", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--arm", action="append",
                       help="restrict to this campaign ARMS row (repeatable)")
        p.add_argument("--mass", type=float, action="append",
                       help="total mass in Msun (repeatable)")
        p.add_argument("--out", help="write JSON here")
        return p

    common(sub.add_parser("templates")).set_defaults(fn=_cmd_templates)
    common(sub.add_parser("validate")).set_defaults(fn=_cmd_validate)
    common(sub.add_parser("fitting-factor")).set_defaults(fn=_cmd_fitting_factor)

    p = common(sub.add_parser("scan"))
    p.add_argument("--gps-start", type=float, required=True)
    p.add_argument("--gps-end", type=float, required=True)
    p.add_argument("--ifos", nargs="+", default=["H1", "L1"])
    p.add_argument("--max-blocks", type=int, default=8)
    p.add_argument("--slides", type=int, default=400)
    p.add_argument("--snr-floor", type=float, default=5.0)
    p.add_argument("--block-s", type=float, default=512.0,
                   help="analysis block length. GWOSC serves 4096 s files and "
                        "gwpy downloads the whole enclosing file however "
                        "little is asked for, so 4096 buys eight times the "
                        "livetime per download on a slow link")
    p.add_argument("--workers", type=int, default=1,
                   help="analyse this many blocks in parallel; "
                        "blocks are independent (own PSD, own crop)")
    p.set_defaults(fn=_cmd_scan)

    p = common(sub.add_parser("inject"))
    p.add_argument("--gps-start", type=float, default=1264317634)
    p.add_argument("--duration", type=float, default=512.0)
    p.add_argument("--ifos", nargs="+", default=["H1"])
    p.add_argument("--target-snr", type=float, default=20.0,
                   help="every injection is placed at the distance "
                        "that gives this optimal SNR")
    p.add_argument("--snr-floor", type=float, default=5.0)
    p.set_defaults(fn=_cmd_inject)

    p = common(sub.add_parser("events"))
    p.add_argument("--event", action="append")
    p.add_argument("--ifos", nargs="+", default=["H1", "L1"])
    p.add_argument("--snr-floor", type=float, default=5.0)
    p.set_defaults(fn=_cmd_events)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
