"""The generated campaign entry point must survive multiprocessing spawn."""
import os
from pathlib import Path
import re
import subprocess
import sys


def test_generated_post_entry_does_not_reenter_cli_in_spawned_children(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = (root/'scripts/campaigns/spinning_wormhole/run_single.sh').read_text()
    body = re.search(r'cat > "\$\{RUN_DIR\}/post.py" <<PY\n(.*?)\nPY', script, re.S).group(1)
    (tmp_path/'post.py').write_text(body.replace('${CONSUMER_MOD}', 'spawn_probe')+'\n')
    package = tmp_path/'spawn_probe'; package.mkdir()
    (package/'__init__.py').write_text('')
    (package/'__main__.py').write_text(
        'from .worker import main\nif __name__ == "__main__":\n    main()\n')
    (package/'worker.py').write_text('''import os
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
def square(value):
    return value*value, os.environ['OMP_NUM_THREADS']
def main():
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn')) as pool:
        print(list(pool.map(square, range(4))))
''')
    result = subprocess.run([sys.executable, str(tmp_path/'post.py')],
        cwd=tmp_path, env={**os.environ, 'PYTHONPATH':str(tmp_path),
                          'SWH_CONSUMER_THREADS':'1'},
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[(0, '1'), (1, '1'), (4, '1'), (9, '1')]"
