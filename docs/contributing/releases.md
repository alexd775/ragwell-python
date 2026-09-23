# Releases

The [release runbook](../release-runbook.md) is the step-by-step maintainer procedure for a version and tag. [Release preparation](../releasing.md) records artifact, security, TestPyPI, PyPI, and qualification gates. The public [changelog](../../CHANGELOG.md) describes user-facing changes.

Releases use the protected GitHub Actions Trusted Publishing workflow. A tag must match the package version and identify a commit on `main`. The release workflow performs the full test and build gates independently of documentation-only CI routing. Published package files are immutable; a bad version is superseded or yanked, never replaced.

Keep `docs/qualification/` for dated, sanitized evidence. Do not put credentials, customer documents, or private endpoint secrets in reports.
