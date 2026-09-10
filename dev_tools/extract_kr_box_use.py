"""Extract only the observed KR use label, never account details."""
import argparse
import ast
from pathlib import Path
from PIL import Image
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('screenshot')
    args = parser.parse_args()
    area = (750, 494, 823, 528)
    with Image.open(args.screenshot) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 game screenshot')
        label = source.convert('RGB').crop(area)
    target = Path('assets/kr/storage/BOX_USE.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new('RGB', (1280, 720))
    canvas.paste(label, area)
    canvas.save(str(target))
    color = tuple(int(v) for v in np.asarray(label).mean(axis=(0, 1)))
    path = Path('module/storage/assets.py')
    lines = path.read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        if line.startswith('BOX_USE = Button('):
            call = ast.parse(line).body[0].value
            fields = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
            for field, value in [('area', area), ('color', color),
                                 ('button', (710, 484, 867, 536)),
                                 ('file', './assets/kr/storage/BOX_USE.png')]:
                fields[field]['kr'] = value
            lines[i] = 'BOX_USE = Button(' + ', '.join(
                '{}={!r}'.format(k, v) for k, v in fields.items()) + ')'
            break
    else:
        raise ValueError('BOX_USE definition missing')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
