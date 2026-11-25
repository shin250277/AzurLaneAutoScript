"""Extract observed KR settlement controls without account or inventory data."""
from PIL import Image


def extract(source_path, target, area, fixture):
    with Image.open(source_path) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 game frame')
        frame = Image.new('RGB', source.size)
        frame.paste(source.crop(area).convert('RGB'), area)
        frame.save(target)
        frame.save(fixture)


if __name__ == '__main__':
    # KR labels settlement as 경영 시작; position distinguishes actual start.
    extract('dev_tools/fixtures/kr_restaurant_wide_start.png',
            'assets/kr/island_handler/ISLAND_RESTAURANT_RECEIVE.png',
            (594, 611, 690, 641), 'dev_tools/fixtures/kr_restaurant_wide_start.png')
    extract('dev_tools/fixtures/kr_restaurant_result.png',
            'assets/kr/island_handler/ISLAND_RESTAURANT_RESULT.png',
            (261, 378, 354, 399), 'dev_tools/fixtures/kr_restaurant_result.png')
    extract('dev_tools/fixtures/kr_restaurant_resting.png',
            'assets/kr/island_handler/ISLAND_RESTAURANT_RESTING.png',
            (602, 611, 679, 641), 'dev_tools/fixtures/kr_restaurant_resting.png')
