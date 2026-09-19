# macOS setup and permissions

Use this reference when discovering a controller, installing Peekaboo, connecting MCP, or diagnosing permissions. Public upstream sources and their versions are in [sources.md](sources.md).

## Discover before installing

```sh
sw_vers
command -v peekaboo
peekaboo --version
peekaboo permissions status --all-sources --json
```

Run the Peekaboo commands only if discovery found the binary. The 4.4.0 release requires macOS 15 or later; its npm launcher requires Node.js 22 or later. An available shell is enough to invoke the CLI: an MCP connection is optional. A non-macOS runtime must use a separately authorized Mac execution host; installing this skill does not create one.

For an authorized setup, the upstream Homebrew path is:

```sh
brew install openclaw/tap/peekaboo
peekaboo --version
```

Do not install or upgrade globally merely to answer a capability question. For temporary validation, a versioned official GitHub release can be extracted outside the repository. Verify the archive against the release's SHA-256 checksum before executing it. Keep downloaded executables and evidence out of the skill. Do not strip quarantine or disable Gatekeeper to overcome a refusal. The signed Mac app and CLI are separate installs; installing the menu-bar app does not necessarily add `peekaboo` to `PATH`.

Basic `see`, `click`, `type`, and permission checks use the local tool implementation and do not need an AI-provider API key. The separate `agent` and image-analysis features may require a provider and can incur cost; they are not prerequisites for this skill.

## Identify the permission owner

`peekaboo permissions status --all-sources --json` distinguishes the selected Bridge host from the local CLI. Grant permissions to the reported execution host, not an arbitrary terminal with a similar name. A daemon or menu-bar host can be the actual capture/input process. Installation, signing, or binary-path changes can invalidate earlier grants.

| Capability | Permission and diagnostic |
| --- | --- |
| Screen/window pixels | Screen Recording, shown as **Screen & System Audio Recording** in current System Settings. |
| Accessibility inspection and semantic actions | **Accessibility** under Privacy & Security. |
| Synthetic keyboard and some pointer operations | Peekaboo's **Event Synthesizing** status; this is not the same as granting Input Monitoring. |
| AppleScript controlling another app | May separately require **Automation** for that scripting route. Peekaboo itself does not require Apple Events Automation permission. |

The user controls grants in **System Settings → Privacy & Security**. These supported commands can request a prompt or show instructions when setup is authorized:

```sh
peekaboo permissions grant
peekaboo permissions request screen-recording
peekaboo permissions request accessibility
peekaboo permissions request event-synthesizing
```

These commands do not all target the same process: in 4.4.0, `request screen-recording` and `request accessibility` request access for the **local CLI**. `request event-synthesizing` follows the selected runtime/Bridge host unless `--no-remote` is supplied. For a Bridge Screen Recording or Accessibility denial, use that host's permission onboarding or the matching System Settings entry; requesting local CLI access does not fix the host's grant.

They do not silently grant access. Explain the exact missing permission and execution host, let the user complete the system interaction, then rerun status and a scoped observation. Do not automate consent clicks, edit TCC databases, reset all permissions, or add unrelated Full Disk Access. If the request is only to write documentation, document the missing permission instead of making completion depend on a grant.

For app-launched runners, SSH, or background sessions, prefer the supported Bridge host in the logged-in graphical session. A successful permission preflight or image file alone can still yield wallpaper/redacted content. Inspect the actual target pixels. Do not switch to `--no-remote` as a universal repair: snapshots belong to their producing host, and a different local process may lack both the GUI context and the snapshot. Diagnose host availability, version compatibility, ownership, and permissions first. Stop only daemons started for the task, never a pre-existing shared host.

## Optional MCP connection

Use the client's supported MCP setup interface and preserve unrelated servers. For clients accepting this JSON structure, a pinned npm launcher is:

```json
{
  "mcpServers": {
    "peekaboo": {
      "command": "npx",
      "args": ["-y", "@steipete/peekaboo@4.4.0", "mcp"]
    }
  }
}
```

For a client using another configuration format, translate through its current supported interface rather than pasting this into an arbitrary settings file. An installed binary can instead be the command, with `mcp` as its argument. Resolve its real path on that machine. Do not add credentials to the example.

Reconnect or start a fresh client session, inspect the live tool catalog, and run a permission/observation call before claiming the connection works. Exact MCP tool names and schemas must come from discovery. Peekaboo's default background-only MCP policy is stricter than the direct CLI: typing and raw key presses require a fresh exact non-dialog snapshot, and typing cannot combine that snapshot with competing app/PID/window selectors. Some foreground pointer tools are absent from that catalog. Do not turn off policy merely to make a CLI example fit MCP.

## Native fallback boundaries

For a screenshot-only task, macOS ships `/usr/sbin/screencapture`. After obtaining a current WindowServer ID for the requested window, an explicit-window capture is:

```sh
/usr/sbin/screencapture -x -l "$CU_WINDOW_ID" "$CU_EVIDENCE/window.png"
```

Set both variables from task-local discovery first. This still needs permission and a valid graphical session. View the file and verify its content; it does not supply element IDs or mouse control. Screenshot shadow, scaling, crop, and coordinate conventions can differ from another controller, so do not feed its pixels directly into unrelated input tools.

An app's documented AppleScript dictionary can be useful for app-specific operations when already authorized. `System Events` UI scripting has its own Accessibility/Automation prerequisites. Do not confuse AppleScript availability with permission to control every app, or use it to bypass a controller's target or permission refusal. Raw coordinate injectors require the same observation and verification discipline and are not the default recovery path.
