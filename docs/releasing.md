# Release preparation

Maintainers executing a release should follow the concise
[release runbook](release-runbook.md). This document records policy, controls and
qualification evidence behind that procedure.

The first developer beta is `ragwell==0.1.0`, published from the immutable
`v0.1.0` tag. A source version alone does not imply package publication or a tag.
The SDK repository owns its release. API deployment and API CI do not build or
publish SDK packages.

The current developer beta is `ragwell==0.2.0`, published from immutable tag
`v0.2.0`. It adds the `2026-09-22.1` machine contract and optional Jev reranking.
The [public-wheel beta report](qualification/2026-09-22-pypi-0.2.0-beta-lifecycle.json)
records the deployed lifecycle, the
[live Jev report](qualification/2026-09-22-0.2.0-live-jev.json) records the paid
provider path, and the
[publication record](qualification/2026-09-22-0.2.0-release-publication.json)
identifies the immutable TestPyPI/PyPI artifacts. Representative quality, latency
and cost evaluation remains a separate product-rollout gate.

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

All eight hosted jobs passed for revision `0240fec` on 2026-09-22: Linux CPython
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

Neither index contained a `ragwell` project at the preparation checkpoint on
2026-09-22. Alex confirmed the exact pending publishers on both accounts. The
tagged `v0.1.0` workflow then created both projects through OIDC and published the
same immutable distributions to each index.

GitHub private vulnerability reporting is enabled. The `testpypi` environment allows
only `v*` tags. The `pypi` environment allows only `v*` tags, requires `alexd775`
approval, permits self-review for the sole maintainer and disallows administrator
bypass. Neither environment contains secrets or variables.

## 0.1.0 publication record

Tag `v0.1.0` identifies commit `bb3204b9e4c16e88f7c7cd19318ab290d7214ab9`
on `main`. The protected [release workflow](https://github.com/alexd775/ragwell-python/actions/runs/35712234816)
passed its build, TestPyPI publication, staged-wheel comparison, clean install and
approved PyPI publication jobs on 2026-09-22.

The TestPyPI wheel then passed the opt-in sync/async beta lifecycle against the
deployed API, including retrieval provenance, verified export and deletion of both
synthetic documents. The public PyPI wheel and source archive were downloaded and
matched the workflow artifacts exactly. A fresh CPython 3.11 environment installed
`ragwell==0.1.0` from the normal PyPI index and imported both public clients.

- [GitHub release](https://github.com/alexd775/ragwell-python/releases/tag/v0.1.0)
- [PyPI package](https://pypi.org/project/ragwell/0.1.0/)
- [TestPyPI package](https://test.pypi.org/project/ragwell/0.1.0/)
- [Exact staged beta report](qualification/2026-09-22-testpypi-beta-lifecycle.json)
- [Publication evidence](qualification/2026-09-22-release-publication.json)

## 0.2.0 publication record

Tag `v0.2.0` identifies commit `273f67219d4688936d4db5fb872d3cfcae5c852b`
on `main`. Its six-job Linux/macOS matrix passed in
[CI run 35770522513](https://github.com/alexd775/ragwell-python/actions/runs/35770522513).
The protected
[release run 35771331505](https://github.com/alexd775/ragwell-python/actions/runs/35771331505)
built the distributions once and published them through OIDC to TestPyPI and PyPI.

The first TestPyPI verification attempt exceeded the original two-minute indexing
window after a successful upload. Once TestPyPI exposed the version, rerunning only
the failed jobs hash-compared and clean-installed the staged wheel, then the approved
production job published the same files. Direct metadata from both indexes reports:

- wheel `ragwell-0.2.0-py3-none-any.whl` SHA-256
  `6e04481e9cbd31da0c475e10988128a3ba093c8cda7463ecb89432b0a64a8fcb`;
- source archive `ragwell-0.2.0.tar.gz` SHA-256
  `60b8e54273605c5eb6af2c4b43c3e88b1f0d12e17adfaa943eca3d0a82160e19`.

A fresh CPython 3.11.16 environment installed `ragwell==0.2.0` from production
PyPI, confirmed both version identities and imported `RerankRequest`. The downloaded
public wheel then passed the bounded sync/async beta lifecycle and deleted both
synthetic documents. See the
[public lifecycle report](qualification/2026-09-22-pypi-0.2.0-beta-lifecycle.json)
and [publication evidence](qualification/2026-09-22-0.2.0-release-publication.json).

## Release sequence

1. Refresh the final checks and evidence, commit the selected stable version and
   changelog, obtain a green CI matrix, and create the matching `vX.Y.Z` tag only
   after reviewing the immutable commit.
2. Let the tag workflow publish and verify TestPyPI. Run the beta lifecycle against
   the exact staged wheel, review its hashes, then approve the protected `pypi`
   deployment. Do not rebuild between indexes.
3. Record immutable artifacts, provenance, changelog and compatibility information.
   Verify the final package installs from the intended index. Yank/supersede a faulty
   release; never overwrite uploaded files.
4. If an example is held on the previous public SDK during release preparation,
   update its PyPI pin and lockfile only after the new version is published. Keep
   that consumer test free of repository paths and editable source overrides.

This sequence keeps source preparation separate from the release tag and package
uploads. Preparing a candidate by itself creates none of them.

References: [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[Twine metadata checks](https://twine.readthedocs.io/en/stable/),
[Gitleaks](https://github.com/gitleaks/gitleaks),
[pip-audit](https://github.com/pypa/pip-audit).
