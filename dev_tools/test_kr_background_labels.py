import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from module.island.data import DIC_ISLAND_ITEM
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class BackgroundLabelsTest(unittest.TestCase):
    def test_reviewed_whole_labels_have_exact_identity(self):
        paths = list(Path('dev_tools/fixtures').glob('kr_background_*.png'))
        self.assertEqual(len(paths), 10)
        ocr = KoreanIslandNameOcr([])
        for path in paths:
            with self.subTest(path=path.name), patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
                expected = DIC_ISLAND_ITEM[int(path.stem.split('_')[-1])]['name']['kr']
                self.assertEqual(ocr.ocr([np.array(Image.open(str(path)))], direct_ocr=True), [expected])
