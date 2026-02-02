# 常见问题排查 v2.0

## 问题 1: 守护进程启动失败

**症状:** `./start.sh` 后进程立即退出

**排查步骤:**
```bash
# 1. 检查日志
tail -50 .dev-state/run.log

# 2. 检查状态文件
cat .dev-state/state.json | python3 -m json.tool

# 3. 手动运行守护进程查看错误
./scripts/daemon.sh
```

**常见原因:**
- 状态文件 JSON 格式错误
- Claude CLI 未安装或未登录
- 权限问题

---

## 问题 2: Claude CLI 无响应

**症状:** 会话启动后长时间无输出

**排查步骤:**
```bash
# 1. 检查 Claude CLI 是否正常
claude --version

# 2. 测试简单命令
claude --print --max-turns 1 "回复 OK"

# 3. 检查认证状态
claude config list
```

**常见原因:**
- API 认证过期
- 网络问题
- 代理配置问题

---

## 问题 3: 任务一直重试

**症状:** 同一个任务反复执行

**排查步骤:**
```bash
# 1. 检查当前任务状态
cat .dev-state/state.json | python3 -c "
import sys, json
state = json.load(sys.stdin)
task = state.get('current_task', {})
print(f'任务: {task.get(\"name\")}')
print(f'重试次数: {task.get(\"retry_count\", 0)}')
"

# 2. 检查错误日志
cat .dev-state/state.json | python3 -c "
import sys, json
state = json.load(sys.stdin)
for err in state.get('errors', [])[-5:]:
    print(f'{err[\"timestamp\"]}: {err[\"error\"]}')
"
```

**解决方案:**
```bash
# 跳过当前任务
python3 << 'EOF'
import json
with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)
state['progress']['skipped'] += 1
if state['task_queue']:
    state['current_task'] = state['task_queue'].pop(0)
else:
    state['current_task'] = None
state['status'] = 'continue'
with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2)
EOF
```

---

## 问题 4: 触发限流

**症状:** 日志显示 rate limit 错误

**解决方案:**
```bash
# 1. 增加重启延迟
# 编辑 scripts/config.env
RESTART_DELAY=60
RATE_LIMIT_WAIT=600

# 2. 减少单次会话轮次
MAX_TURNS=30
```

---

## 问题 5: 心跳超时

**症状:** 守护进程判定会话卡死

**排查步骤:**
```bash
# 1. 检查最后心跳时间
cat .dev-state/state.json | python3 -c "
import sys, json
state = json.load(sys.stdin)
print(f'最后心跳: {state.get(\"last_heartbeat\")}')
"

# 2. 检查是否有 Claude 进程在运行
ps aux | grep claude | grep -v grep
```

**解决方案:**
- 增加 `HEARTBEAT_TIMEOUT` 配置
- 检查任务是否过于复杂需要拆分

---

## 问题 6: 状态文件损坏

**症状:** JSON 解析错误

**解决方案:**
```bash
# 1. 备份当前文件
cp .dev-state/state.json .dev-state/state.json.bak

# 2. 重新初始化
./scripts/init.sh "项目名称" "项目描述"

# 3. 或手动修复 JSON
python3 -m json.tool .dev-state/state.json.bak > .dev-state/state.json
```

---

## 日志级别说明

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 正常运行信息 |
| WARN | 警告，可能需要关注 |
| ERROR | 错误，需要处理 |

## 有用的命令

```bash
# 查看实时日志
tail -f .dev-state/run.log

# 查看错误日志
grep ERROR .dev-state/run.log

# 查看进度统计
./scripts/status.sh

# 强制重置状态
python3 -c "
import json
with open('.dev-state/state.json', 'r') as f:
    state = json.load(f)
state['status'] = 'ready'
state['exit_reason'] = None
with open('.dev-state/state.json', 'w') as f:
    json.dump(state, f, indent=2)
"
```
