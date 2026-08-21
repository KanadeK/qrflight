# Contributing

1. Open an issue describing the user-visible problem and a minimal input when licensing/privacy
   permits sharing it.
2. Install with `uv sync --locked --extra dev`.
3. Add a failing behavioral test before changing loader, decoder, metric, degradation or exit-code
   behavior.
4. Keep the change scoped. Do not add network access, new symbologies or certification language.
5. Run `uv run python scripts/verify.py` before opening a pull request.

Commits use `feat:`, `fix:`, `test:`, `docs:` or `chore:` prefixes. By contributing, you agree that
your contribution is licensed under the MIT License.
