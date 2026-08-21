# Acceptance and repair

## One-command release gate

From a checkout with Python 3.12 or newer and `uv` installed:

```powershell
uv sync --locked --extra dev
uv run python scripts/verify.py
```

The gate formats-checks and lints source/tests/scripts, runs strict mypy, requires at least 90%
branch coverage, builds wheel and source distribution, validates package metadata, installs the
wheel into a clean virtual environment and runs `qrflight version` from that wheel.

## Functional acceptance

```powershell
# Expected exit 0: both baseline decoders recover the documented payload.
uv run qrflight check examples/healthy.png --profile quick

# Expected exit 1: analysis completes, but the two-module quiet zone fails the warning gate.
uv run qrflight check examples/cropped.png --profile quick --fail-on warning

# Expected exit 1: a different payload is a correctness error.
uv run qrflight check examples/healthy.png --expect https://wrong.example

# Expected exit 0 and a self-contained local report.
uv run qrflight check examples/healthy.png --format html --output healthy-report.html
```

## Exit codes

| Code | Meaning |
| ---: | --- |
| 0 | Check completed and no finding met `--fail-on`, or another command succeeded |
| 1 | Check completed and at least one finding met `--fail-on` |
| 2 | Invalid option, unreadable/unsupported input, or output write error |

## Failure-to-repair matrix

| Finding or error | Meaning | Direct repair |
| --- | --- | --- |
| `QR_UNREADABLE` | Neither decoder read the baseline | Export a crisp QR with a clear quiet zone; do not print yet |
| `DECODER_MISS` | Only one baseline decoder read it | Increase module size/contrast and remove styling or interpolation |
| `DECODER_DISAGREEMENT` | Decoders returned different payloads | Regenerate from the intended payload and verify `--expect` |
| `EXPECTED_PAYLOAD_MISMATCH` | Readable content is not the required content | Replace the asset; never redirect around this gate |
| `QUIET_ZONE_TOO_SMALL` | Fewer than four clear modules were measured | Add whitespace on every side; do not stretch the QR itself |
| `CONTRAST_TOO_LOW` | Luminance difference is below the engineering threshold | Use a darker foreground and lighter, non-transparent background |
| `FRACTIONAL_MODULE_SCALING` | Module width is not near an integer pixel count | Export at an integer multiple of the QR module grid |
| `PRINTER_DOTS_TOO_SMALL` | Estimated print dots per module are below four | Print larger or use a higher printer DPI |
| `ROBUSTNESS_PARTIAL` | One decoder failed a scenario | Inspect that scenario; increase margin before strict gating |
| `ROBUSTNESS_FAILED` | Both decoders failed a scenario | Repair the asset or choose a justified, documented profile |
| `not a supported image` | Header/format is invalid or unsupported | Export one PNG/JPEG/WebP/BMP/single-frame TIFF and retry |
| `cannot write output` | The destination cannot be created | Choose an existing writable directory and filename |

If a test fails, run the named test printed by pytest. Do not skip it. If wheel smoke fails while
source tests pass, remove `.venv`, rerun `uv sync --locked --extra dev`, and inspect the first pip or
import error from the clean environment.
