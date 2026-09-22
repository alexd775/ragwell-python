# Vendored machine contract

The development SDK uses artifact `2026-09-22.1` from `contracts/2026-09-22.1/`.
It adds typed optional Jev reranking and result scores to search. The inventory
remains 26 operations; project credential management is browser-only.

- Producer: RAG API commit
  `a4ea919b413eb4223f3f7874b48a27d4621a3bfb`, 2026-09-22.
- Machine SHA-256: `edd7aa3d26def4a1dcafceee4af2b9d4ae5a0d2affde52719ce03e904cc5a509`.
- Canonical SHA-256: `4e0922172d2c8f9c2696a46153b20bdf6d48d6df6862421f5403da59de283151`.

The prior `2026-09-19.1` artifact remains preserved for the published 0.1.0 release.
This SDK change is not yet a published release and does not inherit the old
artifact's qualification. The deployed beta projection matched the new machine
digest during installed-wheel validation; normal tests remain offline and synthetic.

Generation, tests, builds and installation require no backend checkout. The wheel
includes the selected OpenAPI and manifest under `ragwell/_contract/`. Run
`uv run --locked python scripts/generate.py --check` to verify deterministic output.
