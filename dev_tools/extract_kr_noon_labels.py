"""Extract reviewed complete public labels, never full account frames."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

LABELS = [('401_9011', 1, 2703, '철광석'),
          ('603_9081', 1, 3025, '망고 찹쌀밥'),
          ('704_9203', 2, 3047, '식기'),
          ('706_9207', 1, 3040, '신발'),
          ('201_9211', 2, 5103, '참치')]
HASHES = ['b18add093c8ad5f2d776a2cf419895f9fd533b36a42224e4c3c631f16ed73ff3',
          '4c9bdaadc872667b9a243be6900e796ed1b195423b7917ddedc7ced748835a03',
          'ac76d6fbfde3a58870415a7e85e7b4be42d3c8f570f93d7b35756e607416f5ef',
          '266cde6834d900be47facb82fbd12fe9276242b541f979966bf7b821a885aaa3',
          'b96ac773937729155b3f9f66ce57683022e3724223b328949ce1574ee8d2f81a']

if __name__ == '__main__':
    import sys
    for (key, row, item, name), digest in zip(LABELS, HASHES):
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires visual review')
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_noon_%s.png' % item)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_noon_selected.png' % item)
