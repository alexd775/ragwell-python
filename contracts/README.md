# Vendored machine contract

The SDK uses artifact version `2026-09-19.1` from
`contracts/2026-09-19.1/`. Its exact identity is the digest, not the version alone.

- Reviewed producer snapshot on 2026-09-21: API commit
  `e8055ae5d9b92fe8f1f73e437b5a9b3e79ff05d8`.
- Machine SHA-256:
  `8e05de4ae0f3aa76261e97ad07be1fc77756f317c3e2c20ab2be3efb2cb6db90`.
- Canonical API SHA-256:
  `57a1f942f7ca8b89186753a20320588b57e2425663b8529b36037066c02328bb`.
- Inventory: 26 operations, including 25 bearer operations and public upload policy.

The 2026-09-21 refresh changes only the description of the deletion operation's
503 response from “A required dependency is unavailable.” to “Service Unavailable”.
The previous machine digest was
`06d0efac740946c21f0ddfa3d873e2197cf4924487ed512d08b8c2fd824978bd`.
Wire definitions and generated code are unchanged; the canonical producer digest
also reflects browser API changes outside the machine projection.

Generation, tests, builds and installation need no backend checkout. The wheel
includes the reviewed OpenAPI and manifest under `ragwell/_contract/`; the real
HTTP runner compares these to the running service's public OpenAPI projection.

Run `uv run --locked python scripts/generate.py --check` to verify the digest,
manifest inventory and deterministic generated output. Vendoring does not imply
publication or hosted deployment.
