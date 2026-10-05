import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT


def run(*args):
    return subprocess.run([sys.executable, str(ROOT / 'scripts' / 'replica_init.py'), *args], capture_output=True, text=True)


class ReplicaInitTests(unittest.TestCase):
    def test_scaffold_applies_variant_and_name(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'site'
            done = run('--out', str(out), '--name', 'Nocturne', '--variant', 'liquid-blob')
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(json.loads(done.stdout)['variant'], 'liquid-blob')
            theme = (out / 'src' / 'theme.ts').read_text(encoding='utf-8')
            self.assertIn("variant: 'liquid-blob' as SceneVariant", theme)
            self.assertIn("brand: 'Nocturne'", theme)
            for name in ('package.json', 'src/scene/HeroScene.tsx', '.ui-design/replica-card.md', '.ui-design/pattern-library.md'):
                self.assertTrue((out / name).is_file(), name)
            self.assertFalse((out / 'node_modules').exists())

    def test_refuses_non_empty_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'keep.txt').write_text('x', encoding='utf-8')
            self.assertNotEqual(run('--out', folder).returncode, 0)
            self.assertTrue((Path(folder) / 'keep.txt').is_file())

    def test_template_variants_are_registered(self):
        scene = (ROOT / 'templates/r3f-hero/src/scene/HeroScene.tsx').read_text(encoding='utf-8')
        for variant in ('glass-knot', 'liquid-blob', 'orbit-cards'):
            self.assertIn("'%s'" % variant, scene)


if __name__ == '__main__': unittest.main()
