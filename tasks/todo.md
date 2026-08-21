# QRFlight v0.1.0 tasks

## Task 1: Contracts and fixtures

- [ ] Define immutable input, decoder, scenario, finding and report models.
- [ ] Generate known-payload healthy, cropped and low-contrast raster fixtures.
- Acceptance: fixtures are deterministic and the healthy payload is documented.
- Verify: focused fixture tests fail before the generator/model implementation and pass after it.
- Files: `src/qrflight/models.py`, `scripts/make_examples.py`, `tests/test_examples.py`.

## Task 2: Safe load and cross-decode

- [x] Enforce byte, pixel, format and frame limits.
- [x] Decode with OpenCV and ZXing-C++ and reconcile payloads.
- Acceptance: both engines match healthy payload; malformed and oversized inputs fail safely.
- Verify: `python -m pytest tests/test_io.py tests/test_decode.py -q`.
- Files: `src/qrflight/io.py`, `src/qrflight/decode.py`, corresponding tests.

## Task 3: Static print-readiness metrics

- [x] Measure module count/pixels, quiet zone, contrast and physical printer dots.
- [x] Emit targeted findings with measured/required values.
- Acceptance: healthy/cropped/fractionally scaled cases are distinguished.
- Verify: `python -m pytest tests/test_analyze.py -q`.
- Files: `src/qrflight/analyze.py`, `src/qrflight/geometry.py`, tests.

## Task 4: Deterministic degradation matrix

- [ ] Implement bounded scenario families and named profiles.
- [ ] Decode every transformed image with both engines.
- Acceptance: transformations are byte-deterministic and parameters appear in results.
- Verify: `python -m pytest tests/test_degrade.py tests/test_engine.py -q`.
- Files: `src/qrflight/degrade.py`, `src/qrflight/profiles.py`, engine/tests.

## Task 5: Reports and CLI

- [ ] Implement canonical report model and deterministic text/JSON/HTML renderers.
- [ ] Implement stable commands, validation and exit codes.
- Acceptance: formats agree; HTML escapes payloads; repeated files are byte-identical.
- Verify: `python -m pytest tests/test_report.py tests/test_cli.py -q`.
- Files: `src/qrflight/report.py`, `src/qrflight/cli.py`, tests.

## Task 6: Examples

- [ ] Commit real healthy/failing examples and generated hero evidence.
- Acceptance: README commands use committed files and visual evidence comes from real results.
- Verify: `python -m pytest tests/test_examples.py -q`.
- Files: examples/assets/scripts/tests.

## Task 7: Documentation and automation

- [ ] Complete README in English/Chinese, architecture, threat model, acceptance and repair docs.
- [ ] Add CI, CodeQL, release packaging, secret and metadata checks.
- Acceptance: one release command runs all documented gates; workflows use frozen dependencies.
- Verify: `python scripts/verify.py` and workflow syntax/static checks.
- Files: docs, READMEs, `.github`, `scripts`.

## Task 8: Review and public release

- [ ] Resolve independent correctness/architecture/security/performance review findings.
- [ ] Verify clean history, authors, contributors, tag, CI, Release assets and checksums.
- [ ] Send Gmail completion notification only after public verification.
- Acceptance: every success criterion in `docs/spec.md` has recorded evidence.
- Verify: `python scripts/release_check.py --online --strict`.
