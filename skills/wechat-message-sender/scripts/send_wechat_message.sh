#!/bin/zsh

emulate -L zsh
set -euo pipefail
umask 077

if (( $# != 2 )); then
  print -r -- '{"ok":false,"sent":false,"error":"exactly two inputs are required: recipient and message"}'
  exit 64
fi

recipient=$1
message=$2
helper_path=${WECHAT_MESSAGE_HELPER:-}
if [[ -z $helper_path ]]; then
  helper_path="/Applications/WeChat Draft Helper.app/Contents/MacOS/WeChatDraftHelper"
fi

if [[ ! -x $helper_path ]]; then
  print -r -- '{"ok":false,"sent":false,"error":"signed WeChat helper is not installed"}'
  exit 69
fi

if [[ -z ${recipient//[[:space:]]/} || $recipient == *$'\n'* ]]; then
  print -r -- '{"ok":false,"sent":false,"error":"recipient must be one non-empty line"}'
  exit 64
fi

if [[ -z ${message//[[:space:]]/} ]]; then
  print -r -- '{"ok":false,"sent":false,"error":"message must not be empty"}'
  exit 64
fi

temporary_root=${TMPDIR:-/tmp}
temporary_dir=$(/usr/bin/mktemp -d "${temporary_root%/}/wechat-message-sender.XXXXXX")
/bin/chmod 700 "$temporary_dir"

cleanup() {
  /usr/bin/find "$temporary_dir" -type f -delete 2>/dev/null || true
  /bin/rmdir "$temporary_dir" 2>/dev/null || true
}
trap cleanup EXIT HUP INT TERM

recipient_file="$temporary_dir/recipient.txt"
message_file="$temporary_dir/message.txt"
print -rn -- "$recipient" > "$recipient_file"
print -rn -- "$message" > "$message_file"
/bin/chmod 600 "$recipient_file" "$message_file"

receipt_root=${WECHAT_MESSAGE_RECEIPT_DIR:-${HOME}/.codex/state/wechat-message-sender}
/bin/mkdir -p "$receipt_root"
/bin/chmod 700 "$receipt_root"
receipt_path="$receipt_root/$(/bin/date -u +%Y%m%dT%H%M%SZ)-$(/usr/bin/uuidgen).json"

set +e
helper_output=$("$helper_path" send-ocr-message "$recipient_file" "$message_file" "$receipt_path" 2>&1)
helper_status=$?
set -e
print -r -- "$helper_output"

if (( helper_status != 0 )) && [[ -e $receipt_path ]]; then
  print -r -- '{"ok":false,"sent":false,"retry_safe":false,"error":"receipt exists after helper error; outcome is uncertain and must not be retried"}'
  exit 75
fi

if (( helper_status == 0 )) && { [[ ! -e $receipt_path ]] || [[ $helper_output != *'"sent":true'* ]] || [[ $helper_output != *'"recipient_verified":true'* ]] || [[ $helper_output != *'"draft_verified":true'* ]]; }; then
  print -r -- '{"ok":false,"sent":false,"retry_safe":false,"error":"helper success evidence or receipt is missing; do not retry automatically"}'
  exit 70
fi

exit $helper_status
