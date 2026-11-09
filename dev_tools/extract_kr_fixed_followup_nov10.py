"""Reviewed name-only crops from the next live audit pages."""
from pathlib import Path
from hashlib import sha256
import sys
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

CASES = [
    ('601_9061', 'd492f3a7d2e619f48d8919c3dda962395a2027cf32c2f8d0bcc0d84a773b80d0', 0, 4009, '곶감'),
    ('603_9081', '113d440c7d253c5ba7d0522b7b7b8acb31bc9e8d964504b36118a3fdee6e1d77', 1, 3025, '망고 찹쌀밥'),
    ('604_9091', '66581da73cb962a5a8f4cafabda6ea6fbf3153c995f2415817b9cd4dd8e17982', 1, 3115, '레몬 새우'),
    ('703_9201', '0eaa0ceb28247bc35fe00016e4e44585c48e2231d9f4b436d5b25a0e134c6344', 0, 3049, '수첩'),
    ('704_9203', '98e635b02f37f245a0a25a3b5a12fa96fee8db4a95f05720f4799b6bf925faa6', 0, 3043, '케이블'),
    ('706_9207', '50b2da31af5fb661d933011aeab27470d0a024b6187902c13cbc067b22d18bf1', 0, 3035, '천'),
    ('901_9041', '96997773d8a769763eda53b1e9cb3354cea78ba73e50cad2f9d60038f123562e', 1, 3007, '라떼'),
    ('unknown', 'ebbe5135957e58624f5cf3417743175181b57d093f93410528b73683c5f31282', 0, 3019, '꿀 레몬 워터'),
]

if __name__ == '__main__':
    for suffix, digest, row, item_id, name in CASES:
        path = Path('log/kr_island_recipe_unknown.png' if suffix == 'unknown'
                    else 'log/kr_island_recipe_audit_%s.png' % suffix)
        assert sha256(path.read_bytes()).hexdigest() == digest, suffix
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123, 19, 269, 50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_fixed_followup_nov10_%s.png' % item_id)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_followup_nov10_selected.png' % item_id)
