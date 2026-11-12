"""Decay scales for massive scalar bound states."""
import math

# When omega >= mass the field is unbound (no exponential confinement); fall back
# to this finite decay scale so the width stays sane instead of diverging.
_UNBOUND_FALLBACK_KAPPA = 1.0 / 16.0


def bound_width(mass: float, omega: float) -> float:
    """Physical bound-state size R = 1 / sqrt(m^2 - omega^2).

    This is the decay length of a massive complex scalar oscillating at omega:
    the field cannot localize tighter than R without huge gradient energy, so a
    lump narrower than R is not a bound state and disperses.  Returns a large but
    finite width when omega >= mass (marginally/unbound).
    """
    kappa_sq = float(mass) * float(mass) - float(omega) * float(omega)
    kappa = math.sqrt(kappa_sq) if kappa_sq > 0.0 else _UNBOUND_FALLBACK_KAPPA
    return 1.0 / max(kappa, _UNBOUND_FALLBACK_KAPPA)
