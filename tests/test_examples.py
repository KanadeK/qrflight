from pathlib import Path

import cv2

from qrflight.engine import CheckConfig, check_image

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"


def test_healthy_example_passes_default_error_gate() -> None:
    report, _ = check_image(EXAMPLES / "healthy.png", CheckConfig(profile="quick"))

    assert report.payload == "https://github.com/KanadeK/qrflight"
    assert not any(finding.severity == "error" for finding in report.findings)


def test_cropped_example_has_quiet_zone_finding() -> None:
    report, _ = check_image(EXAMPLES / "cropped.png", CheckConfig(profile="quick"))

    assert "QUIET_ZONE_TOO_SMALL" in [finding.code for finding in report.findings]


def test_low_contrast_example_has_contrast_finding() -> None:
    report, _ = check_image(EXAMPLES / "low-contrast.png", CheckConfig(profile="quick"))

    assert "CONTRAST_TOO_LOW" in [finding.code for finding in report.findings]


def test_robustness_grid_is_a_real_png() -> None:
    grid = cv2.imread(str(ROOT / "docs" / "assets" / "robustness-grid.png"))

    assert grid is not None
    assert grid.shape[0] >= 600
    assert grid.shape[1] >= 900
