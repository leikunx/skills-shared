# Public Codex Skills

The canonical source for reusable Codex skills that contain no company-internal source, tenant details, service URLs, credentials, or customer information.

## Companion repository

The team-only companion is [`leikunx/private`](https://github.com/leikunx/private). Both repositories are synchronized by `scripts/sync-codex-skills.ps1` in this repository. The script installs their `skills/` folders into the normal Codex skills directory without silently replacing a locally modified skill.

## Placement rule

Put a skill here only when its instructions, examples, references, and scripts are safe to share publicly. Put it in the private companion repository when it mentions internal projects, systems, URLs, architecture, tenant behavior, or team-only operating procedures. When uncertain, use `private` first and make a reviewed public extraction later.

## Use on a workstation

Clone this repository next to its private companion, then run:

```powershell
.\scripts\sync-codex-skills.ps1 -Mode Apply -Update
```

The `codex-m365` launcher installed on this workstation performs that sync before starting `codex --yolo`.
