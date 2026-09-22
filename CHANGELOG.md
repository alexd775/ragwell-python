# Changelog

## Unreleased

- Update the asynchronous project example to install published `ragwell==0.2.0`
  from PyPI and demonstrate explicit optional reranking.

## 0.2.0 — 2026-09-22

- Optional typed Jev reranking on synchronous and asynchronous search, with
  separate relevance/confidence/hybrid scores and contract `2026-09-22.1`.
- Reranking metadata includes the configured provider and resolved Jev model for
  TypeSafe, OpenRouter and Vercel AI Gateway routing.
- Requires project-owned Jev credentials configured in the dashboard. Ordinary
  retrieval stays unchanged; paid search requests are never automatically retried.
- Rejects malformed reranking metadata as a safe protocol error and exercises
  reranked scores, citations and installed-wheel imports in deterministic tests.
- Adds the Python 3.12 asynchronous project example for folder sync, retrieval and
  project document cleanup; the example intentionally uses ordinary retrieval.

## 0.1.0 — 2026-09-22

First developer beta. The release uses existing-project handles and scoped machine
credentials; project and key administration remain outside the SDK.

- Complete typed sync/async coverage of the 26 reviewed machine operations, with
  existing-project handles and scoped bearer credentials.
- Upload, resumed waiting, lazy pagination and verified export downloads, with
  bounded deadlines/retries and stable idempotency identity.
- Reliability corrections for end-to-end budgets, streamed response/download caps,
  accepted-intake recovery identifiers and redacted protocol/transport failures.
- Reviewed contract packaged in the wheel, installed-package identity verification,
  complete local HTTP fixture qualification, and endpoint-only test ownership.
- Normalize installed-package inventory paths across Windows and POSIX during
  wheel verification, retaining modified-file and unexpected-file checks.
- Opt-in beta lifecycle validation against an independently prepared account/project,
  with private credentials, bounded synthetic usage and checkpointed cleanup reports.
- API reference, lifecycle examples, compatibility/security guidance and local release
  evidence. The Linux, macOS and Windows hosted matrix passes, private vulnerability
  reporting is enabled, and publication uses protected OIDC publishers.

Project creation/administration, key management, browser identity, billing and answer
generation are outside this SDK's current scope.
