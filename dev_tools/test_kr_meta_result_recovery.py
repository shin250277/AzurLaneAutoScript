"""Recover only positively identified META results; never start a battle."""
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image
import module.config.server as server
from module.base.button import Button
from module.os_ash.meta import Meta, KR_META_COMPLETE_HEADER, BATTLE_STATUS
from module.ui.ui import UI


class MetaResultRecoveryTest(unittest.TestCase):
    def test_requires_both_result_header_and_confirm_and_kr(self):
        for region, header, confirm in [('kr', True, True), ('kr', False, True),
                                         ('kr', True, False), ('jp', True, True)]:
            ui = Meta.__new__(Meta)
            ui.device = Mock()
            ui.appear = Mock(return_value=header)
            ui.match_template_color = Mock(return_value=confirm)
            with patch.object(server, 'server', region), patch.object(UI, 'ui_additional', return_value=False) as fallback:
                result = ui.ui_additional(get_ship=False)
            if region == 'kr' and header and confirm:
                self.assertTrue(result)
                ui.device.click.assert_called_once_with(BATTLE_STATUS)
                fallback.assert_not_called()
            else:
                self.assertFalse(result)
                ui.device.click.assert_not_called()
                fallback.assert_called_once_with(get_ship=False)

    def test_local_failure_frame_and_erased_header_or_button(self):
        path = Path('log/error/1793926057402/2026-11-06_09-47-37-388723.png')
        if not path.is_file():
            self.skipTest('Local META failure frame absent; not a live compatibility pass')
        with Image.open(str(path)) as im:
            frame = np.array(im.convert('RGB'))
        confirm = Button(**{key: getattr(BATTLE_STATUS, 'raw_' + key)['kr']
                            for key in ('area', 'color', 'button', 'file')})
        self.assertTrue(KR_META_COMPLETE_HEADER.match(frame, offset=(5, 5)))
        self.assertTrue(confirm.match_template_color(frame, offset=(120, 20), threshold=10))
        for target in [KR_META_COMPLETE_HEADER, confirm]:
            negative = frame.copy()
            x1, y1, x2, y2 = target.area
            negative[y1:y2, x1:x2] = 0
            self.assertFalse(target.match(negative, offset=(5, 5)))
