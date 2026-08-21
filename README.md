# QRFlight

**Your QR scans on screen. Will it still scan after layout, compression, and print?**

QRFlight is an offline command-line preflight for QR artwork. It cross-checks the real image with
independent decoders, measures print-readiness signals, and reruns decoding after deterministic
degradations. Reports explain what failed instead of returning a vague quality score.

> QRFlight is an engineering preflight, not a calibrated ISO/IEC 15415 verifier or a guarantee
> that every phone, printer, paper, and lighting condition will work.

The implementation is in progress. The executable quick start and acceptance commands will be
added before v0.1.0 is published.

## Development

```powershell
uv sync --extra dev
uv run pytest
```

See [the v0.1 specification](docs/spec.md) and [implementation plan](tasks/plan.md).

## License

MIT
