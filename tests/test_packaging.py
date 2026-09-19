"""Exercise the distribution boundary without an API or source-path imports."""

import base64
import csv
import hashlib
import io
import re
import subprocess
import sys
import tarfile
import venv
from collections import deque
from importlib.metadata import Distribution, PackagePath, distribution
from pathlib import Path
from zipfile import ZipFile

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

RUNTIME_REQUIREMENTS = ("attrs", "httpx", "python-dateutil")


def _runtime_dependency_closure() -> list[Distribution]:
    """Resolve installed runtime distributions without consulting a package index."""
    pending = deque(RUNTIME_REQUIREMENTS)
    resolved: dict[str, Distribution] = {}
    while pending:
        name = pending.popleft()
        normalized_name = canonicalize_name(name)
        if normalized_name in resolved:
            continue
        installed = distribution(name)
        resolved[normalized_name] = installed
        for value in installed.metadata.get_all("Requires-Dist") or []:
            requirement = Requirement(value)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                pending.append(requirement.name)
    return [resolved[name] for name in sorted(resolved)]


def _wheel_record_entry(path: str, data: bytes) -> tuple[str, str, str]:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return path, f"sha256={digest.decode('ascii')}", str(len(data))


def _repack_installed_wheel(installed: Distribution, wheelhouse: Path) -> None:
    """Recreate a pure-Python wheel from the locked environment for offline tests."""
    files = installed.files
    wheel_metadata = installed.read_text("WHEEL")
    package_name = installed.metadata["Name"]
    assert files is not None
    assert wheel_metadata is not None
    assert package_name is not None
    assert "Root-Is-Purelib: true" in wheel_metadata

    tags = [
        line.removeprefix("Tag: ")
        for line in wheel_metadata.splitlines()
        if line.startswith("Tag: ")
    ]
    tag = next((candidate for candidate in tags if candidate.startswith("py3-")), None)
    assert tag is not None
    wheel_name = re.sub(r"[-_.]+", "_", package_name)
    wheel_version = re.sub(r"[-]+", "_", installed.version)
    wheel_path = wheelhouse / f"{wheel_name}-{wheel_version}-{tag}.whl"

    archive_files: list[tuple[PackagePath, Path]] = []
    for file in files:
        source = Path(str(installed.locate_file(file)))
        if (
            ".." not in file.parts
            and file.name not in {"INSTALLER", "RECORD", "REQUESTED"}
            and source.is_file()
        ):
            archive_files.append((file, source))
    dist_info_directories = {
        file.parts[0]
        for file, _ in archive_files
        if file.parts and file.parts[0].endswith(".dist-info")
    }
    assert len(dist_info_directories) == 1
    dist_info = dist_info_directories.pop()
    records: list[tuple[str, str, str]] = []
    with ZipFile(wheel_path, "w") as archive:
        for file, source in sorted(
            archive_files, key=lambda candidate: candidate[0].as_posix()
        ):
            archive_path = file.as_posix()
            data = source.read_bytes()
            archive.writestr(archive_path, data)
            records.append(_wheel_record_entry(archive_path, data))

        record_path = f"{dist_info}/RECORD"
        record_buffer = io.StringIO(newline="")
        writer = csv.writer(record_buffer, lineterminator="\n")
        writer.writerows(records)
        writer.writerow((record_path, "", ""))
        archive.writestr(record_path, record_buffer.getvalue().encode())


def _prepare_runtime_wheelhouse(wheelhouse: Path) -> None:
    wheelhouse.mkdir()
    for installed in _runtime_dependency_closure():
        _repack_installed_wheel(installed, wheelhouse)


@pytest.fixture(scope="session")
def distributions(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    output = tmp_path_factory.mktemp("dist")
    repository = Path(__file__).resolve().parents[1]
    # PyPA build's default builds the wheel from the freshly created sdist.
    subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(output)],
        cwd=repository,
        check=True,
    )
    (sdist,) = output.glob("*.tar.gz")
    (wheel,) = output.glob("*.whl")
    return sdist, wheel


def test_distributions_include_sources_typing_and_license(
    distributions: tuple[Path, Path],
) -> None:
    sdist, wheel = distributions
    with tarfile.open(sdist) as archive:
        source_files = {
            Path(name).relative_to(sdist.name.removesuffix(".tar.gz")).as_posix()
            for name in archive.getnames()
        }
    assert {
        "src/ragwell/__init__.py",
        "src/ragwell/py.typed",
        "LICENSE",
        "README.md",
        "CONTRIBUTING.md",
        "pyproject.toml",
        "uv.lock",
        "tests/test_packaging.py",
        "contracts/2026-09-19.1/openapi.json",
        "contracts/2026-09-19.1/manifest.json",
        "contracts/operations.json",
        "docs/generation.md",
        "docs/http-qualification.md",
        "examples/sync_search.py",
        "examples/async_search.py",
        "qualification/http_runner.py",
        "scripts/generate.py",
        "openapi-python-client.yaml",
    } <= source_files

    with ZipFile(wheel) as archive:
        wheel_files = set(archive.namelist())
    assert {"ragwell/__init__.py", "ragwell/py.typed"} <= wheel_files
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in wheel_files)
    assert all(
        name.startswith("ragwell/") or ".dist-info/" in name for name in wheel_files
    )


def test_wheel_imports_with_typing_marker_in_clean_environment(
    distributions: tuple[Path, Path], tmp_path: Path
) -> None:
    _, wheel = distributions
    environment = tmp_path / "venv"
    wheelhouse = tmp_path / "wheelhouse"
    _prepare_runtime_wheelhouse(wheelhouse)
    # POSIX symlinks preserve shared-library lookup for standalone interpreters.
    venv.EnvBuilder(symlinks=sys.platform != "win32").create(environment)
    python = environment / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--offline",
            "--no-index",
            "--find-links",
            str(wheelhouse),
            "--python",
            str(python),
            str(wheel),
        ],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            """
import sys
from importlib.metadata import distribution
from importlib.resources import files
from importlib.util import find_spec
from pathlib import Path

import ragwell

assert Path(ragwell.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert files(ragwell).joinpath("py.typed").is_file()
package = distribution("ragwell")
assert package.metadata["Name"] == "ragwell"
assert package.metadata["License-Expression"] == "MIT"
requirements = package.requires or []
assert requirements == [
    "attrs<26,>=22.2",
    "httpx<0.29,>=0.27.2",
    "python-dateutil<3,>=2.8.2",
]
assert all("pytest" not in item and "ruff" not in item and "mypy" not in item for item in requirements)
assert str(distribution("httpx").version)
assert str(distribution("attrs").version)
assert str(distribution("python-dateutil").version)
assert all(find_spec(name) is None for name in ("mypy", "pytest", "ruff"))
with ragwell.Ragwell(base_url="https://api.example.test", api_key="test-key") as client:
    project = client.project("00000000-0000-0000-0000-000000000001")
    assert str(project.id) == "00000000-0000-0000-0000-000000000001"
print("Clean installed-package import and typing marker passed")
""",
        ],
        cwd=tmp_path,
        check=True,
    )
