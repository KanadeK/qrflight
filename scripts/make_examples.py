from pathlib import Path

import cv2
import numpy as np

from qrflight.degrade import apply_degradation, run_scenarios
from qrflight.profiles import profile_scenarios

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
ASSETS = ROOT / "docs" / "assets"
PAYLOAD = "https://github.com/KanadeK/qrflight"


def main() -> None:
    EXAMPLES.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)

    modules = cv2.QRCodeEncoder_create().encode(PAYLOAD)
    bordered = cv2.copyMakeBorder(modules, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=255)
    healthy = cv2.resize(bordered, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
    cropped = healthy[32:-32, 32:-32]
    low_contrast = np.where(healthy < 128, 100, 180).astype(np.uint8)

    _write_png(EXAMPLES / "healthy.png", healthy)
    _write_png(EXAMPLES / "cropped.png", cropped)
    _write_png(EXAMPLES / "low-contrast.png", low_contrast)
    _write_png(ASSETS / "robustness-grid.png", _robustness_grid(healthy))


def _robustness_grid(healthy: np.ndarray) -> np.ndarray:
    scenarios = profile_scenarios("print")
    results = run_scenarios(healthy, PAYLOAD, scenarios)
    cells = [_cell(healthy, "original", "pass")]
    cells.extend(
        _cell(apply_degradation(healthy, result.scenario), result.scenario.name, result.status)
        for result in results
    )
    rows = [np.hstack(cells[index : index + 3]) for index in range(0, len(cells), 3)]
    return np.vstack(rows)


def _cell(pixels: np.ndarray, label: str, status: str) -> np.ndarray:
    preview = cv2.resize(pixels, (300, 300), interpolation=cv2.INTER_NEAREST)
    canvas = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
    color = {"pass": (52, 120, 55), "partial": (0, 133, 205), "fail": (55, 55, 190)}[status]
    footer = np.full((70, 300, 3), 248, dtype=np.uint8)
    cv2.putText(footer, label, (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (25, 30, 25), 1)
    cv2.putText(footer, status.upper(), (12, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return np.vstack((canvas, footer))


def _write_png(path: Path, pixels: np.ndarray) -> None:
    if not cv2.imwrite(str(path), pixels):
        raise OSError(f"could not write {path.name}")


if __name__ == "__main__":
    main()
