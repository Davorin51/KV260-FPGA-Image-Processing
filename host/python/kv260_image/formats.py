"""Explicit little-endian frame words; no assumptions about host native endian."""

import numpy as np
from numpy.typing import NDArray

from kv260_image.reference import dimensions, validate_gray, validate_rgb


def pack_rgbx(image: NDArray[np.uint8]) -> bytes:
    validate_rgb(image)
    wide = image.astype(np.uint32)
    words = wide[..., 0] | (wide[..., 1] << 8) | (wide[..., 2] << 16)
    return words.astype("<u4").tobytes(order="C")


def pack_gray32(image: NDArray[np.uint8]) -> bytes:
    validate_gray(image)
    return image.astype("<u4").tobytes(order="C")


def unpack_gray32(data: bytes, rows: int, cols: int) -> NDArray[np.uint8]:
    dimensions(rows, cols)
    if len(data) != 4 * rows * cols:
        raise ValueError("GRAY32 byte count does not match rows*cols*4")
    words = np.frombuffer(data, dtype="<u4")
    if np.any(words > 255):
        raise ValueError("GRAY32 padding must be zero; wrong endian/format or corrupt output")
    return words.astype(np.uint8).reshape(rows, cols)
