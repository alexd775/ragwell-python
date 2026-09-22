# Release runbook

This is the maintainer procedure for publishing `ragwell` through GitHub Actions.
The repository uses PyPI Trusted Publishing (OIDC); maintainers do not upload with
Twine and no PyPI token belongs in GitHub or a local `.env` file.

For release policy, qualification evidence and the previous publication record, see
[release preparation](releasing.md). For the opt-in deployed API check, see
[beta validation](beta-validation.md).

## Before tagging

1. Choose a version that has never been uploaded to TestPyPI or PyPI. Published
   files are immutable and a version cannot be reused.
2. Update the stable version in `pyproject.toml`, `src/ragwell/_version.py` and
   `uv.lock`, and add the release to `CHANGELOG.md`.
3. Finish the contract, documentation and qualification evidence for that version.
4. From the repository root, run:

   ```sh
   uv sync --locked
   uv run --locked ruff format --check .
   uv run --locked ruff check .
   uv run --locked mypy
   uv run --locked python scripts/generate.py --check
   uv run --locked pytest
   uv run --locked python -m build --no-isolation
   ```

5. Commit and push the release candidate to `main`. Wait for CI, including the
   example workflow when it applies, to pass on that exact commit.
6. Confirm the working tree is clean and local `HEAD` equals `origin/main`:

   ```sh
   git status --short
   git rev-parse HEAD
   git rev-parse origin/main
   ```

The `testpypi` and `pypi` GitHub environments and matching Trusted Publishers must
already identify owner `alexd775`, repository `ragwell-python`, workflow
`release.yml`, and their corresponding environment names. The `pypi` environment
requires maintainer approval.

## Start the release

Create and push one annotated tag whose name exactly matches the project version:

```sh
git tag -a vX.Y.Z -m "ragwell X.Y.Z"
git push origin vX.Y.Z
```

Do not move or recreate a release tag after pushing it. A manual **Run workflow**
execution is only a build rehearsal; publication jobs run only for a `v*` tag.

The tag starts `.github/workflows/release.yml`, which:

1. checks that the tag is on `main` and equals the package version;
2. runs the locked format, lint, type, generation and test gates;
3. builds the wheel and source archive once and saves their hashes;
4. publishes those artifacts to TestPyPI through OIDC;
5. downloads the staged wheel, compares its hash and installs it cleanly;
6. waits for approval on the protected `pypi` environment; and
7. publishes the same artifacts to production PyPI through OIDC.

Before approving production, review the workflow hashes and run the bounded beta
lifecycle against the exact staged wheel when the release changes runtime behavior
or the API contract. Never rebuild between TestPyPI and PyPI.

## Approve production PyPI

After the staged-wheel verification is green, the production job should show
**Waiting** for the `pypi` environment. In the workflow run:

1. select **Review deployments**;
2. select `pypi`;
3. choose **Approve and deploy**; and
4. wait for **Publish the verified distributions to PyPI** to pass.

This approval is the only manual publication step after pushing the tag.

## TestPyPI indexing delay

A successful TestPyPI upload may take several minutes to appear in its simple index.
In that case the publish job is green, while **Verify the staged TestPyPI wheel**
reports `No matching distribution found` for the new version. This is an indexing
delay, not a missing preparation step.

1. Check `https://test.pypi.org/project/ragwell/X.Y.Z/` or
   `https://test.pypi.org/pypi/ragwell/X.Y.Z/json`.
2. If the version is now visible, open the original Actions run and choose
   **Re-run jobs → Re-run failed jobs**.
3. Do not choose **Re-run all jobs**: TestPyPI has already accepted the immutable
   files, so repeating the successful publish job can only fail.
4. If the version is still absent after 15 minutes, inspect the TestPyPI publish job
   before doing anything else. Do not create another tag or manually upload files.

The workflow waits up to ten minutes and bypasses pip's local cache before reporting
this condition. A later failed-job rerun is safe because it repeats verification and
the dependent production job, not the successful TestPyPI publication.

## Verify the public release

After the workflow is green, verify a clean install from production PyPI:

```sh
python3 -m venv /tmp/ragwell-release-check
/tmp/ragwell-release-check/bin/python -m pip install --no-cache-dir "ragwell==X.Y.Z"
/tmp/ragwell-release-check/bin/python -I -c \
  "from importlib.metadata import version; import ragwell; assert version('ragwell') == 'X.Y.Z'; assert ragwell.__version__ == 'X.Y.Z'"
```

Confirm the PyPI file hashes match the workflow artifact, then create the GitHub
release record and update publication evidence. If a published artifact is faulty,
yank it or publish a new version; never overwrite or reuse the released version.
