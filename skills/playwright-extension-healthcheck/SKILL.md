---
name: playwright-extension-healthcheck
description: "Verify that this machine's Playwright Extension MCP can read the connected browser session without changing browser or site state. Use when diagnosing local extension connectivity, not for application or production-flow validation."
---

# Playwright Extension Healthcheck

Use this skill to prove that Playwright Extension MCP can control the browser currently connected through the extension. It verifies a disposable tab against a real public website; it is not a test of a login, account, or application flow.

## Safety boundary

Use `browser_tabs` with `action: "list"`, `"new"`, `"select"`, and `"close"`, plus read-only `browser_snapshot` and `browser_evaluate`.

Create only one disposable tab at `https://www.baidu.com`, and close that same tab during cleanup. Do not navigate, close, or modify an existing user tab; click, type, fill forms, upload files, accept dialogs, or use `browser_run_code_unsafe`. Do not inspect or report page content beyond the URL host, title, and readiness needed for this check. Do not use network-request tools: they can expose browser-history or query data unrelated to this health check.

## Required gate

1. Confirm that the `mcp__playwright_extension__browser_tabs`, `browser_snapshot`, and `browser_evaluate` tools are available. If they are not, report that the MCP server is unavailable to the current Codex session.
2. List browser tabs with `browser_tabs` / `action: "list"`, then create one new tab with `browser_tabs` / `action: "new"` and `url: "https://www.baidu.com"`.
3. List tabs again, identify the newly created Baidu tab, and select only that tab. A tool error means the extension is not connected; an absent Baidu tab means navigation failed.
4. Capture an accessibility snapshot of the selected Baidu tab.
5. Run `browser_evaluate` with this read-only function:

   ```js
   () => ({ url: location.href, title: document.title, readyState: document.readyState })
   ```

6. Pass only when the disposable tab was created, its evaluated URL has host `www.baidu.com`, its `readyState` is `interactive` or `complete`, and the snapshot succeeds. Report the tool results, tab count, readiness, and host only; redact query strings, fragments, credentials, tokens, and page content from the summary.
7. In a `finally`-equivalent cleanup step, select and close only the identified disposable Baidu tab. Confirm afterward that no Baidu test tab remains. If the extension fails before the tab can be identified, do not close any tab; report the cleanup limitation.

## Failure diagnosis

Classify the first failed gate instead of retrying an unchanged request:

- **MCP unavailable:** the extension tool family is absent from the current session. Restart or configure the Playwright Extension MCP server for that session.
- **Extension disconnected:** tab listing or tab creation errors. Open a browser page and connect the Playwright extension, then rerun the check.
- **Navigation failure:** the disposable Baidu tab is absent or redirects elsewhere. Record only safe URL/host metadata; reconnect the extension before one materially different retry.
- **Page access failure:** the Baidu tab exists but snapshot or evaluation fails. Record the tool error and safe metadata; reconnect the extension before one materially different retry.
- **Loading page:** evaluation returns `loading`. Wait briefly once, then repeat only the Baidu snapshot/evaluation gates.
- **Cleanup failure:** the test tab cannot be closed. Report its index and safe host metadata so the user can close that one tab; never close a different tab as a substitute.

Never treat a running MCP process, a successful tab listing, or an existing-page snapshot alone as proof that page control works.

## Evolution Contract

This skill records task-local outcomes in the selected goal state, not in this file. Proposed improvements remain provisional until a later run demonstrates an objective improvement or a stable safety/operational invariant. Any self-update must record its trigger, exact change, evidence, scope, and rollback condition in the goal iteration log; validate the changed skill before relying on the new rule in a later run. This contract grants no authority to alter unrelated files, expand external actions, or treat a failed run as evidence that the new rule is correct.
