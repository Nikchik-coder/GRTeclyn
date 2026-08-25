# GRTeclyn — research fork

> **This is a research fork**, not the upstream code. It tracks
> [GRTLCollaboration/GRTeclyn](https://github.com/GRTLCollaboration/GRTeclyn)
> and adds a numerical-relativity research tree on top of it. The upstream
> project description follows below.
>
> | Added here | What it is |
> |---|---|
> | [`grteclyn-wrapper/`](grteclyn-wrapper/README.md) | Python orchestration layer — GRTresna initial data → GPU evolution → scoring, plus MAP-Elites / CMA-ES search campaigns. **Start here.** |
> | [`results/`](results/) | Packed, scrubbed campaign extracts. Reproducible without a GPU. |
>
> **Headline result — the Bondi dipole runaway.** A positive-mass boson star
> paired with a negative-mass phantom one self-accelerates, with no horizon and
> no numerical artefact. Both axes of `a = GM/d²` are measured directly:
> `a ∝ d^−2.028` across separations, `a ∝ M^0.966 ± 0.061` across a ×2.46 mass
> range. Data and method:
> [`results/bondi-dipole-runaway/`](results/bondi-dipole-runaway/)
>
> Upstream GRTeclyn is BSD-3-Clause; see [LICENSE](LICENSE). The research tree
> inherits it.

---

# GRTeclyn

GRTeclyn (previously referred to as GRAMReX) is a new numerical relativity code developed by the [GRTL Collaboration](https://www.grtlcollaboration.org) that is currently still under development.  It is a port of the [GRChombo code](https://github.com/GRChombo/GRChombo) (based on the Chombo libraries) to the [AMReX](https://amrex-codes.github.io/) library in order to leverage AMReX's support for GPUs and ongoing active development.

The AMReX documentation can be found [here](https://amrex-codes.github.io/amrex/docs_html).

The name follows a similar pattern to GRChombo, namely "GR" + "\<Tool in a foreign language\>". In this case, "Teclyn" is a Welsh word for "Tool".

## Development status

Please consult this [documentation page](https://grtlcollaboration.github.io/GRTeclyn/#summary-of-features) for a list of the development status of specific features.

## Documentation

Documentation can be found [here](https://grtlcollaboration.github.io/GRTeclyn/) (under construction). Note that the GitHub wiki is no longer in use.

The documentation contains useful information on obtaining and building the code, prerequisities and running the binary black hole example.

## License

GRTeclyn is licensed under the BSD 3-Clause License. Please see [LICENSE](LICENSE) for details.