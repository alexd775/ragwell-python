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

## Hosted source gate

All eight hosted jobs passed for revision `909b6eb` on 2026-09-21: Linux CPython
3.11–3.14 and macOS/Windows CPython 3.11 and 3.14. This closes the previously
deferred hosted gate for that revision. Any later release-source change needs its
own green matrix.

## Trusted publication workflow

The repository workflow `.github/workflows/release.yml` builds once in an
unprivileged job, verifies the package, and preserves the resulting wheel and source
archive as one GitHub artifact. A `vX.Y.Z` tag must exactly match the stable project
version and identify a commit on `main`. Separate OIDC-only jobs publish those same
bytes to TestPyPI, download and hash-compare the staged wheel, install it in a clean
environment, and only then wait on the protected `pypi` environment before
publishing the same files to PyPI.

The workflow pins every external action by commit. It has read-only repository
access; only the two publication jobs receive `id-token: write`. It contains no index
passwords or repository secrets. A manual workflow run builds and verifies but does
not publish because it is not a tag.

Configure pending Trusted Publishers on both indexes with these exact identities:

| Setting | TestPyPI | PyPI |
|---|---|---|
| Project | `ragwell` | `ragwell` |
| GitHub owner | `alexd775` | `alexd775` |
| Repository | `ragwell-python` | `ragwell-python` |
| Workflow | `release.yml` | `release.yml` |
| Environment | `testpypi` | `pypi` |

Neither index contained a `ragwell` project when checked on 2026-09-22. A pending
publisher does not reserve the name; the first successful upload creates the project.
Do not create the release tag until both publishers and environments are verified.

## Remaining external gates

1. Enable and verify GitHub private vulnerability reporting, as recorded in
   [SECURITY.md](../SECURITY.md). This is a repository-setting change requiring the
   maintainer's authorization.
2. Create the `testpypi` and `pypi` GitHub environments. Require manual approval for
   `pypi`; restrict both to protected release tags before any tag is created.
3. Sign in separately to PyPI and TestPyPI, verify both accounts, and register the
   exact pending Trusted Publisher identities above. Name availability does not
   establish ownership or reserve the name.
4. Select `0.1.0`, refresh the final checks and evidence, commit the version and
   changelog, obtain a green CI matrix, and create the matching `v0.1.0` tag only
   after reviewing the immutable commit.
5. Let the tag workflow publish and verify TestPyPI. Review its recorded hashes,
   then approve the protected `pypi` deployment. Do not rebuild between indexes.
6. Record immutable artifacts, provenance, changelog and compatibility information.
   Verify the final package installs from the intended index. Yank/supersede a faulty
   release; never overwrite uploaded files.

Repository settings, publisher ownership/configuration and publication remain
outstanding. Preparing the workflow does not create an environment, publisher,
release tag, GitHub release or package upload.

References: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[Twine metadata checks](https://twine.readthedocs.io/en/stable/),
[Gitleaks](https://github.com/gitleaks/gitleaks),
[pip-audit](https://github.com/pypa/pip-audit).
