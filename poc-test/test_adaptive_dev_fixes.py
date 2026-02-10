#!/usr/bin/env python3
"""
Unit tests for adaptive-dev-engine v2.0 review fixes.

Tests:
  P1: Bash daemon prompt file pipe approach
  P2: health-check.py expanded API search directories
  P2: state-protocol.md directory structure (no locks/)
  P2: health-assessment.md deprecated script warning
  P2: .gitignore covers __pycache__
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent / "skills" / "adaptive-dev-engine"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REFS_DIR = SKILL_ROOT / "references"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ===========================================================================
# P1: Bash daemon uses prompt file + pipe (not CLI argument)
# ===========================================================================

class TestP1BashPromptFile:
    """Verify the bash daemon writes prompt to a temp file and pipes it."""

    def test_no_direct_prompt_argument(self):
        """adaptive-dev should NOT pass $prompt as a CLI argument to claude."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        # Old pattern: claude ... "$prompt"
        # Should NOT exist anymore
        bad_pattern = re.compile(
            r'claude\s+--print.*"\$prompt"'
        )
        matches = bad_pattern.findall(script)
        assert not matches, (
            f"Found direct $prompt CLI argument (ARG_MAX risk): {matches}"
        )

    def test_prompt_written_to_file(self):
        """adaptive-dev should write prompt to session-prompt.txt."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert "session-prompt.txt" in script, (
            "Script should write prompt to session-prompt.txt"
        )

    def test_prompt_piped_via_cat(self):
        """adaptive-dev should pipe prompt file to claude via cat."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert "cat" in script and "session-prompt.txt" in script, (
            "Script should use 'cat session-prompt.txt | claude'"
        )

    def test_printf_writes_prompt(self):
        """adaptive-dev should use printf to write prompt (preserves content)."""
        script = _read(SCRIPTS_DIR / "adaptive-dev")
        assert re.search(r"printf\s+'%s'\s+\"\$prompt\"\s*>\s*\"\$prompt_file\"", script), (
            "Script should use printf '%s' \"$prompt\" > \"$prompt_file\""
        )


# ===========================================================================
# P2: health-check.py expanded API search directories
# ===========================================================================

class TestP2ExpandedApiDirs:
    """Verify health-check.py searches more directories for API endpoints."""

    EXPECTED_DIRS = ["src", "app", "backend", "server", "api", "routes", "handlers", "lib"]

    def test_all_dirs_in_score_code(self):
        """score_code() should search all expected directories."""
        source = _read(SCRIPTS_DIR / "health-check.py")
        for d in self.EXPECTED_DIRS:
            assert f'"{d}"' in source, (
                f"health-check.py score_code() missing search directory: {d}"
            )

    def test_score_code_finds_api_in_routes_dir(self):
        """score_code() should detect API endpoints in routes/ directory."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import importlib
            hc = importlib.import_module("health-check")
        except ImportError:
            # Module name has hyphen; use importlib workaround
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "health_check", SCRIPTS_DIR / "health-check.py"
            )
            hc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hc)
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a project with API files ONLY in routes/
            routes_dir = Path(tmpdir) / "routes"
            routes_dir.mkdir()
            for i in range(6):
                (routes_dir / f"route_{i}.py").write_text(
                    f"@app.get('/item/{i}')\ndef get_item_{i}(): pass\n"
                )
            # Also add enough code files to reach threshold
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            for i in range(50):
                (src_dir / f"mod_{i}.py").write_text(f"# module {i}\n")

            score, detail = hc.score_code(tmpdir)
            assert score == 25, (
                f"Expected score 25 (50+ files, 5+ API modules), got {score}: {detail}"
            )
            assert "API" in detail, f"Detail should mention API modules: {detail}"

    def test_score_code_finds_api_in_handlers_dir(self):
        """score_code() should detect API endpoints in handlers/ directory."""
        sys.path.insert(0, str(SCRIPTS_DIR))
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "health_check", SCRIPTS_DIR / "health-check.py"
            )
            hc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hc)
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as tmpdir:
            handlers_dir = Path(tmpdir) / "handlers"
            handlers_dir.mkdir()
            for i in range(6):
                (handlers_dir / f"handler_{i}.py").write_text(
                    f"@router.post('/action/{i}')\ndef action_{i}(): pass\n"
                )
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            for i in range(50):
                (src_dir / f"mod_{i}.py").write_text(f"# module {i}\n")

            score, detail = hc.score_code(tmpdir)
            assert score == 25, (
                f"Expected score 25, got {score}: {detail}"
            )


# ===========================================================================
# P2: Reference docs - deprecated code warnings
# ===========================================================================

class TestP2ReferenceDocCleanup:
    """Verify reference docs properly mark deprecated code."""

    def test_health_assessment_deprecated_warning(self):
        """health-assessment.md should warn against using old script."""
        content = _read(REFS_DIR / "health-assessment.md")
        assert "请勿使用" in content or "不应" in content, (
            "health-assessment.md should contain deprecation warning"
        )

    def test_health_assessment_details_collapsed(self):
        """health-assessment.md old script should be in <details> block."""
        content = _read(REFS_DIR / "health-assessment.md")
        assert "<details>" in content, (
            "Old script should be wrapped in <details> for collapse"
        )
        assert "</details>" in content, (
            "Old script <details> block should be properly closed"
        )

    def test_state_protocol_update_health_deprecated(self):
        """state-protocol.md update_health() should have deprecation notice."""
        content = _read(REFS_DIR / "state-protocol.md")
        # Find the update_health section
        idx = content.find("update_health")
        assert idx != -1, "state-protocol.md should contain update_health"
        # Check nearby text for deprecation warning
        context = content[max(0, idx - 200):idx + 200]
        assert "health-check.py" in context, (
            "update_health section should reference health-check.py as replacement"
        )
        assert "不应" in context or "请勿" in context or "替代" in context, (
            "update_health section should warn against direct usage"
        )

    def test_state_protocol_no_locks_dir(self):
        """state-protocol.md directory structure should not reference locks/."""
        content = _read(REFS_DIR / "state-protocol.md")
        # Find the directory structure section
        dir_section_match = re.search(
            r"状态文件位置.*?```(.*?)```", content, re.DOTALL
        )
        assert dir_section_match, "Should have directory structure section"
        dir_tree = dir_section_match.group(1)
        assert "locks/" not in dir_tree, (
            "Directory structure should not reference locks/ (removed in v2.0)"
        )

    def test_state_protocol_has_agents_dir(self):
        """state-protocol.md directory structure should include agents/."""
        content = _read(REFS_DIR / "state-protocol.md")
        dir_section_match = re.search(
            r"状态文件位置.*?```(.*?)```", content, re.DOTALL
        )
        assert dir_section_match, "Should have directory structure section"
        dir_tree = dir_section_match.group(1)
        assert "agents/" in dir_tree, (
            "Directory structure should include agents/ (per agent-orchestration.md)"
        )


# ===========================================================================
# P2: .gitignore covers __pycache__
# ===========================================================================

class TestP2Gitignore:
    """Verify .gitignore properly excludes __pycache__."""

    def test_gitignore_exists(self):
        """adaptive-dev-engine should have a .gitignore file."""
        gitignore = SKILL_ROOT / ".gitignore"
        assert gitignore.exists(), f".gitignore not found at {gitignore}"

    def test_gitignore_excludes_pycache(self):
        """.gitignore should exclude __pycache__/."""
        content = _read(SKILL_ROOT / ".gitignore")
        assert "__pycache__" in content, (
            ".gitignore should contain __pycache__ exclusion"
        )

    def test_pycache_not_tracked(self):
        """__pycache__ should not be tracked by git."""
        result = subprocess.run(
            ["git", "ls-files", "--cached", "skills/adaptive-dev-engine/scripts/__pycache__/"],
            capture_output=True, text=True,
            cwd=SKILL_ROOT.parent.parent,
        )
        tracked = result.stdout.strip()
        assert not tracked, (
            f"__pycache__ files still tracked by git: {tracked}"
        )


# ===========================================================================
# Cross-file consistency checks
# ===========================================================================

class TestCrossFileConsistency:
    """Verify consistency across files after fixes."""

    def test_bash_and_ps1_both_use_file_pipe(self):
        """Both bash and PS1 should use file-based prompt delivery."""
        bash_script = _read(SCRIPTS_DIR / "adaptive-dev")
        ps1_script = _read(SCRIPTS_DIR / "adaptive-dev.ps1")

        assert "session-prompt" in bash_script, (
            "Bash should use session-prompt file"
        )
        assert "session-prompt" in ps1_script or "promptFile" in ps1_script, (
            "PS1 should use prompt file"
        )

    def test_health_check_max_scores_match_docs(self):
        """health-check.py MAX_SCORES should match state-protocol.md."""
        hc_source = _read(SCRIPTS_DIR / "health-check.py")
        sp_content = _read(REFS_DIR / "state-protocol.md")

        # Extract MAX_SCORES from health-check.py
        match = re.search(r"MAX_SCORES\s*=\s*\{([^}]+)\}", hc_source)
        assert match, "health-check.py should define MAX_SCORES"

        # Verify each dimension range in state-protocol.md
        expected = {
            "requirements": 20,
            "code": 25,
            "tests": 20,
            "runnable": 20,
            "quality": 15,
        }
        for dim, max_val in expected.items():
            pattern = rf"{dim}.*0-{max_val}"
            assert re.search(pattern, sp_content), (
                f"state-protocol.md should show {dim}: 0-{max_val}"
            )


# ===========================================================================
# Runner
# ===========================================================================

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
