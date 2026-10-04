import importlib.util
from pathlib import Path
import tempfile
import unittest
from support import png
from visual_diff import compare


@unittest.skipUnless(importlib.util.find_spec('PIL'), 'Optional Pillow absent; core helpers still tested')
class DiffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name); self.a = self.folder/'a.png'; self.b = self.folder/'b.png'; self.out = self.folder/'diff.png'
        png(self.a); png(self.b)

    def test_identical(self):
        result = compare(self.a, self.b, self.out)
        self.assertEqual(result['difference_ratio'], 0); self.assertIsNone(result['bounding_box']); self.assertTrue(self.out.is_file())

    def test_changed_region_bbox(self):
        from PIL import Image
        image = Image.open(self.b).convert('RGB'); image.paste('black', (5, 10, 15, 20)); image.save(self.b)
        result = compare(self.a, self.b, self.out)
        self.assertEqual(result['bounding_box'], (5, 10, 15, 20)); self.assertAlmostEqual(result['difference_ratio'], 100/4800)
        cropped = compare(self.a, self.b, self.out, region=[0, 0, 20, 20])
        self.assertAlmostEqual(cropped['difference_ratio'], .25)

    def test_no_silent_resize(self):
        png(self.b, 70, 60); self.assertFalse(compare(self.a, self.b, self.out)['comparable'])
        self.assertFalse(self.out.exists())

    def test_bad_crop_and_threshold(self):
        for region in ([0, 0, 100, 100], [0, 0, 0, 20]):
            with self.assertRaises(ValueError): compare(self.a, self.b, self.out, region=region)
        with self.assertRaises(ValueError): compare(self.a, self.b, self.out, threshold=-1)


if __name__ == '__main__': unittest.main()
