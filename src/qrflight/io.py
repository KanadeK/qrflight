import warnings
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from qrflight.models import LoadedImage

MAX_INPUT_BYTES = 25 * 1024 * 1024
MAX_PIXELS = 40_000_000
ALLOWED_FORMATS = frozenset({"PNG", "JPEG", "WEBP", "BMP", "TIFF"})


class InputError(ValueError):
    """Raised when an image fails QRFlight's input boundary."""


def load_image(path: Path) -> LoadedImage:
    """Load one bounded raster image as grayscale pixels."""
    try:
        size = path.stat().st_size
    except OSError as error:
        raise InputError(f"cannot read input: {path.name}") from error
    if size > MAX_INPUT_BYTES:
        raise InputError(f"input exceeds {MAX_INPUT_BYTES} bytes: {path.name}")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as source:
                image_format = source.format or ""
                if image_format not in ALLOWED_FORMATS:
                    raise InputError(f"not a supported image: {path.name}")
                if getattr(source, "n_frames", 1) != 1:
                    raise InputError(f"multi-frame images are not supported: {path.name}")
                width, height = source.size
                if width * height > MAX_PIXELS:
                    raise InputError(f"image exceeds {MAX_PIXELS} pixels: {path.name}")
                pixels = np.asarray(source.convert("L"), dtype=np.uint8)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as error:
        raise InputError(f"not a supported image: {path.name}") from error

    return LoadedImage(
        display_name=path.name,
        format=image_format,
        width=width,
        height=height,
        pixels=pixels,
    )
