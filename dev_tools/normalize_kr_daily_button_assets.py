"""Place existing public button crops on coordinate canvases for Button loader."""
from PIL import Image


if __name__ == '__main__':
    for filename, area in [('DAILY_SKIP.png', (825, 295, 975, 351)),
                           ('DAILY_NORMAL_RUN.png', (408, 295, 560, 351))]:
        path = 'assets/kr/daily/' + filename
        with Image.open(path) as source:
            if source.size == (1280, 720):
                continue
            if source.size != (area[2] - area[0], area[3] - area[1]):
                raise ValueError('Unexpected cropped asset size: ' + filename)
            canvas = Image.new('RGB', (1280, 720))
            canvas.paste(source.convert('RGB'), area[:2])
        canvas.save(path)
