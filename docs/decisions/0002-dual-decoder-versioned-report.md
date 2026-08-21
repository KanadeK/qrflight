# ADR-0002: Cross-decode into one versioned report model

## Status

Accepted

## Date

2026-08-12

## Context

Decoder success is implementation-dependent, while separate output paths easily drift. CI users
also need a durable machine contract.

## Decision

Use OpenCV QRCodeDetector and ZXing-C++ adapters for each baseline and scenario. Adapters return
the same typed result without assigning severity. The engine reconciles payloads and produces one
immutable report model with schema version 1.0. Text, JSON and HTML are pure projections of it.

## Alternatives considered

### One decoder

Rejected because it proves compatibility with only one implementation.

### More than two decoders in v0.1

Rejected because native/WASM dependency cost grows faster than the added early evidence.

### Each reporter computes its own summary

Rejected because formats would eventually disagree on counts, ordering or thresholds.

## Consequences

- Decoder disagreement is visible and actionable.
- Reporter determinism and parity can be contract-tested.
- Schema changes must be additive within 1.x or receive a new major schema version.
