# SDK development

The repository's [contribution guide](../../CONTRIBUTING.md) is the complete development policy. Maintained public behavior lives in `src/ragwell`; generated internals live in `src/ragwell/_generated` and are never edited by hand. The [README](../../README.md) lists format, lint, type, generation, test, and build commands.

Use Python 3.11+ syntax and synthetic tests. Ordinary tests run without an API endpoint, credentials, private checkout, provider calls, or model downloads. The standalone [async example project](../../examples/async_project/README.md) installs from PyPI rather than from the repository root.

Documentation lives in this repository. Link guides from [the docs index](../index.md), keep examples aligned with the public package, and run `python3 scripts/check_docs.py` to check local links, code fences, and Python snippet syntax. The docs workflow runs this check when documentation changes. Existing publication and qualification records stay under `docs/qualification/`.

For contract refreshes, read [contract generation](contract-generation.md). For publication, read [releases](releases.md).
