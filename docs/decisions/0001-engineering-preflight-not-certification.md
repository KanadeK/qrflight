# ADR-0001: Build an engineering preflight, not a certification verifier

## Status

Accepted

## Date

2026-08-12

## Context

QR print failures are affected by geometry, rasterization, ink/paper, lighting, optics, camera
processing and decoder behavior. ISO/IEC 15415 verification uses defined acquisition and
calibration conditions. QRFlight receives ordinary digital images and optional print dimensions;
it cannot establish those controlled conditions.

## Decision

QRFlight reports measured image signals and reproducible decoder outcomes under named synthetic
scenarios. It calls physical values estimates, exposes raw parameters and never emits an ISO grade
or certification claim. A clean run is scoped to the documented checks, engines and profile.

## Alternatives considered

### Implement a subset of ISO grading labels

Rejected because familiar grade names would create false confidence even with disclaimers.

### Report only baseline decodability

Rejected because one successful decode is exactly the false-confidence gap the project targets.

### Avoid any summary status

Rejected because CI needs a stable gate. Findings and thresholds provide a bounded status without
inventing a universal quality score.

## Consequences

- Reports must preserve scenario names, parameters, engine outcomes and caveats.
- Marketing and documentation must use "preflight", "estimate" and "robustness", not "certify".
- Correlation with physical workflows must be established with future captured samples rather
  than stronger unsupported claims in v0.1.
