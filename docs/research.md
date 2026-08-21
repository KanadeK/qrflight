# Gap research

Research was performed on 2026-08-12 before repository creation. Star counts are a dated snapshot,
not current claims.

## User pain

- DENSO WAVE documents a four-module quiet zone and recommends at least four printer dots per
  module for stable printing: <https://www.qrcode.com/en/howto/code.html> and
  <https://www.qrcode.com/en/howto/cell.html>.
- A Stack Overflow question about reducing the quiet zone has more than 50,000 views, and the
  accepted guidance warns that reducing it lowers decoding reliability:
  <https://stackoverflow.com/questions/10142748/reduce-border-width-on-qr-codes-generated-by-zxing>.
- Repeated questions describe broken QR output after resizing, blur and print interpolation:
  <https://stackoverflow.com/questions/30012079/how-to-re-size-qrcode-image-without-losing-resolution>,
  <https://stackoverflow.com/questions/25873997/how-to-fix-an-unclear-qr-code-image-generated-using-zxing-2-1>, and
  <https://stackoverflow.com/questions/71055395/what-is-the-best-lossless-way-to-scale-up-a-barcode-image-in-c-sharp>.

## GitHub search

Exact intent queries included `qr code print quality`, `qr code robustness test`, `qr code damage
simulator`, `qr code preflight`, `qr code quiet zone contrast`, `printable qr verification`,
`barcode print quality verifier`, `qr code test suite`, and `qr damage`. They returned no mature
open-source project focused on reproducible print-readiness stress testing.

The adjacent category is demonstrably active but answers different questions:

| Repository | Stars at research time | Job |
| --- | ---: | --- |
| [zxing/zxing](https://github.com/zxing/zxing) | 34,067 | General barcode decoding |
| [davidshimjs/qrcodejs](https://github.com/davidshimjs/qrcodejs) | 14,301 | Browser QR generation |
| [soldair/node-qrcode](https://github.com/soldair/node-qrcode) | 8,159 | Node QR generation |
| [nayuki/QR-Code-generator](https://github.com/nayuki/QR-Code-generator) | 6,708 | Multi-language generation |
| [mebjas/html5-qrcode](https://github.com/mebjas/html5-qrcode) | 6,201 | Browser scanning |
| [cozmo/jsQR](https://github.com/cozmo/jsQR) | 4,022 | JavaScript decoding |

Commercial SDKs can expose ISO quality tests, but ordinary raster input cannot establish the
calibrated acquisition conditions required for a certification claim. QRFlight therefore occupies
a narrower engineering-preflight position and explicitly rejects ISO grading.

## Local project overlap

The workspace inventory found no documented QR print-reliability tool. The closest project,
`dpp-preflight`, generates a GS1 Digital Link carrier inside a product-passport bundle; it does not
measure or stress-test scan reliability. QRFlight validates existing QR artwork from any source.

## Product decision

Build one offline CLI job: prove the baseline payload, expose actionable print signals, then show
where independent decoders stop agreeing under named deterministic degradations. Do not build a QR
generator, upload service, dashboard or certification facade.
