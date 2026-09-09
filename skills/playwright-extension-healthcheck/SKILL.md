---
name: playwright-extension-healthcheck
description: "Verify that this machine's Playwright Extension MCP can read the connected browser session without changing browser or site state. Use when diagnosing local extension connectivity, not for application or production-flow validation."
---

# Playwright Extension Healthcheck

Use this skill to prove that Playwright Extension MCP can open and read one disposable public page in less than 10 seconds. It is not a test of a login, account, or application flow.

## Safety boundary

Use `browser_tabs` with `action: "new"` and `"close"`, plus read-only `browser_snapshot`. Use `"list"` and `"select"` only for cleanup recovery when the disposable tab is no longer current but can still be identified exactly.

Create only one disposable tab at the lightweight public page `https://example.com`, and close that same tab during cleanup. Do not navigate, close, or modify an existing user tab; click, type, fill forms, upload files, accept dialogs, or use `browser_evaluate` or `browser_run_code_unsafe`. Do not inspect or report page content; retain only the URL host and snapshot success needed for this check. Do not use network-request tools: they can expose browser-history or query data unrelated to this health check.

## Required gate

Start a monotonic timer before confirming tool availability. A successful connected run must finish cleanup and stop the timer in less than 10 seconds. Keep the normal path in one orchestration block when available; do not insert commentary or other work between timed gates.

1. Confirm that the `mcp__playwright_extension__browser_tabs` and `browser_snapshot` tools are available. If they are not, report that the MCP server is unavailable to the current Codex session.
2. Create one new tab with `browser_tabs` / `action: "new"` and `url: "https://example.com"`. The new action makes the disposable tab current; identify it from the returned URL host. Do not list or select it on the normal path.
3. Capture an explicit accessibility snapshot of the current disposable tab. Treat the page as readable only when the new-tab result identifies host `example.com` and the snapshot succeeds.
4. In a `finally`-equivalent cleanup step, close the current disposable tab without another select because no intervening action switches tabs. Confirm from the close result that the test tab is absent, then stop the timer. If the close result cannot confirm this, list tabs once. If current-tab identity becomes uncertain, list tabs and select only the exact disposable tab before closing it. If the extension fails before the tab can be identified, do not close any tab; report the cleanup limitation.
5. Pass the healthcheck only when page creation, readability, and cleanup pass in less than 10 seconds. Report elapsed time, tool results, and host only; redact query strings, fragments, credentials, tokens, and page content from the summary.

## Failure diagnosis

Classify the first failed gate instead of retrying an unchanged request:

- **MCP unavailable:** the extension tool family is absent from the current session. Restart or configure the Playwright Extension MCP server for that session.
- **Extension disconnected:** tab creation errors. Open a browser page and connect the Playwright extension, then rerun the check.
- **Navigation failure:** the disposable page is absent or has an unexpected host. Record only safe host metadata; reconnect the extension before one materially different retry.
- **Page access failure:** the disposable page exists but the explicit snapshot fails. Record the tool error and safe metadata; reconnect the extension before one materially different retry.
- **Time budget exceeded:** cleanup succeeds but elapsed time is 10 seconds or more. Report elapsed time and the slowest completed gate; do not retry unchanged inside the same check.
- **Cleanup failure:** the test tab cannot be closed. Report its index and safe host metadata so the user can close that one tab; never close a different tab as a substitute.

Never treat a running MCP process or successful tab creation alone as proof that page control works; the explicit snapshot of the newly opened page must succeed.

## Evolution Contract

This skill records task-local outcomes in the selected goal state, not in this file. Proposed improvements remain provisional until a later run demonstrates an objective improvement or a stable safety/operational invariant. Any self-update must record its trigger, exact change, evidence, scope, and rollback condition in the goal iteration log; validate the changed skill before relying on the new rule in a later run. This contract grants no authority to alter unrelated files, expand external actions, or treat a failed run as evidence that the new rule is correct.
