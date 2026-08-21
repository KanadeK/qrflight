import cv2
import numpy as np
import zxingcpp
from numpy.typing import NDArray

from qrflight.models import DecoderResult


def decode_with_all(pixels: NDArray[np.uint8]) -> tuple[DecoderResult, DecoderResult]:
    """Decode grayscale pixels with the two supported QR engines."""
    opencv_payload, points, straight = cv2.QRCodeDetector().detectAndDecode(pixels)
    zxing_result = zxingcpp.read_barcode(pixels, formats=zxingcpp.BarcodeFormat.QRCode)
    corners = None
    if points is not None:
        corners = tuple((float(x), float(y)) for x, y in points[0])
    module_matrix = None
    if straight is not None:
        module_matrix = np.asarray(straight, dtype=np.uint8)
    return (
        DecoderResult(
            engine="opencv",
            payload=opencv_payload or None,
            corners=corners,
            module_matrix=module_matrix,
        ),
        DecoderResult(
            engine="zxing-cpp",
            payload=zxing_result.text if zxing_result is not None else None,
        ),
    )
