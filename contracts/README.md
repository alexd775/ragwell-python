# Vendored machine contract

The SDK is generated and tested against Ragwell machine artifact
`2026-09-19.1` in `contracts/2026-09-19.1/`.

- Source at adoption: local API checkout
  `/Users/alex/projects/rag-api/contracts/machine/2026-09-19.1/`.
- Source API branch/HEAD observed on 2026-09-19:
  `api_enablement_for_sdk` at `a7b57fd51e9bf4314550311f7d717e146559f782`.
- Machine OpenAPI SHA-256:
  `06d0efac740946c21f0ddfa3d873e2197cf4924487ed512d08b8c2fd824978bd`.
- Canonical API SHA-256 recorded by the producer:
  `fcbf93d2fe26cb7e54738dad8a7661611e8d762ec74361c79a75ffb7730b970a`.
- Inventory: 26 operations: 25 bearer operations and public upload policy.

The source API checkout contained uncommitted enablement work when this exact artifact
was adopted. This record does not claim that the artifact is committed, deployed, or
publicly downloadable. The files are vendored so SDK generation, tests, builds, and
ordinary installation require no backend checkout or private repository access.

Run `uv run --locked python scripts/generate.py --check` to verify the digest,
manifest inventory, and deterministic generated output.
