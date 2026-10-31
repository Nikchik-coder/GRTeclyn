"""Pipeline commands retain caps and never launch on an unchecked device."""
from types import SimpleNamespace

import pytest


def config():
    return dict(campaign=dict(runner='runner.sh', python='python'),
                defaults=dict(threads=4, mem_gb=12, gpu_mem_gb=22, timeout_s=60))


def stages():
    return {'trial': dict(name='trial', module='example.solve', args=['seed.npz'], threads=2)}


@pytest.mark.parametrize('gpu,mem', [(None, '12'), (0, '22')])
def test_command_caps_and_dry_run(command, monkeypatch, gpu, mem):
    p = command('pipeline')
    calls = []
    def run(cmd, **kw):
        calls.append((cmd, kw))
        return SimpleNamespace(stdout='0, 0, 0\n', returncode=0)
    monkeypatch.setattr(p.subprocess, 'run', run)
    assert p.cmd_run(config(), stages(), 'trial', gpu, True, False) == 0
    assert all(c[0][0] == 'nvidia-smi' for c in calls)
    assert p.cmd_run(config(), stages(), 'trial', gpu, False, False) == 0
    cmd, kw = calls[-1]
    assert cmd[:3] == ['bash', str(p.repo_root() / 'runner.sh'), 'start']
    assert cmd[cmd.index('--threads')+1] == '2'
    assert cmd[cmd.index('--mem')+1] == mem
    assert cmd[cmd.index('--timeout')+1] == '60'
    assert kw['cwd'] == p.repo_root()
    if gpu is not None:
        assert cmd[-2:] == ['--gpu', '0']


@pytest.mark.parametrize('output,code', [('', 0), ('1, 0, 0\n', 0),
                                        ('0, N/A, 0\n', 0), ('0, 0, 0\n', 1)])
@pytest.mark.parametrize('force', [False, True])
def test_unverified_gpu_never_launches(command, monkeypatch, output, code, force):
    p = command('pipeline')
    def run(cmd, **kw):
        assert cmd[0] == 'nvidia-smi', 'an unverified job was launched'
        return SimpleNamespace(stdout=output, returncode=code)
    monkeypatch.setattr(p.subprocess, 'run', run)
    with pytest.raises(SystemExit, match='pipeline:'):
        p.cmd_run(config(), stages(), 'trial', 0, False, force)


def test_missing_gpu_tool_never_launches(command, monkeypatch):
    p = command('pipeline')
    def run(*a, **kw):
        raise FileNotFoundError('nvidia-smi')
    monkeypatch.setattr(p.subprocess, 'run', run)
    with pytest.raises(SystemExit, match='pipeline:'):
        p.cmd_run(config(), stages(), 'trial', 0, False, False)


def test_busy_gpu_and_unknown_stage(command, monkeypatch):
    p = command('pipeline')
    monkeypatch.setattr(p.subprocess, 'run', lambda *a, **kw:
                        SimpleNamespace(stdout='0, 6000, 10', returncode=0))
    with pytest.raises(SystemExit, match='busy'):
        p.cmd_run(config(), stages(), 'trial', 0, False, False)
    with pytest.raises(SystemExit, match='no stage'):
        p.cmd_run(config(), stages(), 'absent', None, False, False)
    cfg, loaded = p.load()
    assert loaded and len(loaded) == len(cfg['stage'])


@pytest.mark.parametrize('verb,rest', [('status', []), ('tail', ['trial','5']), ('stop', ['trial'])])
def test_job_operations_forward_arguments_and_exit_code(command, monkeypatch, verb, rest):
    p = command('pipeline')
    calls = []
    def run(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(returncode=7)
    monkeypatch.setattr(p.subprocess, 'run', run)
    assert p.passthrough(config(), verb, rest) == 7
    assert calls == [['bash', str(p.repo_root()/'runner.sh'), verb, *rest]]
