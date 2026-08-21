from pathlib import Path

import pytest

from qrflight.io import InputError, load_image


def test_non_image_fails_at_input_boundary(tmp_path: Path) -> None:
    path = tmp_path / "not-an-image.png"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(InputError, match="not a supported image"):
        load_image(path)
