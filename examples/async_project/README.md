# Async project example (Python 3.12)

Three small scripts using the published `ragwell==0.1.0` SDK and `AsyncRagwell`.
They use an existing project; create it and its API key in the dashboard first.
Use a dedicated example project, since cleanup deletes **all** its documents.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
git clone https://github.com/alexd775/ragwell-python.git
cd ragwell-python/examples/async_project
uv sync --locked
cp env.example .env
```

On PowerShell use `Copy-Item env.example .env`. Edit `.env` with the API origin
(e.g. `https://api-beta.ragwell.dev`, without `/v1`), API key and project UUID.
The key must be granted to that project with these scopes:
`document:list`, `document:read`, `document:upload`, `job:read`, `retrieval:search`,
`document:delete`, `deletion:read`.

uv creates a local Python 3.12 environment and installs the SDK from PyPI. The
scripts load this directory's `.env`; shell variables take precedence. `.env`,
extra local documents and `results/` are ignored by Git.

## 1. Sync documents

```sh
uv run sync_documents.py
uv run sync_documents.py --status-only
```

Two fictional sample documents are included in `documents/`. Add PDF, UTF-8 text
or Markdown files there, or set `SYNC_FOLDER` in `.env` (relative to this directory).
The script scans one folder level, skips symlinks and unsupported files, visits all
remote pages, and uploads files whose **exact filename** is absent from the project.
Matching is case-sensitive; changed contents under the same filename are skipped.
It does not replace files or remove remote documents. Run one sync at a time.

Uploads run sequentially and wait for processing. The final list shows document
IDs, document state, searchability and latest job status. Use `--timeout 600` to
increase the default 300-second wait per job. A timeout stops local waiting; rerun
to observe already accepted work. Failed jobs are reported without automatic retry.
Sync exits nonzero if errors occur or project documents remain unsearchable.

## 2. Retrieve

```sh
uv run retrieve.py "Where are the purple lanterns stored?" --k 3
uv run retrieve.py "When does the workshop start?" --k 5 --output results/workshop.json
```

The full response includes chunks, scores and citations. `--k` accepts 1–20
(default 5). Optional filters: `--document-id UUID`, `--tag`, `--tag-all`, `--source`,
`--author`, `--language`, `--category`. Repeat a flag for multiple values; `--tag`
matches any supplied tag, and `--tag-all` requires all. Metadata/tag filters refer
to values already set on project documents. Without `--output`, stdout is JSON;
with it, the script creates a new UTF-8 JSON file and reports its path.

## 3. Clean the project

```sh
uv run clean_project.py           # preview all documents
uv run clean_project.py --yes     # delete them and wait for completion
```

Cleanup prints each deletion receipt and a final cleaned/error/remaining count.
It also removes documents uploaded outside this example. It keeps the project,
API key and local folder. `--timeout 600` increases the wait per deletion; incomplete
cleanup exits nonzero. Avoid concurrent uploads while cleaning.

Run any script with `--help`. Offline example tests: `uv run pytest`.
