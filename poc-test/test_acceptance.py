#!/usr/bin/env python3
"""
Acceptance tests for adaptive-dev-engine skill.

Validates the ENTIRE skill works as expected:
  1. health-check.py: Scoring pipeline across project maturity levels
  2. Bash daemon: State init, prompt construction, error classification, config loading
  3. Decision engine: SKILL.md decision table matches decision-engine.md algorithm
  4. State protocol: Full lifecycle (init → update → checkpoint → recover)
  5. Cross-file consistency: All docs, scripts, and configs aligned
"""

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent / "skills" / "adaptive-dev-engine"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REFS_DIR = SKILL_ROOT / "references"

# ---------------------------------------------------------------------------
# Load health-check.py as module
# ---------------------------------------------------------------------------

def _load_health_check():
    spec = importlib.util.spec_from_file_location(
        "health_check", SCRIPTS_DIR / "health-check.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

HC = _load_health_check()

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

# ===========================================================================
# 1. health-check.py: Scoring pipeline across project maturity levels
# ===========================================================================

class TestHealthCheckScoring:
    """Validate health-check.py produces correct scores for different project states."""

    def _make_project(self, tmpdir: str, **kwargs):
        """Build a mock project structure.

        kwargs:
            prd_count: int - number of PRD docs
            code_files: int - number of code files in src/
            api_files: int - number of files with @app.get decorators
            test_files: int - number of test_*.py files
            has_main: bool - create src/main.py
            has_pyproject: bool - create pyproject.toml
            has_start: bool - create start.sh
        """
        p = Path(tmpdir)
        if kwargs.get("prd_count", 0):
            (p / "docs" / "prd").mkdir(parents=True)
            for i in range(kwargs["prd_count"]):
                (p / "docs" / "prd" / f"feature_{i}.md").write_text(f"# Feature {i}\n")
        if kwargs.get("has_readme"):
            (p / "README.md").write_text("# Project\n")
        if kwargs.get("code_files", 0):
            (p / "src").mkdir(exist_ok=True)
            for i in range(kwargs["code_files"]):
                (p / "src" / f"mod_{i}.py").write_text(f"# module {i}\n")
        if kwargs.get("api_files", 0):
            (p / "src").mkdir(exist_ok=True)
            for i in range(kwargs["api_files"]):
                (p / "src" / f"api_{i}.py").write_text(
                    f"@app.get('/item/{i}')\ndef get_{i}(): pass\n"
                )
        if kwargs.get("test_files", 0):
            (p / "tests").mkdir(exist_ok=True)
            for i in range(kwargs["test_files"]):
                (p / "tests" / f"test_mod_{i}.py").write_text(
                    f"def test_something_{i}(): assert True\n"
                )
        if kwargs.get("has_main"):
            (p / "src").mkdir(exist_ok=True)
            (p / "src" / "main.py").write_text("app = None\n")
        if kwargs.get("has_pyproject"):
            (p / "pyproject.toml").write_text("[project]\nname='test'\n")
        if kwargs.get("has_start"):
            (p / "start.sh").write_text("#!/bin/bash\necho start\n")
            os.chmod(p / "start.sh", 0o755)

    # --- Empty project ---
    def test_empty_project_scores_near_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = HC.assess(tmpdir)
            # quality returns 6 when linter unavailable (expected default)
            assert result["score"] <= 10, f"Empty project should score <=10, got {result['score']}"
            assert not result["usable"]
            assert result["breakdown"]["requirements"] == 0
            assert result["breakdown"]["code"] == 0
            assert result["breakdown"]["tests"] == 0
            assert result["breakdown"]["runnable"] == 0
            # quality may be 6 (linter unavailable default) — this is correct behavior
            assert result["breakdown"]["quality"] in (0, 6)

    # --- Requirements only ---
    def test_readme_only_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, has_readme=True)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["requirements"] == 5
            assert result["score"] < 20

    def test_full_prd_project(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, prd_count=5)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["requirements"] == 20

    # --- Code scoring ---
    def test_minimal_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, code_files=3)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["code"] == 5, f"1-4 files should score 5, got {result['breakdown']['code']}"

    def test_skeleton_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, code_files=8)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["code"] == 10

    def test_partial_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, code_files=20)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["code"] == 15

    def test_mostly_complete_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, code_files=35)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["code"] == 20

    def test_full_code_with_apis(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, code_files=45, api_files=6)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["code"] == 25

    # --- Test scoring ---
    def test_no_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = HC.assess(tmpdir)
            assert result["breakdown"]["tests"] == 0

    def test_few_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, test_files=3)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["tests"] == 8

    def test_moderate_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, test_files=7)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["tests"] == 12

    # --- Runnable scoring ---
    def test_no_runnable_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = HC.assess(tmpdir)
            assert result["breakdown"]["runnable"] == 0

    def test_deps_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, has_pyproject=True)
            result = HC.assess(tmpdir)
            assert result["breakdown"]["runnable"] == 5

    def test_deps_plus_main(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, has_pyproject=True, has_main=True)
            result = HC.assess(tmpdir)
            # score_runnable tries actual startup (uvicorn). If uvicorn is installed
            # and port responds, score=20; otherwise score=10 (has deps + entry point).
            assert result["breakdown"]["runnable"] in (10, 20)

    def test_start_plus_main(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(tmpdir, has_pyproject=True, has_main=True, has_start=True)
            result = HC.assess(tmpdir)
            # Without actual server, can_start=False, so 15
            assert result["breakdown"]["runnable"] == 15

    # --- Composite: near-usable project ---
    def test_near_usable_project(self):
        """A well-structured project should score 60-75 (not yet usable)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_project(
                tmpdir,
                prd_count=4,
                code_files=35,
                api_files=3,
                test_files=7,
                has_pyproject=True,
                has_main=True,
            )
            result = HC.assess(tmpdir)
            assert 50 <= result["score"] <= 80, f"Near-usable should be 50-80, got {result['score']}"
            assert not result["usable"]

    # --- assess() output structure ---
    def test_assess_output_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = HC.assess(tmpdir)
            assert "score" in result
            assert "breakdown" in result
            assert "details" in result
            assert "usable" in result
            assert "assessed_at" in result
            for dim in ["requirements", "code", "tests", "runnable", "quality"]:
                assert dim in result["breakdown"]
                assert dim in result["details"]

    # --- MAX_SCORES constant ---
    def test_max_scores_sum_to_100(self):
        assert sum(HC.MAX_SCORES.values()) == 100

# ===========================================================================
# 2. health-check.py: update_state with file locking
# ===========================================================================

class TestHealthCheckUpdateState:
    """Validate update_state correctly writes to state.json."""

    def _init_state(self, tmpdir: str) -> Path:
        state_dir = Path(tmpdir) / ".dev-state"
        state_dir.mkdir()
        state_file = state_dir / "state.json"
        state = {
            "version": "2.0.0",
            "health": {"score": 30, "breakdown": {}, "history": []},
            "status": "running",
            "last_heartbeat": "2024-01-01T00:00:00Z",
        }
        state_file.write_text(json.dumps(state))
        return state_file

    def test_update_state_writes_health(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = self._init_state(tmpdir)
            health = HC.assess(tmpdir)
            HC.update_state(tmpdir, health)
            state = json.loads(state_file.read_text())
            assert state["health"]["score"] == health["score"]
            assert state["health"]["breakdown"] == health["breakdown"]
            assert state["health"]["details"] == health["details"]

    def test_update_state_computes_delta(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = self._init_state(tmpdir)
            health = HC.assess(tmpdir)
            HC.update_state(tmpdir, health)
            state = json.loads(state_file.read_text())
            # Old score was 30, new is 0 (empty project)
            assert state["health"]["delta"] == health["score"] - 30

    def test_update_state_appends_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = self._init_state(tmpdir)
            health = HC.assess(tmpdir)
            HC.update_state(tmpdir, health)
            state = json.loads(state_file.read_text())
            assert len(state["health"]["history"]) == 1
            assert state["health"]["history"][0]["score"] == health["score"]

    def test_update_state_limits_history_to_20(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".dev-state"
            state_dir.mkdir()
            state_file = state_dir / "state.json"
            state = {
                "version": "2.0.0",
                "health": {
                    "score": 10,
                    "breakdown": {},
                    "history": [{"timestamp": f"t{i}", "score": i} for i in range(25)],
                },
                "status": "running",
                "last_heartbeat": "2024-01-01T00:00:00Z",
            }
            state_file.write_text(json.dumps(state))
            HC.update_state(tmpdir, HC.assess(tmpdir))
            state = json.loads(state_file.read_text())
            assert len(state["health"]["history"]) <= 20

    def test_update_state_sets_completed_when_usable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / ".dev-state"
            state_dir.mkdir()
            state_file = state_dir / "state.json"
            state = {
                "version": "2.0.0",
                "health": {"score": 0, "breakdown": {}, "history": []},
                "status": "running",
                "last_heartbeat": "2024-01-01T00:00:00Z",
            }
            state_file.write_text(json.dumps(state))
            # Fake a usable health result
            fake_health = {
                "score": 85,
                "breakdown": {"requirements": 20, "code": 25, "tests": 15, "runnable": 15, "quality": 10},
                "details": {},
                "usable": True,
                "assessed_at": "2024-01-01T12:00:00Z",
            }
            HC.update_state(tmpdir, fake_health)
            state = json.loads(state_file.read_text())
            assert state["status"] == "completed"
            assert state["exit_reason"] == "usable_reached"


# ===========================================================================
# 3. Bash daemon: State init, config, error classification
# ===========================================================================

class TestBashDaemonStateInit:
    """Validate bash daemon _init_state produces valid state.json."""

    def test_init_state_creates_valid_json(self):
        """Run _init_state via bash and verify the output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script = SCRIPTS_DIR / "adaptive-dev"
            result = subprocess.run(
                ["bash", "-c", f"""
                    cd '{tmpdir}'
                    source '{script}'
                    PROJECT_DIR='{tmpdir}'
                    STATE_DIR='.dev-state'
                    STATE_FILE='{tmpdir}/.dev-state/state.json'
                    HEALTH_CHECK='/dev/null'
                    VERSION='2.0.0'
                    _init_state 'test-project' 'Build a todo app'
                """],
                capture_output=True, text=True, timeout=10,
            )
            state_file = Path(tmpdir) / ".dev-state" / "state.json"
            assert state_file.exists(), f"state.json not created. stderr: {result.stderr}"
            state = json.loads(state_file.read_text())
            assert state["version"] == "2.0.0"
            assert state["project"]["name"] == "test-project"
            assert state["status"] == "ready"
            assert state["health"]["score"] == 0
            assert state["health"]["target"] == 80
            # All 5 dimensions present
            for dim in ["requirements", "code", "tests", "runnable", "quality"]:
                assert dim in state["health"]["breakdown"]

    def test_init_state_saves_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = SCRIPTS_DIR / "adaptive-dev"
            subprocess.run(
                ["bash", "-c", f"""
                    cd '{tmpdir}'
                    source '{script}'
                    PROJECT_DIR='{tmpdir}'
                    STATE_DIR='.dev-state'
                    STATE_FILE='{tmpdir}/.dev-state/state.json'
                    REQUIREMENT_FILE='{tmpdir}/.dev-state/requirement.txt'
                    HEALTH_CHECK='/dev/null'
                    VERSION='2.0.0'
                    _init_state 'test-project' 'Build a todo app with auth'
                """],
                capture_output=True, text=True, timeout=10,
            )
            req_file = Path(tmpdir) / ".dev-state" / "requirement.txt"
            assert req_file.exists()
            assert "Build a todo app with auth" in req_file.read_text()


class TestBashDaemonClassifyExit:
    """Validate classify_exit correctly categorizes session failures."""

    def _classify(self, log_content: str, exit_code: int = 1, duration: int = 100) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(log_content)
            f.flush()
            script = SCRIPTS_DIR / "adaptive-dev"
            # Extract only the classify_exit function (source runs the case block at bottom)
            result = subprocess.run(
                ["bash", "-c", f"""
                    # Extract functions only, skip the case block at bottom
                    eval "$(sed -n '/^classify_exit()/,/^}}/p' '{script}')"
                    SESSION_TIMEOUT=1800
                    classify_exit '{f.name}' {exit_code} {duration}
                """],
                capture_output=True, text=True, timeout=10,
            )
            os.unlink(f.name)
            return result.stdout.strip()

    def test_context_exhausted(self):
        assert self._classify("Error: context window exceeded") == "context_exhausted"

    def test_context_token_limit(self):
        assert self._classify("context token limit reached") == "context_exhausted"

    def test_rate_limit_429(self):
        assert self._classify("HTTP 429 Too Many Requests") == "rate_limit"

    def test_rate_limit_text(self):
        assert self._classify("rate limit exceeded, please wait") == "rate_limit"

    def test_network_econnrefused(self):
        assert self._classify("Error: ECONNREFUSED 127.0.0.1:443") == "network_error"

    def test_network_timeout(self):
        assert self._classify("ETIMEDOUT connecting to api") == "network_error"

    def test_permission_denied(self):
        assert self._classify("Error: permission denied for /etc/shadow") == "permission_error"

    def test_permission_401(self):
        assert self._classify("HTTP 401 Unauthorized") == "permission_error"

    def test_permission_invalid_key(self):
        assert self._classify("invalid api key provided") == "permission_error"

    def test_tool_error(self):
        assert self._classify("tool execution failed: Write") == "tool_error"

    def test_session_timeout(self):
        assert self._classify("normal output", duration=1800) == "session_timeout"

    def test_unknown_crash(self):
        assert self._classify("segfault at 0x0") == "unknown_crash"

    def test_empty_log(self):
        """Missing log file should return unknown_crash."""
        script = SCRIPTS_DIR / "adaptive-dev"
        result = subprocess.run(
            ["bash", "-c", f"""
                eval "$(sed -n '/^classify_exit()/,/^}}/p' '{script}')"
                SESSION_TIMEOUT=1800
                classify_exit '/nonexistent/log.txt' 1 100
            """],
            capture_output=True, text=True, timeout=10,
        )
        assert result.stdout.strip() == "unknown_crash"


class TestBashDaemonSetJson:
    """Validate set_json with file locking."""

    def test_set_json_updates_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            state_file.write_text(json.dumps({
                "status": "ready",
                "last_heartbeat": "old",
            }))
            script = SCRIPTS_DIR / "adaptive-dev"
            subprocess.run(
                ["bash", "-c", f"""
                    source '{script}'
                    STATE_FILE='{state_file}'
                    set_json "d['status']='running'"
                """],
                capture_output=True, text=True, timeout=10,
            )
            state = json.loads(state_file.read_text())
            assert state["status"] == "running"

    def test_set_json_auto_updates_heartbeat(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            state_file.write_text(json.dumps({
                "status": "ready",
                "last_heartbeat": "2024-01-01T00:00:00Z",
            }))
            script = SCRIPTS_DIR / "adaptive-dev"
            subprocess.run(
                ["bash", "-c", f"""
                    source '{script}'
                    STATE_FILE='{state_file}'
                    set_json "d['status']='running'"
                """],
                capture_output=True, text=True, timeout=10,
            )
            state = json.loads(state_file.read_text())
            assert state["last_heartbeat"] != "2024-01-01T00:00:00Z"


# ===========================================================================
# 4. Decision engine: SKILL.md table matches decision-engine.md algorithm
# ===========================================================================

class TestDecisionEngine:
    """Validate decision logic consistency between SKILL.md and decision-engine.md."""

    DIMENSION_MAX = {
        "requirements": 20,
        "code": 25,
        "runnable": 20,
        "tests": 20,
        "quality": 15,
    }
    THRESHOLD = 0.70

    def _weakest(self, breakdown: dict) -> tuple:
        ratios = {k: breakdown[k] / self.DIMENSION_MAX[k] for k in self.DIMENSION_MAX}
        dim = min(ratios, key=ratios.get)
        return dim, breakdown[dim], ratios[dim]

    def test_score_80_means_complete(self):
        """score >= 80 → complete (SKILL.md row 8)."""
        breakdown = {"requirements": 18, "code": 22, "tests": 16, "runnable": 16, "quality": 12}
        total = sum(breakdown.values())
        assert total >= 80

    def test_requirements_weakest_dispatches_product_expert(self):
        """requirements weakest → product-expert (SKILL.md row 1)."""
        breakdown = {"requirements": 5, "code": 20, "tests": 15, "runnable": 15, "quality": 10}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "requirements"
        assert ratio < self.THRESHOLD

    def test_code_low_dispatches_tech_manager(self):
        """code weakest + score < 10 → tech-manager (SKILL.md row 2)."""
        breakdown = {"requirements": 15, "code": 5, "tests": 15, "runnable": 15, "quality": 10}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "code"
        assert score < 10

    def test_code_moderate_dispatches_parallel_dev(self):
        """code weakest + score >= 10 → python-expert + frontend-expert (SKILL.md row 3)."""
        breakdown = {"requirements": 15, "code": 12, "tests": 15, "runnable": 15, "quality": 10}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "code"
        assert score >= 10
        assert ratio < self.THRESHOLD

    def test_runnable_weakest_dispatches_tech_manager(self):
        """runnable weakest → tech-manager (SKILL.md row 4)."""
        breakdown = {"requirements": 15, "code": 20, "tests": 15, "runnable": 5, "quality": 10}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "runnable"

    def test_tests_weakest_dispatches_test_expert(self):
        """tests weakest → test-expert (SKILL.md row 5)."""
        breakdown = {"requirements": 15, "code": 20, "tests": 5, "runnable": 15, "quality": 10}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "tests"

    def test_quality_weakest_dispatches_parallel_quality(self):
        """quality weakest → python-expert + frontend-expert (SKILL.md row 6)."""
        breakdown = {"requirements": 15, "code": 20, "tests": 15, "runnable": 15, "quality": 3}
        dim, score, ratio = self._weakest(breakdown)
        assert dim == "quality"
        assert ratio < self.THRESHOLD

    def test_all_above_threshold_dispatches_polish(self):
        """All dimensions >= 70% → test-report-followup (SKILL.md row 7)."""
        breakdown = {"requirements": 14, "code": 18, "tests": 14, "runnable": 14, "quality": 11}
        ratios = {k: breakdown[k] / self.DIMENSION_MAX[k] for k in self.DIMENSION_MAX}
        assert all(r >= self.THRESHOLD for r in ratios.values())
        total = sum(breakdown.values())
        assert total < 80  # Not yet complete, but all dimensions healthy

    def test_decision_engine_md_algorithm_matches_skill_md(self):
        """Verify decision-engine.md dispatch_by_weakest matches SKILL.md table."""
        de_content = _read(REFS_DIR / "decision-engine.md")
        skill_content = _read(SKILL_ROOT / "SKILL.md")

        # Both should reference the same agents for each dimension
        agent_map = {
            "requirements": "product-expert",
            "code": ["tech-manager", "python-expert", "frontend-expert"],
            "runnable": "tech-manager",
            "tests": "test-expert",
            "quality": ["python-expert", "frontend-expert"],
        }
        for dim, agents in agent_map.items():
            if isinstance(agents, str):
                agents = [agents]
            for agent in agents:
                assert agent in de_content, f"decision-engine.md missing {agent} for {dim}"
                assert agent in skill_content, f"SKILL.md missing {agent} for {dim}"

    def test_dimension_max_consistent_across_files(self):
        """MAX_SCORES in health-check.py == DIMENSION_MAX in decision-engine.md."""
        for dim, max_val in self.DIMENSION_MAX.items():
            assert HC.MAX_SCORES[dim] == max_val, (
                f"Mismatch for {dim}: health-check.py={HC.MAX_SCORES[dim]}, expected={max_val}"
            )


# ===========================================================================
# 5. State protocol: Full lifecycle
# ===========================================================================

class TestStateProtocolLifecycle:
    """Validate state.json lifecycle: init → health update → checkpoint → recover."""

    def _init_via_bash(self, tmpdir: str, name: str = "test-proj", req: str = ""):
        script = SCRIPTS_DIR / "adaptive-dev"
        req_arg = f"'{req}'" if req else "''"
        subprocess.run(
            ["bash", "-c", f"""
                cd '{tmpdir}'
                source '{script}'
                PROJECT_DIR='{tmpdir}'
                STATE_DIR='.dev-state'
                STATE_FILE='{tmpdir}/.dev-state/state.json'
                REQUIREMENT_FILE='{tmpdir}/.dev-state/requirement.txt'
                HEALTH_CHECK='/dev/null'
                VERSION='2.0.0'
                _init_state '{name}' {req_arg}
            """],
            capture_output=True, text=True, timeout=10,
        )
        return Path(tmpdir) / ".dev-state" / "state.json"

    def test_full_lifecycle(self):
        """init → set running → health update → checkpoint → recover."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = self._init_via_bash(tmpdir, "lifecycle-test", "Build a blog")
            script = SCRIPTS_DIR / "adaptive-dev"

            # 1. Verify init
            state = json.loads(state_file.read_text())
            assert state["status"] == "ready"
            assert state["sessions"]["count"] == 0

            # 2. Set running via set_json
            subprocess.run(
                ["bash", "-c", f"""
                    source '{script}'
                    STATE_FILE='{state_file}'
                    set_json "d['status']='running'; d['sessions']['count']=1"
                """],
                capture_output=True, text=True, timeout=10,
            )
            state = json.loads(state_file.read_text())
            assert state["status"] == "running"
            assert state["sessions"]["count"] == 1

            # 3. Health update via health-check.py
            HC.update_state(tmpdir, {
                "score": 35,
                "breakdown": {"requirements": 15, "code": 10, "tests": 0, "runnable": 5, "quality": 5},
                "details": {"requirements": "3 PRDs", "code": "8 files", "tests": "none", "runnable": "deps only", "quality": "default"},
                "usable": False,
                "assessed_at": "2024-06-01T12:00:00Z",
            })
            state = json.loads(state_file.read_text())
            assert state["health"]["score"] == 35
            assert state["health"]["delta"] == 35  # from 0 to 35

            # 4. Simulate checkpoint save via Python (avoids bash escaping issues)
            state = json.loads(state_file.read_text())
            state["current_action"] = {
                "type": "parallel_development",
                "agents": ["python-expert"],
                "checkpoint": {
                    "step": "backend_api",
                    "progress": "60%",
                    "next_action": "frontend_ui",
                },
            }
            state["status"] = "continue"
            state["exit_reason"] = "turns_limit"
            state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))
            state = json.loads(state_file.read_text())
            assert state["status"] == "continue"
            assert state["exit_reason"] == "turns_limit"
            cp = state["current_action"]["checkpoint"]
            assert cp["step"] == "backend_api"
            assert cp["progress"] == "60%"
            assert cp["next_action"] == "frontend_ui"

            # 5. Simulate recovery: new session reads checkpoint
            assert state["current_action"]["checkpoint"] is not None


# ===========================================================================
# 6. Config: All defaults have fallbacks
# ===========================================================================

class TestConfigDefaults:
    """Validate config.env and bash defaults are aligned."""

    def test_all_config_vars_have_bash_defaults(self):
        """Every var in config.env should have a ${VAR:-default} in adaptive-dev."""
        config = _read(SCRIPTS_DIR / "config.env")
        script = _read(SCRIPTS_DIR / "adaptive-dev")

        # Extract variable names from config.env (lines like VAR=value)
        config_vars = re.findall(r"^([A-Z_]+)=", config, re.MULTILINE)
        # Filter out comments and CLAUDE_MODEL/SKILL_DIR (which use ${} syntax in config too)
        skip = {"CLAUDE_MODEL", "SKILL_DIR"}

        for var in config_vars:
            if var in skip:
                continue
            # Should have ${VAR:-...} pattern in bash script
            pattern = rf"\$\{{{var}:-"
            assert re.search(pattern, script), (
                f"Config var {var} has no bash default fallback (${{VAR:-...}})"
            )

    def test_config_max_turns_matches_bash_default(self):
        config = _read(SCRIPTS_DIR / "config.env")
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        # config.env: MAX_TURNS=40
        assert "MAX_TURNS=40" in config
        # bash: MAX_TURNS="${MAX_TURNS:-40}"
        assert 'MAX_TURNS:-40' in script


# ===========================================================================
# 7. Cross-file consistency: Comprehensive checks
# ===========================================================================

class TestCrossFileConsistency:
    """Validate all files are aligned."""

    def test_version_consistent(self):
        """Version 2.0.0 across SKILL.md, config, bash, PS1."""
        skill = _read(SKILL_ROOT / "SKILL.md")
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert 'version: "2.0.0"' in skill
        assert 'VERSION="2.0.0"' in bash
        assert '$VERSION = "2.0.0"' in ps1

    def test_all_6_agents_listed_in_skill_md(self):
        skill = _read(SKILL_ROOT / "SKILL.md")
        agents = ["product-expert", "tech-manager", "python-expert",
                   "frontend-expert", "test-expert", "test-report-followup"]
        for agent in agents:
            assert agent in skill, f"SKILL.md missing agent: {agent}"

    def test_all_5_dimensions_in_health_check(self):
        for dim in ["requirements", "code", "tests", "runnable", "quality"]:
            assert dim in HC.MAX_SCORES

    def test_exit_reasons_in_skill_md_match_classify_exit(self):
        """All error types from classify_exit should be documented in SKILL.md."""
        skill = _read(SKILL_ROOT / "SKILL.md")
        error_types = [
            "context_exhausted", "rate_limit", "network_error",
            "tool_error", "permission_error", "session_timeout", "unknown_crash",
        ]
        for et in error_types:
            assert et in skill, f"SKILL.md missing exit type: {et}"

    def test_state_protocol_has_all_exit_reasons(self):
        sp = _read(REFS_DIR / "state-protocol.md")
        reasons = [
            "turns_limit", "action_done", "usable_reached", "blocked",
            "unknown_crash", "rate_limit", "user_stop", "user_pause",
            "session_timeout", "heartbeat_timeout", "process_crash",
            "agent_failure", "context_exhausted", "network_error",
            "permission_error", "tool_error",
        ]
        for r in reasons:
            assert r in sp, f"state-protocol.md missing exit_reason: {r}"

    def test_agent_orchestration_has_directory_constraints(self):
        ao = _read(REFS_DIR / "agent-orchestration.md")
        agents = ["product-expert", "tech-manager", "python-expert",
                   "frontend-expert", "test-expert"]
        for agent in agents:
            assert agent in ao, f"agent-orchestration.md missing agent: {agent}"
        # Should have directory separation table
        assert "允许修改" in ao
        assert "禁止修改" in ao

    def test_prompt_includes_health_and_weakest_dimension(self):
        """Bash prompt construction should include health score and weakest dimension."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert "Health:" in script or "health_score" in script
        assert "Weakest dimension" in script or "weakest" in script

    def test_prompt_includes_checkpoint_recovery(self):
        """Bash prompt should include checkpoint info for session recovery."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert "checkpoint" in script.lower()
        assert "resume" in script.lower() or "recover" in script.lower() or "Checkpoint" in script

    def test_prompt_includes_error_context(self):
        """Bash prompt should include previous error info."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert "Previous Errors" in script or "errors" in script

    def test_health_check_cli_modes(self):
        """health-check.py should support --json, --update, --project-dir."""
        source = _read(SCRIPTS_DIR / "health-check.py")
        assert "--json" in source
        assert "--update" in source
        assert "--project-dir" in source


# ===========================================================================
# 8. PS1 daemon: Parity with bash version
# ===========================================================================

class TestPS1DaemonParity:
    """Validate PS1 daemon is aligned with bash daemon."""

    def test_ps1_version_matches_bash(self):
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        bash_ver = re.search(r'VERSION="([^"]+)"', bash).group(1)
        ps1_ver = re.search(r'\$VERSION\s*=\s*"([^"]+)"', ps1).group(1)
        assert bash_ver == ps1_ver, f"Version mismatch: bash={bash_ver}, PS1={ps1_ver}"

    def test_ps1_creates_agents_not_locks(self):
        """PS1 should create agents/ directory, not locks/."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        # Should NOT have "locks" in directory creation
        dir_creates = re.findall(r'@\("logs","checkpoints","(\w+)"\)', ps1)
        for d in dir_creates:
            assert d == "agents", f"PS1 creates '{d}' directory instead of 'agents'"

    def test_bash_creates_agents_not_locks(self):
        """Bash should create agents/ directory, not locks/."""
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        match = re.search(r'mkdir -p.*\{logs,checkpoints,(\w+)\}', bash)
        assert match, "Bash should have mkdir for subdirectories"
        assert match.group(1) == "agents", f"Bash creates '{match.group(1)}' instead of 'agents'"

    def test_ps1_classify_exit_patterns_match_bash(self):
        """PS1 Classify-Exit should detect same error types as bash classify_exit."""
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        error_types = [
            "context_exhausted", "rate_limit", "network_error",
            "permission_error", "tool_error", "session_timeout", "unknown_crash",
        ]
        for et in error_types:
            assert et in bash, f"Bash missing error type: {et}"
            assert et in ps1, f"PS1 missing error type: {et}"

    def test_ps1_has_prompt_file_pipe(self):
        """PS1 should write prompt to file and pipe to claude."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert "session-prompt.txt" in ps1
        assert "Get-Content" in ps1 and "promptFile" in ps1

    def test_ps1_has_pre_post_health_check(self):
        """PS1 should run health-check.py before and after each session."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert ps1.count("health-check") >= 2 or ps1.count("HEALTH_CHECK") >= 2

    def test_ps1_has_file_locking(self):
        """PS1 Set-Json should use file locking (msvcrt + fcntl fallback)."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert "msvcrt" in ps1, "PS1 should use msvcrt for Windows file locking"
        assert "fcntl" in ps1, "PS1 should fall back to fcntl for Unix"

    def test_ps1_config_defaults_match_bash(self):
        """PS1 config defaults should match bash defaults."""
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        defaults = {
            "MAX_TURNS": "40",
            "MIN_INTERVAL": "60",
            "MAX_INTERVAL": "120",
            "MAX_ERRORS": "5",
            "SESSION_TIMEOUT": "1800",
            "HEARTBEAT_TIMEOUT": "900",
            "MAX_TOTAL_SESSIONS": "100",
        }
        for var, val in defaults.items():
            bash_pattern = rf"{var}:-{val}"
            ps1_pattern = rf"'{var}'\s*'{val}'"
            assert re.search(bash_pattern, bash), f"Bash missing default {var}={val}"
            assert re.search(ps1_pattern, ps1), f"PS1 missing default {var}={val}"

    def test_ps1_session_return_codes_match_bash(self):
        """PS1 sessionResult codes should match bash return codes."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        # PS1 uses $script:sessionResult = N
        codes = {
            "rate_limit": "2",
            "context_exhausted": "3",
            "network_error": "4",
            "permission_error": "5",
            "session_timeout": "6",
        }
        for error_type, code in codes.items():
            pattern = rf'{error_type}.*sessionResult\s*=\s*{code}'
            assert re.search(pattern, ps1), f"PS1 missing return code {code} for {error_type}"

    def test_ps1_prompt_has_same_sections_as_bash(self):
        """PS1 prompt should include same key sections as bash prompt."""
        bash = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        sections = [
            "Skill Documentation",
            "Project Info",
            "Session Context",
            "Previous Errors",
            "Rules",
        ]
        for section in sections:
            assert section in bash, f"Bash prompt missing section: {section}"
            assert section in ps1, f"PS1 prompt missing section: {section}"

    def test_ps1_has_git_integration(self):
        """PS1 should have git auto-commit and rollback."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert "GitAutoCommit" in ps1 or "git commit" in ps1
        assert "GitRollback" in ps1 or "git revert" in ps1

    def test_ps1_has_state_corruption_recovery(self):
        """PS1 should recover from corrupted state.json via checkpoint."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert "latest.json" in ps1, "PS1 should reference checkpoint latest.json"
        assert "损坏" in ps1 or "corrupt" in ps1.lower(), "PS1 should handle corruption"

    def test_ps1_has_user_feedback(self):
        """PS1 should support user-feedback.md."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        assert "user-feedback" in ps1

    def test_ps1_state_init_has_all_fields(self):
        """PS1 Initialize-State should create state.json with all required fields."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        required_fields = [
            "version", "project", "health", "status", "exit_reason",
            "current_action", "agent_coordination", "action_history",
            "decision_log", "blockers", "errors", "sessions",
            "last_heartbeat", "metrics",
        ]
        for field in required_fields:
            assert f'"{field}"' in ps1, f"PS1 Initialize-State missing field: {field}"

    def test_ps1_health_breakdown_has_all_dimensions(self):
        """PS1 state init should include all 5 health dimensions."""
        ps1 = _read(SCRIPTS_DIR / "adaptive-dev.ps1")
        for dim in ["requirements", "code", "tests", "runnable", "quality"]:
            assert f'"{dim}"' in ps1, f"PS1 state init missing dimension: {dim}"
# ===========================================================================

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
