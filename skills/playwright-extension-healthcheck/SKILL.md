---
name: playwright-extension-healthcheck
description: "Verify that this machine's Playwright Extension MCP can read the connected browser session without changing browser or site state. Use when diagnosing local extension connectivity, not for application or production-flow validation."
---

# Playwright Extension Healthcheck

Use this skill to prove that Playwright Extension MCP can access the browser currently connected through the extension. This is a machine/session health check, not a test of a website, login, account, or application flow.

## Safety boundary

Use only read-only extension tools: `browser_tabs` with `action: "list"`, `browser_snapshot`, and `browser_evaluate`.

Do not navigate, create or close tabs, click, type, fill forms, upload files, accept dialogs, or use `browser_run_code_unsafe`. Do not inspect or report page content beyond the URL, title, and document readiness needed for this check.

## Required gate

1. Confirm that the `mcp__playwright_extension__browser_tabs`, `browser_snapshot`, and `browser_evaluate` tools are available. If they are not, report that the MCP server is unavailable to the current Codex session.
2. List browser tabs with `browser_tabs` / `action: "list"`. A tool error means the extension is not connected; an empty result means no browser page is connected.
3. Without changing the selected tab, capture an accessibility snapshot with `browser_snapshot`.
4. Run `browser_evaluate` with this read-only function:

   ```js
   () => ({ url: location.href, title: document.title, readyState: document.readyState })
   ```

5. Pass only when all three calls succeed, at least one connected tab is listed, and `readyState` is `interactive` or `complete`. Report the tool results, tab count, and readiness only; redact query strings, fragments, credentials, tokens, and page content from the summary.

## Failure diagnosis

Classify the first failed gate instead of retrying an unchanged request:

- **MCP unavailable:** the extension tool family is absent from the current session. Restart or configure the Playwright Extension MCP server for that session.
- **Extension disconnected:** tab listing errors. Open a browser page and connect the Playwright extension, then rerun the check.
- **No connected page:** tab listing succeeds but returns no selectable page. Attach the extension to one non-sensitive browser tab, then rerun.
- **Page access failure:** listing succeeds but snapshot or evaluation fails. Record the tool error and the selected tab's safe metadata; reconnect the extension or select another non-sensitive tab before one materially different retry.
- **Loading page:** evaluation returns `loading`. Wait briefly once, then repeat only the snapshot/evaluation gates.

Never treat a running MCP process or a successful tab listing alone as proof that page control works.

## Evolution Contract

This skill records task-local outcomes in the selected goal state, not in this file. Proposed improvements remain provisional until a later run demonstrates an objective improvement or a stable safety/operational invariant. Any self-update must record its trigger, exact change, evidence, scope, and rollback condition in the goal iteration log; validate the changed skill before relying on the new rule in a later run. This contract grants no authority to alter unrelated files, expand external actions, or treat a failed run as evidence that the new rule is correct.
