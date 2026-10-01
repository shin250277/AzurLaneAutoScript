"""Observed Korean task titles, with strict template matching and Hangul fallback."""
import numpy as np
from module.island.data import DIC_ISLAND_TASK
from module.island_handler.korean_ocr import KoreanIslandNameOcr


class KoreanSeasonTaskOcr(KoreanIslandNameOcr):
    template_folder = 'assets/kr/island_task_name'
    name_dictionary = DIC_ISLAND_TASK

    def prepare_fallback(self, frame):
        # Tight title crops make Windows OCR miss complete Hangul syllables.
        # White breathing room is specific to the light season task cards.
        padding = ((12, 12), (12, 12), (0, 0)) if frame.ndim == 3 else ((12, 12), (12, 12))
        return np.pad(frame, padding, mode='constant', constant_values=255)
