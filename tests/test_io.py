from pathlib import Path

import pytest
from PIL import Image

import qrflight.io as image_io
from qrflight.io import InputError, load_image


def test_non_image_fails_at_input_boundary(tmp_path: Path) -> None:
    path = tmp_path / "not-an-image.png"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(InputError, match="not a supported image"):
        load_image(path)


def test_input_byte_limit_fails_before_image_decode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "too-large.png"
    path.write_bytes(b"1234")
    monkeypatch.setattr(image_io, "MAX_INPUT_BYTES", 3)

    with pytest.raises(InputError, match="input exceeds 3 bytes"):
        load_image(path)


def test_pixel_limit_fails_before_pixel_allocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "too-many-pixels.png"
    Image.new("L", (2, 2), 255).save(path)
    monkeypatch.setattr(image_io, "MAX_PIXELS", 3)

    with pytest.raises(InputError, match="image exceeds 3 pixels"):
        load_image(path)


def test_multi_frame_tiff_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "animated.tiff"
    first = Image.new("L", (16, 16), 255)
    second = Image.new("L", (16, 16), 0)
    first.save(path, save_all=True, append_images=[second])

    with pytest.raises(InputError, match="multi-frame images are not supported"):
        load_image(path)
