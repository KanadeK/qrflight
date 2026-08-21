# Architecture

QRFlight has one directional pipeline:

```text
untrusted raster
  -> bounded loader
  -> OpenCV + ZXing-C++ baseline decode
  -> static geometry and print estimates
  -> deterministic degradation scenarios
  -> OpenCV + ZXing-C++ scenario decode
  -> one versioned report
  -> text / JSON / offline HTML
```

## Module boundaries

- `io.py` is the image trust boundary. It enforces byte, format, frame and pixel limits before a
  NumPy array enters the rest of the program.
- `decode.py` adapts two independent decoders to one small result type. It does not assign
  severity.
- `analyze.py` derives QR module geometry, quiet-zone coverage, luminance contrast and optional
  printer dots per module from the baseline image.
- `degrade.py` contains four deterministic image transforms and immediately decodes their output.
- `profiles.py` is the full public list of bounded scenario parameters.
- `engine.py` orchestrates one check and is the only place that turns evidence into findings.
- `report.py` projects the same immutable report into three formats. Reporters do not reanalyze.
- `cli.py` validates public options, writes output and maps findings to exit codes.

There is no plug-in system, network client, database, background worker or application server.

## Result semantics

Each robustness scenario has one status:

- `pass`: both decoders returned the baseline payload.
- `partial`: exactly one decoder returned the baseline payload.
- `fail`: neither decoder returned the baseline payload.

A profile is evidence, not a universal score. Parameters and per-engine payloads remain visible in
JSON so users can reproduce every result.

## Physical estimates

When `--print-width-mm` is present, QRFlight interprets it as the full input image width on paper.
It derives the QR's share of that width from detected geometry, then estimates printer dots per
module using `--printer-dpi`. It does not infer or override missing physical dimensions.
