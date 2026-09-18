"""Tests for the LIGO search package.

Everything here runs offline.  The network-facing parts (``GwoscStrainSource``)
are exercised through the protocol, with a fake source, which is the whole
point of :mod:`grteclyn_wrapper.gw_search.interfaces`: the pipeline must be
testable without the observatory.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pycbc")

from grteclyn_wrapper.gw_search import interfaces                    # noqa: E402
from grteclyn_wrapper.gw_search.pipeline import (                    # noqa: E402
    CoincidenceEngine, NewSNR, TimeSlideBackground, Trigger, TriggerGenerator,
)
from grteclyn_wrapper.gw_search.strain import (                      # noqa: E402
    DesignNoise, GwoscStrainSource, StandardConditioner, WelchNoise,
)
from grteclyn_wrapper.gw_search.templates import (                   # noqa: E402
    ARM_NAMES, MassLadderBank, load_arm, template_timeseries,
)

SR = 4096


# --------------------------------------------------------------------------
# the protocols are the package's contract; if an implementation drifts off
# one of them, the injection points in `Search` silently stop being swappable
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cls,proto", [
    (GwoscStrainSource, interfaces.StrainSource),
    (StandardConditioner, interfaces.Conditioner),
    (WelchNoise, interfaces.NoiseModel),
    (DesignNoise, interfaces.NoiseModel),
    (MassLadderBank, interfaces.TemplateSource),
    (NewSNR, interfaces.RankingStatistic),
    (TimeSlideBackground, interfaces.BackgroundEstimator),
])
def test_implements_protocol(cls, proto):
    assert isinstance(cls.__new__(cls), proto)


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_arm_integrates_to_a_burst_not_a_pedestal(arm):
    """The Psi_4 -> h clamp must stay at or above one cycle per record.

    This is the regression test for the fly-by bug: with the clamp below
    1/T the reconstructed strain was a pedestal with a wiggle on it, |h| at
    the record's ends reaching 0.83 of its peak, and the burst came out 100x
    too loud.  `drift` is exactly that ratio.
    """
    wf = load_arm(arm)
    assert wf.f0 >= 1.0 / wf.duration_M - 1e-12
    assert wf.drift < 0.55, f"{arm}: reconstructed strain is mostly pedestal"
    assert np.isfinite(wf.H).all()


@pytest.mark.parametrize("arm", ARM_NAMES)
def test_template_peak_sits_at_epoch_zero(arm):
    """A trigger time is the burst's peak only if the template says so."""
    ts = template_timeseries(load_arm(arm), 100.0, 1.0, SR)
    peak_t = float(ts.sample_times[int(np.argmax(np.abs(ts.numpy())))])
    assert abs(peak_t) < 2.0 / SR


def test_template_scales_as_mass_over_distance():
    """The records are scale-free; if that breaks, the whole bank is wrong."""
    wf = load_arm("head-on")
    a = np.abs(template_timeseries(wf, 100.0, 10.0, SR).numpy()).max()
    b = np.abs(template_timeseries(wf, 100.0, 20.0, SR).numpy()).max()
    assert a / b == pytest.approx(2.0, rel=0.02)          # h ~ 1/D
    c = np.abs(template_timeseries(wf, 200.0, 10.0, SR).numpy()).max()
    assert c / a == pytest.approx(2.0, rel=0.05)          # h ~ M


def test_template_never_filtered_below_its_own_corner():
    from grteclyn_wrapper.gw_search.templates import BankTemplate
    wf = load_arm("fly-by")
    bt = BankTemplate(arm=wf.name, mode=wf.mode, mass_msun=125.0, waveform=wf)
    corner_hz = wf.hz(1.0 / wf.duration_M, 125.0)
    assert bt.f_lower_hz(20.0) == pytest.approx(corner_hz)
    assert bt.f_lower_hz(20.0) > 20.0                     # and it bites


# --------------------------------------------------------------------------
# the statistics: these are where a search quietly stops meaning anything
# --------------------------------------------------------------------------
def test_chisq_reweighting_only_ever_penalises():
    stat = NewSNR()
    snr = np.array([10.0, 10.0, 10.0])
    out = stat.single(snr, np.array([0.5, 1.0, 9.0]))
    assert out[0] == pytest.approx(10.0)      # consistent: untouched
    assert out[1] == pytest.approx(10.0)
    assert out[2] < 6.0                       # inconsistent: pushed down hard


def _trig(ifo, t, stat, key="a@1"):
    return Trigger(ifo=ifo, template=key, arm="a", mass_msun=1.0, time=t,
                   snr=stat, chisq_r=1.0, stat=stat, sigma=1.0)


def test_coincidence_requires_same_template_and_window():
    co = CoincidenceEngine(NewSNR(), window_s=0.015)
    h = [_trig("H1", 100.0, 8.0)]
    assert len(co(h, [_trig("L1", 100.005, 8.0)])) == 1          # in window
    assert len(co(h, [_trig("L1", 100.5, 8.0)])) == 0            # out of it
    assert len(co(h, [_trig("L1", 100.005, 8.0, "b@1")])) == 0   # other tmpl


def test_coincidence_keeps_only_the_loudest_partner():
    """One loud glitch must not manufacture many coincidences."""
    co = CoincidenceEngine(NewSNR(), window_s=0.015)
    out = co([_trig("H1", 100.0, 8.0)],
             [_trig("L1", 100.001, 6.0), _trig("L1", 100.002, 9.0)])
    assert len(out) == 1
    assert out[0].stats["L1"] == 9.0


def test_time_slides_destroy_a_real_coincidence():
    """A signal survives zero lag and nothing else; that is the assumption
    the whole background rests on, so it is worth asserting."""
    co = CoincidenceEngine(NewSNR(), window_s=0.015)
    h, l = [_trig("H1", 100.0, 8.0)], [_trig("L1", 100.001, 8.0)]
    assert len(co(h, l)) == 1
    bg = TimeSlideBackground(co, n_slides=20, step_s=1.0).estimate(
        {"H1": h, "L1": l}, livetime_s=100.0)
    assert bg.ranks.size == 0
    assert bg.livetime_s == pytest.approx(20 * 100.0)
    assert bg.n_slides == 20


def test_far_cannot_be_reported_below_one_per_background_livetime():
    """The '+1' in (N_louder + 1)/T.  Without it an event louder than every
    slide is reported at infinite significance from a finite experiment."""
    from grteclyn_wrapper.gw_search.pipeline.background import Background, YEAR_S
    bg = Background(ranks=np.array([1.0, 2.0, 3.0]), livetime_s=1000.0,
                    n_slides=10)
    assert bg.far_of(99.0) == pytest.approx(YEAR_S / 1000.0)
    assert bg.far_of(99.0) == pytest.approx(bg.floor_far_per_year)
    assert bg.far_of(2.5) > bg.far_of(99.0)


def test_chisq_bins_track_template_length():
    """A 5 ms template has fewer independent cells than a 125 ms one, and
    asking for more bins than it can fill does not strengthen the veto."""
    from grteclyn_wrapper.gw_search.pipeline.triggers import chisq_bins
    short = template_timeseries(load_arm("fly-by"), 20.0, 1.0, SR)
    long_ = template_timeseries(load_arm("vacuum BBH twin"), 330.0, 1.0, SR)
    assert 4 <= chisq_bins(short, 20.0, SR) <= chisq_bins(long_, 20.0, SR) <= 16


# --------------------------------------------------------------------------
# end to end, on synthetic noise: the pipeline must find what is really there
# --------------------------------------------------------------------------
def _sigma_mpc(bt, psd):
    """Distance at which this template rings up SNR 1 against ``psd``."""
    from pycbc.filter import sigma
    return float(sigma(bt.series(SR, distance_mpc=1.0).to_frequencyseries(
        delta_f=psd.delta_f), psd=psd,
        low_frequency_cutoff=bt.f_lower_hz()))


def test_injection_is_recovered_in_coloured_noise():
    from pycbc.noise import noise_from_psd
    from pycbc.types import TimeSeries
    from grteclyn_wrapper.gw_search.analysis import inject
    from grteclyn_wrapper.gw_search.templates import BankTemplate

    dur, f_low = 64, 20.0
    psd = DesignNoise(15.0).for_length(dur * SR, 1.0 / SR)
    data = noise_from_psd(dur * SR, 1.0 / SR, psd, seed=11)
    data = TimeSeries(data.numpy(), delta_t=1.0 / SR, epoch=0.0)

    wf = load_arm("head-on")
    bt = BankTemplate(arm=wf.name, mode=wf.mode, mass_msun=150.0, waveform=wf)
    # A REALISTIC loudness.  An injection at, say, 5 Mpc rings up SNR ~6000,
    # and at that amplitude the chi-squared is legitimately enormous -- a
    # relative template mismatch of 1e-4 becomes chi^2 ~ 4000 -- so the test
    # would be asserting that a perfect filter exists, not that the veto
    # spares real signals.  This distance gives SNR ~20, the regime the
    # search actually operates in.
    sig = _sigma_mpc(bt, psd)
    loud = bt.series(SR, distance_mpc=sig / 20.0)
    t_inj = 32.0
    gen = TriggerGenerator(NewSNR(), f_lower=f_low, snr_floor=6.0,
                           psd_seg_s=4.0)

    quiet = gen(data, bt.series(SR), psd, ifo="H1", key=bt.key, arm=bt.arm,
                mass_msun=bt.mass_msun, f_lower=bt.f_lower_hz())
    assert not any(abs(t.time - t_inj) < 0.05 for t in quiet)

    got = gen(inject(data, loud, t_inj), bt.series(SR), psd, ifo="H1",
              key=bt.key, arm=bt.arm, mass_msun=bt.mass_msun,
              f_lower=bt.f_lower_hz())
    near = [t for t in got if abs(t.time - t_inj) < 0.05]
    assert near, "an injected signal was not recovered at its own time"
    best = max(near, key=lambda t: t.snr)
    assert 12.0 < best.snr < 40.0, f"recovered SNR {best.snr:.1f}, expected ~20"
    assert best.chisq_r < 4.0, "the veto rejected a real signal"
    assert best.stat > 0.7 * best.snr
