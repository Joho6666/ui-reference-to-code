#!/usr/bin/env python3
"""Optional Pillow signal, never a UI quality score. Does not resize or align images silently."""
import argparse
import json
from pathlib import Path
import sys


def compare(reference, implementation, output, threshold=16, region=None):
    from PIL import Image, ImageChops
    if type(threshold) is not int or not 0 <= threshold <= 255:
        raise ValueError('threshold must be an integer from 0 to 255')
    with Image.open(reference) as a, Image.open(implementation) as b:
        a.load(); b.load()
        if a.size != b.size:
            return {'comparable': False, 'reason': 'VIEWPORT_MISMATCH', 'reference_size': list(a.size), 'implementation_size': list(b.size)}
        if region:
            x, y, width, height = region
            if min(x, y) < 0 or min(width, height) <= 0 or x + width > a.width or y + height > a.height:
                raise ValueError('region outside image')
            box = (x, y, x + width, y + height); a = a.crop(box); b = b.crop(box)
        difference = ImageChops.difference(a.convert('RGBA'), b.convert('RGBA'))
        bands = difference.split()
        maximum = bands[0]
        for band in bands[1:]:
            maximum = ImageChops.lighter(maximum, band)
        mask = maximum.point(lambda value: 255 if value > threshold else 0)
        pixels = mask.histogram()[255]
        image = Image.new('RGB', a.size, '#ffffff'); image.paste('#ef4444', mask=mask)
        image.save(output)
        return {'comparable': True, 'dimensions': list(a.size), 'region': region,
                'difference_ratio': pixels / (a.width * a.height), 'bounding_box': mask.getbbox(),
                'threshold': threshold, 'diff_image': str(Path(output).resolve()),
                'note': 'Coordinates relative to selected region. Metadata alignment must be checked separately; no UI score inferred.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference'); parser.add_argument('implementation'); parser.add_argument('--output', default='diff.png')
    parser.add_argument('--threshold', type=int, default=16); parser.add_argument('--region', type=int, nargs=4)
    args = parser.parse_args()
    try:
        result = compare(args.reference, args.implementation, args.output, args.threshold, args.region)
    except ImportError:
        print(json.dumps({'comparable': False, 'reason': 'Pillow unavailable; continue manual comparison. Install requirements-visual.txt for this optional signal.'})); return 2
    except (OSError, ValueError) as error:
        print(json.dumps({'comparable': False, 'reason': str(error)})); return 3
    print(json.dumps(result, indent=2)); return 0 if result['comparable'] else 1


if __name__ == '__main__':
    sys.exit(main())
