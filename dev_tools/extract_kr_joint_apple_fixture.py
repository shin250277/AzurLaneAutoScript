"""Held-out public label/artwork only; deliberately not a runtime reference."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop
if __name__ == '__main__':
    for suffix,key,digest in [
            ('603_9081','apple','d50d8ceac12079683148b6dda65ed26303d56ff2c38a151c3c174d14843b34fc'),
            ('706_9207','rope','265e94bf177504ff629e497801d8db8516b24461aa043ea1e71444638f64f34e')]:
        path=Path('log/kr_island_recipe_audit_%s.png'%suffix)
        if sha256(path.read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Changed source requires review')
        frame,buttons=grid(path)
        for kind,area in [('name',(123,19,269,50)),('icon',(20,20,115,115))]:
            Image.fromarray(crop(frame,buttons.crop(area).buttons[0].area)).save(
                'dev_tools/fixtures/kr_nov10_joint_%s_%s.png'%(key,kind))
