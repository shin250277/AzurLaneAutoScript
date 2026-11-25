from pathlib import Path
import unittest
from unittest.mock import Mock

import numpy as np
from PIL import Image
from module.ui.ui import UI, KR_CARD_CAPTION, KR_CARD_ZOOM


class RegisteredCard(unittest.TestCase):
    def test_actual_labels_must_coexist_and_click_avoids_controls(self):
        patches = []
        for button in (KR_CARD_CAPTION, KR_CARD_ZOOM):
            with Image.open(str(Path('assets/kr/ui') / (button.name + '.png'))) as im:
                patches.append(np.array(im.convert('RGB')))
        for present in [(), (0,), (1,), (0, 1)]:
            frame = np.zeros_like(patches[0])
            for i in present:
                frame |= patches[i]
            ui = Mock()
            ui.config.SERVER = 'kr'
            ui.appear.side_effect = lambda btn, offset, similarity, **kw: btn.match(
                frame, offset=offset, similarity=similarity)
            self.assertEqual(UI._handle_kr_registered_ship(ui), len(present) == 2)
            if len(present) == 2:
                ui.device.click.assert_called_once_with(KR_CARD_CAPTION)
                self.assertLess(KR_CARD_CAPTION.button[2], 1000)
            else:
                ui.device.click.assert_not_called()
