"""Extract only observed button text from the recorded failed UI frame."""
from PIL import Image

if __name__ == '__main__':
    source = Image.open('log/error/1789174716931/2026-09-12_09-58-36-918692.png').convert('RGB')
    area = (980, 495, 1096, 526)
    result = Image.new('RGB', (1280, 720))
    result.paste(source.crop(area), area)
    result.save('assets/kr/map/KR_MAP_PREPARATION.png')
    for name, area in [
            ('AUTO_SEARCH_TITLE', (849, 585, 918, 608)),
            ('AUTO_SEARCH_CHECK', (927, 589, 942, 605)),
            ('CLEAR_MODE_TITLE', (965, 585, 1034, 608)),
            ('CLEAR_MODE_CHECK', (1044, 586, 1078, 606))]:
        result = Image.new('RGB', (1280, 720))
        result.paste(source.crop(area), area)
        result.save('assets/kr/handler/' + name + '.png')
