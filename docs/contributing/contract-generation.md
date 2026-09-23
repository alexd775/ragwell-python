# Contract generation

The API's reviewed OpenAPI artifact is vendored under [contracts](../../contracts/README.md). The SDK generator uses that artifact to update public wire types and private generated code; it does not import the API repository. Keep the 26-operation sync/async mapping intact.

Follow the [generation and qualification guide](../generation.md) for the exact review and update steps. Regenerate through `scripts/generate.py`, never by editing `src/ragwell/_generated` manually. A contract change also needs deterministic wire/failure tests, relevant guide/reference updates, and installed-package qualification before release.

For the current public methods, use [clients and resources](../reference/client-and-resources.md).
