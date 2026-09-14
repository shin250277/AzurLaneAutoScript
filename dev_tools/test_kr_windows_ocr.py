"""Korean OCR protocol and safe failure tests; no game input."""
import unittest
from unittest.mock import patch
import numpy as np


class WindowsOcrTest(unittest.TestCase):
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
