"""Keep only public sold-out cards from a visually reviewed local frame."""
from hashlib import sha256
from pathlib import Path
from PIL import Image


def main():
    source = Path('log/kr_event_shop_scan_07.png')
    if sha256(source.read_bytes()).hexdigest() != 'e1b9cec3f847b0acf9004f182b5bf7b67b0ad5e935d4dedebf1b8a0d53916590':
        raise ValueError('Changed source requires visual review')
    frame = Image.open(str(source)).convert('RGB')
    # No account header, balance, identity, or background enters the fixture.
    target = Path('assets/shop/event_kr_sold_out')
    target.mkdir(exist_ok=True)
    for index in range(5):
        x = 284 + 169 * index
        frame.crop((x, 400, x + 32, 447)).save(str(target / ('badge_%s.png' % index)))
    safe = Image.new('RGB', (1280, 720), 'white')
    safe.paste(frame.crop((221, 343, 1049, 554)), (221, 343))
    safe.save('dev_tools/fixtures/kr_event_shop_sold_out_cards.png')


if __name__ == '__main__':
    main()
