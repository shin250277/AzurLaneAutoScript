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


if __name__ == '__main__':
    main()
