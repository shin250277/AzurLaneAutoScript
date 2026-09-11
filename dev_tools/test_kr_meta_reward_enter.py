import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.meta_reward.assets import REWARD_ENTER


class KrMetaRewardEnterTest(unittest.TestCase):
    def test_localized_sync_entry_matches_label_not_blank(self):
        self.assertIn('kr', REWARD_ENTER.raw_file)
        button = Button(area=REWARD_ENTER.raw_area['kr'],
                        color=REWARD_ENTER.raw_color['kr'],
                        button=REWARD_ENTER.raw_button['kr'],
                        file=REWARD_ENTER.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))
