"""Extract reviewed public cloth glyph only, excluding inventory/account UI."""
from hashlib import sha256
from pathlib import Path
from PIL import Image

if __name__ == '__main__':
    path = Path('log/kr_island_recipe_audit_706_9207.png')
    if sha256(path.read_bytes()).hexdigest() != '13d69acbc1d05b1a9c3d0d894d727fe77b323ac9dfb4043616a8999f9e96f2af':
        raise RuntimeError('Source changed; review required')
    Image.open(str(path)).crop((304, 120, 450, 151)).save('dev_tools/fixtures/kr_cloth_settled.png')
