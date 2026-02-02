#!/bin/bash
# 恢复持续开发

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
STATE_FILE="${STATE_DIR}/state.json"

echo "=========================================="
echo "恢复持续开发"
echo "=========================================="

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 状态文件不存在"
    exit 1
fi

CURRENT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('status'))")
echo "当前状态: $CURRENT"

python3 << EOF
import json
with open('$STATE_FILE', 'r') as f:
    d = json.load(f)
d['status'] = 'continue'
d['exit_reason'] = ''
with open('$STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
EOF

echo "✅ 已设置为继续状态"
echo ""
echo "如果守护进程正在运行，它将自动继续"
echo "如果守护进程未运行，请执行 ./scripts/start.sh"
