# Desktop operations with Peekaboo

These examples target the public 4.4.0 CLI. Check `peekaboo help see`, `peekaboo help click`, and `peekaboo help type` for the installed release before acting. MCP uses its discovered schema, not a mechanical translation of CLI flags.

## Find one exact window

Use the task's app name or bundle identifier; do not assume the frontmost app is the target. `TextEdit` below is appropriate only for a disposable test document.

```sh
peekaboo window list --app TextEdit --json
```

Read the result, select the intended window, and store the returned ID as `CU_WINDOW_ID`. Choose either `--app` or `--pid`, not both; use at most one of `--window-id`, `--window-title`, and `--window-index`. A title/index requires its app/PID owner. Prefer the exact ID when multiple windows or duplicate titles exist.

Create an evidence directory outside the repository and observe that window:

```sh
CU_EVIDENCE=$(mktemp -d "${TMPDIR:-/tmp}/computer-use.XXXXXX")
peekaboo see --app TextEdit --window-id "$CU_WINDOW_ID" \
  --annotate --path "$CU_EVIDENCE/before.png" --json
```

Inspect the actual response structure; the CLI normally wraps fields under `data`. Copy the returned `snapshot_id` into `CU_SNAPSHOT_ID` and the intended actionable field's ID into `CU_ELEMENT_ID`. IDs are opaque: never invent an example value, strip its prefix, or reuse an ID from another capture. View the saved image if a visual decision is needed.

In 4.4.0, `semantic_scope: application_partial`, `snapshot_reusable: false`, or `mutation_targeting_available: false` means the returned semantics cannot authorize an exact-window mutation. An empty or read-only map is a limitation, not evidence of an actionable target. OCR rows are non-actionable; do not pass their IDs to `click`.

For an Accessibility-only diagnosis, the version supports `see --tree --no-screenshot`. This does not verify rendered pixels and is not a way around a required permission or unavailable mutation target.

## Focus a field and type

Run commands one step at a time, inspecting each result:

```sh
peekaboo click --on "$CU_ELEMENT_ID" --snapshot "$CU_SNAPSHOT_ID" --json
```

Observe the exact window again after the click. Confirm the correct editable field is focused and replace `CU_SNAPSHOT_ID` with the newly returned reference. Then, for a scratch field whose entire content may be replaced:

```sh
peekaboo type "computer-use-check" --snapshot "$CU_SNAPSHOT_ID" --clear --json
```

`--clear` replaces content and must not be used on an existing document unless replacement is requested. The CLI `type` command does not accept `--on`; focus by a preceding click and use a fresh snapshot. Printable literal replacement can be confirmed by private Accessibility readback; synthetic typing can remain unverified even after dispatch. Do not use `--accept-dispatched` to disguise that distinction.

Observe again and verify the exact field value or intended rendered result. For multiline content, `type` interprets newline/tab escapes as keys: they can submit a form or move focus. Understand the target before sending them. Do not assume a clipboard paste is harmless or required.

If a standalone key is needed, obtain a fresh snapshot first:

```sh
peekaboo press Tab --snapshot "$CU_SNAPSHOT_ID" --json
```

CLI chords use `cmd+...`, such as `cmd+a`; app/PID-only background raw chords are refused. A fresh exact snapshot is the portable background form across CLI and default MCP. Verify what the key did before issuing the next key. Prefer a named menu or semantic control when it expresses the intended operation more precisely.

## Coordinates, Retina, and multiple displays

Use coordinates only after viewing the current target image. Prefer the exact-window `see` result and its `coordinate_context`; retain the screenshot's original raster dimensions and the capture's logical bounds. Do not assume a Retina ratio of 2, a main-display origin of zero, or that an image viewer preserved original size.

For an image of size `Wpx × Hpx` corresponding to logical rectangle `(x0, y0, Wpt, Hpt)`, an original image pixel `(u, v)` maps to global logical points:

```text
x = x0 + u * Wpt / Wpx
y = y0 + v * Hpt / Hpx
```

This conversion is valid only when those dimensions and bounds describe the same capture, including any crop. ROI pixels are not full-window pixels. Use `coordinate_context.logical_bounds` for the observed viewport; check its relationship to `window_logical_bounds`. Multi-display origins can be negative. Reject out-of-bounds points and recapture if the window moves, resizes, changes displays, or is replaced.

Background CLI `click --at` takes **window-local logical points** by default, even when its ownership comes only from the snapshot. Subtract the full window's logical origin from global points, or pass global points explicitly:

```sh
peekaboo click --snapshot "$CU_SNAPSHOT_ID" --at "$CU_GLOBAL_X,$CU_GLOBAL_Y" --global --json
```

Set both coordinate variables from the verified mapping, not guesses. A background coordinate click requires a fresh exact-window snapshot and must stay within it. A general full-screen screenshot is not an exact-window action receipt. Background coordinates still use Accessibility hit-testing; they are not a guaranteed way to click an opaque canvas.

Where the discovered MCP schema supports it, use `coordinate_space: "image_pixels"` and the returned `coordinate_reference` to let the controller apply the mapping. Do not assume CLI `click` has that flag: its `--at` is in logical points. CLI pixel-focus `type --at ... --coordinate-space image_pixels --snapshot ...` is a separate operation with separate restrictions.

Shared-cursor dragging, moving, and some scrolling require explicit foreground mode. Use it only within the user's desktop-interaction scope and after inspecting the target; do not silently add `--foreground` to a failed background request. Foreground focus changes can interrupt the user. Do not keep issuing global input after concurrent user interaction.

## Verify effects and recover

| Observation | Next action |
| --- | --- |
| `verified: false`, `effect: unverifiable`, partial input, or indeterminate delivery | Inspect the app before retrying; some or all input may already have arrived. |
| `requires_fresh_observation: true` or `SNAPSHOT_STALE` | Obtain a new exact-window snapshot; do not replay the old action blindly. |
| Snapshot not found or wrong producer | Observe again through the intended compatible host. Do not replace an explicit host boundary with an unrelated one. |
| Wrong/moved window, changed process, or ambiguous field | Re-identify the app/window and intended control from fresh evidence. |
| Permission denied | Follow [setup](macos-setup.md); no input bypass or privacy reset. |
| Capture exists but is blank, wallpaper-only, or unrelated | Inspect permission owner and graphical-session/Bridge routing; file existence is not a pass. |
| Sparse browser Accessibility tree | Prefer connected browser DOM tools for page content; retain desktop tooling for native surfaces. |

A post-action screenshot/control value proves more than an input acknowledgment. For a test, use a synthetic field and verify the exact marker; for a real task, verify the user's actual requested outcome. Report observed limitations separately from completed actions. Keep all captures and run-specific details outside this skill's source directory.
