# Repository Workflow

After changing this repository, validate the affected skill, review the exact diff, commit only the intended files, and push the resulting commit to its configured upstream before handoff. If the push cannot complete safely, report the exact blocker; do not claim the change is published.

## Skill authoring location

Knowledge/reference skills must use `knowledge-<topic>` as both their folder name and SKILL.md frontmatter name. Select the creator's `--kind knowledge` option for this purpose.

Use `$skills-private:skill-creator` for skill creation and updates. Author new skills only in the editable `skills-private/skills/<name>` or `skills-shared/skills/<name>` Git repositories. Default to private; choose shared only when every instruction, example, reference and script is safe to publish publicly. Do not create standalone user/project skills or edit installed plugin caches as source. Resolve checkout locations from the creator's repository configuration or explicit paths; missing checkouts require locating/cloning them, not falling back to `~/.codex/skills`.
