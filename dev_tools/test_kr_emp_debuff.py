"""EMP must be recognized at the Korean status-bar position."""
import unittest
import numpy as np
from PIL import Image
from module.base.button import Button
from module.os.assets import FLEET_EMP_DEBUFF


class EmpDebuffTest(unittest.TestCase):
    def test_observed_status_and_absence(self):
        button = Button(**{k: getattr(FLEET_EMP_DEBUFF, 'raw_' + k)['kr']
                           for k in ('area', 'color', 'button', 'file')})
        with Image.open('dev_tools/fixtures/kr_os_emp_status.png') as im:
            frame = np.array(im.convert('RGB'))
        self.assertTrue(button.match(frame, offset=(50, 20)))
        frame[74:124, 291:344] = 0
        self.assertFalse(button.match(frame, offset=(50, 20)))
        self.assertFalse(button.match(np.zeros_like(frame), offset=(50, 20)))

    def test_japanese_asset_is_preserved(self):
        self.assertEqual(FLEET_EMP_DEBUFF.raw_area['jp'], (137, 144, 175, 167))
        # Upstream deduplicated the identical JP and CN images; verify the
        # original JP blob, not the spelling of its relative path.
        import hashlib
        from pathlib import Path
        payload = Path(FLEET_EMP_DEBUFF.raw_file['jp']).read_bytes()
        self.assertEqual(hashlib.sha1(b'blob %d\0' % len(payload) + payload).hexdigest(),
                         'e2693be7744f777f03f8c32cd08a934ec3753a11')
