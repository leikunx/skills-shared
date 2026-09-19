# Public sources

Reviewed against the Peekaboo **v4.4.0** public release and Apple documentation on **2026-09-19**. These links are references, not instructions to install from a moving development branch. Recheck current release help before applying version-sensitive flags.

| Source | What it establishes |
| --- | --- |
| [Peekaboo release v4.4.0](https://github.com/openclaw/Peekaboo/releases/tag/v4.4.0) | Versioned binaries and published checksums. |
| [Installation](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/install.md) and [project overview](https://github.com/openclaw/Peekaboo/blob/v4.4.0/README.md) | Homebrew/npm distribution, macOS 15+, Node.js 22+ for npm, separate app/CLI installs. |
| [Permissions](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/permissions.md) | Screen Recording, Accessibility, optional Event Synthesizing, actual Bridge host ownership, and session limitations. |
| [Automation](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/automation.md) | Target selectors, snapshot ownership, background versus foreground behavior, and partial delivery. |
| [Observation](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/commands/see.md) | Exact-window snapshots, actionable versus partial semantics, coordinate context, ROI, and OCR restrictions. |
| [Click](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/commands/click.md), [type](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/commands/type.md), and [press](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/commands/press.md) | Current action flags, focus checks, coordinate units, and verification/retry semantics. |
| [MCP integration](https://github.com/openclaw/Peekaboo/blob/v4.4.0/docs/MCP.md) | Launcher configuration, live schema requirements, and stricter background-only MCP input policy. |
| [Apple: screen and system audio recording](https://support.apple.com/guide/mac-help/control-access-screen-system-audio-recording-mchld6aa7d23/mac) | User-controlled screen-capture grants in Privacy & Security. |
| [Apple: Accessibility access](https://support.apple.com/guide/mac-help/allow-accessibility-apps-to-access-your-mac-mh43185/mac) | User-controlled permission for third-party Accessibility access. |

All examples in this skill are synthetic. Public product names and upstream repositories identify the tools; no employer-specific procedure, internal service, account, or machine mapping is required. Local test results and captured desktop data belong in task-local evidence, not this reference.
