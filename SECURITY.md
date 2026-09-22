# Security policy

This policy covers the `0.1.0` developer beta and its release candidate. There is no
guaranteed response-time SLA. Maintenance initially covers the current 0.x minor.

## Reporting a vulnerability

Do not put API keys, credentials, document/query contents, exploit details involving
other tenants, or raw HTTP dumps in public GitHub issues.

Use GitHub's private “Report a vulnerability” route for this repository. Private
vulnerability reporting was verified enabled on 2026-09-22. Use public issues only
for non-sensitive defects and questions.

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
