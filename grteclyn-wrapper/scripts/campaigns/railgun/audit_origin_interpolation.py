#!/usr/bin/env python3
"""Read-only origin roundoff audit; no JAX backend or numerical solve starts.

Measures angular origin coefficients and radial slopes of the actual saved
interpolant. These diagnose amplification near r=0; they do not replace the
independent Cartesian curvature certificate.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from grteclyn_stationary.railgun.geometry import interpolation_coefficients


def audit(path):
    with np.load(path,allow_pickle=False) as saved:
        meta = json.loads(str(saved['metadata']))
        nx,ny = meta['nx'],meta['ny']
        n = (nx+1)*(ny+1)
        result = {}
        for index,name in enumerate(('f','w','N','b')):
            values = saved['u'][index*n:(index+1)*n].reshape(nx+1,ny+1)
            coefficients = interpolation_coefficients(values).astype(np.longdouble)
            origin = np.polynomial.chebyshev.chebval(np.longdouble(-1),coefficients)
            derivative = np.polynomial.chebyshev.chebder(coefficients,axis=0)
            slope = np.polynomial.chebyshev.chebval(np.longdouble(-1),derivative)*2/meta['length']
            result[name] = dict(nodal_angular_spread=float(np.ptp(values[-1])),
                origin_nonconstant_coefficient_max=float(abs(origin[1:]).max()),
                origin_radial_slope_coefficient_max=float(abs(slope).max()))
    return dict(source=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                grid=[nx,ny],fields=result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources',nargs='+',type=Path)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    payload = dict(method='DCT-I in long double, float64 coefficients as in RingGeometry; '
                  'long-double endpoint evaluation without filtering',
                  curvature_certified=False,records=[audit(path) for path in args.sources])
    text = json.dumps(payload,indent=2)+'\n'
    if args.out:
        args.out.write_text(text)
    else:
        print(text,end='')
