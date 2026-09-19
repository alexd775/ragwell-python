# Contributing

This repository contains the development Ragwell Python SDK. Discuss new public SDK
capabilities in an issue before implementing them, and keep each pull request focused. Include a short
description of the change and the checks actually run. Use synthetic examples;
never include credentials or customer documents in code, logs, issues, or tests.

## Development workflow

Follow the setup and checks in [README.md](README.md). Maintained code lives in
`src/ragwell`; generated internals live in `src/ragwell/_generated`; contract,
behavior, and packaging tests live in `tests`. Ruff handles formatting and linting,
mypy checks types in strict mode against Python 3.11, and pytest runs the tests.
Every contract update must retain the complete sync/async operation map and add
deterministic wire/failure tests. Avoid placeholder tests.

The reviewed contract is vendored under `contracts/`. Regenerate only through:

```sh
uv run --locked python scripts/generate.py
uv run --locked python scripts/generate.py --check
```

Never edit generated output by hand. Review the source artifact digest, manifest,
generator warnings, public mapping, and wire behavior together. The SDK must remain
buildable without the backend checkout.

Run `uv run --locked ruff format .` to format changes. Check the complete
CPython 3.11–3.14 matrix in CI before merging. Ordinary tests must run without API
access, credentials, model downloads, or private repositories.

Development tools belong in `[dependency-groups].dev`, separate from runtime
dependencies. Review and commit `pyproject.toml` and `uv.lock` together when changing
dependencies. To update one tool within its declared range:

```sh
uv lock --upgrade-package ruff
uv sync --locked
```

Run all checks after an update. Keep the uv version in `pyproject.toml`, CI, and the
README aligned. The development lock does not constrain downstream consumers.
Runtime dependency ranges belong in `[project].dependencies`; generation tools
remain development-only.
The build backend is also a development dependency so `python -m build
--no-isolation` uses the locked build tools. Its default build makes the wheel from
the source distribution, checking that the source archive is self-contained.

Tool configuration follows the official [uv project guide](https://docs.astral.sh/uv/guides/projects/),
[Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html), and
[pytest integration guidance](https://docs.pytest.org/en/stable/explanation/goodpractices.html).

## Attribution and future releases

The MIT notice uses `alexd775`, the verified repository owner's GitHub handle.
A legal person or entity name has not been supplied; confirm any replacement
attribution with the owner rather than guessing it. PyPI name availability and
publisher ownership remain unverified. Publication and release automation require
separate maintainer authorization after SDK implementation and qualification.
