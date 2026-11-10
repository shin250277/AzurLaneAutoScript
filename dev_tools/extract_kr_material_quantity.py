"""Extract public quantity digits only from locally observed purchase previews."""
from PIL import Image
from pathlib import Path
from hashlib import sha256

DIGESTS = {'14_device': 'c0b919b9e8767ca5ac211a21e38d7186db802cd8615fc66522d3b05001dd8429',
           14: '4a3eb4cf3596b0b15f07fe4ce964017dddab7facb7c490ddc1e4ca236a292564',
           1: 'fe400c4cc9e35aa6badaed2382d01043c36b0a17f3f716353f6f82ab4e4c3c30'}

if __name__ == '__main__':
    for value, source in [('14_device', 'log/kr_material_quantity_unreadable.png'),
                          (14, 'log/kr_material_amount14_current.png'),
                          (1, 'log/kr_island_material_purchase.png')]:
        assert sha256(Path(source).read_bytes()).hexdigest() == DIGESTS[value]
        Image.open(source).crop((756, 360, 850, 382)).save(
            'dev_tools/fixtures/kr_material_quantity_%s.png' % value)
        Image.open(source).crop((660, 505, 704, 530)).save(
            'dev_tools/fixtures/kr_material_received_%s.png' % value)
