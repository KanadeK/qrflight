from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class LoadedImage:
    display_name: str
    format: str
    width: int
    height: int
    pixels: NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class DecoderResult:
    engine: str
    payload: str | None
