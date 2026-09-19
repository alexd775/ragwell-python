# Contract generation qualification

## Selected tooling

- `openapi-python-client==0.29.0` is pinned as development-only generation tooling.
  Its official project documents OpenAPI 3.0/3.1 generation and an MIT license,
  while warning that not every OpenAPI feature is supported:
  <https://github.com/openapi-generators/openapi-python-client>.
- `httpx>=0.27.2,<0.29` is the maintained runtime transport range. Qualification
  used 0.28.1. HTTPX provides pooled sync/async clients, explicit timeouts,
  streaming, and custom transports and is BSD-3-Clause licensed:
  <https://www.python-httpx.org/>.

Runtime dependencies are deliberately limited to HTTPX (BSD-3-Clause), attrs
(MIT), and python-dateutil (dual Apache-2.0/BSD). The generator is not runtime
metadata. The development lock pins the complete maintainer environment.

## Evaluation result

The unconfigured generator reported two bounded warnings and skipped wire details:
the three raw upload media types (`application/pdf`, `text/plain`, and
`text/markdown`) and the binary `application/x-ndjson` export response. The
generator's documented `content_type_overrides` configuration makes all 26
operation bindings and all 71 referenced component schemas generate without a
warning. Generated raw request code retains the original media-type header values,
and the NDJSON success response becomes bytes.

One generator limitation remains: its multi-content binary upload binding collapses
the three bodies to the same `File` runtime type, so generated branch ordering would
select only the last media type. Generated files are not patched. The maintained
public transport owns raw upload and export streaming, chooses the caller's exact
reviewed media type, retains streaming and retry identity, and is covered by direct
wire-shape tests in both client styles. Generated JSON models and all operation
bindings remain internal; users depend on the maintained resource interface.

Qualification covers OpenAPI 3.1 null unions, omission through `UNSET`, UUIDs,
aware timestamps, query arrays, enums/discriminated citation shapes, additive
response fields, typed normal/quota errors, all three raw uploads, and NDJSON bytes.
Unknown lifecycle enums fail as protocol errors rather than being treated as
success. The checked-in operation manifest maps every contract operation to sync
and async public methods.

## Reproducibility

`openapi-python-client.yaml` is the reviewed generator configuration.
`scripts/generate.py` verifies the artifact digest and complete manifest inventory,
then either regenerates the internal package or compares a clean temporary
regeneration byte-for-byte. It uses only vendored inputs.
