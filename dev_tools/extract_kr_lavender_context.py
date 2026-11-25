"""Extract only the reviewed lavender label from the 07:56 background failure."""
import argparse
from PIL import Image

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('frame')
    with Image.open(p.parse_args().frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        source.convert('RGB').crop((304, 448, 450, 479)).save(
            'dev_tools/fixtures/kr_lavender_background.png')
