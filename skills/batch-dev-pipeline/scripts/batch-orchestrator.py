#!/usr/bin/env python3
"""
Batch Dev Pipeline Orchestrator v0.1.0

Reads ideas from YAML, creates isolated project directories,
dispatches each through adaptive-dev-engine, monitors progress.

Usage:
    python3 batch-orchestrator.py start ideas.yaml [--workspace ./workspace]
    python3 batch-orchestrator.py status [--workspace ./workspace]
    python3 batch-orchestrator.py stop [--workspace ./workspace]
"""

import argparse
import fcntl
import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    sys.exit("Error: PyYAML required. Install with: pip install pyyaml")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "0.1.0"
POLL_INTERVAL = 30          # seconds between state.json polls
STARTUP_WAIT = 5            # seconds to wait after adaptive-dev start
SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
# Data Models (frozen for immutability)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Idea:
    id: str
    name: str
    requirement: str
    priority: int = 1
    tags: tuple = ()
    max_sessions: int = 50


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_idea_progress(idea_id: str, project_dir: str) -> dict:
    return {
        "idea_id": idea_id,
        "status": "pending",
        "health_score": 0,
        "sessions_used": 0,
        "started_at": None,
        "completed_at": None,
        "error": None,
        "project_dir": project_dir,
    }


# ---------------------------------------------------------------------------
# Ideas Loader
# ---------------------------------------------------------------------------


def load_ideas(ideas_file: Path) -> tuple:
    """Parse ideas.yaml, validate, return sorted tuple of Idea objects."""
    with open(ideas_file, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "ideas" not in raw:
        raise ValueError("ideas.yaml must contain a top-level 'ideas' key")

    defaults = raw.get("defaults", {})
    default_max_sessions = defaults.get("max_sessions", 50)

    seen_ids = set()
    ideas = []

    for item in raw["ideas"]:
        idea_id = item.get("id", "")
        if not idea_id:
            raise ValueError("Each idea must have a non-empty 'id'")
        if not SAFE_ID_PATTERN.match(idea_id):
            raise ValueError(
                f"Idea id '{idea_id}' is invalid. "
                "Use alphanumeric, hyphens, underscores (max 64 chars)."
            )
        if idea_id in seen_ids:
            raise ValueError(f"Duplicate idea id: '{idea_id}'")
        seen_ids.add(idea_id)

        requirement = (item.get("requirement") or "").strip()
        if not requirement:
            raise ValueError(f"Idea '{idea_id}' has empty requirement")

        tags = tuple(item.get("tags", []))
        max_sessions = item.get("max_sessions", default_max_sessions)

        ideas.append(Idea(
            id=idea_id,
            name=item.get("name", idea_id),
            requirement=requirement,
            priority=item.get("priority", 1),
            tags=tags,
            max_sessions=max_sessions,
        ))

    return tuple(sorted(ideas, key=lambda i: i.priority))


# ---------------------------------------------------------------------------
# Batch State Manager
# ---------------------------------------------------------------------------


class BatchStateManager:
    """Manages workspace/batch-state.json with file locking."""

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._state_file = workspace / "batch-state.json"

    @property
    def state_file(self) -> Path:
        return self._state_file

    def exists(self) -> bool:
        return self._state_file.exists()

    def load(self) -> dict:
        if not self._state_file.exists():
            return {}
        with open(self._state_file, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def save(self, state: dict) -> None:
        self._workspace.mkdir(parents=True, exist_ok=True)
        tmp = self._state_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(
                    {**state, "last_updated": _now_iso()},
                    f, indent=2, ensure_ascii=False,
                )
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        tmp.replace(self._state_file)

    def update(self, **kwargs) -> dict:
        state = self.load()
        return {**state, **kwargs}

    def update_and_save(self, **kwargs) -> dict:
        new_state = self.update(**kwargs)
        self.save(new_state)
        return new_state

    def update_idea_progress(self, idea_id: str, **kwargs) -> dict:
        state = self.load()
        progress = dict(state.get("progress", {}))
        idea_prog = dict(progress.get(idea_id, {}))
        progress[idea_id] = {**idea_prog, **kwargs}
        new_state = {**state, "progress": progress}
        self.save(new_state)
        return new_state

# ---------------------------------------------------------------------------
# Project Isolator
# ---------------------------------------------------------------------------


class ProjectIsolator:
    """Creates and manages isolated project directories."""

    def __init__(self, workspace: Path):
        self._workspace = workspace

    def create_project(self, idea: Idea) -> Path:
        project_dir = self._workspace / idea.id
        project_dir.mkdir(parents=True, exist_ok=True)
        dev_state = project_dir / ".dev-state"
        dev_state.mkdir(exist_ok=True)

        config_env = dev_state / "config.env"
        if not config_env.exists():
            config_env.write_text(
                f"MAX_TURNS=40\n"
                f"MAX_TOTAL_SESSIONS={idea.max_sessions}\n"
                f"GIT_AUTO_COMMIT=false\n",
                encoding="utf-8",
            )
        return project_dir

    def get_project_dir(self, idea_id: str) -> Path:
        return self._workspace / idea_id

    def read_project_state(self, idea_id: str) -> Optional[dict]:
        state_file = self._workspace / idea_id / ".dev-state" / "state.json"
        if not state_file.exists():
            return None
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None


# ---------------------------------------------------------------------------
# Engine Invoker
# ---------------------------------------------------------------------------


class EngineInvoker:
    """Invokes adaptive-dev-engine for a single project."""

    def __init__(self, adaptive_dev_path: str):
        self._adaptive_dev = adaptive_dev_path

    def start(self, project_dir: Path, requirement: str) -> int:
        """
        Start adaptive-dev in the project directory.
        Returns the subprocess exit code (0 = daemon started).
        """
        result = subprocess.run(
            [self._adaptive_dev, "start", requirement],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode

    def stop(self, project_dir: Path) -> None:
        subprocess.run(
            [self._adaptive_dev, "stop"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
        )

    def is_running(self, project_dir: Path) -> bool:
        pid_file = project_dir / ".dev-state" / "daemon.pid"
        if not pid_file.exists():
            return False
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            return True
        except (ValueError, OSError):
            return False

# ---------------------------------------------------------------------------
# Batch Orchestrator (Main Loop)
# ---------------------------------------------------------------------------


class BatchOrchestrator:
    """Sequential batch orchestrator. Dispatches one idea at a time."""

    def __init__(
        self,
        ideas_file: Path,
        workspace: Path,
        adaptive_dev_path: str,
    ):
        self._ideas_file = ideas_file.resolve()
        self._workspace = workspace.resolve()
        self._state_mgr = BatchStateManager(self._workspace)
        self._isolator = ProjectIsolator(self._workspace)
        self._invoker = EngineInvoker(adaptive_dev_path)
        self._ideas: tuple = ()
        self._running = False
        self._logger = logging.getLogger("batch-orchestrator")

    def start(self) -> None:
        self._ideas = load_ideas(self._ideas_file)
        if not self._ideas:
            self._logger.error("No ideas found in %s", self._ideas_file)
            return

        self._logger.info(
            "Loaded %d ideas from %s", len(self._ideas), self._ideas_file
        )

        self._init_state()
        self._running = True
        self._main_loop()

    def _init_state(self) -> None:
        existing = self._state_mgr.load() if self._state_mgr.exists() else {}
        existing_progress = existing.get("progress", {})

        progress = {}
        for idea in self._ideas:
            project_dir = str(self._isolator.get_project_dir(idea.id))
            if idea.id in existing_progress:
                progress[idea.id] = existing_progress[idea.id]
            else:
                progress[idea.id] = _new_idea_progress(idea.id, project_dir)

        completed = sum(
            1 for p in progress.values() if p["status"] == "completed"
        )
        failed = sum(
            1 for p in progress.values() if p["status"] == "failed"
        )

        self._state_mgr.save({
            "version": VERSION,
            "status": "running",
            "ideas_file": str(self._ideas_file),
            "workspace": str(self._workspace),
            "total_ideas": len(self._ideas),
            "completed_ideas": completed,
            "failed_ideas": failed,
            "current_idea_id": None,
            "progress": progress,
            "started_at": existing.get("started_at", _now_iso()),
            "daemon_pid": os.getpid(),
        })

    def _main_loop(self) -> None:
        for idea in self._ideas:
            if not self._running:
                break

            state = self._state_mgr.load()
            idea_status = state["progress"].get(idea.id, {}).get("status")
            if idea_status in ("completed", "skipped"):
                self._logger.info("Skipping %s (already %s)", idea.id, idea_status)
                continue

            self._logger.info("=== Dispatching idea: %s ===", idea.id)
            self._dispatch_idea(idea)
            result = self._poll_idea(idea)
            self._handle_completion(idea, result)

        if self._running:
            state = self._state_mgr.load()
            completed = sum(
                1 for p in state["progress"].values()
                if p["status"] == "completed"
            )
            failed = sum(
                1 for p in state["progress"].values()
                if p["status"] == "failed"
            )
            final_status = "completed" if failed == 0 else "completed"
            self._state_mgr.update_and_save(
                status=final_status,
                completed_ideas=completed,
                failed_ideas=failed,
                current_idea_id=None,
            )
            self._logger.info(
                "Batch complete: %d/%d succeeded, %d failed",
                completed, len(self._ideas), failed,
            )

    def _dispatch_idea(self, idea: Idea) -> None:
        project_dir = self._isolator.create_project(idea)
        self._state_mgr.update_and_save(current_idea_id=idea.id)
        self._state_mgr.update_idea_progress(
            idea.id,
            status="running",
            started_at=_now_iso(),
            project_dir=str(project_dir),
        )

        self._logger.info("Starting adaptive-dev for %s", idea.id)
        exit_code = self._invoker.start(project_dir, idea.requirement)
        if exit_code != 0:
            self._logger.error(
                "adaptive-dev start failed for %s (exit=%d)", idea.id, exit_code
            )

        time.sleep(STARTUP_WAIT)

    def _poll_idea(self, idea: Idea) -> str:
        project_dir = self._isolator.get_project_dir(idea.id)

        while self._running:
            time.sleep(POLL_INTERVAL)

            project_state = self._isolator.read_project_state(idea.id)
            if project_state is None:
                if not self._invoker.is_running(project_dir):
                    self._logger.warning(
                        "%s: no state.json and daemon not running", idea.id
                    )
                    return "failed"
                continue

            status = project_state.get("status", "unknown")
            health = project_state.get("health", {}).get("score", 0)
            sessions = project_state.get("sessions", {}).get("count", 0)

            self._state_mgr.update_idea_progress(
                idea.id, health_score=health, sessions_used=sessions,
            )

            self._logger.info(
                "%s: health=%d sessions=%d status=%s",
                idea.id, health, sessions, status,
            )

            if status == "completed":
                return "completed"

            if sessions >= idea.max_sessions:
                self._logger.warning(
                    "%s: session limit reached (%d/%d)",
                    idea.id, sessions, idea.max_sessions,
                )
                self._invoker.stop(project_dir)
                return "failed"

            if status not in ("running", "ready", "continue", "paused"):
                if not self._invoker.is_running(project_dir):
                    self._logger.warning(
                        "%s: daemon stopped with status=%s", idea.id, status
                    )
                    return "failed"

        return "stopped"

    def _handle_completion(self, idea: Idea, result: str) -> None:
        project_dir = self._isolator.get_project_dir(idea.id)

        if result == "stopped":
            self._state_mgr.update_and_save(status="stopped")
            return

        project_state = self._isolator.read_project_state(idea.id)
        final_health = 0
        if project_state:
            final_health = project_state.get("health", {}).get("score", 0)

        update_kwargs = {
            "status": result,
            "health_score": final_health,
            "completed_at": _now_iso(),
        }
        if result == "failed":
            update_kwargs["error"] = "Session limit or daemon failure"

        self._state_mgr.update_idea_progress(idea.id, **update_kwargs)

        state = self._state_mgr.load()
        completed = sum(
            1 for p in state["progress"].values() if p["status"] == "completed"
        )
        failed = sum(
            1 for p in state["progress"].values() if p["status"] == "failed"
        )
        self._state_mgr.update_and_save(
            completed_ideas=completed, failed_ideas=failed,
        )

        self._logger.info(
            "%s: %s (health=%d)", idea.id, result, final_health
        )

    def stop(self) -> None:
        self._logger.info("Stopping batch orchestrator...")
        self._running = False

        state = self._state_mgr.load()
        current_id = state.get("current_idea_id")
        if current_id:
            project_dir = self._isolator.get_project_dir(current_id)
            self._invoker.stop(project_dir)

        self._state_mgr.update_and_save(status="stopped", current_idea_id=None)

    def status(self) -> dict:
        return self._state_mgr.load()


# ---------------------------------------------------------------------------
# Signal Handling
# ---------------------------------------------------------------------------

_orchestrator_ref: Optional[BatchOrchestrator] = None


def _signal_handler(signum, frame):
    if _orchestrator_ref:
        _orchestrator_ref.stop()


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------


def cmd_start(args) -> None:
    global _orchestrator_ref

    ideas_file = Path(args.ideas_file)
    if not ideas_file.exists():
        sys.exit(f"Error: ideas file not found: {ideas_file}")

    workspace = Path(args.workspace)
    adaptive_dev = args.adaptive_dev

    if not Path(adaptive_dev).exists() and not _which(adaptive_dev):
        sys.exit(f"Error: adaptive-dev not found: {adaptive_dev}")

    logging.basicConfig(
        level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT,
    )
    log_file = workspace / "batch-orchestrator.log"
    workspace.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logging.getLogger("batch-orchestrator").addHandler(file_handler)

    orchestrator = BatchOrchestrator(ideas_file, workspace, adaptive_dev)
    _orchestrator_ref = orchestrator

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    orchestrator.start()


def cmd_status(args) -> None:
    workspace = Path(args.workspace)
    mgr = BatchStateManager(workspace)
    if not mgr.exists():
        sys.exit(f"No batch state found at {mgr.state_file}")

    state = mgr.load()
    print("=" * 60)
    print(f"Batch Pipeline Status: {state.get('status', 'unknown').upper()}")
    print(
        f"Ideas: {state.get('completed_ideas', 0)}/{state.get('total_ideas', 0)} "
        f"completed, {state.get('failed_ideas', 0)} failed"
    )
    current = state.get("current_idea_id")
    if current:
        print(f"Current: {current}")
    print("=" * 60)

    for idea_id, prog in state.get("progress", {}).items():
        icons = {
            "pending": "[ ]", "running": "[>]", "completed": "[x]",
            "failed": "[!]", "skipped": "[-]",
        }
        icon = icons.get(prog.get("status", ""), "[?]")
        print(
            f"  {icon} {idea_id}: health={prog.get('health_score', 0)}/100 "
            f"sessions={prog.get('sessions_used', 0)} "
            f"status={prog.get('status', 'unknown')}"
        )
    print("=" * 60)


def cmd_stop(args) -> None:
    workspace = Path(args.workspace)
    mgr = BatchStateManager(workspace)
    if not mgr.exists():
        sys.exit(f"No batch state found at {mgr.state_file}")

    state = mgr.load()
    pid = state.get("daemon_pid")
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to batch orchestrator (PID {pid})")
        except OSError:
            print(f"Process {pid} not found, updating state")
    mgr.update_and_save(status="stopped", current_idea_id=None)


def _which(name: str) -> Optional[str]:
    result = subprocess.run(
        ["which", name], capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch Dev Pipeline Orchestrator v" + VERSION
    )
    subparsers = parser.add_subparsers(dest="command")

    sp_start = subparsers.add_parser("start", help="Start batch pipeline")
    sp_start.add_argument("ideas_file", help="Path to ideas.yaml")
    sp_start.add_argument(
        "--workspace", default="./workspace",
        help="Workspace directory (default: ./workspace)",
    )
    sp_start.add_argument(
        "--adaptive-dev",
        default=os.path.expanduser("~/.local/bin/adaptive-dev"),
        help="Path to adaptive-dev script",
    )

    sp_status = subparsers.add_parser("status", help="Show batch status")
    sp_status.add_argument("--workspace", default="./workspace")

    sp_stop = subparsers.add_parser("stop", help="Stop batch pipeline")
    sp_stop.add_argument("--workspace", default="./workspace")

    args = parser.parse_args()

    commands = {
        "start": cmd_start,
        "status": cmd_status,
        "stop": cmd_stop,
    }

    handler = commands.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
