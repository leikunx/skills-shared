#!/usr/bin/env python3
"""Bootstrap or call the local Goal Memory MCP service from any installed skill copy."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil

from goal_memory.core import default_home


def main():
    if sys.version_info < (3, 11):
        candidates = [[shutil.which(name)] for name in ["python3.14", "python3.13", "python3.12", "python3.11", "python3", "python"]]
        if os.name == "nt":
            candidates.append([shutil.which("py"), "-3"])
        else:
            candidates.extend([[str(p)] for p in [Path('/opt/homebrew/bin/python3'), Path('/usr/local/bin/python3')] if p.exists()])
        for candidate in candidates:
            if not candidate[0]:
                continue
            check = subprocess.run([*candidate, "-c", "import sys; print(int(sys.version_info >= (3,11)))"],
                capture_output=True, text=True, timeout=10)
            if check.returncode == 0 and check.stdout.strip() == "1":
                os.execv(candidate[0], [*candidate, str(Path(__file__).resolve()), *sys.argv[1:]])
        raise RuntimeError("No Python 3.11+ runtime found. Install a user-level Python runtime, then rerun ensure.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(default_home()), help="Private per-user data directory; fixtures should use a temporary directory.")
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("ensure", help="Install isolated dependencies, start/reuse the server and register Codex.")
    setup.add_argument("--project", default="", help="Explicit current project root to register.")
    setup.add_argument("--no-configure-codex", action="store_true", help="Use for isolated testing or a non-Codex client.")
    request = sub.add_parser("call", help="Make a real MCP tool call; payload comes from JSON or a file.")
    request.add_argument("tool")
    payload = request.add_mutually_exclusive_group()
    payload.add_argument("--args", default="{}")
    payload.add_argument("--arguments-file")
    for name in ["serve", "status", "stop", "configure-codex", "_call"]:
        sub.add_parser(name)
    args = parser.parse_args()
    home = Path(args.home).expanduser().resolve()
    if args.command == "serve":
        from goal_memory.server import serve
        serve(home)
        return
    if args.command == "_call":
        from goal_memory.client import call
        payload = json.load(sys.stdin)
        result = asyncio.run(call(home, payload["tool"], payload["arguments"]))
    else:
        from goal_memory.bootstrap import configure_codex, ensure, health, python_path, stop
        if args.command == "ensure":
            result = ensure(home, args.project, not args.no_configure_codex)
        elif args.command == "status":
            result = {"running": health(home)}
        elif args.command == "stop":
            result = stop(home)
        elif args.command == "configure-codex":
            result = configure_codex(home)
        elif args.command == "call":
            if not health(home):
                raise ValueError("Service is not ready. Run ensure --project <current-project> first.")
            arguments = json.loads(Path(args.arguments_file).read_text()) if args.arguments_file else json.loads(args.args)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")
            payload = {"tool": args.tool, "arguments": arguments}
            # Never put user records or private authentication material in process arguments.
            completed = subprocess.run([str(python_path(home)), str(Path(__file__).resolve()),
                "--home", str(home), "_call"], input=json.dumps(payload), text=True,
                capture_output=True, timeout=120)
            if completed.returncode:
                raise RuntimeError(completed.stderr.strip())
            result = json.loads(completed.stdout)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
