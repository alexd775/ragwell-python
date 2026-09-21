# Release preparation

The next intended release is `ragwell==0.1.0`, a developer beta. The current source
remains `0.1.0.dev0`; no package publication or tag is implied by this document.
The SDK repository owns its release. API deployment and API CI do not build or
publish SDK packages.

## Local preparation

Run the README checks from the locked SDK environment: Ruff formatting/lint,
strict mypy, deterministic contract generation and pytest. Tests execute examples,
the sync/async operation mapping, failure behavior, wheel-from-sdist packaging and
clean installation. Preserve the earlier minimum-runtime-dependency evidence and
repeat it when runtime/dependency changes or a final release candidate warrant it.

Build a candidate once in a new output directory. Record wheel/sdist SHA-256,
source revision and reviewed machine-contract identity. Check metadata with pinned
Twine (`twine check --strict`), scan the repository and unpacked distributions for
secrets, audit every pinned runtime/development dependency, and inventory runtime
licenses. Keep machine-readable reports under `docs/qualification/` or with the
immutable release artifacts. Refresh advisory data for the final release.

Run [beta validation](beta-validation.md) from the actual installed candidate wheel
using dedicated test credentials. Retain the separate [full HTTP qualification](http-qualification.md)
evidence for the controlled failure/tenant matrix. Neither ordinary unit tests nor
a narrow beta check can claim the other matrix's coverage. If source, metadata or
version changes produce a new wheel, assign a new digest and do not relabel an older
report as a test of those bytes. Unchanged runtime bytes may be compared explicitly,
but final-release artifact qualification still remains a gate.

## Remaining external gates

1. Push the intended source only when Alex resumes that step, then verify its exact
   hosted CI revision: Linux CPython 3.11–3.14 plus macOS/Windows at the supported
   endpoints. A previous commit's matrix does not cover later local changes.
2. Enable and verify GitHub private vulnerability reporting, as recorded in
   [SECURITY.md](../SECURITY.md). This is a repository-setting change requiring the
   maintainer's authorization.
3. Verify the `ragwell` distribution name and actual owner access separately on
   PyPI and TestPyPI. Name availability alone does not establish ownership.
4. Prepare a protected GitHub release environment and PyPI/TestPyPI Trusted
   Publishers restricted to the exact repository, workflow and environment. Pin
   release actions, use OIDC instead of a stored upload token, and require a
   maintainer-selected version/tag. Review this setup before changing settings.
5. After explicit authorization, rehearse publishing to TestPyPI and install the
   staged artifact in a clean environment. Record index, version, artifact digest,
   install result and lifecycle evidence; do not rebuild different bytes for PyPI.
6. Publish only after all required checks and maintainer approval. Record immutable
   artifacts, provenance, changelog and compatibility information. Verify the final
   package installs from the intended index. Yank/supersede a faulty release; never
   overwrite uploaded files.

The hosted matrix, repository settings, publisher ownership/configuration and
publication are outstanding. No GitHub release workflow or publisher setting was
created as part of the local checks.

References: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[Twine metadata checks](https://twine.readthedocs.io/en/stable/),
[Gitleaks](https://github.com/gitleaks/gitleaks),
[pip-audit](https://github.com/pypa/pip-audit).
