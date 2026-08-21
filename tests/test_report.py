import json
from dataclasses import replace
from pathlib import Path

import cv2

from qrflight.engine import CheckConfig, check_image
from qrflight.report import render_html, render_json, render_text


def test_json_and_text_expose_the_same_evidence(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png
    report, pixels = check_image(path, CheckConfig(profile="quick"))

    json_output = render_json(report)
    parsed = json.loads(json_output)
    text_output = render_text(report)

    assert parsed["schema_version"] == "1.0"
    assert parsed["input"]["name"] == "healthy.png"
    assert parsed["payload"] == payload
    assert len(parsed["scenarios"]) == 4
    assert payload in text_output
    assert "healthy.png" in text_output
    assert render_json(report) == json_output
    assert render_html(report, pixels) == render_html(report, pixels)


def test_html_escapes_payload_and_embeds_no_script(tmp_path: Path) -> None:
    payload = "<script>alert('qr')</script>"
    modules = cv2.QRCodeEncoder_create().encode(payload)
    bordered = cv2.copyMakeBorder(modules, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=255)
    pixels = cv2.resize(bordered, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
    path = tmp_path / "hostile.png"
    assert cv2.imwrite(str(path), pixels)
    report, loaded_pixels = check_image(path, CheckConfig(profile="quick"))

    html_output = render_html(report, loaded_pixels)

    assert payload not in html_output
    assert "&lt;script&gt;alert(&#x27;qr&#x27;)&lt;/script&gt;" in html_output
    assert "<script" not in html_output.lower()
    assert "data:image/png;base64," in html_output


def test_expected_payload_mismatch_is_an_error(qr_png: tuple[Path, str]) -> None:
    path, _ = qr_png

    report, _ = check_image(
        path,
        CheckConfig(profile="quick", expected_payload="https://wrong.example"),
    )

    mismatch = [
        finding for finding in report.findings if finding.code == "EXPECTED_PAYLOAD_MISMATCH"
    ]
    assert len(mismatch) == 1
    assert mismatch[0].severity == "error"


def test_text_report_escapes_terminal_control_characters(qr_png: tuple[Path, str]) -> None:
    path, _ = qr_png
    report, _ = check_image(path, CheckConfig(profile="quick"))
    hostile = replace(report, input_name="bad\x1b[31m.png", payload="go\x1b[2J")

    text_output = render_text(hostile)

    assert "\x1b" not in text_output
    assert "\\u001b" in text_output
