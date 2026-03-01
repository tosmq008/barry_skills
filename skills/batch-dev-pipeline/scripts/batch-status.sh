#!/bin/bash
# batch-status.sh - Quick status check across all batch projects
# Usage: batch-status.sh [workspace_dir]

set -e

WORKSPACE="${1:-./workspace}"
BATCH_STATE="$WORKSPACE/batch-state.json"

if [ ! -f "$BATCH_STATE" ]; then
    echo "No batch state found at $BATCH_STATE"
    exit 1
fi

python3 - "$WORKSPACE" << 'PYEOF'
import json
import sys
from pathlib import Path

workspace = Path(sys.argv[1])
state_file = workspace / "batch-state.json"

with open(state_file, encoding="utf-8") as f:
    batch = json.load(f)

print("=" * 60)
print(f"Batch Pipeline Status: {batch.get('status', 'unknown').upper()}")
total = batch.get("total_ideas", 0)
completed = batch.get("completed_ideas", 0)
failed = batch.get("failed_ideas", 0)
print(f"Ideas: {completed}/{total} completed, {failed} failed")
current = batch.get("current_idea_id")
if current:
    print(f"Current: {current}")
if batch.get("started_at"):
    print(f"Started: {batch['started_at']}")
if batch.get("last_updated"):
    print(f"Updated: {batch['last_updated']}")
print("=" * 60)

icons = {
    "pending": "[ ]", "running": "[>]", "completed": "[x]",
    "failed": "[!]", "skipped": "[-]",
}

for idea_id, prog in batch.get("progress", {}).items():
    status = prog.get("status", "unknown")
    icon = icons.get(status, "[?]")
    health = prog.get("health_score", 0)
    sessions = prog.get("sessions_used", 0)
    print(f"  {icon} {idea_id}: health={health}/100 sessions={sessions} status={status}")

    if status == "running":
        pstate_file = Path(prog.get("project_dir", "")) / ".dev-state" / "state.json"
        if pstate_file.exists():
            try:
                with open(pstate_file, encoding="utf-8") as f:
                    ps = json.load(f)
                bd = ps.get("health", {}).get("breakdown", {})
                parts = [
                    f"req={bd.get('requirements', 0)}",
                    f"code={bd.get('code', 0)}",
                    f"test={bd.get('tests', 0)}",
                    f"run={bd.get('runnable', 0)}",
                    f"qual={bd.get('quality', 0)}",
                ]
                print(f"        breakdown: {' '.join(parts)}")
            except (json.JSONDecodeError, OSError):
                pass

    if prog.get("error"):
        print(f"        error: {prog['error']}")

print("=" * 60)
PYEOF
