from dataclasses import dataclass
from typing import Literal

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
    corners: tuple[tuple[float, float], ...] | None = None
    module_matrix: NDArray[np.uint8] | None = None

    @property
    def module_count(self) -> int | None:
        return self.module_matrix.shape[0] if self.module_matrix is not None else None


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: str
    message: str
    measured: float | None = None
    required: float | None = None


@dataclass(frozen=True, slots=True)
class StaticAnalysis:
    payload: str | None
    module_count: int | None
    module_pixels: float | None
    quiet_zone_modules: float | None
    contrast: float | None
    printer_dots_per_module: float | None
    findings: tuple[Finding, ...]


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    family: str
    value: float


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario: Scenario
    status: Literal["pass", "partial", "fail"]
    decoders: tuple[DecoderResult, ...]
