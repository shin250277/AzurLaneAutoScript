"""A known short recipe cannot authorize a different long recipe."""
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image


class NameSubstringTest(unittest.TestCase):
    def test_short_template_is_rejected_inside_long_label(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        ocr = KoreanIslandNameOcr([])
        ocr.templates = [t for t in ocr.templates if t[0] == '두부']
        ocr.mask_references = [t for t in ocr.mask_references if t[0] == '두부']
        frame = np.array(Image.open('dev_tools/fixtures/kr_long_tofu_context.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            self.assertNotEqual(ocr.ocr([frame], direct_ocr=True), ['두부'])

    def test_full_long_label_and_followup_variants_resolve(self):
        from pathlib import Path
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        from module.island.data import DIC_ISLAND_ITEM
        ocr = KoreanIslandNameOcr([])
        paths = list(Path('assets/kr/island_item_name').glob('*_recipe_followup_selected.png'))
        paths.append(Path('assets/kr/island_item_name/3012_recipe_long_selected.png'))
        self.assertEqual(len(paths), 5)
        for path in paths:
            expected = DIC_ISLAND_ITEM[int(path.stem.split('_')[0])]['name']['kr']
            with self.subTest(path=path.name), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
                self.assertEqual(ocr.ocr([np.array(Image.open(str(path)))], direct_ocr=True), [expected])
                backend.assert_not_called()
