"""Read-only offline OCR diagnostic; accepts a saved public name crop."""
import argparse
import cv2
import numpy as np
from PIL import Image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.ocr.windows_ocr import WindowsKoreanOcr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame')
    parser.add_argument('--area', nargs=4, type=int)
    parser.add_argument('--levels', nargs=3, type=int, default=[90,110,130])
    args = parser.parse_args()
    im = Image.open(args.frame).convert('RGB')
    if args.area:
        im = im.crop(args.area)
    frame = np.array(im)
    ocr = KoreanIslandNameOcr([])
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frames = []
    for level in args.levels:
        _, _, stats, _ = cv2.connectedComponentsWithStats((gray < level).astype(np.uint8), 8)
        boxes = [s for s in stats[1:] if s[3] >= 8 and s[2] >= 2]
        if not boxes:
            print('No glyph components', level)
            continue
        left = min(s[0] for s in boxes)
        top = min(s[1] for s in boxes)
        right = max(s[0] + s[2] for s in boxes)
        bottom = max(s[1] + s[3] for s in boxes)
        print(level, (left, top, right, bottom))
        frames.append(ocr.prepare_fallback(frame[max(top-1,0):min(bottom+1,frame.shape[0]),
                                               max(left-1,0):min(right+1,frame.shape[1])]))
    print(repr(WindowsKoreanOcr().atomic_ocr_for_single_lines(frames)).encode('unicode_escape').decode())
