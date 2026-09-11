"""Extract only the verified tactical card heading, excluding account data."""
from pathlib import Path
from PIL import Image


if __name__ == '__main__':
    target = Path('assets/kr/tactical/KR_TACTICAL_REWARD_CARD.png')
    if target.exists():
        raise SystemExit('Refusing to overwrite existing template')
    with Image.open('log/kr_tactical_complete_candidate.png') as source:
        if source.size != (1280, 720):
            raise SystemExit('Expected 1280x720 frame')
        area = (76, 360, 186, 413)
        canvas = Image.new('RGB', source.size)
        canvas.paste(source.convert('RGB').crop(area), area)
        canvas.save(str(target))
