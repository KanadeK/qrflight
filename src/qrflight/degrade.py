from typing import Literal

import cv2
import numpy as np
from numpy.typing import NDArray

from qrflight.decode import decode_with_all
from qrflight.models import Scenario, ScenarioResult


def apply_degradation(pixels: NDArray[np.uint8], scenario: Scenario) -> NDArray[np.uint8]:
    """Apply one deterministic degradation to grayscale pixels."""
    if scenario.family == "blur":
        kernel = max(3, round(scenario.value * 6) | 1)
        return np.asarray(
            cv2.GaussianBlur(pixels, (kernel, kernel), scenario.value), dtype=np.uint8
        )
    if scenario.family == "jpeg":
        encoded = cv2.imencode(".jpg", pixels, [cv2.IMWRITE_JPEG_QUALITY, int(scenario.value)])[1]
        return np.asarray(cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE), dtype=np.uint8)
    if scenario.family == "downsample":
        small = cv2.resize(
            pixels,
            None,
            fx=scenario.value,
            fy=scenario.value,
            interpolation=cv2.INTER_AREA,
        )
        restored = cv2.resize(
            small,
            (pixels.shape[1], pixels.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
        return np.asarray(restored, dtype=np.uint8)
    if scenario.family == "contrast":
        adjusted = (pixels.astype(np.float32) - 127.5) * scenario.value + 127.5
        return np.asarray(np.clip(adjusted, 0, 255), dtype=np.uint8)
    raise ValueError(f"unknown degradation family: {scenario.family}")


def run_scenarios(
    pixels: NDArray[np.uint8],
    expected_payload: str,
    scenarios: tuple[Scenario, ...],
) -> tuple[ScenarioResult, ...]:
    """Transform and cross-decode every scenario in order."""
    results: list[ScenarioResult] = []
    for scenario in scenarios:
        decoders = decode_with_all(apply_degradation(pixels, scenario))
        matches = [decoder.payload == expected_payload for decoder in decoders]
        status: Literal["pass", "partial", "fail"]
        if all(matches):
            status = "pass"
        elif any(matches):
            status = "partial"
        else:
            status = "fail"
        results.append(ScenarioResult(scenario=scenario, status=status, decoders=decoders))
    return tuple(results)
