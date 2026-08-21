from pathlib import Path

import cv2
import numpy as np
import pytest


@pytest.fixture
def qr_png(tmp_path: Path) -> tuple[Path, str]:
    payload = "https://example.com/qrflight-demo"
    modules = cv2.QRCodeEncoder_create().encode(payload)
    bordered = cv2.copyMakeBorder(modules, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=255)
    image = cv2.resize(bordered, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
    path = tmp_path / "healthy.png"
    assert cv2.imwrite(str(path), image)
    return path, payload


@pytest.fixture
def blank_pixels() -> np.ndarray:
    return np.full((256, 256), 255, dtype=np.uint8)
