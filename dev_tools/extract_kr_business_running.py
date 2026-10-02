"""Extract the observed KR running label and account-free list controls."""
from pathlib import Path
from PIL import Image


def main():
    target = Path('assets/kr/island/TEMPLATE_ISLAND_BUSINESS_RUNNING.png')
    fixture = Path('dev_tools/fixtures/kr_business_running_controls.png')
    with Image.open('log/kr_restaurant_running_list.png') as source:
        if source.size != (1280, 720):
            raise ValueError('Expected game frame')
        for path, area in ((target, (1044, 259, 1118, 282)),
                           (fixture, (985, 72, 1180, 690))):
            if path == target:
                frame = source.crop(area).convert('RGB')
            else:
                frame = Image.new('RGB', source.size)
                frame.paste(source.crop(area).convert('RGB'), area)
            frame.save(str(path))

    source_path = Path('dev_tools/fixtures/kr_business_resting_controls.png')
    if not source_path.exists():
        source_path = Path('log/error/1790926563008/2026-10-02_16-36-02-998139.png')
    with Image.open(str(source_path)) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected game frame')
        source.crop((1037, 533, 1096, 555)).convert('RGB').save(
            'assets/kr/island/TEMPLATE_ISLAND_BUSINESS_RESTING.png')
        frame = Image.new('RGB', source.size)
        area = (985, 160, 1180, 565)
        frame.paste(source.crop(area).convert('RGB'), area)
        frame.save('dev_tools/fixtures/kr_business_resting_controls.png')


if __name__ == '__main__':
    main()
