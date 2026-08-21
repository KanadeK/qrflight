# QRFlight

[![CI](https://github.com/KanadeK/qrflight/actions/workflows/ci.yml/badge.svg)](https://github.com/KanadeK/qrflight/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776ab)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Your QR scans on screen. Will it still scan after layout, compression, and print?**

QRFlight is an offline command-line preflight for QR artwork. It reads the real raster with
OpenCV and ZXing-C++, measures actionable print signals, then reruns both decoders after
deterministic blur, JPEG, downsampling and contrast degradations.

[中文说明](README.zh-CN.md)

![A QR code tested across the QRFlight print profile](docs/assets/robustness-grid.png)

The grid is not a mockup. Every cell is the transformed image named underneath it, and every
status is produced by decoding that exact cell with both engines.

> QRFlight is an engineering preflight, not a calibrated ISO/IEC 15415 verifier or a guarantee
> that every phone, printer, paper, and lighting condition will work.

## Why this exists

A successful scan of the source PNG proves very little about the delivered artifact. A layout
tool can crop the four-module quiet zone, fractional resizing can blur module edges, a print job
can leave too few device dots per module, and compression or camera processing can make decoder
implementations disagree.

DENSO WAVE documents a four-module quiet zone and recommends at least four printer dots per module
for stable output. Public questions about quiet zones, resizing and print interpolation have
persisted for years. Yet high-star open-source QR projects overwhelmingly generate or decode a
single image; exact searches found no mature offline tool that measures and reproduces the failure
boundary. See [the dated gap research](docs/research.md).

## Five-minute start

Python 3.12+ and [uv](https://docs.astral.sh/uv/) are required for a source checkout.

```powershell
git clone https://github.com/KanadeK/qrflight.git
cd qrflight
uv sync --locked --extra dev

# Healthy baseline: exits 0.
uv run qrflight check examples/healthy.png --profile quick

# Deliberately cropped quiet zone: exits 1 with a direct repair when warnings gate CI.
uv run qrflight check examples/cropped.png --profile quick --fail-on warning

# Require the exact content, not merely "something decodable".
uv run qrflight check examples/healthy.png --expect https://github.com/KanadeK/qrflight

# Write a self-contained offline evidence report.
uv run qrflight check examples/healthy.png --format html --output healthy-report.html
```

After v0.1.0 is released, install its wheel without cloning:

```powershell
pipx install https://github.com/KanadeK/qrflight/releases/download/v0.1.0/qrflight-0.1.0-py3-none-any.whl
```

## What it checks

| Evidence | What QRFlight reports | Repair direction |
| --- | --- | --- |
| Baseline cross-decode | Payload from OpenCV and ZXing-C++ | Regenerate if unreadable or inconsistent |
| Quiet zone | Consecutive clear modules, up to the required four | Add whitespace around every side |
| Module rasterization | Measured pixels per module and fractional scaling | Export at an integer module multiple |
| Contrast | Mean white/black luminance separation | Darken foreground or lighten background |
| Physical print estimate | Printer dots per module from width and DPI | Print larger or use higher DPI |
| Robustness profile | Per-engine result after every named transform | Inspect the first partial/failing scenario |

Physical estimation is opt-in because QRFlight will not invent print dimensions:

```powershell
uv run qrflight check artwork.png --print-width-mm 24 --printer-dpi 300
```

`--print-width-mm` means the full input image width on paper, including its quiet zone.

## Profiles and reports

- `quick`: one scenario for each of the four degradation families.
- `print` (default): mild and strong levels for each family.

Use `--format text`, `--format json`, or `--format html`. JSON schema version `1.0` includes input
dimensions, baseline decoder evidence, measured signals, every scenario parameter/result and all
findings. HTML is self-contained, contains no JavaScript and escapes decoded payloads.

Exit codes are deliberately simple:

| Code | Meaning |
| ---: | --- |
| 0 | Completed; no finding met `--fail-on` |
| 1 | Completed; a finding met `--fail-on` |
| 2 | Invalid option, unsupported/unreadable input, or output error |

The default is `--fail-on error`; use `--fail-on warning` for a strict print gate or
`--fail-on none` to collect evidence without blocking.

## Verification and repair

```powershell
uv run python scripts/verify.py
```

This runs format/lint, strict typing, branch coverage, package build/metadata validation and a
clean-venv wheel smoke test. Exact acceptance commands, expected exits and a finding-by-finding
repair table are in [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md).

## Design boundaries

- Offline only: no URL fetching, telemetry, upload or payload navigation.
- QR Code only in v0.1; other symbologies have different geometry and contracts.
- Raster input only: PNG, JPEG, WebP, BMP and single-frame TIFF.
- No universal score and no ISO grade. Raw parameters and decoder outcomes stay visible.

Read [the architecture](docs/architecture.md), [threat model](docs/threat-model.md), and
[design decision](docs/decisions/0001-engineering-preflight-not-certification.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities through GitHub private vulnerability
reporting as described in [SECURITY.md](SECURITY.md). QRFlight is released under the MIT License.
