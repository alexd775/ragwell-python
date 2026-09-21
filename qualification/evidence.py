"""Wheel identity and real-HTTP operation evidence, with no backend dependency."""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import re
import sysconfig
import zipfile
from importlib.metadata import distribution
from pathlib import Path
from typing import Any

import httpx

import ragwell


def installed_identity(wheel: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    package = Path(ragwell.__file__).resolve()
    site = Path(sysconfig.get_path("purelib")).resolve()
    if not package.is_relative_to(site):
        raise ValueError(
            "Qualification requires a wheel installed into this interpreter"
        )
    dist = distribution("ragwell")
    direct = json.loads(dist.read_text("direct_url.json") or "{}")
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    archive_info = direct.get("archive_info")
    if (
        not isinstance(archive_info, dict)
        or direct.get("url") != wheel.resolve().as_uri()
    ):
        raise ValueError("Installed distribution does not identify the supplied wheel")
    recorded_hash = archive_info.get("hashes", {}).get("sha256")
    if recorded_hash is not None and recorded_hash != digest:
        raise ValueError("Installed distribution wheel hash differs")
    with zipfile.ZipFile(wheel) as archive:
        names = {
            name
            for name in archive.namelist()
            if name.startswith("ragwell/") and not name.endswith("/")
        }
        for name in names:
            installed = site / name
            if not installed.is_file() or installed.read_bytes() != archive.read(name):
                raise ValueError("Installed package differs from the supplied wheel")
        actual = {
            path.relative_to(site).as_posix()
            for path in package.parent.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        if actual != names:
            raise ValueError("Installed package contains unaccounted files")
    contract = json.loads((package.parent / "_contract/openapi.json").read_text())
    manifest = json.loads((package.parent / "_contract/manifest.json").read_text())
    if (
        hashlib.sha256(
            (package.parent / "_contract/openapi.json").read_bytes()
        ).hexdigest()
        != manifest["machine_sha256"]
    ):
        raise ValueError("Packaged contract digest mismatch")
    return {
        "wheel_sha256": digest,
        "sdk_version": dist.version,
        "python_version": platform.python_version(),
        "platform": platform.system() + " " + platform.machine(),
        "runtime_dependencies": {
            name: distribution(name).version
            for name in ("attrs", "httpx", "httpcore", "python-dateutil")
        },
        "machine_sha256": manifest["machine_sha256"],
        "operation_count": manifest["operation_count"],
    }, contract


def service_projection(canonical: dict[str, Any], artifact_version: str) -> bytes:
    """Apply the documented machine projection to the running public OpenAPI."""
    result = {key: copy.deepcopy(canonical[key]) for key in ("openapi", "info")}
    paths: dict[str, Any] = {}
    for path, methods in canonical["paths"].items():
        for method, operation in methods.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            machine = any(
                "ApiKeyBearer" in item for item in operation.get("security", [])
            )
            if not machine and (method, path) != ("get", "/v1/document-upload-policy"):
                continue
            selected = copy.deepcopy(operation)
            selected["security"] = [{"ApiKeyBearer": []}] if machine else []
            if "parameters" in selected:
                selected["parameters"] = [
                    p
                    for p in selected["parameters"]
                    if not (
                        p.get("in") == "header"
                        and p.get("name", "").lower() == "x-csrf-token"
                    )
                ]
            paths.setdefault(path, {})[method] = selected

    def references(value: Any) -> set[str]:
        if isinstance(value, dict):
            return {v for k, v in value.items() if k == "$ref"} | set().union(
                *(references(v) for v in value.values())
            )
        if isinstance(value, list):
            return set().union(*(references(v) for v in value))
        return set()

    components: dict[str, Any] = {
        "securitySchemes": {
            "ApiKeyBearer": canonical["components"]["securitySchemes"]["ApiKeyBearer"]
        }
    }
    pending, seen = references(paths), set()
    while pending:
        ref = pending.pop()
        if ref in seen:
            continue
        prefix, category, name = ref.rsplit("/", 2)
        if prefix != "#/components":
            raise ValueError("Unsupported contract reference")
        value = canonical["components"][category][name]
        components.setdefault(category, {})[name] = value
        seen.add(ref)
        pending.update(references(value) - seen)
    result.update(paths=paths, components=components)
    result["x-ragwell-artifact-version"] = artifact_version
    return (
        json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode()


class Evidence:
    def __init__(self, contract: dict[str, Any]) -> None:
        self.operations = [
            (
                method.upper(),
                re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path) + "$"),
                operation["operationId"],
            )
            for path, methods in contract["paths"].items()
            for method, operation in methods.items()
        ]
        self.success: set[str] = set()
        self.denials: dict[str, set[str]] = {}
        self.phase = "positive"
        self.drop: tuple[str, str] | None = None
        self.dropped: list[str] = []

    def observe(self, request: httpx.Request, response: httpx.Response) -> bool:
        matches = [
            name
            for method, pattern, name in self.operations
            if request.method == method and pattern.fullmatch(request.url.path)
        ]
        if not matches:
            return False
        name = matches[0]
        if 200 <= response.status_code < 300 and self.phase == "positive":
            self.success.add(name)
        if response.status_code in {401, 403, 404}:
            self.denials.setdefault(self.phase, set()).add(name)
        if (
            self.drop == (request.method, request.url.path)
            and 200 <= response.status_code < 300
        ):
            self.drop = None
            self.dropped.append(name)
            return True
        return False


class FaultTransport(httpx.BaseTransport):
    """Forward to real TCP; discard one selected response only after acceptance."""

    def __init__(self, evidence: Evidence) -> None:
        self.inner = httpx.HTTPTransport(trust_env=False)
        self.evidence = evidence

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = self.inner.handle_request(request)
        if self.evidence.observe(request, response):
            response.read()
            response.close()
            raise httpx.ReadError(
                "Qualification discarded an accepted response", request=request
            )
        return response

    def close(self) -> None:
        self.inner.close()


class AsyncFaultTransport(httpx.AsyncBaseTransport):
    def __init__(self, evidence: Evidence) -> None:
        self.inner = httpx.AsyncHTTPTransport(trust_env=False)
        self.evidence = evidence

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self.inner.handle_async_request(request)
        if self.evidence.observe(request, response):
            await response.aread()
            await response.aclose()
            raise httpx.ReadError(
                "Qualification discarded an accepted response", request=request
            )
        return response

    async def aclose(self) -> None:
        await self.inner.aclose()
