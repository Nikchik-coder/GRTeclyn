# `gw_search` — the campaign's waveforms against real LIGO data

A matched-filter search of public Gravitational Wave Open Science Center
(GWOSC) strain for the five radiating channels of the wormhole-merger
campaign, with a χ² veto, H1–L1 coincidence, and a time-slide background —
so that what comes out is a **false-alarm rate**, not a signal-to-noise
ratio.

The article's Sec. V (`research/merger/article/research.tex`, `sec:ligo`) is
written from what this package prints.

---

## 1. What is being searched for

The campaign evolves drainhole-wormhole pairs in full numerical relativity
and records `r Ψ₄` on extraction spheres. Five channels radiate, and the
search treats each as a hypothesis:

| channel | mode | resolved `f Ψ₄` peak (`fM`) | record | integration quality (`drift`) |
|---|---|---|---|---|
| collapsing throat | (2,0) | 0.0563 | 70 M | **0.02** |
| head-on merger | (2,0) | 0.0600 | 50 M | 0.31 |
| spiral merger | (2,2) | 0.0600 | 50 M | 0.42 |
| fly-by (no horizon) | (2,2) | 0.0286 | 35 M | 0.40 |
| vacuum BBH twin (control) | (2,2) | 0.0664 | 75 M | **0.07** |

The rows are **not** restated here in code. They are `ARMS` in
`visualisation/wormhole_merger/plot_psi4_gallery.py` — the same table the
article's two wave figures read — so the search and the figures can never
disagree about what a scenario is, which stream it lives in, which sphere is
innermost, or where it is gated.

### The mass band, and why the old estimate was wrong

The records are **scale-free**: with the source's total ADM mass as the unit,
strain scales as `M/D` and frequency as `1/M`, so one record covers every
candidate mass at once and the only bank dimension is the total mass.

A note that used to live here reasoned from a ringdown at `f ≈ 0.3/M` in code
units and concluded that only 500–2000 M⊙ could put a signal in band. **The
campaign's records do not carry 0.3.** Their resolved Ψ₄ band peaks are
`fM = 0.028–0.066`, a factor of 5–10 lower, so the band that matters is a
factor of 5–10 *lighter*: roughly **20–400 M⊙**, the intermediate-mass
window. That is a better place to be looking — it is where the modelled
searches are thinnest, and where a short burst is least likely to have been
recovered by a chirp template.

---

## 2. The hard step: Ψ₄ → h

`Ψ₄ = ḧ₊ − i ḧ₊ₓ`, so strain is a **double** time integral — a division by
`(2πf)²` in the Fourier domain. Two integration constants ride in, and on a
record tens of masses long they are not small: the low-frequency end of a
numerical Ψ₄ stream carries drift (gauge, near-zone content, junk the gate
could not reach), and dividing drift by `f²` turns it into a parabola that
dwarfs the wave.

`templates/nr.py` uses **fixed-frequency integration** (Reisswig & Pollney
2011), with the divisor *clamped* below `f₀` rather than rolled off — a
filter that zeroes a band cannot be told apart from a signal that has none.
Two guards decide `f₀`, and neither is a free dial:

1. the lowest instantaneous frequency the record carries over its body
   (measured with the figures' own energy-weighted phase derivative, so the
   search and Fig. `psi4_ligo`(c) cannot disagree), times 0.75;
2. **never below one cycle per record, `1/T`.** A record of length `T`
   cannot tell a wave at `f < 1/T` from a drift — there is less than a cycle
   of it — so clamping below `1/T` does not protect signal, it amplifies the
   integration constants.

Guard 2 is not hypothetical. The fly-by's instantaneous frequency genuinely
falls to `fM = 0.0098` as the pair separates, while its record resolves only
`1/T = 0.029`. Without the floor the clamp sat at 0.0073, **98 % of the
reconstructed strain's power landed below half the resolved Ψ₄ peak**, `|h|`
at the record's *ends* came out 0.83 of its peak — a pedestal with a wiggle
on it — and the burst was reported at 100× the article's amplitude.

`drift` (table above) is the residual of exactly this: `|h|` at the record's
ends over `|h|` at its peak. Below ~0.1 the record integrates cleanly. **The
head-on, spiral and fly-by sit at 0.3–0.4, and their low-frequency strain is
an upper bound, not a measurement.** The search protects itself by filtering
each template only from its own corner `1/T` in Hz and never below
(`BankTemplate.f_lower_hz`): SNR harvested from a band the simulation never
resolved is not SNR.

### Orientation

The figures plot the mode coefficient `|r Ψ₄| M`. A detector sees
`h = Σ h_ℓm · ₋₂Y_ℓm(θ,φ)`, so each arm is given its **optimal** orientation:
(2,2) face-on, `√(5/4π) = 0.631`; (2,0) edge-on, `√(15/32π) = 0.386`, since a
head-on axis radiates nothing along itself. Every horizon quoted by the
search is in that convention; divide by ≈2.26 for the sky-and-orientation
average.

---

## 3. The validation that can fail

Everything above rests on a step that is easy to get wrong and impossible to
check by eye. The campaign supplies its own control: the **vacuum BBH twin**
is an equal-mass non-spinning binary *black hole* evolved with the same code,
grid and extraction. Whatever a wormhole merger looks like, this one has to
look like a binary black hole.

```
python -m grteclyn_wrapper.gw_search.cli validate
```

```
  M_NR  FF(full model)  FF(same window)  M recovered   error
    60           0.488            0.902           57   -5.0%
   100           0.395            0.908          100   +0.0%
   150           0.631            0.911          158   +5.0%
   200           0.613            0.922          200   +0.0%
   300           0.608            0.938          360  +20.0%

VERDICT: PASS -- same-window match 0.902-0.938 against a threshold of 0.85
```

Two numbers, answering different questions. Against the **full** IMRPhenomD
waveform the twin scores 0.40–0.63 — not a failure, but the answer to a
different question: the model spends seconds in band climbing an inspiral
ramp, while the twin's record is 75 M of merger with no inspiral attached,
so most of the model's power has nothing to align with. Cut the model to the
twin's **own window** about its peak and the comparison is like for like:
**0.90–0.94, recovering the correct total mass.** The residual few per cent
is accounted for — the twin's momentum is 59 % of circular so it is an
eccentric plunge, its record is short, and it is extracted at `R = 14` rather
than at infinity.

**Read every wormhole channel's fitting factor against that 0.90–0.94
ceiling, never against 1.**

### 3a. And the one that tests the pipeline, not the templates

Correct templates in a broken pipeline recover nothing, and the failure is
silent in the worst way: an empty trigger list looks exactly like a quiet sky.
So `gws inject` adds each channel to **real O3 conditioned strain** at the
distance that gives optimal SNR 20, then searches it with the whole bank —
not with the injected template alone, which would test an inner product
rather than a search.

```
found 15/15; recovered/optimal SNR 0.93-1.39 (median 1.03); chi2_r 0.60-4.82
```

Every injection recovered, at its own time to within 3 ms, at 93–139 % of
optimal (median 103 %; above 1 is noise adding to signal, plus the bank's
neighbouring rungs). χ² stays near 1 for the long templates — a real signal
is *not* vetoed — and that is the check that would have caught the bug below.

The one row that does not pass cleanly is the shortest template in the bank,
`fly-by@18.4` (5 ms, 4 χ² bins): χ²ᵣ = 4.82 pushes SNR 27.8 down to
newsnr 14.2. That is the documented weakness of a bin test on a template with
almost no time–bandwidth product, it is confined to the lowest-mass fly-by
rungs, and it costs sensitivity there rather than producing false triggers.

**A bug this caught.** The χ² call passed PyCBC the *normalised* SNR where it
wants the unnormalised one alongside `snr_norm`, which squares the norm twice.
On an injection of the filter's own template this returned χ²ᵣ = 28.7 instead
of ≈ 1 and demoted a perfect SNR-19.6 signal to newsnr 4.1. A search carrying
that bug finds nothing and reports a quiet sky.

---

## 4. Why a bare SNR is not a result

Advanced LIGO data is neither Gaussian nor stationary. SNR 8 triggers arrive
constantly and essentially all of them are glitches. The script that lived
here before 2026-09-18 printed `*** TRIGGER FOUND *** SNR 9.3` and stopped,
which establishes nothing. Three steps turn a number into a statement:

1. **χ² veto** (`pipeline/ranking.py`). Allen's bin test asks whether a
   trigger's SNR arrived spread across frequency bands, as a signal's must,
   or dumped into one, as a glitch's does. The ranked statistic is the
   reweighted `newsnr`, never `ρ`. *Caveat specific to this bank:* the veto's
   power grows with the template's time–bandwidth product, and these
   templates are 5–125 ms. `chisq_bins` scales the bin count accordingly and
   returns as few as 4, so the veto is weaker here than in a CBC search — and
   the background measures whatever it failed to remove, which is the point
   of measuring rather than assuming.
2. **Coincidence** (`pipeline/coincidence.py`). Both detectors, same
   template, within the 10 ms light-travel time plus timing error.
3. **Time-slide background** (`pipeline/background.py`). Shift one detector
   past the other; every surviving coincidence is accidental by construction.
   `N` slides of `T` seconds buy `N·T` of background. The FAR is
   `(N_louder + 1)/T_bg` — the `+1` is what stops an event louder than every
   slide being reported at infinite significance from a finite experiment.

The templates are short, so the bank is cheap, so the slides can run into the
thousands. What is lost on the veto is bought back on the statistics.

---

## 5. Structure

Each layer depends only on the layer below and on `interfaces.py`; nothing
depends on `cli.py`.

```
cli.py          entry points; the only module that formats for a human,
                and the only place concrete pieces are chosen and injected
analysis/       what the templates MEAN, with no data:
                  fitting_factor.py   would the modelled searches find them?
                  validation.py       the Ψ₄ → h chain vs IMRPhenomD
pipeline/       the search:
                  triggers.py         matched filter + χ² + clustering
                  ranking.py          NewSNR
                  coincidence.py      H1–L1 pairing
                  background.py       time slides → FAR
                  search.py           the orchestrator
templates/      campaign waveforms as filters:
                  nr.py               Ψ₄ → h, the ARMS table → NRWaveform
                  bank.py             the mass ladder
strain/         detector data:
                  gwosc.py            GWOSC source + cache
                  conditioning.py     high-pass, resample, crop
                  noise.py            WelchNoise (measured) / DesignNoise
interfaces.py   the Protocols the above are wired together with
```

`interfaces.py` is dependency inversion in the useful sense, not the
decorative one. `Search` is written against those names only, so:

* swapping `StrainSource` for one returning coloured noise plus a known
  injection tests the pipeline end to end without the network;
* swapping `NoiseModel` between the measured Welch estimate and the aLIGO
  design curve is how a *projection* is kept distinct from a *measurement* —
  quoting a design-curve horizon as a search result overstates a null result
  by a factor of a few;
* adding a radiating channel is a new row in `ARMS` and nothing else.

### Where the data goes

Downloaded strain is cached as float64 `.npz` keyed by
`(ifo, gps_start, gps_end, rate)` in **`<repo>/runs/gw_search/strain_cache`**
(override with `GW_SEARCH_CACHE`). It is bulk detector data, not source, so
it lives outside the package and is git-ignored. Re-running the analysis —
different ranking, more slides — touches the network zero times, which is
what makes the background cheap to re-derive and the article's numbers
reproducible years later.

### How the data gets here

**Not through the proxy.** This environment exports
`http(s)_proxy=http://127.0.0.1:8119`, and `GwoscStrainSource` clears it on
construction (`use_cluster_network_directly`) so the archive is reached over
the cluster's own route. Two reasons, measured on the same 4 MB range request
of an O3b strain file on 2026-09-18:

| route | throughput |
|---|---|
| via `127.0.0.1:8119` | 884 kB/s |
| direct | 1580 kB/s |

Speed is the smaller half. That proxy is one local process, and when it
exited mid-scan every in-flight fetch died together with
`ProxyError('Unable to connect to proxy', ConnectionRefused)` — 0 of 2 blocks
and an hour of downloads lost, in a log that reads exactly like an
unreachable archive. Set `GW_SEARCH_USE_PROXY=1` to keep whatever the
environment exports, on a host where the proxy is the only way out.

Note that gwpy downloads the whole enclosing 4096 s GWOSC file (~130 MB)
however little of it is asked for, so `--block-s 4096` costs the same
transfer as `--block-s 512` and yields eight times the livetime. The
per-fetch deadline scales with the request for the same reason.

---

## 6. Running it

```bash
export PYTHONPATH=$PWD/grteclyn-wrapper/src
alias gws="grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.gw_search.cli"

gws templates                 # the five arms as templates, and their quality
gws validate                  # the Ψ₄ → h chain against IMRPhenomD  [must PASS]
gws fitting-factor --out results/merger/gw_search/fitting_factors.json
gws inject --duration 128 --target-snr 20 \
           --out results/merger/gw_search/injections.json   # [must PASS]
gws scan --gps-start 1264317000 --gps-end 1264340000 \
         --block-s 4096 --max-blocks 6 --workers 3 --slides 5000 \
         --out results/merger/gw_search/o3b_scan.json
gws events --event GW190521   # the bank against a catalogue event
```

Dependencies are the `gw-search` extra: `uv sync --extra gw-search`.

A `scan` block costs ≈95 s for the 125-template bank across two detectors;
bank placement is a one-off ≈2 min. Downloads are ≈130 MB per detector per
GWOSC file, which is ≈80 s direct and several minutes through the proxy the
source now bypasses.

---

## 7. Results

See `results/merger/gw_search/` for the JSON each run writes, and the
article's Sec. V for what they mean.
