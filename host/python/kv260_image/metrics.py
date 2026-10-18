import math

import numpy as np
from numpy.typing import NDArray

from kv260_image.reference import validate_gray


def compare(reference: NDArray[np.uint8], candidate: NDArray[np.uint8]) -> dict:
    validate_gray(reference)
    validate_gray(candidate)
    if reference.shape != candidate.shape:
        raise ValueError("Image shapes differ")
    difference = reference.astype(np.float64) - candidate.astype(np.float64)
    mse = float(np.mean(difference * difference))
    exact = mse == 0
    return {
        "pixels": int(reference.size),
        "different_pixels": int(np.count_nonzero(difference)),
        "max_absolute_error": int(np.max(np.abs(difference))),
        "mse": mse,
        "psnr_db": None if exact else 10 * math.log10(255**2 / mse),
        "psnr_infinite": exact,
        "exact_match": exact,
    }
