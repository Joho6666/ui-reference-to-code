import ast
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from support import ROOT, evidence, fixture


class RepositoryTests(unittest.TestCase):
    def test_python_syntax(self):
        for folder in ('scripts', 'tests'):
            for file in (ROOT/folder).rglob('*.py'):
                with self.subTest(file=file): ast.parse(file.read_text(encoding='utf-8'))

    def test_internal_markdown_links(self):
        for file in ROOT.rglob('*.md'):
            if '.git' in file.parts: continue
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'): continue
                target = target.split('#')[0]
                with self.subTest(file=file, target=target): self.assertTrue((file.parent/target).is_file())

    @unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'Development-only JSON Schema validator absent')
    def test_schema_fixtures(self):
        import jsonschema
        contract = evidence.load(ROOT/'schemas/contracts.json')
        def check(data, name):
            schema = {**contract, '$ref': '#/$defs/'+name}
            jsonschema.Draft202012Validator(schema).validate(data)
        for file, name in [('qa-unverified.json', 'qa'), ('design-spec.json', 'design-spec'), ('preservation.json', 'preservation')]:
            check(evidence.load(ROOT/'examples'/file), name)
        with tempfile.TemporaryDirectory() as folder:
            run, report, shot = fixture(folder)
            check(report, 'qa'); check(evidence.load(run/'run.json'), 'run'); check(evidence.load(run/'evidence.json'), 'evidence')
            for artifact in evidence.load(run/'evidence.json')['artifacts']:
                check(artifact, 'artifact')
                if 'capture' in artifact: check(artifact['capture'], 'capture')
                if artifact['type'] == 'check-result': check(evidence.load(run/artifact['path']), 'check-result')


if __name__ == '__main__': unittest.main()
