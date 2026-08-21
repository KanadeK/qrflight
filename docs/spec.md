# Specification: QRFlight v0.1.0

## Objective

QRFlight is an offline command-line engineering preflight for QR artwork. It tells designers,
print operators and release engineers whether the supplied raster asset is readable now, which
print-readiness risks are measurable, and where independent decoders begin to fail under a
deterministic degradation suite.

It is not a calibrated barcode verifier. A passing report means only that the documented checks
and simulations passed for this file and configuration.

## Public contract

```text
qrflight check IMAGE [--expect TEXT] [--profile quick|print|screen|torture]
                     [--print-width-mm MM] [--printer-dpi DPI]
                     [--format text|json|html] [--output PATH]
                     [--fail-on none|note|warning|error|critical]
qrflight profiles
qrflight version
```

Exit codes are stable:

- `0`: command completed and no finding met `--fail-on`, or a non-check command succeeded.
- `1`: analysis completed and one or more findings met `--fail-on`.
- `2`: invalid arguments, unsafe/unreadable input, unsupported file, decoder initialization or
  output failure.

The JSON report uses `schema_version: "1.0"`, contains only relative/display input names, orders
families and scenarios deterministically, and never includes absolute local paths.

## Technology

- Python 3.12-3.13 and `hatchling` for a pure-Python wheel.
- Pillow for bounded image loading and report thumbnails.
- NumPy/OpenCV for geometry, metrics, transformations and one decoder.
- ZXing-C++ Python bindings for an independent decoder.
- Typer/Rich for a typed cross-platform CLI.
- Pytest, branch coverage, Ruff and strict mypy for verification.

Dependency versions are constrained in `pyproject.toml` and resolved into `uv.lock`. QRFlight
does not fetch URLs or execute decoded payloads.

## Commands

```powershell
# Bootstrap
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"

# Focused test
.venv\Scripts\python -m pytest tests/test_engine.py -q

# Full verification and release package
.venv\Scripts\python scripts/verify.py
.venv\Scripts\python scripts/package_release.py

# Five-minute acceptance
.venv\Scripts\qrflight check examples/healthy.png --profile print
.venv\Scripts\qrflight check examples/cropped.png --fail-on warning
.venv\Scripts\qrflight check examples/healthy.png --format html --output reports/healthy.html
```

POSIX equivalents use `.venv/bin/python` and `.venv/bin/qrflight`.

## Project structure

```text
src/qrflight/       package and CLI
tests/              unit, integration, CLI and abuse-case tests
examples/           deterministic healthy and failing assets
docs/               research, architecture, threat model, acceptance and ADRs
docs/assets/        generated visual evidence
scripts/            deterministic examples, verification and packaging
tasks/              implementation plan and tracked acceptance tasks
.github/workflows/  CI, CodeQL and release gates
```

## Code style

Public functions are typed; validated immutable dataclasses cross module boundaries. Orchestration
does not contain decoder- or transformation-specific branches.

```python
def analyze_image(image: LoadedImage, config: CheckConfig) -> AnalysisReport:
    """Return a deterministic report for an already validated image."""
    decoded = decode_with_all(image.pixels)
    baseline = reconcile_payloads(decoded, expected=config.expected_payload)
    return build_report(image, baseline, config)
```

Names describe physical units (`print_width_mm`, `module_pixels`, `printer_dots_per_module`). No
unlabelled numeric quality score may be added.

## Testing strategy

- Unit tests: finding thresholds, geometry, quiet-zone sampling, transformations, deterministic
  ordering, report encoding and HTML escaping.
- Integration tests: generated known-payload QR, cross-decoder agreement, cropped/low-contrast
  failure and expected-payload mismatch.
- CLI tests: all exit codes, stdout versus file output, invalid paths and each format.
- Abuse cases: decompression bombs, pixel limits, unsupported/multi-frame input, hostile filenames,
  HTML-like payloads and unwritable output.
- Release tests: full suite at >=90% branch coverage, lint, format, strict typing, build, metadata,
  dependency audit, secret scan, deterministic example assertions and clean-venv wheel smoke.

Tests use generated fixtures with known payloads and assert real decoder output. No fixed mock
result may stand in for the core analysis path.

## Security and resource boundaries

- Maximum input: 25 MiB, 40 megapixels, one frame. Pillow decompression warnings are errors.
- Accepted formats are detected from decoded content, not trusted extensions.
- No network access, shell execution, QR payload navigation, plug-in loading or dynamic code.
- HTML reports escape all names and payloads and embed only tool-generated PNG thumbnails.
- Output uses explicit files; analysis never overwrites the input.
- Transform counts and dimensions are profile-bounded; no user-controlled unbounded loops.
- Error messages omit stack traces and absolute paths unless `QRFLIGHT_DEBUG=1` is explicitly set.

## Boundaries

Always:

- Write a failing behavioral test before implementation behavior.
- Preserve deterministic order and stable exit semantics.
- Run the full verification gate before release commits.
- Label estimated metrics as estimates and retain scenario parameters in reports.

Ask first:

- Add network access, telemetry, a hosted service, new barcode symbologies or a breaking schema.
- Change exit codes or reinterpret existing severities.

Never:

- Claim ISO certification or guaranteed readability on every device.
- Upload, visit, execute or otherwise act on a decoded payload.
- Commit secrets, absolute user paths, skipped tests or generated build directories.

## Success criteria

1. A healthy committed example is decoded to the documented payload by both engines and exits 0.
2. A cropped committed example produces a quiet-zone finding and exits 1 at `--fail-on warning`.
3. An incorrect `--expect` produces an error finding rather than silently accepting another URL.
4. Every named degradation is actually rendered and decoded; JSON records per-engine outcomes.
5. Two runs on identical inputs/config produce byte-identical JSON and HTML.
6. The package installs from its wheel into a clean virtual environment and runs offline.
7. CI passes on Linux and Windows; CodeQL passes; a public v0.1.0 tag and GitHub Release expose
   the verified package built from the same commit.
8. Git author/committer and public contributor data list only KanadeK and contain no
   `Co-authored-by` trailer.
9. README includes exact acceptance commands and a failure-to-repair procedure.

## Open questions resolved for v0.1

- Default gate: `--fail-on error`; warnings are visible but opt-in as a strict CI failure.
- Default profile: `print`; it uses a bounded set of mild and moderate scenarios.
- Physical input: `--print-width-mm` is the full image width on paper. Code size is derived from
  its measured pixel share. `--printer-dpi` defaults to 300 only when physical width is supplied.

## Approval

Accepted on 2026-08-12 under the user's explicit authority to choose and implement the project
through publication.
