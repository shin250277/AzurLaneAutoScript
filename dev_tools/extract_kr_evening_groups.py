"""Reviewed public names from six local failure frames; no account export."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from module.base.utils import crop
from module.island.data import DIC_ISLAND_ITEM

CASES = [
    ('603_9081', '1a4cea49b54a908268c1dee1373953c7dcf132980ba103aa79323467f03d52fd', ['오렌지 파이', '망고 찹쌀밥', '바나나 크레이프']),
    ('604_9091', '1ac8aa878d26ac46a39515f63459fc30b424e5becd5db0f140e4c8d80af830c6', ['햄버그 덮밥', '레몬 새우', '가재 볶음']),
    ('703_9201', 'ab5105eca5b54cfcaf27515fdf8513a8675bdf9ae906c9f630fd3c236457e273', ['책상과 의자', '특선 나무통', '서류 캐비닛']),
    ('704_9203', '8bd4810448d16a32ca16d526889b978989364e080493a8f6cebdc6d7e37b666e', ['못', '화학품', '화약']),
    ('706_9207', 'c314f74bb7c23698598dafbe311ca6136ba4085a3d20018e9e394388d8b7033e', ['밧줄', '장갑', '향낭']),
    ('901_9041', 'f7ecba30e7f30cebb953f5f9015f54312ee3e1574cb9da64d1ac8f484806218e', ['오믈렛', '아이스 커피', '치즈']),
]

if __name__ == '__main__':
    from dev_tools.extract_kr_recipe_followup_nov9 import grid
    for group, digest, names in CASES:
        path = Path('log/kr_island_recipe_audit_%s.png' % group)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires visual review')
        frame, buttons = grid(path)
        assert len(buttons.buttons) == len(names)
        for row, name in enumerate(names):
            ids = [k for k,v in DIC_ISLAND_ITEM.items() if v['name'].get('kr') == name]
            assert len(ids) == 1, name
            label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
            label.save('dev_tools/fixtures/kr_evening_group_%s.png' % ids[0])
            if name not in ('오렌지 파이', '바나나 크레이프', '화약'):
                label.save('assets/kr/island_item_name/%s_evening_group_selected.png' % ids[0])
