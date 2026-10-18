import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from kv260_image.fixtures import fixture
from kv260_image.formats import pack_gray32, pack_rgbx, unpack_gray32
from kv260_image.metrics import compare
from kv260_image.reference import dimensions, grayscale


def test_known_colors_and_neutral_ramp():
    colors = np.array(
        [[[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255], [0, 0, 0]]], dtype=np.uint8
    )
    np.testing.assert_array_equal(grayscale(colors), [[77, 149, 29, 255, 0]])
    ramp = np.repeat(np.arange(256, dtype=np.uint8)[None, :, None], 3, axis=2)
    np.testing.assert_array_equal(grayscale(ramp), np.arange(256)[None, :])


@pytest.mark.parametrize(
    "image",
    [
        np.zeros((1, 1), dtype=np.uint8),
        np.zeros((1, 1, 4), dtype=np.uint8),
        np.zeros((1, 1, 3)),
        np.zeros((0, 1, 3), dtype=np.uint8),
        np.zeros((1, 1921, 3), dtype=np.uint8),
    ],
)
def test_invalid_rgb(image):
    with pytest.raises(ValueError):
        grayscale(image)


@pytest.mark.parametrize(
    "rows,cols", [(0, 1), (1, 0), (-1, 2), (1081, 1), (1, 1921), (True, 1), (1.5, 1)]
)
def test_dimension_validation(rows, cols):
    with pytest.raises(ValueError):
        dimensions(rows, cols)


def test_packing_is_little_endian_and_padding_is_zero():
    rgb = np.array([[[1, 2, 3], [255, 0, 128]]], dtype=np.uint8)
    assert pack_rgbx(rgb) == bytes([1, 2, 3, 0, 255, 0, 128, 0])
    gray = np.array([[1, 255]], dtype=np.uint8)
    assert pack_gray32(gray) == bytes([1, 0, 0, 0, 255, 0, 0, 0])
    np.testing.assert_array_equal(unpack_gray32(pack_gray32(gray), 1, 2), gray)
    with pytest.raises(ValueError):
        unpack_gray32(b"\0", 1, 1)
    with pytest.raises(ValueError):
        unpack_gray32(bytes([1, 1, 0, 0]), 1, 1)
    with pytest.raises(ValueError):
        pack_gray32(np.zeros((1, 1, 1), dtype=np.uint8))


@given(
    st.lists(
        st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
        min_size=1,
        max_size=60,
    )
)
def test_reference_matches_scalar_equation_and_word_layout(pixels):
    array = np.array([pixels], dtype=np.uint8)
    expected = [(77 * r + 150 * g + 29 * b + 128) // 256 for r, g, b in pixels]
    np.testing.assert_array_equal(grayscale(array), [expected])
    words = np.frombuffer(pack_rgbx(array), dtype="<u4")
    assert words.tolist() == [r + (g << 8) + (b << 16) for r, g, b in pixels]


def test_exact_and_maximum_difference_metrics():
    zero = np.zeros((2, 3), dtype=np.uint8)
    exact = compare(zero, zero)
    assert exact["mse"] == 0 and exact["psnr_infinite"] and exact["psnr_db"] is None
    assert exact["different_pixels"] == 0 and exact["max_absolute_error"] == 0
    worst = compare(zero, np.full_like(zero, 255))
    assert worst["mse"] == 65025 and worst["psnr_db"] == 0
    assert worst["different_pixels"] == 6 and worst["max_absolute_error"] == 255
    one = zero.copy()
    one[0, 0] = 1
    result = compare(zero, one)
    assert result["mse"] == pytest.approx(1 / 6)
    assert math.isfinite(result["psnr_db"]) and not result["psnr_infinite"]
    with pytest.raises(ValueError):
        compare(zero, np.zeros((3, 2), dtype=np.uint8))
    with pytest.raises(ValueError):
        compare(zero, zero.astype(float))


def test_fixtures_reproducible_and_invalid_pattern():
    for pattern in ["mixed", "random"]:
        np.testing.assert_array_equal(fixture(5, 7, 51, pattern), fixture(5, 7, 51, pattern))
    assert not np.array_equal(fixture(5, 7, 51, "random"), fixture(5, 7, 52, "random"))
    with pytest.raises(ValueError):
        fixture(pattern="unknown")
