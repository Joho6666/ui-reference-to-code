"""Fixture setup/assembly, called by browser_evaluation.mjs. No browser dependency in the skill itself."""
import argparse
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evidence as ev
import qa_gate as gate


def prepare(output, base):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    fixture_dir = Path(__file__).parent / 'fixtures'
    records = []
    for name in ('portfolio', 'responsive'):
        project = output / name; project.mkdir()
        for src, dest in [('before.html', 'index.html'), ('reference.html', 'reference.html'),
                          ('redesigned.html' if name == 'portfolio' else 'responsive-bug.html', 'candidate.html')]:
            shutil.copyfile(fixture_dir / src, project / dest)
        run = ev.create_run(project, base + '/' + name + '/index.html', ['index.html'])
        ev.save(run / 'preservation.json', {'schema_version': 1, 'scope': 'hero and project browsing', 'reason': 'Scoped baseline before redesign',
                'items': [{'id': 'links', 'kind': 'links', 'expected': ['#contact', '#agent', '#video'], 'reason': 'Original destinations'},
                          {'id': 'copy', 'kind': 'important_copy', 'expected': ['Ideas into useful AI experiences.', 'Prototype / task orchestration', 'Prototype / batch editing'], 'reason': 'Title and honest project stages'},
                          {'id': 'search', 'kind': 'functional_behaviors', 'expected': [1, 0, 2, 1], 'reason': 'Agent, missing, clear, video queries'}]})
        spec = run / 'spec-input.json'; ev.save(spec, {'schema_version': 1, 'intent': 'Light editorial portfolio with clear hierarchy and usable project search',
                'regions': [{'region_id': 'hero', 'rule': 'Strong heading, readable copy, responsive CTA, preserved projects and search', 'component': '#hero in index.html'}]})
        ev.add(run, spec, 'spec', 'design-spec', 'reference')
        records.append({'name': name, 'project': str(project), 'run': str(run), 'url': base + '/' + name + '/index.html'})
    ev.save(output / 'config.json', records)
    return records


def snapshot(folder):
    run = ev.load(Path(folder) / 'run.json')
    return ev.revision(run['project_path'], run['project_revision']['files'], run['project_revision']['selection'])['fingerprint']


def assemble(output):
    results = []
    for record in ev.load(Path(output) / 'config.json'):
        folder = Path(record['run']); run = ev.load(folder / 'run.json')
        captures = ev.load(folder / 'captures.json')
        require_observed = folder / 'observations.json'
        observations = ev.load(require_observed)  # Written only after actual image review by agent/human.
        registered = {a['id'] for a in ev.load(folder / 'evidence.json')['artifacts']}
        for item in captures:
            if item['id'] in registered: continue
            ev.add(folder, folder / item['file'], item['id'], 'screenshot', item['role'], item['capture'],
                   item['id'] in observations, 'agent' if item['id'] in observations else 'unobserved', item['capture']['iteration'])
        iterations = (2, 3) if record['name'] == 'responsive' else (2,)
        for iteration in iterations:
            if (folder / f'qa-{iteration}.json').exists(): continue
            prefix = 'fixed' if iteration == 3 else 'candidate'
            if not (folder / f'{prefix}-code.json').exists(): continue
            for kind in ('code', 'preserve'):
                ev.add(folder, folder / f'{prefix}-{kind}.json', f'{prefix}-{kind}', 'check-result', 'implementation', iteration=iteration)
            browser = {d: f'{prefix}-{d}' for d in ('desktop', 'mobile')}
            report = {'schema_version': 2, 'run_id': run['run_id'], 'iteration': iteration, 'mode': 'D', 'modifiers': ['F'], 'scope': 'hero and project browsing',
                      'design_spec': 'spec', 'code_checks': [prefix+'-code'], 'preservation_checks': [prefix+'-preserve'], 'browser': browser,
                      'comparisons': [{'region_id': 'hero', 'kind': 'design-spec', 'reference_artifact': 'spec', 'implementation_artifact': identifier,
                                       'reviewed': True, 'observation': observations[identifier]} for identifier in browser.values()],
                      'dimensions': {n: {'applicable': True, 'score': 6 if n == 'responsive' and record['name'] == 'responsive' and iteration == 2 else 8,
                                        'confidence': 'medium', 'reason': 'Agent review of actual fixture captures and browser checks; not automatically scored',
                                        'evidence': [{'artifact_id': prefix+'-preserve' if n == 'interaction' else browser['mobile'] if n == 'responsive' else browser['desktop'],
                                                      'region_id': 'hero', 'observation': 'Real input events for search' if n == 'interaction' else observations[browser['mobile'] if n == 'responsive' else browser['desktop']]}]} for n in gate.F_DIMENSIONS},
                      'differences': [], 'failures': []}
            if record['name'] == 'responsive':
                report['differences'] = [{'id': 'CTA-OVERFLOW', 'severity': 'Major', 'region_id': 'hero', 'expected': 'CTA within mobile viewport',
                         'observed': 'CTA right edge exceeds viewport, confirmed by DOM bounds and reviewed screenshot',
                         'reference_artifact': 'ref-mobile', 'implementation_artifact': 'candidate-mobile', 'resolved': iteration == 3,
                         'resolution': {'artifact_id': 'fixed-mobile', 'observation': observations.get('fixed-mobile', ''), 'reviewed': True} if iteration == 3 else None}]
            ev.save(folder / f'qa-{iteration}.json', report)
            result = gate.evaluate(report, folder)
            ev.save(folder / f'gate-{iteration}.json', result); results.append({'fixture': record['name'], **result})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['prepare', 'snapshot', 'assemble']); parser.add_argument('path'); parser.add_argument('--base', default='http://127.0.0.1:8766')
    args = parser.parse_args()
    if args.command == 'prepare': result = prepare(args.path, args.base)
    elif args.command == 'snapshot': result = snapshot(args.path)
    else: result = assemble(args.path)
    import json
    print(json.dumps(result, indent=2))
