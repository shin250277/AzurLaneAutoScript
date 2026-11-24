"""Small KR button-label crops only; no inbox contents, input, or account data."""
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
from module.base.button import Button
from module.freebies import assets


class KoreanMailLabels(unittest.TestCase):
    def test_manage_claim_delete_do_not_match_other_mail_actions(self):
        fixture = Path(__file__).parent / 'fixtures' / 'kr_mail_labels'
        for label, xy, expected in [
                ('normal', (385, 625), {'MAIL_MANAGE'}),
                ('special', (385, 625), set()),
                ('actions', (570, 510), {'MAIL_BATCH_CLAIM', 'MAIL_BATCH_DELETE'})]:
            frame = Image.new('RGB', (1280, 720))
            with Image.open(str(fixture / (label + '.png'))) as patch:
                frame.paste(patch, xy)
            matches = set()
            for name in ('MAIL_MANAGE', 'MAIL_BATCH_CLAIM', 'MAIL_BATCH_DELETE'):
                b = getattr(assets, name)
                # Resolve KR explicitly; leave the test runner's global region untouched.
                button = Button(**{key: getattr(b, 'raw_' + key)['kr']
                                   for key in ('area', 'color', 'button', 'file')})
                if button.match(np.asarray(frame), offset=(30, 30)):
                    matches.add(name)
            self.assertEqual(matches, expected, label)
