#!/usr/bin/env python3
"""
Initialize adaptive-dev-engine state.json for IDE Native Mode.
Usage: python3 init-state.py --project-dir <dir> [--requirement "text"]
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser("Init State")
    parser.add_argument("--project-dir", default=os.getcwd())
    parser.add_argument("--requirement", default="")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    state_dir = project_dir / ".dev-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    
    (state_dir / "logs").mkdir(exist_ok=True)
    (state_dir / "checkpoints").mkdir(exist_ok=True)
    (state_dir / "agents").mkdir(exist_ok=True)

    if args.requirement:
        (state_dir / "requirement.txt").write_text(args.requirement)

    state_file = state_dir / "state.json"
    if not state_file.exists():
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        project_name = project_dir.name
        
        state = {
            "version": "2.0.0",
            "project": {"name": project_name, "path": str(project_dir), "type": "unknown", "created_at": now},
            "health": {
                "score": 0,
                "breakdown": {"requirements": 0, "code": 0, "tests": 0, "runnable": 0, "quality": 0},
                "details": {},
                "usable": False,
                "target": 80,
                "assessed_at": None,
                "history": [],
                "delta": 0
            },
            "status": "ready",
            "exit_reason": None,
            "current_action": None,
            "agent_coordination": {"active_agents": [], "completed_agents": [], "pending_sync": False},
            "action_history": [],
            "decision_log": [],
            "blockers": [],
            "errors": [],
            "sessions": {"count": 0, "total_turns": 0, "current_session": None},
            "last_heartbeat": now,
            "metrics": {"total_duration_seconds": 0, "parallel_executions": 0, "avg_health_delta_per_session": 0}
        }
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Initialized state.json at {state_file}")
    else:
        print(f"state.json already exists at {state_file}")

if __name__ == "__main__":
    main()
