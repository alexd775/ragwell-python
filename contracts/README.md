# Vendored machine contract

The development SDK uses artifact `2026-10-02.1` from `contracts/2026-10-02.1/`.
It adds generation identity to search hits and document/version identity to bounded
source previews. All 26 sync/async operations remain unchanged.

- Producer: Ragwell API source-fetch working tree, 2026-10-02; canonical contract
  SHA-256 `c64f9cba4b04a126756a79aa32eb811e07c144014046af7d948c3012bf3075b4`.
- Machine SHA-256: `8f41e9a1ea22238e6152361b4dd244181d5ef2732de9100ccb29e85c8ef255e5`.
- SDK candidate: unpublished 0.2.1; deploy the updated API before adopting it.

Previously consumed artifacts remain preserved for published 0.1.0/0.2.0. The new
candidate does not inherit their deployed beta or public-wheel qualification.
The source-fetch delivery record is maintained in the API project; ordinary SDK
generation, tests, builds and installation require no backend checkout.

The wheel includes the selected OpenAPI and manifest under `ragwell/_contract/`.
Run `uv run --locked python scripts/generate.py --check` to verify generation.
