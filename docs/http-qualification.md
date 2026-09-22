# Installed-wheel HTTP qualification

The complete synchronous and asynchronous matrix passed against an isolated,
migrated local API on 2026-09-21. This is deterministic HTTP integration evidence.
Hosted CI, exact-artifact beta validation and protected publication also passed for
the public `ragwell==0.1.0` release; each remains separate evidence.

Qualification is **endpoint-only**. The SDK repository owns the HTTP assertions,
wheel verification and reports. It does not start the API, access its database,
apply migrations, provision accounts/projects/keys, or require an API checkout or
Poetry environment. The API repository owns its server behavior and contract; it
contains no SDK qualification launcher or SDK-specific fixture tests.

`qualification/http_runner.py` uses only public HTTP operations and a prepared
fixture manifest. Ordinary SDK tests remain offline and backend independent.
The HTTP runner performs document mutations against the supplied test endpoint,
so use a dedicated synthetic environment prepared by its owner.

## Run against a prepared endpoint

Build the distribution with `uv run --locked python -m build --no-isolation`.
Install that wheel, with its runtime dependencies, into a fresh environment. Run
with that environment's interpreter, not an editable SDK installation:

```sh
RAGWELL_QUALIFICATION_CREDENTIALS_FILE=/private/fixture/credentials.json \
  /path/to/venv/bin/python qualification/http_runner.py \
  --manifest /private/fixture/manifest.json \
  --wheel /absolute/path/ragwell-0.2.0-py3-none-any.whl \
  --output /absolute/path/qualification-result.json
```

The manifest supplies the existing `base_url`. Credentials belong in a private file
(0600 on POSIX), never command-line arguments. Use a new report filename for each run.
The SDK's local development toolchain uses uv; an installed-wheel HTTP run itself
only needs Python, the installed package and fixture files. No Docker, Poetry,
backend imports or database tooling are required by this command.

The environment owner supplies the running API, workers and fixtures independently.
The SDK does not dictate how they are deployed or provisioned. The
[fixture requirements](qualification-fixtures.md) describe the data and lifecycle
conditions the HTTP assertions need, without embedding a service launcher.

## Required evidence

The runner fails closed unless the supplied wheel is the installed distribution,
all package files match the archive, and the live machine projection matches the
packaged contract. It records the wheel digest, contract digest, Python/runtime
versions, fixture identity, operation coverage and sanitized resource/cleanup IDs.

Each client style must pass:

- All 26 operations successfully; all 25 authenticated operations denied under a
  foreign project and under missing scopes; foreign nested resource substitutions
  and revoked-key rejection.
- PDF, text and Markdown ingestion, upload-state recovery, meaningful retrieval,
  exact source spans, identities, scores and profile/representation versions.
- Metadata revision conflict and receipt replay after a later revision; document,
  job and retrieval filters; document/job/chunk pagination and forbidden tenant
  selectors sent directly over HTTP (the SDK types do not expose those selectors).
- Multi-part text exports both with and without embeddings, explicit generation,
  every part's byte size/hash, manifest count and chunk count.
- Timeout followed by state recovery, failed-job retry, queued cancellation,
  expired-export denial, failed-deletion retry, completed deletion and absence from
  subsequent retrieval.
- A transport that forwards to real TCP and discards one already accepted response
  for each of nine mutation kinds. Replays must preserve server resource/command
  identity; job and deletion retry counters advance once.

Documents created by the runner are deleted in `finally` on partial failure. If
finalization failed ambiguously, upload-state reads recover a document for cleanup.
Unfinalized uploads are reported for normal API expiry or environment-owner cleanup.
Pre-provisioned resources, accounts, keys and service infrastructure remain the
responsibility of the environment owner. The SDK report does not claim to dispose
of that infrastructure.

## Optional validation against real beta

A narrower opt-in validation can use the deployed beta API with one dedicated
ordinary test account, a pre-created project and a key scoped to the lifecycle
operations it exercises. The environment owner provisions these through normal
administration. No staff credential or SDK-specific API mode is needed.

The recommended flow is to install the candidate wheel and, in both client styles,
upload small synthetic documents, wait for processing, retrieve authored content,
inspect/export, then delete the documents and verify completion. Give each run its
own identifiers, bound polling and provider usage, and clean up only resources
created by that run. Supply credentials privately. Run this check explicitly when
deployed compatibility needs validation; keep ordinary CI offline.

This opt-in flow is implemented by `qualification/beta_runner.py`; follow the
[beta validation instructions](beta-validation.md) and record its result separately.
The full `http_runner.py` expects the fixture contract, including two-tenant
references, restricted/revoked credentials and controlled failure states. A single
beta account/key cannot satisfy that matrix. A normal-lifecycle result must be
reported separately and must not claim full failure/security qualification.

## Evidence and ownership correction

The original [passing report](qualification/2026-09-21-local-http.json) records both
HTTP checks and the temporary environment's verified disposal. The separate API-side
bootstrap script used for that run was removed after Alex selected endpoint-only
qualification. Its source hashes and teardown fields remain historical evidence;
they are not prerequisites or capabilities of the current SDK runner. The runner,
wheel and contract identities in that report are unchanged by this ownership fix.

The historical service used deterministic embedding/scanner/parser adapters and a
server-owned Starter assignment. It made no paid provider or billing calls. This
proves HTTP and lifecycle behavior, not semantic ranking quality or hostile parser
isolation. API-owned security, parser, evaluation and deployment gates still apply.
