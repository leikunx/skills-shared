---
name: playwright-extension-healthcheck
description: "Verify that this machine's Playwright Extension MCP can read the connected browser session without changing browser or site state. Use when diagnosing local extension connectivity, not for application or production-flow validation."
---

# Playwright Extension Healthcheck

Use this skill to prove that Playwright Extension MCP can control the browser currently connected through the extension. It verifies a disposable tab against a real public website; it is not a test of a login, account, or application flow.

## Safety boundary

Use `browser_tabs` with `action: "list"`, `"new"`, and `"close"`, plus read-only `browser_snapshot` and `browser_evaluate`. Use `"select"` only for cleanup recovery when the disposable tab is no longer current but can still be identified exactly.

Create only one disposable tab at `https://www.baidu.com`, and close that same tab during cleanup. Do not navigate, close, or modify an existing user tab; click, type, fill forms, upload files, accept dialogs, or use `browser_run_code_unsafe`. Do not inspect or report page content beyond the URL host, title, and readiness needed for this check. Do not use network-request tools: they can expose browser-history or query data unrelated to this health check.

## Required gate

Start a monotonic timer before confirming tool availability. A successful connected run must finish cleanup and stop the timer in less than 30 seconds. Keep the normal path in one orchestration block when available; do not insert commentary or other work between timed gates.

1. Confirm that the `mcp__playwright_extension__browser_tabs`, `browser_snapshot`, and `browser_evaluate` tools are available. If they are not, report that the MCP server is unavailable to the current Codex session.
2. List tabs once to establish the baseline count, then create one new tab with `browser_tabs` / `action: "new"` and `url: "https://www.baidu.com"`. The new action makes the disposable tab current; identify it from that result and the evaluation below. Do not list or select it again on the normal path.
3. Run the accessibility snapshot and this read-only evaluation concurrently:

   ```js
   () => ({ url: location.href, readyState: document.readyState })
   ```

4. Pass the control gates only when the disposable tab was created, its evaluated URL has host `www.baidu.com`, its `readyState` is `interactive` or `complete`, and the snapshot succeeds.
5. In a `finally`-equivalent cleanup step, close the current disposable tab without another select because no intervening action switches tabs. List tabs once afterward to confirm that no Baidu test tab remains, then stop the timer. If current-tab identity becomes uncertain, list tabs and select only the exact disposable tab before closing it. If the extension fails before the tab can be identified, do not close any tab; report the cleanup limitation.
6. Pass the healthcheck only when the control gates and cleanup pass in less than 30 seconds. Report elapsed time, tool results, tab counts, readiness, and host only; redact query strings, fragments, credentials, tokens, and page content from the summary.

## Failure diagnosis

Classify the first failed gate instead of retrying an unchanged request:

- **MCP unavailable:** the extension tool family is absent from the current session. Restart or configure the Playwright Extension MCP server for that session.
- **Extension disconnected:** tab listing or tab creation errors. Open a browser page and connect the Playwright extension, then rerun the check.
- **Navigation failure:** the disposable Baidu tab is absent or redirects elsewhere. Record only safe URL/host metadata; reconnect the extension before one materially different retry.
- **Page access failure:** the Baidu tab exists but snapshot or evaluation fails. Record the tool error and safe metadata; reconnect the extension before one materially different retry.
- **Loading page:** evaluation returns `loading`. Fail this timed run without retrying inside it.
- **Time budget exceeded:** cleanup succeeds but elapsed time is 30 seconds or more. Report elapsed time and the slowest completed gate; do not retry unchanged inside the same check.
- **Cleanup failure:** the test tab cannot be closed. Report its index and safe host metadata so the user can close that one tab; never close a different tab as a substitute.

Never treat a running MCP process, a successful tab listing, or an existing-page snapshot alone as proof that page control works.

## Evolution Contract

This skill records task-local outcomes in the selected goal state, not in this file. Proposed improvements remain provisional until a later run demonstrates an objective improvement or a stable safety/operational invariant. Any self-update must record its trigger, exact change, evidence, scope, and rollback condition in the goal iteration log; validate the changed skill before relying on the new rule in a later run. This contract grants no authority to alter unrelated files, expand external actions, or treat a failed run as evidence that the new rule is correct.
