---
name: wechat-message-sender
description: Send one explicitly requested message to one exact contact through the signed macOS WeChat desktop app, using local OCR to select and verify the recipient. Use when the user supplies both the recipient name and exact message content and asks Codex to send it now; do not use for drafts, bulk messaging, contact discovery, or unattended campaigns.
---

# WeChat Message Sender

Send exactly one message using exactly two user inputs:

1. `recipient`: the exact visible WeChat contact name.
2. `message`: the exact content to send.

Treat a request containing both values and an explicit instruction to send as authorization for one attempt. Never infer a recipient, broaden a name, alter the message, add a greeting, or reuse authorization for another attempt.

## Preconditions

- Run only on macOS with the official `/Applications/WeChat.app` already signed in.
- Require the signed helper at `/Applications/WeChat Draft Helper.app/Contents/MacOS/WeChatDraftHelper`.
- The helper must have macOS Accessibility and Screen & System Audio Recording permission. Request permission through macOS only; never bypass TCC.
- Do not use unofficial WeChat protocols, hooks, injection, or stored account credentials.

## Execute

Invoke the bundled script with exactly two positional arguments:

```bash
scripts/send_wechat_message.sh "RECIPIENT" "MESSAGE"
```

The script stores inputs only in a mode-`0700` temporary directory, deletes them on exit, and keeps only a mode-`0600` receipt containing hashes. The helper preserves and restores the clipboard. Temporary WeChat-window screenshots are processed locally with Apple Vision and immediately deleted.

The native gate must complete this sequence before Return is allowed:

1. Temporarily move an off-main-display WeChat window into a coordinate-safe main-display frame, preserving its original frame for restoration.
2. Click the left sidebar Search field, replace its contents with the exact recipient, and OCR the bounded result band.
3. Require one exact result, click it, and require the same exact name once in the conversation-title region.
4. Click the editor, paste the exact message, and require one exact OCR match in the editor region.
5. Write the hash-only one-attempt receipt before the single Return event, then restore the original window frame and clipboard.

## Result handling

- Report success only when helper JSON contains `"sent":true`, `"recipient_verified":true`, and `"draft_verified":true`.
- On `"sent":false`, report the helper's bounded error and do not claim delivery.
- If the script reports that a receipt exists after an error, the outcome is uncertain: do not retry because Return may already have occurred.
- Do not take or retain screenshots outside the helper, print OCR text unrelated to the exact target, enumerate contacts, or read chat history.
- Never loop sends. A new message requires a new explicit user request containing both inputs.
