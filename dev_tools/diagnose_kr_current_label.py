"""Read-only geometry/identity scores for a local failure frame."""
import sys
from pathlib import Path
import cv2
import numpy as np
from module.base.utils import crop, load_image
from module.island_handler.korean_name_mask import glyph_mask, whole_label_coverage
from module.island_handler.korean_ocr import KoreanIslandNameOcr

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    from dev_tools.extract_kr_recipe_followup_nov9 import grid
    if '--audit' in sys.argv:
        for source in sorted(Path('log').glob('kr_island_recipe_audit_*.png')):
            frame, buttons = grid(source)
            labels = [crop(frame, b.area) for b in buttons.crop((123,19,269,50)).buttons]
            print(source.name, KoreanIslandNameOcr([]).ocr(labels, direct_ocr=True), flush=True)
        sys.exit(0)
    frame, buttons = grid(Path('log/kr_island_recipe_unknown.png'))
    label = crop(frame, buttons.crop((123,19,269,50)).buttons[0].area)
    gray = cv2.cvtColor(label, cv2.COLOR_RGB2GRAY)
    if '--fixture' in sys.argv:
        from hashlib import sha256
        from PIL import Image
        source = Path('log/kr_island_recipe_unknown.png')
        if sha256(source.read_bytes()).hexdigest() != '0efcbbee6f240786bab5dc0c7cbf403c1e1d51f9f493998b57c0b55258769aa3':
            raise RuntimeError('Changed failure frame requires review')
        Image.fromarray(label).save('dev_tools/fixtures/kr_tuna_nov9_dispatch.png')
        sys.exit(0)
    ocr = KoreanIslandNameOcr([])
    print('shape', gray.shape)
    for level in (110,130,150,170):
        observed = glyph_mask(gray,level)
        scores={}
        for name,ref in ocr.mask_references:
            score=whole_label_coverage(observed,glyph_mask(ref,level))
            scores[name]=max(scores.get(name,0),score)
        print(level, None if observed is None else observed.shape,
              sorted(((v,n) for n,v in scores.items()),reverse=True)[:5])
    scores={}
    blurred=cv2.GaussianBlur(gray,(5,5),0)
    for name,ref,strict in ocr.templates:
        if ref.shape[0]>gray.shape[0] or ref.shape[1]>gray.shape[1]:
            continue
        _,score,_,point=cv2.minMaxLoc(cv2.matchTemplate(blurred,ref,cv2.TM_CCOEFF_NORMED))
        if not ocr.complete_label_span(gray,point[0],point[0]+ref.shape[1]):
            continue
        scores[name]=max(scores.get(name,0),score)
    print('gray',sorted(((v,n) for n,v in scores.items()),reverse=True)[:6])
    from module.ocr.windows_ocr import WindowsKoreanOcr
    variants = [('padded', ocr.prepare_fallback(label))]
    variants += [('glyph%d' % i, f) for i, f in enumerate(ocr.glyph_fallbacks(label))]
    variants += [('ink%d' % level, ocr.prepare_fallback(np.where(gray < level, 0, 255).astype(np.uint8)))
                 for level in (90,110,130,150,170,190)]
    reads = WindowsKoreanOcr().atomic_ocr_for_single_lines([f for _,f in variants])
    print('OCR', list(zip([n for n,_ in variants], reads)))
