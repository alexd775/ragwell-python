# Local SDK qualification — 2026-09-19

The following checks passed locally on macOS with CPython 3.11.16 and uv 0.12.17:

```text
uv sync --locked --python 3.11
uv run --locked ruff format --check .        # 150 files formatted
uv run --locked ruff check .                 # passed
uv run --locked mypy                         # 138 source files passed
uv run --locked python scripts/generate.py --check
uv run --locked pytest                       # 29 passed
uv run --locked python -m build --no-isolation
```

The build produced `ragwell-0.1.0.dev0.tar.gz` and the universal
`ragwell-0.1.0.dev0-py3-none-any.whl`. Pytest built a wheel from the fresh source
distribution, installed the wheel and its three runtime dependencies offline into
an isolated virtual environment, and imported/constructed the installed client
without the editable checkout.

A separate temporary CPython 3.11 environment installed the declared floors
`attrs==22.2.0`, `httpx==0.27.2`, and `python-dateutil==2.8.2`, then installed the
wheel with `--no-deps`; the isolated import/client-construction smoke check passed.
The locked development environment exercises current compatible dependency versions.

The deterministic suite executes all 26 reviewed operations through both public
client styles, plus retry identity, no search replay, typed errors/correlation/quota,
opaque/repeated cursors, timeout/resume, async cancellation, all upload media types,
caller stream ownership, mutation/checksum rejection, and verified atomic export
downloads. Synthetic sync/async examples execute against HTTPX mock transports.

GitHub Actions now defines Linux CPython 3.11–3.14 checks and macOS/Windows smoke
jobs at Python 3.11 and 3.14. Those hosted jobs were configured but not run locally,
so this document does not claim their results.

No isolated matching real-service endpoint or scoped fixtures were supplied. The
installed-wheel runner is prepared in `qualification/http_runner.py`, but live HTTP
qualification remains open and mocks are not counted as server evidence. Public
artifact hosting, TestPyPI/PyPI, provenance publication, and service deployment also
remain separate release prerequisites.
