"""Korean OCR protocol and safe failure tests; no game input."""
import unittest
from unittest.mock import patch
import numpy as np


class WindowsOcrTest(unittest.TestCase):
    def test_pixel_exact_requires_unique_observation_not_correlation_alone(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        check = KoreanIslandNameOcr.pixel_exact_match
        candidates = [(1.0, 'a'), (0.93, 'b')]
        self.assertTrue(check(candidates, {'a': 0.1, 'b': 8}))
        self.assertFalse(check(candidates, {'a': 2, 'b': 8}))
        self.assertFalse(check(candidates, {'a': 0.1, 'b': 0.2}))
        self.assertFalse(check([(0.99, 'a')], {'a': 0.1}))
        self.assertFalse(check([], {}))

    def test_name_fallback_adds_whitespace_without_changing_observation(self):
        from module.island_handler.korean_ocr import KoreanIslandNameOcr
        ocr = KoreanIslandNameOcr([])
        for shape in ((23, 146), (23, 146, 3)):
            frame = np.full(shape, 71, dtype=np.uint8)
            original = frame.copy()
            result = ocr.prepare_fallback(frame)
            self.assertEqual(result.shape[:2], (63, 186))
            np.testing.assert_array_equal(result[20:-20, 20:-20], original)
            self.assertTrue(np.all(result[:20] == 255))
            self.assertTrue(np.all(result[:, -20:] == 255))
            np.testing.assert_array_equal(frame, original)

    def test_invalid_responses_are_not_silently_truncated(self):
        from module.ocr.windows_ocr import WindowsKoreanOcr
        for response in (None, [], ['one', 'two'], [None], 'text'):
            with self.subTest(response=response), patch.object(WindowsKoreanOcr, 'recognize_paths', return_value=response):
                with self.assertRaises(RuntimeError):
                    WindowsKoreanOcr().atomic_ocr_for_single_lines([np.zeros((23,146), np.uint8)])

    def test_output_protocol_and_alphabet_filter(self):
        from module.ocr.windows_ocr import WindowsKoreanOcr
        with patch.object(WindowsKoreanOcr, 'recognize_paths', return_value=['1 / 9']):
            result = WindowsKoreanOcr().atomic_ocr_for_single_lines([np.zeros((23,146), np.uint8)], alphabet='019/')
        self.assertEqual(result, [['1', '/', '9']])

    def test_empty_batch_does_not_start_process(self):
        from module.ocr.windows_ocr import WindowsKoreanOcr
        with patch.object(WindowsKoreanOcr, 'recognize_paths') as run:
            self.assertEqual(WindowsKoreanOcr().atomic_ocr_for_single_lines([]), [])
        run.assert_not_called()

    def test_failed_backend_is_not_empty_success(self):
        from module.ocr.windows_ocr import WindowsKoreanOcr
        with patch.object(WindowsKoreanOcr, 'recognize_paths') as run:
            run.side_effect = RuntimeError('Korean OCR unavailable')
            with self.assertRaises(RuntimeError):
                WindowsKoreanOcr().atomic_ocr_for_single_lines([np.full((23, 146), 255, np.uint8)])
