# SpinningWormhole

Nonlinear evolution of **one rotating Ellis–Bronnikov wormhole** (Kleihaus–Kunz
family: real phantom scalar, rotation in the metric). Plan:
`research/spinningwormhole/SpinningWormhole.md`; campaign state:
`research/spinningwormhole/STATUS.md`. Replaces the deleted
`RotatingWormholeCollapse` (2026-10-10), whose complex-scalar phase winding put
the angular momentum in the matter, not the geometry.

**One background format, no in-code families.** All physics input is a
tabulated stationary background (`.spinbg`): f, ν̄ = ν/sin²θ, ω (+ exact
derivatives), φ on a grid in (x, μ) = ((2/π) atan(η/η₀), cos θ). Static,
O(J²) and full numerical backgrounds all arrive through this file, generated
by `grteclyn_wrapper.analysis.spinning_wormhole.backgrounds`; the C++ never
changes with the family.

| file | responsibility |
|---|---|
| `RotatingBackgroundTable.hpp` | load + GPU-sample the `.spinbg` table |
| `SpinningWormholeInitialData.hpp` | background → CCZ4 variables (conventions in its header) |
| `InitialGammas.hpp` | Γ̃^i from h_ij by FD (the metric is not conformally flat) |
| `SpinningWormholeLevel.{hpp,cpp}` | initData, CCZ4+matter RHS, sponge, tagging, diagnostics |
| `SpinningThroatDiagnostics.hpp` | R_eq(t), R_pol(t), min(−g_tt) → `throat_geometry.dat` |
| `CoreRadialProfile.hpp` | radial min/max profile (shared with the merger example) |
| `SimulationParameters.hpp` | the `spinning_*` parameter namespace |

The static limit (f = 2u, ν = ω = 0) is exactly the merger campaign's massive
drainhole — the cross-check for the whole pipeline (plan Step 0).

**Output streams** (`data/`): `constraint_norms.dat`,
`collapse_diagnostics.dat` (merger's 10-column contract),
`throat_geometry.dat` (ergo_min < 0 ⇒ ergoregion), optional
`core_radial_profile.dat`, `Weyl4_mode_*.dat`.

**Build and run** — only through the campaign scripts
(`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`): `build_binary.sh
--tag <word>`, then `launch.sh --template ... --name ... --gpu ... --profile
... --binary <bin>`. Smoke test: `params_test.txt` (its header says how to
generate the static `background.spinbg`).
