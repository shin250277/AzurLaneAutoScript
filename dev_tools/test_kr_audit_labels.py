"""Observed labels must resolve without guessed OCR or competing identities."""
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image


class AuditLabelTest(unittest.TestCase):
    def test_exact_reviewed_labels(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        from module.island.data import DIC_ISLAND_ITEM
        ocr = KoreanIslandNameOcr([])
        paths = list(Path('assets/kr/island_item_name').glob('*_recipe_audit_selected.png'))
        self.assertEqual(len(paths), 34)
        for path in paths:
            expected = DIC_ISLAND_ITEM[int(path.stem.split('_')[0])]['name']['kr']
            with self.subTest(path=path.name), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
                self.assertEqual(ocr.ocr([np.array(Image.open(str(path)))], direct_ocr=True), [expected])
                backend.assert_not_called()
