"""Offline diagnostics for reviewed labels; no device or settings writes."""
import cv2
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.korean_name_mask import glyph_mask, whole_label_coverage

if __name__ == '__main__':
    ocr = KoreanIslandNameOcr([])
    for item, name in [(2021, '아보카도'), (3114, '피시 앤 칩스'), (3025, '망고 찹쌀밥'),
                       (3115, '레몬 새우'), (3051, '특선 나무통')]:
        gray = cv2.cvtColor(load_image('dev_tools/fixtures/kr_late_%s.png' % item), cv2.COLOR_RGB2GRAY)
        # Exclude the newly captured exact reference to measure generalization.
        from pathlib import Path
        refs = [cv2.cvtColor(load_image(str(p)), cv2.COLOR_RGB2GRAY)
                for p in Path(ocr.template_folder).glob('%s*.png' % item) if '_late_' not in p.stem]
        print(item, [round(max([whole_label_coverage(glyph_mask(gray, level), glyph_mask(ref, level))
                               for ref in refs] or [0]), 5) for level in (130, 150, 170)])
