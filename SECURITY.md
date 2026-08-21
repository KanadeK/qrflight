# Security policy

## Supported versions

Security fixes are applied to the latest release.

## Reporting

Please use GitHub's private vulnerability reporting for this repository. Do not post a malicious
sample, exploit details or a sensitive QR payload in a public issue.

Include the QRFlight version, operating system, Python version, file format/dimensions, the minimum
steps needed to reproduce, and whether the issue affects availability, payload confidentiality,
filesystem integrity or HTML report safety.

## Scope reminder

QRFlight processes untrusted local raster files through Pillow, OpenCV and ZXing-C++. Run it with
least privilege. It performs no network requests and never follows decoded payloads.
