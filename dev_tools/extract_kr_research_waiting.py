"""Extract the observed KR waiting label for computer-vision matching."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from module.base.utils import rgb2gray


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    args = parser.parse_args()
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected the 1280x720 KR research timeout frame')
        # 2026-09-10: center card's "진행 대기", excluding time and rewards.
        label = rgb2gray(np.array(frame.convert('RGB'))[566:592, 630:731])
    target = Path(__file__).resolve().parents[1] / 'assets/kr/research/TEMPLATE_WAITING.png'
    Image.fromarray(label).save(str(target))


if __name__ == '__main__':
    main()
