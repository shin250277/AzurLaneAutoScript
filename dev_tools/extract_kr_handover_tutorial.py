"""Read-only device capture; extract the observed tutorial text, no input."""
import io
import subprocess
import sys
from PIL import Image


if __name__ == '__main__':
    data = subprocess.check_output([
        'toolkit/Lib/site-packages/adbutils/binaries/adb.exe',
        '-s', sys.argv[1], 'exec-out', 'screencap', '-p'])
    source = Image.open(io.BytesIO(data)).convert('RGB')
    assert source.size == (1280, 720)
    suffix = sys.argv[2] if len(sys.argv) > 2 else ''
    assert suffix in ('', '_2', '_3', '_4')
    source.save('log/kr_handover_tutorial_20260912' + suffix + '.png')
    area = (490, 317, 791, 400)
    canvas = Image.new('RGB', source.size)
    canvas.paste(source.crop(area), area)
    canvas.save('assets/kr/handler/KR_HANDOVER_TUTORIAL' + suffix + '.png')
