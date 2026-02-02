#!/bin/bash
# 查看持续开发状态 v2.0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.env" 2>/dev/null || true

STATE_DIR="${STATE_DIR:-.dev-state}"
STATE_FILE="${STATE_DIR}/state.json"
PID_FILE="${STATE_DIR}/daemon.pid"

echo "=========================================="
echo "持续开发状态"
echo "=========================================="
echo ""

# 守护进程状态
echo "【守护进程】"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "  状态: ✅ 运行中 (PID: $PID)"
    else
        echo "  状态: ❌ 已停止 (PID 文件存在但进程不在)"
    fi
else
    echo "  状态: ⏹️  未启动"
fi
echo ""

# 项目状态
if [ ! -f "$STATE_FILE" ]; then
    echo "❌ 状态文件不存在，请先运行 init.sh"
    exit 1
fi

python3 << EOF
import json
from datetime import datetime

with open('$STATE_FILE', 'r') as f:
    s = json.load(f)

project = s.get('project', {})
workflow = s.get('workflow', {})
progress = s.get('progress', {})
task = s.get('current_task', {})
rate = s.get('rate_limit', {})

print("【项目信息】")
print(f"  名称: {project.get('name', 'N/A')}")
print(f"  状态: {s.get('status', 'N/A')}")
print(f"  退出原因: {s.get('exit_reason') or 'N/A'}")
print()

print("【工作流】")
print(f"  当前阶段: {workflow.get('current_phase', 'N/A')}")
print(f"  迭代轮次: {workflow.get('iteration', 1)}")
ps = workflow.get('phase_status', {})
for phase, status in ps.items():
    icon = {'completed': '✅', 'in_progress': '🔄', 'pending': '⏳', 'failed': '❌'}.get(status, '❓')
    print(f"    {phase}: {icon} {status}")
print()

print("【当前任务】")
if task:
    print(f"  ID: {task.get('id', 'N/A')}")
    print(f"  名称: {task.get('name', 'N/A')}")
    print(f"  Skill: {task.get('skill', 'N/A')}")
    print(f"  重试: {task.get('retry_count', 0)}")
    cp = task.get('checkpoint')
    if cp:
        print(f"  断点: {cp}")
print()

print("【进度统计】")
total_all = sum(p.get('total', 0) for p in progress.values())
done_all = sum(p.get('completed', 0) for p in progress.values())
for phase, p in progress.items():
    t, c, f = p.get('total', 0), p.get('completed', 0), p.get('failed', 0)
    pct = f"{c}/{t} ({c/t*100:.0f}%)" if t > 0 else f"{c}/{t}"
    print(f"  {phase}: {pct}" + (f" (失败: {f})" if f > 0 else ""))
if total_all > 0:
    print(f"  总计: {done_all}/{total_all} ({done_all/total_all*100:.1f}%)")
print()

print("【限流状态】")
print(f"  连续限流: {rate.get('consecutive_limits', 0)} 次")
print(f"  最后调用: {rate.get('last_call') or 'N/A'}")
print()

print("【心跳】")
hb = s.get('last_heartbeat')
if hb:
    try:
        hb_time = datetime.fromisoformat(hb.replace('Z', '+00:00'))
        age = (datetime.now(hb_time.tzinfo) - hb_time).total_seconds()
        print(f"  最后心跳: {hb} ({int(age)}秒前)")
    except:
        print(f"  最后心跳: {hb}")
EOF

echo ""
echo "=========================================="
echo "最近日志:"
echo "------------------------------------------"
tail -5 "$STATE_DIR/logs/daemon.log" 2>/dev/null || echo "  (无日志)"
echo "=========================================="
