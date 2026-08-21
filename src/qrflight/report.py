import base64
import html
import json
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from qrflight.models import AnalysisReport, DecoderResult, Finding, ScenarioResult


def render_json(report: AnalysisReport) -> str:
    """Render the stable machine-readable report."""
    return json.dumps(_report_dict(report), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_text(report: AnalysisReport) -> str:
    """Render a concise terminal report."""
    baseline = ", ".join(
        (
            f"{result.engine}=pass"
            if result.payload == report.payload and report.payload
            else f"{result.engine}=miss"
        )
        for result in report.baseline_decoders
    )
    lines = [
        f"QRFlight {report.tool_version}",
        f"Input: {report.input_name} ({report.input_format}, {report.width}x{report.height})",
        f"Profile: {report.profile}",
        f"Payload: {report.payload if report.payload is not None else 'unreadable'}",
        f"Baseline: {baseline}",
    ]
    metrics = report.metrics
    if metrics.module_count is not None:
        lines.append(
            "Metrics: "
            f"modules={metrics.module_count}, module_pixels={metrics.module_pixels}, "
            f"quiet_zone={metrics.quiet_zone_modules}, contrast={metrics.contrast}, "
            f"printer_dots={metrics.printer_dots_per_module}"
        )
    lines.append("Scenarios:")
    if report.scenarios:
        lines.extend(
            f"  [{result.status.upper()}] {result.scenario.name} "
            f"({result.scenario.family}={result.scenario.value:g})"
            for result in report.scenarios
        )
    else:
        lines.append("  none (baseline payload unavailable)")
    lines.append("Findings:")
    if report.findings:
        lines.extend(
            f"  [{finding.severity.upper()}] {finding.code}: {finding.message}"
            for finding in report.findings
        )
    else:
        lines.append("  none")
    return "\n".join(lines) + "\n"


def render_html(report: AnalysisReport, pixels: NDArray[np.uint8]) -> str:
    """Render a self-contained offline evidence report."""
    preview = _preview_data_url(pixels)
    scenario_rows = "".join(
        "<tr>"
        f"<td>{html.escape(result.scenario.name)}</td>"
        f"<td>{html.escape(result.scenario.family)}</td>"
        f"<td>{result.scenario.value:g}</td>"
        f'<td class="status {result.status}">{result.status}</td>'
        "</tr>"
        for result in report.scenarios
    )
    finding_items = (
        "".join(
            f'<li class="{finding.severity}"><strong>{html.escape(finding.code)}</strong>: '
            f"{html.escape(finding.message)}</li>"
            for finding in report.findings
        )
        or "<li>None</li>"
    )
    payload = html.escape(report.payload) if report.payload is not None else "Unreadable"
    metrics = report.metrics
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>QRFlight report — {html.escape(report.input_name)}</title>
<style>
:root{{
  --ink:#172018;--muted:#657267;--paper:#f6f4eb;--card:#fff;
  --green:#1b6b3a;--amber:#a45b00;--red:#a22b2b
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:960px;margin:auto;padding:32px}}
header,.card{{
  background:var(--card);border:1px solid #d9ddd5;border-radius:14px;
  padding:24px;margin-bottom:18px
}}
h1,h2{{margin-top:0}}
.hero{{
  display:grid;grid-template-columns:minmax(180px,280px) 1fr;
  gap:28px;align-items:center
}}
img{{width:100%;image-rendering:pixelated;border:1px solid #d9ddd5}}
code{{overflow-wrap:anywhere}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:9px;text-align:left;border-bottom:1px solid #e4e6e1}}
.status{{font-weight:700}}.pass{{color:var(--green)}}.partial,.warning{{color:var(--amber)}}.fail,.error{{color:var(--red)}}
@media(max-width:640px){{.hero{{grid-template-columns:1fr}}main{{padding:16px}}}}
</style>
</head>
<body><main>
<header class="hero"><img src="{preview}" alt="Analyzed QR image"><div>
<p>QRFlight {html.escape(report.tool_version)} · schema {html.escape(report.schema_version)}</p>
<h1>{html.escape(report.input_name)}</h1>
<p>
{report.input_format} · {report.width}x{report.height}px ·
profile {html.escape(report.profile)}
</p>
<p><strong>Payload</strong><br><code>{payload}</code></p>
</div></header>
<section class="card"><h2>Measured signals</h2><dl>
<dt>Modules</dt><dd>{metrics.module_count}</dd>
<dt>Pixels per module</dt><dd>{metrics.module_pixels}</dd>
<dt>Quiet zone (modules)</dt><dd>{metrics.quiet_zone_modules}</dd>
<dt>Contrast (0-255)</dt><dd>{metrics.contrast}</dd>
<dt>Estimated printer dots per module</dt><dd>{metrics.printer_dots_per_module}</dd>
</dl></section>
<section class="card"><h2>Robustness scenarios</h2><table>
<thead><tr><th>Scenario</th><th>Family</th><th>Value</th><th>Result</th></tr></thead>
<tbody>{scenario_rows}</tbody></table></section>
<section class="card"><h2>Findings</h2><ul>{finding_items}</ul></section>
<footer>Engineering preflight only — not calibrated ISO/IEC 15415 verification.</footer>
</main></body></html>
"""


def _decoder_dict(result: DecoderResult) -> dict[str, Any]:
    return {"engine": result.engine, "payload": result.payload}


def _finding_dict(finding: Finding) -> dict[str, Any]:
    return {
        "code": finding.code,
        "severity": finding.severity,
        "message": finding.message,
        "measured": finding.measured,
        "required": finding.required,
    }


def _scenario_dict(result: ScenarioResult) -> dict[str, Any]:
    return {
        "name": result.scenario.name,
        "family": result.scenario.family,
        "value": result.scenario.value,
        "status": result.status,
        "decoders": [_decoder_dict(decoder) for decoder in result.decoders],
    }


def _report_dict(report: AnalysisReport) -> dict[str, Any]:
    metrics = report.metrics
    return {
        "schema_version": report.schema_version,
        "tool_version": report.tool_version,
        "input": {
            "name": report.input_name,
            "format": report.input_format,
            "width": report.width,
            "height": report.height,
        },
        "profile": report.profile,
        "payload": report.payload,
        "baseline_decoders": [_decoder_dict(result) for result in report.baseline_decoders],
        "metrics": {
            "module_count": metrics.module_count,
            "module_pixels": metrics.module_pixels,
            "quiet_zone_modules": metrics.quiet_zone_modules,
            "contrast": metrics.contrast,
            "printer_dots_per_module": metrics.printer_dots_per_module,
        },
        "scenarios": [_scenario_dict(result) for result in report.scenarios],
        "findings": [_finding_dict(finding) for finding in report.findings],
    }


def _preview_data_url(pixels: NDArray[np.uint8]) -> str:
    height, width = pixels.shape
    scale = min(1.0, 320 / max(width, height))
    preview = cv2.resize(
        pixels,
        (round(width * scale), round(height * scale)),
        interpolation=cv2.INTER_NEAREST,
    )
    encoded = cv2.imencode(".png", preview)[1]
    return "data:image/png;base64," + base64.b64encode(encoded.tobytes()).decode("ascii")
