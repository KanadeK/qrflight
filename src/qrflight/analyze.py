import cv2
import numpy as np

from qrflight.models import DecoderResult, Finding, LoadedImage, StaticAnalysis

QUIET_ZONE_REQUIRED = 4.0
PRINTER_DOTS_REQUIRED = 4.0
CONTRAST_REQUIRED = 100.0
FRACTIONAL_MODULE_TOLERANCE = 0.1
SAMPLES_PER_MODULE = 8


def analyze_static(
    image: LoadedImage,
    decoders: tuple[DecoderResult, ...],
    *,
    print_width_mm: float | None = None,
    printer_dpi: int = 300,
) -> StaticAnalysis:
    """Measure baseline QR geometry and print-readiness signals."""
    findings: list[Finding] = []
    payloads = {result.payload for result in decoders if result.payload is not None}
    if len(payloads) > 1:
        findings.append(
            Finding(
                code="DECODER_DISAGREEMENT",
                severity="error",
                message="Decoders returned different payloads.",
            )
        )
        payload = None
    else:
        payload = next(iter(payloads), None)

    successful = sum(result.payload is not None for result in decoders)
    if successful == 0:
        findings.append(
            Finding(code="QR_UNREADABLE", severity="error", message="No decoder read the QR code.")
        )
    elif successful < len(decoders):
        findings.append(
            Finding(
                code="DECODER_MISS",
                severity="warning",
                message="Only one decoder read the QR code.",
            )
        )

    geometry = next(
        (
            result
            for result in decoders
            if result.corners is not None and result.module_matrix is not None
        ),
        None,
    )
    if geometry is None or geometry.corners is None or geometry.module_matrix is None:
        return StaticAnalysis(
            payload=payload,
            module_count=None,
            module_pixels=None,
            quiet_zone_modules=None,
            contrast=None,
            printer_dots_per_module=None,
            findings=tuple(findings),
        )

    module_count = geometry.module_matrix.shape[0]
    module_pixels = _module_pixels(geometry.corners, module_count)
    quiet_zone_modules = _quiet_zone_modules(
        image.pixels,
        geometry.corners,
        module_count,
    )
    contrast = _contrast(
        image.pixels,
        geometry.corners,
        geometry.module_matrix,
    )

    if quiet_zone_modules < QUIET_ZONE_REQUIRED:
        findings.append(
            Finding(
                code="QUIET_ZONE_TOO_SMALL",
                severity="warning",
                message=(
                    f"Quiet zone is about {quiet_zone_modules:g} modules; keep at least "
                    f"{QUIET_ZONE_REQUIRED:g} clear modules on every side."
                ),
                measured=quiet_zone_modules,
                required=QUIET_ZONE_REQUIRED,
            )
        )

    if contrast < CONTRAST_REQUIRED:
        findings.append(
            Finding(
                code="CONTRAST_TOO_LOW",
                severity="warning",
                message=(
                    f"Measured luminance contrast is {contrast:g}; use at least "
                    f"{CONTRAST_REQUIRED:g} on the 0-255 scale."
                ),
                measured=round(contrast, 3),
                required=CONTRAST_REQUIRED,
            )
        )

    fractional_error = abs(module_pixels - round(module_pixels))
    if fractional_error > FRACTIONAL_MODULE_TOLERANCE:
        findings.append(
            Finding(
                code="FRACTIONAL_MODULE_SCALING",
                severity="warning",
                message=(
                    f"Estimated module width is {module_pixels:.3f} pixels; export at an integer "
                    "number of pixels per module to avoid interpolation."
                ),
                measured=round(module_pixels, 3),
            )
        )

    printer_dots = None
    if print_width_mm is not None:
        qr_width_mm = print_width_mm * (module_pixels * module_count / image.width)
        printer_dots = qr_width_mm / module_count * printer_dpi / 25.4
        printer_dots = round(printer_dots, 3)
        if printer_dots < PRINTER_DOTS_REQUIRED:
            findings.append(
                Finding(
                    code="PRINTER_DOTS_TOO_SMALL",
                    severity="warning",
                    message=(
                        f"Estimated {printer_dots:g} printer dots per module; use at least "
                        f"{PRINTER_DOTS_REQUIRED:g}."
                    ),
                    measured=printer_dots,
                    required=PRINTER_DOTS_REQUIRED,
                )
            )

    return StaticAnalysis(
        payload=payload,
        module_count=module_count,
        module_pixels=round(module_pixels, 3),
        quiet_zone_modules=quiet_zone_modules,
        contrast=round(contrast, 3),
        printer_dots_per_module=printer_dots,
        findings=tuple(findings),
    )


def _module_pixels(corners: tuple[tuple[float, float], ...], module_count: int) -> float:
    points = np.asarray(corners, dtype=np.float32)
    sides = [np.linalg.norm(points[(index + 1) % 4] - points[index]) + 1.0 for index in range(4)]
    return float(np.mean(sides)) / module_count


def _normalized_canvas(
    pixels: np.ndarray,
    corners: tuple[tuple[float, float], ...],
    module_count: int,
    quiet_modules: int,
) -> np.ndarray:
    samples = SAMPLES_PER_MODULE
    size = (module_count + 2 * quiet_modules) * samples
    offset = quiet_modules * samples
    far = (quiet_modules + module_count) * samples - 1
    destination = np.asarray(
        [(offset, offset), (far, offset), (far, far), (offset, far)],
        dtype=np.float32,
    )
    transform = cv2.getPerspectiveTransform(np.asarray(corners, dtype=np.float32), destination)
    return cv2.warpPerspective(
        pixels,
        transform,
        (size, size),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )


def _quiet_zone_modules(
    pixels: np.ndarray,
    corners: tuple[tuple[float, float], ...],
    module_count: int,
) -> float:
    quiet = int(QUIET_ZONE_REQUIRED)
    samples = SAMPLES_PER_MODULE
    canvas = _normalized_canvas(pixels, corners, module_count, quiet)
    _, binary = cv2.threshold(canvas, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    code_start = quiet * samples
    code_end = (quiet + module_count) * samples
    confirmed = 0
    for ring in range(1, quiet + 1):
        before_start = (quiet - ring) * samples
        before_end = before_start + samples
        after_start = (quiet + module_count + ring - 1) * samples
        after_end = after_start + samples
        bands = (
            binary[code_start:code_end, before_start:before_end],
            binary[code_start:code_end, after_start:after_end],
            binary[before_start:before_end, code_start:code_end],
            binary[after_start:after_end, code_start:code_end],
        )
        if min(float(np.mean(band == 255)) for band in bands) < 0.95:
            break
        confirmed = ring
    return float(confirmed)


def _contrast(
    pixels: np.ndarray,
    corners: tuple[tuple[float, float], ...],
    module_matrix: np.ndarray,
) -> float:
    module_count = module_matrix.shape[0]
    rectified = _normalized_canvas(pixels, corners, module_count, 0)
    mask = cv2.resize(
        module_matrix,
        (rectified.shape[1], rectified.shape[0]),
        interpolation=cv2.INTER_NEAREST,
    )
    white = float(np.mean(rectified[mask >= 128]))
    black = float(np.mean(rectified[mask < 128]))
    return white - black
