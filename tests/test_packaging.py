"""Exercise the distribution boundary without an API or source-path imports."""

import subprocess
import sys
import tarfile
import venv
from pathlib import Path
from zipfile import ZipFile

import pytest


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
    # POSIX symlinks preserve shared-library lookup for standalone interpreters.
    venv.EnvBuilder(with_pip=True, symlinks=sys.platform != "win32").create(environment)
    python = environment / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--offline",
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
with ragwell.Ragwell(base_url="https://api.example.test", api_key="test-key") as client:
    project = client.project("00000000-0000-0000-0000-000000000001")
    assert str(project.id) == "00000000-0000-0000-0000-000000000001"
print("Clean installed-package import and typing marker passed")
""",
        ],
        cwd=tmp_path,
        check=True,
    )
