"""Export only public shop titles; no account, stock or currency pixels."""
from PIL import Image

if __name__ == '__main__':
    for source, name in [('log/kr_seed_shop_0948.png', 'SEED'),
                         ('log/kr_processing_1003.png', 'PROCESSING')]:
        with Image.open(source) as image:
            if image.size != (1280, 720):
                raise ValueError('Unexpected resolution')
            area = (148, 18, 310, 54)
            output = Image.new('RGB', image.size)
            output.paste(image.convert('RGB').crop(area), area[:2])
            output.save('assets/kr/ui/ISLAND_%s_HEADER.png' % name)
