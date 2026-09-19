import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from goal_memory.core import Memory


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.root = Path(self.scratch.name)
        self.memory = Memory(self.root / "memory")
        self.a, self.b = self.root / "alpha", self.root / "beta"
        self.a.mkdir(); self.b.mkdir()
        self.pa = self.memory.register_project(str(self.a))["id"]
        self.pb = self.memory.register_project(str(self.b))["id"]

    def tearDown(self):
        self.scratch.cleanup()

    def record(self, root, project, name, *, scope="portable", status="validated", objective="iOS release signing recovery"):
        folder = root / ".codex/goals" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "gate.txt").write_text("Independent later-run signing verification passed.\n")
        record = {"schemaVersion": 1, "goalId": name, "objective": objective, "tags": ["ios", "signing"],
            "lessons": [{"id": "signing", "title": "Verify provisioning before signing", "trigger": "iOS release signing failed",
                "action": "Inspect provisioning expiry, then rerun the native signing gate.", "outcome": "Later run passed.",
                "status": status, "scope": scope, "validation": "Later independent run confirmed the gate.",
                "evidence": [{"path": str((folder / 'gate.txt').relative_to(root)), "gate": "native signing", "result": "passed"}]}]}
        return self.memory.save_goal(project, str(folder.relative_to(root)), record)

    def test_cross_project_retrieval_and_status_are_preserved(self):
        for i in range(5): self.record(self.b, self.pb, f"past-{i}")
        self.record(self.b, self.pb, "private", scope="project")
        self.record(self.b, self.pb, "idea", status="provisional")
        result = self.memory.search_goals("iOS signing provisioning", self.pa)
        self.assertEqual(len(result["goals"]), 5)
        self.assertEqual(len({g["goalId"] for g in result["goals"]}), 5)
        self.assertNotIn("private", {g["goalId"] for g in result["goals"]})
        lesson = self.memory.get_goal("idea", self.pa)["lessons"][0]
        self.assertEqual(lesson["status"], "provisional")
        self.assertTrue(lesson["evidenceCurrent"])
        with self.assertRaises(ValueError): self.memory.get_goal("private", self.pa)

    def test_shortfall_exclusion_and_no_irrelevant_padding(self):
        self.record(self.a, self.pa, "current")
        self.record(self.b, self.pb, "previous")
        result = self.memory.search_goals("iOS signing", self.pa, exclude_goal_id="current")
        self.assertEqual([g["goalId"] for g in result["goals"]], ["previous"])
        self.assertIsNotNone(result["shortfall"])
        self.assertEqual(self.memory.search_goals("astronomy telescopes", self.pa)["count"], 0)

    def test_duplicate_goals_do_not_count_as_independent_experience(self):
        self.record(self.b, self.pb, "original")
        shutil.copytree(self.b / ".codex/goals/original", self.b / ".codex/goals/copied")
        result = self.memory.search_goals("iOS signing", self.pa)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["index"]["distinctGoals"], 1)

    def test_conflicting_duplicate_is_not_selected(self):
        self.record(self.b, self.pb, "original")
        folder = self.b / ".codex/goals/copied"
        shutil.copytree(self.b / ".codex/goals/original", folder)
        p = folder / "evolution.json"; value = json.loads(p.read_text())
        value["objective"] = "A different objective"; p.write_text(json.dumps(value))
        result = self.memory.search_goals("iOS signing", self.pa)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["index"]["conflicts"], ["original"])

    def test_incremental_refresh_and_deleted_sources(self):
        self.record(self.b, self.pb, "old")
        self.assertEqual(self.memory.refresh()["changedGoals"], 0)
        shutil.rmtree(self.b / ".codex/goals/old")
        result = self.memory.search_goals("iOS signing", self.pa)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["index"]["changedGoals"], 1)

    def test_modified_evidence_is_not_current(self):
        receipt = self.record(self.b, self.pb, "old")
        (self.b / ".codex/goals/old/gate.txt").write_text("Verification was withdrawn.")
        lesson = self.memory.get_goal("old", self.pa)["lessons"][0]
        self.assertFalse(lesson["evidenceCurrent"])
        self.assertEqual(lesson["evidence"][0]["integrity"], "changed")
        path = self.b / ".codex/goals/old/evolution.json"
        record = json.loads(path.read_text()); record["summary"] = "An unrelated update"
        with self.assertRaises(ValueError):
            self.memory.save_goal(self.pb, ".codex/goals/old", record, receipt["revision"])

    def test_application_evidence_is_rechecked_after_artifact_changes(self):
        source = self.record(self.b, self.pb, "source")
        current = self.memory.save_goal(self.pa, ".codex/goals/current",
            {"schemaVersion": 1, "objective": "Verify iOS signing", "lessons": []})
        evidence = self.a / ".codex/goals/current/result.txt"; evidence.write_text("pass")
        outcome = self.memory.record_application(self.pa, ".codex/goals/current", "source", "signing",
            source["revision"], "passed", "Independent run", [{"path": str(evidence.relative_to(self.a)),
            "gate": "native signing", "result": "passed"}], current["revision"])
        evidence.write_text("withdrawn")
        record = self.memory.get_goal(outcome["goalId"], self.pa)
        self.assertEqual(record["applications"][0]["evidence"][0]["integrity"], "changed")

    def test_compare_and_swap_preserves_existing_record(self):
        receipt = self.record(self.a, self.pa, "same")
        path = self.a / ".codex/goals/same/evolution.json"
        value = json.loads(path.read_text()); value["summary"] = "new summary"
        with self.assertRaises(ValueError):
            self.memory.save_goal(self.pa, ".codex/goals/same", value)
        self.assertEqual(json.loads(path.read_text())["summary"], "")
        self.memory.save_goal(self.pa, ".codex/goals/same", value, receipt["revision"])
        self.assertEqual(json.loads(path.read_text())["summary"], "new summary")

    def test_reuse_writes_to_current_goal_without_promoting_source(self):
        source = self.record(self.b, self.pb, "source", status="provisional")
        current = self.memory.save_goal(self.pa, ".codex/goals/current",
            {"schemaVersion": 1, "objective": "Verify iOS signing", "lessons": []})
        result = self.memory.record_application(self.pa, ".codex/goals/current", "source", "signing",
            source["revision"], "test-next", "Needs validation in this project", [], current["revision"])
        record = self.memory.get_goal(result["goalId"], self.pa)
        self.assertEqual(record["applications"][0]["outcome"], "test-next")
        self.assertEqual(self.memory.get_goal("source", self.pa)["lessons"][0]["status"], "provisional")

    def test_index_rebuild_preserves_source_records(self):
        receipt = self.record(self.b, self.pb, "persist")
        with self.memory.connect(write=True) as db:
            db.execute("DELETE FROM search"); db.execute("DELETE FROM documents")
        self.memory.refresh()
        self.assertEqual(self.memory.get_goal("persist", self.pa)["revision"], receipt["revision"])

    def test_legacy_state_is_not_assumed_portable_or_validated(self):
        folder = self.b / ".codex/goals/legacy"; folder.mkdir(parents=True)
        (folder / "STATE.md").write_text("# Repair signing\n- Objective: iOS signing\n## Durable lessons\n- Check provisioning expiry.\n## Logs\nSECRET_LOG_SHOULD_NOT_BE_INDEXED\n")
        self.assertEqual(self.memory.search_goals("signing", self.pa)["count"], 0)
        own = self.memory.search_goals("signing", self.pb)
        self.assertEqual(own["goals"][0]["lessons"][0]["status"], "provisional")
        self.assertEqual(self.memory.search_goals("SECRET_LOG_SHOULD_NOT_BE_INDEXED", self.pb)["count"], 0)

    def test_empty_legacy_lessons_do_not_fill_the_review_quota(self):
        folder = self.b / ".codex/goals/empty"; folder.mkdir(parents=True)
        (folder / "STATE.md").write_text("# Goal Loop State\n- **Objective:** Improve signing\n## Durable lessons\n- None.\n")
        result = self.memory.search_goals("signing", self.pb)
        self.assertEqual(result["count"], 0)
        self.assertIsNotNone(result["shortfall"])

    def test_paths_and_symlinks_cannot_escape_registered_roots(self):
        record = {"schemaVersion": 1, "objective": "Example", "lessons": []}
        with self.assertRaises(ValueError): self.memory.save_goal(self.pa, "../outside", record)
        with self.assertRaises(ValueError): self.memory.save_goal("unknown", ".codex/goals/x", record)
        outside = self.root / "outside"; outside.mkdir()
        link = self.a / ".codex/goals/link"; link.parent.mkdir(parents=True)
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError): self.memory.save_goal(self.pa, ".codex/goals/link", record)
        self.assertFalse((outside / "evolution.json").exists())

    def test_invalid_validation_claim_is_rejected(self):
        record = {"schemaVersion": 1, "objective": "Example", "lessons": [
            {"id": "x", "title": "Claim", "action": "Do this", "status": "validated"}]}
        with self.assertRaises(ValueError): self.memory.save_goal(self.pa, ".codex/goals/x", record)


if __name__ == "__main__": unittest.main()
