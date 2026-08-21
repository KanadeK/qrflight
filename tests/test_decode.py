from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from qrflight.decode import decode_with_all
from qrflight.io import load_image


def test_real_qr_payload_is_read_by_both_engines(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png

    image = load_image(path)
    results = decode_with_all(image.pixels)

    assert [result.engine for result in results] == ["opencv", "zxing-cpp"]
    assert [result.payload for result in results] == [payload, payload]
    assert results[0].module_count == 29


def test_blank_image_returns_explicit_misses(blank_pixels: NDArray[np.uint8]) -> None:
    results = decode_with_all(blank_pixels)

    assert [result.payload for result in results] == [None, None]
