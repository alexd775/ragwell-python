# Security policy

This SDK is an unpublished developer build. Package publication remains gated on
release checks and a verified private reporting channel. There is no supported
stable release or guaranteed response-time SLA yet. After the first beta release,
maintenance initially covers the current 0.x minor.

## Reporting a vulnerability

Do not put API keys, credentials, document/query contents, exploit details involving
other tenants, or raw HTTP dumps in public GitHub issues.

The intended channel is GitHub's private vulnerability reporting for this repository.
**Release prerequisite:** the repository's reporting setting was verified disabled
on 2026-09-21. The maintainer must enable it and verify the private “Report a
vulnerability” route before publishing the package. This document does not claim
that an unconfigured private channel is available. Until it is enabled, use a
public issue only to request a private contact, without sensitive details.

When a private route is available, include a minimal synthetic reproduction, affected
SDK/API contract versions, impact, and safe request IDs. Avoid sending active keys
or customer documents. Rotate a suspected exposed API key through normal account
administration; the SDK cannot rotate or revoke keys.

## Maintainer checks

Keep dependency, secret and distribution scans with each release's evidence. Review
runtime and development dependencies, preserve license notices, and scan source plus
wheel/sdist contents. A passing advisory scan is a point-in-time check, not a claim
that every defect or secret has been ruled out. Keep CI for forks credential-free.
SDK/API endpoint tests must use dedicated synthetic projects and scoped keys.

Use a reviewed immutable artifact, protected publisher and recorded provenance.
Do not publish when the required CI, package ownership or reporting-channel gates
are unresolved. See [release preparation](docs/releasing.md).
