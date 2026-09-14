"""Optional offline Korean OCR using the installed Windows language pack."""
import asyncio
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image


class WindowsKoreanOcr:
    @staticmethod
    def recognize_paths(paths):
        # Python/WinRT calls the installed OS model directly. No PowerShell,
        # execution-policy changes, external service, or desktop capture.
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
        from winrt.windows.storage import StorageFile
        from winrt.windows.graphics.imaging import BitmapDecoder

        async def recognize():
            engine = OcrEngine.try_create_from_language(Language('ko'))
            if engine is None:
                raise RuntimeError('Windows Korean OCR language is not installed')
            results = []
            for path in paths:
                file = await StorageFile.get_file_from_path_async(path)
                stream = await file.open_read_async()
                try:
                    decoder = await BitmapDecoder.create_async(stream)
                    bitmap = await decoder.get_software_bitmap_async()
                    try:
                        result = await engine.recognize_async(bitmap)
                        results.append(result.text)
                    finally:
                        bitmap.close()
                finally:
                    stream.close()
            return results
        return asyncio.run(asyncio.wait_for(recognize(), timeout=45))

    def atomic_ocr_for_single_lines(self, images, alphabet=None):
        if not images:
            return []
        with tempfile.TemporaryDirectory(prefix='alas_kr_ocr_') as folder:
            paths = []
            for index, array in enumerate(images):
                image = Image.fromarray(np.asarray(array, dtype=np.uint8)).convert('RGB')
                image = image.resize((image.width * 3, image.height * 3), Image.BICUBIC)
                path = Path(folder) / ('line_%d.png' % index)
                image.save(str(path))
                paths.append(str(path.resolve()))
            values = self.recognize_paths(paths)
        if not isinstance(values, list) or len(values) != len(images) or not all(isinstance(v, str) for v in values):
            raise RuntimeError('Invalid Windows Korean OCR response')
        if alphabet:
            values = [''.join(c for c in value if c in alphabet) for value in values]
        return [list(value) for value in values]
