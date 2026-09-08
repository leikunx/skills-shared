# Shared Codex Skills Marketplace

The canonical Git marketplace for reusable Codex skills that contain no company-internal source, tenant details, service URLs, credentials, or customer information.

## Companion repository

The team-only companion is [`leikunx/skills-private`](https://github.com/leikunx/skills-private). The installable plugin is `skills-shared`, declared in `.agents/plugins/marketplace.json`; its `.codex-plugin/` manifest and `skills/` directory are at this repository's root.

## Placement rule

Put a skill here only when its instructions, examples, references, and scripts are safe to share publicly. Put it in the private companion repository when it mentions internal projects, systems, URLs, architecture, tenant behavior, or team-only operating procedures. When uncertain, use `private` first and make a reviewed public extraction later.

## Engineering review

- `$skills-shared:architecture-health-review` produces architecture and production-readiness findings backed by executable receipts, counter-searches, and explicit blast-radius gates. It is read-only unless implementation is separately requested.

## Use on a workstation

Register both Git marketplaces once:

```powershell
codex plugin marketplace add leikunx/skills-shared --ref main
codex plugin marketplace add leikunx/skills-private --ref main
codex plugin add skills-shared@skills-shared
codex plugin add skills-private@skills-private
```

For later updates, run `codex-m365`. Before it refreshes and reinstalls the plugins, it safely commits and pushes non-ignored changes in this repository and its private companion. It blocks likely secret files, merge divergence, missing upstream branches, or failed Git operations rather than overwriting or force-pushing.
