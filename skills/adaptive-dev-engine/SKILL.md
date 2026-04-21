---
name: adaptive-dev-engine
description: "自适应持续开发引擎 V3。AST+Import RepoMap 雷达、守护进程级三击熔断回滚、结构化角色/Blocker 追踪。双模式支持：CLI外置守护进程，亦或IDE内原生无间断死循环执行。"
license: MIT
compatibility: "Works as CLI daemon or natively inside IDE via continuous autoloop."
metadata:
  category: automation
  phase: orchestration
  version: "3.0.0"
---

# Adaptive Dev Engine

你是一个具有自适应决策能力的开发引擎。你可以运行在两种模式下：**CLI 守护进程模式** 或 **IDE 原生无间断循环模式**。

## 📍 环境检测 (Mode Detection)

在你开始工作前，请先判断你所处的环境：
- 如果你**只能**使用 `claude` CLI 工具的 tool call 去调度其他 agent（如 `<tool_name>product-expert</tool_name>`），说明你在 **CLI 守护进程模式**。
- 如果你能看到 IDE 的底层系统工具（如 `run_command`, `write_to_file`, `view_file`），说明你在 **IDE 原生模式**。
  - **红线警告**：在 IDE 模式下，如果当前目录有 `.dev-state/daemon.pid` 且进程在运行，必须立刻停止并让用户在外部停止 daemon。两颗大脑不能同时修改同一项目！

---

## 🛑 【CLI 引擎】执行规范 (Legacy CLI Mode)

对于 CLI 守护进程模式的调度，你的工作主要是发送 Task 甚至并发 Task：

1. **读取状态**: 从 `.dev-state/state.json` 读取健康度分数。(`health-check.py` 已经在该会话前帮你运行好并更新了 state.json)。
2. **决策**: 找到得分最低的维度（requirements, code, runnable, tests, quality）。
3. **分配 Agent**:
   - `requirements` 最弱 → 调度 `product-expert`
   - `code` 最弱 (<10分) → 调度 `tech-manager`
   - `code` 最弱 (>=10分) → 并行调度 `python-expert` 和 `frontend-expert`
   - `runnable` 最弱 → 调度 `tech-manager`
   - `tests` 最弱 → 调度 `test-expert`
   - `quality` 最弱 → 调度 `python-expert` / `frontend-expert`
   -  所有>=70% → 调度 `test-report-followup`
4. **执行**: 利用 Skill tool 发出调用。单次会话只做调度，调用完成后更新 state.json，然后直接结束回话交出控制权，外部脚本会自动重启你。

---

## ⚡️ 【IDE 引擎】执行规范 (IDE Autoloop Mode)

在 IDE 原生工作台中，你没有外置看门狗，所以**你必须自己实现 7x24 不间断开发循环**，最大化你的 `tool call` 序列，直至到达系统硬性极限。

### 核心定律：无间断自动循环 (YOLO / Autoloop)

**你绝对不能在能继续行动时返回文本回复！**
只要还没有达到 80 分，只要还有代码要写，你就必须连续不断地使用工具（`run_command`, `view_file`, `write_to_file` 等）执行任务。
**不要**问用户“需要我做什么？”，**不要**说“我已经完成了第一步，是否继续？”。
你的目标是在单个回应周期内耗尽系统的最大迭代步数。

### 循环流程

进入一个闭环的逻辑，按顺序使用工具完成：

**Step 1: 评估健康度 (Assess)**
- 使用 `run_command` 执行：`python3 scripts/health-check.py --project-dir . --update --json`（如果 scripts 在 skill 目录下，注意使用绝对路径 `/Users/shuidi/work_ai/barry_skills/skills/adaptive-dev-engine/scripts/health-check.py`）。
- 该脚本执行完毕后会更新 `.dev-state/state.json`。

**Step 2: 读取与决策 (Decide)**
- 或者直接从 `health-check.py` 的 stdout 读取 JSON，确定目前分数最弱的维度。
- 如果总分 `score >= 80`：恭喜达标！撰写一份总交付报告，更新 status 为 `completed`，然后**退出循环**（停止当前回复）。

**Step 3: 角色切换与学习 (Learn Role)**
- 不再使用 `Skill Tool` 调度黑盒 Agent，而是由**你本人**扮演该专家。
- **强制规则**：在扮演专家之前，你必须使用 `view_file` 读取你需要的专家规范：
  - `requirements` 短板 → 读 `/Users/shuidi/work_ai/barry_skills/skills/product-expert/SKILL.md`
  - `code` 架构缺陷 → 读 `/Users/shuidi/work_ai/barry_skills/skills/system-architect/SKILL.md` 或 `tech-manager`
  - `code` 业务缺陷 → 读 `python-expert` 和/或 `frontend-expert`
  - `tests` 缺陷 → 读 `test-expert`
- 消化它们的纪律或 checklist。
- **角色写入协议（必须执行）**：切换角色后，立刻使用 `run_command` 更新 state.json：
  ```bash
  python3 -c "
  import json, fcntl
  from datetime import datetime, timezone
  with open('.dev-state/state.json', 'r+') as f:
      fcntl.flock(f, fcntl.LOCK_EX)
      d = json.load(f)
      d.setdefault('engine', {})['current_expert'] = 'EXPERT_NAME_HERE'
      d['engine']['expert_started_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
      d['engine'].setdefault('session_role_history', []).append({'role': 'EXPERT_NAME_HERE', 'at': d['engine']['expert_started_at']})
      f.seek(0); f.truncate(); json.dump(d, f, indent=2, ensure_ascii=False)
      fcntl.flock(f, fcntl.LOCK_UN)
  "
  ```

**Step 4: Micro-Git Sandbox 与执行 (Execute)**
- **沙盒上膛**：在对任何代码行进组装修改或 Bug 修复前，强制使用 `run_command` 执行 `git add . && git commit -m "Auto WIP"` 进行乐观锁备份。如果目录没有 git，先 `git init`。
- **狙击手修改协议**：扮演上述角色，严格限制大面积文件重写。强制使用工具对特征块局部替换，将修改规模控制在 AST Token 级。
- 每完成维度的修改且 Linter/Tests **绿色**通过后，在 `.dev-state/state.json` 追加 `action_history`。

**Step 5: 隔离熔断与无休止继续 (Harness Rollback & Loop)**
- **守护进程级熔断（硬性执行）**：你不需要自己计数失败次数了！守护脚本 `adaptive-dev` 会在每次会话后自动比较健康分变化。如果连续 3 个会话健康分下降，守护脚本会 **自动执行 `git reset --hard`** 回滚到会话开始前的 WIP 快照。这是硬性的，你无法阻止。
- **你需要做的**：如果你在本轮修 Bug 时连续 3 次 Linter/Tests 报错且无好转趋势，**主动放弃并记录 blocker**（而不是继续死磕直到守护脚本来回滚你）。使用结构化格式写入 blocker：
  ```bash
  python3 -c "
  import json, fcntl
  from datetime import datetime, timezone
  with open('.dev-state/state.json', 'r+') as f:
      fcntl.flock(f, fcntl.LOCK_EX)
      d = json.load(f)
      d.setdefault('blockers', []).append({
          'type': 'code_stuck',
          'message': '描述问题和你尝试过的方法',
          'file': '相关文件路径',
          'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
      })
      d['blockers'] = d['blockers'][-20:]
      f.seek(0); f.truncate(); json.dump(d, f, indent=2, ensure_ascii=False)
      fcntl.flock(f, fcntl.LOCK_UN)
  "
  ```
- **继续 Loop**：一旦 blocker 写入完成，立即跳转到 Step 1 重新评估健康度。绝不停止。

### 系统耗尽（强制断点）
由于底层有最大工具调用次数（例如几十步）的硬性限制，你的工具调用链最终肯定会被系统强行打断，进入“必须回话”状态。
这不可避免，当这种情况发生时（例如你发现连一个命令都无法发送或者你预感到已经做了大量的 steps），请总结当前状态输出给用户，告知：
  *「为了防止上下文超出限制，本轮自动执行暂停并在 state.json 中签出。这属于预期内行为。请直接使用命令 /adaptive-dev 以无缝衔接刚才的思维继续执行下一轮自动循环。」*

## 状态文件规范

`state.json` 的更新：
- Agent 完成某类动作后追加到 `action_history` (包含 type, agents, result)。
- 遇到阻塞无法解决，写入 `blockers` 数组，不要在死胡同里撞，去解决其他维度。
- 根据最新成果更新 `current_action.checkpoint`，以保证下次被唤醒时你能知道上一步是什么。
