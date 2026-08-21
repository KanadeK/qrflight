from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from qrflight import __version__
from qrflight.analyze import analyze_static
from qrflight.decode import decode_with_all
from qrflight.degrade import run_scenarios
from qrflight.io import load_image
from qrflight.models import AnalysisReport, Finding, ScenarioResult
from qrflight.profiles import profile_scenarios


@dataclass(frozen=True, slots=True)
class CheckConfig:
    profile: str = "print"
    expected_payload: str | None = None
    print_width_mm: float | None = None
    printer_dpi: int = 300


def check_image(
    path: Path,
    config: CheckConfig,
) -> tuple[AnalysisReport, NDArray[np.uint8]]:
    """Run the complete offline preflight for one image."""
    image = load_image(path)
    baseline_decoders = decode_with_all(image.pixels)
    metrics = analyze_static(
        image,
        baseline_decoders,
        print_width_mm=config.print_width_mm,
        printer_dpi=config.printer_dpi,
    )
    findings = list(metrics.findings)

    if (
        config.expected_payload is not None
        and metrics.payload is not None
        and metrics.payload != config.expected_payload
    ):
        findings.append(
            Finding(
                code="EXPECTED_PAYLOAD_MISMATCH",
                severity="error",
                message="Decoded payload does not match --expect.",
            )
        )

    scenarios: tuple[ScenarioResult, ...] = ()
    if metrics.payload is not None:
        scenarios = run_scenarios(
            image.pixels,
            metrics.payload,
            profile_scenarios(config.profile),
        )
        for result in scenarios:
            if result.status != "pass":
                findings.append(
                    Finding(
                        code=(
                            "ROBUSTNESS_PARTIAL"
                            if result.status == "partial"
                            else "ROBUSTNESS_FAILED"
                        ),
                        severity="warning",
                        message=(
                            f"Scenario {result.scenario.name} was "
                            f"{result.status} across the two decoders."
                        ),
                    )
                )

    report = AnalysisReport(
        schema_version="1.0",
        tool_version=__version__,
        input_name=image.display_name,
        input_format=image.format,
        width=image.width,
        height=image.height,
        profile=config.profile,
        payload=metrics.payload,
        baseline_decoders=baseline_decoders,
        metrics=metrics,
        scenarios=scenarios,
        findings=tuple(findings),
    )
    return report, image.pixels
