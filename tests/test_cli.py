import json
from pathlib import Path

import cv2
from typer.testing import CliRunner

from qrflight.cli import app
from qrflight.engine import CheckConfig, check_image

runner = CliRunner()


def test_check_healthy_qr_outputs_json_and_exits_zero(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png

    result = runner.invoke(app, ["check", str(path), "--profile", "quick", "--format", "json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout)["payload"] == payload


def test_expected_payload_mismatch_exits_one(qr_png: tuple[Path, str]) -> None:
    path, _ = qr_png

    result = runner.invoke(app, ["check", str(path), "--expect", "wrong"])

    assert result.exit_code == 1
    assert "EXPECTED_PAYLOAD_MISMATCH" in result.stdout


def test_warning_threshold_rejects_cropped_quiet_zone(
    qr_png: tuple[Path, str], tmp_path: Path
) -> None:
    path, _ = qr_png
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    cropped_path = tmp_path / "cropped.png"
    assert cv2.imwrite(str(cropped_path), pixels[32:-32, 32:-32])

    result = runner.invoke(app, ["check", str(cropped_path), "--fail-on", "warning"])

    assert result.exit_code == 1
    assert "QUIET_ZONE_TOO_SMALL" in result.stdout


def test_invalid_input_exits_two(tmp_path: Path) -> None:
    path = tmp_path / "broken.png"
    path.write_text("broken", encoding="utf-8")

    result = runner.invoke(app, ["check", str(path)])

    assert result.exit_code == 2
    assert "not a supported image" in result.stderr


def test_html_output_is_written_to_requested_file(qr_png: tuple[Path, str], tmp_path: Path) -> None:
    path, _ = qr_png
    output = tmp_path / "report.html"

    result = runner.invoke(
        app,
        ["check", str(path), "--profile", "quick", "--format", "html", "--output", str(output)],
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    assert output.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_output_cannot_overwrite_input(qr_png: tuple[Path, str]) -> None:
    path, payload = qr_png

    result = runner.invoke(app, ["check", str(path), "--output", str(path)])

    assert result.exit_code == 2
    assert "must not overwrite" in result.stderr
    assert check_image(path, CheckConfig(profile="quick"))[0].payload == payload
