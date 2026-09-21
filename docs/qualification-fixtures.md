# Prepared endpoint and fixture requirements

The SDK HTTP runner consumes an independently prepared test environment. This
file describes its inputs, not a deployment or database setup procedure. The SDK
owns no API launcher, migrations, seed script or infrastructure teardown.

The endpoint must expose the reviewed public OpenAPI document and all 26 machine
operations. Its ingestion, export and deletion workers must be running. Allow
sufficient synthetic storage, document, page, token and retrieval capacity for the
complete run; the historical run used Starter capacity. Requests must complete
within the runner's finite deadlines. Use a fresh fixture set for each run because
retry, cancellation and deletion checks change the supplied control resources.

## Manifest

Pass a JSON file using `--manifest`. It contains:

| Field | Required value |
|---|---|
| `base_url` | URL of the already running isolated API |
| `fixture_revision` | Environment owner's fixture revision identifier |
| `api_commit` | Tested service source/release identifier; supplied as metadata, with no repository access |
| `machine_sha256` | Reviewed machine-contract digest; also verified independently over HTTP |
| `configuration` | Non-secret description of provider/profile/storage/database configuration |
| `marker` | Authored search term present in all three supplied documents |
| `fixtures` | Three objects with local absolute `path` and file `sha256`, using `.txt`, `.md` and `.pdf` |
| `tenants.owner`, `tenants.foreign` | Resource references described below |

Each tenant reference contains UUID strings named `project_id`, `document_id`,
`generation_id`, `source_id`, `chunk_id`, `upload_id`, `job_id`, `export_id` and
`receipt_id`. The document must remain readable with a succeeded generation and
an available export part numbered zero. The source/chunk belong to that generation;
the finalized upload and job belong to that document. The deletion receipt belongs
to a different document so the baseline document remains available. Projects must
belong to separate tenants with no cross-tenant grants. Baseline references must
remain usable throughout both client styles.

The owner reference additionally contains separate `sync` and `async` control
objects. Each contains:

| Control | References and starting state |
|---|---|
| `retry` | `job_id` and its `document_id`; failed, manually retryable job with a valid original upload; one retry must complete successfully |
| `cancel` | `job_id` and its `document_id`; job held queued until cancellation, then reconciled to `cancelled` by the service |
| `delete` | `receipt_id` and its `document_id`; failed receipt that one retry can complete |
| `expired` | `document_id`, `export_id`; readable document with retained expired export metadata; downloading part zero must return `export_not_available` |

The owner baseline receipt can reference the sync failed-deletion control; receipts
must remain readable after completion. Expired exports must not occupy the active
export capacity. Keep room for two new retained exports during each client style.

Supply synthetic documents within the API's upload/parser limits. Each must produce
searchable chunks with exact source-span citations. The `.txt` fixture must produce
more than 100 chunks and multiple export parts under the configured processing
profile, exercising pagination and multi-part downloads. The three fixture bytes
are verified against their manifest hashes before upload. Expected metadata is set
by the runner through the public API.

## Credentials

Set `RAGWELL_QUALIFICATION_CREDENTIALS_FILE` to a private JSON file. Its fields are:

| Label | Credential requirements |
|---|---|
| `owner` | Existing API key granted to the owner project with every machine scope listed below |
| `read_only` | Owner project grant and only `project:read` |
| `search_only` | Owner project grant and only `retrieval:search` |
| `revoked` | Previously valid owner credential, revoked before the run |

Owner scopes: `project:read`, `document:list`, `document:read`, `document:upload`,
`document:update`, `document:delete`, `job:list`, `job:read`, `job:retry`, `job:cancel`,
`retrieval:search`, `deletion:read` and `deletion:retry`.

Keep secrets out of the manifest and report. On POSIX the credential file must have
no group/other permissions. The runner does not create or revoke credentials.

## Cleanup ownership

The runner deletes its own uploaded documents over HTTP and records cleanup results,
including identifiers needed after partial failure. It exercises the supplied
control operations but does not remove all pre-provisioned baseline/control resources.
The environment owner retires those resources and credentials and decides when to
stop or dispose of the service. The SDK never receives database or infrastructure
credentials.
