from pathlib import Path

import cv2
import numpy as np

from qrflight.analyze import analyze_static
from qrflight.decode import decode_with_all
from qrflight.io import load_image


def test_healthy_qr_reports_real_geometry(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png
    image = load_image(path)

    analysis = analyze_static(
        image,
        decode_with_all(image.pixels),
        print_width_mm=20.0,
        printer_dpi=300,
    )

    assert analysis.payload == payload
    assert analysis.module_count == 29
    assert analysis.module_pixels == 8.0
    assert analysis.quiet_zone_modules == 4.0
    assert analysis.contrast >= 250.0
    assert analysis.printer_dots_per_module is not None
    assert analysis.printer_dots_per_module > 4.0
    assert analysis.findings == ()


def test_cropped_quiet_zone_is_actionable(qr_png: tuple[Path, str], tmp_path: Path) -> None:
    path, _ = qr_png
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    cropped_path = tmp_path / "cropped.png"
    assert cv2.imwrite(str(cropped_path), pixels[32:-32, 32:-32])
    image = load_image(cropped_path)

    analysis = analyze_static(image, decode_with_all(image.pixels))

    assert analysis.quiet_zone_modules == 2.0
    assert [finding.code for finding in analysis.findings] == ["QUIET_ZONE_TOO_SMALL"]


def test_small_print_size_reports_insufficient_printer_dots(qr_png: tuple[Path, str]) -> None:
    path, _ = qr_png
    image = load_image(path)

    analysis = analyze_static(
        image,
        decode_with_all(image.pixels),
        print_width_mm=10.0,
        printer_dpi=300,
    )

    assert analysis.printer_dots_per_module is not None
    assert analysis.printer_dots_per_module < 4.0
    assert [finding.code for finding in analysis.findings] == ["PRINTER_DOTS_TOO_SMALL"]


def test_low_contrast_is_reported(qr_png: tuple[Path, str], tmp_path: Path) -> None:
    path, _ = qr_png
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    low_contrast = np.where(pixels < 128, 100, 180).astype(np.uint8)
    low_contrast_path = tmp_path / "low-contrast.png"
    assert cv2.imwrite(str(low_contrast_path), low_contrast)
    image = load_image(low_contrast_path)

    analysis = analyze_static(image, decode_with_all(image.pixels))

    assert analysis.contrast is not None
    assert analysis.contrast < 100.0
    assert "CONTRAST_TOO_LOW" in [finding.code for finding in analysis.findings]


def test_fractional_module_scaling_is_reported(qr_png: tuple[Path, str], tmp_path: Path) -> None:
    path, _ = qr_png
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    scaled = cv2.resize(pixels, (307, 307), interpolation=cv2.INTER_NEAREST)
    scaled_path = tmp_path / "fractional.png"
    assert cv2.imwrite(str(scaled_path), scaled)
    image = load_image(scaled_path)

    analysis = analyze_static(image, decode_with_all(image.pixels))

    assert analysis.module_pixels is not None
    assert abs(analysis.module_pixels - round(analysis.module_pixels)) > 0.1
    assert [finding.code for finding in analysis.findings] == ["FRACTIONAL_MODULE_SCALING"]
