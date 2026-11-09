"""Extract public quantity digits only from locally observed purchase previews."""
from PIL import Image
from pathlib import Path
from hashlib import sha256

DIGESTS = {14: '4a3eb4cf3596b0b15f07fe4ce964017dddab7facb7c490ddc1e4ca236a292564',
           1: 'fe400c4cc9e35aa6badaed2382d01043c36b0a17f3f716353f6f82ab4e4c3c30'}

if __name__ == '__main__':
    for value, source in [(14, 'log/kr_material_amount14_current.png'),
                          (1, 'log/kr_island_material_purchase.png')]:
        assert sha256(Path(source).read_bytes()).hexdigest() == DIGESTS[value]
        Image.open(source).crop((756, 360, 850, 382)).save(
            'dev_tools/fixtures/kr_material_quantity_%s.png' % value)
