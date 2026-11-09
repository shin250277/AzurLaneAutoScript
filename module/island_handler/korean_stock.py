"""Remove a visible Korean stock-label colon, never a guessed leading digit."""
import cv2
import numpy as np

from module.ocr.ocr import Digit


def mask_stock_prefix(image):
    stats = cv2.connectedComponentsWithStats((image < 128).astype(np.uint8))[2][1:]
    dots = [r for r in stats if 1 <= r[2] <= 4 and 1 <= r[3] <= 4 and 2 <= r[4] <= 10]
    boundaries = set()
    for upper in dots:
        for lower in dots:
            if (3 <= upper[1] <= 8 and 10 <= lower[1] <= 16
                    and 5 <= lower[1] - upper[1] <= 10
                    and abs((upper[0] + upper[2] / 2) - (lower[0] + lower[2] / 2)) <= 1.5):
                end = max(upper[0] + upper[2], lower[0] + lower[2])
                # Require a real digit-sized component to the right.
                if end < image.shape[1] / 2 and any(r[0] > end and r[3] >= 8 for r in stats):
                    boundaries.add(int(end))
    if len(boundaries) == 1:
        image = image.copy()
        image[:, :boundaries.pop()] = 255
    return image


class KoreanRecipeStockDigit(Digit):
    def pre_process(self, image):
        image = mask_stock_prefix(super().pre_process(image)).copy()
        # The pale rounded stock badge otherwise survives letter extraction as
        # gray context and CNOCR can hallucinate a trailing digit. Keep the dark
        # glyphs (including their inner antialiasing), not the badge background.
        # Never repair a recognized number by dropping or guessing digits.
        image[image > 160] = 255
        return image
