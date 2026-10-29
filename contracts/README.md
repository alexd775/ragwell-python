# Vendored machine contract

The source candidate SDK uses artifact `2026-10-29.1` from
`contracts/2026-10-29.1/`. It adds the bounded project agent-description projection
with current `retrieval:search` authorization and preserves the complete
28-operation sync/async map.

- Producer: Ragwell API Outcome 69 working tree, 2026-10-29; canonical contract
  SHA-256 `4a4e470af6bb7c0b9d7ee7652a32fbda08882b0f3199b51947657dcc15d8b819`.
- Machine SHA-256:
  `9d92aa868fb134a8de534765f2bf41b6f7e45c871bbc425a12d566d6a3a3ff5a`.
- SDK candidate: unpublished `0.2.3`; deploy the matching API and publish the SDK
  before installed integrations adopt the new method.

The refresh also types the existing project document-storage location/editability
fields. Previously consumed artifacts remain preserved for published releases,
including `0.2.2`'s `2026-10-03.1` contract. The candidate does not inherit their
live-service or public-wheel qualification.

The wheel includes the selected OpenAPI and manifest under `ragwell/_contract/`.
Ordinary generation, tests, builds and installation require no backend checkout.
Run `uv run --locked python scripts/generate.py --check` to verify generation.
