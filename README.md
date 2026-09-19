# Ragwell Python SDK

The future Python SDK for Ragwell, a managed service for document ingestion and
retrieval with source citations.

**Status: initial repository scaffold.** The package currently contains no usable
clients or API operations. `0.1.0.dev0` is a development version, not a published
SDK release. The intended distribution and import name is `ragwell`; PyPI name
availability and ownership have not been verified.

## Local development

Use CPython 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/)
**0.12.17**, matching CI. From the repository root:

```sh
uv sync --locked --python 3.11
```

This creates `.venv`, installs the package in editable mode, and installs the
development tools from `uv.lock`. The package has no runtime dependencies.
No API credentials or other repository checkouts are needed. Initial setup needs
internet access to download tools and, if necessary, Python.

## Checks and build

```sh
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked pytest
uv run --locked python -m build --no-isolation
```

The tests build a source distribution and a wheel from that source distribution,
check their contents, then install the wheel into a fresh virtual environment.
An isolated Python process checks the installed import and `py.typed` marker
without access to the editable checkout. These are packaging checks; SDK behavior
tests will accompany implementation. Tests make no network or service calls.

Build artifacts go to `dist/`. Builds use the locked development environment,
including Hatchling. GitHub Actions runs the checks on CPython 3.11–3.14 on Linux;
there is no publishing workflow.

See [CONTRIBUTING.md](CONTRIBUTING.md) for dependency updates and contribution
guidance. Client implementation, contract-generation qualification, API workflow
prerequisites, and release qualification are future work.

## License

[MIT](LICENSE). Attribution currently uses repository owner `alexd775`'s GitHub
handle; see the attribution note in [CONTRIBUTING.md](CONTRIBUTING.md).
