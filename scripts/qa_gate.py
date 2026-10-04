#!/usr/bin/env python3
"""Verify QA v2 against local run artifacts. Semantic observation remains agent/human judgment."""
import argparse
import json
import math
from pathlib import Path
import sys

from evidence import EvidenceError, inside, load, require, text, timestamp, validate, version

ReportError = EvidenceError
DIMENSIONS = ('layout', 'typography', 'color', 'component', 'responsive', 'interaction')
E_DIMENSIONS = ('geometry', 'typography', 'visual', 'composition', 'responsive', 'interaction')
F_DIMENSIONS = ('consistency', 'hierarchy', 'usability', 'responsive', 'interaction', 'content')
EXIT_CODES = {'verified': 0, 'needs-repair': 1, 'unverified': 2, 'invalid-report': 3}
FAILURES = {'REFERENCE_UNAVAILABLE', 'BROWSER_UNAVAILABLE', 'FONT_UNAVAILABLE', 'ASSET_UNAVAILABLE',
            'VIEWPORT_MISMATCH', 'STALE_EVIDENCE', 'CONTENT_REGRESSION', 'FUNCTION_REGRESSION',
            'VISUAL_MAJOR', 'VISUAL_CRITICAL', 'EVIDENCE_INVALID', 'EVIDENCE_INSUFFICIENT', 'CODE_CHECK_FAILED'}
REPAIR = {'CONTENT_REGRESSION', 'FUNCTION_REGRESSION', 'VISUAL_MAJOR', 'VISUAL_CRITICAL', 'CODE_CHECK_FAILED'}


def matched(reference, implementation, region):
    """E comparisons never auto-resize. Same route or explicitly mapped region, plus same capture conditions."""
    a, b = reference['capture'], implementation['capture']
    keys = ('viewport', 'dpr', 'theme', 'state', 'scroll')
    return all(a[k] == b[k] for k in keys) and region in a['regions'] and region in b['regions']


def evaluate(report, folder):
    version(report, 2, 'qa')
    run, artifacts, failures = validate(folder)
    require(report['run_id'] == run['run_id'], 'QA belongs to another run')
    require(type(report['iteration']) is int and report['iteration'] > 0, 'invalid QA iteration')
    require(report['mode'] in ('B', 'C', 'D') and text(report['scope']), 'invalid mode/scope')
    modifiers = report['modifiers']
    require(isinstance(modifiers, list) and len(modifiers) <= 1 and all(m in ('E', 'F') for m in modifiers),
            'modifiers must be []/[E]/[F]; use separate QA scopes for E and F')
    def fail(code, detail):
        failures.append({'code': code, 'detail': detail})
    def artifact(identifier, kind=None, role=None, current=True, observed=False, region=None):
        require(text(identifier), 'artifact ID required')
        item = artifacts.get(identifier)
        if item is None:
            fail('EVIDENCE_INVALID', 'artifact ID not registered: ' + identifier); return None
        require(not kind or item['type'] == kind, identifier + ': wrong artifact type')
        require(not role or item['role'] == role, identifier + ': wrong artifact role')
        if item['iteration'] > report['iteration']:
            fail('EVIDENCE_INVALID', identifier + ': artifact from future iteration')
        if current and item['role'] == 'implementation' and item['source_revision'] != run['project_revision']['fingerprint']:
            fail('STALE_EVIDENCE', identifier + ': screenshot/check belongs to older code')
        if observed and not item['observed']:
            fail('EVIDENCE_INSUFFICIENT', identifier + ': image has not been declared observed')
        if region is not None and item['type'] in ('screenshot', 'diff') and region not in item['capture']['regions']:
            fail('EVIDENCE_INVALID', identifier + ': missing region ' + region)
        return item
    def document(item):
        if not item:
            return {}
        try:
            return load(inside(folder, item['path']))
        except (OSError, ValueError):
            return {}
    spec = document(artifact(report['design_spec'], 'design-spec', 'reference', current=False))
    if spec:
        version(spec, 1, 'design-spec')
    spec_regions = spec.get('regions', [])
    regions = {r['region_id'] for r in spec_regions}
    require(len(regions) == len(spec_regions) and all(text(r) for r in regions), 'invalid/duplicate region ID')
    if not regions or not text(spec.get('intent')):
        fail('REFERENCE_UNAVAILABLE', 'adopted design spec missing regions/intent')
    def region_id(value):
        require(text(value), 'region_id required')
        if value not in regions:
            fail('EVIDENCE_INVALID', 'unknown design region: ' + value)
    browser = report['browser']
    screenshots = []
    for device in ('desktop', 'mobile'):
        screenshots.append(artifact(browser[device], 'screenshot', 'implementation', observed=True))
    if all(screenshots):
        require(browser['desktop'] != browser['mobile'], 'desktop and mobile need separate captures')
        if screenshots[0]['capture']['viewport'][0] <= screenshots[1]['capture']['viewport'][0]:
            fail('VIEWPORT_MISMATCH', 'desktop must be wider than mobile')
        for item in screenshots:
            if item['capture']['url'].split('#')[0] != run['preview_url'].split('#')[0]:
                fail('EVIDENCE_INVALID', item['id'] + ': capture URL differs from run preview URL; use separate run per route')
    for identifier in report['code_checks']:
        check = document(artifact(identifier, 'check-result', 'implementation'))
        if not text(check.get('command')) or type(check.get('exit_code')) is not int:
            fail('EVIDENCE_INSUFFICIENT', identifier + ': command/exit_code missing')
        elif check['exit_code'] != 0 or check.get('status') != 'passed':
            fail('CODE_CHECK_FAILED', identifier + ': code check failed')
    if not report['code_checks']:
        fail('EVIDENCE_INSUFFICIENT', 'code check artifacts required')
    baseline_path = Path(folder) / 'preservation.json'
    try:
        preservation = load(baseline_path); version(preservation, 1, 'preservation')
    except OSError:
        preservation = {}; fail('EVIDENCE_INSUFFICIENT', 'preservation.json missing')
    baseline = preservation.get('items', [])
    require(isinstance(baseline, list), 'preservation items must be a list')
    require(len({i['id'] for i in baseline}) == len(baseline), 'duplicate preservation item')
    kinds = {'routes', 'links', 'api_contracts', 'important_copy', 'data_fields', 'functional_behaviors'}
    require(all(text(i['id']) and i['kind'] in kinds and 'expected' in i for i in baseline), 'invalid preservation baseline')
    if not baseline and (report['mode'] == 'D' or not text(preservation.get('reason'))):
        fail('EVIDENCE_INSUFFICIENT', 'scoped preservation baseline is empty')
    checks = {}
    for identifier in report['preservation_checks']:
        data = document(artifact(identifier, 'check-result', 'implementation'))
        for check in data.get('checks', []):
            require(check['id'] not in checks, 'duplicate preservation check')
            require(type(check.get('passed')) is bool, 'check.passed must be boolean')
            checks[check['id']] = check
    for item in baseline:
        check = checks.get(item['id'])
        if not check or not text(check.get('method')) or check.get('expected') != item['expected']:
            fail('EVIDENCE_INSUFFICIENT', item['id'] + ': preservation proof missing/baseline mismatch')
        elif check['passed'] is not True or check.get('observed') != item['expected']:
            fail('FUNCTION_REGRESSION' if item['kind'] in ('functional_behaviors', 'api_contracts', 'routes')
                 else 'CONTENT_REGRESSION', item['id'] + ': scoped value/behavior changed')
    comparisons = report['comparisons']
    require(isinstance(comparisons, list), 'comparisons must be a list')
    compared = set()
    for comparison in comparisons:
        region = comparison['region_id']; region_id(region)
        require(type(comparison['reviewed']) is bool and text(comparison['observation']), 'comparison needs review declaration/observation')
        require(comparison['kind'] in ('reference', 'design-spec'), 'invalid comparison kind')
        source = artifact(comparison['reference_artifact'], 'screenshot' if comparison['kind'] == 'reference' else 'design-spec', 'reference', current=False,
                          observed=comparison['kind'] == 'reference', region=region)
        impl = artifact(comparison['implementation_artifact'], 'screenshot', 'implementation', observed=True, region=region)
        if not comparison['reviewed']:
            fail('EVIDENCE_INSUFFICIENT', region + ': comparison not reviewed')
        compared.add((comparison['implementation_artifact'], region))
        if 'E' in modifiers and (comparison['kind'] != 'reference' or not source or not impl or not matched(source, impl, region)):
            fail('VIEWPORT_MISMATCH', region + ': E needs matched reference viewport/DPR/theme/state/scroll and mapped region')
        if 'F' in modifiers and comparison['kind'] != 'design-spec':
            fail('EVIDENCE_INSUFFICIENT', 'F compares adopted design intent, not pixel similarity')
    if not comparisons or not all(any(i == browser[d] for i, _ in compared) for d in ('desktop', 'mobile')):
        fail('EVIDENCE_INSUFFICIENT', 'desktop and mobile both need region comparison; E mobile without source requires a separate adapted scope')
    dimensions = report['dimensions']
    names = E_DIMENSIONS if 'E' in modifiers else F_DIMENSIONS if 'F' in modifiers else DIMENSIONS
    require(set(dimensions) == set(names), 'dimensions do not match selected evaluation mode')
    required = {'responsive', names[0]}
    for name, score in dimensions.items():
        require(type(score['applicable']) is bool and text(score['reason']), name + ': applicability/reason required')
        value, confidence = score['score'], score['confidence']
        require(confidence in ('high', 'medium', 'low', 'none'), 'invalid confidence')
        require(value is None or type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10, 'invalid score')
        if not score['applicable']:
            require(name not in required and value is None, name + ': invalid exemption'); continue
        if value is None or confidence in ('low', 'none') or not score['evidence']:
            fail('EVIDENCE_INSUFFICIENT', name + ': insufficient evidence; score must be null until supported')
        elif value < 7:
            fail('VISUAL_MAJOR', name + ': below 7/10')
        for proof in score['evidence']:
            require(text(proof['observation']), 'score evidence needs observation')
            region = proof['region_id']; region_id(region)
            item = artifact(proof['artifact_id'], observed=name != 'interaction', region=region)
            if item:
                require(item['role'] == 'implementation', 'scores require implementation proof')
                require(item['type'] == ('check-result' if name == 'interaction' else 'screenshot'), 'wrong score evidence type')
                if name != 'interaction' and (item['id'], region) not in compared:
                    fail('EVIDENCE_INSUFFICIENT', name + ': score screenshot/region has not been compared')
                if name == 'responsive' and item['id'] != browser['mobile']:
                    fail('EVIDENCE_INSUFFICIENT', 'responsive score requires current mobile capture')
                if name == 'interaction':
                    check_doc = document(item)
                    browser_checks = [c for c in check_doc.get('checks', []) if c.get('method') == 'browser-interaction']
                    if not browser_checks:
                        fail('EVIDENCE_INSUFFICIENT', 'interaction needs real browser action result')
                    elif check_doc.get('status') != 'passed' or any(c.get('passed') is not True for c in browser_checks):
                        fail('FUNCTION_REGRESSION', 'browser interaction check failed')
    differences = report['differences']; seen = set()
    require(isinstance(differences, list), 'differences must be a list')
    for difference in differences:
        identifier = difference['id']
        require(text(identifier) and identifier not in seen, 'difference IDs must be unique'); seen.add(identifier)
        region = difference['region_id']; region_id(region)
        require(difference['severity'] in ('Critical', 'Major', 'Minor') and type(difference['resolved']) is bool, 'invalid difference severity/resolved')
        require(text(difference['expected']) and text(difference['observed']), 'difference expected/observed required')
        artifact(difference['reference_artifact'], role='reference', current=False, region=region)
        old = artifact(difference['implementation_artifact'], 'screenshot', 'implementation', current=not difference['resolved'], observed=True, region=region)
        if difference['resolved']:
            resolution = difference.get('resolution')
            if not isinstance(resolution, dict) or not text(resolution.get('observation')) or resolution.get('reviewed') is not True:
                fail('EVIDENCE_INSUFFICIENT', identifier + ': resolution lacks review/new evidence'); continue
            new = artifact(resolution['artifact_id'], 'screenshot', 'implementation', observed=True, region=region)
            if not old or not new or old['id'] == new['id'] or new['iteration'] <= old['iteration'] or new['sha256'] == old['sha256'] or timestamp(new['captured_at']) <= timestamp(old['captured_at']):
                fail('EVIDENCE_INSUFFICIENT', identifier + ': resolution requires a changed, later capture')
            elif not matched(old, new, region):
                fail('VIEWPORT_MISMATCH', identifier + ': resolution capture conditions changed')
        elif difference['severity'] in ('Critical', 'Major'):
            fail('VISUAL_' + difference['severity'].upper(), identifier + ': ' + difference['observed'])
    # Previously recorded serious differences cannot be silently removed in later QA rounds.
    for path in Path(folder).glob('qa*.json'):
        prior = load(path)
        if prior.get('run_id') == run['run_id'] and type(prior.get('iteration')) is int and prior['iteration'] < report['iteration']:
            for difference in prior.get('differences', []):
                if difference['severity'] in ('Critical', 'Major') and difference['id'] not in seen:
                    fail('EVIDENCE_INSUFFICIENT', difference['id'] + ': previous serious difference omitted')
    for failure in report.get('failures', []):
        require(failure['code'] in FAILURES and text(failure['detail']), 'unknown failure code/empty detail')
        fail(failure['code'], failure['detail'])
    repair = [f for f in failures if f['code'] in REPAIR]
    status = 'needs-repair' if repair else 'unverified' if failures else 'verified'
    return {'status': status, 'run_id': run['run_id'], 'iteration': report['iteration'], 'failures': failures,
            'note': 'Files, PNG structure, revision, references and conditions checked. Capture provenance, observation, scores and semantic truth remain declared.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('report', type=Path)
    parser.add_argument('--run', type=Path, help='defaults to report parent')
    args = parser.parse_args(argv)
    try:
        result = evaluate(load(args.report), args.run or args.report.parent)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'status': 'invalid-report', 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2)); return EXIT_CODES[result['status']]


if __name__ == '__main__':
    sys.exit(main())
