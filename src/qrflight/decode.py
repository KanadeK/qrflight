import cv2
import numpy as np
import zxingcpp
from numpy.typing import NDArray

from qrflight.models import DecoderResult


def decode_with_all(pixels: NDArray[np.uint8]) -> tuple[DecoderResult, DecoderResult]:
    """Decode grayscale pixels with the two supported QR engines."""
    opencv_payload, _, _ = cv2.QRCodeDetector().detectAndDecode(pixels)
    zxing_result = zxingcpp.read_barcode(pixels, formats=zxingcpp.BarcodeFormat.QRCode)
    return (
        DecoderResult(engine="opencv", payload=opencv_payload or None),
        DecoderResult(
            engine="zxing-cpp",
            payload=zxing_result.text if zxing_result is not None else None,
        ),
    )
