import unittest
from unittest.mock import patch
from PIL import Image
import numpy as np
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class PhotometricLabelsTest(unittest.TestCase):
    def test_small_lighting_change_never_changes_product_identity(self):
        from pathlib import Path
        from module.island.data import DIC_ISLAND_ITEM
        ocr = KoreanIslandNameOcr([])
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            for path in Path(ocr.template_folder).glob('*.png'):
                expected = DIC_ISLAND_ITEM[int(path.stem.split('_')[0])]['name']['kr']
                frame = np.array(Image.open(str(path)).convert('RGB'))
                changed = np.clip(frame.astype(float)*1.04-2, 0, 255).astype(np.uint8)
                with self.subTest(reference=path.name):
                    self.assertIn(ocr.ocr([changed], direct_ocr=True)[0], ('', expected))

    def test_observed_brightness_without_new_reference(self):
        for item, name in [(3049, '수첩'), (3030, '닭고기 감자 플래터')]:
            with self.subTest(item=item):
                frame = np.array(Image.open('dev_tools/fixtures/kr_photometric_%s.png' % item))
                with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
                    backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
                    self.assertEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), [name])

    def test_known_ocr_not_overridden(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_photometric_3049.png'))
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [['두부']]
            self.assertNotEqual(KoreanIslandNameOcr([]).ocr([frame], direct_ocr=True), ['수첩'])

    def test_photometric_rejects_blank_and_changed_geometry(self):
        from module.island_handler.korean_ocr import photometric_agreement
        x = np.arange(400, dtype=float).reshape(20, 20) % 200 + 20
        self.assertTrue(photometric_agreement(x, 1.05*x-3))
        self.assertFalse(photometric_agreement(x, np.roll(x, 1, axis=1)))
        self.assertFalse(photometric_agreement(x, 1.5*x))
        self.assertFalse(photometric_agreement(x, x+40))
        self.assertFalse(photometric_agreement(np.ones((20,20)), np.ones((20,20))))

    def test_competing_identity_rejects_lighting_fallback(self):
        frame = np.array(Image.open('dev_tools/fixtures/kr_photometric_3049.png'))
        ocr = KoreanIslandNameOcr([])
        ocr.templates = ocr.templates + [('두부', template, exact)
                                        for name, template, exact in ocr.templates if name == '수첩']
        ocr.mask_references = []
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.side_effect = lambda images: [[] for _ in images]
            self.assertEqual(ocr.ocr([frame], direct_ocr=True), [''])
