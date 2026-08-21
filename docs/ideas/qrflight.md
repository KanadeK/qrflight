# QRFlight

## Problem statement

How might we help designers, print shops and maintainers catch QR artwork that scans on a
monitor but fails after layout, scaling, compression, printing or phone capture, without buying
calibrated verification hardware or uploading customer payloads to a website?

## Recommended direction

Build an offline engineering preflight, not another generator and not an ISO certification
claim. QRFlight reads the actual raster asset, checks design and print-readiness signals, decodes
it with independent engines, then measures a reproducible failure boundary across named image
degradations. Every result keeps the original payload local and includes evidence that a human or
CI job can inspect.

The target user is someone about to ship or print a QR-bearing asset. Success means that within
five minutes they can identify a concrete cause such as a cropped quiet zone, fractional module
scaling, insufficient printer dots per module, low contrast, or failure under a mild degradation.

## Alternatives considered

1. A QR generator with safer defaults: useful, but the mature generator market is already
   crowded and it cannot validate artwork produced elsewhere.
2. A browser-only scanner: easy to demo, but it proves only that one engine reads one current
   image and conflicts with the local/private requirement.
3. A calibrated ISO/IEC 15415 verifier: valuable, but dishonest without controlled illumination,
   optics and calibration targets.
4. A generic image linter: broad but weak. It would lose the physical QR module model and become
   indistinguishable from existing local audit projects.

## Key assumptions to validate

- [x] The pain recurs: public questions repeatedly report quiet-zone, scaling, blur and print
  interpolation failures.
- [x] The category has demand: QR generation and decoding foundations have thousands to tens of
  thousands of GitHub stars.
- [x] The specific discoverable gap exists: exact GitHub searches for QR print preflight and
  robustness testing returned no mature repository on 2026-08-12.
- [ ] Synthetic failure thresholds correlate with physical print/capture workflows. This remains
  an explicit post-v0.1 validation question and is not implied by the synthetic results.

## MVP scope

- Raster input: PNG, JPEG, WebP, BMP and single-frame TIFF.
- OpenCV and ZXing-C++ cross-decoding with payload agreement checks.
- Quiet-zone, contrast, module-size, fractional-scaling and physical printer-dot estimates.
- Deterministic degradation profiles covering common print/capture failure modes.
- Text, versioned JSON and self-contained offline HTML reports.
- Stable exit codes and configurable fail threshold for CI.

## Not doing (and why)

- ISO/IEC 15415 grades or certification: uncalibrated images cannot support that claim.
- Web upload or hosted service: payload privacy and offline use are product constraints.
- QR styling or general generation UX: crowded category and not the core job.
- PDF/SVG layout parsing in v0.1: rasterizing an entire page raises ambiguous crop and scale
  semantics; explicit raster export plus print width makes the first contract testable.
- Data Matrix, Aztec and 1D barcodes: each has different geometry and standards.
- A dashboard: reports and a CLI deliver the complete user job without an application shell.

## Open questions

- Which synthetic scenarios best predict a specific printer/paper/camera pipeline?
- Should a future release ingest calibration-sheet photos and automatically locate each cell?
- Which vector/PDF crop contract is least surprising for a future input adapter?

## Decision

Accepted on 2026-08-12 under the user's goal-scoped authorization to research, choose and ship a
distinct practical open-source tool end to end.
