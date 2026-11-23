import unittest
from pathlib import Path

import numpy as np
from PIL import Image
from module.base.button import Button
from module.gacha.assets import BUILD_SUBMIT_ORDERS, SHOP_MEDAL_CHECK


class TestKRGachaLabelStates(unittest.TestCase):
    def test_gold_buttons_do_not_alias(self):
        detectors = [Button(**{k: Button.parse_property(getattr(b, 'raw_' + k), 'kr')
                               for k in ('area', 'color', 'button', 'file')})
                     for b in (BUILD_SUBMIT_ORDERS, SHOP_MEDAL_CHECK)]
        folder = Path(__file__).parent / 'fixtures' / 'kr_gacha_labels'
        for label, expected in [('construct', [True, False]), ('support', [False, True])]:
            image = Image.new('RGB', (1280, 720))
            with Image.open(str(folder / (label + '.png'))) as patch:
                image.paste(patch, (1024, 595))
            self.assertEqual([b.appear_on(np.asarray(image)) for b in detectors], expected, label)
