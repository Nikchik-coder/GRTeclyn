"""Resume certificates include the shared algorithms after relocation."""
import hashlib
from pathlib import Path
from types import SimpleNamespace

from grteclyn_stationary.studies.runner import source_manifest


def test_source_manifest_covers_numerics_and_spinning_model(tmp_path):
    reference = tmp_path / 'reference.json'
    reference.write_text('{}')
    reference.with_suffix('.npz').write_bytes(b'fixture')
    options = ('nx ny x0 m_min m_max q_min q_max potential_domain maxfev engine seed '
               'sigma0 popsize fatol m_step walk_max_splits walk_max_iter free_J '
               'J_min J_max J_step').split()
    manifest = source_manifest(reference, {'candidate_seeds': []},
                               SimpleNamespace(**dict.fromkeys(options)), 'fixture')
    package = Path(__file__).resolve().parents[2] / 'packages/stationary/src/grteclyn_stationary'
    for name in ('numerics/newton.py', 'numerics/jacobian.py', 'numerics/spectral.py',
                 'numerics/device.py', 'spinning_wormhole/equations.py',
                 'matter/equations.py', 'profiles/boson_star_ode.py'):
        assert manifest['code'][name] == hashlib.sha256((package / name).read_bytes()).hexdigest()
