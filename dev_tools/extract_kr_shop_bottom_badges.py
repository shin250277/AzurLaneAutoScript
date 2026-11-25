"""Public sold-out cards only; no header, balances or account background."""
from pathlib import Path
from hashlib import sha256
from PIL import Image


def main():
    path = Path('log/kr_event_shop_scan_08.png')
    if sha256(path.read_bytes()).hexdigest() != '9b3902cb1e2e398a8540e9907762d226e945dee5c2d84454b21ea5ac934355c5':
        raise ValueError('Changed source requires visual review')
    source = Image.open(str(path)).convert('RGB')
    safe = Image.new('RGB', (1280, 720), 'white')
    for index, (x, y) in enumerate([(266 + 169 * i, 248) for i in range(5)] + [(266, 471)]):
        source.crop((x + 18, y + 13, x + 50, y + 60)).save(
            'assets/shop/event_kr_sold_out/bottom_%s.png' % index)
        box = (x - 45, y - 44, x + 107, y + 161)
        safe.paste(source.crop(box), box[:2])
    safe.save('dev_tools/fixtures/kr_event_shop_sold_out_bottom.png')


if __name__ == '__main__':
    main()
