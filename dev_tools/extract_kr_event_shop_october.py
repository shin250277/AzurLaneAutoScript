"""Keep only the observed product row; exclude account/currency/background."""
from PIL import Image
from pathlib import Path


if __name__ == '__main__':
    # The live scan overwrites numbered frames. Never silently replace an
    # established regression fixture with a different scrolling position.
    if Path('dev_tools/fixtures/kr_event_shop_october_shifted.png').exists():
        raise SystemExit('Fixture already exists; inspect new frames before extracting again')
    source = Image.open('log/kr_event_shop_scan_04.png').convert('RGB')
    fixture = Image.new('RGB', (1280, 720))
    area = (221, 194, 1049, 632)
    fixture.paste(source.crop(area), area[:2])
    fixture.save('dev_tools/fixtures/kr_event_shop_october_shifted.png')
    source = Image.open('log/kr_event_shop_scan_05.png').convert('RGB')
    fixture = Image.new('RGB', (1280, 720))
    area = (221, 203, 1049, 410)
    fixture.paste(source.crop(area), area[:2])
    fixture.save('dev_tools/fixtures/kr_event_shop_october_plates.png')
    from dev_tools.check_kr_event_shop_frame import scan_frame
    names = ['PlateGunT3', 'PlateTorpedoT3', 'PlateAntiairT3', 'PlatePlaneT3']
    for path, variant in [('log/kr_event_shop_scan_05.png', 'october'),
                          ('dev_tools/fixtures/kr_event_shop_october_plates.png', 'october_row')]:
        frame, grid = scan_frame(path)
        grid.predict(frame, save_unknown=False)
        for item, name in zip(grid.items[:4], names):
            Image.fromarray(item.image).save('assets/shop/event_kr/%s__%s.png' % (name, variant))
