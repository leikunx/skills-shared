import asyncio
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import httpx
    from goal_memory.client import call
    HAVE_SDK = True
except ImportError:
    HAVE_SDK = False
from goal_memory.bootstrap import configure_codex, health
from goal_memory.core import Memory, atomic_json


@unittest.skipUnless(HAVE_SDK, "Run with the installed Goal Memory virtual environment for real MCP transport checks.")
class TransportTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.root = Path(self.scratch.name)
        self.home = self.root / "memory"
        self.memory = Memory(self.home)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]
        self.config = {"port": port, "token": secrets.token_urlsafe(32), "instanceId": "test", "release": "test"}
        atomic_json(self.home / "server.json", self.config)
        self.log = (self.home / "test-server.log").open("w")
        self.process = subprocess.Popen([sys.executable, str(Path(__file__).resolve().parents[1] / "goal_memory_cli.py"),
            "--home", str(self.home), "serve"], stdout=self.log, stderr=self.log)
        for _ in range(100):
            if health(self.home): break
            if self.process.poll() is not None: self.fail("MCP server exited during test setup")
            time.sleep(0.05)
        else: self.fail("MCP server did not become ready")

    def tearDown(self):
        self.process.terminate(); self.process.wait(timeout=10)
        self.log.close(); self.scratch.cleanup()

    async def test_real_mcp_tools_and_revision_conflict(self):
        tools = await call(self.home, "tools/list", {})
        self.assertIn("search_goals", [t["name"] for t in tools["tools"]])
        project = self.root / "project"; project.mkdir()
        p = await call(self.home, "register_project", {"path": str(project)})
        args = {"project_id": p["id"], "goal_directory": ".codex/goals/current",
                "record": {"schemaVersion": 1, "objective": "Check MCP transport", "lessons": []}}
        first = await call(self.home, "save_goal", args)
        args["expected_revision"] = first["revision"]
        one = {**args, "record": {**args["record"], "summary": "writer one"}}
        two = {**args, "record": {**args["record"], "summary": "writer two"}}
        results = await asyncio.gather(call(self.home, "save_goal", one), call(self.home, "save_goal", two), return_exceptions=True)
        self.assertEqual(sum(isinstance(r, dict) for r in results), 1)
        final = await call(self.home, "get_goal", {"goal_id": first["goalId"], "requesting_project_id": p["id"]})
        self.assertIn(final["summary"], ["writer one", "writer two"])

    async def test_http_rejects_unauthenticated_and_browser_origin(self):
        url = f'http://127.0.0.1:{self.config["port"]}/health'
        async with httpx.AsyncClient(trust_env=False) as client:
            self.assertEqual((await client.get(url)).status_code, 401)
            headers = {"Authorization": "Bearer " + self.config["token"]}
            self.assertEqual((await client.get(url, headers=headers)).status_code, 200)
            self.assertEqual((await client.get(url, headers={**headers, "Origin": "https://example.test"})).status_code, 401)

    async def test_codex_header_update_preserves_other_configuration(self):
        config_root = self.root / "codex"; config_root.mkdir()
        path = config_root / "config.toml"
        content = '# keep this comment\nmodel = "example"\n[mcp_servers.goal_memory]\nurl = "http://127.0.0.1:%d/mcp"\n' % self.config["port"]
        path.write_text(content)
        with patch.dict(os.environ, {"CODEX_HOME": str(config_root)}):
            self.assertTrue(configure_codex(self.home)["changed"])
            self.assertFalse(configure_codex(self.home)["changed"])
            self.assertIn('# keep this comment\nmodel = "example"', path.read_text())
            path.write_text(content.replace('/mcp', '/unrelated'))
            with self.assertRaises(ValueError): configure_codex(self.home)
            self.assertEqual(path.read_text(), content.replace('/mcp', '/unrelated'))


if __name__ == "__main__": unittest.main()
