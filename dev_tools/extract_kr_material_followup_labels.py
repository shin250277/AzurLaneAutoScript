"""Only complete public names from reviewed local audit frames."""
from pathlib import Path
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

LABELS = [('201_9211', 0, 5103, '참치'), ('603_9081', 1, 3025, '망고 찹쌀밥'),
          ('604_9091', 0, 3034, '햄버그 덮밥'), ('604_9091', 1, 3115, '레몬 새우'),
          ('706_9207', 2, 3041, '붕대'), ('901_9041', 0, 3006, '치즈')]

if __name__ == '__main__':
    import sys
    install = '--install' in sys.argv
    for key, row, item, name in LABELS:
        frame, buttons = grid(Path('log/kr_island_recipe_audit_%s.png' % key))
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_material_followup_%s.png' % item)
        if install:
            label.save('assets/kr/island_item_name/%s_material_followup_selected.png' % item)
    frame, buttons = grid(Path('log/kr_island_recipe_audit_602_9071.png'))
    artwork = Image.fromarray(crop(frame, buttons.crop((20,20,115,115)).buttons[1].area))
    artwork.save('dev_tools/fixtures/kr_fruit_set_card.png')
    if install:
        artwork.crop((8,8,84,76)).save('assets/kr/island_recipe_icon/3103.png')
