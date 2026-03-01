#!/bin/bash
# PoC: Batch Dev Pipeline end-to-end test
# Usage: bash run-poc.sh [--adaptive-dev /path/to/adaptive-dev]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$SCRIPT_DIR/workspace"
IDEAS_FILE="$SCRIPT_DIR/test-ideas.yaml"
ORCHESTRATOR="$SCRIPT_DIR/../../skills/batch-dev-pipeline/scripts/batch-orchestrator.py"
STATUS_SCRIPT="$SCRIPT_DIR/../../skills/batch-dev-pipeline/scripts/batch-status.sh"
ADAPTIVE_DEV="${1:-${HOME}/.local/bin/adaptive-dev}"
MAX_WAIT=600  # 10 minutes max

echo "=========================================="
echo "PoC: Batch Dev Pipeline"
echo "=========================================="
echo "Ideas file:   $IDEAS_FILE"
echo "Workspace:    $WORKSPACE"
echo "Orchestrator: $ORCHESTRATOR"
echo "Adaptive-dev: $ADAPTIVE_DEV"
echo "=========================================="

# 1. Clean workspace
echo ""
echo "1. Cleaning workspace..."
rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"

# 2. Start batch orchestrator in background
echo "2. Starting batch orchestrator..."
python3 "$ORCHESTRATOR" start "$IDEAS_FILE" \
    --workspace "$WORKSPACE" \
    --adaptive-dev "$ADAPTIVE_DEV" &
ORCH_PID=$!
echo "   Orchestrator PID: $ORCH_PID"

# 3. Trap to cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill "$ORCH_PID" 2>/dev/null || true
    wait "$ORCH_PID" 2>/dev/null || true
}
trap cleanup EXIT

# 4. Wait and monitor
echo "3. Monitoring progress (max ${MAX_WAIT}s)..."
ELAPSED=0
INTERVAL=10

while [ "$ELAPSED" -lt "$MAX_WAIT" ]; do
    sleep "$INTERVAL"
    ELAPSED=$((ELAPSED + INTERVAL))

    if [ -f "$WORKSPACE/batch-state.json" ]; then
        STATUS=$(python3 -c "
import json
with open('$WORKSPACE/batch-state.json') as f:
    s = json.load(f)
print(s.get('status', 'unknown'))
" 2>/dev/null || echo "unknown")

        COMPLETED=$(python3 -c "
import json
with open('$WORKSPACE/batch-state.json') as f:
    s = json.load(f)
print(s.get('completed_ideas', 0))
" 2>/dev/null || echo "0")

        TOTAL=$(python3 -c "
import json
with open('$WORKSPACE/batch-state.json') as f:
    s = json.load(f)
print(s.get('total_ideas', 0))
" 2>/dev/null || echo "0")

        echo "   [${ELAPSED}s] status=$STATUS completed=$COMPLETED/$TOTAL"

        if [ "$STATUS" = "completed" ] || [ "$STATUS" = "stopped" ] || [ "$STATUS" = "failed" ]; then
            break
        fi
    else
        echo "   [${ELAPSED}s] waiting for batch-state.json..."
    fi

    # Check if orchestrator is still running
    if ! kill -0 "$ORCH_PID" 2>/dev/null; then
        echo "   Orchestrator process exited"
        break
    fi
done

# 5. Show final status
echo ""
echo "4. Final status:"
if [ -f "$WORKSPACE/batch-state.json" ]; then
    bash "$STATUS_SCRIPT" "$WORKSPACE"
else
    echo "   No batch-state.json found"
fi

# 6. Verify project directories
echo ""
echo "5. Project verification:"
for dir in "$WORKSPACE"/*/; do
    [ -d "$dir" ] || continue
    project=$(basename "$dir")
    if [ -f "$dir/.dev-state/state.json" ]; then
        HEALTH=$(python3 -c "
import json
with open('$dir/.dev-state/state.json') as f:
    print(json.load(f).get('health', {}).get('score', 0))
" 2>/dev/null || echo "0")
        FILE_COUNT=$(find "$dir" -name "*.py" -o -name "*.ts" -o -name "*.js" | wc -l | tr -d ' ')
        echo "   $project: health=$HEALTH files=$FILE_COUNT"
    else
        echo "   $project: no state.json"
    fi
done

echo ""
echo "=========================================="
echo "PoC Complete"
echo "=========================================="
