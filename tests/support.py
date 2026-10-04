import json
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import evidence
import qa_gate


def png(path, width=80, height=60, color=220):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\0' + bytes([color, color, color]) * width for _ in range(height))
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
    data += chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
    Path(path).write_bytes(data)


def fixture(project):
    project = Path(project)
    (project / 'index.html').write_text('<h1>Demo</h1><a href="#contact">Contact</a>')
    folder = evidence.create_run(project, 'http://localhost:9000/')
    run = evidence.load(folder / 'run.json')
    evidence.save(folder / 'preservation.json', {'schema_version': 1, 'scope': 'hero', 'reason': 'Preserve CTA',
                                              'items': [{'id': 'cta', 'kind': 'links', 'expected': '#contact', 'reason': 'Primary action'}]})
    def doc(identifier, data, kind='check-result', role='implementation'):
        path = project / (identifier + '.json')
        # Stage outside project so default all-files revision stays stable.
        path = folder / (identifier + '.json')
        if kind == 'check-result':
            data.update(schema_version=1, run_id=run['run_id'], iteration=1, captured_at=evidence.now(), source_revision=run['project_revision']['fingerprint'])
        evidence.save(path, data)
        return evidence.add(folder, path, identifier, kind, role)
    doc('spec', {'schema_version': 1, 'intent': 'Readable light hero', 'regions': [{'region_id': 'hero', 'rule': 'Clear CTA', 'component': 'hero'}]}, 'design-spec', 'reference')
    def shot(identifier, width, color=220, role='implementation', iteration=1):
        path = folder / (identifier + '.png'); png(path, width, 60, color)
        receipt = {'run_id': run['run_id'], 'iteration': iteration, 'url': run['preview_url'], 'route': '/', 'viewport': [width, 60], 'dpr': 1,
                   'theme': 'light', 'state': 'default', 'scroll': [0, 0], 'captured_at': evidence.now(), 'source_revision': run['project_revision']['fingerprint'],
                   'regions': {'hero': [0, 0, width, 60]}}
        return evidence.add(folder, path, identifier, 'screenshot', role, receipt, True, 'agent', iteration)
    shot('desktop', 80); shot('mobile', 40)
    doc('code', {'status': 'passed', 'command': 'actual test fixture command (synthetic unit evidence)', 'exit_code': 0})
    doc('preserve', {'status': 'passed', 'checks': [{'id': 'cta', 'expected': '#contact', 'observed': '#contact', 'passed': True, 'method': 'browser-interaction'}]})
    report = {'schema_version': 2, 'run_id': run['run_id'], 'iteration': 1, 'mode': 'D', 'modifiers': [], 'scope': 'hero', 'design_spec': 'spec',
              'code_checks': ['code'], 'preservation_checks': ['preserve'], 'browser': {'desktop': 'desktop', 'mobile': 'mobile'},
              'comparisons': [{'region_id': 'hero', 'kind': 'design-spec', 'reference_artifact': 'spec', 'implementation_artifact': i,
                               'reviewed': True, 'observation': 'Synthetic unit fixture observation'} for i in ('desktop', 'mobile')],
              'dimensions': {n: {'applicable': True, 'score': 8, 'confidence': 'medium', 'reason': 'Synthetic unit fixture, not actual UI quality',
                                'evidence': [{'artifact_id': 'preserve' if n == 'interaction' else 'mobile' if n == 'responsive' else 'desktop',
                                              'region_id': 'hero', 'observation': 'Synthetic unit fixture'}]} for n in qa_gate.DIMENSIONS},
              'differences': [], 'failures': []}
    return folder, report, shot
