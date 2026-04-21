#!/usr/bin/env python3
"""
Independent project health assessment for adaptive-dev-engine.
Run by daemon BEFORE and AFTER each Claude session.
Replaces AI self-evaluation with deterministic, reproducible scoring.

Usage:
    python3 health-check.py                          # Print human-readable report
    python3 health-check.py --json                   # Output JSON
    python3 health-check.py --update                 # Write results to state.json
    python3 health-check.py --project-dir /path      # Specify project directory
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MAX_SCORES = {
    "requirements": 20,
    "code": 25,
    "tests": 20,
    "runnable": 20,
    "quality": 15,
}

EXCLUDE_DIRS = {"venv", ".venv", "node_modules", ".dev-state", "__pycache__", ".git", ".tox", "dist", "build"}
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".php"}


def count_code_files(project_dir: str) -> int:
    count = 0
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if Path(f).suffix in CODE_EXTENSIONS:
                count += 1
    return count


def score_requirements(project_dir: str) -> tuple:
    """Score requirements clarity: 0-20"""
    prd_dir = Path(project_dir) / "docs" / "prd"
    prd_count = len(list(prd_dir.glob("*.md"))) if prd_dir.is_dir() else 0

    has_prd = (Path(project_dir) / "PRD.md").exists()
    has_readme = (Path(project_dir) / "README.md").exists()
    has_req = (Path(project_dir) / "requirements.md").exists()

    if prd_count >= 4:
        return 20, f"{prd_count} PRD docs (complete)"
    elif prd_count >= 2 or has_prd:
        return 15, f"{prd_count} PRD docs, PRD.md={has_prd}"
    elif prd_count >= 1 or has_req:
        return 10, f"{prd_count} PRD docs"
    elif has_readme:
        return 5, "README.md only"
    else:
        return 0, "No requirements found"


def score_code(project_dir: str) -> tuple:
    """Score code completeness: 0-25"""
    code_count = count_code_files(project_dir)

    # Check for API endpoints (pure Python, no grep dependency)
    import re
    api_count = 0
    api_pattern = re.compile(r"@(app|router|api)\.")
    for subdir in ["src", "app", "backend", "server", "api", "routes", "handlers", "lib"]:
        search_dir = Path(project_dir) / subdir
        if not search_dir.exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for fname in files:
                if Path(fname).suffix in CODE_EXTENSIONS:
                    try:
                        text = (Path(root) / fname).read_text(errors="ignore")
                        if api_pattern.search(text):
                            api_count += 1
                    except OSError:
                        pass

    if code_count >= 50 and api_count >= 5:
        return 25, f"{code_count} files, {api_count} API modules"
    elif code_count >= 30:
        return 20, f"{code_count} files (mostly complete)"
    elif code_count >= 15:
        return 15, f"{code_count} files (partial)"
    elif code_count >= 5:
        return 10, f"{code_count} files (skeleton)"
    elif code_count >= 1:
        return 5, f"{code_count} files (minimal)"
    else:
        return 0, "No code files"


def score_tests(project_dir: str) -> tuple:
    """Score test coverage: 0-20"""
    import fnmatch
    test_patterns = [
        "test_*.py", "*_test.py", "*.test.ts", "*.spec.ts",
        "*.test.js", "*.spec.js", "*.test.tsx", "*.spec.tsx",
    ]
    test_count = 0
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if any(fnmatch.fnmatch(f, p) for p in test_patterns):
                test_count += 1

    # Try collecting tests with pytest (no execution)
    pytest_ok = False
    try:
        result = subprocess.run(
            ["pytest", "--tb=no", "-q", "--co"],
            cwd=project_dir, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and "test" in result.stdout.lower():
            pytest_ok = True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if test_count >= 10 and pytest_ok:
        return 20, f"{test_count} test files, pytest OK"
    elif test_count >= 10:
        return 15, f"{test_count} test files"
    elif test_count >= 5:
        return 12, f"{test_count} test files"
    elif test_count >= 2:
        return 8, f"{test_count} test files"
    elif test_count >= 1:
        return 5, f"{test_count} test file"
    else:
        return 0, "No test files"


def _try_start(project_dir: str, cmd: str) -> bool:
    """Safely try to start project using process group isolation."""
    import socket
    proc = None
    try:
        # Pre-check: record ports already in use (avoid false positives)
        pre_open = set()
        for port in [8000, 3000, 5000, 8080]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    if s.connect_ex(("127.0.0.1", port)) == 0:
                        pre_open.add(port)
            except OSError:
                pass

        kwargs = {"shell": True, "cwd": project_dir,
                  "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        # Process group isolation (Unix only)
        if hasattr(os, "setsid"):
            kwargs["preexec_fn"] = os.setsid
        proc = subprocess.Popen(cmd, **kwargs)
        time.sleep(8)

        if proc.poll() is not None:
            return False  # Process already exited

        for port in [8000, 3000, 5000, 8080]:
            if port in pre_open:
                continue  # Was already open before we started
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(("127.0.0.1", port))
                if result == 0:
                    return True
            except OSError:
                continue
            finally:
                if sock:
                    try:
                        sock.close()
                    except OSError:
                        pass
        return False
    except Exception:
        return False
    finally:
        if proc and proc.poll() is None:
            try:
                if hasattr(os, "killpg"):
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                else:
                    proc.terminate()
            except (ProcessLookupError, OSError):
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except OSError:
                    pass
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass  # Process truly stuck


def score_runnable(project_dir: str) -> tuple:
    """Score runnability: 0-20. Tries actual startup."""
    p = Path(project_dir)
    has_start = (p / "start.sh").exists()
    has_docker = (p / "docker-compose.yml").exists()
    has_package = (p / "package.json").exists()
    has_pyproject = (p / "pyproject.toml").exists()
    has_req_txt = (p / "requirements.txt").exists()

    has_main = any([
        (p / "src" / "main.py").exists(),
        (p / "app" / "main.py").exists(),
        (p / "main.py").exists(),
    ])
    has_index = any([
        (p / "src" / "index.ts").exists(),
        (p / "src" / "index.js").exists(),
    ])

    can_start = False
    if has_start:
        can_start = _try_start(project_dir, "./start.sh")
    elif has_main:
        can_start = _try_start(project_dir, "python3 -m uvicorn src.main:app --port 8000")
        if not can_start:
            can_start = _try_start(project_dir, "python3 -m uvicorn app.main:app --port 8000")
    elif has_package and has_index:
        can_start = _try_start(project_dir, "npm start")

    if can_start:
        return 20, "Starts and responds"
    elif has_start and (has_main or has_index):
        return 15, "Has start script + entry point"
    elif (has_pyproject or has_package) and (has_main or has_index):
        return 10, "Has deps + entry point"
    elif has_pyproject or has_package or has_req_txt:
        return 5, "Has dependency config"
    else:
        return 0, "No runnable config"


def score_quality(project_dir: str) -> tuple:
    """Score code quality: 0-15"""
    lint_errors = -1

    # Try ruff for Python projects
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--quiet", "--statistics"],
            cwd=project_dir, capture_output=True, text=True, timeout=30,
        )
        lint_errors = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        if result.returncode == 0:
            lint_errors = 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try eslint for JS/TS projects (if ruff not available)
    if lint_errors < 0 and (Path(project_dir) / "package.json").exists():
        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--quiet", "--format", "compact"],
                cwd=project_dir, capture_output=True, text=True, timeout=60,
            )
            lint_errors = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            if result.returncode == 0:
                lint_errors = 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    if lint_errors == 0:
        return 15, "No lint errors"
    elif 0 < lint_errors < 10:
        return 10, f"{lint_errors} lint issues"
    elif lint_errors >= 10:
        return 5, f"{lint_errors} lint issues"
    else:
        return 6, "Linter not available, default"

def _parse_python_imports(text: str) -> list:
    """Use Python ast to extract import targets from .py files."""
    import ast as _ast
    imports = []
    try:
        tree = _ast.parse(text)
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, _ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except (SyntaxError, ValueError):
        pass
    return imports


def _parse_python_signatures(text: str) -> tuple:
    """Use Python ast to extract class and function signatures from .py files."""
    import ast as _ast
    classes = []
    functions = []
    try:
        tree = _ast.parse(text)
        for node in _ast.iter_child_nodes(tree):
            if isinstance(node, _ast.ClassDef):
                bases = ", ".join(
                    getattr(b, "id", getattr(b, "attr", "?"))
                    for b in node.bases
                )
                classes.append((node.name, bases))
                # Extract methods
                for item in _ast.iter_child_nodes(node):
                    if isinstance(item, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                        args = ", ".join(a.arg for a in item.args.args)
                        functions.append((f"{node.name}.{item.name}", args))
            elif isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                args = ", ".join(a.arg for a in node.args.args)
                functions.append((node.name, args))
    except (SyntaxError, ValueError):
        pass
    return classes, functions


def _parse_js_ts_imports(text: str) -> list:
    """Extract import/require targets from JS/TS files using regex."""
    import re
    imports = []
    # ES module: import ... from "module"
    es_pattern = re.compile(r'''import\s+.*?\s+from\s+['"](.*?)['"]''', re.MULTILINE)
    # CommonJS: require("module")
    cjs_pattern = re.compile(r'''require\s*\(\s*['"](.*?)['"]\s*\)''')
    # Dynamic import: import("module")
    dyn_pattern = re.compile(r'''import\s*\(\s*['"](.*?)['"]\s*\)''')
    for pat in [es_pattern, cjs_pattern, dyn_pattern]:
        imports.extend(pat.findall(text))
    return imports


def _parse_js_ts_signatures(text: str) -> tuple:
    """Extract class and function signatures from JS/TS files using regex."""
    import re
    classes = []
    functions = []
    class_pattern = re.compile(
        r'^\s*(?:export\s+)?(?:abstract\s+)?(?:class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?',
        re.MULTILINE,
    )
    func_pattern = re.compile(
        r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*(\([^)]*\))',
        re.MULTILINE,
    )
    for m in class_pattern.finditer(text):
        classes.append((m.group(1), m.group(2) or ""))
    for m in func_pattern.finditer(text):
        functions.append((m.group(1), m.group(2)))
    return classes, functions


def generate_repomap(project_dir: str) -> bool:
    """Generate an AST-based structure of the project with import relationships.

    Output format per file:
        File: relative/path.py
          class ClassName(Base1, Base2)
            def ClassName.method(self, arg)
          def top_level_func(arg1, arg2)
          → imports: module1, module2
    """
    map_file = Path(project_dir) / ".dev-state" / "repomap.txt"
    try:
        if not map_file.parent.exists():
            map_file.parent.mkdir(parents=True, exist_ok=True)

        output = []
        file_count = 0
        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in sorted(files):
                suffix = Path(f).suffix
                if suffix not in CODE_EXTENSIONS:
                    continue
                try:
                    filepath = Path(root) / f
                    rel_path = filepath.relative_to(project_dir)
                    text = filepath.read_text(errors="ignore")

                    # Dispatch to language-specific parsers
                    if suffix == ".py":
                        classes, functions = _parse_python_signatures(text)
                        imports = _parse_python_imports(text)
                    elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
                        classes, functions = _parse_js_ts_signatures(text)
                        imports = _parse_js_ts_imports(text)
                    else:
                        # Fallback minimal regex for other languages
                        import re
                        classes = [
                            (m.group(2), "")
                            for m in re.finditer(
                                r'^\s*(class|interface|struct)\s+(\w+)',
                                text, re.MULTILINE,
                            )
                        ]
                        functions = [
                            (m.group(2), m.group(3))
                            for m in re.finditer(
                                r'^\s*(def|func|fn|function)\s+(\w+)\s*(\([^)]*\))',
                                text, re.MULTILINE,
                            )
                        ]
                        imports = []

                    if not (classes or functions or imports):
                        continue

                    output.append(f"File: {rel_path}")
                    for name, bases in classes:
                        base_str = f"({bases})" if bases else ""
                        output.append(f"  class {name}{base_str}")
                    for name, args in functions:
                        arg_str = f"({args})" if not args.startswith("(") else args
                        output.append(f"  def {name}{arg_str}")
                    if imports:
                        output.append(f"  → imports: {', '.join(imports)}")
                    output.append("")
                    file_count += 1
                except OSError:
                    pass

        header = f"# RepoMap — {file_count} files analyzed at {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        map_file.write_text(header + "\n".join(output))
        return True
    except Exception:
        return False


def assess(project_dir: str) -> dict:
    """Run full health assessment."""
    scorers = {
        "requirements": score_requirements,
        "code": score_code,
        "tests": score_tests,
        "runnable": score_runnable,
        "quality": score_quality,
    }

    breakdown = {}
    details = {}
    for dim, fn in scorers.items():
        try:
            score, detail = fn(project_dir)
        except Exception as e:
            score, detail = 0, f"Error: {e}"
        breakdown[dim] = score
        details[dim] = detail

    total = sum(breakdown.values())

    return {
        "score": total,
        "breakdown": breakdown,
        "details": details,
        "usable": total >= 80,
        "assessed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def update_state(project_dir: str, health: dict):
    """Write health results into state.json with file locking."""
    state_file = Path(project_dir) / ".dev-state" / "state.json"
    try:
        f = open(state_file, "r+")
    except (FileNotFoundError, OSError):
        return

    with f:
        # Cross-platform file locking
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            lock_release = lambda: fcntl.flock(f, fcntl.LOCK_UN)
        except ImportError:
            try:
                import msvcrt
                sz = max(os.path.getsize(state_file), 1)
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, sz)
                lock_release = lambda: (f.seek(0), msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, sz))
            except ImportError:
                lock_release = lambda: None
        try:
            try:
                state = json.load(f)
            except json.JSONDecodeError:
                # Corrupted state.json - try backup
                backup = state_file.with_suffix(".json.bak")
                if backup.exists():
                    try:
                        state = json.loads(backup.read_text())
                    except (json.JSONDecodeError, OSError):
                        return  # Both files corrupted
                else:
                    return  # finally block handles lock release

            old_score = state.get("health", {}).get("score", 0)
            history = state.get("health", {}).get("history", [])
            history.append({"timestamp": health["assessed_at"], "score": health["score"]})
            history = history[-20:]

            state["health"] = {
                "score": health["score"],
                "breakdown": health["breakdown"],
                "details": health["details"],
                "usable": health["usable"],
                "target": 80,
                "assessed_at": health["assessed_at"],
                "history": history,
                "delta": health["score"] - old_score,
            }
            state["last_heartbeat"] = health["assessed_at"]

            if health["usable"]:
                state["status"] = "completed"
                state["exit_reason"] = "usable_reached"

            f.seek(0)
            f.truncate()
            json.dump(state, f, indent=2, ensure_ascii=False)
        finally:
            lock_release()


def main():
    parser = argparse.ArgumentParser(description="Project health assessment")
    parser.add_argument("--project-dir", default=os.getcwd())
    parser.add_argument("--update", action="store_true", help="Update state.json")
    parser.add_argument("--json", action="store_true", help="JSON output only")
    parser.add_argument("--repomap", action="store_true", help="Generate RepoMap AST in .dev-state/repomap.txt")
    args = parser.parse_args()

    health = assess(args.project_dir)

    if args.update:
        update_state(args.project_dir, health)

    if args.update or args.repomap:
        generate_repomap(args.project_dir)

    if args.json:
        print(json.dumps(health))
    else:
        label = "USABLE" if health["usable"] else "IN PROGRESS"
        print(f"Health: {health['score']}/100 [{label}]")
        for dim, score in health["breakdown"].items():
            print(f"  {dim}: {score}/{MAX_SCORES[dim]} - {health['details'][dim]}")

    sys.exit(0 if health["usable"] else 1)


if __name__ == "__main__":
    main()
