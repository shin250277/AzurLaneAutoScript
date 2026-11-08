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


def whole_label_coverage(a, b):
    """Symmetric one-pixel ink coverage; no scaling or partial-word matching."""
    if a is None or b is None or any(abs(x-y) > 2 for x, y in zip(a.shape, b.shape)):
        return 0
    shape = (max(a.shape[0], b.shape[0])+4, max(a.shape[1], b.shape[1])+4)
    left = np.zeros(shape, np.uint8)
    left[2:2+a.shape[0], 2:2+a.shape[1]] = a
    expanded_left = cv2.dilate(left, np.ones((3, 3), np.uint8))
    best = 0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            right = np.zeros_like(left)
            right[2+dy:2+dy+b.shape[0], 2+dx:2+dx+b.shape[1]] = b
            expanded_right = cv2.dilate(right, np.ones((3, 3), np.uint8))
            value = min(np.count_nonzero((left > 0) & (expanded_right > 0)) / float(np.count_nonzero(left)),
                        np.count_nonzero((right > 0) & (expanded_left > 0)) / float(np.count_nonzero(right)))
            best = max(best, value)
    return best


def long_label_coverage_agrees(frame, references, candidate):
    """Supplement independent grayscale identity only for long Korean labels.

    Fractional scroll rendering changes antialiasing by a pixel. Require
    >=99.5% symmetric ink coverage at all three levels, a competing-name gap,
    and the same candidate at every level. Short, clipped-word and ambiguous
    identities must not be authorized by this check alone.
    """
    if sum('\uac00' <= c <= '\ud7a3' for c in candidate) < 6:
        return False
    for level in (130, 150, 170):
        observed = glyph_mask(frame, level)
        scores = {}
        for name, gray in references:
            value = whole_label_coverage(observed, glyph_mask(gray, level))
            scores[name] = max(scores.get(name, 0), value)
        ranked = sorted(((v, n) for n, v in scores.items()), reverse=True)
        if (not ranked or ranked[0][1] != candidate or ranked[0][0] < .995
                or (len(ranked) > 1 and ranked[0][0]-ranked[1][0] < .15)):
            return False
    return True
