"""Extract only public requirement icons from the observed ambiguous order."""
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    asset = Path('assets/kr/island/KR_ORDER_CORN.png')
    fixture = Path('dev_tools/fixtures/kr_order_corn.png')
    if asset.exists() or fixture.exists():
        raise SystemExit('Refusing to replace established assets')
    with Image.open('log/kr_order_corn_ambiguous.png') as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720')
        output = Image.new('RGB', frame.size)
        for row in range(3):
            area = (900, 253 + row * 79, 951, 304 + row * 79)
            output.paste(frame.crop(area).convert('RGB'), area)
        output.save(str(fixture))
        frame.crop((900, 411, 951, 462)).convert('RGB').save(str(asset))
