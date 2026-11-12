"""Shape-domain restrictions, separate from stationary or stability validation."""
import numpy as np

DOMAINS = ("positive", "endpoint-positive")


def shape_diagnostics(q):
    """Exact polynomial extrema on the closed field interval, including endpoints."""
    coeff = np.asarray([1., *q], dtype=float)
    if not np.isfinite(coeff).all():
        raise ValueError("nonfinite potential coefficients")
    derivative = np.polynomial.polynomial.polyder(coeff)
    roots = np.polynomial.polynomial.polyroots(derivative)
    points = [0., 1.] + [float(z.real) for z in roots
                         if abs(z.imag) < 1e-12 and 0. < z.real < 1.]
    values = np.polynomial.polynomial.polyval(points, coeff)
    i = int(np.argmin(values))
    return dict(min_Q=float(values[i]), min_Q_u=points[i],
                Q_end=float(np.sum(coeff)), negative_interior=bool(values[i] < 0.))


def admissible(q, domain="positive"):
    if domain not in DOMAINS:
        raise ValueError(f"unknown potential domain: {domain}")
    try:
        info = shape_diagnostics(q)
    except (ValueError, np.linalg.LinAlgError):
        return False
    return info["Q_end" if domain == "endpoint-positive" else "min_Q"] > 0.


def validate_start(args, q, error):
    """Reject invalid domains before selecting a GPU or creating outputs."""
    if args.potential_domain == "endpoint-positive" and not args.m_min > 0.:
        error("endpoint-positive searches require --m-min > 0 for massive vacua")
    if not admissible(q, args.potential_domain):
        error("--x0 violates the selected potential domain")
