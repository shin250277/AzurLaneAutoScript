"""Extract only public recipe text from reviewed Nov 9 08:41-42 frames."""
from PIL import Image

if __name__ == '__main__':
    for key, item in [('703_9201', 3049), ('604_9091', 3030)]:
        with Image.open('log/kr_island_recipe_audit_%s.png' % key) as source:
            if source.size != (1280, 720):
                raise ValueError('Unexpected frame size')
            source.convert('RGB').crop((304, 281, 450, 312)).save(
                'dev_tools/fixtures/kr_photometric_%s.png' % item)
