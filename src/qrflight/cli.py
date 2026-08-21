from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from qrflight import __version__
from qrflight.engine import CheckConfig, check_image
from qrflight.io import InputError
from qrflight.report import render_html, render_json, render_text

app = typer.Typer(add_completion=False, no_args_is_help=True)


class Profile(StrEnum):
    quick = "quick"
    print = "print"


class OutputFormat(StrEnum):
    text = "text"
    json = "json"
    html = "html"


class FailOn(StrEnum):
    none = "none"
    warning = "warning"
    error = "error"


@app.command()
def check(
    image: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True),
    ],
    expect: Annotated[str | None, typer.Option(help="Required decoded payload.")] = None,
    profile: Annotated[Profile, typer.Option(help="Bounded degradation profile.")] = Profile.print,
    print_width_mm: Annotated[
        float | None,
        typer.Option(min=0.01, help="Full image width on paper in millimetres."),
    ] = None,
    printer_dpi: Annotated[
        int,
        typer.Option(min=1, help="Printer resolution used with --print-width-mm."),
    ] = 300,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Report format."),
    ] = OutputFormat.text,
    output: Annotated[Path | None, typer.Option(help="Write the report to this file.")] = None,
    fail_on: Annotated[
        FailOn,
        typer.Option(help="Lowest finding severity that exits 1."),
    ] = FailOn.error,
) -> None:
    """Check one QR image and report its print-readiness evidence."""
    try:
        report, pixels = check_image(
            image,
            CheckConfig(
                profile=profile.value,
                expected_payload=expect,
                print_width_mm=print_width_mm,
                printer_dpi=printer_dpi,
            ),
        )
    except InputError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(2) from error

    if output_format is OutputFormat.json:
        rendered = render_json(report)
    elif output_format is OutputFormat.html:
        rendered = render_html(report, pixels)
    else:
        rendered = render_text(report)

    if output is None:
        typer.echo(rendered, nl=False)
    else:
        if output.resolve() == image.resolve():
            typer.echo("Error: output must not overwrite the input image", err=True)
            raise typer.Exit(2)
        try:
            output.write_text(rendered, encoding="utf-8", newline="\n")
        except OSError as error:
            typer.echo(f"Error: cannot write output: {output.name}", err=True)
            raise typer.Exit(2) from error

    severity_rank = {"warning": 1, "error": 2}
    if fail_on is not FailOn.none:
        threshold = severity_rank[fail_on.value]
        if any(severity_rank[finding.severity] >= threshold for finding in report.findings):
            raise typer.Exit(1)


@app.command("profiles")
def list_profiles() -> None:
    """List the built-in bounded degradation profiles."""
    typer.echo("quick: one scenario per degradation family")
    typer.echo("print: mild and strong scenarios per degradation family")


@app.command()
def version() -> None:
    """Print the installed QRFlight version."""
    typer.echo(__version__)
