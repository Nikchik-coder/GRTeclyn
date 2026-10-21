# The spectral solver's solutions

`solutions.tsv` holds every solution the solver saved: 462 stationary rotating
Ellis–Bronnikov wormholes in 20 continuation legs, one row each, tab-separated with
one header line. A leg follows one family (fixed η0 and γ) in steps of the angular
momentum J; each converged Newton step is one row. Numbers are written at full double
precision for the figure scripts; `grteclyn_wrapper.visualisation.spinning_wormhole.solutions.load`
reads the table back.

## Columns

Conventions and symbols follow the paper (Sec. II) and Chew, Kleihaus and Kunz,
Phys. Rev. D 94, 104031 (2016). Lengths are in units of the family's η0 as listed.

| Column | Meaning |
|---|---|
| `leg`, `step` | the continuation leg and the step along it |
| `eta0` | the throat parameter η0 |
| `gamma` | γ, the value of f at η → −∞: how unequal the two ends are |
| `omega_inf` | ω∞, the angular velocity of the η → −∞ end |
| `map`, `map_L` | the radial compactification: `arctan`, x = (2/π) arctan(η/η0), or `logstretch` with stretch `map_L` |
| `nx`, `ny` | the grid: Chebyshev modes in x, cosine modes in θ |
| `J` | the angular momentum |
| `v_e` | the equatorial rotation velocity of the throat, R_e Ω_throat |
| `mu_plus`, `mu_minus` | the masses of the η → +∞ and η → −∞ ends (μ+ is the ADM mass) |
| `D` | the scalar charge |
| `R_e`, `R_pol` | the throat's equatorial and polar circumferential radii |
| `R_A` | the throat's areal radius, (A/4π)^1/2 |
| `Omega_throat` | ω on the throat's equator |
| `eta_throat` | η of the throat, the area-minimizing η = const surface |
| `tail_max` | the largest ratio of the last three Chebyshev coefficients to the largest, over the fields and both directions (the asymptotic tails of Table I) |
| `Ec_rel` | the largest residual of the first-order constraint, Eq. (6) of the paper, relative to its largest term |
| `D2_spread` | the largest relative deviation of the pointwise D² from its median over the domain |
| `J_spread` | the largest relative deviation of the angular-momentum flux through η = const surfaces from its median |
| `smarr_rel` | the relative residual of the Smarr relation μ+ + μ− = 2 ω∞ J |

The last five columns are computed on every solution from equations the solver does not
solve. The continuation refines the grid by a factor 1.5 whenever `tail_max` exceeds
1e-11, up to 192 Chebyshev modes; the full Einstein-equation residual of the paper's
Table I is evaluated separately and is not a column here.

## Legs

Family (a) is the drainhole family the paper evolves, family (b) the symmetric family
compared with Kleihaus and Kunz (Fig. 2); the comparison legs are the fixed-γ families of
Chew, Kleihaus and Kunz used for Table II. "Packed": each solution of the leg is also in
`../solutions/<leg>/` as a `.json` (parameters, charges, checks) and an `.npz` (the metric
functions f, ω and ν on the spectral grid).

| Leg | Family | γ | η0 | Map | Grid | v_e | Rows | Packed |
|---|---|---|---|---|---|---|---|---|
| `anchor_g0` | comparison | 0 | 1 | arctan | 48×12 | 0.22–0.85 | 26 | no |
| `anchor_g0_r1` | comparison | 0 | 1 | arctan | 48×12–72×18 | 0.86–0.97 | 19 | no |
| `anchor_g1b` | comparison | 1 | 1 | arctan | 48×12 | 0.09–0.97 | 32 | no |
| `anchor_g1b_r1` | comparison | 1 | 1 | arctan | 48×12–108×28 | 0.98–1.06 | 33 | no |
| `anchor_g2` | comparison | 2 | 1 | arctan | 48×12 | 0.75–0.98 | 9 | no |
| `anchor_g2b` | comparison | 2 | 1 | arctan | 48×12 | 0.04–1.01 | 23 | no |
| `anchor_g2b_r1` | comparison | 2 | 1 | arctan | 48×12–162×42 | 1.03–1.22 | 56 | no |
| `anchor_g2b_r2` | comparison | 2 | 1 | arctan | 162×42–192×64 | 1.03–1.09 | 31 | no |
| `anchor_gm1` | comparison | −1 | 1 | arctan | 48×12 | 0.13–0.74 | 26 | no |
| `anchor_gm1_r1` | comparison | −1 | 1 | arctan | 48×12 | 0.75–0.83 | 7 | no |
| `fam_a` | (a) drainhole | −π | 2 | arctan | 48×12–72×18 | 0.06–0.20 | 9 | yes |
| `fam_a_log` | (a) drainhole | −π | 2 | logstretch | 96×20–144×30 | 0.06–0.99 | 65 | yes |
| `fam_a_p4` | (a) drainhole | −π | 2 | arctan | 108×28–162×42 | 0.91–0.95 | 16 | yes |
| `fam_a_p4b` | (a) drainhole | −π | 2 | arctan | 162×42 | 0.95–0.96 | 6 | yes |
| `fam_a_r1` | (a) drainhole | −π | 2 | arctan | 72×18–108×28 | 0.21–0.91 | 33 | yes |
| `fam_b` | (b) symmetric | 0 | 1 | arctan | 48×12 | 0.22–0.85 | 26 | yes |
| `fam_b_low` | (b) symmetric | 0 | 1 | arctan | 48×12 | 0.02–0.20 | 10 | yes |
| `fam_b_p4` | (b) symmetric | 0 | 1 | arctan | 48×12–72×18 | 0.91–0.95 | 7 | yes |
| `fam_b_p4b` | (b) symmetric | 0 | 1 | arctan | 72×18 | 0.96–0.99 | 21 | yes |
| `fam_b_r1` | (b) symmetric | 0 | 1 | arctan | 48×12 | 0.86–0.91 | 7 | yes |
