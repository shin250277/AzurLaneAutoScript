import unittest
from pathlib import Path
from unittest.mock import patch
from module.base.utils import load_image
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class LowerRecipeNamesTest(unittest.TestCase):
    def test_scroll_references_are_exact_only(self):
        paths = list(Path('assets/kr/island_item_name').glob('*nov9*.png'))
        # Keep the original reviewed references mandatory, while allowing
        # additional observed renderings of the same labels.
        expected = {'%s_lower_nov9_selected.png' % item for item in
                    (3007, 3019, 3025, 3037, 3044, 3052, 3109, 3120, 5103)}
        expected.add('3114_followup_nov9_selected.png')
        self.assertTrue(expected.issubset({path.name for path in paths}))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.stem.endswith('_selected'))

    def test_tuna_scroll_label(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            frame = load_image('dev_tools/fixtures/kr_tuna_nov9.png')
            self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['참치'])

    def test_reviewed_lower_page_labels(self):
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            ocr = KoreanIslandNameOcr([])
            for item, name in [(3019, '꿀 레몬 워터'), (3025, '망고 찹쌀밥'),
                               (3109, '미트 카니발'), (3052, '서류 캐비닛'),
                               (3044, '못'), (3007, '라떼'), (3037, '밧줄')]:
                with self.subTest(item=item):
                    frame = load_image('dev_tools/fixtures/kr_recipe_name_nov9_%s.png' % item)
                    self.assertEqual(ocr.ocr([frame], direct_ocr=True), [name])
