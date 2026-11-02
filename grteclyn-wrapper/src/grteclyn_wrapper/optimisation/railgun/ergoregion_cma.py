"""CMA-ES chooses central redshift; bounded continuation solves the fields.

For the fixed k=1 free massive scalar model this is a one-parameter branch
search. Numerical map scales are not represented as physical dimensions.
Failed trials receive penalties and never become accepted fields. Only
three-grid acceptance can establish the sampled ergoregion target.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np

from .ergoregion_scan import common_metric_samples, extra_checks


class BudgetExhausted(RuntimeError):
    pass


@dataclass
class SolveBudget:
    search_limit: int
    refinement_limit: int
    search_used: int = 0
    refinement_used: int = 0

    def take(self, refinement=False):
        key = 'refinement' if refinement else 'search'
        used, limit = f'{key}_used', f'{key}_limit'
        if getattr(self, used) >= getattr(self, limit):
            raise BudgetExhausted(key)
        setattr(self, used, getattr(self, used)+1)


def score(record, sample=None):
    """Every independently passing candidate outranks every failed trial."""
    if record.get('verdict') == 'PASS' and record.get('independent') and sample is not None:
        ratio = sample.get('shift_norm_over_lapse_max', float('nan'))
        if np.isfinite(ratio) and ratio >= 0:
            return 1/(1+ratio)
    residual = record.get('newton', {}).get('res_scaled_inf')
    if residual is None or not np.isfinite(residual):
        return 4.
    return 2.+float(np.clip(np.log10(max(1., abs(residual)/1e-14)), 0., 20.))/20.


def next_log_lapse(current, target, maximum):
    return float(current+np.clip(target-current, -maximum, maximum))


def predictor(current, older, target_log, current_log, older_log):
    if older is None or abs(current_log-older_log) < 1e-4:
        return np.array(current, copy=True)
    ratio = np.clip((target_log-current_log)/(current_log-older_log), -2., 2.)
    return current+ratio*(current-older)


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def write(path, value):
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n')


def bounded_cma(config, objective, stop):
    """The wormhole search's ask/tell loop with a strict partial-population cap."""
    import cma
    es = cma.CMAEvolutionStrategy([config['x0']], config['sigma0'],
         dict(bounds=[[config['central_lapse_bounds'][0]], [config['central_lapse_bounds'][1]]],
              popsize=config['popsize'], maxfevals=config['max_evaluations'],
              seed=config['seed'], verbose=-9, verb_log=0,
              # pycma 4.4.4 cannot clip a one-dimensional sigma_vec. Its
              # boundary transform still enforces the physical lapse bounds.
              maxstd=float('inf')))
    count, reason = 0, 'cma_stop'
    try:
        while not es.stop() and count < config['max_evaluations'] and not stop():
            xs, values = es.ask(), []
            for x in xs:
                if count >= config['max_evaluations'] or stop():
                    break
                count += 1
                values.append(objective(float(x[0])))
            if len(values) == len(xs):
                es.tell(xs, values)
        if stop():
            reason = 'validated_ergoregion'
        elif count >= config['max_evaluations']:
            reason = 'evaluation_budget'
    except BudgetExhausted as error:
        reason = 'refinement_solve_budget' if str(error) == 'refinement' else 'search_solve_budget'
    return dict(reason=reason, criteria=dict(es.stop()), evaluations_started=count,
                cma_version=cma.__version__)


def preflight(source, config):
    expected = dict(source_sha256='e586e4c1a4048773dcb4e3be87c67ce6cd523f7846b371a716cb4b1981b150ff',
                    central_lapse_bounds=[.14, .41], x0=.30, sigma0=.05, seed=171, popsize=4,
                    max_evaluations=32, max_search_solves=80, max_finalists=3,
                    max_refinement_solves=9, max_log_lapse_step=.04, max_splits_per_evaluation=4,
                    search_grid=[128, 16], grids=[[128, 16], [160, 20], [192, 24]],
                    length=2.5, max_iter=30, newton_tol=1e-14, equation_tol=1e-8,
                    tail_tol=1e-6, observable_tol=1e-6)
    maximising = config.get('mode') == 'maximise'
    if maximising:
        if config.get('seed') not in (271, 272):
            raise ValueError('bounded maximisation seeds 271 or 272 required')
        expected.update(mode='maximise', seed=config['seed'],
            source_sha256='a173848c072ce0e618a6995b8b13154570a2a94f2fc58fd1845795ad853cbb52',
            central_lapse_bounds=[.08, .32], x0=.20, sigma0=.05,
            max_finalists=4, max_refinement_solves=12, finalist_log_separation=.02,
            search_grid=[160, 20], grids=[[160, 20], [192, 24], [224, 28]])
    if config != expected:
        raise ValueError('one of the bounded discovery/maximisation CMA profiles is required')
    if hashlib.sha256(Path(source).read_bytes()).hexdigest() != config['source_sha256']:
        raise ValueError('accepted source hash mismatch')
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.asarray(data['u'])
    fields = meta['fields']
    n = (meta['nx']+1)*(meta['ny']+1)
    if (meta.get('schema') != 1 or meta.get('model') != 'canonical_regular_centre'
            or not meta.get('validated') or meta.get('target_j') is not None
            or (meta.get('central_lapse') is not None and not maximising)
            or any(meta.get('frequency_targets', []))
            or len(fields) != 1 or fields[0]['winding'] != 1 or fields[0]['mass'] != 1
            or fields[0]['parity'] != 'even' or fields[0]['quartic'] or fields[0]['sextic']
            or meta['length'] != 2.5 or [meta['nx'], meta['ny']] != [192, 24]
            or u.shape != (5*n+1,) or not np.isfinite(u).all()):
        raise ValueError('accepted canonical single-ring source required')
    central = float(np.exp(np.mean(u[:n].reshape(193, 25)[-1])/2))
    if maximising and (meta.get('central_lapse') is None or abs(meta['central_lapse']-central) > 1e-12):
        raise ValueError('maximisation requires the accepted central-lapse ergoregion source')
    return dict(metadata=meta, central_lapse=central, initial_frequency=float(u[-1]),
                max_newton_solves=config['max_search_solves']+config['max_refinement_solves'],
                numerical_execution=False,
                physical_parameters=['central lapse; frequency and amplitude solved'],
                model='unchanged k=1, m=1 canonical free scalar')


class Search:
    def __init__(self, source, config, directory):
        from .workflow import load_state
        self.plan = preflight(source, config)
        self.config, self.source, self.directory = config, Path(source), Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.budget = SolveBudget(config['max_search_solves'], config['max_refinement_solves'])
        p, u, _ = load_state(source)
        if p.jax.devices()[0].platform != 'gpu':
            raise RuntimeError('GPU required; CPU fallback refused')
        self.floor = .001*float(p.charge_integrals(u)[0])
        if not np.isfinite(self.floor) or self.floor <= 0:
            raise ValueError('positive source charge required')
        self.pool = [dict(log=math.log(self.plan['central_lapse']), p=p, u=u, path=str(source))]
        self.evaluations, self.finalists = [], []
        self.found, self.best_path, self.best_ratio = False, None, -1.
        self.best_ergo_ratio = -1.
        self.best_log = self.pool[0]['log']
        self.incumbent_ratio = None
        if config.get('mode') == 'maximise':
            sample = common_metric_samples(source)
            if sample['gtt_max'] <= 0 or sample['shift_norm_over_lapse_max'] <= 1:
                raise ValueError('positive ergoregion required in the maximisation source')
            self.incumbent_ratio = self.best_ratio = self.best_ergo_ratio = sample['shift_norm_over_lapse_max']
            self.found = True
            self.best_path = str(self.directory/'incumbent.npz')
            for name in ('incumbent.npz', 'best_validated.npz', 'accepted_ergoregion.npz'):
                shutil.copy2(source, self.directory/name)
            write(self.directory/'incumbent.json', sample)
        self.started = time.monotonic()
        self.manifest = dict(config=config, plan=self.plan, source=str(source),
                             commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
                             platform=p.jax.devices()[0].platform, float64=bool(p.jax.config.jax_enable_x64),
                             minimum_charge=self.floor, stability='not_assessed')
        write(self.directory/'manifest.json', self.manifest)

    def progress(self):
        write(self.directory/'progress.json', dict(search_solves=self.budget.search_used,
              refinement_solves=self.budget.refinement_used, evaluations=self.evaluations,
              finalists=self.finalists, ergoregion_resolved=self.found, best_path=self.best_path,
              best_ratio=self.best_ratio, incumbent_ratio=self.incumbent_ratio,
              seconds=time.monotonic()-self.started))

    def should_stop(self):
        return self.found and self.config.get('mode') != 'maximise'

    def solve(self, log_target, seed, *, independent):
        from .problem import RingProblem
        from .model import ScalarField
        from .workflow import branch_checks, save_state
        from .diagnostics import validate
        from ..solver.newton import newton
        self.budget.take()
        path = self.directory/'attempts'/f'{self.budget.search_used:03d}'
        path.mkdir(parents=True)
        p = RingProblem([ScalarField(**f) for f in self.plan['metadata']['fields']],
                        nx=self.config['search_grid'][0], ny=self.config['search_grid'][1],
                        length=2.5, central_lapse=math.exp(log_target))
        near = sorted(self.pool, key=lambda item: abs(item['log']-seed['log']))
        second = next((item for item in near if abs(item['log']-seed['log']) >= 1e-4), None)
        current = p.transfer(seed['p'], seed['u'])
        older = p.transfer(second['p'], second['u']) if second else None
        guess = predictor(current, older, log_target, seed['log'], second['log'] if second else 0.)
        # The perturbation requires fresh corrections even for an unchanged target.
        arrays, omega = p.unpack(guess)
        shape = (1-p.s[:, None]**2)**2*(1-p.y[None, :]**2)**2
        for tag in ('f', 'w', 'N', 'b'):
            arrays[tag] = arrays[tag]+1e-5*shape
        guess = p.pack(arrays, omega)
        write(path/'manifest.json', dict(central_lapse=math.exp(log_target), seed=seed['path'],
              seed_sha256=hashlib.sha256(Path(seed['path']).read_bytes()).hexdigest(), independent=independent))
        write(path/'stage.json', dict(stage='newton', search_solves=self.budget.search_used))
        self.progress()
        try:
            u, info = newton(p.residual, p.jacobian, guess, tol=1e-14, max_iter=30,
                             min_updates=2, chord_ratio=0., verbose=True)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            u, info = guess, dict(converged=False, reason=str(error))
        save_state(path/'state.npz', p, u)
        try:
            row = validate(p, u, info, independent=independent)
            branch_checks(row, p, u, dict(minimum_charges=[self.floor], require_nodeless=True))
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            row = dict(verdict='REJECT', reasons=[str(error)], newton=info)
        row['independent'] = independent
        sample = None
        if row['verdict'] == 'PASS' and independent:
            try:
                sample = common_metric_samples(path/'state.npz')
            except (ValueError, FloatingPointError) as error:
                row['verdict'] = 'REJECT'
                row['reasons'].append(str(error))
        write(path/'record.json', row)
        if sample is not None:
            write(path/'metric.json', sample)
        item = dict(log=log_target, p=p, u=u, path=str(path/'state.npz'), row=row, sample=sample)
        if row['verdict'] == 'PASS':
            self.pool.append(item)  # initial guesses only; every file stays provisional
        print(json.dumps(clean(dict(event='cma_solve', attempt=self.budget.search_used,
              central_lapse=math.exp(log_target), independent=independent, verdict=row['verdict'],
              reasons=row['reasons'], sample=sample))), flush=True)
        p.jax.clear_caches()
        self.progress()
        return item

    def evaluate(self, target):
        target_log = math.log(float(target))
        splits = 0
        while True:
            seed = min(self.pool, key=lambda item: abs(item['log']-target_log))
            step = next_log_lapse(seed['log'], target_log, self.config['max_log_lapse_step'])
            while True:
                final = abs(step-target_log) < 1e-12
                item = self.solve(step, seed, independent=final)
                if item['row']['verdict'] == 'PASS':
                    break
                splits += 1
                if splits > self.config['max_splits_per_evaluation'] or abs(step-seed['log']) < 1e-5:
                    return item
                step = (step+seed['log'])/2
            if final:
                return item

    def refine(self, item):
        from .workflow import run_study
        if (len(self.finalists) >= self.config['max_finalists']
                or self.budget.refinement_limit-self.budget.refinement_used < 3
                or any(abs(row['log_lapse']-item['log']) < self.config.get('finalist_log_separation',1e-4)
                       for row in self.finalists)):
            return dict(accepted=False, reason='refinement_budget_or_duplicate')
        index = len(self.finalists)+1
        config = dict(fields=self.plan['metadata']['fields'], length=2.5, central_lapse=math.exp(item['log']),
                      grids=self.config['grids'], require_gpu=True, max_iter=30, min_updates=2,
                      newton_tol=1e-14, chord_ratio=0., perturbation=1e-5, equation_tol=1e-8,
                      tail_tol=1e-6, observable_tol=1e-6, minimum_charges=[self.floor], require_nodeless=True)
        path = self.directory/'finalists'/f'{index:02d}'
        # Reserve all three calls before entering a workflow with its own stop gates.
        for _ in range(3):
            self.budget.take(refinement=True)
        self.progress()
        try:
            result = run_study(config, path, seed_path=item['path'],
                               acceptance_check=lambda rows: extra_checks(path, rows, self.source, self.config))
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            row = dict(log_lapse=item['log'], accepted=False, directory=str(path), error=str(error))
            self.finalists.append(row)
            self.progress()
            return row
        self.budget.refinement_used -= 3-len(result['records'])
        accepted = bool(result['accepted'] and len(result['records']) == 3
            and [r.get('grid') for r in result['records']] == config['grids']
            and all(r.get('verdict') == 'PASS' for r in result['records'])
            and result['additional_acceptance'].get('passed')
            and len(result['additional_acceptance'].get('common_point_extrema', [])) == 3)
        row = dict(log_lapse=item['log'], accepted=accepted, directory=str(path),
                   checks=result['additional_acceptance'])
        self.finalists.append(row)
        if accepted:
            ratio = result['additional_acceptance']['common_point_extrema'][-1]['shift_norm_over_lapse_max']
            if ratio > self.best_ratio:
                self.best_ratio, self.best_path = ratio, str(path/'accepted.npz')
                self.best_log = item['log']
                shutil.copy2(path/'accepted.npz', self.directory/'best_validated.npz')
            if result['additional_acceptance']['ergoregion_resolved']:
                self.found = True
                if ratio > self.best_ergo_ratio:
                    self.best_ergo_ratio = ratio
                    shutil.copy2(path/'accepted.npz', self.directory/'accepted_ergoregion.npz')
        self.progress()
        return row

    def objective(self, target):
        maximising = self.config.get('mode') == 'maximise'
        if maximising and (self.budget.refinement_limit-self.budget.refinement_used < 3
                           or len(self.finalists) >= self.config['max_finalists']):
            raise BudgetExhausted('refinement')
        record = dict(central_lapse=target, stage='evaluating', passed=False, sample=None)
        self.evaluations.append(record)
        self.progress()
        try:
            item = self.evaluate(target)
            value = score(item['row'], item['sample'])
            record.update(stage='complete', score=value, path=item['path'],
                          passed=item['row']['verdict']=='PASS' and item['sample'] is not None,
                          sample=item['sample'])
            if maximising:
                record['single_grid_passed'] = record['passed']
                record['single_grid_sample'] = item['sample']
                # Only three-grid accepted values enter the feasible CMA
                # ranking. A provisional extremum never leads the search.
                record.update(passed=False, score=4., sample=None, resolution_status='REJECT')
                if item['sample'] is not None and record['single_grid_passed']:
                    if item['sample']['shift_norm_over_lapse_max'] > self.best_ratio:
                        record['stage'] = 'resolution_study'
                        self.progress()
                        refinement = self.refine(item)
                        record['refinement'] = refinement
                        if refinement['accepted']:
                            sample = refinement['checks']['common_point_extrema'][-1]
                            record.update(passed=True, sample=sample, resolution_status='PASS',
                                score=score(dict(verdict='PASS', independent=True), sample))
                        else:
                            self.pool = [v for v in self.pool if v['path'] != item['path']]
                    else:
                        record['rejection_reason'] = 'does_not_improve_validated_best'
                record['stage'] = 'complete'
                value = record['score']
            self.progress()
            if (self.config.get('mode') != 'maximise' and item['sample'] is not None
                    and item['sample']['gtt_max'] > 0):
                self.refine(item)
            return value
        except BudgetExhausted:
            record['stage'] = 'solve_budget_exhausted'
            self.progress()
            raise
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
            record.update(stage='failed', score=4., error=str(error))
            self.progress()
            return 4.

    def run(self):
        # Prove that the new border reproduces the initial physical solution.
        bootstrap = self.solve(self.pool[0]['log'], self.pool[0], independent=True)
        if bootstrap['row']['verdict'] != 'PASS':
            write(self.directory/'outcome.json', dict(stage='bootstrap_rejected', ergoregion_resolved=self.found,
                  best_path=self.best_path, best_shift_norm_over_lapse=self.best_ratio))
            return False
        original = json.loads(self.source.with_name('grid_192x24.json').read_text())
        row = bootstrap['row']
        drift = max(abs(row[k]-original[k])/max(1., abs(original[k])) for k in ('M_ADM_estimate','J_volume'))
        drift = max(drift, abs(float(bootstrap['u'][-1])-self.plan['initial_frequency']))
        write(self.directory/'bootstrap.json', dict(reproduction_drift=drift, passed=drift <= 1e-6))
        if drift > 1e-6:
            write(self.directory/'outcome.json', dict(stage='bootstrap_mismatch', ergoregion_resolved=self.found,
                  best_path=self.best_path, best_shift_norm_over_lapse=self.best_ratio))
            return False
        cfg = self.config
        stopped = bounded_cma(cfg, self.objective, self.should_stop)
        if cfg.get('mode') != 'maximise' and not self.should_stop():
            candidates = sorted((v for v in self.evaluations if v['passed']), key=lambda v:v['score'])
            for candidate in candidates:
                if len(self.finalists) >= cfg['max_finalists'] or self.should_stop():
                    break
                item = next(item for item in self.pool if item['path'] == candidate['path'])
                self.refine(item)
        self.progress()
        self.manifest['cma_version'] = stopped['cma_version']
        write(self.directory/'manifest.json', self.manifest)
        write(self.directory/'outcome.json', dict(stage='complete', stop_reason=(
              'validated_ergoregion' if self.should_stop() else stopped['reason']), cma_stop=stopped,
              ergoregion_resolved=self.found, best_path=self.best_path, evaluations=len(self.evaluations),
              best_shift_norm_over_lapse=self.best_ratio, best_central_lapse=math.exp(self.best_log),
              incumbent_ratio=self.incumbent_ratio, global_maximum_established=False,
              searched_central_lapse_bounds=cfg['central_lapse_bounds'],
              search_solves=self.budget.search_used, refinement_solves=self.budget.refinement_used,
              seconds=time.monotonic()-self.started, stability='not_assessed',
              scope='Fixed-model stationary search; best sampled branch values, no global maximum or stability claim.'))
        return self.found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--gpu', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    plan = preflight(args.source, config)
    if args.gpu < 0:
        parser.error('nonnegative GPU index required')
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    os.environ.setdefault('XLA_PYTHON_CLIENT_ALLOCATOR', 'platform')
    os.environ.setdefault('XLA_PYTHON_CLIENT_PREALLOCATE', 'false')
    from ..solver.device import select_device
    select_device(args.gpu, 128)
    return 0 if Search(args.source, config, args.out).run() else 2


if __name__ == '__main__':
    raise SystemExit(main())
