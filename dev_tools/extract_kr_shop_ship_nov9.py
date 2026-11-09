"""Keep only a reviewed public shop card, never account chrome."""
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    source = Image.open('log/kr_event_shop_scan_01.png').convert('RGB')
    if source.size != (1280, 720):
        raise ValueError('Unexpected source size')
    target = Image.new('RGB', source.size, (200, 200, 200))
    area = (220, 195, 375, 401)
    target.paste(source.crop(area), area[:2])
    target.save('dev_tools/fixtures/kr_shop_ship_nov9.png')
    source = Image.open('log/kr_event_shop_scan_08.png').convert('RGB')
    # Visually reviewed public title: 대공포 부속 T3; excludes quantities/account.
    label = source.crop((391, 320, 543, 348))
    label.save('dev_tools/fixtures/kr_shop_antiair_nov9.png')
    import sys
    if '--install' in sys.argv:
        label.save('assets/shop/event_kr_names/PlateAntiairT3__nov9.png')
