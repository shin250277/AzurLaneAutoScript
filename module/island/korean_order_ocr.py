"""Read Korean item names on the light order requirement cards."""
import numpy as np
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class KoreanOrderNameOcr(KoreanIslandNameOcr):
    def prepare_fallback(self, frame):
        padding = ((12, 12), (12, 12), (0, 0)) if frame.ndim == 3 else ((12, 12), (12, 12))
        return np.pad(frame, padding, mode='constant', constant_values=255)
