#!/usr/bin/env python3
"""
Acceptance tests for batch-dev-pipeline.

Tests:
  1. Ideas YAML parsing and validation
  2. Batch state management (init, update, resume)
  3. Project isolation (directory creation, config.env)
  4. Engine invoker (mock adaptive-dev)
  5. Orchestrator lifecycle (mocked engine)
  6. Status reporting
"""

import importlib.util
import json
import os
import tempfile
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# ---------------------------------------------------------------------------
# Load batch-orchestrator module dynamically
# ---------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent / "skills" / "batch-dev-pipeline"
SCRIPTS_DIR = SKILL_ROOT / "scripts"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "batch_orchestrator", SCRIPTS_DIR / "batch-orchestrator.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BO = _load_module()


# ===========================================================================
# 1. Ideas YAML Parsing
# ===========================================================================


class TestIdeasParsing:

    def _write_yaml(self, tmpdir, content):
        p = Path(tmpdir) / "ideas.yaml"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p

    def test_valid_ideas_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                defaults:
                  max_sessions: 50
                ideas:
                  - id: "app-a"
                    name: "App A"
                    requirement: "Build app A"
                    priority: 2
                  - id: "app-b"
                    name: "App B"
                    requirement: "Build app B"
                    priority: 1
            """)
            ideas = BO.load_ideas(f)
            assert len(ideas) == 2
            assert ideas[0].id == "app-b"  # priority 1 first
            assert ideas[1].id == "app-a"  # priority 2 second
    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "dup"
                    name: "A"
                    requirement: "Build A"
                  - id: "dup"
                    name: "B"
                    requirement: "Build B"
            """)
            with pytest.raises(ValueError, match="Duplicate"):
                BO.load_ideas(f)

    def test_empty_requirement_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "empty"
                    name: "Empty"
                    requirement: ""
            """)
            with pytest.raises(ValueError, match="empty requirement"):
                BO.load_ideas(f)

    def test_ideas_sorted_by_priority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "c"
                    requirement: "C"
                    priority: 3
                  - id: "a"
                    requirement: "A"
                    priority: 1
                  - id: "b"
                    requirement: "B"
                    priority: 2
            """)
            ideas = BO.load_ideas(f)
            assert [i.id for i in ideas] == ["a", "b", "c"]

    def test_defaults_applied(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                defaults:
                  max_sessions: 99
                ideas:
                  - id: "app"
                    requirement: "Build it"
            """)
            ideas = BO.load_ideas(f)
            assert ideas[0].max_sessions == 99

    def test_unsafe_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "../escape"
                    requirement: "Bad"
            """)
            with pytest.raises(ValueError, match="invalid"):
                BO.load_ideas(f)

    def test_per_idea_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f = self._write_yaml(tmpdir, """
                version: "1.0"
                defaults:
                  max_sessions: 50
                ideas:
                  - id: "custom"
                    requirement: "Build it"
                    max_sessions: 10
            """)
            ideas = BO.load_ideas(f)
            assert ideas[0].max_sessions == 10


# ===========================================================================
# 2. Batch State Management
# ===========================================================================


class TestBatchStateManager:

    def test_init_creates_state_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({"version": "0.1.0", "status": "ready"})
            assert mgr.exists()
            state = mgr.load()
            assert state["version"] == "0.1.0"
            assert state["status"] == "ready"

    def test_update_is_immutable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({"status": "ready", "total": 3})
            original = mgr.load()
            new_state = mgr.update(status="running")
            assert new_state["status"] == "running"
            reloaded = mgr.load()
            assert reloaded["status"] == "ready"  # not saved yet

    def test_update_and_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({"status": "ready"})
            mgr.update_and_save(status="running")
            state = mgr.load()
            assert state["status"] == "running"

    def test_update_idea_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({
                "progress": {
                    "app-a": {"idea_id": "app-a", "status": "pending", "health_score": 0}
                }
            })
            mgr.update_idea_progress("app-a", status="running", health_score=45)
            state = mgr.load()
            assert state["progress"]["app-a"]["status"] == "running"
            assert state["progress"]["app-a"]["health_score"] == 45

    def test_last_updated_auto_set(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({"status": "ready"})
            state = mgr.load()
            assert "last_updated" in state


# ===========================================================================
# 3. Project Isolation
# ===========================================================================


class TestProjectIsolation:

    def _make_idea(self, idea_id="test-app", max_sessions=10):
        return BO.Idea(
            id=idea_id, name="Test", requirement="Build it",
            priority=1, max_sessions=max_sessions,
        )

    def test_creates_project_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            idea = self._make_idea()
            project_dir = iso.create_project(idea)
            assert project_dir.exists()
            assert project_dir.name == "test-app"

    def test_creates_dev_state_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            idea = self._make_idea()
            project_dir = iso.create_project(idea)
            assert (project_dir / ".dev-state").is_dir()

    def test_writes_config_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            idea = self._make_idea(max_sessions=25)
            project_dir = iso.create_project(idea)
            config = (project_dir / ".dev-state" / "config.env").read_text()
            assert "MAX_TOTAL_SESSIONS=25" in config

    def test_projects_are_independent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            dir_a = iso.create_project(self._make_idea("app-a"))
            dir_b = iso.create_project(self._make_idea("app-b"))
            assert dir_a != dir_b
            assert dir_a.name == "app-a"
            assert dir_b.name == "app-b"

    def test_read_project_state_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            assert iso.read_project_state("nonexistent") is None

    def test_read_project_state_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            iso = BO.ProjectIsolator(Path(tmpdir))
            idea = self._make_idea()
            project_dir = iso.create_project(idea)
            state_file = project_dir / ".dev-state" / "state.json"
            state_file.write_text(
                json.dumps({"health": {"score": 55}, "status": "running"}),
                encoding="utf-8",
            )
            state = iso.read_project_state("test-app")
            assert state["health"]["score"] == 55


# ===========================================================================
# 4. Engine Invoker
# ===========================================================================


class TestEngineInvoker:

    def test_is_running_no_pid_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            invoker = BO.EngineInvoker("/fake/adaptive-dev")
            assert not invoker.is_running(Path(tmpdir))

    def test_is_running_stale_pid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            dev_state = project / ".dev-state"
            dev_state.mkdir()
            (dev_state / "daemon.pid").write_text("999999999")
            invoker = BO.EngineInvoker("/fake/adaptive-dev")
            assert not invoker.is_running(project)

    @patch("subprocess.run")
    def test_start_calls_adaptive_dev(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        invoker = BO.EngineInvoker("/usr/local/bin/adaptive-dev")
        with tempfile.TemporaryDirectory() as tmpdir:
            code = invoker.start(Path(tmpdir), "Build an app")
            assert code == 0
            call_args = mock_run.call_args
            assert call_args[0][0] == [
                "/usr/local/bin/adaptive-dev", "start", "Build an app"
            ]

    @patch("subprocess.run")
    def test_stop_calls_adaptive_dev(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        invoker = BO.EngineInvoker("/usr/local/bin/adaptive-dev")
        with tempfile.TemporaryDirectory() as tmpdir:
            invoker.stop(Path(tmpdir))
            call_args = mock_run.call_args
            assert call_args[0][0] == ["/usr/local/bin/adaptive-dev", "stop"]


# ===========================================================================
# 5. Orchestrator Lifecycle (Mocked Engine)
# ===========================================================================


class TestOrchestratorLifecycle:

    def _write_ideas(self, tmpdir, ideas_content):
        f = Path(tmpdir) / "ideas.yaml"
        f.write_text(textwrap.dedent(ideas_content), encoding="utf-8")
        return f

    def test_start_initializes_batch_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ideas_file = self._write_ideas(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "app-a"
                    requirement: "Build A"
                  - id: "app-b"
                    requirement: "Build B"
            """)
            workspace = Path(tmpdir) / "workspace"

            orch = BO.BatchOrchestrator(ideas_file, workspace, "/fake/adaptive-dev")
            orch._ideas = BO.load_ideas(ideas_file)
            orch._init_state()

            state = orch._state_mgr.load()
            assert state["total_ideas"] == 2
            assert state["status"] == "running"
            assert "app-a" in state["progress"]
            assert "app-b" in state["progress"]
            assert state["progress"]["app-a"]["status"] == "pending"

    def test_completed_idea_skipped_on_resume(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ideas_file = self._write_ideas(tmpdir, """
                version: "1.0"
                ideas:
                  - id: "done"
                    requirement: "Already done"
                  - id: "todo"
                    requirement: "Still todo"
            """)
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()

            mgr = BO.BatchStateManager(workspace)
            mgr.save({
                "progress": {
                    "done": {"idea_id": "done", "status": "completed", "health_score": 85},
                }
            })

            orch = BO.BatchOrchestrator(ideas_file, workspace, "/fake/adaptive-dev")
            orch._ideas = BO.load_ideas(ideas_file)
            orch._init_state()

            state = orch._state_mgr.load()
            assert state["progress"]["done"]["status"] == "completed"
            assert state["completed_ideas"] == 1


# ===========================================================================
# 6. Status Reporting
# ===========================================================================


class TestStatusReporting:

    def test_status_returns_all_ideas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            mgr.save({
                "status": "running",
                "total_ideas": 2,
                "completed_ideas": 1,
                "failed_ideas": 0,
                "progress": {
                    "app-a": {"status": "completed", "health_score": 82},
                    "app-b": {"status": "running", "health_score": 45},
                },
            })
            state = mgr.load()
            assert len(state["progress"]) == 2
            assert state["progress"]["app-a"]["health_score"] == 82

    def test_status_with_empty_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = BO.BatchStateManager(Path(tmpdir))
            assert not mgr.exists()


# ===========================================================================
# 7. Integration: Full Pipeline (Mocked)
# ===========================================================================


class TestFullPipelineMocked:

    def _write_ideas(self, tmpdir):
        f = Path(tmpdir) / "ideas.yaml"
        f.write_text(textwrap.dedent("""
            version: "1.0"
            defaults:
              max_sessions: 3
            ideas:
              - id: "simple"
                requirement: "Build simple app"
                priority: 1
        """), encoding="utf-8")
        return f

    @patch.object(BO.EngineInvoker, "start", return_value=0)
    @patch.object(BO.EngineInvoker, "stop")
    @patch.object(BO.EngineInvoker, "is_running", return_value=False)
    def test_idea_completes_when_state_completed(self, mock_running, mock_stop, mock_start):
        with tempfile.TemporaryDirectory() as tmpdir:
            ideas_file = self._write_ideas(tmpdir)
            workspace = Path(tmpdir) / "workspace"

            orch = BO.BatchOrchestrator(ideas_file, workspace, "/fake/adaptive-dev")

            # Simulate: after dispatch, state.json shows completed
            original_poll = orch._poll_idea

            def fake_poll(idea):
                project_dir = orch._isolator.get_project_dir(idea.id)
                state_file = project_dir / ".dev-state" / "state.json"
                state_file.write_text(json.dumps({
                    "status": "completed",
                    "health": {"score": 85},
                    "sessions": {"count": 2},
                }), encoding="utf-8")
                orch._running = True
                # Read once and return
                return "completed"

            orch._poll_idea = fake_poll
            orch.start()

            state = orch._state_mgr.load()
            assert state["completed_ideas"] == 1
            assert state["progress"]["simple"]["status"] == "completed"

