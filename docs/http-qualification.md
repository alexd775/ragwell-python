# Installed-wheel HTTP qualification

`qualification/http_runner.py` is the SDK-owned real-service runner. Execute it only
against an isolated matching endpoint with pre-provisioned scoped synthetic keys,
projects, a foreign project ID, and synthetic fixtures. It deliberately uses no
browser administration or test-control endpoint and refuses the editable checkout.

The runner records artifact identity and SDK version, exercises both client styles,
proves a foreign project is hidden, uploads and waits, searches cited data, creates
and verifies an export in the sync flow, and deletes its synthetic documents.

The service owner must separately provide controlled jobs/receipts for retry,
cancellation, expired-export, and failed-deletion cases. The runner records that
limitation rather than manufacturing public test controls.

No qualifying endpoint or scoped fixtures were supplied during local implementation,
so this runner has been prepared but not executed. Mock transport tests are not
reported as real-service evidence.
