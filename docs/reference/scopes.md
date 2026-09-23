# API key scopes

The dashboard creates a key and grants it to a project. Each request needs both the current project/resource grant and its operation's scope. These are the SDK's current operation groups; consult [clients and resources](client-and-resources.md) for every method.

| Work | Required scope |
|---|---|
| Read upload policy | Public, no key scope |
| Read project or embedding connection | `project:read` |
| Create, transfer, finalize, or inspect upload intake | `document:upload` |
| List documents | `document:list` |
| Read, inspect, export, or view activity/chunks/sources | `document:read` |
| Replace document metadata | `document:update` |
| Delete a document | `document:delete` |
| List jobs | `job:list` |
| Read or wait for a job | `job:read` |
| Retry a job | `job:retry` |
| Cancel a job | `job:cancel` |
| Search, with or without optional reranking | `retrieval:search` |
| Read or wait for a deletion receipt | `deletion:read` |
| Retry deletion | `deletion:retry` |

The upload-policy endpoint has no scope requirement, although client construction still requires a configured Ragwell key. `documents.upload_and_wait()` requires both `document:upload` and `job:read`. `client.project(project_id)` is local and needs no `project:read` preflight. Grant only the scopes the application actually uses. See [projects and keys](../concepts/projects-and-keys.md).
