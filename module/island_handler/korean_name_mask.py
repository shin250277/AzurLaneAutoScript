"""Conservative whole-label consensus for translucent Korean recipe cards."""
import cv2
import numpy as np


def glyph_mask(gray, level):
    mask = (gray < level).astype(np.uint8) * 255
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    boxes = [s for s in stats[1:] if s[3] >= 8 and s[2] >= 2]
    if not boxes:
        return None
    left, top = min(s[0] for s in boxes), min(s[1] for s in boxes)
    right, bottom = max(s[0]+s[2] for s in boxes), max(s[1]+s[3] for s in boxes)
    return np.pad(mask[top:bottom, left:right], 2, mode='constant')


def mask_consensus(frame, references):
    """No resizing/substrings: all three levels and whole text extent must agree.

    This supplements, rather than weakens, existing grayscale matching. A
    caller must never use it to overwrite a conflicting valid OCR name.
    """
    winners = []
    for level in (110, 130, 150):
        observed = glyph_mask(frame, level)
        if observed is None:
            return None
        scores = {}
        for name, gray in references:
            mask = glyph_mask(gray, level)
            if mask is None or any(abs(a-b) > 2 for a, b in zip(mask.shape, observed.shape)):
                continue
            score = cv2.minMaxLoc(cv2.matchTemplate(
                np.pad(observed, 2, mode='constant'), mask, cv2.TM_CCOEFF_NORMED))[1]
            if np.isfinite(score):
                scores[name] = max(scores.get(name, 0), score)
        ranked = sorted(((value, name) for name, value in scores.items()), reverse=True)
        if not ranked or ranked[0][0] < .93 or (len(ranked) > 1 and ranked[0][0]-ranked[1][0] < .15):
            return None
        winners.append(ranked[0])
    if len({name for _, name in winners}) == 1 and max(s for s, _ in winners) > .98:
        return winners[0][1]
    return None
