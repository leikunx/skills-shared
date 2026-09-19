# Local cross-project Goal Memory

Use this procedure when starting a goal, recording reusable lessons, or recovering
memory access. The same bundled implementation runs independently on each machine;
no remembered server, machine-specific path, cloud database, or embedding API is
required. Only locally available, registered goal folders are indexed. This does
not synchronize machines or inherit a previous goal's authorization.

## First use and every later goal

1. Locate this installed skill's `scripts/goal_memory_cli.py` and Python 3.11+.
   Use `python3` on macOS/Linux or `py -3` on Windows after checking its version.
   If Python is absent, install a user-level runtime through the machine's supported
   package manager within the setup authority; otherwise report that exact prerequisite.
2. Run the following from the current project, substituting the discovered skill path:

   ```sh
   python3 <skill-dir>/scripts/goal_memory_cli.py ensure --project .
   ```

   This creates an isolated virtual environment, installs pinned dependencies,
   copies immutable server code into private user storage, starts/reuses one
   authenticated loopback HTTP service, registers this project, and adds the scoped
   `goal_memory` Codex MCP connection. Repeated setup reuses the same process;
   changed bundled code upgrades only the authenticated owned service. It starts
   again on a later invocation after a machine reboot. A server holds no agent
   loop, scheduler, or authority to act on projects.
3. Verify `call tools/list` and a real `search_goals` call. Use discovered MCP tools
   when exposed. New registration may need a fresh Codex session; the command-line
   client below talks to the **same MCP endpoint immediately**, so current goal
   learning need not wait for tool-catalog refresh.

   ```sh
   python3 <skill-dir>/scripts/goal_memory_cli.py call tools/list
   python3 <skill-dir>/scripts/goal_memory_cli.py call memory_status
   python3 <skill-dir>/scripts/goal_memory_cli.py call search_goals --arguments-file /path/to/query.json
   ```

   Example query file (use the actual ID returned by `ensure`):

   ```json
   {"query":"iOS release signing provisioning recovery", "project_id":"<registered-project-id>", "limit":5, "exclude_goal_id":"<current-goal-id>"}
   ```

4. Read `get_goal` for 3–5 distinct relevant results, aiming for five. Inspect the
   trigger, changed action, context, status, original evidence and current hash
   integrity. Record which lessons apply, which need an experiment and which are
   rejected. A provisional lesson can inform a bounded experiment; reading it does
   not validate it. Never count duplicate worktrees or unrelated goals to fill the
   quota. Report fewer than three relevant results honestly, then proceed with the
   available evidence. A genuinely unavailable service is an explicit memory gate;
   diagnose startup logs and pursue independent goal work while it is unresolved.

Default private storage is `$XDG_DATA_HOME/goal-memory` or
`~/.local/share/goal-memory` on macOS/Linux, and `%LOCALAPPDATA%/GoalMemory` on
Windows. `GOAL_MEMORY_HOME` or global `--home <path>` selects another location.
Never commit its database, credentials, configuration backups, or private records.
Selected tool results become task context; the service itself uses no external
storage or external embedding service.

## Sources and records

Register another project only when it is within the user's task scope:

```json
{"path":"/absolute/project", "name":"Example", "goals_directory":".codex/goals"}
```

Pass this to `register_project`. Git worktrees share a project identity; their
individual roots remain registered separately. Custom state locations can use an
explicit project-relative `goals_directory`. Never register the whole home or
filesystem root. The service reads only `STATE.md`, `state.md`, and `evolution.json`
under registered goal folders, with file-size limits and symlink/traversal guards.

New goals keep `STATE.md` for execution and `evolution.json` for transferable
knowledge. Create the latter with `save_goal`:

```json
{
  "project_id":"<registered-project-id>",
  "goal_directory":".codex/goals/example",
  "record":{
    "schemaVersion":1,
    "objective":"Make native startup reliable",
    "summary":"A concise observed result",
    "status":"active",
    "tags":["ios","startup"],
    "lessons":[{
      "id":"matching-runtime",
      "title":"Check runtime compatibility before retrying a launch",
      "trigger":"A native app exits during startup",
      "action":"Inspect the crash and compare the runtime's requirements with the app's native configuration.",
      "outcome":"Record the observed gate result here.",
      "status":"provisional",
      "scope":"project",
      "context":["Applies only when crash evidence supports a runtime mismatch"],
      "validation":"Candidate until a later run confirms the improvement.",
      "rollback":"Stop applying this method if later evidence contradicts the diagnosis.",
      "evidence":[{"path":".codex/goals/example/evidence/startup.txt","gate":"native startup","result":"failed"}]
    }],
    "reviews":[],
    "applications":[]
  }
}
```

The example is a schema illustration, not a validated lesson. Create the actual
evidence file first; evidence paths are relative to the registered project. For
artifacts elsewhere, retain a small, redacted goal-local evidence excerpt with
its provenance rather than granting arbitrary filesystem access. Evidence records
contain a gate, result and SHA-256; retrieval reports missing or changed files.
An unrelated update cannot silently reseal changed evidence.

`save_goal` returns a stable `goalId`, `source`, and `revision`. Store them in
STATE.md. To update, pass the current `expected_revision`; a stale writer fails
without overwriting another writer's record. Preserve the goal ID. With multiple
registered worktrees, include `root_path` to select the intended one explicitly.

Lesson statuses are `provisional`, `validated`, `rejected`, and `superseded`.
`validated` requires evidence and a validation account describing the later
confirming run or user-established invariant. The server preserves that recorded
claim; the agent remains responsible for its truth and fresh verification.
`scope: portable` explicitly permits cross-project retrieval. Keep private paths,
account details, tenant context and project-only assumptions out of portable
lesson prose. Cross-project results expose portable lesson text, not private
goal summaries, reviews or application history.

Existing Markdown goals are indexed conservatively from their objective and
Durable/Validated/Lessons learned section. Imported lessons remain provisional
and project-local; headings alone do not prove validation. Review them and save
structured records before widening their scope. Full transcripts and tool logs
are not indexed. Conflicting records sharing a goal ID are excluded until resolved.

## Recording learning and reuse

In `reviews`, record the query, selected goal IDs/revisions, evidence considered,
per-lesson decisions, and any shortfall. Save this review before substantive goal
execution. After a material failure, update it when a different search changes
the next decision. Keep only concise, decision-relevant history.

`record_application` appends one decision or measured outcome to the **new** goal:

```json
{
  "project_id":"<current-project-id>",
  "goal_directory":".codex/goals/current",
  "source_goal_id":"<prior-goal-id>",
  "lesson_id":"<prior-lesson-id>",
  "source_revision":"<revision-read-from-get_goal>",
  "outcome":"test-next",
  "notes":"Why the lesson applies, or which prerequisite still needs checking.",
  "evidence":[],
  "expected_revision":"<current-evolution-json-revision>"
}
```

Outcomes: `applied`, `rejected`, `test-next`, `passed`, `failed`, `inconclusive`.
Measured pass/fail outcomes require evidence. Every append returns a new revision.
Reuse does not change the source goal or automatically promote its lessons. Apply
the skill's later-validation and stable-invariant rules before updating reusable
guidance. Record failures as well as successes; avoid repeated self-confirmation.

The index uses SQLite FTS5 keyword relevance, project context and duplicate-goal
suppression. Search refreshes changed records and removes deleted sources. This
initial version does not claim semantic embedding similarity. Use specific task
terms, technologies and symptoms, and reformulate once when terminology differs.

## Operations and verification

```sh
python3 <skill-dir>/scripts/goal_memory_cli.py status
python3 <skill-dir>/scripts/goal_memory_cli.py call refresh_index
python3 <skill-dir>/scripts/goal_memory_cli.py stop
```

`ensure` can restart a stopped service. Inspect `server.log` and
`dependency-install.log` under the selected private home on failure. Setup never
kills an unverified port owner or overwrites an unrelated `goal_memory` MCP entry.
It retains old installed code and configuration backups. Do not print the private
bearer token or copy it into goal records. The HTTP endpoint binds only to loopback,
requires its bearer token, and rejects browser-origin requests.

For isolated tests, always supply `--home <temporary-directory>` and
`ensure --project <synthetic-project> --no-configure-codex`; stop that service after
the test. Validate new-machine bootstrap, actual MCP calls, relevant cross-project
retrieval, evidence/status preservation, duplicate/stale handling and revision
conflicts before claiming readiness. Test the platform actually available; do
not claim Windows/Linux runtime validation from a Mac-only run.
