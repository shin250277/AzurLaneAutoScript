"""KR announcement close target must stay on the detected cross."""
import unittest

from dev_tools.button_extract import ImageExtractor
from module.handler.assets import LOGIN_ANNOUNCE_2


class KoreanAnnouncementCloseTest(unittest.TestCase):
    def test_runtime_target_is_detected_close_icon(self):
        self.assertEqual(LOGIN_ANNOUNCE_2.raw_button['kr'],
                         LOGIN_ANNOUNCE_2.raw_area['kr'])

    def test_generator_preserves_kr_close_target(self):
        asset = ImageExtractor('handler', 'LOGIN_ANNOUNCE_2.png')
        self.assertEqual(asset.button['kr'], asset.area['kr'])

    def test_other_servers_keep_existing_target(self):
        for server in ('cn', 'en', 'jp', 'tw'):
            self.assertEqual(LOGIN_ANNOUNCE_2.raw_button[server], (1171, 83, 1193, 105))


if __name__ == '__main__':
    unittest.main()
