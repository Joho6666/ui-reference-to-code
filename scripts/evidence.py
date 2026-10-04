#!/usr/bin/env python3
"""Small runtime-neutral run/evidence helper. PNG validation uses the standard library."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import uuid
import zlib


class EvidenceError(ValueError):
    pass


def require(test, detail):
    if not test:
        raise EvidenceError(detail)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    require(text(value), 'timestamp required')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(dt.tzinfo is not None, 'timestamp must include timezone')
    return dt


def version(data, expected, name):
    require(isinstance(data, dict), name + ': expected object')
    require(type(data.get('schema_version')) is int and data['schema_version'] == expected,
            f'{name}: unsupported schema_version {data.get("schema_version")}; expected {expected}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inside(root, relative):
    require(text(relative) and not Path(relative).is_absolute(), 'path must be relative')
    path = (Path(root) / relative).resolve()
    require(path.is_relative_to(Path(root).resolve()) if hasattr(path, 'is_relative_to')
            else Path(root).resolve() in path.parents, 'path escapes root')
    return path


def revision(project, files=None, selection='all'):
    project = Path(project).resolve()
    def git(*args):
        result = subprocess.run(['git', '-C', str(project), *args], capture_output=True)
        return result.stdout if result.returncode == 0 else None
    commit = git('rev-parse', 'HEAD')
    status = git('status', '--porcelain')
    if selection == 'all':
        tracked = git('ls-files', '-z', '--cached', '--others', '--exclude-standard')
        files = set(tracked.decode().split('\0')) if tracked is not None else {
            str(f.relative_to(project)) for f in project.rglob('*') if f.is_file()}
    require(files is not None, 'selected file list required')
    hashes = {}
    for name in sorted(files):
        if not name or any(p in ('.git', '.ui-design', '__pycache__', '.DS_Store') for p in Path(name).parts):
            continue
        path = inside(project, name)
        if path.is_file():
            hashes[name] = digest(path.read_bytes())
    require(hashes, 'revision selection has no files')
    result = {'commit': commit.decode().strip() if commit else None, 'dirty': bool(status),
              'selection': selection, 'files': hashes}
    # dirty is informational; unselected changes do not invalidate selected evidence.
    result['fingerprint'] = digest(json.dumps({k: result[k] for k in ('commit', 'files')}, sort_keys=True).encode())
    return result


def png_size(path):
    """Parse PNG chunks/CRC and decompress scanlines; reject unsupported interlacing explicitly."""
    data = Path(path).read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'core screenshot validation requires PNG')
    pos, compressed, header, ended = 8, bytearray(), None, False
    while pos < len(data):
        require(pos + 12 <= len(data), 'truncated PNG chunk')
        length, kind = struct.unpack('>I4s', data[pos:pos+8])
        require(pos + length + 12 <= len(data), 'truncated PNG payload')
        payload = data[pos+8:pos+8+length]
        crc = struct.unpack('>I', data[pos+8+length:pos+12+length])[0]
        require(zlib.crc32(kind + payload) & 0xffffffff == crc, 'invalid PNG CRC')
        if header is None:
            require(kind == b'IHDR' and length == 13, 'PNG must start with IHDR')
            header = struct.unpack('>IIBBBBB', payload)
        elif kind == b'IHDR':
            raise EvidenceError('duplicate PNG header')
        if kind == b'IDAT':
            compressed.extend(payload)
        if kind == b'IEND':
            require(length == 0, 'invalid IEND')
            ended = True
            pos += length + 12
            break
        pos += length + 12
    require(ended and pos == len(data) and compressed, 'incomplete PNG')
    width, height, depth, color, compression, filtering, interlace = header
    depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
    require(width > 0 and height > 0 and color in depths and depth in depths[color], 'invalid PNG header')
    require(compression == filtering == interlace == 0, 'unsupported PNG encoding/interlacing; export standard PNG')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    stride = (width * channels * depth + 7) // 8 + 1
    expected = stride * height
    require(expected <= 128 * 1024 * 1024, 'PNG exceeds 128 MiB decoded limit')
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, expected + 1)
    require(len(raw) == expected and decoder.eof and not decoder.unused_data,
            'invalid PNG scanline data')
    require(all(raw[row * stride] <= 4 for row in range(height)), 'invalid PNG row filter')
    if color == 3:
        require(b'PLTE' in data, 'indexed PNG missing palette')
    return [width, height]


def capture_valid(capture, size):
    required = ('run_id', 'iteration', 'url', 'route', 'viewport', 'dpr', 'theme', 'state',
                'scroll', 'captured_at', 'source_revision', 'regions')
    require(all(k in capture for k in required), 'capture contract missing fields')
    require(all(text(capture[k]) for k in ('run_id', 'url', 'route', 'state', 'source_revision')), 'capture has empty identity')
    require(type(capture['iteration']) is int and capture['iteration'] > 0, 'invalid capture iteration')
    viewport = capture['viewport']
    require(isinstance(viewport, list) and len(viewport) == 2 and
            all(type(n) is int and n > 0 for n in viewport), 'invalid viewport')
    dpr = capture['dpr']
    require(type(dpr) in (int, float) and math.isfinite(dpr) and 0 < dpr <= 8, 'invalid DPR')
    require(size == [round(n * dpr) for n in viewport], 'VIEWPORT_MISMATCH: image dimensions differ from viewport × DPR')
    require(capture['theme'] in ('light', 'dark'), 'invalid theme')
    scroll = capture['scroll']
    require(isinstance(scroll, list) and len(scroll) == 2 and all(type(n) in (int, float)
            and math.isfinite(n) and n >= 0 for n in scroll), 'invalid scroll')
    timestamp(capture['captured_at'])
    regions = capture['regions']
    require(isinstance(regions, dict) and regions, 'capture needs region_id rectangles')
    for key, box in regions.items():
        require(text(key) and isinstance(box, list) and len(box) == 4 and
                all(type(n) is int and n >= 0 for n in box), 'invalid region rectangle')
        x, y, w, h = box
        require(w > 0 and h > 0 and x + w <= size[0] and y + h <= size[1], 'region outside screenshot')


def create_run(project, preview_url, files=None):
    project = Path(project).resolve()
    identifier = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
    folder = project / '.ui-design' / 'runs' / identifier
    folder.mkdir(parents=True)
    run = {'schema_version': 1, 'run_id': identifier, 'project_path': str(project),
           'project_revision': revision(project, files, 'selected' if files else 'all'),
           'preview_url': preview_url, 'created_at': now()}
    save(folder / 'run.json', run)
    save(folder / 'evidence.json', {k: v for k, v in run.items() if k not in ('project_path', 'created_at')}
         | {'captured_at': run['created_at'], 'artifacts': []})
    return folder


def add(folder, source, identifier, kind, role, capture=None, observed=False, observer='unobserved', iteration=1):
    folder, source = Path(folder).resolve(), Path(source).resolve()
    run, manifest = load(folder / 'run.json'), load(folder / 'evidence.json')
    require(identifier.replace('-', '').replace('_', '').isalnum(), 'artifact ID must be alphanumeric/hyphen/underscore')
    require(not any(a['id'] == identifier for a in manifest['artifacts']), 'artifact ID already registered')
    require(kind in ('screenshot', 'design-spec', 'check-result', 'diff') and role in ('reference', 'implementation'), 'invalid artifact type/role')
    require(type(iteration) is int and iteration > 0, 'iteration must be positive')
    require(observer in ('agent', 'human', 'unobserved') and observed == (observer != 'unobserved'), 'observed/observer mismatch')
    current = revision(run['project_path'], run['project_revision']['files'], run['project_revision']['selection'])
    data = source.read_bytes()
    require(data, 'empty artifact')
    if kind in ('screenshot', 'diff'):
        size = png_size(source)
        require(isinstance(capture, dict), 'screenshot/diff requires capture receipt')
        capture_valid(capture, size)
        require(capture['run_id'] == run['run_id'] and capture['iteration'] == iteration, 'capture run/iteration mismatch')
    else:
        capture = capture or {'captured_at': now(), 'source_revision': current['fingerprint']}
        document = load(source)
        if kind == 'check-result':
            version(document, 1, 'check-result')
            capture = {k: document[k] for k in ('run_id', 'iteration', 'captured_at', 'source_revision')}
            require(capture['run_id'] == run['run_id'] and capture['iteration'] == iteration, 'check-result run/iteration mismatch')
    if role == 'implementation':
        require(capture['source_revision'] == current['fingerprint'], 'STALE_EVIDENCE: capture revision is not current')
    path = 'artifacts/' + identifier + source.suffix.lower()
    destination = inside(folder, path)
    require(not destination.exists(), 'immutable artifact path already exists')
    destination.parent.mkdir(exist_ok=True)
    shutil.copyfile(source, destination)
    artifact = {'id': identifier, 'run_id': run['run_id'], 'iteration': iteration, 'type': kind,
                'path': path, 'role': role, 'bytes': len(data), 'sha256': digest(data),
                'captured_at': capture['captured_at'], 'source_revision': capture['source_revision'],
                'observed': observed, 'observer': observer}
    if kind in ('screenshot', 'diff'):
        artifact['capture'] = capture
    manifest['artifacts'].append(artifact)
    manifest.update(project_revision=current, captured_at=now())
    run['project_revision'] = current
    save(folder / 'run.json', run)
    save(folder / 'evidence.json', manifest)
    return artifact


def validate(folder):
    folder = Path(folder).resolve()
    run, manifest = load(folder / 'run.json'), load(folder / 'evidence.json')
    version(run, 1, 'run'); version(manifest, 1, 'evidence')
    require(run['run_id'] == manifest['run_id'] == folder.name, 'run identity mismatch')
    require(run['project_revision'] == manifest['project_revision'], 'run/evidence revision mismatch')
    require(run['preview_url'] == manifest['preview_url'], 'preview URL mismatch')
    timestamp(run['created_at']); timestamp(manifest['captured_at'])
    artifacts, issues, paths = {}, [], set()
    require(isinstance(manifest['artifacts'], list), 'artifacts must be a list')
    for item in manifest['artifacts']:
        identifier = item.get('id')
        require(text(identifier) and identifier not in artifacts, 'duplicate/empty artifact ID')
        require(item['run_id'] == run['run_id'], 'artifact belongs to another run')
        require(type(item['iteration']) is int and item['iteration'] > 0, 'invalid artifact iteration')
        require(item['role'] in ('reference', 'implementation') and item['type'] in
                ('screenshot', 'diff', 'design-spec', 'check-result'), 'invalid artifact type/role')
        require(type(item['observed']) is bool and item['observer'] in ('agent', 'human', 'unobserved')
                and item['observed'] == (item['observer'] != 'unobserved'), 'invalid observation declaration')
        path = inside(folder, item['path'])
        require(str(path) not in paths, 'duplicate artifact path')
        paths.add(str(path)); artifacts[identifier] = item
        try:
            data = path.read_bytes()
            require(data and len(data) == item['bytes'] and digest(data) == item['sha256'], 'artifact size/hash mismatch')
            timestamp(item['captured_at'])
            require(timestamp(item['captured_at']) >= timestamp(run['created_at']), 'capture predates run')
            if item['type'] in ('screenshot', 'diff'):
                capture_valid(item['capture'], png_size(path))
                require(all(item[k] == item['capture'][k] for k in ('run_id', 'iteration', 'captured_at', 'source_revision')), 'artifact/capture identity mismatch')
            else:
                document = load(path)
                if item['type'] == 'check-result':
                    version(document, 1, 'check-result')
                    require(all(document[k] == item[k] for k in ('run_id', 'iteration', 'captured_at', 'source_revision')), 'check-result/artifact identity mismatch')
        except (OSError, ValueError, KeyError, zlib.error) as error:
            issues.append({'code': 'VIEWPORT_MISMATCH' if 'VIEWPORT_MISMATCH' in str(error) else 'EVIDENCE_INVALID', 'detail': identifier + ': ' + str(error)})
    current = revision(run['project_path'], run['project_revision']['files'], run['project_revision']['selection'])
    if current['fingerprint'] != run['project_revision']['fingerprint']:
        issues.append({'code': 'STALE_EVIDENCE', 'detail': 'project files/HEAD changed since latest capture'})
    return run, artifacts, issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create-run'); create.add_argument('--project', required=True); create.add_argument('--url', required=True); create.add_argument('--files', nargs='+')
    for name in ('add', 'validate', 'list', 'snapshot'):
        command = commands.add_parser(name); command.add_argument('--run', required=True, type=Path)
        if name == 'add':
            command.add_argument('--path', required=True, type=Path); command.add_argument('--id', required=True)
            command.add_argument('--type', required=True, choices=['screenshot', 'design-spec', 'check-result', 'diff'])
            command.add_argument('--role', required=True, choices=['reference', 'implementation']); command.add_argument('--capture', type=Path)
            command.add_argument('--observer', default='unobserved', choices=['agent', 'human', 'unobserved']); command.add_argument('--iteration', type=int, default=1)
    args = parser.parse_args()
    try:
        if args.command == 'create-run':
            result = {'run': str(create_run(args.project, args.url, args.files))}
        elif args.command == 'add':
            result = add(args.run, args.path, args.id, args.type, args.role,
                         load(args.capture) if args.capture else None, args.observer != 'unobserved', args.observer, args.iteration)
        else:
            run, artifacts, issues = validate(args.run)
            result = {'run_id': run['run_id'], 'artifacts': list(artifacts) if args.command == 'list' else len(artifacts), 'issues': issues}
            if args.command == 'snapshot':
                result['project_revision'] = revision(run['project_path'], run['project_revision']['files'], run['project_revision']['selection'])
            if issues:
                print(json.dumps(result, indent=2)); return 2
    except (OSError, ValueError, KeyError, TypeError, zlib.error) as error:
        print(json.dumps({'error': str(error)})); return 3
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    sys.exit(main())
