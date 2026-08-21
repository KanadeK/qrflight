import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def run(*args: str, python: Path | None = None) -> None:
    executable = str(python or Path(sys.executable))
    subprocess.run([executable, *args], cwd=ROOT, check=True)


def main() -> None:
    run("-m", "ruff", "format", "--check", "src", "tests", "scripts")
    run("-m", "ruff", "check", "src", "tests", "scripts")
    run("-m", "mypy", "src")
    run(
        "-m",
        "pytest",
        "--cov=qrflight",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
    )

    if DIST.exists():
        shutil.rmtree(DIST)
    run("-m", "build")
    artifacts = sorted(str(path) for path in DIST.iterdir())
    run("-m", "twine", "check", *artifacts)

    wheel = next(DIST.glob("*.whl"))
    with tempfile.TemporaryDirectory(prefix="qrflight-wheel-") as directory:
        environment = Path(directory)
        run("-m", "venv", str(environment))
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        run("-m", "pip", "install", "--disable-pip-version-check", str(wheel), python=python)
        run("-m", "qrflight", "version", python=python)


if __name__ == "__main__":
    main()
