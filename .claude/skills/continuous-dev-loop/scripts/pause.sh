#!/bin/bash
# 暂停持续开发

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
STATE_FILE="${STATE_DIR}/state.json"

echo "=========================================="
echo "暂停持续开发"
echo "=========================================="

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 状态文件不存在"
    exit 1
fi

python3 << EOF
import json
with open('$STATE_FILE', 'r') as f:
    d = json.load(f)
d['status'] = 'paused'
d['exit_reason'] = 'user_pause'
with open('$STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
EOF

echo "✅ 已设置为暂停状态"
echo "恢复: ./scripts/resume.sh"
