"""Extract reviewed public artwork/text only from local Nov10 audit frames."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
from module.base.utils import crop
from dev_tools.extract_kr_recipe_followup_nov9 import grid

SAMPLES = [('401_9011',1,2703), ('706_9207',0,3035),
           ('401_9011',2,2704), ('501_9101',1,2017),
           ('601_9061',1,3120), ('602_9071',0,3019),
           ('603_9081',1,3028), ('604_9091',0,3034),
           ('604_9092',0,3034), ('706_9207',2,3037),
           ('901_9041',1,3010)]

REVIEWED = {
    '401_9011': 'ee909fef524bf4ed944516ced3dcdc918a1aebb4b8e22c9815a8289c4c558748',
    '501_9101': 'cabec4f90d4fee7fac58eecef4d6ef36e71e95ad1c9f7fdfe2cf1d3b054899e6',
    '601_9061': '8a2ba56b05a959a5dde161ddb5a8a3f679b420d814d4537a5e0328a7c26bf030',
    '602_9071': '8c41b088b88bdd0fb08830bc133e1f04774d3ff35e4ac1e8018fc59733a548fc',
    '603_9081': '5685c05d2c67aaa4acec1d1447365334083cf59ac38079d015ee99c9a5eded38',
    '604_9091': 'e5832d165353ef17d0170112e7bb7e20c880a02598b9b160ee185736fba8396a',
    '604_9092': 'c46b65f90cd41331e2eae507111777d6613baea65189f97bfbf43c43c786bcc8',
    '706_9207': '52c128417c123e341b8a0ed2d44058d3cfb17b1712e545d792794094a7eccb4d',
    '901_9041': '6e64f50e0bf46c48d35ff8b78d7f0d9fbbda9eee7cdb18dcd65339b630547b73',
}

if __name__ == '__main__':
    for key, row, item in SAMPLES:
        path = Path('log/kr_island_recipe_audit_%s.png' % key)
        if sha256(path.read_bytes()).hexdigest() != REVIEWED[key]:
            raise RuntimeError('Source changed; visual review required')
        frame, buttons = grid(path)
        label = crop(frame, buttons.crop((123,19,269,50)).buttons[row].area)
        icon = crop(frame, buttons.crop((20,20,115,115)).buttons[row].area)
        Image.fromarray(label).save('assets/kr/island_item_name/%s_nov10_pair_%s_selected.png' % (item,key))
        Image.fromarray(icon).save('dev_tools/fixtures/kr_nov10_pair_%s_%s_icon.png' % (key,item))
        Image.fromarray(label).save('dev_tools/fixtures/kr_nov10_pair_%s_%s_name.png' % (key,item))
        target = Path('assets/kr/island_recipe_icon/%s.png' % item)
        if not target.exists():
            Image.fromarray(icon).crop((8,8,84,76)).save(str(target))
