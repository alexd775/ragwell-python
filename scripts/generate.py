"""Verify and deterministically regenerate the vendored internal API client."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "contracts" / "2026-09-22.1"
OPENAPI = ARTIFACT / "openapi.json"
MANIFEST = ARTIFACT / "manifest.json"
CONFIG = ROOT / "openapi-python-client.yaml"
CHECKED_IN = ROOT / "src" / "ragwell" / "_generated"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inventory(openapi: dict[str, object]) -> set[tuple[str, str, str]]:
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        raise SystemExit("OpenAPI paths must be an object")
    result: set[tuple[str, str, str]] = set()
    for path, item in paths.items():
        if not isinstance(path, str) or not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not isinstance(operation, dict) or not isinstance(
                operation.get("operationId"), str
            ):
                raise SystemExit(f"Missing operationId for {method.upper()} {path}")
            result.add((method.upper(), path, operation["operationId"]))
    return result


def verify_contract() -> None:
    manifest = json.loads(MANIFEST.read_text())
    openapi = json.loads(OPENAPI.read_text())
    actual_digest = _sha256(OPENAPI)
    if actual_digest != manifest["machine_sha256"]:
        raise SystemExit(
            f"Machine contract digest mismatch: {actual_digest} != "
            f"{manifest['machine_sha256']}"
        )
    expected = {
        (row["method"], row["path"], row["operation_id"])
        for row in manifest["operations"]
    }
    actual = _inventory(openapi)
    if actual != expected or len(actual) != manifest["operation_count"]:
        raise SystemExit("Manifest operation inventory does not match openapi.json")


def generate(output: Path, *, overwrite: bool) -> None:
    command = [
        "openapi-python-client",
        "generate",
        "--path",
        str(OPENAPI),
        "--config",
        str(CONFIG),
        "--meta",
        "none",
        "--output-path",
        str(output),
        "--fail-on-warning",
    ]
    if overwrite:
        command.append("--overwrite")
    subprocess.run(command, cwd=ROOT, check=True)
    ruff_config = ROOT / "pyproject.toml"
    subprocess.run(
        [
            "ruff",
            "check",
            str(output),
            "--fix-only",
            "--config",
            str(ruff_config),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["ruff", "format", str(output), "--config", str(ruff_config)],
        cwd=ROOT,
        check=True,
    )


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and ".ruff_cache" not in path.parts
    }


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="ragwell-generation-") as directory:
        generated = Path(directory) / "_generated"
        generate(generated, overwrite=False)
        expected = _files(CHECKED_IN)
        actual = _files(generated)
        if actual != expected:
            missing = sorted(expected.keys() - actual.keys())
            extra = sorted(actual.keys() - expected.keys())
            changed = sorted(
                name
                for name in expected.keys() & actual.keys()
                if expected[name] != actual[name]
            )
            raise SystemExit(
                "Generated client drift detected\n"
                f"missing={missing}\nextra={extra}\nchanged={changed}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="compare a temporary regeneration"
    )
    arguments = parser.parse_args()
    verify_contract()
    if arguments.check:
        check()
    else:
        generate(CHECKED_IN, overwrite=True)


if __name__ == "__main__":
    main()
