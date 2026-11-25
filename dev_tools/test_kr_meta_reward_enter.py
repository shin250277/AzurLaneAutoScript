import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.meta_reward.assets import REWARD_ENTER, REWARD_CHECK, REWARD_RECEIVE


class KrMetaRewardEnterTest(unittest.TestCase):
    def test_reward_screen_and_claim_are_localized(self):
        for asset in (REWARD_CHECK, REWARD_RECEIVE):
            self.assertIn('kr', asset.raw_file)
            button = Button(area=asset.raw_area['kr'], color=asset.raw_color['kr'],
                            button=asset.raw_button['kr'], file=asset.raw_file['kr'])
            frame = np.asarray(Image.open(button.file).convert('RGB'))
            self.assertTrue(button.match(frame, offset=(20, 20)))
            self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))

    def test_localized_sync_entry_matches_label_not_blank(self):
        self.assertIn('kr', REWARD_ENTER.raw_file)
        button = Button(area=REWARD_ENTER.raw_area['kr'],
                        color=REWARD_ENTER.raw_color['kr'],
                        button=REWARD_ENTER.raw_button['kr'],
                        file=REWARD_ENTER.raw_file['kr'])
        frame = np.asarray(Image.open(button.file).convert('RGB'))
        self.assertTrue(button.match(frame, offset=(20, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(20, 20)))
