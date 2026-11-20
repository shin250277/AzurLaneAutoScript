import unittest
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import confirmed_multiview_name, KoreanIslandNameOcr


class MultiviewNamesTest(unittest.TestCase):
    names = {'애플파이', '레몬 새우', '민물 새우', '못', '딸기', '딸기 샬럿'}

    def test_reader_integration_without_matching_template(self):
        frame = load_image('dev_tools/fixtures/kr_lemon_shrimp_bright_title.png')
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = [
                [['noise']], [['레몬 새우'], ['레몬 새우'], ['레본새우'],
                              ['레몬 새우'], ['레몬 재우'], ['레몬 재우']]]
            reader = KoreanIslandNameOcr([])
            reader.templates = []
            self.assertEqual(reader.ocr([frame], direct_ocr=True), ['레몬 새우'])
            self.assertEqual(backend.return_value.atomic_ocr_for_single_lines.call_count, 2)

    def test_two_contrast_plus_original_pixels(self):
        self.assertEqual(confirmed_multiview_name('0H플파이1',
                         ['0H플파이', '애플파이', '애플파이'],
                         ['0H플파이', '0H플파이', '애플파이'], self.names), '애플파이')
        self.assertEqual(confirmed_multiview_name('noise',
                         ['레몬 새우', '레몬새우', '레본새우'],
                         ['레몬 새우', '레몬 재우', '레몬 재우'], self.names), '레몬 새우')

    def test_known_conflict_never_outvoted(self):
        self.assertIsNone(confirmed_multiview_name('noise', ['레몬 새우'] * 3,
                          ['레몬 새우', '레몬 새우', '민물 새우'], self.names))
        self.assertIsNone(confirmed_multiview_name('딸기', ['딸기 샬럿'] * 3,
                          ['딸기 샬럿'] * 3, self.names))

    def test_short_missing_or_single_view_rejected(self):
        for contrast, localized in [(['못'] * 3, ['못'] * 3),
                                   (['애플파이'] * 3, [''] * 3),
                                   (['애플파이', '', ''], ['애플파이'] * 3),
                                   ([], []), ([''] * 3, [''] * 3)]:
            self.assertIsNone(confirmed_multiview_name('', contrast, localized, self.names))


if __name__ == '__main__':
    unittest.main()
