"""Extract only public popup wording, never an account screenshot."""
from PIL import Image
import sys

if __name__ == '__main__':
    source = Image.open(sys.argv[1]).convert('RGB')
    output = Image.new('RGB', (1280, 720))
    area = (625, 333, 788, 357)
    output.paste(source.crop(area), area[:2])
    output.save('assets/kr/handler/KR_URGENT_PHRASE.png')
