"""Fail-closed recovery for one observed interrupted KR research requirement."""
import numpy as np


def can_resume_zero_requirement(code, image, reference):
    if code != 'E-315-MI' or image.shape != (720, 1280, 3):
        return False
    sample = image[529:550, 1052:1105]
    if reference.shape != sample.shape or reference.std() < 10:
        return False
    # Every pixel must agree. A similarity score can hide changed digits in
    # an otherwise identical label and must not authorize material consumption.
    return bool(np.max(np.abs(sample.astype(np.int16) - reference.astype(np.int16))) <= 10)
