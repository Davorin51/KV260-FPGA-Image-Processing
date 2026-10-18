import numpy as np
from numpy.typing import NDArray

from kv260_image.reference import dimensions


def fixture(
    rows: int = 64, cols: int = 128, seed: int = 51, pattern: str = "mixed"
) -> NDArray[np.uint8]:
    dimensions(rows, cols)
    if pattern == "random":
        return np.random.default_rng(seed).integers(0, 256, (rows, cols, 3), dtype=np.uint8)
    if pattern != "mixed":
        raise ValueError("Pattern must be mixed or random")
    image = np.zeros((rows, cols, 3), dtype=np.uint8)
    bars = np.array(
        [
            [255, 255, 255],
            [255, 255, 0],
            [0, 255, 255],
            [0, 255, 0],
            [255, 0, 255],
            [255, 0, 0],
            [0, 0, 255],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    )
    image[:] = bars[np.minimum(np.arange(cols) * 8 // cols, 7)]
    ramp = np.linspace(0, 255, cols, dtype=np.uint8)
    image[rows // 2 :, :, 0] = ramp
    image[rows // 2 :, :, 1] = ramp[::-1]
    image[rows // 2 :, :, 2] = np.random.default_rng(seed).integers(
        0, 256, (rows - rows // 2, cols), dtype=np.uint8
    )
    return image
