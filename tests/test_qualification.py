"""Offline checks of the qualification evidence boundary."""

import copy
import json
from pathlib import Path

import httpx

from qualification.evidence import Evidence, service_projection

CONTRACT = Path(__file__).resolve().parents[1] / "contracts/2026-09-19.1/openapi.json"


def test_runtime_projection_detects_schema_and_machine_inventory_drift() -> None:
    canonical = json.loads(CONTRACT.read_bytes())
    version = canonical["x-ragwell-artifact-version"]
    assert service_projection(canonical, version) == CONTRACT.read_bytes()
    changed = copy.deepcopy(canonical)
    changed["paths"]["/v1/new-machine-path"] = {
        "get": {
            "operationId": "new_machine_operation",
            "security": [{"ApiKeyBearer": []}],
            "responses": {"200": {"description": "OK"}},
        }
    }
    assert service_projection(changed, version) != CONTRACT.read_bytes()
    changed = copy.deepcopy(canonical)
    changed["components"]["schemas"]["DocumentResponse"]["properties"][
        "metadata_revision"
    ]["type"] = "string"
    assert service_projection(changed, version) != CONTRACT.read_bytes()


def test_denials_and_faults_cannot_satisfy_positive_operation_coverage() -> None:
    evidence = Evidence(json.loads(CONTRACT.read_bytes()))
    request = httpx.Request("GET", "http://127.0.0.1/v1/projects/example")
    evidence.phase = "missing_scope"
    evidence.observe(request, httpx.Response(403))
    assert not evidence.success
    assert len(evidence.denials["missing_scope"]) == 1
    evidence.phase = "positive"
    evidence.drop = ("GET", request.url.path)
    assert not evidence.observe(request, httpx.Response(503))
    assert evidence.drop is not None and not evidence.success
    assert evidence.observe(request, httpx.Response(200))
    assert evidence.drop is None and len(evidence.dropped) == 1
    assert not evidence.observe(request, httpx.Response(200))
    assert len(evidence.success) == 1
