"""Extract only the verified normal Arbiter title from the KR mission frame."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('screenshot')
    args = parser.parse_args()
    target = Path('assets/kr/os_handler/OS_MONTHBOSS_NORMAL.png')
    if target.exists():
        parser.error('Refusing to overwrite an existing template')
    area = (567, 184, 711, 211)
    with Image.open(args.screenshot) as source:
        if source.size != (1280, 720):
            parser.error('Expected 1280x720 screenshot')
        label = source.convert('RGB').crop(area)
        canvas = Image.new('RGB', source.size)
        canvas.paste(label, area)
    canvas.save(str(target))
    print('area={}, color={}'.format(area, tuple(int(v) for v in np.asarray(label).mean(axis=(0, 1)))))
