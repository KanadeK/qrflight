# Repository rules

- Treat every input image as untrusted. Keep byte, pixel, frame and output limits fail-closed.
- Do not describe QRFlight as an ISO/IEC 15415 verifier or certification tool.
- Preserve CLI exit codes: 0 accepted, 1 completed with findings at the configured threshold, 2 tool/input error.
- Keep reports deterministic and offline. Never fetch URLs embedded in QR payloads.
- Add a failing behavioral test before changing analyzer, degradation, decoder or exit-code behavior.
- Run `python scripts/verify.py` before a release commit.
- Never commit generated build directories, credentials, absolute user paths or `Co-authored-by` trailers.

