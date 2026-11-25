import unittest
from unittest.mock import Mock

import numpy as np

from module.freebies import mail_white as mail


class MailNoEligibleTest(unittest.TestCase):
    def test_requires_both_mail_message_and_close(self):
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[319:356, 487:794] = mail._KR_EMPTY_FILTER_TEXT.image
        self.assertFalse(mail.kr_mail_no_eligible(frame))
        frame[166:207, 887:930] = mail._KR_EMPTY_FILTER_CLOSE.image
        self.assertTrue(mail.kr_mail_no_eligible(frame))
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui.device.image = frame
        self.assertFalse(mail.MailWhite._mail_claim_execute(ui))
        ui.device.click.assert_called_once_with(mail._KR_EMPTY_FILTER_X)
        ui.handle_popup_confirm.assert_not_called()
        frame[319:356, 487:794] = 255
        self.assertFalse(mail.kr_mail_no_eligible(frame))
