# Adaptive Dev Engine v2.0 - Review Report

## 总体评价

v2.0 是一次成功的重构。v1.0 review 中识别的 3 个 P0 问题（健康度自评虚高、会话间上下文丢失、并发写入无保护）和大部分 P1/P2 问题均已修复。系统架构清晰，跨文件一致性良好，可投入实际使用。

**文件统计:**

| 文件 | 行数 | 状态 |
|------|------|------|
| SKILL.md | 135 | 从 580 行精简，结构清晰 |
| scripts/adaptive-dev | 950 | 全面重写，修复所有 P0/P1 |
| scripts/adaptive-dev.ps1 | 785 | 同步重写，修复 Job/PID 混用 |
| scripts/health-check.py | 413 | 新增，独立健康度评估 |
| scripts/config.env | 51 | 新增，外部化配置 |
| references/ (5 docs) | 2255 | 更新，与代码一致 |
| **总计** | **4589** | |

---

## 一、v1.0 问题修复验证

### P0 问题（全部修复）

| # | 问题 | 修复方式 | 验证 |
|---|------|----------|------|
| P0-1 | 健康度自评虚高 | 新增 `health-check.py` 独立脚本，守护进程会话前后自动运行 | `adaptive-dev:547-552`, `health-check.py:294-322` |
| P0-2 | 会话间上下文丢失 | prompt 传递完整上下文（checkpoint/history/blockers/errors/weakest dimension） | `adaptive-dev:577-696` |
| P0-3 | 并发写 state.json | `set_json()` 使用 `fcntl.flock`（bash）/ `msvcrt.locking`（PS1） | `adaptive-dev:58-75`, `adaptive-dev.ps1:104-134` |

### P1 问题（全部修复）

| # | 问题 | 修复方式 | 验证 |
|---|------|----------|------|
| P1-1 | 决策树过于线性 | 改为维度优先决策（最弱维度 → 对应 Agent） | `SKILL.md:Step 3`, `decision-engine.md:38-152` |
| P1-2 | 并行 Agent 文件冲突 | 移除不可靠的文件锁，改为 prompt 约束目录范围 | `agent-orchestration.md:冲突避免` |
| P1-3 | pkill 误杀进程 | bash: `setsid` + `kill -- -$PGID`（macOS 回退到 PID）; PS1: `Start-Process` + 进程树清理 | `adaptive-dev:703-720`, `adaptive-dev.ps1:287-289` |
| P1-4 | 无回滚机制 | `git_auto_commit()` 会话前自动提交，`git_rollback()` 失败时回滚 | `adaptive-dev:104-129` |
| P1-5 | 无人工介入接口 | 新增 `feedback` 命令 + `user-feedback.md` 文件 | `adaptive-dev:862-872` |

### P2 问题（全部修复）

| # | 问题 | 修复方式 |
|---|------|----------|
| P2-1 | SKILL.md 过长(580行) | 精简到 135 行，代码示例移到 references/ |
| P2-2 | 日志无轮转 | `cleanup_old_logs()` 按天数+数量轮转 |
| P2-3 | 无会话总数限制 | `MAX_TOTAL_SESSIONS` 配置项（默认 100） |
| P2-4 | PS1 Job/PID 混用 | 改用 `Start-Process -PassThru` 获取真实 PID |
| P2-5 | 轮次限制断点 | `MAX_TURNS` 降到 40，prompt 提示在 turn 35 保存 checkpoint |
| P2-6 | 心跳依赖 AI 更新 | `set_json()` 每次调用自动更新 `last_heartbeat` |

---

## 二、v2.0 新发现问题

### P1: Bash prompt 作为 CLI 参数传递（可能超出 ARG_MAX）

**文件:** `scripts/adaptive-dev:707-709`

**问题:** Bash 版将整个 prompt 作为 claude CLI 的命令行参数传递：
```bash
$setsid_cmd claude --print ... "$prompt" > "$session_log" 2>&1 &
```
当项目上下文较大时（长 checkpoint、多 action_history、多 errors），prompt 可能超过系统 ARG_MAX 限制（Linux 通常 2MB，macOS 256KB）。

**对比:** PS1 版已正确处理——将 prompt 写入临时文件再 pipe：
```powershell
$prompt | Set-Content $promptFile -Encoding UTF8
# ...
$runScript = "Get-Content -Raw '$promptFile' | & claude ..."
```

**建议:** Bash 版应采用相同策略：
```bash
local prompt_file="$PROJECT_DIR/$STATE_DIR/session-prompt.txt"
echo "$prompt" > "$prompt_file"
$setsid_cmd bash -c "cat '$prompt_file' | claude --print ..." > "$session_log" 2>&1 &
```

**严重度:** P1 — 大型项目上下文可能导致会话启动失败

---

### P2: health-check.py API 端点搜索目录有限

**文件:** `scripts/health-check.py:75-88`

**问题:** `score_code()` 只在 `src/`、`app/`、`backend/` 中搜索 API 端点。使用 `routes/`、`api/`、`server/`、`handlers/` 等目录结构的项目会被低估。

**建议:** 扩展搜索目录列表：
```python
for subdir in ["src", "app", "backend", "server", "api", "routes", "handlers", "lib"]:
```

**严重度:** P2 — 影响部分项目的 code 维度评分准确性

---

### P2: Reference 文档包含过时的代码示例

**文件:** `references/health-assessment.md:245-391`, `references/state-protocol.md`

**问题:**
- `health-assessment.md` 仍包含旧版 `assess_health()` 脚本（~150 行），虽标注"已由 health-check.py 替代"，但 AI 可能仍然参考执行
- `state-protocol.md` 包含 `update_health()` 等函数，在 v2.0 中健康度由 health-check.py 更新，AI 不应直接调用

**建议:**
- `health-assessment.md` 中的旧脚本代码块改为折叠或删除，只保留评分标准表格
- `state-protocol.md` 中标注哪些函数是"仅供参考"vs"AI 应调用"

**严重度:** P2 — 可能导致 AI 执行冗余或错误的健康度更新

---

### P2: __pycache__ 被 git 跟踪

**文件:** `scripts/__pycache__/health-check.cpython-312.pyc`

**建议:** 添加到 `.gitignore`：
```
scripts/__pycache__/
```

**严重度:** P2 — 代码卫生问题

---

### P3: PS1 心跳超时使用 pkill -P

**文件:** `scripts/adaptive-dev.ps1:576`

**问题:** PS1 版在 Linux/macOS 上使用 `pkill -P $cpid` 清理子进程，而 bash 版使用更精确的 PGID 机制。`pkill -P` 只杀直接子进程，不杀孙进程。

**建议:** 仅影响 PS1 在 Unix 上运行的场景（少见），可接受。

**严重度:** P3

---

### P3: 无成本/Token 监控

**问题:** 7x24 运行消耗大量 API token，但无预算控制。`MAX_TOTAL_SESSIONS=100` 提供了间接限制，但无法精确控制成本。

**建议:** 未来版本可在 `metrics` 中增加 token 统计，或集成 claude CLI 的 usage 输出。

**严重度:** P3 — 功能增强建议

---

## 三、跨文件一致性检查

| 检查项 | 结果 |
|--------|------|
| SKILL.md 决策表 vs decision-engine.md 算法 | 一致 |
| health-assessment.md 评分标准 vs health-check.py 实现 | 一致 |
| state-protocol.md 结构 vs bash/PS1 _init_state() | 一致 |
| recovery-scenarios.md 场景 vs classify_exit() 分类 | 一致 |
| config.env 默认值 vs bash/PS1 默认值 | 一致 |
| SKILL.md 维度满分 vs health-check.py MAX_SCORES | 一致 |
| bash prompt 构建 vs PS1 prompt 构建 | 逻辑一致，实现方式不同（bash 直接传参 vs PS1 文件管道） |
| bash 错误处理返回码 vs PS1 sessionResult | 一致（0=成功, 2=限流, 3=上下文, 4=网络, 5=权限, 6=超时, 99=未知） |

---

## 四、架构亮点

1. **独立健康度评估**: health-check.py 使用客观标准（文件计数、linter 输出、实际启动测试），消除了 AI 自评偏差
2. **进程组隔离**: bash 版使用 `setsid` 创建新进程组，`kill -- -$PGID` 精确清理，macOS 无 setsid 时安全回退到 PID
3. **文件锁保护**: `set_json()` 和 `update_state()` 均使用 OS 级文件锁，防止并发写入损坏
4. **完整上下文传递**: prompt 包含 checkpoint、action_history、blockers、errors、weakest dimension，确保会话间连续性
5. **state.json 损坏恢复**: 守护进程检测到损坏时自动从 checkpoint 恢复
6. **分层错误处理**: classify_exit() 将错误分为 7 类，每类有不同的恢复策略和错误计数规则
7. **配置外部化**: config.env 支持项目级覆盖，所有硬编码值均可配置

---

## 五、问题汇总

| 优先级 | 问题 | 文件 | 建议 |
|--------|------|------|------|
| P1 | Bash prompt 作为 CLI 参数（ARG_MAX 风险） | adaptive-dev:707 | 改为写入临时文件再 pipe |
| P2 | API 端点搜索目录有限 | health-check.py:75 | 扩展搜索目录列表 |
| P2 | Reference 文档含过时代码示例 | health-assessment.md, state-protocol.md | 标注或删除过时代码 |
| P2 | __pycache__ 被 git 跟踪 | scripts/__pycache__/ | 添加 .gitignore |
| P3 | PS1 心跳超时用 pkill -P | adaptive-dev.ps1:576 | 可接受，仅影响 PS1+Unix |
| P3 | 无成本/Token 监控 | - | 未来版本增强 |

---

## 六、结论

v2.0 相比 v1.0 有质的提升：

- **P0 问题全部修复**: 健康度评估可靠、上下文完整传递、并发写入安全
- **P1 问题全部修复**: 维度优先决策、进程组隔离、git 集成、用户反馈
- **P2 问题全部修复**: SKILL.md 精简、日志轮转、会话限制
- **跨文件一致性良好**: 所有文档与代码实现保持同步
- **仅剩 1 个 P1**: Bash prompt 传参方式需改为文件管道

**建议:** 修复 P1（bash prompt 传参）后即可正式发布。P2/P3 问题可在后续迭代中处理。
