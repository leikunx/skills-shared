"""Source-backed goal records and a rebuildable SQLite full-text index."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
import uuid

MAX_FILE = 1_048_576
STATUSES = {"provisional", "validated", "rejected", "superseded"}
STOP = set("a an and are as at be by for from goal how i in is it of on or our that the this to use we with".split())


def default_home() -> Path:
    if os.environ.get("GOAL_MEMORY_HOME"):
        return Path(os.environ["GOAL_MEMORY_HOME"]).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "GoalMemory"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "goal-memory"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_bytes(path: Path) -> bytes:
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ValueError(f"Missing or oversized goal record: {path.name}")
    return path.read_bytes()


def atomic_json(path: Path, value: object):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    if len(raw) > MAX_FILE:
        raise ValueError("Goal record exceeds 1 MiB.")
    fd, temporary = tempfile.mkstemp(prefix=".goal-memory-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inside(root: Path, relative: str, *, directory=False) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Use a relative path without parent traversal.")
    result = (root / candidate).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError("Path escapes its registered project.")
    # Do not ingest symlinked files or directory trees, including links within a root.
    current = root
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symlinked memory sources are not supported.")
    if directory and result.exists() and not result.is_dir():
        raise ValueError("Expected a goal directory.")
    return result


def text(value, maximum=12000) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"Expected text of at most {maximum} characters.")
    # Index summaries, never credentials or full tool transcripts.
    value = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}", "Bearer [redacted]", value)
    value = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,})\b", "[redacted]", value)
    value = re.sub(r"(?im)\b(password|api[_-]?key|access[_-]?token)\s*[:=]\s*[^\s,;]+", r"\1=[redacted]", value)
    return value.strip()


def identifier(value) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value):
        raise ValueError("Invalid stable identifier.")
    return value


class Memory:
    def __init__(self, home: Path | str | None = None):
        self.home = Path(home or default_home()).expanduser().resolve()
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            self.home.chmod(0o700)
        self.registry = self.home / "projects.json"
        self.database = self.home / "index.sqlite3"
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    source TEXT PRIMARY KEY, goal_id TEXT, project_id TEXT,
                    goal_directory TEXT, revision TEXT, payload TEXT);
                CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
                    goal_id UNINDEXED, project_id UNINDEXED, scope UNINDEXED, body,
                    tokenize='unicode61');
            """)

    @contextmanager
    def connect(self, write=False):
        db = sqlite3.connect(self.database, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def projects(self) -> list[dict]:
        return json.loads(read_bytes(self.registry)).get("projects", []) if self.registry.exists() else []

    def project(self, project_id: str) -> dict:
        return next((p for p in self.projects() if p["id"] == project_id), None) or self._unknown_project()

    @staticmethod
    def _unknown_project():
        raise ValueError("Unknown project; register its explicit root first.")

    def register_project(self, path: str, name: str = "", goals_directory: str = ".codex/goals") -> dict:
        root = Path(path).expanduser().resolve()
        if not root.is_dir() or root == Path.home().resolve() or root == Path(root.anchor):
            raise ValueError("Register one existing project, not a home directory or filesystem root.")
        inside(root, goals_directory, directory=True)
        common = root
        try:
            result = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=root, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                common = Path(result.stdout.strip()).resolve()
        except (OSError, subprocess.TimeoutExpired):
            pass
        project_id = "project-" + digest(str(common).encode())[:20]
        with self.connect(write=True):
            projects = self.projects()
            item = next((p for p in projects if p["id"] == project_id), None)
            if item is None:
                item = {"id": project_id, "name": text(name or root.name, 160), "roots": []}
                projects.append(item)
            entry = {"path": str(root), "goalsDirectory": goals_directory}
            if entry not in item["roots"]:
                item["roots"].append(entry)
            atomic_json(self.registry, {"schemaVersion": 1, "projects": projects})
        return item

    def goal_path(self, project_id: str, goal_directory: str, root_path: str = "") -> tuple[Path, Path]:
        project = self.project(project_id)
        roots = [r for r in project["roots"] if not root_path or r["path"] == str(Path(root_path).resolve())]
        if len(roots) != 1:
            raise ValueError("Specify root_path when a project has multiple registered worktrees.")
        root = Path(roots[0]["path"])
        goals = inside(root, roots[0]["goalsDirectory"], directory=True)
        goal = inside(root, goal_directory, directory=True)
        if goal == goals or not goal.is_relative_to(goals):
            raise ValueError("Goal must be inside the registered goals directory.")
        return root, goal

    def evidence(self, root: Path, entries: list, *, seal=False) -> list[dict]:
        if not isinstance(entries, list) or len(entries) > 30:
            raise ValueError("Evidence must be a list of at most 30 file references.")
        result = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("Evidence entries must be objects.")
            relative = text(entry.get("path", ""), 1000)
            path = inside(root, relative)
            value = {"path": relative, "gate": text(entry.get("gate", ""), 2000),
                     "result": text(entry.get("result", ""), 100), "sha256": entry.get("sha256")}
            if not relative or not value["gate"] or not value["result"]:
                raise ValueError("Each evidence reference needs path, gate and result.")
            if path.is_file() and path.stat().st_size <= 20 * MAX_FILE:
                actual = digest(path.read_bytes())
                if seal:
                    if value["sha256"] and value["sha256"] != actual:
                        raise ValueError("Evidence changed; do not silently reseal an existing validation claim.")
                    value["sha256"] = actual
                value["integrity"] = "current" if value["sha256"] == actual else "changed" if value["sha256"] else "unsealed"
            else:
                value["integrity"] = "missing"
                if seal:
                    raise ValueError(f"Evidence file is missing or oversized: {relative}")
            result.append(value)
        return result

    def normalize(self, raw: dict, root: Path, *, seal=False) -> dict:
        if not isinstance(raw, dict) or raw.get("schemaVersion") != 1:
            raise ValueError("Expected an evolution.json object with schemaVersion: 1.")
        record = {"schemaVersion": 1, "goalId": identifier(raw.get("goalId")),
            "objective": text(raw.get("objective", "")), "summary": text(raw.get("summary", "")),
            "status": text(raw.get("status", "active"), 40), "tags": raw.get("tags", []),
            "lessons": [], "reviews": raw.get("reviews", []), "applications": raw.get("applications", [])}
        if not record["objective"]:
            raise ValueError("A goal needs an objective.")
        if not isinstance(record["tags"], list) or len(record["tags"]) > 30:
            raise ValueError("At most 30 tags are supported.")
        record["tags"] = [text(t, 100) for t in record["tags"]]
        lessons = raw.get("lessons", [])
        if not isinstance(lessons, list) or len(lessons) > 50:
            raise ValueError("At most 50 concise lessons per goal are supported.")
        seen = set()
        for raw_lesson in lessons:
            if not isinstance(raw_lesson, dict) or not isinstance(raw_lesson.get("context", []), list) or len(raw_lesson.get("context", [])) > 30:
                raise ValueError("Each lesson needs an object and at most 30 context conditions.")
            lesson = {"id": identifier(raw_lesson.get("id")),
                **{key: text(raw_lesson.get(key, "")) for key in ["title", "trigger", "action", "outcome", "validation", "rollback"]},
                "status": raw_lesson.get("status", "provisional"), "scope": raw_lesson.get("scope", "project"),
                "context": [text(c, 300) for c in raw_lesson.get("context", [])],
                "evidence": self.evidence(root, raw_lesson.get("evidence", []), seal=seal)}
            if lesson["id"] in seen or not lesson["title"] or not lesson["action"]:
                raise ValueError("Lessons require unique IDs, titles and actions.")
            seen.add(lesson["id"])
            if lesson["status"] not in STATUSES or lesson["scope"] not in {"project", "portable"}:
                raise ValueError("Invalid lesson status or scope.")
            if lesson["status"] == "validated" and (not lesson["validation"] or not lesson["evidence"]):
                raise ValueError("Validated lessons require a validation account and evidence references.")
            record["lessons"].append(lesson)
        for collection in ["reviews", "applications"]:
            if not isinstance(record[collection], list) or len(record[collection]) > 200:
                raise ValueError(f"Expected at most 200 {collection} entries.")
            # Stored decisions are data, not additional instructions or automatic promotions.
            record[collection] = json.loads(text(json.dumps(record[collection], ensure_ascii=False), 150000))
        for application in record["applications"]:
            if not isinstance(application, dict):
                raise ValueError("Application outcomes must be objects.")
            application["evidence"] = self.evidence(root, application.get("evidence", []), seal=seal)
            for entry in application["evidence"]:
                entry.pop("integrity", None)
        return record

    def legacy(self, raw: bytes, project_id: str, relative: str) -> dict:
        value = raw.decode("utf-8")
        match = re.search(r"(?im)^[ \t]*[-*]?[ \t]*(?:\*\*)?(?:Objective|Outcome)(?:\*\*)?[ \t]*:[ \t]*(?:\*\*)?[ \t]*(\S.+)$", value)
        heading = re.search(r"(?m)^#\s+(.+)$", value)
        objective = text(match.group(1) if match else heading.group(1) if heading else Path(relative).parent.name)
        goal_id = "legacy-" + digest((project_id + relative + objective).encode())[:24]
        lessons = []
        section = re.search(r"(?ims)^##\s+(?:Durable lessons|Validated lessons|Lessons learned)\s*\n(.*?)(?=^##\s|\Z)", value)
        placeholders = {"", "none", "none yet", "n/a", "tbd", "pending", "no lessons yet", "no durable lessons", "no durable lessons yet", "no validated lessons"}
        section_lines = [line.strip(" \t-*.").lower() for line in section.group(1).splitlines()] if section else []
        if section and any(line not in placeholders for line in section_lines):
            content = text(section.group(1).strip())
            lessons.append({"id": "legacy-notes", "title": "Imported goal lessons", "trigger": objective,
                "action": content, "outcome": "", "status": "provisional", "scope": "project",
                "context": [], "evidence": [], "validation": "Legacy text; validation and portability were not inferred.", "rollback": ""})
        return {"schemaVersion": 1, "goalId": goal_id, "objective": objective, "summary": "Imported from STATE.md",
            "status": "unknown", "tags": [], "lessons": lessons, "reviews": [], "applications": []}

    @staticmethod
    def lesson_text(lessons: list[dict]) -> str:
        return "\n".join(" ".join(str(l.get(k, "")) for k in ["title", "trigger", "action", "outcome", "context"]) for l in lessons)

    def refresh(self) -> dict:
        with self.connect(write=True) as db:
            return self._refresh_locked(db)

    def _refresh_locked(self, db) -> dict:
        documents, errors = [], []
        for project in self.projects():
            for registration in project["roots"]:
                root = Path(registration["path"])
                try:
                    goals = inside(root, registration["goalsDirectory"], directory=True)
                    if not goals.exists():
                        continue
                    folders = sorted({p.parent for pattern in ["STATE.md", "state.md", "evolution.json"] for p in goals.rglob(pattern)})
                    if len(folders) > 10000:
                        raise ValueError("Project exceeds the 10,000-goal scan limit.")
                    for folder in folders:
                        source = folder / "evolution.json"
                        if not source.exists():
                            source = folder / ("STATE.md" if (folder / "STATE.md").exists() else "state.md")
                        try:
                            source = inside(root, str(source.relative_to(root)))
                            raw = read_bytes(source)
                            record = self.normalize(json.loads(raw), root) if source.name == "evolution.json" else self.legacy(raw, project["id"], str(source.relative_to(root)))
                            documents.append((str(source), record["goalId"], project["id"], str(folder.relative_to(root)), digest(raw), json.dumps(record)))
                        except (ValueError, OSError, TypeError, KeyError) as exc:
                            errors.append({"source": str(source), "error": str(exc)})
                except (ValueError, OSError) as exc:
                    errors.append({"projectId": project["id"], "error": str(exc)})
        conflicts = set()
        by_id = {}
        for row in documents:
            previous = by_id.setdefault(row[1], row[5])
            if previous != row[5]:
                conflicts.add(row[1])
        old = {r["source"]: tuple(r) for r in db.execute("SELECT * FROM documents")}
        new = {r[0]: r for r in documents}
        dirty = {r[1] for p, r in old.items() if new.get(p) != r} | {r[1] for p, r in new.items() if old.get(p) != r}
        for source in old.keys() - new.keys():
            db.execute("DELETE FROM documents WHERE source=?", (source,))
        for source, row in new.items():
            if old.get(source) != row:
                db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)", row)
        for goal_id in dirty:
            db.execute("DELETE FROM search WHERE goal_id=?", (goal_id,))
        seen = set()
        for row in documents:
            if row[1] not in dirty or row[1] in conflicts or (row[1], row[2]) in seen:
                continue
            seen.add((row[1], row[2]))
            record = json.loads(row[5])
            active = [l for l in record["lessons"] if l["status"] not in {"rejected", "superseded"}]
            if not active:
                continue
            body = " ".join([record["objective"], record["summary"], *record["tags"], self.lesson_text(active)])
            db.execute("INSERT INTO search VALUES (?,?,?,?)", (row[1], row[2], "project", body))
            portable = [l for l in active if l["scope"] == "portable"]
            if portable:
                db.execute("INSERT INTO search VALUES (?,?,?,?)", (row[1], row[2], "portable", self.lesson_text(portable)))
        return {"sources": len(documents), "distinctGoals": len(by_id), "changedGoals": len(dirty), "conflicts": sorted(conflicts), "errors": errors}

    def get_goal(self, goal_id: str, requesting_project_id: str) -> dict:
        self.project(requesting_project_id)
        with self.connect() as db:
            rows = db.execute("SELECT * FROM documents WHERE goal_id=? ORDER BY project_id=? DESC,source", (goal_id, requesting_project_id)).fetchall()
        if not rows:
            raise ValueError("Unknown or unindexed goal.")
        if len({r["payload"] for r in rows}) > 1:
            raise ValueError("Conflicting records share this goal ID; resolve the source conflict first.")
        row = rows[0]
        source = Path(row["source"])
        registrations = self.project(row["project_id"])["roots"]
        root = next(Path(r["path"]) for r in registrations if source.is_relative_to(Path(r["path"]).resolve()))
        source = inside(root, str(source.relative_to(root)))
        if not source.is_file() or digest(read_bytes(source)) != row["revision"]:
            raise ValueError("Goal source changed or disappeared; refresh before using it.")
        record = json.loads(row["payload"])
        own = row["project_id"] == requesting_project_id
        lessons = [l for l in record["lessons"] if own or l["scope"] == "portable"]
        if not own and not lessons:
            raise ValueError("This goal has no portable lessons for the requesting project.")
        # Recheck evidence rather than treating an old index as proof of current integrity.
        for lesson in lessons:
            lesson["evidence"] = self.evidence(root, lesson["evidence"])
            lesson["evidenceCurrent"] = bool(lesson["evidence"]) and all(e["integrity"] == "current" for e in lesson["evidence"])
            lesson["recordedStatus"] = lesson["status"]
        if own:
            for application in record["applications"]:
                application["evidence"] = self.evidence(root, application.get("evidence", []))
        return {"goalId": goal_id, "projectId": row["project_id"], "revision": row["revision"],
            "goalDirectory": row["goal_directory"], "source": str(source),
            "objective": record["objective"] if own else "; ".join(l["title"] for l in lessons),
            "summary": record["summary"] if own else "Portable lessons from another registered project",
            "lessons": lessons, "reviews": record["reviews"] if own else [],
            "applications": record["applications"] if own else [],
            "caution": "Recorded validation is not proof for the new goal. Verify applicability and run its gate."}

    def search_goals(self, query: str, project_id: str, limit: int = 5, exclude_goal_id: str = "") -> dict:
        self.project(project_id)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 5:
            raise ValueError("Select one to five distinct prior goals.")
        tokens = list(dict.fromkeys(t.lower() for t in re.findall(r"[^\W_]+", text(query, 2000), re.UNICODE) if len(t) > 1 and t.lower() not in STOP))[:40]
        refreshed = self.refresh()
        results, seen = [], set()
        if tokens:
            expression = " OR ".join('"' + token + '"' for token in tokens)
            with self.connect() as db:
                rows = db.execute("""SELECT goal_id, project_id, scope, body, bm25(search) AS rank FROM search
                    WHERE search MATCH ? AND (project_id=? OR scope='portable') AND goal_id<>?
                    ORDER BY rank LIMIT 100""", (expression, project_id, exclude_goal_id)).fetchall()
            candidates = []
            for row in rows:
                matches = [t for t in tokens if t in row["body"].lower()]
                score = len(matches) / len(tokens) + min(-row["rank"], 5) / 20
                if row["project_id"] == project_id:
                    score += 0.05
                candidates.append((score, row, matches))
            for score, row, matches in sorted(candidates, key=lambda item: (-item[0], item[1]["goal_id"])):
                if row["goal_id"] in seen:
                    continue
                try:
                    goal = self.get_goal(row["goal_id"], project_id)
                except (ValueError, OSError):
                    continue
                active = [l for l in goal["lessons"] if l["status"] not in {"rejected", "superseded"}]
                if not active:
                    continue
                seen.add(row["goal_id"])
                results.append({"goalId": goal["goalId"], "projectId": goal["projectId"], "objective": goal["objective"],
                    "revision": goal["revision"], "score": round(score, 4), "matchedTerms": matches,
                    "lessons": [{k: l[k] for k in ["id", "title", "status", "scope", "evidenceCurrent"]} for l in active]})
                if len(results) == limit:
                    break
        return {"goals": results, "reviewTarget": "3–5 distinct relevant goals", "count": len(results),
            "shortfall": "Fewer than three relevant indexed goals with reusable lessons are available; do not pad with unrelated goals." if len(results) < 3 else None,
            "index": refreshed, "ranking": "Keyword relevance and current-project context; no semantic embeddings or automatic validation."}

    def save_goal(self, project_id: str, goal_directory: str, record: dict,
                  expected_revision: str | None = None, root_path: str = "") -> dict:
        root, folder = self.goal_path(project_id, goal_directory, root_path)
        path = inside(root, str((folder / "evolution.json").relative_to(root)))
        with self.connect(write=True):
            current = digest(read_bytes(path)) if path.exists() else None
            if current != expected_revision:
                raise ValueError("Revision conflict. Read the current record before writing.")
            previous = json.loads(read_bytes(path)) if path.exists() else None
            raw = dict(record)
            raw.setdefault("goalId", previous["goalId"] if previous else str(uuid.uuid4()))
            if previous and raw["goalId"] != previous["goalId"]:
                raise ValueError("A goal ID cannot be changed by an update.")
            normalized = self.normalize(raw, root, seal=True)
            for lesson in normalized["lessons"]:
                for entry in lesson["evidence"]:
                    entry.pop("integrity", None)
            atomic_json(path, normalized)
            revision = digest(read_bytes(path))
        self.refresh()
        return {"goalId": normalized["goalId"], "revision": revision, "source": str(path)}

    def record_application(self, project_id: str, goal_directory: str, source_goal_id: str,
                           lesson_id: str, source_revision: str, outcome: str, notes: str,
                           evidence: list, expected_revision: str, root_path: str = "") -> dict:
        if outcome not in {"applied", "rejected", "test-next", "passed", "failed", "inconclusive"}:
            raise ValueError("Invalid application outcome.")
        source = self.get_goal(source_goal_id, project_id)
        if source["revision"] != source_revision:
            raise ValueError("The source lesson changed; review it again before recording reuse.")
        lesson = next((l for l in source["lessons"] if l["id"] == lesson_id), None)
        if lesson is None or lesson["status"] in {"rejected", "superseded"}:
            raise ValueError("Unknown or retired source lesson.")
        root, folder = self.goal_path(project_id, goal_directory, root_path)
        path = inside(root, str((folder / "evolution.json").relative_to(root)))
        record = json.loads(read_bytes(path))
        if record["goalId"] == source_goal_id:
            raise ValueError("Cross-goal reuse must reference a different goal.")
        if outcome in {"passed", "failed"} and not evidence:
            raise ValueError("A measured outcome needs evidence.")
        record.setdefault("applications", []).append({"id": str(uuid.uuid4()), "at": now(),
            "sourceGoalId": source_goal_id, "lessonId": lesson_id, "sourceRevision": source_revision,
            "outcome": outcome, "notes": text(notes), "evidence": self.evidence(root, evidence, seal=True)})
        return self.save_goal(project_id, goal_directory, record, expected_revision, root_path)

    def status(self) -> dict:
        with self.connect() as db:
            count = db.execute("SELECT count(DISTINCT goal_id) FROM documents").fetchone()[0]
        return {"service": "goal-memory", "schemaVersion": 1, "home": str(self.home),
            "projects": self.projects(), "indexedGoals": count}
