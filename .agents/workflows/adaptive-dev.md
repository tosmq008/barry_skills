---
description: 启动自适应持续开发引擎 (IDE原生模式)，无间断全自动运行直到目标达成
---

// turbo-all

1. 检查是否存在 CLI 守护进程锁（若存在则需终止并报错退出，防止冲突）：
   `cat .dev-state/daemon.pid`
   *(如果文件存在，请告知用户必须先停止外置的 adaptive-dev 守护进程)*

2. 检查 .dev-state/state.json 是否存在，如果不存在则进行初始化：
   运行命令: `python3 /Users/shuidi/work_ai/barry_skills/skills/adaptive-dev-engine/scripts/init-state.py --project-dir .`
   *(如果需要传入需求描述，可以在命令后追加 `--requirement "你的需求" `)*

3. 读取核心引擎规则：
   使用 view_file 读取 `/Users/shuidi/work_ai/barry_skills/skills/adaptive-dev-engine/SKILL.md` 并学习 [IDE 引擎] 部分的指令。

4. **进入无间断自动循环 (Continuous Autoloop Mode)**:
   - 立即开始执行 SKILL.md 中的 IDE 工作流。
   - **绝对不要**在每个步骤后停下来询问用户。
   - 连续进行 `health-check` -> `决策分析` -> `调用其他专家技能文档` -> `修改代码` -> `更新 state.json` 等一系列 tool calls。
   - 一直执行下去直到项目健康度 >= 80 或者遇到阻碍必须人工介入为止。
