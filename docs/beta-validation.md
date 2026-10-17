# Optional validation against the deployed beta API

This SDK-owned check uses an installed wheel and a dedicated ordinary beta account,
project and API key. It connects only through public HTTPS. It does not start the
API, create accounts/projects/keys, access a database or require a backend checkout.
Ordinary CI remains offline. This is a normal-lifecycle integration check; it does
not replace the full two-tenant and controlled-failure qualification matrix.

## Prepare the account and key

Create a dedicated test account and project through normal beta administration.
Choose an available processing profile/embedding connection. Allow capacity for two
small text ingestions, two searches and one temporary document export at a time.
Provider-backed ingestion/search uses the project's normal quotas and provider
configuration; the runner neither changes plans nor supplies provider credentials.

Grant the key to that project only, with these seven scopes:

- `project:read`
- `document:upload`
- `document:read`
- `job:read`
- `retrieval:search`
- `document:delete`
- `deletion:read`

Store the key alone in a private local file, outside the repository. On POSIX the
file must have no group/other access (for example, mode `0600`); symlinks are rejected.
Supply its path through `RAGWELL_BETA_API_KEY_FILE`. The runner does not load `.env`
files or accept a key on its command line. Do not paste it into issues or reports.

## Build, install and run

From the SDK repository, build a new candidate and install it in a fresh environment:

```sh
uv run --locked python -m build --no-isolation --outdir /absolute/path/candidate
python3 -m venv /absolute/path/beta-validation-venv
/absolute/path/beta-validation-venv/bin/python -m pip install \
  /absolute/path/candidate/ragwell-0.2.0-py3-none-any.whl

RAGWELL_BETA_API_KEY_FILE=/private/path/to/key \
  /absolute/path/beta-validation-venv/bin/python -m qualification.beta_runner \
  --base-url https://api-beta.ragwell.dev \
  --project-id YOUR_PROJECT_UUID \
  --wheel /absolute/path/candidate/ragwell-0.2.0-py3-none-any.whl \
  --output /absolute/path/new-beta-validation-report.json
```

Pass the API origin without `/v1`; resource methods add that prefix. The output
must be a new filename in an existing directory. The runner rejects an editable
installation, changed package files, or a live machine-contract digest that differs
from the packaged reviewed contract before issuing authenticated mutations. It
never disables TLS verification or follows redirects. Runtime execution needs only
Python and the installed wheel's dependencies; uv is used for SDK development.

## Flow and limits

The runner performs the synchronous flow first, then the asynchronous flow only if
the first completes successfully:

1. Read the granted project; upload one uniquely named synthetic `.txt` document
   smaller than 1 KiB and retain its upload/document/job identities.
2. Wait for processing and inspect its searchable generation.
3. Search only that new document, checking authored content, document/version
   identity, citations and finite scores. Search is not automatically replayed.
4. Create an export without embeddings, wait, and download all parts with the SDK's
   manifest size/hash verification. Export downloads are capped at 1 MiB total and
   ten parts; temporary downloads are removed locally.
5. Delete the created document, wait for the deletion receipt and verify that the
   document can no longer be read.

Each SDK operation has a 30-second deadline; upload/download helpers have 60 seconds.
Each processing/export/deletion wait defaults to 180 seconds, with polling starting
at two seconds and backing off to five. `--wait-timeout` accepts 1–600 seconds per
wait. These are per-operation/wait limits, not a single wall-clock budget for the
entire run. The runner performs at most two logical uploads and two searches and
stops after any failed style. It does not inject server faults or retry failed jobs.

## Evidence, failures and cleanup

The JSON report records `qualification: beta_lifecycle`, the exact wheel and live
contract digests, runner/evidence source hashes, runtime versions, run ID, resource
IDs, per-style checks and cleanup results. It is written privately and checkpointed
with atomic replacement. It contains no API key, document/query text, downloaded
content, raw server messages or credential-file path. Exit status is zero only when
both styles and their deletion checks pass. An interrupted run is not passing evidence.

Cleanup runs after failures and recoverable interruption, using only this run's
resource identifiers. A lost finalization response can be recovered through the
public upload-state endpoint. Unknown upload acceptance or an unfinalized upload is
reported for normal expiry/operator follow-up; the runner never enumerates and
bulk-deletes project contents. Forced process termination or an unavailable API can
prevent cleanup, so retain the report and resolve any remaining resource IDs before
rerunning. Account, project, key and infrastructure lifecycle remains with their owner.

Save successful evidence separately from the full
[HTTP qualification](http-qualification.md) report. A beta result proves the tested
wheel/contract/lifecycle integration at that time, not complete operation coverage,
provider quality, load capacity or cross-tenant authorization.
