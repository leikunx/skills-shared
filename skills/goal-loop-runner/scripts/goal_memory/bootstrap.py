"""Portable, idempotent per-user setup. No remembered paths or global Python packages."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
import uuid

from .core import Memory, atomic_json, now, read_bytes


def python_path(home: Path) -> Path:
    return home / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def check_process_running(pid: int):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid < 1:
        raise ValueError("Invalid setup-owner PID.")
    if os.name != "nt":
        os.kill(pid, 0)
        return
    # os.kill(pid, 0) can call TerminateProcess on Windows; use query-only handles.
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER: no such process
            raise ProcessLookupError(pid)
        raise OSError(error, "Cannot establish setup-owner liveness")
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            raise OSError(ctypes.get_last_error(), "Cannot query setup-owner exit code")
        if code.value != 259:  # STILL_ACTIVE
            raise ProcessLookupError(pid)
    finally:
        kernel.CloseHandle(handle)


def health(home: Path):
    path = home / "server.json"
    if not path.exists():
        return None
    config = json.loads(read_bytes(path))
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, message, headers, newurl):
            return None
    try:
        request = Request(f'http://127.0.0.1:{config["port"]}/health',
            headers={"Authorization": "Bearer " + config["token"]})
        with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=2) as response:
            result = json.load(response)
        if result.get("service") != "goal-memory" or result.get("instanceId") != config["instanceId"]:
            raise ValueError("The endpoint is not this installation's Goal Memory service.")
        return result
    except (URLError, TimeoutError, ConnectionError):
        return None


@contextmanager
def setup_lock(home: Path):
    path = home / "bootstrap.lock"
    for attempt in range(2):
        try:
            path.mkdir()
            atomic_json(path / "owner.json", {"pid": os.getpid(), "at": now()})
            break
        except FileExistsError:
            try:
                owner = json.loads(read_bytes(path / "owner.json"))
                check_process_running(owner["pid"])
            except ProcessLookupError:
                path.rename(home / ("stale-bootstrap-" + uuid.uuid4().hex))
                continue
            except (OSError, ValueError, KeyError):
                pass
            raise RuntimeError("Another setup owns bootstrap.lock; inspect its owner instead of starting a duplicate.")
    else:
        raise RuntimeError("Could not claim the setup lock.")
    try:
        yield
    finally:
        shutil.rmtree(path)


def source_release(home: Path) -> tuple[str, Path]:
    scripts = Path(__file__).resolve().parents[1]
    files = [scripts / "goal_memory_cli.py", *sorted((scripts / "goal_memory").glob("*.py")),
             scripts / "goal_memory/requirements.txt"]
    hasher = hashlib.sha256()
    for source in files:
        hasher.update(str(source.relative_to(scripts)).encode())
        hasher.update(source.read_bytes())
    revision = hasher.hexdigest()[:20]
    target = home / "releases" / revision
    for source in files:
        destination = target / source.relative_to(scripts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != source.read_bytes():
            raise RuntimeError("An immutable installed release was modified.")
        if not destination.exists():
            shutil.copy2(source, destination)
    return revision, target


def configure_codex(home: Path, executable: str = "codex") -> dict:
    """Use the supported CLI to add the endpoint, then set its private header in TOML."""
    import tomlkit
    config = json.loads(read_bytes(home / "server.json"))
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    path = codex_home / "config.toml"
    before = path.read_text() if path.exists() else ""
    document = tomlkit.parse(before)
    url = f'http://127.0.0.1:{config["port"]}/mcp'
    entry = document.get("mcp_servers", {}).get("goal_memory")
    if entry is not None and entry.get("url") != url:
        raise ValueError("An unrelated goal_memory MCP entry already exists; it was not replaced.")
    expected_header = "Bearer " + config["token"]
    if entry is not None and entry.get("http_headers", {}).get("Authorization") == expected_header:
        return {"configured": True, "changed": False, "server": "goal_memory"}
    backups = home / "config-backups"
    backups.mkdir(exist_ok=True)
    if path.exists():
        backup = backups / ("config-" + uuid.uuid4().hex + ".toml")
        backup.write_text(before)
        if os.name != "nt":
            backup.chmod(0o600)
    if entry is None:
        result = subprocess.run([executable, "mcp", "add", "goal_memory", "--url", url],
            capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError("Codex could not register goal_memory. Service remains available through the CLI.")
    current = path.read_text()
    document = tomlkit.parse(current)
    entry = document["mcp_servers"]["goal_memory"]
    if entry.get("url") != url:
        raise RuntimeError("MCP configuration changed during setup; no header was written.")
    if "http_headers" not in entry:
        entry["http_headers"] = tomlkit.table()
    entry["http_headers"]["Authorization"] = expected_header
    entry["startup_timeout_sec"] = 20
    entry["tool_timeout_sec"] = 60
    temporary = path.with_name(".goal-memory-config-" + uuid.uuid4().hex)
    try:
        with temporary.open("x") as output:
            if os.name != "nt":
                os.fchmod(output.fileno(), 0o600)
            output.write(tomlkit.dumps(document))
        if path.read_text() != current:
            raise RuntimeError("Codex configuration changed concurrently; retry scoped setup.")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return {"configured": True, "changed": True, "server": "goal_memory",
        "pickup": "Use the bundled MCP client immediately; a new Codex session may be needed for tool discovery."}


def stop(home: Path) -> dict:
    live = health(home)
    if not live:
        return {"stopped": False, "reason": "No authenticated running service found."}
    os.kill(live["pid"], signal.SIGTERM)
    for _ in range(30):
        if not health(home):
            return {"stopped": True}
        time.sleep(0.1)
    raise RuntimeError("The owned service did not stop; inspect its log.")


def ensure(home: Path, project: str = "", configure: bool = True) -> dict:
    if sys.version_info < (3, 11):
        raise RuntimeError("Goal Memory needs Python 3.11 or later (python3 on Unix; py -3 on Windows).")
    memory = Memory(home)
    with setup_lock(home):
        revision, release = source_release(home)
        python = python_path(home)
        if not python.exists():
            subprocess.run([sys.executable, "-m", "venv", str(home / "venv")], check=True, timeout=120)
        requirements = release / "goal_memory/requirements.txt"
        fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
        installed = home / "dependencies.json"
        if not installed.exists() or json.loads(read_bytes(installed)).get("sha256") != fingerprint:
            with (home / "dependency-install.log").open("w") as output:
                result = subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "-r", str(requirements)], stdout=output, stderr=subprocess.STDOUT, timeout=600)
            if result.returncode:
                raise RuntimeError(f"Dependency setup failed; inspect {home / 'dependency-install.log'}.")
            atomic_json(installed, {"sha256": fingerprint, "at": now()})
        live = health(home)
        path = home / "server.json"
        if path.exists():
            config = json.loads(read_bytes(path))
        else:
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            config = {"port": port, "token": secrets.token_urlsafe(32), "instanceId": str(uuid.uuid4())}
        if live and live["release"] != revision:
            stop(home)
            live = None
        config["release"] = revision
        atomic_json(path, config)
        if not live:
            # An occupied address must never cause us to control another process.
            with socket.socket() as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    probe.bind(("127.0.0.1", config["port"]))
                except OSError as exc:
                    raise RuntimeError("The configured loopback port is occupied by an unverified process.") from exc
            argv = [str(python), str(release / "goal_memory_cli.py"), "--home", str(home), "serve"]
            options = {"start_new_session": True} if os.name != "nt" else {
                "creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
            with (home / "server.log").open("a") as output:
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                    close_fds=True, **options)
            for _ in range(100):
                live = health(home)
                if live:
                    break
                if child.poll() is not None:
                    raise RuntimeError(f"Service exited; inspect {home / 'server.log'}.")
                time.sleep(0.2)
            else:
                child.terminate()
                raise RuntimeError("Service did not become ready within 20 seconds; inspect server.log.")
        registration = memory.register_project(project) if project else None
        result = {"service": live, "project": registration, "home": str(home)}
        if configure:
            executable = shutil.which("codex")
            if executable:
                # Run configuration in the isolated environment containing tomlkit.
                output = subprocess.run([str(python), str(release / "goal_memory_cli.py"), "--home", str(home),
                    "configure-codex"], capture_output=True, text=True, timeout=45)
                if output.returncode:
                    raise RuntimeError(output.stderr.strip() or "Scoped Codex registration failed.")
                result["codex"] = json.loads(output.stdout)
            else:
                result["codex"] = {"configured": False, "reason": "Codex CLI is unavailable; use the bundled MCP client."}
        return result
