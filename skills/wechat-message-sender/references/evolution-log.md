# WeChat Message Sender Evolution Log

## 2026-09-06 — Select an exact search result with the verified Search input

- **Trigger:** On WeChat 4.x, clicking an OCR-matched lower sidebar occurrence of an exact mixed-script contact did not open a conversation, even though the Search input and candidate text were recognized exactly.
- **Exact change:** Locate the Search control with OCR instead of fixed percentages; after the exact query and one exact left-column candidate are verified, refocus the exact Search input and use Return to select. Keep the editor empty until the selected conversation title is independently verified, and retain a separate receipt-before-Return gate for sending.
- **Evidence:** The no-send selector returned `recipient_verified:true` for `德扑-ofcc`; the subsequent authorized run returned `recipient_verified:true`, `draft_verified:true`, and `sent:true`; the receipt hashes matched both inputs and replay with the same receipt was rejected before UI work. Twelve helper safety tests and Playwright Extension connectivity checks passed.
- **Scope:** Official macOS WeChat with the signed local helper, exact recipient input, one exact left-column candidate, and exact post-selection title verification. This does not permit fuzzy recipient selection, retries after a receipt exists, or any message to be staged before selection.
- **Rollback condition:** Restore the prior selection strategy if a future no-send gate shows that Return can leave the verified Search field or select a nonmatching title; never weaken the post-selection exact-title requirement.

## 2026-09-06 — Recognize separate WeChat search-result surfaces

- **Trigger:** Searching for `ms尼欧` placed the only exact candidate in a separate WeChat-owned layer-3 popup while the main window held the query; the top of the main sidebar also rendered a second same-text UI element outside the actual Search input.
- **Exact change:** Prefer exactly one exact target in a bounded non-main WeChat search surface, falling back to the main left column only when no popup target exists. Restrict Search-input uniqueness to the OCR-located left control region so same-text UI elsewhere does not create a false ambiguity. Keep verified-input Return selection and exact post-selection title verification unchanged.
- **Evidence:** After the geometry correction, three consecutive no-send selections returned `recipient_verified:true`. A later explicitly authorized run returned `recipient_verified:true`, `draft_verified:true`, and `sent:true`; its mode-`0600` receipt hashes matched both inputs, and replay with that receipt was rejected before UI work. Thirteen helper safety tests passed.
- **Scope:** Official macOS WeChat where search results may render in a separate process-owned popup. Every accepted candidate must remain an exact, unique target match, and the main conversation title must independently match after Return.
- **Rollback condition:** Disable popup preference or revise the bounded Search-input region if a no-send run produces a nonmatching title, multiple exact popup targets, or a verified Search input outside the accepted control region.
