# Ragwell Python SDK guidance

- This standalone repository contains the development Ragwell Python SDK. Read
  `README.md`, `CONTRIBUTING.md`, and `pyproject.toml` before editing.
- Keep changes within the requested scope. Public behavior is maintained in the
  handwritten clients/resources; never edit `src/ragwell/_generated` by hand.
- Support Python 3.11+ syntax and the CPython 3.11–3.14 CI matrix. Keep public
  boundaries explicitly typed and retain `src/ragwell/py.typed` in distributions.
- Keep runtime dependencies minimal and development tools in the development
  dependency group. Update `uv.lock` with dependency changes; do not hand-edit it.
- Installation, imports, builds, and ordinary tests must be independent of backend
  imports, private repositories, credentials, provider calls, and model downloads.
- Wire schemas come from the reviewed vendored artifact under `contracts/`.
  Regenerate through `scripts/generate.py` and preserve the recorded digest and
  complete 26-operation sync/async mapping.
- Add deterministic tests for real behavior. Preserve the wheel/sdist and clean
  installed-package checks. Run the README checks and report unavailable checks
  accurately.
- Never inspect local `.env` values or include secrets, customer data, or private
  infrastructure details in source, artifacts, logs, or documentation.
- Keep documentation truthful about development, qualification, and publication
  status. Preserve unrelated changes.
  Commit, push, publish, and repository-setting changes require an explicit request.
