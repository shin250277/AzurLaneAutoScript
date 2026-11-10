"""Reviewed public labels from noon live failures; reject changed sources."""
from hashlib import sha256
from pathlib import Path
from PIL import Image
from dev_tools.extract_kr_recipe_followup_nov9 import grid
from module.base.utils import crop

LABELS = [('601_9061', 0, 4009, '곶감', '62600c8c3b30d985b0bc73460aa7967788cb9cbc18e34b2cfae08358be896b58'),
          ('602_9071', 0, 3017, '사과 주스', 'c905535be7943d7b29f8fc76b26c797b402ce064fc6a313ee9f523490ff03934'),
          ('602_9071', 1, 3018, '바나나 망고 주스', 'c905535be7943d7b29f8fc76b26c797b402ce064fc6a313ee9f523490ff03934'),
          ('603_9081', 0, 3009, '애플파이', '7aa5d0a2f3f653319122528afb186d6261ac79dafa297445ac61fe044a8b2361'),
          ('706_9207', 2, 3039, '향낭', '06e17a190b18ce3acfd3eb6360dd2ea24721531d2ef56a414a92b747b4c83b86'),
          ('901_9041', 2, 3113, '프루트 트윈즈', 'f5d0eb220a4345b053a638901f63183735be4b5514008a2cb8c0c0b5e0a2fd27'),
          ('501_9101', 0, 2017, '감귤', '97e0abeb55b88d7d8bbffbfc5ae9584a8df2ff4f40e62cd0845d183384f99c91'),
          ('602_9071', 1, 3020, '딸기 레몬 드링크', '1a2f2ab8b0f92cbfd0a2400f3b4193b0ffdda269db42e7667fda9f9bb2448a14'),
          ('603_9081', 0, 3118, '파에야', '2897a7c328a446724085396c023412bd604b5691e005825994efa9941d178a7e'),
          ('901_9041', 1, 3010, '딸기 밀크쉐이크', 'f6af8f87d2d954ea463d60f1daff76b1192de4b8584b27a508377475f2124174')]

if __name__ == '__main__':
    import sys
    for key, row, item, name, digest in LABELS:
        selected = [arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('--item=')]
        if selected and str(item) not in selected:
            continue
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Changed source requires visual review')
        frame, buttons = grid(path)
        label = Image.fromarray(crop(frame, buttons.crop((123,19,269,50)).buttons[row].area))
        label.save('dev_tools/fixtures/kr_noon_restaurant_%s.png' % item)
        if '--install' in sys.argv:
            label.save('assets/kr/island_item_name/%s_noon_restaurant_selected.png' % item)
