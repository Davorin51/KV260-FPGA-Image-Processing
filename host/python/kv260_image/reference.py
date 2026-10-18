"""Independent array reference with explicit integer rounding and no gamma conversion."""

import numpy as np
from numpy.typing import NDArray

MAX_ROWS = 1080
MAX_COLS = 1920


def dimensions(rows: int, cols: int) -> None:
    if type(rows) is not int or type(cols) is not int:
        raise ValueError("Image dimensions must be integers")
    if not (1 <= rows <= MAX_ROWS and 1 <= cols <= MAX_COLS):
        raise ValueError("Expected 1..1080 rows and 1..1920 columns (project limits)")


def validate_rgb(image: NDArray[np.uint8]) -> None:
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected an H x W x 3 uint8 RGB array")
    dimensions(image.shape[0], image.shape[1])


def validate_gray(image: NDArray[np.uint8]) -> None:
    if image.dtype != np.uint8 or image.ndim != 2:
        raise ValueError("Expected an H x W uint8 grayscale array")
    dimensions(image.shape[0], image.shape[1])


def grayscale(image: NDArray[np.uint8]) -> NDArray[np.uint8]:
    validate_rgb(image)
    wide = image.astype(np.uint32)
    # Division rather than reusing/porting a compiled C++ helper.
    numerator = wide[..., 0] * 77 + wide[..., 1] * 150 + wide[..., 2] * 29
    return ((numerator + 128) // 256).astype(np.uint8)
