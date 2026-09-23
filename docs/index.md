# Ragwell Python SDK documentation

Ragwell accepts documents, processes them, and retrieves relevant chunks with source citations. The Python SDK provides synchronous `Ragwell` and asynchronous `AsyncRagwell` clients. It does not generate answers.

**New here?** Follow the [quickstart](quickstart.md) to install the published package, upload a sample document, and retrieve a cited result. You need an existing project and a Ragwell API key from the dashboard.

| Learn | Use the SDK | Look up details |
|---|---|---|
| [Projects and keys](concepts/projects-and-keys.md) | [Upload and sync](guides/upload-and-sync.md) | [Clients and resources](reference/client-and-resources.md) |
| [Document lifecycle](concepts/document-lifecycle.md) | [Search and filters](guides/search-and-filter.md) | [Configuration](reference/configuration.md) |
| [Retrieval and citations](concepts/retrieval-and-citations.md) | [Async applications](guides/async-applications.md) | [Errors](reference/errors.md) |
| | [Errors and recovery](guides/errors-and-recovery.md) | [Scopes](reference/scopes.md) |
| | [Exports](guides/exports.md) | [Compatibility](help/compatibility.md) |
| | [Optional reranking](guides/reranking.md) | |

For a runnable Python 3.12 project, use the [three-script async example](../examples/async_project/README.md). It installs the published SDK from PyPI.

[Troubleshooting](help/troubleshooting.md) covers common setup and lifecycle failures. SDK contributors can start with [development](contributing/development.md), [contract generation](contributing/contract-generation.md), and [releases](contributing/releases.md). The [changelog](../CHANGELOG.md) records version changes.
