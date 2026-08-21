from pathlib import Path

import numpy as np

from qrflight.degrade import apply_degradation, run_scenarios
from qrflight.io import load_image
from qrflight.models import Scenario
from qrflight.profiles import profile_scenarios


def test_print_profile_has_two_ordered_levels_per_family() -> None:
    scenarios = profile_scenarios("print")

    assert [scenario.name for scenario in scenarios] == [
        "blur-mild",
        "blur-strong",
        "jpeg-mild",
        "jpeg-strong",
        "downsample-mild",
        "downsample-strong",
        "contrast-mild",
        "contrast-strong",
    ]


def test_each_degradation_is_deterministic(qr_png: tuple[Path, str]) -> None:
    path, _ = qr_png
    pixels = load_image(path).pixels

    for scenario in profile_scenarios("quick"):
        first = apply_degradation(pixels, scenario)
        second = apply_degradation(pixels, scenario)
        assert first.shape == pixels.shape
        assert first.dtype == np.uint8
        assert np.array_equal(first, second)


def test_matrix_really_decodes_each_transformed_image(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png
    pixels = load_image(path).pixels

    results = run_scenarios(pixels, payload, profile_scenarios("quick"))

    assert len(results) == 4
    assert all(
        [decoder.engine for decoder in result.decoders] == ["opencv", "zxing-cpp"]
        for result in results
    )
    assert {result.status for result in results} <= {"pass", "partial", "fail"}


def test_extreme_downsample_crosses_a_real_failure_boundary(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png
    pixels = load_image(path).pixels
    scenario = Scenario(name="downsample-extreme", family="downsample", value=0.08)

    result = run_scenarios(pixels, payload, (scenario,))[0]

    assert result.status == "fail"
    assert [decoder.payload for decoder in result.decoders] == [None, None]
