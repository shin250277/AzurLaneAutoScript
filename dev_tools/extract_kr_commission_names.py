"""Extract a manually verified KR title crop; never guess names from scan indices.

Diagnostic scan filenames are overwritten. Verify the supplied image and card
bottom before each invocation. Only title glyphs, not account frames, are saved.
"""
from pathlib import Path
import argparse

from module.base.utils import load_image, save_image
from module.commission.project import crop_kr_name_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--bottom', type=int, required=True)
    parser.add_argument('--destination', type=Path, default=Path('assets/kr/commission/names'))
    args = parser.parse_args()
    if not args.name.replace('_', '').isalnum():
        parser.error('Name must contain only letters, digits and underscores')
    image = load_image(str(args.image))
    if image.shape != (720, 1280, 3) or not 96 <= args.bottom <= 720:
        parser.error('Expected a 1280x720 frame and a visible card bottom')
    title = crop_kr_name_image(image, (364, args.bottom - 96, 608, args.bottom - 66))
    if title is None:
        parser.error('No title glyphs found')
    output = args.destination / (args.name + '.png')
    if output.exists():
        parser.error('Refusing to overwrite an existing verified template')
    args.destination.mkdir(parents=True, exist_ok=True)
    save_image(title, str(output))
    print('{}: {}x{}'.format(args.name, title.shape[1], title.shape[0]))
