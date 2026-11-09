"""Name-only references from reviewed current restaurant pages."""
from pathlib import Path
from hashlib import sha256
import sys
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

CASES = [
    ('unknown', '9645912a68c8a0a9a22dba37429cb07015ca5df79fa018cf45c64ec91911f720', 1, 2704, '황광석'),
    ('604_9091', '348823cb0e6b901c2d1c1b4861f4c7fb277e7d8d17f16e3d8861769c5d71e868', 0, 3034, '햄버그 덮밥'),
    ('604_9091', '348823cb0e6b901c2d1c1b4861f4c7fb277e7d8d17f16e3d8861769c5d71e868', 1, 3115, '레몬 새우'),
    ('706_9207', 'f7f0cf97aaae97f95be6b83480e5e2845dbfccc27b1cc86ea6393c487887dfa8', 0, 3035, '천'),
    ('901_9041', 'c206b8e559a36784c2e67d84004a758fc1012cfc8b2f25a4f03e48fa938dd70f', 1, 3007, '라떼'),
    ('601_9061', '29d89519e422f42b543e272a86699b4a7d1add3f0f21c3a96227110b179cca1b', 0, 4009, '곶감'),
    ('602_9071', 'dd12ce7c54ed808922171ce5943423b6a2be0a677536db603bf3773915d1bd5e', 0, 3021, '라벤더 차'),
    ('602_9071', 'dd12ce7c54ed808922171ce5943423b6a2be0a677536db603bf3773915d1bd5e', 1, 3022, '딸기 꿀 프라페'),
    ('602_9071', 'dd12ce7c54ed808922171ce5943423b6a2be0a677536db603bf3773915d1bd5e', 2, 3103, '향기로운 과일 세트'),
    ('603_9081', '5389f114b9661c957f0e630a1f15ed5f6ebe125cd84c309e2cc49ebbb96275ef', 0, 3106, '스위트 테이스트'),
    ('603_9081', '5389f114b9661c957f0e630a1f15ed5f6ebe125cd84c309e2cc49ebbb96275ef', 1, 3107, '과수원의 이중주'),
    ('603_9081', '5389f114b9661c957f0e630a1f15ed5f6ebe125cd84c309e2cc49ebbb96275ef', 2, 3108, '베리 오렌지 디저트'),
]

if __name__ == '__main__':
    for suffix, digest, row, item_id, name in CASES:
        path = Path('log/kr_island_recipe_unknown.png' if suffix == 'unknown'
                    else 'log/kr_island_recipe_audit_%s.png' % suffix)
        assert sha256(path.read_bytes()).hexdigest() == digest, suffix
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_sets_nov10_%s.png' % item_id)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_sets_nov10_selected.png' % item_id)
