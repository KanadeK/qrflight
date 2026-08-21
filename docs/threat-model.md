# Threat model

## Trust boundary

The input raster, filename, decoded payload and output path are untrusted. QRFlight does not trust
file extensions: Pillow must successfully identify an allowed single-frame raster.

## Protected assets

- Local availability: crafted files must not cause unbounded memory or CPU use.
- Payload privacy: decoded content must stay on the local machine.
- Filesystem integrity: reports must not overwrite the analyzed image.
- Report integrity: filenames and payloads must remain data, never executable markup.

## Controls

- Input files are capped at 25 MiB and 40 megapixels.
- PNG, JPEG, WebP, BMP and single-frame TIFF are accepted; multi-frame images are rejected.
- Scenario count and output dimensions are fixed by the selected built-in profile.
- QRFlight makes no HTTP requests and never opens, resolves or executes a decoded payload.
- HTML escapes filenames, payloads and finding text and contains no JavaScript.
- The CLI refuses an output path that resolves to the input image.
- Expected input/output errors produce concise exit code 2 messages. Unexpected internal errors
  are not swallowed.

## Out of scope

QRFlight is not a sandbox for vulnerable native image libraries. Keep dependencies updated and do
not process hostile files with privileges beyond those needed to read the file and write a report.
It is not calibrated verification equipment and does not certify compliance with ISO/IEC 15415.

Report suspected vulnerabilities through the private process in `SECURITY.md`.
