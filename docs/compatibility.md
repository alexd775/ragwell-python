# Compatibility and support

The SDK is currently an unpublished development build (`0.1.0.dev0`). The intended
first package release is `0.1.0`, a developer beta. Do not treat a planned release
or configured CI job as a published or qualified artifact.

## Public interface

Supported entry points are `Ragwell`, `AsyncRagwell`, their documented resources and
helpers, `ragwell.types`, and public exceptions. Names under `_generated` and other
underscore-prefixed modules are internal. Examples target the maintained interface.
Generated response models retain additive fields where supported; unknown enums
or incompatible shapes raise protocol errors. Omitted values (`UNSET`) and explicit
nulls (`None`) are distinct. Request-model fields must match the documented API.

SDK and API versions are independent. Compatibility evidence identifies a reviewed
machine-contract digest, exact SDK wheel and tested endpoint. The client does not
silently change environments or fetch new schemas at runtime. Contract refreshes
are reviewed changes to the SDK's vendored artifact and generated internals.

## Versions and changes

After the first release, compatible corrections are patch releases. A breaking
public change before 1.0 requires a new minor version and migration notes describing
the affected calls and replacements. Prefer a documented deprecation period when
practical; do not silently repurpose existing arguments or return values. Critical
security fixes may require an immediate documented correction.

Initially maintain only the current 0.x minor. No long-term maintenance or response
SLA is promised for older minors. A 1.0 stability commitment requires explicit
maintainer acceptance after real sync and async integrations provide feedback.
A bad release is superseded or yanked; existing published files are never replaced.

## Platforms and qualification

The syntax/runtime floor is Python 3.11. The configured release matrix targets
CPython 3.11–3.14 on Linux and the oldest/newest versions on macOS and Windows.
The latest local 3.11/3.14 results do not substitute for the deferred hosted matrix.
PyPy, Trio, free-threaded Python and later Python versions are not qualified.
Async clients use asyncio and must remain in their owning event loop.

Runtime ranges live in `pyproject.toml`; `uv.lock` fixes the maintainer environment
rather than constraining downstream applications. Release evidence must include
minimum-supported and current-compatible dependency checks. A new public/API
contract or transport dependency version requires appropriate requalification.

## Reporting problems

For ordinary SDK issues, use [GitHub issues](https://github.com/alexd775/ragwell-python/issues)
with a minimal synthetic reproduction, SDK/Python versions, the relevant contract
or release identity, and safe error class/code/request ID. Remove keys, account
credentials, source documents, query text and raw HTTP bodies. Do not file sensitive
security reports publicly; follow [SECURITY.md](../SECURITY.md).

The SDK excludes project provisioning, key administration, browser login, billing,
answer generation, framework adapters and folder synchronization. API quotas,
provider behavior, parser limits and lifecycle authorization remain server-owned.
