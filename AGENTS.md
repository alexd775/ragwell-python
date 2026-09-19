# Ragwell Python SDK guidance

- This standalone repository currently contains only a packaging scaffold. Read
  `README.md`, `CONTRIBUTING.md`, and `pyproject.toml` before editing.
- Keep changes within the requested scope. Do not implement or stub clients,
  transport, generated models, or API methods as part of scaffold maintenance.
- Support Python 3.11+ syntax and the CPython 3.11–3.14 CI matrix. Keep public
  boundaries explicitly typed and retain `src/ragwell/py.typed` in distributions.
- Keep runtime dependencies minimal and development tools in the development
  dependency group. Update `uv.lock` with dependency changes; do not hand-edit it.
- Installation, imports, builds, and ordinary tests must be independent of backend
  imports, private repositories, credentials, provider calls, and model downloads.
- Future wire schemas come from a reviewed public API contract; do not invent a
  contract snapshot or select a generator during basic repository setup.
- Add deterministic tests for real behavior. Preserve the wheel/sdist and clean
  installed-package checks. Run the README checks and report unavailable checks
  accurately.
- Never inspect local `.env` values or include secrets, customer data, or private
  infrastructure details in source, artifacts, logs, or documentation.
- Keep documentation truthful about scaffold status. Preserve unrelated changes.
  Commit, push, publish, and repository-setting changes require an explicit request.
