"""Extract observed labels only from the 2026-09-10 KR zone dropdown."""
import argparse
import ast
from pathlib import Path
import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('screenshot')
    parser.add_argument('--closed', action='store_true', help='Extract the closed-card heading instead of menu labels')
    args = parser.parse_args()
    areas = ({'ZONE_OBSCURE': (84, 225, 171, 248)} if args.closed else
             {'SELECT_OBSCURE': (87, 249, 169, 272),
              'SELECT_SAFE': (87, 315, 169, 338)})
    with Image.open(args.screenshot) as image:
        if image.size != (1280, 720):
            raise ValueError('Expected 1280x720 screenshot')
        source = image.convert('RGB')
    path = Path('module/os/assets.py')
    lines = path.read_text(encoding='utf-8').splitlines()
    for name, area in areas.items():
        target = Path('assets/kr/os') / (name + '.png')
        label = source.crop(area)
        canvas = Image.new('RGB', source.size)
        canvas.paste(label, area)
        canvas.save(str(target))
        color = tuple(int(v) for v in np.asarray(label).mean(axis=(0, 1)))
        for i, line in enumerate(lines):
            if not line.startswith(name + ' = Button('):
                continue
            call = ast.parse(line).body[0].value
            fields = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
            for key, value in [('area', area), ('button', area), ('color', color),
                               ('file', './' + target.as_posix())]:
                fields[key]['kr'] = value
            lines[i] = name + ' = Button(' + ', '.join(
                '{}={!r}'.format(k, v) for k, v in fields.items()) + ')'
            break
        else:
            raise ValueError('Missing asset: ' + name)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
